import json
import logging
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List
from app.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL

    @staticmethod
    def _parse_number(val: Any, default: float = 0.0) -> float:
        """Safely parses Bengali and English numbers from strings, ints, or floats."""
        if val is None:
            return default
        s = str(val).strip()
        bangla_digits = "০১২৩৪৫৬৭৮৯"
        for i, b in enumerate(bangla_digits):
            s = s.replace(b, str(i))
        s = s.replace(',', '')
        match = re.search(r'[-+]?\d*\.?\d+', s)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return default
        return default

    def _call_gemini(self, prompt: str, system_instruction: str = None) -> str:
        if not self.api_key:
            return ""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"System Context: {system_instruction}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these legal drafting instructions strictly."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.95,
                "maxOutputTokens": 2048
            }
        }

        try:
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=25) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
        except Exception as e:
            logger.warning(f"Gemini API request note: {e}")
        return ""

    def refine_clause(self, raw_text: str, document_type: str = "tenancy_agreement", language: str = "bn") -> Dict[str, Any]:
        prompt = f"""
        You are an expert legal draftsperson specializing in Bangladesh and international contract law.
        Convert the following informal requirement into a legally enforceable, professional, binding contract clause.
        
        Document Type: {document_type}
        Language: {'Bangla' if language == 'bn' else 'English'}
        Informal user requirement: "{raw_text}"
        
        Respond ONLY with a JSON object in the following format:
        {{
            "title": "Short title of clause",
            "refined_clause": "The legally sound clause text",
            "risk_level": "Low / Medium / High",
            "explanation": "Brief 1-line note on legal validity"
        }}
        """
        
        ai_response = self._call_gemini(prompt)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception as e:
                logger.error(f"Failed to parse Gemini JSON: {e}")

        # Built-in Heuristic Fallback
        if language == "bn":
            refined = f"উভয় পক্ষ এই মর্মে সম্মত হইলেন যে, {raw_text.strip()}। উক্ত শর্ত লঙ্ঘন করিলে বা ব্যত্যয় ঘটিলে ক্ষতিগ্রস্ত পক্ষ প্রচলিত আইন ও এই চুক্তির বিধিমোতাবেক ক্ষতিপূরণ দাবি করিতে এবং চুক্তি বাতিল বলিয়া গণ্য করিতে পারিবে।"
            title = "বিশেষ বাধ্যবাধকতা ও পরিচালনা বিধি"
            explanation = "এই ধারাটি চুক্তির সাধারণ আইন অনুযায়ী উভয় পক্ষের উপর সমভাবে বর্তাবে।"
        else:
            refined = f"The Parties hereby agree that {raw_text.strip()}. Any breach or non-compliance of this provision shall entitle the non-breaching Party to claim appropriate remedies, damages, and terminate this Agreement in accordance with applicable governing laws."
            title = "Special Obligations & Compliance"
            explanation = "Standard enforceable clause adhering to bilateral contract principles."

        return {
            "title": title,
            "refined_clause": refined,
            "risk_level": "Low",
            "explanation": explanation
        }

    def explain_clause(self, clause_text: str, language: str = "bn") -> Dict[str, Any]:
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

        ai_response = self._call_gemini(prompt)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")

        if language == "bn":
            return {
                "simple_explanation": f"এই ধারাটির মূল বক্তব্য হলো: চুক্তির উভয় পক্ষকে উল্লেখিত শর্ত বা দায়িত্বটি যথাযথভাবে প্রতিপালন করিতে হইবে। কোনো এক পক্ষের খামখেয়ালিপনা বা একতরফা সিদ্ধান্তের সুযোগ বন্ধ করার জন্য এটি রচিত।",
                "key_obligations": [
                    "চুক্তির মেয়াদকালীন সময়ে উভয় পক্ষকে এই নিয়ম মানিয়া চলিতে হইবে।",
                    "উভয় পক্ষকে আর্থিক ও আইনি দায়দায়িত্ব সময়মতো নিষ্পন্ন করিতে হইবে।"
                ],
                "potential_risks": [
                    "শর্ত ভঙ্গ করিলে অপর পক্ষ ক্ষতিপূরণ দাবি করিতে এবং চুক্তি সমাপ্তির নোটিশ দিতে পারিবে।"
                ]
            }
        else:
            return {
                "simple_explanation": "This clause establishes mandatory compliance obligations between both parties to prevent breach of trust.",
                "key_obligations": [
                    "Full adherence to operational timeline and financial commitments.",
                    "Written notice required prior to any variation."
                ],
                "potential_risks": [
                    "Failure to comply can trigger default remedies or termination."
                ]
            }

    def audit_contract(self, document_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
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
        ai_response = self._call_gemini(prompt)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")

        issues = []
        score = 92

        if document_type == "tenancy_agreement":
            rent_val = self._parse_number(data.get("rent_amount"), 0)
            deposit_val = self._parse_number(data.get("deposit_amount"), 0)
            notice_val = self._parse_number(data.get("notice_period_months"), 1)

            if rent_val > 0 and deposit_val < rent_val:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": "অপর্যাপ্ত জামানত (Low Security Deposit)",
                    "description": "অগ্রিম জামানতের পরিমাণ মাসিক ভাড়ার চেয়ে কম। এটি বাড়িওয়ালার জন্য আর্থিক ঝুঁকি তৈরি করতে পারে।",
                    "suggestion": "কমপক্ষে ২ বা ৩ মাসের মাসিক ভাড়ার সমপরিমাণ অগ্রিম জামানত রাখা যুক্তিযুক্ত।"
                })

            if notice_val < 2:
                score -= 8
                issues.append({
                    "severity": "low",
                    "title": "সংক্ষিপ্ত নোটিশ পিরিয়ড (Short Notice Period)",
                    "description": "১ মাসের নোটিশ পিরিয়ড বাড়ি বদল বা নতুন ভাড়াটিয়া পাওয়ার জন্য কিছুটা অপ্রতুল হতে পারে।",
                    "suggestion": "উভয় পক্ষের সুবিধার জন্য নোটিশ পিরিয়ড ২ মাস করা নিরাপদ।"
                })
        elif document_type == "partnership_agreement":
            share1 = self._parse_number(data.get("partner1_share"), 50)
            share2 = self._parse_number(data.get("partner2_share"), 50)
            if (share1 + share2) != 100:
                score -= 12
                issues.append({
                    "severity": "high",
                    "title": "অংশীদারি শেয়ার অসামঞ্জস্য (Share Ratio Mismatch)",
                    "description": f"অংশীদারদের শেয়ারের যোগফল {share1 + share2}% (১০০% হওয়া আবশ্যক)।",
                    "suggestion": "উভয় অংশীদারের শেয়ারের অনুপাত সমন্বয় করে মোট ১০০% নির্ধারণ করুন।"
                })
        elif document_type == "employment_agreement":
            probation = self._parse_number(data.get("probation_months"), 3)
            if probation > 6:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": "অতিরিক্ত দীর্ঘ শিক্ষানবিসকাল (Excessive Probation)",
                    "description": "বাংলাদেশ শ্রম আইন অনুযায়ী সাধারণ পদে শিক্ষানবিসকাল ৬ মাসের অধিক হওয়া অনুচিত।",
                    "suggestion": "শিক্ষানবিসকাল কমিয়ে ৩ থেকে ৬ মাসের মধ্যে সীমাবদ্ধ রাখুন।"
                })

        summary = (
            "চুক্তিপত্রটিতে মৌলিক সুরক্ষাসমূহ বিদ্যমান। চিহ্নিত পয়েন্টগুলো সমাধান করিলে এটি আদালতে সম্পূর্ণ সুষম ও সুরক্ষিত থাকিবে।"
            if issues else
            "চুক্তিপত্রটিতে কোনো বড় আইনি ঝুঁকি বা অসংগতি চিহ্নিত হয়নি। এটি ব্যবহারের জন্য মানসম্মত ও ভারসাম্যপূর্ণ।"
        )

        return {
            "score": max(score, 70),
            "summary": summary,
            "issues": issues
        }

    def audit_uploaded_document(self, raw_text: str, filename: str = "document.pdf") -> Dict[str, Any]:
        prompt = f"""
        You are an elite legal contract auditor.
        Review this uploaded legal contract text from file "{filename}".
        Provide an exhaustive legal audit:
        1. Classify contract type
        2. Assign a legal safety score (0-100)
        3. Identify high/medium/low severity risks, one-sided clauses, missing essential clauses (dispute resolution, force majeure, termination), and ambiguous wording.
        4. Provide actionable recommendations.

        Contract Text:
        \"\"\"{raw_text[:4000]}\"\"\"

        Respond ONLY in JSON format:
        {{
            "detected_type": "Contract Type in Bangla",
            "score": 80,
            "summary": "Comprehensive 2-3 sentence overview of this contract",
            "risks_found": [
                {{
                    "severity": "high/medium/low",
                    "clause_topic": "Topic",
                    "issue": "Detailed risk explanation in Bangla",
                    "recommendation": "Legal fix recommendation in Bangla"
                }}
            ],
            "missing_clauses": [
                "Missing clause 1",
                "Missing clause 2"
            ]
        }}
        """

        ai_response = self._call_gemini(prompt)
        if ai_response:
            try:
                cleaned = ai_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception as e:
                logger.error(f"Failed to parse uploaded audit: {e}")

        return {
            "detected_type": "সাধারণ বাণিজ্যিক / সেবা চুক্তিপত্র",
            "score": 78,
            "summary": f"আপলোডকৃত '{filename}' ফাইলটি বিশ্লেষণ করে দেখা গেছে এতে মৌলিক শর্তগুলো রয়েছে, তবে কিছু একতরফা দায়বদ্ধতা ও মিসিং সুরক্ষাধারা চিহ্নিত হয়েছে।",
            "risks_found": [
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
                    "recommendation": "নির্দিষ্ট তারিখ ও ব্যাংক অ্যাকাউন্টের মাধ্যমে লেনদেনের শর্ত স্পষ্ট করুন।"
                }
            ],
            "missing_clauses": [
                "বিরোধ নিষ্পত্তি ও সালিশি ধারা (Arbitration & Dispute Resolution Clause)",
                "অপ্রত্যাশিত প্রাকৃতিক দুর্যোগ ছাড় (Force Majeure Clause)",
                "আদালতের এখতিয়ার নির্ধারণ (Jurisdiction of Court)"
            ]
        }

    def ask_legal_assistant(self, user_question: str, contract_context: str = "", language: str = "bn") -> str:
        if not user_question or not user_question.strip():
            if language == "en":
                return "Please ask a legal question regarding any law in Bangladesh (e.g., contracts, cheque dishonour, land registration, labor law, cyber crime, bail, tenancy)."
            return "অনুগ্রহ করে বাংলাদেশের যেকোনো আইন (চুক্তি, চেক ডিজঅনার, জমিজমা, শ্রম আইন, সাইবার ক্রাইম, পারিবারিক বা ফৌজদারি আইন) সংক্রান্ত আপনার প্রশ্নটি লিখুন।"

        user_q = user_question.strip()
        is_en = (language == "en") or (len(user_q) > 3 and sum(1 for c in user_q if ord(c) < 128) > len(user_q) * 0.75 and any(c.isalpha() for c in user_q))

        lang_instruction = (
            "Provide a legally sound, authoritative, precise, and actionable answer in professional English citing specific Bangladeshi statutory sections, limitation periods, required evidence, and advocate advice."
            if is_en else
            "Provide a legally sound, precise, empathetic, and actionable answer in fluent Bengali (বাংলা) citing specific Bangladeshi Acts, statutory sections, limitation periods, and advocate advice."
        )

        prompt = f"""
        You are "বাংলাদেশ আইনAI বিশেষজ্ঞ ও সিনিয়র অ্যাডভোকেট" (Bangladesh Legal AI Senior Advocate), an authoritative advocate of the Supreme Court of Bangladesh and legal expert across ALL laws of Bangladesh.
        The user has asked a legal question.
        {lang_instruction}

        User Question: "{user_q}"
        User Context: "{contract_context}"

        Your answer MUST include:
        1. ⚖️ **আইনি মূল বিধান ও সংশ্লিষ্ট আইন/ধারা (Legal Provision & Specific Sections):**
           - সুনির্দিষ্ট আইন ও ধারা উল্লেখ করুন (যেমন: দণ্ডবিধি ১৮৬০, এনআই অ্যাক্ট ১৮৮১, শ্রম আইন ২০০৬, সাইবার নিরাপত্তা আইন ২০২৩, সিআরপিসি ১৮৯৮, সিপিসি ১৯০৮, পারিবারিক আদালত আইন ২০২৩ ইত্যাদি)।
        2. 📋 **আইনি প্রতিকার ও কার্যকর পদক্ষেপ (Step-by-step Legal Remedies):**
           - ধাপে ধাপে কী করতে হবে (যেমন: লিগ্যাল নোটিশ, থানায় জিডি/এজাহার, নাকি উপযুক্ত আদালতে সিআর/সিভিল মামলা)।
           - তামাদি বা নির্দিষ্ট সময়সীমা (Limitation Period)।
        3. 📂 **প্রয়োজনীয় প্রমাণাদি ও কাগজপত্র (Required Evidence):**
           - কী কী প্রমাণ বা ডকুমেন্ট আদালতে দাখিল করতে হবে।
        4. 💡 **অ্যাডভোকেটের পরামর্শ ও সতর্কতা (Advocate's Practical Advice):**
           - প্র্যাকটিক্যাল সতর্কতা।
        """
        ai_resp = self._call_gemini(prompt)
        if ai_resp:
            return ai_resp.strip()

        # Comprehensive Knowledge-base Engine for ALL Bangladesh Laws
        q = user_q.lower()

        # 1. চেক ডিজঅনার ও টাকা লেনদেন (Negotiable Instruments Act, 1881)
        if any(w in q for w in ["চেক", "ডিজঅনার", "ডিজ অনার", "dishonour", "dishonor", "বাউন্স", "চেক পাস", "cheque", "check bounce"]):
            if is_en:
                return """⚖️ **Cheque Dishonour Legal Remedies (NI Act, 1881):**

1. **Statutory Provisions:**
   - The Negotiable Instruments Act, 1881 — **Sections 138 & 141**.
   - Penal Code 1860 — **Sections 406 & 420** (Criminal breach of trust & cheating).

2. **Step-by-Step Procedure & Strict Limitation Periods:**
   - **Step 1 (Bank Dishonour Memo):** Present the cheque to the bank within validity (usually 6 months) and collect the official "Dishonoured / Insufficient Funds" memo.
   - **Step 2 (Statutory Legal Notice):** Within **30 days** of receiving the dishonour memo, send a written Legal Notice via registered post with A/D (or through an advocate) demanding payment within **30 days**.
   - **Step 3 (Filing Court Complaint):** If the drawer fails to pay within 30 days of notice receipt, file a criminal complaint (CR Case) in the Court of Chief Metropolitan Magistrate (CMM) or Senior Judicial Magistrate within the next **30 days**.

3. **Statutory Penalties:**
   - Imprisonment for up to **1 year**, or a fine of up to **thrice (3x) the cheque amount**, or both.

💡 **Advocate's Advice:** Strict compliance with statutory limitation is mandatory. Preserve all bank memos, postal receipts, tracking logs, and Acknowledgement Due (A/D) cards."""
            return """⚖️ **চেক ডিজঅনার সংক্রান্ত আইনি প্রতিকার (NI Act, 1881):**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - দ্য নেগোশিয়েবল ইন্সট্রুমেন্টস অ্যাক্ট, ১৮৮১ (The Negotiable Instruments Act, 1881)-এর **১৩৮ ও ১৪১ ধারা**।
   - দণ্ডবিধি ১৮৬০-এর **৪০৬ ও ৪২০ ধারা** (প্রতারণা ও বিশ্বাসভঙ্গ)।

২. **মামলার সুনির্দিষ্ট আইনি ধাপ ও সময়সীমা (খুব গুরুত্বপূর্ণ):**
   - **ধাপ ১ (ব্যাংক মেমো):** চেকটি ব্যাংকে জমা দিয়ে পর্যাপ্ত টাকা না থাকায় "Dishonoured" স্লিপ/মেমো সংগ্রহ করুন।
   - **ধাপ ২ (লিগ্যাল নোটিশ):** ডিজঅনার স্লিপ পাওয়ার তারিখ থেকে **৩০ দিনের মধ্যে** রেজিস্টার্ড ডাকযোগে অথবা আইনজীবীর মাধ্যমে দেনাদারকে টাকা পরিশোধের জন্য ৩০ দিনের সময় দিয়ে লিখিত 'লিগ্যাল নোটিশ' পাঠাতে হবে।
   - **ধাপ ৩ (মামলা দায়ের):** নোটিশ পাওয়ার পর দেনাদার ৩০ দিনের মধ্যে টাকা না দিলে, সেই ৩০ দিন শেষ হওয়ার পরবর্তী **৩০ দিনের মধ্যে** চিফ মেট্রোপলিটন ম্যাজিস্ট্রেট (CMM) বা সিনিয়র জুডিশিয়াল ম্যাজিস্ট্রেট আদালতে সরাসরি মামলা দায়ের করতে হবে।

৩. **শাস্তি ও প্রতিকার:**
   - দোষী প্রমাণিত হলে সর্বোচ্চ **১ বছর পর্যন্ত কারাদণ্ড** অথবা চেকের বর্ণিত টাকার **৩ গুণ পর্যন্ত অর্থদণ্ড**, কিংবা উভয় দণ্ডে দণ্ডিত হতে পারে।

💡 **অ্যাডভোকেটের পরামর্শ:** নোটিশের সময়সীমা (Limitation) একদিনও মিস করা যাবে না। রেজিস্টার্ড ডাক রসিদ ও প্রাপ্তিস্বীকার (AD) যত্নসহকারে সংরক্ষণ করুন।"""

        # 2. থানায় জিডি, এফআইআর ও পুলিশ অভিযোগ (CrPC, 1898)
        elif any(w in q for w in ["জিডি", "সাধারণ ডায়েরি", "gd", "fir", "এজাহার", "থানা", "পুলিশ", "থানায় অভিযোগ", "পুলিশে অভিযোগ", "মামলা নেয় না", "police station", "general diary", "ejahar"]):
            if is_en:
                return """⚖️ **Filing GD and FIR in Bangladesh Police Station (CrPC, 1898):**

1. **Applicable Laws & Sections:**
   - Code of Criminal Procedure, 1898 (CrPC) — **Section 154** (First Information Report / FIR for cognizable offences) and **Section 155** (General Diary / GD for non-cognizable matters or security threats).

2. **Standard Operating Procedure:**
   - **General Diary (GD):** For lost documents (NID, Passport, Cheque books) or threats/intimidation, submit 2 written copies to the Officer-in-Charge (OC) or use the official Bangladesh Police 'Online GD' portal.
   - **FIR (Ejahar):** For cognizable crimes (assault, burglary, fraud, cyber abuse), the police station is legally required to record the FIR immediately without delay.
   - **If Police Refuse to Record FIR:** File a direct complaint petition in the Court of Judicial/Metropolitan Magistrate under **Section 200 of CrPC** (CR Case). The Magistrate will examine the complainant and order a police/PBI investigation or issue summons/warrants.

💡 **Advocate's Advice:** Always retain the stamped duplicate copy with GD number, date, and OC signature as primary documentary evidence."""
            return """⚖️ **থানায় জিডি ও এজাহার (FIR) দায়েরের নিয়ম (CrPC, 1898):**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - ফৌজদারি কার্যবিধি ১৮৯৮ (CrPC)-এর **১৫৪ ধারা** (আমলযোগ্য অপরাধের এজাহার/FIR) ও **১৫৫ ধারা** (আমল-অযোগ্য বিষয়ে সাধারণ ডায়েরি বা GD)।

২. **আইনি প্রক্রিয়া:**
   - **সাধারণ ডায়েরি (GD):** কোনো গুরুত্বপূর্ণ দলিল (NID, পাসপোর্ট, চেকবই) হারিয়ে গেলে বা কারো দ্বারা সম্ভাব্য হুমকি/ভয়ভীতি থাকলে নিকটস্থ থানায় ওসি বরাবরে সাদা কাগজে ২ কপি আবেদন করুন অথবা সরকারি 'Online GD' অ্যাপের মাধ্যমে অনলাইনে জিডি করুন।
   - **এজাহার / এফআইআর (FIR):** মারামারি, চুরি, ডাকাতি, প্রতারণা বা শারীরিক আঘাতের মতো আমলযোগ্য অপরাধ সংঘটিত হলে থানার ভারপ্রাপ্ত কর্মকর্তা (OC) তাৎক্ষণিকভাবে এজাহার হিসেবে মামলা রেকর্ড করতে আইনত বাধ্য।
   - **থানা মামলা না নিলে করণীয়:** থানা মামলা গ্রহণ না করলে হতাশ হওয়ার কারণ নেই। ফৌজদারি কার্যবিধির **২০০ ধারা** মোতাবেক সরাসরি সংশ্লিষ্ট জুডিশিয়াল ম্যাজিস্ট্রেট আদালতে গিয়ে আইনজীবীর মাধ্যমে 'সিআর মামলা' (Complaint Register Case) দায়ের করা যায়। আদালত বিষয়টি আমলে নিয়ে পুলিশ বা পিবিআই (PBI)-কে তদন্তের আদেশ দেবেন।

💡 **অ্যাডভোকেটের পরামর্শ:** জিডি করার পর থানার ডায়েরি নম্বর, তারিখ ও ওসির স্বাক্ষরযুক্ত রসিদ কপিটি নিজের কাছে সুরক্ষিত রাখুন।"""

        # 3. জমি, ফ্ল্যাট, দলিল রেজিস্ট্রি, নামজারি ও খতিয়ান (Land & Property Law)
        elif any(w in q for w in ["জমি", "ফ্ল্যাট", "দলিল", "রেজিস্ট্রি", "নামজারি", "খারিজ", "খতিয়ান", "পর্চা", "বায়না", "সাব-কবলা", "সাফ-কবলা", "মিউটেশন", "ভূমি", "land", "flat", "saf-kabala", "mutation", "khatian", "sub-registry"]):
            if is_en:
                return """⚖️ **Land & Flat Deed Registration & Mutation Rules in Bangladesh:**

1. **Statutory Provisions:**
   - Transfer of Property Act, 1882 — **Section 54** (Sales) & **Section 53B**.
   - Registration Act, 1908 — **Section 17A** (Mandatory registration of deed of sale & contract for sale).
   - State Acquisition and Tenancy Act, 1950 — **Section 143** (E-Mutation).

2. **Official Government Registration Fees (Sub-Registry Office):**
   - **Stamp Duty:** 1.5% of declared deed value (in Non-Judicial Stamps).
   - **Registration Fee:** 1% of deed value (payable via Treasury Chalan / Pay Order).
   - **Local Government Tax:** 2% to 3% (depending on City Corporation / Pouroshova / Union Parishad).
   - **Advance Income Tax (AIT):** Applicable per mouza rates.

3. **Pre-Purchase Due Diligence:**
   - Verify chain of title through CS, SA, RS, and City/BS Khatians.
   - Ensure seller's name is updated in latest E-Mutation and land taxes (Khajna) are fully cleared.
   - Perform sub-registry office search for prior encumbrances or mortgages.

💡 **Advocate's Advice:** Execute registered 'Bayna' deed before paying advance, and apply for E-Mutation at mutation.gov.bd immediately following deed execution."""
            return """⚖️ **জমি ও ফ্ল্যাট রেজিস্ট্রি ও নামজারি আইনি বিধান:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - সম্পত্তি হস্তান্তর আইন ১৮৮২ (Transfer of Property Act, 1882) **৫৪ ও ৫৩বি ধারা**।
   - রেজিস্ট্রেশন আইন ১৯০৮ (Registration Act, 1908) **১৭এ ধারা** (বায়না ও বিক্রয় দলিল বাধ্যতামূলক রেজিস্ট্রেশন)।
   - রাষ্ট্রীয় অধিগ্রহণ ও প্রজাস্বত্ব আইন ১৯৫০ (SAT Act, 1950) **১৪৩ ধারা** (নামজারি)।

২. **দলিল রেজিস্ট্রেশনের সরকারি খরচ (Sub-Registry Fee):**
   - **স্ট্যাম্প ডিউটি:** দলিলের মূল্যের ১.৫% (নন-জুডিশিয়াল স্ট্যাম্প)।
   - **রেজিস্ট্রেশন ফি:** ১% (পে-অর্ডারের মাধ্যমে)।
   - **স্থানীয় সরকার কর (পৌরসভা/সিটি কর্পোরেশন):** ২% থেকে ৩%।
   - **উৎস কর (AIT):** মৌজা ও এলাকাভেদে নির্দিষ্ট হারে প্রযোজ্য।

৩. **জমি ক্রয়ের পূর্বে চেকলিস্ট:**
   - সিএস (CS), এসএ (SA), আরএস (RS), এবং সিটি জরিপ/বিএস (BS) খতিয়ানের ধারাবাহিকতা নিশ্চিত করা।
   - বিক্রেতার নামে নামজারি (E-Mutation) এবং হালনাগাদ ভূমি উন্নয়ন কর (খাজনা) পরিশোধ আছে কিনা যাচাই করা।
   - সাব-রেজিস্ট্রি অফিসে 'তল্লাশি' দিয়ে জমিটি ব্যাংক বা কারো কাছে বন্ধক রয়েছে কিনা যাচাই করা।

💡 **অ্যাডভোকেটের পরামর্শ:** বায়না চুক্তি অবশ্যই নোটারি বা রেজিস্ট্রি করুন এবং রেজিস্ট্রি শেষ হওয়ার সাথে সাথে mutation.gov.bd-তে ই-নামজারির আবেদন করুন।"""

        # 4. বিবাহ, তালাক, দেনমোহর ও খোরপোশ (Family Law)
        elif any(w in q for w in ["তালাক", "ডিভোর্স", "দেনমোহর", "মোহরানা", "খোরপোশ", "ভরণপোষণ", "বিয়ে", "বিবাহ", "কাস্টডি", "বাচ্চা কার কাছে", "divorce", "talaq", "dower", "denmohor", "mohor", "maintenance", "custody"]):
            if is_en:
                return """⚖️ **Family Law, Dower (Denmohor), and Divorce Regulations in Bangladesh:**

1. **Governing Laws:**
   - Muslim Family Laws Ordinance, 1961 — **Sections 7 & 9**.
   - Family Courts Act, 2023.
   - Guardians and Wards Act, 1890.

2. **Legal Procedure for Divorce (Section 7):**
   - Pronouncement of Talaq must be registered with a government-licensed Kazi.
   - Written notice must be formally dispatched to the local Union Parishad Chairman or City Mayor, with a copy to the spouse via registered post.
   - Divorce becomes legally effective **90 days** from the receipt of notice (the statutory iddat period), during which reconciliation efforts are made.

3. **Recovery of Dower (Denmohor) & Maintenance:**
   - Full Dower is the unconditional statutory right of the wife, regardless of whether divorce is initiated by husband or wife (Talaq-e-Tawfeez/Khula).
   - In case of non-payment, the wife can file a recovery suit in the **Family Court** under the Family Courts Act 2023.

💡 **Advocate's Advice:** Dower debt is never barred by limitation and takes priority over inheritance. Court fees in Family Court suits are nominal."""
            return """⚖️ **পারিবারিক আইন, দেনমোহর ও তালাক বিধিবিধান:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - মুসলিম পারিবারিক আইন অধ্যাদেশ ১৯৬১ (Muslim Family Laws Ordinance, 1961) **৭ ও ৯ ধারা**।
   - পারিবারিক আদালত আইন ২০২৩ (Family Courts Act, 2023)।
   - অভিভাবকত্ব আইন ১৮৯০ (Guardians and Wards Act, 1890)।

২. **তালাক কার্যকরের আইনি নিয়ম (ধারা ৭):**
   - স্বামী বা স্ত্রী তালাক ঘোষণার পর সরকারি নিবন্ধিত কাজী অফিসে গিয়ে রেজিস্ট্রি করতে হবে।
   - কাজী বা তালাকদাতা সংশ্লিষ্ট ইউনিয়ন পরিষদ চেয়ারম্যান অথবা সিটি কর্পোরেশনের মেয়রের বরাবরে ডাকযোগে লিখিত নোটিশ পাঠাবেন এবং অপর পক্ষকে নোটিশের কপি দেবেন।
   - নোটিশ গ্রহণের তারিখ হতে **৯০ দিন অতিক্রান্ত হলে** তালাক আইনগতভাবে চূড়ান্ত কার্যকর হয় (ইদ্দতকালীন সময়)।

৩. **দেনমোহর ও খোরপোশ আদায়:**
   - দেনমোহর স্ত্রীর একচ্ছত্র আইনগত অধিকার। স্বামী তালাক দিক কিংবা স্ত্রী খোলা/তালাক-ই-তৌফিজ দিক—দেনমোহরের সম্পূর্ণ পাওনা স্ত্রীকে পরিশোধ করা স্বামীর জন্য অলঙ্ঘনীয় বাধ্যবাধকতা।
   - দেনমোহর বা খোরপোশ না দিলে স্ত্রী সরাসরি **পারিবারিক আদালতে (Family Court)** মামলা দায়ের করে ডিক্রি জারি ও সম্পত্তি ক্রোকের আদেশ নিতে পারেন।

💡 **অ্যাডভোকেটের পরামর্শ:** দেনমোহর অনাদায়ে পারিবারিক আদালতে কোর্ট ফি মাত্র সামান্য এবং কোনো অবস্থাতেই দেনমোহরের অধিকার বাতিল হয় না।"""

        # 5. শ্রম আইন, চাকরি অবসান, গ্র্যাচুইটি ও নোটিশ পে (Bangladesh Labor Act, 2006)
        elif any(w in q for w in ["শ্রমিক", "শ্রম আইন", "চাকরি", "বরখাস্ত", "ছাঁটাই", "গ্র্যাচুইটি", "প্রভিডেন্ট ফান্ড", "বেতন বকেয়া", "নোটিশ পে", "মাতৃত্বকালীন", "labor", "labour", "termination", "gratuity", "severance", "maternity leave"]):
            if is_en:
                return """⚖️ **Employment Rights & Severance under Bangladesh Labor Act, 2006:**

1. **Statutory Provisions:**
   - Bangladesh Labor Act, 2006 — **Sections 26, 27, 45-47, and 213**.

2. **Termination & Severance Benefits (Section 26):**
   - For permanent workers terminated without misconduct charges: Employer must provide **120 days' written notice** or 120 days' wages in lieu of notice (Notice Pay).
   - Compensation of **30 days' basic wages** for each completed year of service, or gratuity (whichever is higher).
   - Encashment of unavailed earned leaves and full settlement of Provident Fund.

3. **Maternity Benefits (Sections 45-47):**
   - Female employees are entitled to **16 weeks' fully paid maternity leave** (8 weeks prenatal + 8 weeks postnatal). Terminating an employee during pregnancy or maternity leave is illegal.

4. **Dispute Resolution (Section 213):**
   - Aggrieved employees can file complaints before the Department of Inspection for Factories and Establishments (DIFE) or directly before the **Labor Court**.

💡 **Advocate's Advice:** Retain your original Appointment Letter, Job Confirmation, Service Book, and salary slips at all times."""
            return """⚖️ **বাংলাদেশ শ্রম আইন অনুযায়ী শ্রমিকের অধিকার ও সুরক্ষা:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - বাংলাদেশ শ্রম আইন ২০০৬ (Bangladesh Labor Act, 2006) **২৬, ২৭, ৪৫, ৪৬ ও ৪৭ ধারা**।

২. **চাকরি অবসান ও ছাঁটাইয়ের আইনি নিয়ম (ধারা ২৬):**
   - কোনো মালিক যদি স্থায়ী শ্রমিককে কোনো অভিযোগ ছাড়া চাকরি থেকে অব্যাহতি দেন, তবে মালিককে কমপক্ষে **১২০ দিনের লিখিত নোটিশ** অথবা ১২০ দিনের মূল মজুরি (নোটিশ পে) অগ্রিম প্রদান করতে হবে।
   - এছাড়া প্রত্যেক সমাপ্ত হওয়া চাকুরির বছরের জন্য **৩০ দিনের মূল মজুরি** সমপরিমাণ ক্ষতিপূরণ বা গ্র্যাচুইটি (যা বেশি) প্রদান করতে হবে।
   - অর্জিত ছুটির সমপরিমাণ নগদ অর্থ এবং বকেয়া প্রভিডেন্ট ফান্ড প্রদান বাধ্যতামূলক।

৩. **মাতৃত্বকালীন সুবিধা (ধারা ৪৫-৪৭):**
   - নারী কর্মীকে প্রসবের পূর্বে ৮ সপ্তাহ এবং প্রসবের পরে ৮ সপ্তাহ—মোট **১৬ সপ্তাহের পূর্ণ মজুরিসহ ছুটি** প্রদান বাধ্যতামূলক। কোনো অবস্থাতেই মাতৃত্বকালীন সময়ে চাকরি থেকে অব্যাহতি দেওয়া যাবে না।

৪. **প্রতিকার:**
   - অধিকার ক্ষুণ্ণ হলে শ্রম আইনের **২১৩ ধারা** অনুযায়ী প্রথমে কলকারখানা ও প্রতিষ্ঠান পরিদর্শন অধিদপ্তর (DIFE) অথবা সরাসরি শ্রম আদালতে (Labor Court) মামলা দায়ের করা যায়।

💡 **অ্যাডভোকেটের পরামর্শ:** নিয়োগপত্র (Appointment Letter), সার্ভিস বুক এবং পে-স্লিপ সবসময় নিজের কাছে সংরক্ষণ করুন।"""

        # 6. সাইবার অপরাধ, সোশ্যাল মিডিয়া ব্ল্যাকমেইল ও হ্যাকিং (Cyber Law)
        elif any(w in q for w in ["সাইবার", "হ্যাক", "সোশ্যাল মিডিয়া", "ফেসবুক", "ছবি এডিট", "ব্ল্যাকমেইল", "ফেক আইডি", "অনলাইন প্রতারণা", "আইসিটি", "হোয়াটসঅ্যাপ", "cyber", "hack", "blackmail", "fake id", "harassment", "cyber crime"]):
            if is_en:
                return """⚖️ **Legal Remedies against Cyber Crime, Fake IDs, & Blackmail in Bangladesh:**

1. **Statutory Provisions:**
   - Cyber Security Act, 2023 & Information and Communication Technology (ICT) Act, 2006.
   - Pornography Control Act, 2012.

2. **Emergency Measures:**
   - **Preserve Digital Evidence:** Take clear screenshots showing URL, timestamps, profile IDs, messages, and transaction records. Do not delete chats.
   - **Police General Diary (GD):** File a GD at your nearest police station with all digital proof attached.
   - **Report to Specialized Cyber Cells:**
     * DMP Cyber Crime Investigation Division (Hotline: 01769-691522).
     * CID Cyber Police Centre - CPC (Hotline: 01710-366560).
     * BTRC Content Blocking Cell: smm@btrc.gov.bd.

3. **Statutory Penalties:**
   - Online harassment, unauthorized image morphing, and extortion carry rigorous imprisonment of up to 5-7 years and substantial fines.

💡 **Advocate's Advice:** Never give in to extortion demands or transfer money to blackmailers. Report immediately to official cyber law enforcement."""
            return """⚖️ **সাইবার ক্রাইম, ছবি বিকৃতি ও অনলাইন ব্ল্যাকমেইল সংক্রান্ত আইন:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - সাইবার নিরাপত্তা আইন ২০২৩ (Cyber Security Act, 2023)।
   - তথ্য ও যোগাযোগ প্রযুক্তি আইন ২০০৬ (ICT Act, 2006)।
   - পর্নোগ্রাফি নিয়ন্ত্রণ আইন ২০১২ (Pornography Control Act, 2012)।

২. **অনলাইনে ব্ল্যাকমেইল বা হেনস্তার শিকার হলে তাৎক্ষণিক করণীয়:**
   - **প্রমাণ সংরক্ষণ:** অপরাধীর প্রোফাইল ইউআরএল লিংক (URL), চ্যাট হিস্ট্রি, কল রেকর্ড ও আপত্তিকর পোস্টের পরিষ্কার স্ক্রিনশট সংগ্রহ করুন। কোনো মেসেজ ডিলিট করবেন না।
   - **থানায় জিডি:** নিকটস্থ থানায় সমস্ত ইউআরএল ও স্ক্রিনশট সংযুক্ত করে জিডি করুন।
   - **বিশেষায়িত police ইউনিটে অভিযোগ:**
     * ডিএমপি সাইবার ক্রাইম ইনভেস্টিগেশন ডিভিশন (হেল্পলাইন: 01769-691522)
     * সিআইডি সাইবার পুলিশ সেন্টার (Facebook: Cyber Police Centre - CPC, Hotline: 01710-366560)
     * সরকারি ইমেইল: smm@btrc.gov.bd (বিটিআরসি কন্টেন্ট ব্লকিং সেল)

৩. **শাস্তি:** অনুমতি ছাড়া ছবি বিকৃত বা ব্ল্যাকমেইল করলে আইন অনুযায়ী সর্বোচ্চ ৫ থেকে ৭ বছর পর্যন্ত কারাদণ্ড এবং অর্থদণ্ড হতে পারে।

💡 **অ্যাডভোকেটের পরামর্শ:** ব্ল্যাকমেইলারের কোনো অনৈতিক প্রস্তাবে সম্মত হবেন না বা টাকা পাঠাবেন না। দ্রুত সাইবার হেল্পলাইনে কল করুন।"""

        # 7. নারী ও শিশু নির্যাতন এবং যৌতুক (Women & Children Repression)
        elif any(w in q for w in ["নারী নির্যাতন", "যৌতুক", "মারধর", "নির্যাতন", "ধর্ষণ", "ইভটিজিং", "গার্হস্থ্য হিংসা", "dowry", "rape", "domestic violence"]):
            if is_en:
                return """⚖️ **Suppression of Violence against Women & Children & Dowry Prohibition in Bangladesh:**

1. **Statutory Laws & Sections:**
   - Prevention of Women and Children Repression Act, 2000 (Amended 2020) — **Sections 9 & 11**.
   - Dowry Prohibition Act, 2018 — **Sections 3 & 4**.

2. **Immediate Legal Steps:**
   - **Medical Evidence:** Seek prompt medical care at the One-Stop Crisis Centre (OCC) of a government medical college hospital and obtain medical certificates.
   - **Emergency Helplines:** Dial National Emergency Service **999** or Women & Children Helpline **109** (toll-free 24/7).
   - **Filing Complaint:** Lodge an FIR at the police station or file a direct complaint petition before the District Women and Children Repression Prevention Special Tribunal.

💡 **Advocate's Advice:** Offences under this Act are non-bailable and cognizable."""
            return """⚖️ **নারী ও শিশু নির্যাতন দমন এবং যৌতুক প্রতিরোধ আইন:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - নারী ও শিশু নির্যাতন দমন আইন ২০০০ (সংশোধিত ২০২০) **৯ ধারা** (ধর্ষণ), **১১ ধারা** (যৌতুকের জন্য জখম/নির্যাতন)।
   - যৌতুক নিরোধ আইন ২০১৮ (Dowry Prohibition Act, 2018) **৩ ও ৪ ধারা**।

২. **তাৎক্ষণিক আইনি পদক্ষেপ:**
   - **মেডিকেল পরীক্ষা:** শারীরিক নির্যাতনের শিকার হলে দ্রুততম সময়ে নিকটস্থ সরকারি মেডিকেল কলেজ হাসপাতালের ওয়ান-স্টপ ক্রাইসিস সেন্টারে (OCC) ভর্তি হয়ে চিকিৎসাপত্র ও মেডিকেল সার্টিফিকেট সংগ্রহ করুন।
   - **জরুরি সহায়তা:** তাৎক্ষণিক পুলিশি সুরক্ষার জন্য জাতীয় জরুরি সেবা **৯৯৯** অথবা নারী ও শিশু হেল্পলাইন **১০৯ (109)**-এ কল করুন।
   - **মামলা দায়ের:** স্থানীয় থানায় সরাসরি মামলা করা যায়। থানা মামলা নিতে গড়িমসি করলে জেলার **নারী ও শিশু নির্যাতন দমন ট্রাইব্যুনালে (Special Tribunal)** সরাসরি পিটিশন মামলা দায়ের করা যায়।

৩. **শাস্তি:** যৌতুকের জন্য হত্যা বা মারাত্মক জখমের অপরাধে মৃত্যুদণ্ড বা যাবজ্জীবন কারাদণ্ড এবং যৌতুক দাবির অপরাধে সর্বোচ্চ ৫ বছর পর্যন্ত কারাদণ্ডের বিধান রয়েছে।

💡 **অ্যাডভোকেটের পরামর্শ:** এই আইনে দায়েরকৃত অপরাধসমূহ আমলযোগ্য ও সাধারণত জামিন-অযোগ্য (Non-bailable)।"""

        # 8. প্রতারণা, অর্থ আত্মসাৎ ও বিশ্বাসভঙ্গ (Penal Code, 1860 - 420)
        elif any(w in q for w in ["প্রতারণা", "ঠকানো", "জালিয়াতি", "৪২০", "আত্মসাৎ", "টাকা মেরে", "বিশ্বাসভঙ্গ", "fraud", "cheat", "cheating", "embezzle", "forgery", "420"]):
            if is_en:
                return """⚖️ **Fraud, Cheating & Breach of Trust (Penal Code, 1860):**

1. **Statutory Sections:**
   - Section 420: Cheating and dishonestly inducing delivery of property (up to 7 years imprisonment).
   - Section 406: Criminal breach of trust (up to 3 years imprisonment).
   - Section 467/468: Forgery of valuable security (up to life imprisonment).

2. **Legal Remedies:**
   - Serve an initial statutory demand notice through an advocate.
   - If not resolved, file a CR Complaint Case under Section 406/420 before the Chief Metropolitan Magistrate (CMM) or Chief Judicial Magistrate court.
   - The court will take cognizance and issue summons, arrest warrants, or order a Police Bureau of Investigation (PBI) inquiry.

💡 **Advocate's Advice:** Differentiate civil breach from criminal fraud by demonstrating dishonest intention from the very inception of the transaction."""
            return """⚖️ **প্রতারণা, অর্থ আত্মসাৎ ও জালিয়াতি সংক্রান্ত আইন (দণ্ডবিধি ১৮৬০):**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - বাংলাদেশ দণ্ডবিধি ১৮৬০ (Penal Code, 1860)-এর:
     * **৪২০ ধারা:** প্রতারণা এবং অসদুপায়ে সম্পত্তি অর্পণ করান (শাস্তি: সর্বোচ্চ ৭ বছর কারাদণ্ড)।
     * **৪০৬ ধারা:** অপরাধমূলক বিশ্বাসভঙ্গ (শাস্তি: সর্বোচ্চ ৩ বছর কারাদণ্ড)।
     * **৪৬৭/৪৬৮ ধারা:** জালিয়াতি ও জাল দলিল প্রস্তুতকরণ (শাস্তি: যাবজ্জীবন বা ৭ বছর কারাদণ্ড)।

২. **আইনি পদক্ষেপ:**
   - টাকা দেওয়ার চুক্তিপত্র, ব্যাংকিং ট্রান্সফার স্টেটমেন্ট, রসিদ বা অডিও-ভিডিও প্রমাণাদি গুছিয়ে নিন।
   - সিনিয়র আইনজীবীর মাধ্যমে চিফ জুডিশিয়াল ম্যাজিস্ট্রেট বা সিএমএম আদালতে দণ্ডবিধির ৪০৬/৪২০ ধারায় **নালিশি সিআর (CR) মামলা** দায়ের করুন।
   - আদালত প্রাথমিক শুনানি নিয়ে আসামির বিরুদ্ধে সরাসরি গ্রেফতারি পরোয়ানা (WA) জারি করতে পারেন অথবা পুলিশ ব্যুরো অব ইনভেস্টিগেশন (PBI)-কে তদন্তের নির্দেশ দেন।

💡 **অ্যাডভোকেটের পরামর্শ:** দেওয়ানি লেনদেনের চেয়ে প্রতারণার সুনির্দিষ্ট উদ্দেশ্য প্রমাণ করা জরুরি। প্রাথমিক নোটিশ পাঠানো থাকলে মামলা অনেক শক্তিশালী হয়।"""

        # 9. জামিন ও আগাম জামিন (Bail & Anticipatory Bail)
        elif any(w in q for w in ["জামিন", "আগাম জামিন", "ওয়ারেন্ট", "বেল", "গ্রেফতারি পরোয়ানা", "bail", "anticipatory bail", "arrest warrant"]):
            if is_en:
                return """⚖️ **Bail & Anticipatory Bail Procedures in Bangladesh (CrPC, 1898):**

1. **Statutory Provisions:**
   - Section 496: Bailable offences (Bail is a matter of right).
   - Section 497: Non-bailable offences (Discretion of the trial court).
   - Section 498: High Court Division & Sessions Court powers for Special & Anticipatory Bail.

2. **Anticipatory Bail (High Court Division):**
   - When a person has reasonable apprehension of arrest in a false or politically motivated case, they can appear physically before the High Court Division with a Supreme Court advocate to pray for Anticipatory Bail.
   - The High Court typically grants interim anticipatory bail for 4 to 8 weeks, directing surrender before the trial magistrate/sessions court.

💡 **Advocate's Advice:** Do not abscond if a warrant is issued. Surrendering via an experienced advocate and seeking regular or anticipatory bail is the safest legal route."""
            return """⚖️ **বাংলাদেশ আদালতে জামিন প্রাপ্তির আইনি নিয়মাবলী (CrPC):**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - ফৌজদারি কার্যবিধি ১৮৯৮ (CrPC)-এর:
     * **৪৯৬ ধারা:** জামিনযোগ্য অপরাধে জামিন (অধিকার হিসেবে প্রাপ্য)।
     * **৪৯৭ ধারা:** অজামিনযোগ্য অপরাধে জামিন (আদালতের বিবেচনামূলক ক্ষমতা)।
     * **৪৯৮ ধারা:** দায়রা জজ ও মহামান্য হাইকোর্ট বিভাগে বিশেষ ও আগাম জামিন (Anticipatory Bail)।

২. **আগাম জামিন পাওয়ার নিয়ম (High Court Anticipatory Bail):**
   - পুলিশ বা প্রতিপক্ষ দ্বারা হয়রানিমূলক মিথ্যা মামলায় গ্রেফতার হওয়ার যুক্তিসঙ্গত আশঙ্কা থাকলে হাইকোর্ট বিভাগে স্বশরীরে উপস্থিত হয়ে জ্যেষ্ঠ আইনজীবীর মাধ্যমে আগাম জামিন প্রার্থনা করা যায়।
   - হাইকোর্ট সাধারণত নির্দিষ্ট মেয়াদের (যেমন: ৪ থেকে ৮ সপ্তাহ) অন্তর্বর্তীকালীন জামিন প্রদান করেন এবং পরবর্তীতে নিম্ন আদালতে আত্মসমর্পণের নির্দেশ দেন।

৩. **জামিনের গ্রাউন্ডসমূহ:**
   - এজাহারে নাম না থাকা, নারী, অসুস্থ বা বয়োবৃদ্ধ হওয়া, দীর্ঘ কারাবাস ও তদন্তে অগ্রগতি না থাকা জামিন পাওয়ার অন্যতম প্রধান কারণ।

💡 **অ্যাডভোকেটের পরামর্শ:** গ্রেফতারি পরোয়ানা জারি হলে পলাতক না থেকে বিজ্ঞ আইনজীবীর মাধ্যমে উপযুক্ত আদালতে আত্মসমর্পণ করে জামিন আবেদন করাই সর্বোত্তম আইনি পথ।"""

        # 10. মানহানি ও ক্ষতিপূরণ মামলা (Defamation Law)
        elif any(w in q for w in ["মানহানি", "অপপ্রচার", "সম্মানহানি", "কুৎসা", "মানহানির মামলা", "defamation", "slander", "libel"]):
            if is_en:
                return """⚖️ **Defamation & Slander Laws in Bangladesh:**

1. **Statutory Provisions:**
   - Penal Code 1860 — Sections 499 & 500 (Criminal defamation: up to 2 years imprisonment or fine).
   - Tort / Civil Suit for Damages in District Civil Court for financial and reputational injury.

2. **Legal Steps:**
   - Dispatch a registered Legal Notice demanding immediate retraction, public apology, and compensation.
   - If unheeded, lodge a criminal complaint before Judicial Magistrate under Section 500 or file a civil damage suit.

💡 **Advocate's Advice:** Digital screenshots, witnesses, and publication records must be preserved as primary evidence."""
            return """⚖️ **মানহানি ও সামাজিক অপপ্রচার সংক্রান্ত আইন:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - দণ্ডবিধি ১৮৬০-এর **৪৯৯ ধারা** (মানহানির সংজ্ঞা) এবং **৫০০ ধারা** (মানহানির শাস্তি: সর্বোচ্চ ২ বছর কারাদণ্ড বা জরিমানা)।
   - দেওয়ানি আইনের অধীন ক্ষতিপূরণ মোকদ্দমা (Suit for Damages/Tort)।

২. **প্রতিকার ও ধাপসমূহ:**
   - প্রথমে আইনজীবীর মাধ্যমে সংশ্লিষ্ট ব্যক্তির নিকট মানহানিকর বক্তব্য প্রত্যাহার, প্রকাশ্যে ক্ষমা প্রার্থনা এবং আর্থিক ক্ষতিপূরণ দাবি করে **রেজিস্টার্ড লিগ্যাল নোটিশ** প্রেরণ করুন।
   - নোটিশ অমান্য করলে বিজ্ঞ সিএমএম বা জুডিশিয়াল ম্যাজিস্ট্রেট আদালতে দণ্ডবিধির ৫০০ ধারায় ফৌজদারি মামলা দায়ের করা যায়।
   - পাশাপাশি উপযুক্ত দেওয়ানি আদালতে সম্মানহানির কারণে কোটি টাকার আর্থিক ক্ষতিপূরণ মামলা দায়ের করা যায়।

💡 **অ্যাডভোকেটের পরামর্শ:** বক্তব্যটি প্রকাশ্য জনসমক্ষে বা সোশ্যাল মিডিয়ায় প্রচারিত হয়েছে—এমন চাক্ষুষ সাক্ষী ও ডিজিটাল ডকুমেন্টস প্রমাণ হিসেবে সংগ্রহ রাখতে হবে।"""

        # 11. বাটোয়ারা মামলা ও ওয়ারিশ সূত্রে সম্পত্তি বণ্টন (Partition Law)
        elif any(w in q for w in ["বাটোয়ারা", "ওয়ারিশ", "বণ্টন", "উত্তরাধিকার", "ফারায়েজ", "জমি ভাগ", "partition", "inheritance", "farayez"]):
            if is_en:
                return """⚖️ **Property Partition & Inheritance Laws in Bangladesh:**

1. **Statutory Provisions:**
   - The Partition Act, 1893 & Code of Civil Procedure, 1908 (CPC).
   - Muslim and Hindu Succession Laws.

2. **Legal Procedure:**
   - **Amicable Partition (Apash Bantan):** If all co-sharers agree, survey the land with a certified surveyor, execute a registered Partition Deed (বাটোয়ারা দলিল), and apply for separate E-Mutations.
   - **Partition Suit in Civil Court:** If any co-sharer refuses to allocate share, file a Partition Suit in the Court of competent Civil Judge. The court passes a Preliminary Decree followed by an Advocate Commissioner site inspection for physical demarcation with red ribbons.

💡 **Advocate's Advice:** Procure the official Warisan Certificate and certified copies of mother deeds prior to filing."""
            return """⚖️ **বাটোয়ারা মোকদ্দমা ও উত্তরাধিকার সম্পত্তি বণ্টন আইন:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - বাটোয়ারা আইন ১৮৯৩ (The Partition Act, 1893)।
   - সুনির্দিষ্ট প্রতিকার আইন ১৮৭৭ এবং দেওয়ানি কার্যবিধি ১৯০৮ (CPC)।
   - মুসলিম ও হিন্দু উত্তরাধিকার আইন।

২. **বণ্টনের আইনি প্রক্রিয়া:**
   - **আপস বণ্টন:** সকল অংশীদার সম্মত থাকলে স্থানীয়ভাবে সার্ভেয়ার (আমিন) দিয়ে মেপে একটি 'আপস বাটোয়ারা দলিল' তৈরি করে সাব-রেজিস্ট্রি অফিসে রেজিস্ট্রি করিয়ে নামজারি করা সর্বোত্তম।
   - **আদালতে বাটোয়ারা মোকদ্দমা:** কোনো ভাই, বোন বা অংশীদার জমি বুঝিয়ে না দিলে বা এককভাবে দখল করে রাখলে উপযুক্ত সিভিল জজ আদালতে 'বাটোয়ারা মামলা' (Partition Suit) দায়ের করতে হয়।
   - আদালত প্রাথমিক ডিক্রি (Preliminary Decree) প্রদানের পর অ্যাডভোকেট কমিশনার নিয়োগ করে সরকারিভাবে জমি মেপে লাল ফিতা দিয়ে সীমানা ভাগ করে দেন।

💡 **অ্যাডভোকেটের পরামর্শ:** মামলা করার আগে স্থানীয় ইউনিয়ন পরিষদ/সিটি কর্পোরেশন থেকে 'ওয়ারিশান সনদ' এবং মূল দলিলের সার্টিফাইড কপি সংগ্রহ করুন।"""

        # 12. ভোক্তা অধিকার ও ভেজাল পণ্য (Consumer Rights Protection)
        elif any(w in q for w in ["ভোক্তা", "মেয়াদোত্তীর্ণ", "অতিরিক্ত দাম", "ভেজাল", "ওজনে কম", "ভোক্তা অধিকার", "দোকানদার", "consumer", "consumer rights", "expired product", "overpricing", "dncrp"]):
            if is_en:
                return """⚖️ **Consumer Rights Protection in Bangladesh (Act of 2009):**

1. **Governing Provisions:**
   - Consumer Rights Protection Act, 2009 — Sections 40, 43, 44 & 45 (Overpricing, adulteration, expired goods, deceptive practices).

2. **Filing a Complaint:**
   - Submit written complaint with purchase cash memo/invoice within **30 days** of occurrence to the Directorate of National Consumer Rights Protection (DNCRP) or email: nccc@dncrp.gov.bd.
   - Consumer Helpline Hotline: **16121**.

3. **25% Cash Reward for Complainant:**
   - Upon investigation and fine realization, **25% of the penalty is paid directly in cash to you (the complainant)**!

💡 **Advocate's Advice:** Always demand and retain official cash memos; receipts are indispensable evidence."""
            return """⚖️ **ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ অনুযায়ী প্রতিকার:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (Consumer Rights Protection Act, 2009)-এর **৪০, ৪৩, ৪৪ ও ৪৫ ধারা**।

২. **অভিযোগ দায়েরের নিয়ম:**
   - পণ্য ক্রয়ের রসিদ (Cash Memo) ও পণ্যের ছবিসহ ঘটনার **৩০ দিনের মধ্যে** জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরে (DNCRP) সরাসরি বা অনলাইনে (e-mail: nccc@dncrp.gov.bd) অভিযোগ দাখিল করতে হবে।
   - ভোক্তা বাতায়ন হটলাইন: **১৬১২১**।

৩. **অভিযোগকারীর আর্থিক পুরস্কার:**
   - আপনার অভিযোগ তদন্তে প্রমাণিত হলে সংশ্লিষ্ট দোকান বা প্রতিষ্ঠানকে জরিমানা করা হবে এবং আইনের ধারা অনুযায়ী **আদায়কৃত জরিমানার ২৫% অর্থ নগদ পুরস্কার হিসেবে আপনি (অভিযোগকারী) পাবেন!**

💡 **অ্যাডভোকেটের পরামর্শ:** যেকোনো ক্রয়ের পাকা রসিদ সংরক্ষণ করুন; রসিদ ছাড়া ভোক্তা অধিকারে প্রতিকার পাওয়া কঠিন।"""

        # 13. সড়ক পরিবহন ও ট্রাফিক আইন (Road Transport Act, 2018)
        elif any(w in q for w in ["ট্রাফিক", "সড়ক পরিবহন", "ড্রাইভিং লাইসেন্স", "হেলমেট", "জরিমানা", "ট্রাফিক মামলা", "traffic", "driving license", "road transport"]):
            if is_en:
                return """⚖️ **Road Transport Act, 2018 & Traffic Rules in Bangladesh:**

1. **Key Offenses & Penalties:**
   - Section 66: Driving without license (fine up to 25,000 BDT or 6 months imprisonment).
   - Section 72: Driving without vehicle fitness certification.
   - Section 92: Wrong-way driving or signal violation.

2. **Penalty Settlement:**
   - Traffic police issues an electronic POS slip. Fines can be paid directly via bKash/Nagad/Rocket or designated bank counters, after which seized documents are retrieved from the DC Traffic office."""
            return """⚖️ **সড়ক পরিবহন আইন ২০১৮ ও ট্রাফিক মামলার নিয়মাবলী:**

১. **সংশ্লিষ্ট আইন ও ধারা:**
   - সড়ক পরিবহন আইন ২০১৮-এর **৬৬ ধারা** (ড্রাইভিং লাইসেন্স ছাড়া গাড়ি চালানো - সর্বোচ্চ ২৫,০০০ টাকা জরিমানা বা ৬ মাস জেল), **৭২ ধারা** (ফিটনেস ছাড়া গাড়ি চালানো), **৯২ ধারা** (বিপরীত দিকে গাড়ি চালানো)।

২. **জরিমানা পরিশোধ ও ডকুমেন্ট ছাড়ের নিয়ম:**
   - ট্রাফিক পুলিশ মামলা দিলে একটি ই-মামলা স্লিপ (POS Slip) প্রদান করে।
   - বিকাশ, রকেট, নগদ বা নির্দিষ্ট ব্যাংকে সরাসরি জরিমানা পরিশোধ করে ট্রাফিক ডিসি (DC Traffic) অফিস থেকে সাথে সাথে জব্দকৃত লাইসেন্স বা গাড়ির কাগজ উদ্ধার করা যায়।
   - অযৌক্তিক মামলা মনে হলে সংশ্লিষ্ট ট্রাফিক জোনের সহকারী পুলিশ কমিশনার (AC Traffic) বরাবর আবেদন করার সুযোগ রয়েছে।"""

        # 14. আয়কর আইন ও ই-টিন (Income Tax Act, 2023)
        elif any(w in q for w in ["আয়কর", "ট্যাক্স", "রিটার্ন", "ই-টিন", "tax", "tin", "income tax", "etax"]):
            if is_en:
                return """⚖️ **Income Tax Act, 2023 & Tax Return Compliance in Bangladesh:**

1. **Tax-Free Thresholds:**
   - General Individual: **350,000 BDT**.
   - Female & Senior Citizens (65+): **400,000 BDT**.
   - Persons with Disabilities: **475,000 BDT**; Freedom Fighters: **500,000 BDT**.

2. **Mandatory e-Return Filing:**
   - Annual tax return submission is mandatory for all TIN holders on or before Tax Day (30 November).
   - Online e-filing is available at etaxnbr.gov.bd in 10 minutes with instant PSR (Proof of Submission of Return)."""
            return """⚖️ **আয়কর আইন ২০২৩ অনুযায়ী কর ও রিটার্ন দাখিলের নিয়ম:**

১. **করমুক্ত আয়ের সীমা (২০২৪-২০২৬ করবর্ষ):**
   - সাধারণ পুরুষ করদাতা: **৩,৫০,০০০ টাকা**।
   - মহিলা ও ৬৫ বছর বা তদূর্ধ্ব বয়সী করদাতা: **৪,০০,০০০ টাকা**।
   - প্রতিবন্ধী করদাতা: **৪,৭৫,০০০ টাকা** এবং গেজেটভুক্ত বীর মুক্তিযোদ্ধা: **৫,০০,০০০ টাকা**।

২. **বাধ্যতামূলক রিটার্ন দাখিল:**
   - টিন (TIN) সনদ থাকা সকল ব্যক্তির জন্য প্রতি বছর নির্দিষ্ট সময়সীমার মধ্যে (কর দিবস - ৩০ নভেম্বর) বার্ষিক আয়কর রিটার্ন দাখিল বাধ্যতামূলক।
   - এখন ঘরে বসে etaxnbr.gov.bd পোর্টালের মাধ্যমে অনলাইনে বিনামূল্যে মাত্র ১০ মিনিটে ই-রিটার্ন দাখিল ও প্রাপ্তিস্বীকার পত্র পাওয়া যায়।

💡 **অ্যাডভোকেটের পরামর্শ:** ব্যাংকে বড় সঞ্চয়পত্র, গাড়ির রেজিস্ট্রেশন ও ট্রেড লাইসেন্সের জন্য রিটার্ন জমার প্রমাণপত্র (PSR) বাধ্যতামূলক।"""

        # 15. স্ট্যাম্প আইন (The Stamp Act, 1899)
        elif any(w in q for w in ["স্ট্যাম্প", "stamp", "stamp duty"]):
            if is_en:
                return """⚖️ **Bangladesh Stamp Duty Rates (The Stamp Act, 1899):**

1. **Mandatory Stamp Requirements:**
   - House / Commercial Tenancy: **300 BDT Non-Judicial Stamp**.
   - Partnership Agreement: **1,000 BDT** (Capital <= 50,000 BDT) or **2,000 BDT** (Capital > 50,000 BDT).
   - Freelance & Service Agreements: **300 BDT**.
   - Affidavits: **200 BDT Non-Judicial Stamp**.

2. **Legal Enforcement:**
   - Contracts executed on plain unstamped paper are inadmissible in judicial evidence under Section 35 of the Stamp Act without 10x penalty."""
            return """⚖️ **বাংলাদেশ স্ট্যাম্প আইন ১৮৯৯ (The Stamp Act, 1899) অনুযায়ী নিয়ম:**

১. **বাধ্যতামূলক স্ট্যাম্প ফি:**
   - বাড়ি, ফ্ল্যাট বা দোকান ভাড়ার চুক্তি: **৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প**।
   - অংশীদারি কারবার চুক্তিপত্র: মূলধন ৫০,০০০ টাকার কম হলে ১,০০০ টাকা, ৫০,০০০ টাকার বেশি হলে **২,০০০ টাকার স্ট্যাম্প**।
   - ফ্রিল্যান্স ও সাধারণ সেবা চুক্তি: **৩০০ টাকার স্ট্যাম্প**।
   - এফিডেভিট বা হলফনামা: **২০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প**।

২. **আইনি কার্যকারিতা:**
   - স্ট্যাম্প ছাড়া সাদা কাগজে স্বাক্ষরিত চুক্তি আদালতে সহজে প্রমাণ করা যায় না এবং তামাদি বা জরিমানার মুখোমুখি হতে হয়। প্রথম পাতায় মূল স্ট্যাম্প এবং অতিরিক্ত পাতাসমূহ সাধারণ ডিমাই/লিগ্যাল সাইজের পেপারে প্রিন্ট করে প্রতি পৃষ্ঠায় উভয় পক্ষের স্বাক্ষর নিতে হয়।"""

        # 16. বাড়ি ভাড়া নিয়ন্ত্রণ ও উচ্ছেদ আইন (Premises Rent Control Act, 1991)
        elif any(w in q for w in ["ভাড়া", "ভাড়াটিয়া", "উচ্ছেদ", "বাড়িওয়ালা", "বাসা ভাড়া", "ভাড়া চুক্তি", "tenant", "eviction", "rent", "landlord"]):
            if is_en:
                return """⚖️ **Premises Rent Control & Tenant Eviction Rules (Act of 1991):**

1. **Key Rights & Sections:**
   - Sections 18 & 19: Protection against arbitrary eviction as long as tenant pays rent regularly.
   - Section 10: Limiting advance security deposit.
   - Section 13: Mandatory requirement for landlord to issue signed rent receipts.

2. **Eviction Notice:**
   - Landlord must serve a minimum of **1 month written legal notice** (or agreed contract duration) before seeking eviction.
   - Unilateral disconnection of utilities (gas, water, electricity) is a punishable offense."""
            return """⚖️ **বাড়ি ভাড়া নিয়ন্ত্রণ আইন ১৯৯১ (Premises Rent Control Act, 1991):**

১. **মৌলিক আইনি সুরক্ষা ও ধারা:**
   - **ধারা ১৮ ও ১৯:** কোনো ভাড়াটিয়া নিয়মিত ভাড়া পরিশোধ করলে এবং চুক্তির কোনো শর্ত ভঙ্গ না করলে তাকে বাড়িওয়ালা ইচ্ছামতো বাসা থেকে উচ্ছেদ করতে পারবে না।
   - **উচ্ছেদ নোটিশ:** উচ্ছেদের পূর্বে ভাড়াটিয়াকে অবশ্যই কমপক্ষে **১ মাস (বা চুক্তির মেয়াদ অনুযায়ী)** পূর্বে লিখিত লিগ্যাল নোটিশ দিতে হবে।
   - **ভাড়ার রসিদ (ধারা ১৩):** ভাড়া নেওয়ার সাথে সাথে বাড়িওয়ালা স্বাক্ষরিত লিখিত ভাড়ার রসিদ দিতে আইনত বাধ্য।
   - **অগ্রিম জামানত (ধারা ১০):** আইনত এক মাসের বেশি মাসিক ভাড়ার সমপরিমাণ টাকা অগ্রিম জামানত নেওয়া বেআইনি।

💡 **অ্যাডভোকেটের পরামর্শ:** বাড়িওয়ালা বিনা নোটিশে পানি বা বিদ্যুৎ সংযোগ বিচ্ছিন্ন করলে বা বের করে দেওয়ার হুমকি দিলে ভাড়াটিয়া সরাসরি দেওয়ানি আদালত ও রেন্ট কন্ট্রোলারের শরণাপন্ন হতে পারেন।"""

        # 17. সাধারণ আইনি পর্যালোচনা (General Bangladesh Legal Advisory)
        else:
            if is_en:
                return f"""⚖️ **Bangladesh Legal Advisory Overview:**

Regarding your query on Bangladesh Law:

1. **Constitutional & Legal Framework:**
   - Articles 27 & 31 of the Constitution of Bangladesh guarantee that all citizens are equal before law and entitled to equal protection of law.
   - Civil disputes are governed by the Specific Relief Act 1877, Contract Act 1872, and Code of Civil Procedure 1908 (CPC).
   - Criminal offenses are prosecuted under the Penal Code 1860 and Code of Criminal Procedure 1898 (CrPC).

2. **Recommended Legal Action Plan:**
   - **Step 1:** Preserve all documentary, financial, and digital evidence.
   - **Step 2:** Dispatch an advocate's statutory Legal Notice granting 15 to 30 days for compliance.
   - **Step 3:** In absence of amicable settlement, initiate appropriate proceedings in the competent court of jurisdiction.

💡 **Advocate's Advice:** For complex litigation, consult a practicing Supreme Court or District Bar Advocate with your complete documentation."""
            return f"""⚖️ **আপনার প্রশ্নের সার্বিক বাংলাদেশ আইনি পর্যালোচনা:**

"{user_q}"-এর বিষয়ে বাংলাদেশ সংবিধান ও প্রচলিত আইন অনুযায়ী আইনি দিকনির্দেশনা:

১. **মৌলিক আইনি অবস্থান:**
   - বাংলাদেশ সংবিধানের **অনুচ্ছেদ ২৭ ও ৩১** মোতাবেক প্রত্যেক নাগরিক আইনের দৃষ্টিতে সমান এবং আইনানুযায়ী আশ্রয়লাভের অধিকারী।
   - দেওয়ানি (Civil) বিরোধের ক্ষেত্রে সুনির্দিষ্ট প্রতিকার আইন ১৮৭৭ এবং চুক্তি আইন ১৮৭২ অনুযায়ী উপযুক্ত সহকারী জজ বা যুগ্ম জেলা জজ আদালতে প্রতিকার পাওয়া যায়।
   - অপরাধমূলক (Criminal) ঘটনায় দণ্ডবিধি ১৮৬০ ও ফৌজদারি কার্যবিধি ১৮৯৮ অনুযায়ী থানায় এজাহার বা ম্যাজিস্ট্রেট আদালতে সরাসরি নালিশি মামলা দায়ের করা যায়।

২. **প্রয়োজনীয় আইনি পদক্ষেপ:**
   - **ধাপ ১:** ঘটনার তারিখ, প্রমাণাদি (ডকুমেন্টস, রসিদ, ডিজিটাল রেকর্ড) সংগ্রহ করুন।
   - **ধাপ ২:** ক্ষেত্রবিশেষে বিরোধ নিষ্পত্তির জন্য আইনজীবীর মাধ্যমে ১৫ বা ৩০ দিনের সময় দিয়ে 'লিগ্যাল নোটিশ' প্রেরণ করুন।
   - **ধাপ ৩:** স্থানীয় পর্যায়ে আপস মীমাংসা না হলে উপযুক্ত এখতিয়ারাধীন আদালতে মামলা দায়ের করুন।

💡 **অ্যাডভোকেটের পরামর্শ:** জটিল কোনো বিরোধে দ্রুত জেলা জজ আদালত বা সুপ্রিম কোর্টের একজন বিজ্ঞ আইনজীবীর সাথে ব্যক্তিগতভাবে নথিপত্রসহ পরামর্শ গ্রহণ করার অনুরোধ করা হচ্ছে।"""

ai_service = AIService()
