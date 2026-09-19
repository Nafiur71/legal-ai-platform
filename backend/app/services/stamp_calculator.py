from typing import Dict, Any

class StampCalculatorService:
    @staticmethod
    def calculate_stamp_duty(doc_type: str, rent_amount: float = 0, duration_months: int = 12, deposit_amount: float = 0, total_capital: float = 0) -> Dict[str, Any]:
        """
        Calculates statutory non-judicial stamp duty under The Stamp Act 1899 (Bangladesh)
        and relevant Finance Acts.
        """
        stamp_value = 300
        legal_basis = "স্ট্যাম্প আইন ১৮৯৯ (The Stamp Act, 1899) এর তফসিল-১, অনুচ্ছেদ ৫ অনুযায়ী।"
        explanation = ""
        stamps_breakdown = []
        is_registration_mandatory = False

        dt = (doc_type or "").lower().strip()

        if "tenan" in dt or "rent" in dt or "lease" in dt:
            # Tenancy agreement rules:
            # Under Registration Act 1908 Sec 17(1)(d), lease exceeding 1 year requires compulsory registration.
            if duration_months > 12:
                is_registration_mandatory = True

            if duration_months <= 12:
                stamp_value = 300
                explanation = "১ বছর বা তার কম মেয়াদের আবাসিক/বাণিজ্যিক ভাড়ার চুক্তির জন্য ৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প বাধ্যতামূলক।"
                stamps_breakdown = ["১টি ৩০০ টাকার স্ট্যাম্প (অথবা ৩টি ১০০ টাকার স্ট্যাম্প)"]
            else:
                stamp_value = 300
                explanation = "১ বছরের অধিক মেয়াদের চুক্তির ক্ষেত্রে ৩০০ টাকার স্ট্যাম্পে চুক্তি সম্পাদন করে সাব-রেজিস্ট্রি অফিসে নিবন্ধন (Registration) করা আইনিভাবে বাধ্যতামূলক।"
                stamps_breakdown = ["৩টি ১০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প (বা ১টি ৩০০ টাকার স্ট্যাম্প)"]

        elif "partner" in dt:
            # Partnership Deed (The Stamp Act 1899, Article 46):
            # Up to 50,000 Tk capital: 1,000 Tk. Above 50,000 Tk: 2,000 Tk.
            if total_capital > 50000:
                stamp_value = 2000
                legal_basis = "স্ট্যাম্প আইন ১৮৯৯ এর অনুচ্ছেদ ৪৬(বি) অনুযায়ী (৫০,০০০ টাকার অধিক মূলধনের জন্য)।"
                explanation = "৫০ হাজার টাকার অধিক মূলধনের অংশীদারি চুক্তির জন্য ২০০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প প্রয়োজন।"
                stamps_breakdown = ["২টি ১,০০০ টাকার স্ট্যাম্প অথবা ২০টি ১০০ টাকার স্ট্যাম্প"]
            else:
                stamp_value = 1000
                legal_basis = "স্ট্যাম্প আইন ১৮৯৯ এর অনুচ্ছেদ ৪৬(এ) অনুযায়ী।"
                explanation = "৫০ হাজার টাকা পর্যন্ত মূলধনের অংশীদারি চুক্তির জন্য ১০০০ টাকার স্ট্যাম্প প্রযোজ্য।"
                stamps_breakdown = ["১টি ১,০০০ টাকার স্ট্যাম্প"]

        elif "nda" in dt or "disclos" in dt or "freelance" in dt or "service" in dt:
            stamp_value = 300
            legal_basis = "স্ট্যাম্প আইন ১৮৯৯ এর অনুচ্ছেদ ৫ (সাধারণ চুক্তিপত্র ও সমঝোতা স্মারক)।"
            explanation = "সাধারণ বাণিজ্যিক সেবা, ফ্রিল্যান্সিং বা নন-ডিসক্লোজার চুক্তির জন্য ৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্পে সম্পাদন করাই আইনত যথেষ্ট।"
            stamps_breakdown = ["১টি ৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প"]

        elif "employ" in dt or "job" in dt:
            stamp_value = 300
            legal_basis = "বাংলাদেশ শ্রম আইন ২০০৬ ও স্ট্যাম্প আইন ১৮৯৯।"
            explanation = "কর্মসংস্থান চুক্তি সাধারণ কোম্পানির অফিশিয়াল প্যাডে উভয় পক্ষের স্বাক্ষরে সম্পাদিত হতে পারে, তবে অধিকতর সুরক্ষায় ৩০০ টাকার স্ট্যাম্প ব্যবহার করা শ্রেয়।"
            stamps_breakdown = ["কোম্পানির লেটারহেড প্যাড অথবা ৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প"]

        return {
            "document_type": doc_type,
            "recommended_stamp_value": stamp_value,
            "formatted_stamp": f"৳ {stamp_value:,} টাকা",
            "legal_basis": legal_basis,
            "explanation": explanation,
            "stamps_breakdown": stamps_breakdown,
            "is_registration_mandatory": is_registration_mandatory,
            "tips": [
                "১০০ বা ৩০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প অনুমোদিত ভেন্ডার (Vendor) বা ডিসি অফিস ট্রেজারি থেকে সংগ্রহ করুন।",
                "স্ট্যাম্পের প্রথম পাতায় উভয় পক্ষের নাম, বিষয়বস্তু এবং তারিখ সুস্পষ্টভাবে উল্লেখ থাকতে হবে।",
                "চুক্তির প্রতিটি পাতার নিচে উভয় পক্ষের সংক্ষিপ্ত স্বাক্ষর (Initial) থাকা শ্রেয়।"
            ]
        }

stamp_calculator = StampCalculatorService()
