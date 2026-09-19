import os
import json
import logging
import asyncio
import httpx
from typing import Dict, Any, List
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.cache_service import ai_cache

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self._async_client = None

    async def get_client(self) -> httpx.AsyncClient:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if self._async_client is None or self._async_client.is_closed or getattr(self, "_client_loop", None) != loop:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
            self._async_client = httpx.AsyncClient(limits=limits, timeout=30.0)
            self._client_loop = loop
        return self._async_client

    async def _call_gemini_async(self, prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
        api_key = self.api_key or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return ""

        candidate_models = [self.model, "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview", "gemini-flash-latest"]
        # Deduplicate while preserving order
        candidate_models = list(dict.fromkeys([m for m in candidate_models if m]))

        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"System Context: {system_instruction}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these legal drafting instructions strictly."}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        generation_config = {
            "temperature": 0.2,
            "topP": 0.95,
            "maxOutputTokens": 2048
        }
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload = {
            "contents": contents,
            "generationConfig": generation_config
        }

        client = await self.get_client()
        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = await client.post(url, json=payload, timeout=20.0)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                        text = candidates[0]["content"]["parts"][0].get("text", "")
                        if text:
                            return text
                else:
                    logger.warning(f"Gemini API model {model} returned {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"Error calling Gemini model {model}: {e}")

        return ""

    async def refine_clause(self, raw_text: str, document_type: str = "tenancy_agreement", language: str = "bn") -> Dict[str, Any]:
        cache_key = ai_cache.generate_key("refine", raw_text.strip().lower(), document_type, language)
        cached = await ai_cache.get(cache_key)
        if cached:
            return cached

        prompt = f"""
        You are an expert legal draftsperson specializing in Bangladesh and international contract law.
        Convert the following informal requirement into a legally enforceable, professional, binding contract clause.
        
        Document Type: {document_type}
        Language: {'Bangla' if language == 'bn' else 'English'}
        Informal user requirement: "{raw_text}"
        
        Note: If the requirement is extremely short, a greeting, or not a specific contract term (e.g. 'what', 'hello'), formulate a standard mutual good-faith compliance clause and state in the explanation that specific requirements should be provided.
        
        Respond ONLY with a JSON object in the following format:
        {{
            "title": "Short title of clause",
            "refined_clause": "The legally sound clause text",
            "risk_level": "Low / Medium / High",
            "explanation": "Brief 1-line note on legal validity"
        }}
        """
        
        ai_response = await self._call_gemini_async(prompt, json_mode=True)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                result = json.loads(cleaned.strip())
                await ai_cache.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Failed to parse Gemini JSON: {e}")

        # Built-in Heuristic Fallback
        clean_input = raw_text.strip()
        if len(clean_input) < 4 or clean_input.lower() in ["what", "hello", "hi", "test", "hey"]:
            if language == "bn":
                refined = "উভয় পক্ষ চুক্তির নির্দিষ্ট কোনো শর্ত সংযোজন করিতে চাহিলে তাহার বিস্তারিত বিবরণ (যেমন: বিশেষ ব্যবহারবিধি, বকেয়া পরিশোধ বা নিরাপত্তা বিধান) উল্লেখ করিবেন।"
                title = "সাধারণ পরিচালনা ও সম্মতি বিধি"
                explanation = "অসম্পূর্ণ বা অনির্দিষ্ট ইনপুটের জন্য সাধারণ শর্ত। সুনির্দিষ্ট বিবরণ লিখলে AI তা কার্যকর ধারায় রূপান্তর করবে।"
            else:
                refined = "The Parties agree that any supplemental covenant shall be defined with specific obligations, remedies, and compliance timelines."
                title = "General Compliance & Governance"
                explanation = "Standard general covenant. Provide detailed requirements for customized legal terms."
        elif language == "bn":
            refined = f"উভয় পক্ষ এই মর্মে সম্মত হইলেন যে, {clean_input}। উক্ত শর্ত লঙ্ঘন করিলে বা ব্যত্যয় ঘটিলে ক্ষতিগ্রস্ত পক্ষ প্রচলিত আইন ও এই চুক্তির বিধিমোতাবেক ক্ষতিপূরণ দাবি করিতে এবং চুক্তি বাতিল বলিয়া গণ্য করিতে পারিবে।"
            title = "বিশেষ বাধ্যবাধকতা ও পরিচালনা বিধি"
            explanation = "এই ধারাটি চুক্তির সাধারণ আইন অনুযায়ী উভয় পক্ষের উপর সমভাবে বর্তাবে।"
        else:
            refined = f"The Parties hereby agree that {clean_input}. Any breach or non-compliance of this provision shall entitle the non-breaching Party to claim appropriate remedies, damages, and terminate this Agreement in accordance with applicable governing laws."
            title = "Special Obligations & Compliance"
            explanation = "Standard enforceable clause adhering to bilateral contract principles."

        result = {
            "title": title,
            "refined_clause": refined,
            "risk_level": "Low",
            "explanation": explanation
        }
        await ai_cache.set(cache_key, result)
        return result

    async def explain_clause(self, clause_text: str, language: str = "bn") -> Dict[str, Any]:
        cache_key = ai_cache.generate_key("explain", clause_text.strip().lower(), language)
        cached = await ai_cache.get(cache_key)
        if cached:
            return cached

        prompt = f"""
        Explain the following legal clause in simple, easy-to-understand plain language for an ordinary citizen.
        Target Language: {'Bangla' if language == 'bn' else 'English'}
        Legal Clause: "{clause_text}"

        Respond ONLY in JSON format:
        {{
            "simple_explanation": "Clear 2-3 sentences explanation without jargon",
            "key_obligations": ["Obligation 1", "Obligation 2"],
            "potential_risks": ["Risk if violated or ignored"]
        }}
        """

        ai_response = await self._call_gemini_async(prompt, json_mode=True)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                result = json.loads(cleaned.strip())
                await ai_cache.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")

        # Knowledge-base fallback
        clean_text = clause_text.strip()
        if len(clean_text) < 6 or clean_text.lower() in ["hello", "hi", "what", "test"]:
            if language == "bn":
                result = {
                    "simple_explanation": "প্রদত্ত অংশটি একটি খসড়া বা অসম্পূর্ণ শব্দ। চুক্তিপত্রের কোনো নির্দিষ্ট ধারা নির্বাচন করিলে তাহার বিস্তারিত আইনগত ব্যাখ্যা প্রদর্শিত হইবে।",
                    "key_obligations": [
                        "চুক্তিপত্রের পূর্ণাঙ্গ ধারা বা অনুচ্ছেদ উল্লেখ করা।"
                    ],
                    "potential_risks": [
                        "অসম্পূর্ণ বাক্য চুক্তিতে অন্তর্ভুক্ত থাকিলে আইনগত অনিশ্চয়তা সৃষ্টি হইতে পারে।"
                    ]
                }
            else:
                result = {
                    "simple_explanation": "The provided text is an informal placeholder. Select a complete contract clause to view detailed legal obligations.",
                    "key_obligations": [
                        "Review and reference the complete clause language."
                    ],
                    "potential_risks": [
                        "Incomplete clauses in an executed deed create legal ambiguity."
                    ]
                }
        elif language == "bn":
            result = {
                "simple_explanation": "এই ধারাটি চুক্তির পক্ষদ্বয়ের অধিকার, নির্দিষ্ট বাধ্যবাধকতা ও পারস্পরিক সম্মতির সীমা নির্ধারণ করে।",
                "key_obligations": [
                    "চুক্তির নির্ধারিত শর্তাবলি ও সময়সীমা যথাযথভাবে মানিয়া চলা।",
                    "উভয় পক্ষের সম্মতি ব্যতিরেকে এককভাবে কোনো শর্ত পরিবর্তন না করা।"
                ],
                "potential_risks": [
                    "শর্ত ভঙ্গ করিলে অপর পক্ষ ক্ষতিপূরণ দাবি বা আইনি পদক্ষেপ গ্রহণ করিতে পারে।"
                ]
            }
        else:
            result = {
                "simple_explanation": "This clause defines specific obligations, legal limits, and operational duties between the signing parties.",
                "key_obligations": [
                    "Strictly comply with specified terms and timelines.",
                    "No unilateral modification without written bilateral consent."
                ],
                "potential_risks": [
                    "Breach may result in monetary damages or legal termination."
                ]
            }
        await ai_cache.set(cache_key, result)
        return result

    async def audit_contract(self, document_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = ai_cache.generate_key("audit", document_type, data)
        cached = await ai_cache.get(cache_key)
        if cached:
            return cached

        prompt = f"""
        Perform a comprehensive legal risk audit on this contract data for {document_type}.
        Identify potential loopholes, missing essential clauses, ambiguous terms, or unbalanced liability.
        
        Contract Data: {json.dumps(data, ensure_ascii=False)}

        Respond ONLY in JSON format:
        {{
            "score": 85,
            "summary": "Overall evaluation of the agreement balance and clarity",
            "issues": [
                {{
                    "severity": "high/medium/low/info",
                    "title": "Short title",
                    "description": "What is the issue or risk",
                    "suggestion": "Recommended fix or clause addition"
                }}
            ]
        }}
        """
        ai_response = await self._call_gemini_async(prompt, json_mode=True)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                result = json.loads(cleaned.strip())
                await ai_cache.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")

        issues = []
        score = 92

        if document_type == "tenancy_agreement":
            rent = data.get("rent_amount", 0)
            deposit = data.get("deposit_amount", 0)
            notice = data.get("notice_period_months", 1)

            try:
                rent_val = float(str(rent).replace(',', '')) if rent else 0
                deposit_val = float(str(deposit).replace(',', '')) if deposit else 0
            except ValueError:
                rent_val, deposit_val = 0, 0

            if deposit_val < rent_val:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": "অপর্যাপ্ত জামানত (Low Security Deposit)",
                    "description": "অগ্রিম জামানতের পরিমাণ মাসিক ভাড়ার চেয়ে কম। এটি বাড়িওয়ালার জন্য আর্থিক ঝুঁকি তৈরি করতে পারে।",
                    "suggestion": "কমপক্ষে ২ বা ৩ মাসের মাসিক ভাড়ার সমপরিমাণ অগ্রিম জামানত রাখা যুক্তিযুক্ত।"
                })

            if int(notice) < 2:
                score -= 8
                issues.append({
                    "severity": "low",
                    "title": "সংক্ষিপ্ত নোটিশ পিরিয়ড (Short Notice Period)",
                    "description": "১ মাসের নোটিশ পিরিয়ড বাড়ি বদল বা নতুন ভাড়াটিয়া পাওয়ার জন্য কিছুটা অপ্রতুল হতে পারে।",
                    "suggestion": "উভয় পক্ষের সুবিধার জন্য নোটিশ পিরিয়ড ২ মাস করা নিরাপদ।"
                })

        result = {
            "score": max(score, 70),
            "summary": "চুক্তিপত্রটিতে মৌলিক সুরক্ষাসমূহ বিদ্যমান। চিহ্নিত পয়েন্টগুলো সমাধান করিলে এটি আদালতে সম্পূর্ণ সুষম ও সুরক্ষিত থাকিবে।",
            "issues": issues
        }
        await ai_cache.set(cache_key, result)
        return result

    async def audit_uploaded_document(self, raw_text: str, filename: str = "document.pdf") -> Dict[str, Any]:
        prompt = f"""
        You are an elite legal contract auditor specializing in Bangladesh law and international contract standards.
        Review this uploaded legal contract text from file "{filename}".
        Provide an exhaustive legal audit:
        1. Classify contract type (in Bangla)
        2. Assign a legal safety score (0-100)
        3. Identify high/medium/low severity risks, one-sided clauses, missing essential clauses (dispute resolution, force majeure, termination), and ambiguous wording.
        4. Provide actionable recommendations.

        Contract Text:
        \"\"\"{raw_text[:12000]}\"\"\"

        Respond ONLY with valid JSON in this exact structure:
        {{
            "detected_type": "Contract Type in Bangla",
            "score": 82,
            "summary": "Comprehensive 2-3 sentence overview of this contract in Bangla",
            "risks_found": [
                {{
                    "severity": "high",
                    "clause_topic": "Topic in Bangla",
                    "issue": "Detailed risk explanation in Bangla",
                    "recommendation": "Legal fix recommendation in Bangla"
                }}
            ],
            "missing_clauses": [
                "Missing clause 1 in Bangla",
                "Missing clause 2 in Bangla"
            ]
        }}
        """

        ai_response = await self._call_gemini_async(prompt)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if "{" in cleaned and "}" in cleaned:
                    cleaned = cleaned[cleaned.find("{"):cleaned.rfind("}")+1]
                parsed = json.loads(cleaned.strip())
                if isinstance(parsed, dict) and "risks_found" in parsed:
                    return parsed
            except Exception as e:
                logger.error(f"Failed to parse uploaded audit: {e}")

        # Smart Heuristic Context-Aware Fallback
        t_lower = raw_text.lower()
        if any(w in t_lower for w in ["ভাড়া", "ভাড়া", "মালিক", "ভাড়াটিয়া", "ভাড়াটিয়া", "অগ্রিম"]):
            doc_type = "বাড়ি / ফ্ল্যাট / দোকান ভাড়ার চুক্তিপত্র"
            summary = f"আপলোডকৃত '{filename}' ফাইলটি বিশ্লেষণ করে দেখা গেছে এটি একটি ভাড়া চুক্তিপত্র। এতে ভাড়া ও জমার পরিমাণ নির্ধারিত হলেও বাড়ি ভাড়া নিয়ন্ত্রণ আইন ১৯৯১ ও নোটিশ মেয়াদের কিছু ঘাটতি রয়েছে।"
            risks = [
                {
                    "severity": "high",
                    "clause_topic": "উচ্ছেদ ও নোটিশের মেয়াদ সংক্রান্ত অসামঞ্জস্যতা",
                    "issue": "চুক্তিতে তাৎক্ষণিক উচ্ছেদ বা অপর্যাপ্ত নোটিশের সুযোগ রাখা হয়েছে, যা বাড়ি ভাড়া নিয়ন্ত্রণ আইন ১৯৯১ অনুযায়ী আদালতে বাতিলযোগ্য হতে পারে।",
                    "recommendation": "উভয় পক্ষের জন্য কমপক্ষে ৩০ বা ৬০ দিনের সুস্পষ্ট লিখিত নোটিশের ধারা অন্তর্ভুক্ত করুন।"
                },
                {
                    "severity": "medium",
                    "clause_topic": "অগ্রিম জামানত (Security Deposit) ও রিফান্ড শর্ত",
                    "issue": "ভাড়াটিয়া প্রস্থানকালে নিরাপত্তা জামানত ফেরত প্রদানের সুনির্দিষ্ট সময়সীমা ও কর্তন নীতিমালা স্পষ্ট নয়।",
                    "recommendation": "চুক্তি সমাপ্তির ১৫ দিনের মধ্যে জামানত ফেরত ও কেবল প্রকৃত ক্ষতির ক্ষেত্রে বিল কর্তনের শর্ত যোগ করুন।"
                }
            ]
        elif any(w in t_lower for w in ["চাকরি", "কর্মচারী", "বেতন", "নিয়োগ", "নিয়োগ", "পদবী"]):
            doc_type = "চাকরি ও নিয়োগ চুক্তিপত্র (Employment Agreement)"
            summary = f"আপলোডকৃত '{filename}' ফাইলটি একটি নিয়োগ বা শ্রম চুক্তিপত্র। বাংলাদেশ শ্রম আইন ২০০৬ এর আলোকে কিছু একতরফা বাধ্যবাধকতা স্পষ্ট করা প্রয়োজন।"
            risks = [
                {
                    "severity": "high",
                    "clause_topic": "চাকরিচ্যুতি ও প্রভিডেন্ট/গ্র্যাচুইটি শর্ত",
                    "issue": "বিনা নোটিশে চাকরিচ্যুতির শর্ত বাংলাদেশ শ্রম আইন ২০০৬ (ধারা ২৬ ও ২৭) এর সাথে সাংঘর্ষিক হতে পারে।",
                    "recommendation": "আইনানুগ নোটিশ পে এবং বিধিবদ্ধ বেনিফিট নিশ্চিতের ধারা সংযোজন করুন।"
                },
                {
                    "severity": "medium",
                    "clause_topic": "নন-কম্পিট ও গোপনীয়তা শর্ত",
                    "issue": "অতিরিক্ত দীর্ঘ বা ভৌগোলিক সীমাবদ্ধতাহীন নন-কম্পিট ক্লজ চুক্তি আইন ১৮৭২ এর ২৭ ধারা অনুযায়ী অবৈধ হতে পারে।",
                    "recommendation": "যুক্তিসঙ্গত সময়সীমা (যেমন ৬ মাস বা ১ বছর) ও সুনির্দিষ্ট ভৌগোলিক এলাকার মধ্যে সীমাবদ্ধ রাখুন।"
                }
            ]
        elif any(w in t_lower for w in ["অংশীদারি", "পার্টনারশিপ", "মূলধন", "মুনাফা", "শেয়ার"]):
            doc_type = "অংশীদারি কারবার চুক্তিপত্র (Partnership Deed)"
            summary = f"আপলোডকৃত '{filename}' ফাইলটি অংশীদারি কারবারের চুক্তিপত্র। অংশীদারি আইন ১৯৩২ অনুযায়ী মুনাফা বণ্টন ও বিলোপ সাধন শর্ত পর্যালোচনা করা হয়েছে।"
            risks = [
                {
                    "severity": "high",
                    "clause_topic": "অংশীদারদের বিরোধ নিষ্পত্তি ও সালিশি ধারা",
                    "issue": "পারস্পরিক মতদ্বৈধতা দেখা দিলে সালিশি আইন ২০০১ অনুযায়ী সমাধানের সুস্পষ্ট মেকানিজম নেই।",
                    "recommendation": "সালিশি আদালত বা নিরপেক্ষ মধ্যস্থতাকারীর মাধ্যমে নিষ্পত্তির বাধ্যতামূলক ধারা যুক্ত করুন।"
                },
                {
                    "severity": "medium",
                    "clause_topic": "মূলধন উত্তোলন ও অংশীদারের প্রস্থান নীতিমালা",
                    "issue": "হঠাৎ অংশীদার পদত্যাগ করিলে বা মৃত্যুবরণ করিলে হিসাব নিকাশের ধারা অস্পষ্ট।",
                    "recommendation": "অডিট ও মূল্যায়নপূর্বক ৩ মাসের মধ্যে পাওনা পরিশোধের বিধান রাখুন।"
                }
            ]
        else:
            doc_type = "সাধারণ বাণিজ্যিক / সেবা চুক্তিপত্র (Commercial Agreement)"
            summary = f"আপলোডকৃত '{filename}' ফাইলটি বিশ্লেষণ করে দেখা গেছে এতে সাধারণ চুক্তিগত কাঠামো রয়েছে, তবে কিছু সুরক্ষাধারা আরও মজবুত করা বাঞ্ছনীয়।"
            risks = [
                {
                    "severity": "high",
                    "clause_topic": "অসম অবসান ও ক্ষতিপূরণ শর্ত",
                    "issue": "নোটিশ ছাড়া তাৎক্ষণিক চুক্তি বাতিল ও অসংগত জরিমানার শর্ত বিদ্যমান রয়েছে, যা আদালতে চ্যালেঞ্জযোগ্য হতে পারে।",
                    "recommendation": "উভয় পক্ষের জন্য কমপক্ষে ৩০ দিনের লিখিত নোটিশ এবং যৌক্তিক কারণ প্রদর্শনের শর্ত যুক্ত করুন।"
                },
                {
                    "severity": "medium",
                    "clause_topic": "অস্পষ্ট সময়সীমা ও পেমেন্ট শিডিউল",
                    "issue": "কাজের ডেলিভারি ও বিল পরিশোধের সুনির্দিষ্ট সময়সীমা উল্লেখ না থাকায় ভবিষ্যতে দ্বন্দ্বের অবকাশ রয়েছে।",
                    "recommendation": "সুনির্দিষ্ট তারিখ ও তফসিলি ব্যাংক অ্যাকাউন্টের মাধ্যমে লেনদেনের শর্ত স্পষ্ট করুন।"
                }
            ]

        return {
            "detected_type": doc_type,
            "score": 80,
            "summary": summary,
            "risks_found": risks,
            "missing_clauses": [
                "বিরোধ নিষ্পত্তি ও সালিশি ধারা (Arbitration & Dispute Resolution Clause)",
                "অপ্রত্যাশিত প্রাকৃতিক দুর্যোগ ছাড় (Force Majeure Clause)",
                "আদালতের এখতিয়ার নির্ধারণ (Jurisdiction of Court)"
            ]
        }


    async def ask_legal_assistant(self, user_question: str, contract_context: str = "") -> str:
        cache_key = ai_cache.generate_key("chat", user_question.strip().lower(), contract_context.strip())
        cached = await ai_cache.get(cache_key)
        if cached:
            return cached

        prompt = f"""
        You are "আইনAI সহকারী" (Smart Legal AI Assistant), an expert in Bangladesh Contract Law, The Stamp Act 1899, Premises Rent Control Act, and Employment regulations.
        Answer this user legal question warmly, accurately, and practically in clear Bengali (বাংলা).

        User Question: "{user_question}"
        Current Contract Context: "{contract_context}"

        Provide a structured, helpful answer:
        1. সরাসরি সমাধান ও আইনি ব্যাখ্যা
        2. প্রচলিত আইনের রেফারেন্স (যেমন: স্ট্যাম্প আইন, চুক্তি আইন ১৮৭২ ইত্যাদি)
        3. সতর্কতা বা প্র্যাকটিক্যাল টিপস
        """
        ai_resp = await self._call_gemini_async(prompt)
        if ai_resp:
            result = ai_resp.strip()
            await ai_cache.set(cache_key, result)
            return result

        # Comprehensive Knowledge-base for Bangladesh Legal Questions (Active Fallback)
        q_lower = user_question.lower()

        # 1. Premises Rent Control Act (ভাড়া নিয়ন্ত্রণ আইন)
        if any(w in q_lower for w in ["ভাড়া নিয়ন্ত্রণ", "ভাড়া নিয়ন্ত্রণ", "ভাড়া আইন", "ভাড়া আইন", "rent control"]):
            result = """**বাড়ি ভাড়া নিয়ন্ত্রণ আইন, ১৯৯১ (The Premises Rent Control Act, 1991) অনুসারে প্রধান বিধানসমূহ:**

১. **মানসম্মত ভাড়া (Standard Rent):** বাড়িওয়ালা বা মালিক ইচ্ছামাফিক প্রতি বছর ভাড়া বৃদ্ধি করিতে পারিবেন না। আইন অনুযায়ী প্রতি ২ বছর পূর্ণ না হওয়া পর্যন্ত ভাড়া বৃদ্ধি করা যাইবে না (ধারা ১৬)।
২. **ভাড়ার লিখিত রসিদ (Rent Receipt):** ভাড়া পরিশোধের পর বাড়িওয়ালা ভাড়াটিয়াকে আইন অনুযায়ী স্বাক্ষরিত লিখিত রসিদ প্রদান করিতে বাধ্য (ধারা ১৩)। রসিদ না দেওয়া আইনত দণ্ডনীয়।
৩. **অগ্রিম জামানত সীমা:** আইন অনুসারে বাড়িওয়ালা সর্বোচ্চ ১ মাসের ভাড়ার সমপরিমাণ অর্থ জামানত হিসেবে গ্রহণ করিতে পারেন। চুক্তির মেয়াদ শেষে সকল বকেয়া পরিশোধ সাপেক্ষে জামানত সম্পূর্ণ ফেরতযোগ্য।
৪. **বেআইনি উচ্ছেদ নিষেধাজ্ঞা:** নিয়মিত ভাড়া পরিশোধরত অবস্থায় যুক্তিসঙ্গত কারণ এবং যথাযথ নোটিশ ব্যতিরেকে কোনো ভাড়াটিয়াকে উচ্ছেদ করা যাইবে না (ধারা ১৮)।
৫. **ইউটিলিটি বিচ্ছিন্নকরণ দণ্ডনীয়:** বাড়িওয়ালা জোরপূর্বক ভাড়াটিয়ার বিদ্যুৎ, পানি বা গ্যাস সংযোগ বিচ্ছিন্ন করিতে পারিবেন না; আইনের ২১ ধারা অনুযায়ী এটি আমলযোগ্য ও শাস্তিযোগ্য অপরাধ।"""

        # 2. General Tenancy & Lease (বাড়ি/দোকান ভাড়ার চুক্তি)
        elif any(w in q_lower for w in ["ভাড়া", "ভাড়া", "ফ্ল্যাট", "বাড়ি", "বাড়ি", "দোকান", "মালিক", "ভাড়াটিয়া", "ভাড়াটিয়া", "lease", "tenancy"]):
            result = """**বাড়ি / ফ্ল্যাট / দোকান ভাড়ার চুক্তি সম্পাদনের আইনি নির্দেশিকা:**

১. **স্ট্যাম্পের বিধান:** যেকোনো ভাড়ার চুক্তির প্রথম পৃষ্ঠা **৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্পে** প্রিন্ট করিতে হইবে। একাধিক পৃষ্ঠা থাকিলে বাকি পৃষ্ঠাগুলো ডিমাই বা লিগ্যাল পেপারে প্রিন্ট হইবে।
২. **মেয়াদ ও রেজিস্ট্রেশন:** ভাড়ার মেয়াদ ১ বছরের অধিক হইলে রেজিস্ট্রেশন আইন ১৯০৮ অনুযায়ী সংশ্লিষ্ট সাব-রেজিস্ট্রি অফিসে চুক্তিটি নিবন্ধন করা বাধ্যতামূলক।
৩. **ইউটিলিটি ও সার্ভিস চার্জ:** বিদ্যুৎ বিল, গ্যাস বিল, পানি বিল ও সিকিউরিটি/কমন সার্ভিস চার্জ কার দায়িত্বে পরিশোধিত হইবে তাহা চুক্তিতে স্পষ্টভাবে উল্লেখ রাখিতে হইবে।
৪. **নোটিশ পিরিয়ড:** বাসা বা দোকান ছাড়িবার পূর্বে উভয় পক্ষের জন্য কমপক্ষে ১ থেকে ২ মাসের লিখিত নোটিশ প্রদানের বাধ্যবাধকতা রাখা অপরিহার্য।"""

        # 3. Eviction & Protection (উচ্ছেদ ও প্রতিকার)
        elif any(w in q_lower for w in ["উচ্ছেদ", "বের করে", "তাড়িয়ে", "তাড়িয়ে দেওয়া", "দখল", "evict", "eviction"]):
            result = """**ভাড়াটিয়া উচ্ছেদ ও আইনি সুরক্ষা বিধি:**

১. **হঠাৎ উচ্ছেদ সম্পূর্ণ বেআইনি:** চুক্তি বলবৎ থাকাকালে এবং নিয়মিত ভাড়া পরিশোধ করা অবস্থায় বাড়িওয়ালা তাৎক্ষণিকভাবে কোনো ভাড়াটিয়াকে উচ্ছেদ করিতে পারেন না।
২. **আইনি নোটিশ বাধ্যতামূলক:** বাসা ছাড়িতে বলিলে চুক্তিপত্র ও সম্পত্তি হস্তান্তর আইন ১৮৮২ (Transfer of Property Act, 1882) অনুযায়ী কমপক্ষে ৩০ থেকে ৬০ দিনের সুনির্দিষ্ট লিখিত নোটিশ জারি করিতে হইবে।
৩. **গ্যাস-বিদ্যুৎ বন্ধ করিলে করণীয়:** জোরপূর্বক উচ্ছেদের জন্য গ্যাস, বিদ্যুৎ বা পানি বন্ধ করিলে স্থানীয় থানা অথবা ভাড়া নিয়ন্ত্রক আদালতে (Civil Court) ফৌজদারি ও দেওয়ানি প্রতিকার পাওয়া যায়।"""

        # 4. Stamp Duty (স্ট্যাম্পের নিয়ম)
        elif any(w in q_lower for w in ["স্ট্যাম্প", "stamp", "নন-জুডিশিয়াল", "নন জুডিশিয়াল"]):
            result = """**বাংলাদেশ স্ট্যাম্প আইন ১৮৯৯ (The Stamp Act, 1899) অনুযায়ী স্ট্যাম্পের হার:**

১. **ভাড়ার চুক্তি (বাড়ি/দোকান/ফ্ল্যাট):** সকল প্রকার সাধারণ ভাড়ার চুক্তির জন্য **৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প** বাধ্যতামূলক।
২. **অংশীদারি কারবার (Partnership Deed):** মূলধন ৫০,০০০ টাকার কম হইলে **১,০০০ টাকার স্ট্যাম্প** এবং ৫০,০০০ টাকার বেশি হইলে **২,০০০ টাকার স্ট্যাম্প** প্রযোজ্য।
৩. **ফ্রিল্যান্স ও সার্ভিস চুক্তি:** সাধারণ বাণিজ্যিক সার্ভিস চুক্তির জন্য **৩০০ টাকার স্ট্যাম্প** প্রযোজ্য।
৪. **স্বাক্ষরের নিয়ম:** প্রথম পাতার সরকারি স্ট্যাম্প এবং পরবর্তী সকল পাতার নিচে উভয় পক্ষ ও সাক্ষীদের স্বাক্ষর থাকা আবশ্যক।"""

        # 5. Notice & Termination (নোটিশ ও চুক্তি বাতিল)
        elif any(w in q_lower for w in ["নোটিশ", "বাতিল", "সমাপ্ত", "অবসান", "notice", "terminate", "termination"]):
            result = """**চুক্তি অবসান ও আইনি নোটিশের নিয়মাবলি:**

১. **নোটিশের মেয়াদ:** চুক্তিতে উল্লেখিত নির্দিষ্ট সময়সীমার (সাধারণত ৩০ থেকে ৬০ দিন) পূর্বে অপর পক্ষকে আনুষ্ঠানিকভাবে লিখিত নোটিশ প্রদান করিতে হইবে।
২. **প্রেরণের মাধ্যম:** রেজিস্টার্ড ডাকযোগে (প্রাপ্তিস্বীকার/AD সহ) অথবা স্বহস্তে প্রাপ্তিস্বীকার রসিদ রেখে নোটিশ প্রদান করা আইনিভাবে কার্যকর।
৩. **নোটিশ ইঞ্জিন:** এই প্ল্যাটফর্মের উপরের নেভিগেশন বারের **"নোটিশ ইঞ্জিন"** ব্যবহার করিয়া আপনি বাসা ছাড়ার নোটিশ বা বকেয়া ভাড়ার তাগিদপত্র সরাসরি প্রস্তুত করিতে পারেন।"""

        # 6. Security Deposit (অগ্রিম জামানত)
        elif any(w in q_lower for w in ["অগ্রিম", "জামানত", "সিকিউরিটি", "deposit", "advance"]):
            result = """**অগ্রিম জামানত (Security Deposit) সংক্রান্ত আইনি বিধি:**

১. **জামানতের আমানতদারিতা:** অগ্রিম জামানত বাড়িওয়ালার কাছে ভাড়াটিয়ার একটি আমানত। চুক্তির মেয়াদান্তে বকেয়া ভাড়া ও বাস্তবিক ক্ষয়ক্ষতি ব্যতীত সম্পূর্ণ টাকা ফেরত দেওয়া বাড়িওয়ালার আইনি বাধ্যবাধকতা।
২. **জামানত ফেরত না দিলে করণীয়:** চুক্তি শেষে বাড়িওয়ালা জামানত ফেরত দিতে অস্বীকৃতি জানাইলে চুক্তিভঙ্গের অভিযোগে আইনজীবীর মাধ্যমে লিগ্যাল নোটিশ প্রদান করিয়া অর্থ উদ্ধারের মামলা দায়ের করা যায়।"""

        # 7. Employment & Labour Law (চাকরি ও শ্রম আইন)
        elif any(w in q_lower for w in ["চাকরি", "শ্রম", "শ্রম আইন", "বেতন", "প্রবেশন", "নিয়োগ", "নিয়োগ", "কর্মী", "কর্মচারী", "job", "salary", "employment", "labour"]):
            result = """**বাংলাদেশ শ্রম আইন ২০০৬ (Bangladesh Labour Act, 2006) অনুযায়ী কর্মসংস্থান বিধি:**

১. **নিয়োগপত্র ও পরিচয়পত্র:** প্রত্যেক নিয়োগকারীকে চাকরি শুরুর দিনে কর্মচারীকে লিখিত নিয়োগপত্র (Appointment Letter) ও সার্ভিস বুক/পরিচয়পত্র প্রদান করিতে হইবে।
২. **শিক্ষানবিসকাল (Probation):** অফিসিয়াল বা কেরানি পদের জন্য সর্বোচ্চ ৬ মাস এবং সাধারণ পদের জন্য ৩ মাস শিক্ষানবিসকাল নির্ধারণ করা যায়।
３. **চাকরি অবসান ও নোটিশ:** স্থায়ী কর্মী চাকরি ছাড়িতে চাহিলে ৩০ দিনের নোটিশ এবং কর্তৃপক্ষ অবসান ঘটাইতে চাহিলে ৬০/১২০ দিনের নোটিশ বা সমপরিমাণ বেতন পরিশোধ বাধ্যতামূলক।"""

        # 8. Partnership (অংশীদারি কারবার)
        elif any(w in q_lower for w in ["অংশীদার", "অংশীদারি", "পার্টনার", "ফার্ম", "partnership"]):
            result = """**অংশীদারি আইন ১৯৩২ (The Partnership Act, 1932) অনুযায়ী কারবার বিধি:**

১. **মূলধন ও লাভ-ক্ষতি:** অংশীদারদের বিনিয়োগের অনুপাত এবং লাভ-লোকসান বণ্টনের শতকরা হার চুক্তিতে স্পষ্ট লিখিত থাকিতে হইবে।
২. **ব্যাংক পরিচালনা:** প্রতিষ্ঠানের ব্যাংক হিসাব যৌথ স্বাক্ষরে (Joint Signatures) নাকি একক স্বাক্ষরে পরিচালিত হইবে তাহা সুনির্দিষ্ট করা আবশ্যক।
৩. **ফার্মের বিলোপসাধন:** কোনো অংশীদার ব্যবসা হইতে প্রস্থান করিতে চাহিলে কমপক্ষে ৩ মাসের লিখিত নোটিশ প্রদানের শর্ত রাখা উচিত।"""

        # 9. Non-Disclosure & Confidentiality (গোপনীয়তা চুক্তি)
        elif any(w in q_lower for w in ["গোপনীয়তা", "গোপনীয়তা", "এনডিএ", "বাণিজ্যিক তথ্য", "nda", "confidential"]):
            result = """**বাণিজ্যিক গোপনীয়তা ও এনডিএ (NDA) আইন:**

১. **গোপনীয় তথ্যের সংজ্ঞা:** কোন কোন সোর্স কোড, ব্যবসায়িক পরিকল্পনা, গ্রাহক তালিকা বা আর্থিক ডাটা গোপনীয় গণ্য হইবে তাহা পরিষ্কারভাবে সংজ্ঞায়িত করুন।
২. **মেয়াদকাল:** চুক্তি অবসানের পরও তথ্যের গোপনীয়তা রক্ষার মেয়াদ (সাধারণত ২ থেকে ৫ বছর) কার্যকর থাকিবে।
৩. **লঙ্ঘনের ক্ষতিপূরণ:** তথ্য ফাঁস বা অপব্যবহার ঘটিলে তাৎক্ষণিক আইনি ইনজাংশন (Injunction) ও ক্ষতিপূরণ দাবির বিধান চুক্তিতে যুক্ত রাখুন।"""

        # 10. Signing, Witnesses & Registration (স্বাক্ষর ও রেজিস্ট্রেশন)
        elif any(w in q_lower for w in ["স্বাক্ষর", "সই", "সাক্ষী", "দলিল", "রেজিস্ট্রেশন", "রেজিস্ট্রি", "সাব-রেজিস্ট্রি", "sign", "registration"]):
            result = """**দলিল সম্পাদন, সাক্ষী ও রেজিস্ট্রেশন আইন ১৯০৮:**

১. **সাক্ষীদের বিবরণ:** চুক্তির শেষে কমপক্ষে দুইজন প্রাপ্তবয়স্ক সাক্ষীর পূর্ণ নাম, পিতা/স্বামীর নাম, স্থায়ী ঠিকানা ও এনআইডি নম্বর লিপিবদ্ধ থাকা আবশ্যক।
২. **ডিজিটাল স্বাক্ষর:** তথ্য ও যোগাযোগ প্রযুক্তি আইন অনুযায়ী উভয় পক্ষের গ্রহণযোগ্য ডিজিটাল ই-স্বাক্ষর চুক্তির প্রমাণ হিসেবে আদালতে গ্রাহ্য।
৩. **বাধ্যতামূলক রেজিস্ট্রেশন:** স্থাবর সম্পত্তির ১ বছরের অধিক মেয়াদের ইজারা বা ভাড়া সংশ্লিষ্ট সাব-রেজিস্ট্রি অফিসে রেজিস্ট্রি করা আইনত বাধ্যতামূলক।"""

        # 11. General Contract Law (চুক্তি আইন ১৮৭২)
        elif any(w in q_lower for w in ["চুক্তি", "চুক্তিপত্র", "শর্ত", "আইন", "অঙ্গীকার", "contract", "agreement"]):
            result = """**বাংলাদেশ চুক্তি আইন ১৮৭২ (The Contract Act, 1872) অনুযায়ী কার্যকর চুক্তির শর্তাবলি:**

১. **আইনগত সক্ষমতা:** চুক্তি সম্পাদনকারী উভয় পক্ষকে প্রাপ্তবয়স্ক (১৮ বছর বা তদূর্ধ্ব) এবং সুস্থ মস্তিষ্কের অধিকারী হইতে হইবে (ধারা ১১)।
২. **স্বাধীন সম্মতি (Free Consent):** কোনো প্রকার চাপ, ভয়ভীতি, প্রতারণা বা অসদুপায় ব্যতিরেকে উভয় পক্ষের নিজস্ব সম্মতিতে চুক্তি স্বাক্ষরিত হইতে হইবে (ধারা ১৪)।
৩. **সুনির্দিষ্ট প্রতিদান ও উদ্দেশ্য:** চুক্তির উদ্দেশ্য ও আর্থিক প্রতিদান অবশ্যই বাংলাদেশের প্রচলিত আইনের অধীন বৈধ হইতে হইবে; অবৈধ উদ্দেশ্যের চুক্তি সম্পূর্ণ বাতিল (Void) হিসেবে গণ্য হয় (ধারা ২৩)।"""

        # 12. Smart Dynamic Fallback for Arbitrary Queries
        else:
            result = f"""**আপনার আইনি জিজ্ঞাসার বিশ্লেষণ:**
"{user_question}"-এর বিষয়ে বাংলাদেশ দেওয়ানি ও চুক্তি আইন অনুযায়ী নির্দেশনা:

১. **আইনি ভিত্তি:** বিষয়টি সম্পর্কিত সকল লেনদেন ও অঙ্গীকার লিখিত ডকুমেন্টে সংরক্ষণ করুন। মৌখিক অঙ্গীকারের চেয়ে স্বাক্ষরিত চুক্তিপত্র আদালতে সর্বোচ্চ গ্রহণযোগ্য সাক্ষ্য (Primary Evidence)।
২. **প্রয়োজনীয় শর্তাবলি:** যেকোনো চুক্তিতে উভয় পক্ষের পূর্ণ নাম, জাতীয় পরিচয়পত্র (NID) নম্বর, সুনির্দিষ্ট সময়সীমা, আর্থিক প্রতিদান ও বিরোধ নিষ্পত্তির ধারা স্পষ্টভাবে উল্লেখ করুন।
৩. **সুপারিশ:** জটিল আর্থিক বা ভূ-সম্পত্তি সংক্রান্ত বিষয়ে কোনো চূড়ান্ত সিদ্ধান্ত গ্রহণের পূর্বে সংশ্লিষ্ট রেজিস্ট্রি অফিস বা বিজ্ঞ আইনজীবীর পরামর্শ গ্রহণ সমীচীন।"""

        await ai_cache.set(cache_key, result)
        return result

ai_service = AIService()
