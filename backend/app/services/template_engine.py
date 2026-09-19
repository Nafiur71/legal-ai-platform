from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, List
from app.config import TEMPLATES_DIR
import io
from docx import Document

class TemplateEngine:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.templates_meta = {
            "tenancy_agreement": {
                "id": "tenancy_agreement",
                "title_bn": "বাড়ি / ফ্ল্যাট / দোকান ভাড়ার চুক্তিপত্র",
                "title_en": "Residential & Commercial Tenancy Agreement",
                "template_file": "tenancy_agreement.html",
                "category": "Property & Real Estate",
                "defaults_bn": {
                    "execution_date": "১২ সেপ্টেম্বর, ২০২৬",
                    "landlord_name": "মো: রফিকুল ইসলাম",
                    "landlord_father": "মরহুম আলহাজ্ব আব্দুল করিম",
                    "landlord_address": "বাড়ি নং-১২, রোড নং-০৫, সেক্টর-৩, উত্তরা, ঢাকা",
                    "landlord_nid": "১৯৮৫২৬৯২৪১৫১২৩৪৫৬",
                    "landlord_phone": "০১৭১১-২২৩৩৪৪",
                    "tenant_name": "মো: তানভীর আহমেদ",
                    "tenant_father": "মো: নূরুল হুদা",
                    "tenant_address": "গ্রাম: চরভদ্রাসন, থানা: কোতোয়ালী, জেলা: ফরিদপুর",
                    "tenant_nid": "১৯৯২২৬৯২৪১৫৯৮৭৬৫৪",
                    "tenant_phone": "০১৮১১-৫৫৬৬৭৭",
                    "property_address": "ফ্ল্যাট নং-৪বি (৪র্থ তলা), বাড়ি নং-১২, রোড নং-০৫, সেক্টর-৩, উত্তরা, ঢাকা-১২৩০",
                    "property_type": "আবাসিক ফ্ল্যাট (৩ বেড, ৩ বাথ, ড্রয়িং-ডাইনিং)",
                    "duration_months": "২৪",
                    "start_date": "০১ অক্টোবর, ২০২৬",
                    "rent_amount": "২৫,০০০",
                    "rent_in_words": "পঁচিশ হাজার টাকা মাত্র",
                    "payment_due_day": "৭",
                    "deposit_amount": "৭৫,০০০",
                    "notice_period_months": "২",
                    "utility_terms": "বিদ্যুৎ বিল, গ্যাস বিল, পানি বিল ও মাসিক কমন সার্ভিস চার্জ (৩,০০০ টাকা) ২য় পক্ষ প্রতি মাসে নির্ধারিত তারিখের মধ্যে পরিশোধ করিবেন।",
                    "witness1_name": "মো: কামরুল হাসান",
                    "witness1_address": "উত্তরা, ঢাকা",
                    "witness2_name": "সাজিদ মাহমুদ",
                    "witness2_address": "মিরপুর, ঢাকা",
                    "custom_clauses": [
                        {
                            "title": "নিরাপত্তা ও পারিবারিক অনুশাসন",
                            "text": "ভাড়াকৃত ফ্ল্যাটে কোনো প্রকার অসামাজিক, অবৈধ বা আইন পরিপন্থী কর্মকাণ্ড পরিচালনা করা যাইবে না এবং রাত ১১টার পর প্রধান গেটের নিরাপত্তা বজায় রাখিতে হইবে।"
                        }
                    ]
                },
                "defaults_en": {
                    "execution_date": "12 September 2026",
                    "landlord_name": "Md. Rafiqul Islam",
                    "landlord_father": "Late Alhaj Abdul Karim",
                    "landlord_address": "House 12, Road 05, Sector 3, Uttara, Dhaka",
                    "landlord_nid": "19852692415123456",
                    "landlord_phone": "+880 1711-223344",
                    "tenant_name": "Tanvir Ahmed",
                    "tenant_father": "Md. Nurul Huda",
                    "tenant_address": "Charbhadrasan, Kotwali, Faridpur",
                    "tenant_nid": "19922692415987654",
                    "tenant_phone": "+880 1811-556677",
                    "property_address": "Flat 4B (4th Floor), House 12, Road 05, Sector 3, Uttara, Dhaka-1230",
                    "property_type": "Residential Apartment (3 Bed, 3 Bath, Living-Dining)",
                    "duration_months": "24",
                    "start_date": "01 October 2026",
                    "rent_amount": "25,000",
                    "rent_in_words": "Twenty-Five Thousand Taka Only",
                    "payment_due_day": "7",
                    "deposit_amount": "75,000",
                    "notice_period_months": "2",
                    "utility_terms": "Electricity, gas, water charges, and common service maintenance fees (BDT 3,000) shall be borne directly by the Tenant.",
                    "witness1_name": "Kamrul Hassan",
                    "witness1_address": "Uttara, Dhaka",
                    "witness2_name": "Sajid Mahmud",
                    "witness2_address": "Mirpur, Dhaka",
                    "custom_clauses": [
                        {
                            "title": "Quiet Enjoyment & Peaceable Possession",
                            "text": "The leased premises shall be utilized exclusively for lawful residential purposes without disturbance, public nuisance, or breach of peace."
                        }
                    ]
                }
            },
            "nda_agreement": {
                "id": "nda_agreement",
                "title_bn": "গোপনীয় তথ্য সুরক্ষা ও প্রকাশ না করার চুক্তিপত্র",
                "title_en": "Non-Disclosure & Confidentiality Agreement",
                "template_file": "nda_agreement.html",
                "category": "Corporate & Tech",
                "defaults_bn": {
                    "execution_date": "১২ সেপ্টেম্বর, ২০২৬",
                    "disclosing_party_name": "টেকনোভেশন সফটওয়্যার লিমিটেড",
                    "disclosing_party_address": "লেভেল ৫, বনানী বাণিজ্যিক এলাকা, ঢাকা",
                    "disclosing_party_rep": "আসিফ ইকবাল (ব্যবস্থাপনা পরিচালক)",
                    "receiving_party_name": "ডাটাফ্লো অ্যানালিটিক্স ইনকর্পোরেশন",
                    "receiving_party_address": "রোড ১১, গুলশান ২, ঢাকা",
                    "receiving_party_rep": "ফাহিম জামান (চিফ টেকনোলজি অফিসার)",
                    "purpose": "প্রস্তাবিত ক্লাউড ইআরপি ও ফিনটেক প্ল্যাটফর্মের যৌথ প্রযুক্তিগত মূল্যায়ন ও কোড রিভিউ পরিচালনা করণ।",
                    "duration_years": "৩",
                    "custom_clauses": [
                        {
                            "title": "কর্মচারী নিয়োগ নিষেধাজ্ঞা",
                            "text": "চুক্তির মেয়াদকালীন সময়ে এবং চুক্তি অবসানের পরবর্তী ১ বছরের মধ্যে কোনো পক্ষ অন্য পক্ষের কোনো প্রকৌশলী বা কর্মীকে নিজ প্রতিষ্ঠানে প্রলুব্ধ বা নিয়োগ প্রদান করিতে পারিবে না।"
                        }
                    ]
                },
                "defaults_en": {
                    "execution_date": "12 September 2026",
                    "disclosing_party_name": "Technovation Software Ltd.",
                    "disclosing_party_address": "Level 5, Banani Commercial Area, Dhaka",
                    "disclosing_party_rep": "Asif Iqbal (Managing Director)",
                    "receiving_party_name": "DataFlow Analytics Inc.",
                    "receiving_party_address": "Road 11, Gulshan 2, Dhaka",
                    "receiving_party_rep": "Fahim Zaman (Chief Technology Officer)",
                    "purpose": "Joint technical evaluation and architectural review of proprietary enterprise cloud software.",
                    "duration_years": "3",
                    "custom_clauses": [
                        {
                            "title": "Non-Solicitation Covenant",
                            "text": "Neither party shall directly or indirectly solicit, induce, or hire any key personnel of the other party during the term hereof and for one year thereafter."
                        }
                    ]
                }
            },
            "freelance_contract": {
                "id": "freelance_contract",
                "title_bn": "ফ্রিল্যান্স সার্ভিস ও পরামর্শক চুক্তিপত্র",
                "title_en": "Independent Contractor & Service Agreement",
                "template_file": "freelance_contract.html",
                "category": "Freelancing & Services",
                "defaults_bn": {
                    "execution_date": "১২ সেপ্টেম্বর, ২০২৬",
                    "client_name": "নেক্সাস ডিজিটাল মার্কেটিং এজেন্সী",
                    "client_address": "ধানমন্ডি ২৭, ঢাকা",
                    "client_email": "client@nexusdigital.com",
                    "freelancer_name": "সাব্বির হোসেন",
                    "freelancer_title": "সফটওয়্যার প্রকৌশলী ও পরামর্শক",
                    "freelancer_address": "মিরপুর ডিওএইচএস, ঢাকা",
                    "freelancer_email": "sabbir.dev@gmail.com",
                    "scope_of_work": "আধুনিক ক্লাউড প্ল্যাটফর্ম, ওয়েব অ্যাপ্লিকেশন তৈরি ও রক্ষণাবেক্ষণ সম্পন্ন করা।",
                    "currency": "৳",
                    "total_amount": "১,৫০,০০০",
                    "payment_milestones": "প্রজেক্ট শুরুর পূর্বে ৩০% অগ্রিম (৳ ৪৫,০০০), আলফা রিলিজ ও অনুমোদনে ৪০% (৳ ৬০,০০০), এবং সোর্স কোড হস্তান্তরে বাকি ৩০% (৳ ৪৫,০০০) পরিশোধযোগ্য হইবে।",
                    "deadline": "১৫ নভেম্বর, ২০২৬",
                    "free_revisions": "৩",
                    "custom_clauses": [
                        {
                            "title": "ত্রুটি সংশোধন সহায়তা",
                            "text": "চূড়ান্ত ডেলিভারির পর পরবর্তী ৩০ দিন পর্যন্ত যেকোনো কারিগরি ত্রুটি সেবা প্রদানকারী কোনো অতিরিক্ত পারিশ্রমিক ছাড়াই সংশোধন করিয়া দিবেন।"
                        }
                    ]
                },
                "defaults_en": {
                    "execution_date": "12 September 2026",
                    "client_name": "Nexus Digital Marketing Agency",
                    "client_address": "Dhanmondi 27, Dhaka",
                    "client_email": "client@nexusdigital.com",
                    "freelancer_name": "Sabbir Hossain",
                    "freelancer_title": "Senior Full-Stack Software Engineer",
                    "freelancer_address": "Mirpur DOHS, Dhaka",
                    "freelancer_email": "sabbir.dev@gmail.com",
                    "scope_of_work": "Design, develop, test, and deploy a secure SaaS e-commerce web application with cloud deployment.",
                    "currency": "USD",
                    "total_amount": "1,500",
                    "payment_milestones": "30% upfront deposit ($450), 40% upon alpha milestone approval ($600), and 30% upon deployment and code transfer ($450).",
                    "deadline": "15 November 2026",
                    "free_revisions": "3",
                    "custom_clauses": [
                        {
                            "title": "Warranty & Defect Rectification",
                            "text": "The Contractor covenants to rectify any technical defect or bug without additional cost within 30 days of final delivery."
                        }
                    ]
                }
            },
            "partnership_agreement": {
                "id": "partnership_agreement",
                "title_bn": "অংশীদারি কারবার চুক্তিপত্র",
                "title_en": "Partnership Deed & Agreement",
                "template_file": "partnership_agreement.html",
                "category": "Business & Trade",
                "defaults_bn": {
                    "execution_date": "১২ সেপ্টেম্বর, ২০২৬",
                    "partner1_name": "আব্দুল্লাহ আল মামুন",
                    "partner1_father": "মরহুম সামসুল হক",
                    "partner1_address": "বনশ্রী, রামপুরা, ঢাকা",
                    "partner1_nid": "১৯৮৮২৬৯২৪১৫৫৬৭৮৯০",
                    "partner1_phone": "০১৭০০-১১২২৩৩",
                    "partner2_name": "মাহমুদুর রহমান",
                    "partner2_father": "মো: রেজাউল করিম",
                    "partner2_address": "খিলগাঁও, ঢাকা",
                    "partner2_nid": "১৯৯০২৬৯২৪১৫০৯৮৭৬৫",
                    "partner2_phone": "০১৮০০-৪৪৫৫৬৬",
                    "firm_name": "মেসার্স ব্লুমিং এগ্রো অ্যান্ড টেক সল্যুশনস",
                    "firm_address": "হাউজ ৪, ব্লক সি, বনশ্রী, ঢাকা",
                    "total_capital": "২০,০০,০০০",
                    "partner1_share": "৫০",
                    "partner2_share": "৫০",
                    "bank_operation": "উভয় অংশীদারের যৌথ স্বাক্ষরে",
                    "notice_period_months": "৩",
                    "custom_clauses": [
                        {
                            "title": "নতুন অংশীদার গ্রহণ বিধি",
                            "text": "উভয় অংশীদারের সর্বসম্মত লিখিত সম্মতি ব্যতীত কোনো তৃতীয় ব্যক্তিকে এই ফার্মের অংশীদার হিসেবে অন্তর্ভুক্ত করা যাইবে না।"
                        }
                    ]
                },
                "defaults_en": {
                    "execution_date": "12 September 2026",
                    "partner1_name": "Abdullah Al Mamun",
                    "partner1_father": "Late Samsul Haque",
                    "partner1_address": "Banasree, Rampura, Dhaka",
                    "partner1_nid": "19882692415567890",
                    "partner1_phone": "+880 1700-112233",
                    "partner2_name": "Mahmudur Rahman",
                    "partner2_father": "Md. Rezaul Karim",
                    "partner2_address": "Khilgaon, Dhaka",
                    "partner2_nid": "19902692415098765",
                    "partner2_phone": "+880 1800-445566",
                    "firm_name": "Blooming Agro & Tech Solutions",
                    "firm_address": "House 4, Block C, Banasree, Dhaka",
                    "total_capital": "2,000,000",
                    "partner1_share": "50",
                    "partner2_share": "50",
                    "bank_operation": "Joint Signatures of both partners",
                    "notice_period_months": "3",
                    "custom_clauses": [
                        {
                            "title": "Admission of New Partners",
                            "text": "No third party shall be admitted as a partner in the firm without the unanimous written consent of both founding partners."
                        }
                    ]
                }
            },
            "employment_agreement": {
                "id": "employment_agreement",
                "title_bn": "কর্মসংস্থান ও চাকরির চুক্তিপত্র",
                "title_en": "Employment Agreement & Appointment Letter",
                "template_file": "employment_agreement.html",
                "category": "HR & Corporate",
                "defaults_bn": {
                    "execution_date": "১২ সেপ্টেম্বর, ২০২৬",
                    "company_name": "ইনোভেক্স ক্লাউড ল্যাবস লিমিটেড",
                    "company_address": "সফটওয়্যার টেকনোলজি পার্ক, কাওরান বাজার, ঢাকা",
                    "company_rep": "সাকিব আল হাসান (প্রধান মানবসম্পদ কর্মকর্তা)",
                    "employee_name": "ফারহান কবির",
                    "employee_father": "মো: রফিকুল আলম",
                    "employee_address": "মোহাম্মদপুর, ঢাকা",
                    "employee_nid": "১৯৯৫২৬৯২৪১৫৭৮৯৪৫৬",
                    "employee_phone": "০১৯১১-২২৩৩৪৪",
                    "designation": "সফটওয়্যার কোয়ালিটি অ্যাসিউরেন্স ইঞ্জিনিয়ার",
                    "department": "প্রকৌশল ও পণ্য উন্নয়ন বিভাগ",
                    "salary_amount": "৬০,০০০",
                    "probation_months": "৩",
                    "notice_period_days": "৩০",
                    "custom_clauses": [
                        {
                            "title": "তথ্যপ্রযুক্তি ও নিরাপত্তা সুরক্ষা",
                            "text": "কর্মকর্তাকে প্রদত্ত প্রাতিষ্ঠানিক ল্যাপটপ ও ডিজিটাল ক্রেডেনশিয়াল শুধুমাত্র অফিশিয়াল কাজে ব্যবহৃত হইবে এবং কোনো সিকিউরিটি কোড তৃতীয় পক্ষের নিকট শেয়ার করা যাইবে না।"
                        }
                    ]
                },
                "defaults_en": {
                    "execution_date": "12 September 2026",
                    "company_name": "Innovex Cloud Labs Ltd.",
                    "company_address": "Software Technology Park, Karwan Bazar, Dhaka",
                    "company_rep": "Sakib Al Hasan (Head of Human Resources)",
                    "employee_name": "Farhan Kabir",
                    "employee_father": "Md. Rafiqul Alam",
                    "employee_address": "Mohammadpur, Dhaka",
                    "employee_nid": "19952692415789456",
                    "employee_phone": "+880 1911-223344",
                    "designation": "Software Quality Assurance Engineer",
                    "department": "Engineering & Product Development",
                    "salary_amount": "60,000",
                    "probation_months": "3",
                    "notice_period_days": "30",
                    "custom_clauses": [
                        {
                            "title": "Information Security & Hardware Care",
                            "text": "All laptops, security credentials, and company intellectual property must be utilized exclusively for authorized corporate duties."
                        }
                    ]
                }
            }
        }

    def list_templates(self) -> List[Dict[str, Any]]:
        result = []
        for t_id, meta in self.templates_meta.items():
            result.append({
                "id": t_id,
                "title_bn": meta["title_bn"],
                "title_en": meta["title_en"],
                "category": meta["category"],
                "defaults": meta["defaults_bn"],
                "defaults_bn": meta["defaults_bn"],
                "defaults_en": meta["defaults_en"]
            })
        return result

    def get_template_meta(self, doc_type: str) -> Dict[str, Any]:
        return self.templates_meta.get(doc_type, self.templates_meta["tenancy_agreement"])

    def render_html(self, doc_type: str, data: Dict[str, Any], language: str = "bn") -> str:
        meta = self.get_template_meta(doc_type)
        template = self.env.get_template(meta["template_file"])
        title = meta["title_bn"] if language == "bn" else meta["title_en"]
        return template.render(
            title=title,
            data=data,
            language=language
        )

    def generate_docx(self, doc_type: str, data: Dict[str, Any], language: str = "bn") -> io.BytesIO:
        meta = self.get_template_meta(doc_type)
        doc = Document()
        title = meta["title_bn"] if language == "bn" else meta["title_en"]
        
        doc.add_heading(title, level=0)
        doc.add_paragraph(f"Execution Date: {data.get('execution_date', '')}")

        doc.add_heading("Parties Involved", level=1)
        for key, val in data.items():
            if isinstance(val, str) and val and not key.startswith("custom"):
                doc.add_paragraph(f"{key.replace('_', ' ').capitalize()}: {val}")

        if "custom_clauses" in data and isinstance(data["custom_clauses"], list):
            doc.add_heading("Special AI Clauses", level=1)
            for c in data["custom_clauses"]:
                doc.add_heading(c.get("title", "Clause"), level=2)
                doc.add_paragraph(c.get("text", ""))

        target_stream = io.BytesIO()
        doc.save(target_stream)
        target_stream.seek(0)
        return target_stream

template_engine = TemplateEngine()
