let state = {
  currentTemplate: 'tenancy_agreement',
  currentLang: 'bn',
  templates: [],
  formData: {},
  customClauses: [],
  debounceTimer: null,
  lastRefinedClause: null,
  isDirectEdit: false,
  showStamp: true,
  currentContractId: null,
  sigTarget: 'p1',
  isDrawing: false,
  watermarkMode: 'none', // 'none' | 'draft' | 'confidential'
  currentDocHash: ''
};

function getVaultSessionId() {
  let vid = localStorage.getItem('smartlegal_vault_id');
  if (!vid) {
    const randPart = Math.random().toString(36).substring(2, 10) + Math.random().toString(36).substring(2, 6);
    vid = 'usr_' + randPart;
    localStorage.setItem('smartlegal_vault_id', vid);
  }
  return vid;
}

const formDefinitions = {
  tenancy_agreement: {
    bn: {
      step1: [
        { id: 'execution_date', label: 'চুক্তির সম্পাদন তারিখ', type: 'text' },
        { id: 'landlord_name', label: 'প্রথম পক্ষ (মালিক)-এর পূর্ণ নাম', type: 'text' },
        { id: 'landlord_father', label: 'প্রথম পক্ষের পিতা/স্বামীর নাম', type: 'text' },
        { id: 'landlord_address', label: 'প্রথম পক্ষের বর্তমান ও স্থায়ী ঠিকানা', type: 'text' },
        { id: 'landlord_nid', label: 'প্রথম পক্ষের জাতীয় পরিচয়পত্র নং', type: 'text' },
        { id: 'landlord_phone', label: 'প্রথম পক্ষের মোবাইল নম্বর', type: 'text' },
        { id: 'tenant_name', label: 'দ্বিতীয় পক্ষ (ভাড়াটিয়া)-এর পূর্ণ নাম', type: 'text' },
        { id: 'tenant_father', label: 'দ্বিতীয় পক্ষের পিতা/স্বামীর নাম', type: 'text' },
        { id: 'tenant_address', label: 'দ্বিতীয় পক্ষের স্থায়ী ঠিকানা', type: 'text' },
        { id: 'tenant_nid', label: 'দ্বিতীয় পক্ষের জাতীয় পরিচয়পত্র নং', type: 'text' },
        { id: 'tenant_phone', label: 'দ্বিতীয় পক্ষের মোবাইল নম্বর', type: 'text' }
      ],
      step2: [
        { id: 'property_address', label: 'ভাড়াকৃত সম্পত্তির ঠিকানা ও পূর্ণ বিবরণ', type: 'textarea' },
        { id: 'property_type', label: 'সম্পত্তির ধরণ (যেমন: আবাসিক ফ্ল্যাট / বাণিজ্যিক দোকান)', type: 'text' },
        { id: 'start_date', label: 'চুক্তি কার্যকরের তারিখ', type: 'text' },
        { id: 'duration_months', label: 'চুক্তির মেয়াদ (মাসে)', type: 'number' },
        { id: 'rent_amount', label: 'মাসিক ভাড়া (টাকায়)', type: 'text' },
        { id: 'rent_in_words', label: 'ভাড়ার পরিমাণ (কথায়)', type: 'text' },
        { id: 'payment_due_day', label: 'প্রতি মাসের কত তারিখের মধ্যে পরিশোধযোগ্য', type: 'number' },
        { id: 'deposit_amount', label: 'অগ্রিম জামানতের পরিমাণ (টাকায়)', type: 'text' },
        { id: 'notice_period_months', label: 'চুক্তি বাতিলের নোটিশের মেয়াদ (মাসে)', type: 'number' },
        { id: 'utility_terms', label: 'ইউটিলিটি বিল ও রক্ষণাবেক্ষণ খরচ শর্ত', type: 'textarea' }
      ],
      step4: [
        { id: 'witness1_name', label: 'প্রথম সাক্ষীর নাম', type: 'text' },
        { id: 'witness1_address', label: 'প্রথম সাক্ষীর পূর্ণ ঠিকানা', type: 'text' },
        { id: 'witness2_name', label: 'দ্বিতীয় সাক্ষীর নাম', type: 'text' },
        { id: 'witness2_address', label: 'দ্বিতীয় সাক্ষীর পূর্ণ ঠিকানা', type: 'text' }
      ]
    },
    en: {
      step1: [
        { id: 'execution_date', label: 'Execution Date', type: 'text' },
        { id: 'landlord_name', label: 'First Party (Landlord) Full Name', type: 'text' },
        { id: 'landlord_father', label: 'Father / Spouse Name', type: 'text' },
        { id: 'landlord_address', label: 'Permanent & Present Address', type: 'text' },
        { id: 'landlord_nid', label: 'National ID (NID) / Passport No.', type: 'text' },
        { id: 'landlord_phone', label: 'Mobile / Phone Number', type: 'text' },
        { id: 'tenant_name', label: 'Second Party (Tenant) Full Name', type: 'text' },
        { id: 'tenant_father', label: 'Father / Spouse Name', type: 'text' },
        { id: 'tenant_address', label: 'Permanent Address', type: 'text' },
        { id: 'tenant_nid', label: 'National ID (NID) No.', type: 'text' },
        { id: 'tenant_phone', label: 'Mobile / Phone Number', type: 'text' }
      ],
      step2: [
        { id: 'property_address', label: 'Demised Premises Address & Description', type: 'textarea' },
        { id: 'property_type', label: 'Premises Type (e.g. Residential Apartment / Office)', type: 'text' },
        { id: 'start_date', label: 'Commencement Date', type: 'text' },
        { id: 'duration_months', label: 'Tenancy Tenor (Months)', type: 'number' },
        { id: 'rent_amount', label: 'Monthly Rent Amount', type: 'text' },
        { id: 'rent_in_words', label: 'Rent in Words', type: 'text' },
        { id: 'payment_due_day', label: 'Monthly Due Date (Calendar Day)', type: 'number' },
        { id: 'deposit_amount', label: 'Security Deposit Amount', type: 'text' },
        { id: 'notice_period_months', label: 'Termination Notice Period (Months)', type: 'number' },
        { id: 'utility_terms', label: 'Utilities & Service Maintenance Terms', type: 'textarea' }
      ],
      step4: [
        { id: 'witness1_name', label: 'First Attesting Witness Name', type: 'text' },
        { id: 'witness1_address', label: 'First Witness Full Address', type: 'text' },
        { id: 'witness2_name', label: 'Second Attesting Witness Name', type: 'text' },
        { id: 'witness2_address', label: 'Second Witness Full Address', type: 'text' }
      ]
    }
  },
  nda_agreement: {
    bn: {
      step1: [
        { id: 'execution_date', label: 'চুক্তির সম্পাদন তারিখ', type: 'text' },
        { id: 'disclosing_party_name', label: 'তথ্য প্রকাশকারী পক্ষ (ব্যক্তি বা প্রতিষ্ঠান)', type: 'text' },
        { id: 'disclosing_party_address', label: 'তথ্য প্রকাশকারী পক্ষের ঠিকানা', type: 'text' },
        { id: 'disclosing_party_rep', label: 'অনুমোদিত প্রতিনিধি ও পদবি', type: 'text' },
        { id: 'receiving_party_name', label: 'তথ্য গ্রহণকারী পক্ষ (ব্যক্তি বা প্রতিষ্ঠান)', type: 'text' },
        { id: 'receiving_party_address', label: 'তথ্য গ্রহণকারী পক্ষের ঠিকানা', type: 'text' },
        { id: 'receiving_party_rep', label: 'অনুমোদিত প্রতিনিধি ও পদবি', type: 'text' }
      ],
      step2: [
        { id: 'purpose', label: 'তথ্য বিনিময়ের মূল বাণিজ্যিক উদ্দেশ্য', type: 'textarea' },
        { id: 'duration_years', label: 'গোপনীয়তার মেয়াদ (বছরে)', type: 'number' }
      ],
      step4: []
    },
    en: {
      step1: [
        { id: 'execution_date', label: 'Date of Execution', type: 'text' },
        { id: 'disclosing_party_name', label: 'Disclosing Party Name / Entity', type: 'text' },
        { id: 'disclosing_party_address', label: 'Principal Business Address', type: 'text' },
        { id: 'disclosing_party_rep', label: 'Authorized Signatory & Designation', type: 'text' },
        { id: 'receiving_party_name', label: 'Receiving Party Name / Entity', type: 'text' },
        { id: 'receiving_party_address', label: 'Principal Business Address', type: 'text' },
        { id: 'receiving_party_rep', label: 'Authorized Signatory & Designation', type: 'text' }
      ],
      step2: [
        { id: 'purpose', label: 'Authorized Commercial Purpose of Disclosure', type: 'textarea' },
        { id: 'duration_years', label: 'Confidentiality Survival Period (Years)', type: 'number' }
      ],
      step4: []
    }
  },
  freelance_contract: {
    bn: {
      step1: [
        { id: 'execution_date', label: 'চুক্তির সম্পাদন তারিখ', type: 'text' },
        { id: 'client_name', label: 'গ্রাহক / প্রতিষ্ঠানের নাম', type: 'text' },
        { id: 'client_address', label: 'গ্রাহক প্রতিষ্ঠানের ঠিকানা', type: 'text' },
        { id: 'client_email', label: 'গ্রাহকের প্রাতিষ্ঠানিক ইমেইল', type: 'text' },
        { id: 'freelancer_name', label: 'সেবা প্রদানকারীর নাম', type: 'text' },
        { id: 'freelancer_title', label: 'পেশাগত পদবি (যেমন: সফটওয়্যার প্রকৌশলী)', type: 'text' },
        { id: 'freelancer_address', label: 'স্থায়ী ঠিকানা', type: 'text' },
        { id: 'freelancer_email', label: 'ব্যক্তিগত / অফিশিয়াল ইমেইল', type: 'text' }
      ],
      step2: [
        { id: 'scope_of_work', label: 'কাজের পরিধি ও ফলাফল বিবরণী', type: 'textarea' },
        { id: 'currency', label: 'মুদ্রা প্রতীক (যেমন: ৳ বা $)', type: 'text' },
        { id: 'total_amount', label: 'সর্বমোট পারিশ্রমিকের পরিমাণ', type: 'text' },
        { id: 'payment_milestones', label: 'পরিশোধের শর্তাবলি ও পর্যায়', type: 'textarea' },
        { id: 'deadline', label: 'কাজের চূড়ান্ত সমর্পণের তারিখ', type: 'text' },
        { id: 'free_revisions', label: 'বিনামূল্যে সংশোধন সংখ্যা', type: 'number' }
      ],
      step4: []
    },
    en: {
      step1: [
        { id: 'execution_date', label: 'Date of Execution', type: 'text' },
        { id: 'client_name', label: 'Client / Company Name', type: 'text' },
        { id: 'client_address', label: 'Client Registered Office Address', type: 'text' },
        { id: 'client_email', label: 'Official Contact Email', type: 'text' },
        { id: 'freelancer_name', label: 'Contractor / Consultant Full Name', type: 'text' },
        { id: 'freelancer_title', label: 'Professional Title / Role', type: 'text' },
        { id: 'freelancer_address', label: 'Permanent Address', type: 'text' },
        { id: 'freelancer_email', label: 'Professional Email Address', type: 'text' }
      ],
      step2: [
        { id: 'scope_of_work', label: 'Scope of Work & Deliverables', type: 'textarea' },
        { id: 'currency', label: 'Currency Symbol (e.g. USD or BDT)', type: 'text' },
        { id: 'total_amount', label: 'Total Agreed Contract Price', type: 'text' },
        { id: 'payment_milestones', label: 'Payment Terms & Milestone Schedule', type: 'textarea' },
        { id: 'deadline', label: 'Completion & Final Delivery Deadline', type: 'text' },
        { id: 'free_revisions', label: 'Complimentary Revision Rounds', type: 'number' }
      ],
      step4: []
    }
  },
  partnership_agreement: {
    bn: {
      step1: [
        { id: 'execution_date', label: 'চুক্তির সম্পাদন তারিখ', type: 'text' },
        { id: 'partner1_name', label: 'প্রথম অংশীদারের পূর্ণ নাম', type: 'text' },
        { id: 'partner1_father', label: 'প্রথম অংশীদারের পিতা/স্বামীর নাম', type: 'text' },
        { id: 'partner1_address', label: 'প্রথম অংশীদারের স্থায়ী ঠিকানা', type: 'text' },
        { id: 'partner1_nid', label: 'প্রথম অংশীদারের জাতীয় পরিচয়পত্র নং', type: 'text' },
        { id: 'partner1_phone', label: 'প্রথম অংশীদারের মোবাইল নম্বর', type: 'text' },
        { id: 'partner2_name', label: 'দ্বিতীয় অংশীদারের পূর্ণ নাম', type: 'text' },
        { id: 'partner2_father', label: 'দ্বিতীয় অংশীদারের পিতা/স্বামীর নাম', type: 'text' },
        { id: 'partner2_address', label: 'দ্বিতীয় অংশীদারের স্থায়ী ঠিকানা', type: 'text' },
        { id: 'partner2_nid', label: 'দ্বিতীয় অংশীদারের জাতীয় পরিচয়পত্র নং', type: 'text' },
        { id: 'partner2_phone', label: 'দ্বিতীয় অংশীদারের মোবাইল নম্বর', type: 'text' }
      ],
      step2: [
        { id: 'firm_name', label: 'অংশীদারি কারবারের নাম', type: 'text' },
        { id: 'firm_address', label: 'প্রধান কার্যালয়ের পূর্ণ ঠিকানা', type: 'text' },
        { id: 'total_capital', label: 'প্রাথমিক মোট মূলধন (টাকায়)', type: 'text' },
        { id: 'partner1_share', label: 'প্রথম অংশীদারের মূলধন ও মুনাফার হার (%)', type: 'number' },
        { id: 'partner2_share', label: 'দ্বিতীয় অংশীদারের মূলধন ও মুনাফার হার (%)', type: 'number' },
        { id: 'bank_operation', label: 'ব্যাংক হিসাব পরিচালনা পদ্ধতি', type: 'text' },
        { id: 'notice_period_months', label: 'কারবার অবসানের নোটিশের মেয়াদ (মাসে)', type: 'number' }
      ],
      step4: []
    },
    en: {
      step1: [
        { id: 'execution_date', label: 'Date of Execution', type: 'text' },
        { id: 'partner1_name', label: 'First Partner Full Name', type: 'text' },
        { id: 'partner1_father', label: 'Father / Spouse Name', type: 'text' },
        { id: 'partner1_address', label: 'Permanent Address', type: 'text' },
        { id: 'partner1_nid', label: 'National ID (NID) / Passport No.', type: 'text' },
        { id: 'partner1_phone', label: 'Mobile / Phone Number', type: 'text' },
        { id: 'partner2_name', label: 'Second Partner Full Name', type: 'text' },
        { id: 'partner2_father', label: 'Father / Spouse Name', type: 'text' },
        { id: 'partner2_address', label: 'Permanent Address', type: 'text' },
        { id: 'partner2_nid', label: 'National ID (NID) / Passport No.', type: 'text' },
        { id: 'partner2_phone', label: 'Mobile / Phone Number', type: 'text' }
      ],
      step2: [
        { id: 'firm_name', label: 'Partnership Firm Name', type: 'text' },
        { id: 'firm_address', label: 'Principal Place of Business', type: 'text' },
        { id: 'total_capital', label: 'Initial Capital Contribution', type: 'text' },
        { id: 'partner1_share', label: 'First Partner Share / Profit Ratio (%)', type: 'number' },
        { id: 'partner2_share', label: 'Second Partner Share / Profit Ratio (%)', type: 'number' },
        { id: 'bank_operation', label: 'Bank Account Operating Authority', type: 'text' },
        { id: 'notice_period_months', label: 'Dissolution Notice Period (Months)', type: 'number' }
      ],
      step4: []
    }
  },
  employment_agreement: {
    bn: {
      step1: [
        { id: 'execution_date', label: 'যোগদানের তারিখ', type: 'text' },
        { id: 'company_name', label: 'নিয়োগকারী প্রতিষ্ঠানের নাম', type: 'text' },
        { id: 'company_address', label: 'প্রতিষ্ঠানের কার্যালয় ঠিকানা', type: 'text' },
        { id: 'company_rep', label: 'অনুমোদিত প্রতিনিধি ও পদবি', type: 'text' },
        { id: 'employee_name', label: 'নিযুক্ত কর্মকর্তা / কর্মচারীর নাম', type: 'text' },
        { id: 'employee_father', label: 'পিতা/স্বামীর নাম', type: 'text' },
        { id: 'employee_address', label: 'স্থায়ী ঠিকানা', type: 'text' },
        { id: 'employee_nid', label: 'জাতীয় পরিচয়পত্র নং', type: 'text' },
        { id: 'employee_phone', label: 'মোবাইল নম্বর', type: 'text' }
      ],
      step2: [
        { id: 'designation', label: 'নির্ধারিত পদবি', type: 'text' },
        { id: 'department', label: 'কার্যনির্বাহী বিভাগ', type: 'text' },
        { id: 'salary_amount', label: 'মাসিক সর্বসাকুল্যে বেতন (টাকায়)', type: 'text' },
        { id: 'probation_months', label: 'শিক্ষানবিসকাল (মাসে)', type: 'number' },
        { id: 'notice_period_days', label: 'চাকরি অবসানের নোটিশের মেয়াদ (দিনে)', type: 'number' }
      ],
      step4: []
    },
    en: {
      step1: [
        { id: 'execution_date', label: 'Appointment / Joining Date', type: 'text' },
        { id: 'company_name', label: 'Employer / Company Name', type: 'text' },
        { id: 'company_address', label: 'Registered Corporate Address', type: 'text' },
        { id: 'company_rep', label: 'Authorized Signatory & Designation', type: 'text' },
        { id: 'employee_name', label: 'Employee Full Legal Name', type: 'text' },
        { id: 'employee_father', label: 'Father / Spouse Name', type: 'text' },
        { id: 'employee_address', label: 'Permanent Address', type: 'text' },
        { id: 'employee_nid', label: 'National ID (NID) / SSN No.', type: 'text' },
        { id: 'employee_phone', label: 'Contact Phone Number', type: 'text' }
      ],
      step2: [
        { id: 'designation', label: 'Job Title / Position', type: 'text' },
        { id: 'department', label: 'Operational Department', type: 'text' },
        { id: 'salary_amount', label: 'Gross Monthly Remuneration', type: 'text' },
        { id: 'probation_months', label: 'Probationary Period (Months)', type: 'number' },
        { id: 'notice_period_days', label: 'Termination Notice Period (Days)', type: 'number' }
      ],
      step4: []
    }
  }
};

const uiTranslations = {
  bn: {
    page_title: "SmartLegal AI - আইনি অটোমেশন ও দলিল জেনারেটর",
    brand_sub: "বুদ্ধিমান আইনি অটোমেশন ও দলিল জেনারেটর",
    nav_notice: "নোটিশ ইঞ্জিন",
    nav_verify: "হ্যাশ যাচাই",
    nav_stamp_calc: "স্ট্যাম্প ক্যালকুলেটর",
    nav_share: "শেয়ার ও সাইন",
    nav_history: "হিস্ট্রি",
    nav_audit: "ফাইল অডিট",
    nav_sign: "ই-স্বাক্ষর",
    nav_save: "সেভ",
    nav_docx: "Word",
    nav_instant_print: "তাত্ক্ষণিক PDF / প্রিন্ট (০ সেকেন্ড)",
    nav_cloud_pdf: "ক্লাউড PDF",
    template_label: "চুক্তিপত্র:",
    step1_tab: "১. পক্ষের তথ্য",
    step2_tab: "২. মূল শর্তাবলি",
    step3_tab: "৩. AI কাস্টম ধারা",
    step4_tab: "৪. স্বাক্ষর ও সমাপ্তি",
    step1_banner_title: "চুক্তির মূল পক্ষদ্বয়:",
    step1_banner_sub: "১ম ও ২য় পক্ষের নাম ও বিবরণ এখানে পরিবর্তন করুন। এই নামসমূহ দলিলের শীর্ষে ও স্বাক্ষরের স্থানে স্বয়ংক্রিয়ভাবে আপডেট হবে।",
    step3_card_title: "AI লিগ্যাল ক্লজ রিফাইনার",
    step3_card_desc: "আপনার কাস্টম কোনো শর্ত সাধারণ ভাষায় লিখুন। আমাদের AI তা আদালত ও চুক্তি আইনসম্মত ভাষায় রূপান্তর করবে।",
    step3_placeholder: "যেমন: 'ভাড়াটিয়া রাত ১১টার পর কোনো বহিরাগত আনতে পারবে না এবং ফ্ল্যাটে কোনো পোষা বিড়াল বা কুকুর রাখা যাবে না...'",
    step3_refine_btn: "AI দিয়ে আইনি ভাষায় পলিশ করুন",
    step3_add_btn: "চুক্তিতে ধারাটি যুক্ত করুন",
    step3_explain_btn: "সহজ ব্যাখ্যা দেখুন",
    step3_clauses_label: "সংযুক্ত কাস্টম শর্তাবলি:",
    step4_banner_text: "১ম ও ২য় পক্ষের নাম পরিবর্তন করতে চান?",
    step4_banner_sub: "মূল চুক্তিকারীদের নাম <strong>১. পক্ষের তথ্য</strong> ট্যাবে রয়েছে।",
    step4_banner_btn: "১ম ট্যাবে যান",
    step4_esign_title: "ডিজিটাল ই-স্বাক্ষর",
    step4_esign_desc: "স্ক্রিনে সরাসরি স্বাক্ষর করুন অথবা লিংক পাঠিয়ে অপর পক্ষের স্বাক্ষর সংগ্রহ করুন।",
    step4_esign_btn: "স্বাক্ষর ক্যানভাস খুলুন",
    step4_witness_title: "সাক্ষীগণের নাম ও ঠিকানা (দলিলের শেষ অংশে):",
    step4_no_witness: "এই চুক্তির জন্য পৃথক সাক্ষীর ফর্ম প্রযোজ্য নয়। মূল পক্ষদ্বয়ের সরাসরি স্বাক্ষরই যথেষ্ট।",
    preview_edit_btn: "সরাসরি পেপারে এডিট",
    preview_stamp_btn: "৩০০ টাকার স্ট্যাম্প",
    preview_watermark_btn: "ওয়াটারমার্ক: বন্ধ",
    preview_a4_badge: "A4 (২১০×২৯৭মিমি)",
    preview_secured: "সিকিউরড",
    preview_sha_calc: "গণনা হচ্ছে...",
    preview_empty: "ডকুমেন্ট রেন্ডার হচ্ছে...",
    chatbot_title: "আইনAI সহকারী",
    chatbot_welcome: "👋 নমস্কার! আমি আপনার <strong>আইনAI সহকারী</strong>।<br>চুক্তিপত্র, স্ট্যাম্পের নিয়ম, ভাড়া নিয়ন্ত্রণ আইন বা নোটিশ বিষয়ে যেকোনো আইনি প্রশ্ন আমাকে বাংলায় জিজ্ঞেস করতে পারেন।",
    chatbot_placeholder: "আইনি প্রশ্নটি লিখুন...",
    tmpl_tenancy: "🏠 বাড়ি / ফ্ল্যাট / দোকান ভাড়ার চুক্তিপত্র",
    tmpl_nda: "🔒 গোপনীয় তথ্য সুরক্ষা ও প্রকাশ না করার চুক্তিপত্র",
    tmpl_freelance: "💼 ফ্রিল্যান্স সার্ভিস ও পরামর্শক চুক্তিপত্র",
    tmpl_partnership: "🤝 অংশীদারি কারবার চুক্তিপত্র",
    tmpl_employment: "👔 কর্মসংস্থান ও চাকরির চুক্তিপত্র"
  },
  en: {
    page_title: "SmartLegal AI - Legal Automation & Deed Generator",
    brand_sub: "Intelligent Legal Automation & Document Generator",
    nav_notice: "Notice Engine",
    nav_verify: "Verify Hash",
    nav_stamp_calc: "Stamp Calculator",
    nav_share: "Share & Sign",
    nav_history: "History",
    nav_audit: "File Audit",
    nav_sign: "E-Signature",
    nav_save: "Save",
    nav_docx: "Word",
    nav_instant_print: "Instant Print / PDF (0s)",
    nav_cloud_pdf: "Cloud PDF",
    template_label: "Agreement:",
    step1_tab: "1. Parties Information",
    step2_tab: "2. Terms & Conditions",
    step3_tab: "3. AI Custom Clauses",
    step4_tab: "4. Signatures & Execution",
    step1_banner_title: "Principal Parties:",
    step1_banner_sub: "Enter details for the First and Second Parties. These names will automatically update across deed headings and signature lines.",
    step3_card_title: "AI Legal Clause Refiner",
    step3_card_desc: "Describe your custom conditions in plain language. Our AI will draft them in formal, court-admissible legal phrasing.",
    step3_placeholder: "e.g. 'The tenant shall not bring unauthorized visitors after 11 PM and pets are strictly prohibited...'",
    step3_refine_btn: "Refine with Legal AI",
    step3_add_btn: "Add Clause to Agreement",
    step3_explain_btn: "View Plain Summary",
    step3_clauses_label: "Attached Custom Clauses:",
    step4_banner_text: "Want to edit party names?",
    step4_banner_sub: "Party details can be edited under <strong>1. Parties Information</strong> tab.",
    step4_banner_btn: "Go to Step 1",
    step4_esign_title: "Digital E-Signature",
    step4_esign_desc: "Draw your signature directly on screen or send a share link to collect remote signatures.",
    step4_esign_btn: "Open Signature Pad",
    step4_witness_title: "Attesting Witnesses (Execution Page):",
    step4_no_witness: "No separate witnesses required for this agreement. Direct signatures of both parties are sufficient.",
    preview_edit_btn: "Edit Directly on Paper",
    preview_stamp_btn: "Stamp Paper (BDT 300)",
    preview_watermark_btn: "Watermark: Off",
    preview_a4_badge: "A4 (210×297mm)",
    preview_secured: "Secured",
    preview_sha_calc: "Calculating...",
    preview_empty: "Rendering document...",
    chatbot_title: "Legal AI Assistant",
    chatbot_welcome: "👋 Hello! I am your <strong>Legal AI Assistant</strong>.<br>You may ask any questions regarding agreements, contract terms, or legal notices in English.",
    chatbot_placeholder: "Ask a legal question...",
    tmpl_tenancy: "🏠 Residential & Commercial Tenancy Agreement",
    tmpl_nda: "🔒 Non-Disclosure & Confidentiality Agreement",
    tmpl_freelance: "💼 Independent Contractor & Service Agreement",
    tmpl_partnership: "🤝 Partnership Deed & Agreement",
    tmpl_employment: "👔 Employment Contract & Appointment Letter"
  }
};

function applyLanguage(lang) {
  state.currentLang = lang;
  document.documentElement.lang = lang;
  const t = uiTranslations[lang] || uiTranslations.bn;
  const isEn = lang === 'en';

  const setTxt = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
  };
  const setHtml = (id, html) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  };

  // Header & Brand
  document.title = t.page_title;
  setTxt('lbl-brand-title', 'SmartLegal AI');
  setTxt('lbl-brand-desc', t.brand_sub);

  // Navbar buttons
  setTxt('lbl-nav-notice', t.nav_notice);
  setTxt('lbl-nav-verify', t.nav_verify);
  setTxt('lbl-nav-stamp-calc', t.nav_stamp_calc);
  setTxt('lbl-nav-share', t.nav_share);
  setTxt('lbl-nav-history', t.nav_history);
  setTxt('lbl-nav-audit', t.nav_audit);
  setTxt('lbl-nav-sign', t.nav_sign);
  setTxt('lbl-nav-save', t.nav_save);
  setTxt('lbl-nav-docx', t.nav_docx);
  setTxt('lbl-nav-instant-print', t.nav_instant_print);
  setTxt('lbl-nav-cloud-pdf', t.nav_cloud_pdf);

  // Template select label & options
  setTxt('template-select-label', t.template_label);
  const tmplSelect = document.getElementById('template-select');
  if (tmplSelect && tmplSelect.options) {
    Array.from(tmplSelect.options).forEach(opt => {
      if (opt.value === 'tenancy_agreement') opt.text = t.tmpl_tenancy;
      else if (opt.value === 'nda_agreement') opt.text = t.tmpl_nda;
      else if (opt.value === 'freelance_contract') opt.text = t.tmpl_freelance;
      else if (opt.value === 'partnership_agreement') opt.text = t.tmpl_partnership;
      else if (opt.value === 'employment_agreement') opt.text = t.tmpl_employment;
    });
  }

  // Wizard Tabs
  setTxt('lbl-tab-1', t.step1_tab);
  setTxt('lbl-tab-2', t.step2_tab);
  setTxt('lbl-tab-3', t.step3_tab);
  setTxt('lbl-tab-4', t.step4_tab);

  // Step 1 Banner
  setHtml('step1-banner-title', `<i class="fa-solid fa-users"></i> ${t.step1_banner_title}`);
  setTxt('step1-banner-sub', t.step1_banner_sub);

  // Step 3 AI Card
  setTxt('step3-card-title', t.step3_card_title);
  setTxt('step3-card-desc', t.step3_card_desc);
  const aiInput = document.getElementById('ai-clause-input');
  if (aiInput) aiInput.placeholder = t.step3_placeholder;
  setTxt('lbl-refine-clause', t.step3_refine_btn);
  setTxt('lbl-add-clause', t.step3_add_btn);
  setTxt('lbl-explain-clause-action', t.step3_explain_btn);
  setTxt('step3-clauses-header', t.step3_clauses_label);

  // Step 4
  setTxt('step4-banner-text', t.step4_banner_text);
  setHtml('step4-banner-sub', t.step4_banner_sub);
  setTxt('lbl-step4-go-step1', t.step4_banner_btn);
  setTxt('step4-esign-title', t.step4_esign_title);
  setTxt('step4-esign-desc', t.step4_esign_desc);
  setTxt('lbl-step4-sign-btn', t.step4_esign_btn);
  setTxt('step4-witness-title', t.step4_witness_title);

  // Preview Action Bar
  if (!state.isDirectEdit) setTxt('edit-mode-label', t.preview_edit_btn);
  setTxt('stamp-mode-label', t.preview_stamp_btn);
  if (state.watermarkMode === 'none') setTxt('watermark-label', t.preview_watermark_btn);
  else if (state.watermarkMode === 'draft') setTxt('watermark-label', isEn ? 'Watermark: Draft' : 'ওয়াটারমার্ক: খসড়া');
  else if (state.watermarkMode === 'confidential') setTxt('watermark-label', isEn ? 'Watermark: Confidential' : 'ওয়াটারমার্ক: গোপনীয়');
  setTxt('lbl-a4-badge', t.preview_a4_badge);
  setTxt('crypto-secured-label', t.preview_secured);
  setTxt('preview-loading-text', t.preview_empty);

  // Chatbot
  setTxt('chatbot-header-title', t.chatbot_title);
  const chatInput = document.getElementById('chat-input');
  if (chatInput) chatInput.placeholder = t.chatbot_placeholder;
  const welcomeBubble = document.getElementById('chatbot-welcome-bubble');
  if (welcomeBubble) welcomeBubble.innerHTML = t.chatbot_welcome;

  // Modals
  setTxt('stamp-calc-title', isEn ? 'Stamp Duty Calculator' : 'বাংলাদেশ স্ট্যাম্প ডিউটি ক্যালকুলেটর');
  setTxt('calc-doc-type-label', isEn ? 'Agreement Type:' : 'চুক্তির ধরণ:');
  setTxt('calc-amount-label', isEn ? 'Amount (Rent / Capital):' : 'টাকার পরিমাণ (ভাড়া / মূলধন):');
  setTxt('calc-duration-label', isEn ? 'Tenor (Months):' : 'মেয়াদ (মাসে):');
  setTxt('lbl-calc-btn', isEn ? 'Calculate Duty' : 'হিসাব করুন');
  const btnCloseStamp = document.getElementById('btn-close-stamp-calc-footer');
  if (btnCloseStamp) btnCloseStamp.innerText = isEn ? 'Close' : 'বন্ধ করুন';

  setTxt('share-modal-title', isEn ? 'Remote Signing & Sharing Link' : 'দূরবর্তী স্বাক্ষর ও শেয়ারিং লিংক');
  setTxt('share-modal-desc', isEn ? 'Send this secure link to the counterparty. They can review and sign the agreement digitally from any browser or phone:' : 'নিচের লিংকটি অপর পক্ষের কাছে পাঠান। তারা তাদের ডিভাইস থেকেই চুক্তি পড়ে সরাসরি ডিজিটাল সই করতে পারবেন:');
  setTxt('lbl-copy-share', isEn ? 'Copy' : 'কপি');
  setTxt('lbl-whatsapp-share', isEn ? 'Send via WhatsApp' : 'হোয়াটসঅ্যাপে পাঠান');
  const btnCloseShare = document.getElementById('btn-close-share-footer');
  if (btnCloseShare) btnCloseShare.innerText = isEn ? 'Close' : 'বন্ধ করুন';

  setTxt('sign-modal-title', isEn ? 'Digital Signature Pad' : 'ডিজিটাল স্বাক্ষর প্যাড');
  setTxt('lbl-signing-party', isEn ? 'Currently Signing:' : 'বর্তমানে স্বাক্ষর করছেন:');
  setTxt('lbl-pad-guide', isEn ? 'Sign using mouse or finger on the pad below' : 'মাউস বা আঙুল দিয়ে নিচের প্যাডে সই করুন');
  setTxt('lbl-existing-sig', isEn ? 'Saved Signature:' : 'বর্তমান স্বাক্ষর:');
  setTxt('lbl-re-sign', isEn ? 'Clear & Re-sign' : 'মুছে নতুন সই দিন');
  setTxt('lbl-sig-line', isEn ? 'Signature Line' : 'স্বাক্ষর লাইন');
  setTxt('lbl-clear-pad', isEn ? 'Clear' : 'পরিষ্কার');
  setTxt('lbl-apply-signature', isEn ? 'Attach Signature' : 'স্বাক্ষর সংযুক্ত করুন');
  const btnCloseSign = document.getElementById('btn-close-sign-footer');
  if (btnCloseSign) btnCloseSign.innerText = isEn ? 'Cancel' : 'বাতিল';

  setTxt('history-modal-title', isEn ? 'Saved Agreements (Database History)' : 'সংরক্ষিত চুক্তিসমূহ');
  const btnCloseHist = document.getElementById('btn-close-history-footer');
  if (btnCloseHist) btnCloseHist.innerText = isEn ? 'Close' : 'বন্ধ করুন';

  setTxt('upload-modal-title', isEn ? 'Document Upload & AI Compliance Audit' : 'বাইরের ডকুমেন্ট আপলোড ও AI অডিট');
  setHtml('upload-file-label', isEn ? '<i class="fa-solid fa-cloud-arrow-up" style="color: #7c3aed;"></i> Upload Agreement File (PDF, DOCX, TXT):' : '<i class="fa-solid fa-cloud-arrow-up" style="color: #7c3aed;"></i> চুক্তিপত্র ফাইল আপলোড করুন (PDF, DOCX, TXT):');
  setTxt('lbl-upload-size-max', isEn ? 'Max 15 MB' : 'সর্বোচ্চ ১৫ মেগাবাইট');
  setTxt('upload-text-label', isEn ? 'Or paste / edit full contract text below:' : 'অথবা চুক্তিপত্রের সম্পূর্ণ টেক্সট নিচে পেস্ট/সম্পাদনা করুন:');
  const uploadTextInput = document.getElementById('upload-text-input');
  if (uploadTextInput) uploadTextInput.placeholder = isEn ? 'File content will appear here automatically, or paste contract text directly...' : 'ফাইলের টেক্সট স্বয়ংক্রিয়ভাবে এখানে চলে আসবে অথবা যেকোনো চুক্তিপত্র সরাসরি এখানে পেস্ট করুন...';
  setTxt('lbl-run-audit-btn', isEn ? 'Audit Agreement with AI' : 'AI দিয়ে সম্পূর্ণ চুক্তি অডিট করুন');
  const btnCloseUpload = document.getElementById('btn-close-upload-footer');
  if (btnCloseUpload) btnCloseUpload.innerText = isEn ? 'Close' : 'বন্ধ করুন';

  setTxt('explainer-modal-title', isEn ? 'Plain Legal Summary & Risk Assessment' : 'সহজ ভাষায় আইনি ধারার অর্থ');
  const btnCloseExp = document.getElementById('btn-close-explainer-footer');
  if (btnCloseExp) btnCloseExp.innerText = isEn ? 'Close' : 'বন্ধ করুন';

  setTxt('notice-modal-title', isEn ? 'Legal Notice Engine' : 'আইনি নোটিশ জেনারেটর');
  setTxt('notice-modal-desc', isEn ? 'Draft formal legal notices, eviction demands, or contract renewal letters with one click.' : 'ভাড়াটিয়া বা সংশ্লিষ্ট পক্ষের অনুকূলে এক ক্লিকে আইনি নোটিশ, উচ্ছেদ পত্র অথবা বকেয়া তাগিদপত্র প্রস্তুত করুন।');
  setTxt('notice-type-label', isEn ? 'Select Notice Type:' : 'নোটিশের ধরণ নির্বাচন করুন:');
  const noticeTypeSelect = document.getElementById('notice-type-select');
  if (noticeTypeSelect && noticeTypeSelect.options) {
    if (noticeTypeSelect.options[0]) noticeTypeSelect.options[0].text = isEn ? '🏠 Eviction & Vacate Notice' : '🏠 বাসা / দোকান ছাড়ার আইনি নোটিশ';
    if (noticeTypeSelect.options[1]) noticeTypeSelect.options[1].text = isEn ? '📄 Contract Renewal Proposal' : '📄 চুক্তি নবায়ন ও শর্ত প্রস্তাবনা পত্র';
    if (noticeTypeSelect.options[2]) noticeTypeSelect.options[2].text = isEn ? '⚠️ Rent Arrears Demand Notice' : '⚠️ বকেয়া ভাড়া ও পাওনা নিষ্পত্তির তাগিদপত্র';
  }
  setTxt('notice-landlord-label', isEn ? 'Notice Sender (First Party):' : 'নোটিশ প্রেরক (১ম পক্ষ):');
  setTxt('notice-tenant-label', isEn ? 'Notice Recipient (Second Party):' : 'নোটিশ প্রাপক (২য় পক্ষ):');
  setTxt('notice-address-label', isEn ? 'Premises / Property Full Address:' : 'সম্পত্তি / প্রাঙ্গণের পূর্ণ ঠিকানা:');
  setTxt('notice-reason-label', isEn ? 'Specific Ground or Details (Optional):' : 'বিশেষ কারণ বা অতিরিক্ত বিবরণ (ঐচ্ছিক):');
  setTxt('lbl-generate-notice-btn', isEn ? 'Generate Legal Notice' : 'প্রফেশনাল আইনি নোটিশ তৈরি করুন');
  setTxt('lbl-copy-notice', isEn ? 'Copy' : 'কপি');
  setTxt('lbl-inject-notice', isEn ? 'View in Preview' : 'প্রিভিউতে দেখুন');
  const btnCloseNotice = document.getElementById('btn-close-notice-footer');
  if (btnCloseNotice) btnCloseNotice.innerText = isEn ? 'Close' : 'বন্ধ করুন';

  setTxt('verify-modal-title', isEn ? 'SHA-256 Cryptographic Hash & Tamper-Proof Verification' : 'SHA-256 ক্রিপ্টোগ্রাফিক হ্যাশ ও প্রমাণিকতা যাচাই');
  setTxt('verify-modal-desc', isEn ? 'Each agreement is bound to a unique cryptographic mathematical hash. Any alteration post-signing breaks the hash.' : 'প্রতিটি দলিলের জন্য একটি অনন্য গাণিতিক হ্যাশ তৈরি হয়। চুক্তি স্বাক্ষরের পর কোনো একটি অক্ষরও পরিবর্তন হলে এই হ্যাশ পরিবর্তিত হয়ে যায়।');
  setTxt('verify-active-hash-label', isEn ? 'Current Active Document Hash:' : 'বর্তমান দলিলের সক্রিয় হ্যাশ:');
  setTxt('verify-input-label', isEn ? 'Paste reference hash code to verify authenticity:' : 'যাচাই করার জন্য রেফারেন্স হ্যাশ বা কোড পেস্ট করুন:');
  setTxt('lbl-run-verify-btn', isEn ? 'Verify Document Authenticity' : 'দলিলের প্রমাণিকতা যাচাই করুন');
  const btnCloseVerify = document.getElementById('btn-close-verify-footer');
  if (btnCloseVerify) btnCloseVerify.innerText = isEn ? 'Close' : 'বন্ধ করুন';
}

async function initApp() {
  try {
    const res = await fetch('/api/templates');
    state.templates = await res.json();
    
    // Check if remote signing view requested via URL param (?share_id=...)
    const urlParams = new URLSearchParams(window.location.search);
    const shareId = urlParams.get('share_id');
    if (shareId) {
      await loadSharedContractForSigning(shareId);
    } else {
      setupTemplate(state.currentTemplate);
    }
  } catch (err) {
    console.error('Failed to load templates:', err);
  }

  applyLanguage(state.currentLang);
  initSignatureCanvas();
  attachEvents();
}

async function loadSharedContractForSigning(shareId) {
  try {
    const res = await fetch(`/api/contracts/share/${shareId}`);
    if (res.ok) {
      const item = await res.json();
      state.currentContractId = item.id;
      state.currentTemplate = item.document_type;
      state.currentLang = item.language || 'bn';
      const tmplSelect = document.getElementById('template-select');
      if (tmplSelect) tmplSelect.value = item.document_type;
      const langSelect = document.getElementById('lang-select');
      if (langSelect) langSelect.value = state.currentLang;
      applyLanguage(state.currentLang);
      setupTemplate(item.document_type, item.data);
      
      // Auto prompt 2nd party to sign
      setTimeout(() => {
        openSignModal('p2');
      }, 600);
    } else {
      alert(state.currentLang === 'en' ? 'The shared agreement was not found or link is invalid.' : 'শেয়ারকৃত চুক্তিপত্রটি পাওয়া যায়নি বা লিংকটি সঠিক নয়।');
    }
  } catch (e) {
    console.error('Failed to load shared contract:', e);
    alert('Load error: ' + e.message);
  }
}

function setupTemplate(docType, loadedData = null) {
  state.currentTemplate = docType;
  
  if (loadedData) {
    state.formData = loadedData;
    state.customClauses = loadedData.custom_clauses || [];
  } else {
    const currentMeta = state.templates.find(t => t.id === docType);
    if (currentMeta) {
      const defaults = state.currentLang === 'en'
        ? (currentMeta.defaults_en || currentMeta.defaults)
        : (currentMeta.defaults_bn || currentMeta.defaults);
      state.formData = JSON.parse(JSON.stringify(defaults || {}));
      state.customClauses = state.formData.custom_clauses || [];
    } else {
      state.formData = {};
      state.customClauses = [];
    }
  }

  renderFormFields();
  renderCustomClausesList();
  triggerDocumentRender();
}

function renderFormFields() {
  const templateDef = formDefinitions[state.currentTemplate] || formDefinitions.tenancy_agreement;
  const def = templateDef[state.currentLang] || templateDef.bn;

  const buildFields = (fields) => {
    return fields.map(f => {
      const val = state.formData[f.id] || '';
      if (f.type === 'textarea') {
        return `
          <div class="form-group">
            <label class="form-label">${f.label}</label>
            <textarea class="form-textarea field-input" data-key="${f.id}" rows="2">${val}</textarea>
          </div>
        `;
      }
      return `
        <div class="form-group">
          <label class="form-label">${f.label}</label>
          <input type="${f.type}" class="form-input field-input" data-key="${f.id}" value="${val}">
        </div>
      `;
    }).join('');
  };

  document.getElementById('parties-form-fields').innerHTML = buildFields(def.step1 || []);
  document.getElementById('terms-form-fields').innerHTML = buildFields(def.step2 || []);
  
  const step4Container = document.getElementById('witness-form-fields');
  if (def.step4 && def.step4.length > 0) {
    step4Container.innerHTML = buildFields(def.step4);
  } else {
    const noWitnessNotice = state.currentLang === 'en'
      ? 'No separate attesting witnesses required for this agreement. Direct execution by both parties is sufficient.'
      : 'এই চুক্তির জন্য পৃথক সাক্ষীর ফর্ম প্রযোজ্য নয়। মূল পক্ষদ্বয়ের সরাসরি স্বাক্ষরই যথেষ্ট।';
    step4Container.innerHTML = `<p style="color: #64748b; font-size: 0.9rem;">${noWitnessNotice}</p>`;
  }

  document.querySelectorAll('.field-input').forEach(input => {
    input.addEventListener('input', (e) => {
      const key = e.target.getAttribute('data-key');
      state.formData[key] = e.target.value;
      debouncedRender();
    });
  });
}

function debouncedRender() {
  if (state.isDirectEdit) return;
  clearTimeout(state.debounceTimer);
  state.debounceTimer = setTimeout(() => {
    triggerDocumentRender();
  }, 250);
}

async function triggerDocumentRender() {
  try {
    state.formData.custom_clauses = state.customClauses;
    const previewPanel = document.querySelector('.preview-panel');
    const savedScrollTop = previewPanel ? previewPanel.scrollTop : 0;

    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_type: state.currentTemplate,
        language: state.currentLang,
        data: state.formData
      })
    });
    if (res.ok) {
      const data = await res.json();
      const container = document.getElementById('preview-container');
      container.innerHTML = data.rendered_html;

      // Restore scroll position so typing does not yank the user back to the top of page 1
      if (previewPanel && savedScrollTop > 0) {
        previewPanel.scrollTop = savedScrollTop;
      }

      const stamp = document.getElementById('stamp-header');
      if (stamp) {
        stamp.style.display = state.showStamp ? 'flex' : 'none';
      }

      attachClauseExplainerButtons();
      attachSignatureBoxClicks();
      applyWatermarkToPreview();
      refreshDocumentHash();
      updatePageGuideAndCount();
    }
  } catch (err) {
    console.error('Render error:', err);
  }
}

function updatePageGuideAndCount() {
  const container = document.getElementById('preview-container');
  const badge = document.getElementById('preview-page-count-badge');
  if (!container) return;

  const isEn = state.currentLang === 'en';

  // Remove existing dividers
  container.querySelectorAll('.preview-page-divider').forEach(d => d.remove());

  // Wait a microtask / frame for CSS reflow to give exact pixel metrics
  requestAnimationFrame(() => {
    // 1 A4 page height in pixels at 96 DPI: 297mm * 96 / 25.4 = ~1122.5px
    const a4HeightPx = 1122.5;
    const totalHeight = container.scrollHeight;
    const pageCount = Math.max(1, Math.ceil(totalHeight / a4HeightPx));

    if (badge) {
      badge.innerHTML = `<i class="fa-solid fa-file"></i> ${isEn ? (pageCount + (pageCount > 1 ? ' Pages (A4)' : ' Page (A4)')) : (pageCount + ' পৃষ্ঠা (A4)')}`;
    }

    // If content spans more than 1 A4 page, show clear boundary markers
    if (pageCount > 1) {
      for (let p = 1; p < pageCount; p++) {
        const topOffset = p * a4HeightPx;
        const divider = document.createElement('div');
        divider.className = 'preview-page-divider';
        divider.style.top = `${topOffset}px`;
        divider.innerHTML = isEn
          ? `<span><i class="fa-solid fa-scissors"></i> End of Page ${p} • Start of Page ${p + 1} (A4 Page Break)</span>`
          : `<span><i class="fa-solid fa-scissors"></i> পৃষ্ঠা ${p} সমাপ্ত • পৃষ্ঠা ${p + 1} শুরু</span>`;
        container.appendChild(divider);
      }
    }
  });
}

function applyWatermarkToPreview() {
  const container = document.getElementById('preview-container');
  if (!container) return;

  const existingOverlay = container.querySelector('.sla-watermark-overlay');
  if (existingOverlay) existingOverlay.remove();

  if (state.watermarkMode === 'none') return;

  const isEn = state.currentLang === 'en';
  const labels = isEn
    ? { draft: 'DRAFT COPY', confidential: 'STRICTLY CONFIDENTIAL' }
    : { draft: 'খসড়া দলিল', confidential: 'অতি গোপনীয়' };

  const overlay = document.createElement('div');
  overlay.className = 'sla-watermark-overlay';
  overlay.innerText = labels[state.watermarkMode] || (isEn ? 'DRAFT COPY' : 'খসড়া দলিল');
  overlay.style.cssText = 'position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-32deg); font-size: 52px; font-weight: 900; color: rgba(220, 38, 38, 0.12); text-transform: uppercase; letter-spacing: 5px; pointer-events: none; z-index: 10; white-space: nowrap; user-select: none; text-align: center; border: 6px dashed rgba(220, 38, 38, 0.14); padding: 14px 30px; border-radius: 12px;';
  container.style.position = 'relative';
  container.appendChild(overlay);
}

async function refreshDocumentHash() {
  try {
    const container = document.getElementById('preview-container');
    if (!container) return;
    const cleanText = container.innerText || '';
    const res = await fetch('/api/tools/generate-hash', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: cleanText })
    });
    if (res.ok) {
      const data = await res.json();
      state.currentDocHash = data.sha256 || '';
      const badge = document.getElementById('sha-badge-text');
      if (badge) badge.innerText = data.short_hash || '...';
      const fullDisplay = document.getElementById('current-doc-full-hash');
      if (fullDisplay) fullDisplay.innerText = data.sha256 || '';
    }
  } catch (e) {
    console.error('Hash update error:', e);
  }
}

function attachClauseExplainerButtons() {
  const isEn = state.currentLang === 'en';
  const clauses = document.querySelectorAll('#preview-container .clause-item');
  clauses.forEach((cl) => {
    const existingBtn = cl.querySelector('.clause-explain-btn');
    if (!existingBtn) {
      const btn = document.createElement('span');
      btn.className = 'clause-explain-btn';
      btn.innerHTML = `<i class="fa-solid fa-lightbulb"></i> ${isEn ? 'Explain' : 'ব্যাখ্যা'}`;
      btn.title = isEn ? 'Click to see plain summary and risk assessment' : 'ক্লিক করুন: এই ধারাটির সহজ অর্থ ও ঝুঁকি দেখতে';
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openClauseExplainer(cl.innerText);
      });
      cl.appendChild(btn);
    }
  });
}

function renderCustomClausesList() {
  const isEn = state.currentLang === 'en';
  const list = document.getElementById('custom-clauses-list');
  if (state.customClauses.length === 0) {
    list.innerHTML = `<p style="color: #94a3b8; font-size: 0.85rem;">${isEn ? 'No custom clauses added.' : 'কোনো বিশেষ শর্ত যুক্ত করা হয়নি।'}</p>`;
    return;
  }

  list.innerHTML = state.customClauses.map((c, idx) => `
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <strong style="font-size: 0.85rem; color: #1e3a8a;">${c.title || (isEn ? 'Custom Clause' : 'বিশেষ ধারা')}</strong>
        <button class="btn btn-secondary" style="padding: 2px 8px; font-size: 0.75rem; color: #ef4444;" onclick="deleteCustomClause(${idx})">
          <i class="fa-solid fa-trash"></i> ${isEn ? 'Delete' : 'মুছে ফেলুন'}
        </button>
      </div>
      <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">${c.text}</p>
    </div>
  `).join('');
}

window.deleteCustomClause = function(idx) {
  state.customClauses.splice(idx, 1);
  renderCustomClausesList();
  triggerDocumentRender();
};

function getPartyLabels() {
  const tmpl = state.currentTemplate;
  const isEn = state.currentLang === 'en';

  if (isEn) {
    if (tmpl === 'employment_agreement') {
      return { p1: 'Employer', p2: 'Employee' };
    } else if (tmpl === 'freelance_contract') {
      return { p1: 'Client', p2: 'Contractor' };
    } else if (tmpl === 'partnership_agreement') {
      return { p1: 'First Partner', p2: 'Second Partner' };
    } else if (tmpl === 'nda_agreement') {
      return { p1: 'Disclosing Party', p2: 'Receiving Party' };
    }
    return { p1: 'Landlord (First Party)', p2: 'Tenant (Second Party)' };
  }

  if (tmpl === 'employment_agreement') {
    return { p1: 'নিয়োগকারী প্রতিষ্ঠান', p2: 'কর্মকর্তা / কর্মচারী' };
  } else if (tmpl === 'freelance_contract') {
    return { p1: 'গ্রাহক', p2: 'ফ্রিল্যান্সার / সেবা প্রদানকারী' };
  } else if (tmpl === 'partnership_agreement') {
    return { p1: 'প্রথম অংশীদার', p2: 'দ্বিতীয় অংশীদার' };
  } else if (tmpl === 'nda_agreement') {
    return { p1: 'তথ্য প্রকাশকারী পক্ষ', p2: 'তথ্য গ্রহণকারী পক্ষ' };
  }
  return { p1: 'প্রথম পক্ষ (মালিক)', p2: 'দ্বিতীয় পক্ষ (ভাড়াটিয়া)' };
}

function selectSignParty(party) {
  state.sigTarget = party;
  const isEn = state.currentLang === 'en';
  const labels = getPartyLabels();
  const targetP1 = document.getElementById('sign-target-p1');
  const targetP2 = document.getElementById('sign-target-p2');
  const p1Badge = document.getElementById('p1-status-badge');
  const p2Badge = document.getElementById('p2-status-badge');
  const signerNameEl = document.getElementById('current-signer-name');
  const existingBox = document.getElementById('existing-sig-box');
  const existingImg = document.getElementById('existing-sig-img');

  const p1Signed = !!state.formData.party1_signature;
  const p2Signed = !!state.formData.party2_signature;

  if (p1Badge) {
    p1Badge.innerHTML = p1Signed
      ? `<i class="fa-solid fa-check"></i> ${isEn ? 'Signed' : 'স্বাক্ষরিত'}`
      : (isEn ? 'Pending Signature' : 'স্বাক্ষর বাকি');
    p1Badge.style.background = p1Signed ? '#16a34a' : (party === 'p1' ? 'rgba(255,255,255,0.25)' : '#e2e8f0');
    p1Badge.style.color = p1Signed ? '#ffffff' : (party === 'p1' ? '#ffffff' : '#475569');
  }
  if (p2Badge) {
    p2Badge.innerHTML = p2Signed
      ? `<i class="fa-solid fa-check"></i> ${isEn ? 'Signed' : 'স্বাক্ষরিত'}`
      : (isEn ? 'Pending Signature' : 'স্বাক্ষর বাকি');
    p2Badge.style.background = p2Signed ? '#16a34a' : (party === 'p2' ? 'rgba(255,255,255,0.25)' : '#e2e8f0');
    p2Badge.style.color = p2Signed ? '#ffffff' : (party === 'p2' ? '#ffffff' : '#475569');
  }

  if (party === 'p1') {
    if (targetP1) targetP1.className = 'btn btn-primary';
    if (targetP2) targetP2.className = 'btn btn-secondary';
    if (signerNameEl) signerNameEl.textContent = labels.p1;
    if (p1Signed && existingBox && existingImg) {
      existingBox.style.display = 'flex';
      existingImg.src = state.formData.party1_signature;
    } else if (existingBox) {
      existingBox.style.display = 'none';
    }
  } else {
    if (targetP2) targetP2.className = 'btn btn-primary';
    if (targetP1) targetP1.className = 'btn btn-secondary';
    if (signerNameEl) signerNameEl.textContent = labels.p2;
    if (p2Signed && existingBox && existingImg) {
      existingBox.style.display = 'flex';
      existingImg.src = state.formData.party2_signature;
    } else if (existingBox) {
      existingBox.style.display = 'none';
    }
  }

  const canvas = document.getElementById('sig-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

function openSignModal(targetParty = null) {
  const labels = getPartyLabels();
  const labelP1 = document.getElementById('label-p1-btn');
  const labelP2 = document.getElementById('label-p2-btn');
  if (labelP1) labelP1.textContent = labels.p1;
  if (labelP2) labelP2.textContent = labels.p2;

  let chosen = targetParty;
  if (!chosen) {
    if (state.formData.party1_signature && !state.formData.party2_signature) {
      chosen = 'p2';
    } else {
      chosen = 'p1';
    }
  }

  selectSignParty(chosen);
  document.getElementById('sign-modal').style.display = 'flex';
}

function attachSignatureBoxClicks() {
  document.querySelectorAll('#preview-container .sig-col').forEach(col => {
    col.addEventListener('click', () => {
      const target = col.getAttribute('data-target-sign') || 'p1';
      openSignModal(target);
    });
  });
}

function initSignatureCanvas() {
  const canvas = document.getElementById('sig-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.strokeStyle = '#0f172a';
  ctx.lineWidth = 2.5;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches && e.touches.length > 0 ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches && e.touches.length > 0 ? e.touches[0].clientY : e.clientY;
    return {
      x: (clientX - rect.left) * (canvas.width / rect.width),
      y: (clientY - rect.top) * (canvas.height / rect.height)
    };
  }

  function startDraw(e) {
    state.isDrawing = true;
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
  }

  function draw(e) {
    if (!state.isDrawing) return;
    const pos = getPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
  }

  function stopDraw() {
    state.isDrawing = false;
  }

  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('mousemove', draw);
  window.addEventListener('mouseup', stopDraw);

  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startDraw(e);
  }, { passive: false });

  canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    draw(e);
  }, { passive: false });

  window.addEventListener('touchend', () => {
    stopDraw();
  });

  document.getElementById('btn-clear-canvas').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  });

  const targetP1 = document.getElementById('sign-target-p1');
  const targetP2 = document.getElementById('sign-target-p2');
  if (targetP1) targetP1.addEventListener('click', () => { selectSignParty('p1'); });
  if (targetP2) targetP2.addEventListener('click', () => { selectSignParty('p2'); });

  const btnRemoveSig = document.getElementById('btn-remove-sig');
  if (btnRemoveSig) {
    btnRemoveSig.addEventListener('click', () => {
      if (state.sigTarget === 'p1') {
        delete state.formData.party1_signature;
      } else {
        delete state.formData.party2_signature;
      }
      selectSignParty(state.sigTarget);
      triggerDocumentRender();
    });
  }

  document.getElementById('btn-apply-signature').addEventListener('click', async () => {
    // Check if user drew on canvas
    const pixelBuffer = new Uint32Array(
      ctx.getImageData(0, 0, canvas.width, canvas.height).data.buffer
    );
    const hasDrawn = pixelBuffer.some(color => color !== 0);

    if (hasDrawn) {
      const dataUrl = canvas.toDataURL('image/png');
      if (state.sigTarget === 'p1') {
        state.formData.party1_signature = dataUrl;
      } else {
        state.formData.party2_signature = dataUrl;
      }

      // If in remote signing mode or has contract ID, submit back to server
      if (state.currentContractId) {
        try {
          await fetch(`/api/contracts/share/${state.currentContractId}/sign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              signature_data: dataUrl,
              target: state.sigTarget === 'p1' ? 'party1' : 'party2'
            })
          });
        } catch (e) {
          console.error('Remote signature error:', e);
        }
      }
    }

    await triggerDocumentRender();
    document.getElementById('sign-modal').style.display = 'none';
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Scroll directly to the signature block on the preview document
    setTimeout(() => {
      const sigSec = document.querySelector('.signatures-section');
      if (sigSec) {
        sigSec.scrollIntoView({ behavior: 'smooth', block: 'center' });
        sigSec.style.transition = 'background 0.4s';
        sigSec.style.background = '#f0fdf4';
        setTimeout(() => { sigSec.style.background = 'transparent'; }, 1200);
      }
    }, 250);
  });
}

// Database History Modal (Private Vault Isolated)
async function openHistoryModal() {
  const isEn = state.currentLang === 'en';
  const modal = document.getElementById('history-modal');
  const container = document.getElementById('history-list-container');
  modal.style.display = 'flex';
  
  const vaultId = getVaultSessionId();
  container.innerHTML = `<p style="text-align: center; color: #0284c7; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Loading vault contents...' : 'ভল্ট লোড হচ্ছে...'}</p>`;

  try {
    const res = await fetch('/api/contracts', {
      headers: { 'X-Session-ID': vaultId }
    });
    const list = await res.json();

    const vaultBanner = `
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #334155;">
          <i class="fa-solid fa-vault" style="color: #0f172a; font-size: 0.95rem;"></i>
          <span>${isEn ? 'Your Personal Secure Vault:' : 'আপনার ব্যক্তিগত ভল্ট:'}</span>
          <code style="background: #e2e8f0; padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #0f172a; font-size: 0.8rem;">${vaultId}</code>
        </div>
        <button id="btn-copy-vault" style="background: white; border: 1px solid #cbd5e1; border-radius: 5px; padding: 4px 10px; cursor: pointer; color: #0f172a; font-size: 0.78rem; font-weight: 600; display: flex; align-items: center; gap: 4px;" onclick="copyVaultId()">
          <i class="fa-regular fa-copy"></i> ${isEn ? 'Copy Key' : 'কপি কি'}
        </button>
      </div>
    `;

    if (!Array.isArray(list) || list.length === 0) {
      container.innerHTML = vaultBanner + `<p style="text-align: center; color: #64748b; padding: 25px;">${isEn ? 'No agreements saved in your vault yet. Click <strong>"Save Draft"</strong> in the left editor panel to store your drafts.' : 'আপনার ভল্টে এখনো কোনো চুক্তি সংরক্ষিত নেই। বাম পাশের এডিটর থেকে <strong>"খসড়া সেভ করুন"</strong> বাটনে ক্লিক করে সেভ করুন।'}</p>`;
      return;
    }

    container.innerHTML = vaultBanner + list.map(item => `
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h4 style="color: #0f172a; font-size: 0.95rem; margin-bottom: 4px;">${item.title}</h4>
          <span style="font-size: 0.8rem; color: #64748b;">
            <i class="fa-regular fa-clock"></i> ${item.updated_at} | <strong>${item.document_type}</strong>
          </span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-primary" style="padding: 4px 10px; font-size: 0.8rem;" onclick="loadContractById('${item.id}', '${item.document_type}')">
            <i class="fa-solid fa-folder-open"></i> ${isEn ? 'Load' : 'লোড'}
          </button>
          <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.8rem; color: #ef4444;" onclick="deleteContractById('${item.id}')">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<p style="color: #ef4444;">${isEn ? 'Failed to load vault history.' : 'হিস্ট্রি লোড করতে ব্যর্থ হয়েছে।'}</p>`;
  }
}

window.copyVaultId = function() {
  const isEn = state.currentLang === 'en';
  const vid = getVaultSessionId();
  const markCopied = () => {
    const btn = document.getElementById('btn-copy-vault');
    if (btn) {
      btn.innerHTML = `<i class="fa-solid fa-check" style="color: #10b981;"></i> ${isEn ? 'Copied!' : 'কপি হয়েছে!'}`;
      setTimeout(() => {
        btn.innerHTML = `<i class="fa-regular fa-copy"></i> ${isEn ? 'Copy Key' : 'কপি কি'}`;
      }, 2000);
    }
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(vid).then(markCopied).catch(() => {
      prompt(isEn ? 'Your Vault Key:' : 'আপনার ভল্ট কি:', vid);
    });
  } else {
    prompt(isEn ? 'Your Vault Key:' : 'আপনার ভল্ট কি:', vid);
  }
};

window.loadContractById = async function(id, docType) {
  const isEn = state.currentLang === 'en';
  try {
    const res = await fetch(`/api/contracts/${id}`, {
      headers: { 'X-Session-ID': getVaultSessionId() }
    });
    const item = await res.json();
    state.currentContractId = item.id;
    if (item.language) {
      state.currentLang = item.language;
      const langSelect = document.getElementById('lang-select');
      if (langSelect) langSelect.value = item.language;
      applyLanguage(item.language);
    }
    document.getElementById('template-select').value = item.document_type;
    setupTemplate(item.document_type, item.data);
    document.getElementById('history-modal').style.display = 'none';
  } catch (err) {
    alert(isEn ? ('Failed to load agreement: ' + err.message) : ('চুক্তি লোড করতে ব্যর্থ হয়েছে: ' + err.message));
  }
};

window.deleteContractById = async function(id) {
  const isEn = state.currentLang === 'en';
  const confirmMsg = isEn ? 'Are you sure you want to delete this agreement permanently?' : 'আপনি কি নিশ্চিত এই চুক্তিটি মুছে ফেলতে চান?';
  if (!confirm(confirmMsg)) return;
  try {
    await fetch(`/api/contracts/${id}`, {
      method: 'DELETE',
      headers: { 'X-Session-ID': getVaultSessionId() }
    });
    openHistoryModal();
  } catch (err) {
    alert(isEn ? ('Failed to delete: ' + err.message) : ('মুছতে ব্যর্থ হয়েছে: ' + err.message));
  }
};

async function openClauseExplainer(clauseText) {
  const isEn = state.currentLang === 'en';
  const modal = document.getElementById('explainer-modal');
  const content = document.getElementById('explainer-content');
  modal.style.display = 'flex';
  content.innerHTML = `<p style="text-align: center; color: #6366f1; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'AI Legal Analysis in progress...' : 'AI বিশ্লেষণ চলছে...'}</p>`;

  try {
    const res = await fetch('/api/ai/explain-clause', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clause_text: clauseText, language: state.currentLang })
    });
    const data = await res.json();
    content.innerHTML = `
      <div style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 12px; margin-bottom: 16px; border-radius: 0 8px 8px 0;">
        <h4 style="color: #1e3a8a; margin-bottom: 6px; font-size: 0.95rem;">${isEn ? 'Plain English Summary:' : 'সহজ সারসংক্ষেপ:'}</h4>
        <p style="font-size: 0.92rem; color: #1e293b; line-height: 1.6;">${data.simple_explanation}</p>
      </div>
      <div style="margin-bottom: 16px;">
        <h4 style="color: #0f172a; margin-bottom: 8px; font-size: 0.9rem;"><i class="fa-solid fa-circle-check" style="color: #10b981;"></i> ${isEn ? 'Key Obligations:' : 'মূল দায়িত্ব:'}</h4>
        <ul style="padding-left: 20px; font-size: 0.88rem; color: #334155;">
          ${data.key_obligations.map(o => `<li style="margin-bottom: 4px;">${o}</li>`).join('')}
        </ul>
      </div>
      <div>
        <h4 style="color: #b91c1c; margin-bottom: 8px; font-size: 0.9rem;"><i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i> ${isEn ? 'Potential Legal Risks:' : 'সম্ভাব্য ঝুঁকি:'}</h4>
        <ul style="padding-left: 20px; font-size: 0.88rem; color: #7f1d1d;">
          ${data.potential_risks.map(r => `<li style="margin-bottom: 4px;">${r}</li>`).join('')}
        </ul>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<p style="color: #ef4444;">${isEn ? 'Failed to load AI explanation.' : 'AI ব্যাখ্যা লোড করতে ব্যর্থ হয়েছে।'}</p>`;
  }
}

window.goToStep = function(stepNum) {
  document.querySelectorAll('.step-tab').forEach(t => {
    if (t.getAttribute('data-step') == stepNum) {
      t.classList.add('active');
    } else {
      t.classList.remove('active');
    }
  });
  document.querySelectorAll('.step-content').forEach(c => c.style.display = 'none');
  const targetStep = document.getElementById(`step-${stepNum}`);
  if (targetStep) targetStep.style.display = 'block';

  // Smart preview sync: auto-scroll preview panel to relevant document section
  const previewPanel = document.querySelector('.preview-panel');
  if (previewPanel) {
    if (stepNum == 1) {
      previewPanel.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (stepNum == 2) {
      const target = document.querySelector('.clauses-container') || document.querySelector('.highlight-box');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (stepNum == 3) {
      const target = document.querySelector('.clauses-container');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (stepNum == 4) {
      const sigTarget = document.querySelector('.signatures-section') || document.querySelector('.witness-section');
      if (sigTarget) {
        sigTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        previewPanel.scrollTo({ top: previewPanel.scrollHeight, behavior: 'smooth' });
      }
    }
  }
};

function attachEvents() {
  document.querySelectorAll('.step-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const stepNum = tab.getAttribute('data-step');
      window.goToStep(stepNum);
    });
  });

  document.getElementById('template-select').addEventListener('change', (e) => {
    state.currentContractId = null;
    setupTemplate(e.target.value);
  });

  document.getElementById('lang-select').addEventListener('change', (e) => {
    const oldLang = state.currentLang;
    const newLang = e.target.value;
    if (oldLang === newLang) return;
    state.currentLang = newLang;
    applyLanguage(newLang);

    // Swap defaults if form data hasn't been heavily customized by user
    const currentMeta = state.templates.find(t => t.id === state.currentTemplate);
    if (currentMeta) {
      const oldDefaults = oldLang === 'en'
        ? (currentMeta.defaults_en || currentMeta.defaults)
        : (currentMeta.defaults_bn || currentMeta.defaults);
      const newDefaults = newLang === 'en'
        ? (currentMeta.defaults_en || currentMeta.defaults)
        : (currentMeta.defaults_bn || currentMeta.defaults);

      let isDefault = true;
      for (const k of Object.keys(oldDefaults || {})) {
        if (state.formData[k] && state.formData[k] !== oldDefaults[k]) {
          isDefault = false;
          break;
        }
      }
      if (isDefault && newDefaults) {
        const p1Sig = state.formData.party1_signature;
        const p2Sig = state.formData.party2_signature;
        state.formData = JSON.parse(JSON.stringify(newDefaults));
        if (p1Sig) state.formData.party1_signature = p1Sig;
        if (p2Sig) state.formData.party2_signature = p2Sig;
        state.customClauses = state.formData.custom_clauses || [];
      }
    }

    renderFormFields();
    renderCustomClausesList();
    triggerDocumentRender();
  });

  // Direct Edit Mode
  const btnToggleEdit = document.getElementById('btn-toggle-edit');
  const previewContainer = document.getElementById('preview-container');
  const editLabel = document.getElementById('edit-mode-label');

  btnToggleEdit.addEventListener('click', () => {
    const isEn = state.currentLang === 'en';
    state.isDirectEdit = !state.isDirectEdit;
    previewContainer.contentEditable = state.isDirectEdit ? 'true' : 'false';
    if (state.isDirectEdit) {
      previewContainer.style.outline = '2px dashed #2563eb';
      btnToggleEdit.style.background = '#dbeafe';
      btnToggleEdit.style.color = '#1d4ed8';
      editLabel.innerText = isEn ? '✅ Edit Mode Active' : '✅ এডিট মোড চলছে';
    } else {
      previewContainer.style.outline = 'none';
      btnToggleEdit.style.background = '';
      btnToggleEdit.style.color = '';
      editLabel.innerText = isEn ? 'Direct Paper Edit' : 'সরাসরি পেপারে এডিট';
      updatePageGuideAndCount();
      refreshDocumentHash();
    }
  });

  previewContainer.addEventListener('input', () => {
    if (state.isDirectEdit) {
      updatePageGuideAndCount();
      refreshDocumentHash();
    }
  });

  // Toggle 300 Tk Stamp
  document.getElementById('btn-toggle-stamp').addEventListener('click', () => {
    state.showStamp = !state.showStamp;
    const stamp = document.getElementById('stamp-header');
    if (stamp) {
      stamp.style.display = state.showStamp ? 'flex' : 'none';
    }
    updatePageGuideAndCount();
    refreshDocumentHash();
  });

  // Stamp Duty Calculator Modal
  document.getElementById('btn-open-stamp-calc').addEventListener('click', () => {
    document.getElementById('stamp-calc-modal').style.display = 'flex';
  });

  document.getElementById('btn-run-stamp-calc').addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    const docType = document.getElementById('calc-doc-type').value;
    const amount = parseFloat(document.getElementById('calc-amount').value) || 0;
    const duration = parseInt(document.getElementById('calc-duration').value) || 12;

    try {
      const res = await fetch('/api/tools/stamp-calculator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doc_type: docType,
          rent_amount: amount,
          duration_months: duration,
          total_capital: amount
        })
      });
      const data = await res.json();
      const resEl = document.getElementById('stamp-calc-result');
      resEl.style.display = 'block';
      resEl.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <strong style="color:#9a3412;">${isEn ? 'Required Non-Judicial Stamp Duty:' : 'প্রয়োজনীয় স্ট্যাম্প ডিউটি:'}</strong>
          <span style="font-size:1.3rem; font-weight:800; color:#c2410c;">${data.formatted_stamp}</span>
        </div>
        <p style="font-size:0.86rem; color:#7c2d12; margin-bottom:6px;">${data.explanation}</p>
        <span style="font-size:0.8rem; color:#64748b;"><strong>${isEn ? 'Legal Reference:' : 'আইনি রেফারেন্স:'}</strong> ${data.legal_basis}</span>
        ${data.is_registration_mandatory ? `<div style="margin-top:8px; padding:6px 8px; background:#fee2e2; color:#991b1b; border-radius:4px; font-size:0.8rem; font-weight:bold;">${isEn ? '⚠️ Registration at Sub-Registry Office is mandatory for tenancy exceeding 1 year.' : '⚠️ ১ বছরের অধিক হওয়ায় সাব-রেজিস্ট্রি অফিসে রেজিস্ট্রেশন বাধ্যতামূলক।'}</div>` : ''}
      `;
    } catch (e) {
      alert(isEn ? 'Failed to calculate stamp duty.' : 'স্ট্যাম্প হিসাব করতে ব্যর্থ হয়েছে।');
    }
  });

  // Share & Remote Signing Modal
  document.getElementById('btn-share-contract').addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    const btn = document.getElementById('btn-share-contract');
    const origHtml = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Creating share link...' : 'শেয়ার লিংক তৈরি হচ্ছে...'}`;
    btn.disabled = true;

    try {
      state.formData.custom_clauses = state.customClauses;
      const currentMeta = state.templates.find(t => t.id === state.currentTemplate);
      const title = `${currentMeta ? (state.currentLang === 'bn' ? currentMeta.title_bn : currentMeta.title_en) : (isEn ? 'Agreement' : 'চুক্তিপত্র')} - ${new Date().toLocaleDateString(isEn ? 'en-US' : 'bn-BD')}`;
      const vaultId = getVaultSessionId();

      const res = await fetch('/api/contracts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': vaultId
        },
        body: JSON.stringify({
          id: state.currentContractId || null,
          owner_id: vaultId,
          title: title,
          document_type: state.currentTemplate,
          language: state.currentLang,
          data: state.formData
        })
      });

      if (!res.ok) {
        throw new Error(isEn ? 'Failed to save agreement on server' : 'সার্ভারে চুক্তি সংরক্ষণ ব্যর্থ হয়েছে');
      }

      const resData = await res.json();
      state.currentContractId = resData.id;

      const shareUrl = `${window.location.origin}/?share_id=${state.currentContractId}`;
      document.getElementById('share-url-input').value = shareUrl;
      const inviteMsg = isEn
        ? `Invitation to sign legal agreement via SmartLegal AI: ${shareUrl}`
        : `SmartLegal AI এর মাধ্যমে আপনার চুক্তিপত্রে স্বাক্ষরের আমন্ত্রণ: ${shareUrl}`;
      document.getElementById('btn-whatsapp-share').href = `https://api.whatsapp.com/send?text=${encodeURIComponent(inviteMsg)}`;
      document.getElementById('share-modal').style.display = 'flex';
    } catch (err) {
      alert(isEn ? ('Share link creation failed: ' + err.message) : ('শেয়ার লিংক তৈরি করতে সমস্যা হয়েছে: ' + err.message));
    } finally {
      btn.innerHTML = origHtml;
      btn.disabled = false;
    }
  });

  document.getElementById('btn-copy-share-url').addEventListener('click', () => {
    const isEn = state.currentLang === 'en';
    const input = document.getElementById('share-url-input');
    input.select();
    input.setSelectionRange(0, 99999);
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(input.value);
      } else {
        document.execCommand('copy');
      }
    } catch (_) {
      document.execCommand('copy');
    }
    const btn = document.getElementById('btn-copy-share-url');
    btn.innerHTML = `<i class="fa-solid fa-check"></i> ${isEn ? 'Copied!' : 'কপিড!'}`;
    setTimeout(() => { btn.innerHTML = `<i class="fa-solid fa-copy"></i> ${isEn ? 'Copy' : 'কপি'}`; }, 1500);
  });

  // Floating Chatbot Interactions
  const fab = document.getElementById('fab-chatbot');
  const chatWindow = document.getElementById('chatbot-window');
  const closeChat = document.getElementById('close-chatbot');
  const chatInput = document.getElementById('chat-input');
  const chatSend = document.getElementById('btn-chat-send');
  const chatBody = document.getElementById('chat-body');

  fab.addEventListener('click', () => {
    chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
  });
  closeChat.addEventListener('click', () => {
    chatWindow.style.display = 'none';
  });

  const sendChatMessage = async () => {
    const isEn = state.currentLang === 'en';
    const q = chatInput.value.trim();
    if (!q) return;

    chatBody.innerHTML += `<div class="chat-bubble-user">${q}</div>`;
    chatInput.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    const loaderId = 'loader_' + Date.now();
    chatBody.innerHTML += `<div class="chat-bubble-ai" id="${loaderId}"><i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'AI Assistant is thinking...' : 'আইনAI লিখছে...'}</div>`;
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
      const res = await fetch('/api/ai/legal-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, contract_context: state.currentTemplate })
      });
      const data = await res.json();
      const loader = document.getElementById(loaderId);
      if (loader) {
        loader.innerHTML = data.answer.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      }
      chatBody.scrollTop = chatBody.scrollHeight;
    } catch (e) {
      const loader = document.getElementById(loaderId);
      if (loader) loader.innerHTML = isEn ? 'Unable to retrieve answer. Please try again.' : 'উত্তর পেতে সমস্যা হয়েছে।';
    }
  };

  chatSend.addEventListener('click', sendChatMessage);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChatMessage();
  });

  // History & Sign buttons
  document.getElementById('btn-history').addEventListener('click', openHistoryModal);
  document.getElementById('btn-open-sign').addEventListener('click', () => openSignModal());
  const step4SignBtn = document.getElementById('btn-step4-sign');
  if (step4SignBtn) step4SignBtn.addEventListener('click', () => openSignModal());

  // Upload Audit
  document.getElementById('btn-upload-audit').addEventListener('click', () => {
    document.getElementById('upload-modal').style.display = 'flex';
  });

  const uploadFileInput = document.getElementById('upload-file-input');
  const uploadTextInput = document.getElementById('upload-text-input');
  const uploadStatus = document.getElementById('upload-file-status');
  const btnRunAudit = document.getElementById('btn-run-upload-audit');

  uploadFileInput.addEventListener('change', async (e) => {
    const isEn = state.currentLang === 'en';
    const file = e.target.files[0];
    if (!file) return;

    state.uploadedFileName = file.name;
    const ext = file.name.split('.').pop().toLowerCase();

    // Plain text files can be read directly in the browser
    if (ext === 'txt' || ext === 'md') {
      const reader = new FileReader();
      reader.onload = (evt) => {
        uploadTextInput.value = evt.target.result;
        uploadTextInput.disabled = false;
        btnRunAudit.disabled = false;
        uploadStatus.style.display = 'block';
        uploadStatus.style.background = '#f0fdf4';
        uploadStatus.style.color = '#166534';
        uploadStatus.style.border = '1px solid #bbf7d0';
        uploadStatus.innerHTML = isEn
          ? `<i class="fa-solid fa-circle-check"></i> <strong>${file.name}</strong> loaded successfully (${uploadTextInput.value.length} characters).`
          : `<i class="fa-solid fa-circle-check"></i> <strong>${file.name}</strong> টেক্সট ফাইল লোড সম্পন্ন হয়েছে (${uploadTextInput.value.length} অক্ষর)।`;
      };
      reader.readAsText(file);
      return;
    }

    // Binary documents (PDF, DOCX, DOC) must be extracted cleanly via backend
    uploadStatus.style.display = 'block';
    uploadStatus.style.background = '#eff6ff';
    uploadStatus.style.color = '#1e40af';
    uploadStatus.style.border = '1px solid #bfdbfe';
    uploadStatus.innerHTML = isEn
      ? `<i class="fa-solid fa-spinner fa-spin"></i> Extracting text from <strong>${file.name}</strong>... Please wait...`
      : `<i class="fa-solid fa-spinner fa-spin"></i> <strong>${file.name}</strong> ফাইল থেকে টেক্সট এক্সট্র্যাক্ট করা হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন...`;
    uploadTextInput.value = isEn
      ? `[Extracting text: ${file.name}...\nPlease wait...]`
      : `[ফাইল বিশ্লেষণ চলছে: ${file.name}...\nঅনুগ্রহ করে অপেক্ষা করুন...]`;
    uploadTextInput.disabled = true;
    btnRunAudit.disabled = true;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/api/tools/extract-file-text', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || (isEn ? 'Failed to extract text from file.' : 'ফাইল থেকে টেক্সট এক্সট্র্যাক্ট করা সম্ভব হয়নি।'));
      }

      uploadTextInput.value = data.extracted_text;
      uploadTextInput.disabled = false;
      btnRunAudit.disabled = false;

      uploadStatus.style.display = 'block';
      uploadStatus.style.background = '#f0fdf4';
      uploadStatus.style.color = '#166534';
      uploadStatus.style.border = '1px solid #bbf7d0';
      uploadStatus.innerHTML = isEn
        ? `<i class="fa-solid fa-circle-check"></i> Successfully extracted ${data.character_count.toLocaleString()} characters from <strong>${data.filename}</strong> (${data.detected_format.toUpperCase()})!`
        : `<i class="fa-solid fa-circle-check"></i> <strong>${data.filename}</strong> (${data.detected_format.toUpperCase()}) থেকে ${data.character_count.toLocaleString('bn-BD')} টি অক্ষর সফলভাবে এক্সট্র্যাক্ট করা হয়েছে!`;
    } catch (err) {
      console.error('File extraction error:', err);
      uploadTextInput.value = '';
      uploadTextInput.disabled = false;
      btnRunAudit.disabled = false;

      uploadStatus.style.display = 'block';
      uploadStatus.style.background = '#fef2f2';
      uploadStatus.style.color = '#991b1b';
      uploadStatus.style.border = '1px solid #fecaca';
      uploadStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${err.message || (isEn ? 'File extraction failed. Please paste text directly.' : 'ফাইল প্রসেস করতে ব্যর্থ হয়েছে। সরাসরি টেক্সট কপি করে পেস্ট করুন।')}`;
    }
  });

  btnRunAudit.addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    const text = uploadTextInput.value.trim();
    if (!text || text.startsWith('[') && text.includes('...')) {
      return alert(isEn ? 'Please provide valid text or upload an agreement file first.' : 'অনুগ্রহ করে বৈধ টেক্সট বা ফাইল প্রদান করুন।');
    }

    const oldText = btnRunAudit.innerHTML;
    btnRunAudit.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Running Deep AI Audit...' : 'AI গভীর অডিট বিশ্লেষণ চলছে...'}`;
    btnRunAudit.disabled = true;

    try {
      const filename = state.uploadedFileName || 'Uploaded_Document.docx';
      const res = await fetch('/api/ai/audit-upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: text, filename: filename })
      });
      if (!res.ok) throw new Error(isEn ? 'Audit request failed on server.' : 'সার্ভারে অডিট রিকোয়েস্ট ব্যর্থ হয়েছে।');
      const data = await res.json();
      const resContainer = document.getElementById('upload-audit-result');
      resContainer.style.display = 'block';

      const risksHtml = (data.risks_found && data.risks_found.length > 0)
        ? data.risks_found.map(r => `
          <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px; border-radius: 0 6px 6px 0; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <strong style="font-size: 0.85rem; color: #991b1b;">${r.clause_topic || (isEn ? 'Risky Clause' : 'ঝুঁকিপূর্ণ ধারা')}</strong>
              <span class="badge ${r.severity === 'high' ? 'badge-high' : (r.severity === 'medium' ? 'badge-medium' : 'badge-low')}">
                ${r.severity === 'high' ? (isEn ? 'High Risk' : 'উচ্চ ঝুঁকি') : (r.severity === 'medium' ? (isEn ? 'Medium Risk' : 'মাঝারি ঝুঁকি') : (isEn ? 'Low Risk' : 'সাধারণ সতর্কতা'))}
              </span>
            </div>
            <p style="font-size: 0.82rem; color: #7f1d1d; margin: 4px 0;">${r.issue}</p>
            <div style="font-size: 0.8rem; color: #1e40af; background: #eff6ff; padding: 6px 8px; border-radius: 4px; margin-top: 4px;">
              <strong>${isEn ? 'Recommendation:' : 'পরামর্শ:'}</strong> ${r.recommendation}
            </div>
          </div>
        `).join('')
        : `<p style="font-size: 0.82rem; color: #166534;">${isEn ? 'No critical risks detected.' : 'কোনো উচ্চ ঝুঁকি পাওয়া যায়নি।'}</p>`;

      const missingHtml = (data.missing_clauses && data.missing_clauses.length > 0)
        ? `
          <h4 style="font-size: 0.88rem; color: #b45309; margin: 12px 0 6px 0; display: flex; align-items: center; gap: 6px;">
            <i class="fa-solid fa-triangle-exclamation"></i> ${isEn ? 'Missing Essential Safeguard Clauses:' : 'মিসিং বা অনুপস্থিত আবশ্যকীয় সুরক্ষাধারা:'}
          </h4>
          <ul style="padding-left: 20px; font-size: 0.82rem; color: #92400e; margin: 0 0 10px 0;">
            ${data.missing_clauses.map(m => `<li style="margin-bottom: 4px;">${m}</li>`).join('')}
          </ul>
        `
        : '';

      resContainer.innerHTML = `
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
            <strong style="color: #1e3a8a; font-size: 0.95rem;">
              <i class="fa-solid fa-scale-balanced"></i> ${data.detected_type || (isEn ? 'Detected Agreement' : 'শনাক্তকৃত চুক্তিপত্র')}
            </strong>
            <span class="badge ${data.score >= 80 ? 'badge-low' : (data.score >= 60 ? 'badge-medium' : 'badge-high')}">
              ${isEn ? 'Safety Score:' : 'নিরাপত্তা স্কোর:'} ${data.score}/100
            </span>
          </div>
          <p style="font-size: 0.88rem; color: #334155; line-height: 1.5; margin: 0;">${data.summary}</p>
        </div>
        <h4 style="font-size: 0.9rem; color: #0f172a; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-shield-halved" style="color: #ef4444;"></i> ${isEn ? 'Identified Risk Clauses:' : 'চিহ্নিত ঝুঁকিপূর্ণ শর্তসমূহ:'}
        </h4>
        ${risksHtml}
        ${missingHtml}
      `;
    } catch (err) {
      alert(isEn ? 'Audit analysis encountered an error. Please try again.' : 'অডিট করতে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।');
    } finally {
      btnRunAudit.innerHTML = oldText;
      btnRunAudit.disabled = false;
    }
  });

  // Save Contract to SQLite Database
  document.getElementById('btn-save-draft').addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    state.formData.custom_clauses = state.customClauses;
    const currentMeta = state.templates.find(t => t.id === state.currentTemplate);
    const title = `${currentMeta ? (state.currentLang === 'bn' ? currentMeta.title_bn : currentMeta.title_en) : (isEn ? 'Agreement' : 'চুক্তিপত্র')} - ${new Date().toLocaleDateString(isEn ? 'en-US' : 'bn-BD')}`;

    try {
      const vaultId = getVaultSessionId();
      const res = await fetch('/api/contracts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': vaultId
        },
        body: JSON.stringify({
          id: state.currentContractId,
          owner_id: vaultId,
          title: title,
          document_type: state.currentTemplate,
          language: state.currentLang,
          data: state.formData
        })
      });
      const data = await res.json();
      state.currentContractId = data.id;

      const btn = document.getElementById('btn-save-draft');
      const oldText = btn.innerHTML;
      btn.innerHTML = `<i class="fa-solid fa-check" style="color: #10b981;"></i> ${isEn ? 'Saved!' : 'সেভ হয়েছে!'}`;
      setTimeout(() => { btn.innerHTML = oldText; }, 2000);
    } catch (err) {
      alert(isEn ? 'Failed to save to database.' : 'ডাটাবেসে সেভ করতে সমস্যা হয়েছে।');
    }
  });

  // AI Refine Clause Button
  document.getElementById('btn-refine-clause').addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    const rawInput = document.getElementById('ai-clause-input').value.trim();
    if (!rawInput) return alert(isEn ? 'Please describe your custom clause first.' : 'অনুগ্রহ করে শর্তটি লিখুন।');

    const btn = document.getElementById('btn-refine-clause');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'AI Polishing...' : 'AI পলিশ করছে...'}`;
    btn.disabled = true;

    try {
      const res = await fetch('/api/ai/refine-clause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: rawInput,
          document_type: state.currentTemplate,
          language: state.currentLang
        })
      });

      if (res.ok) {
        const data = await res.json();
        state.lastRefinedClause = data;
        document.getElementById('ai-res-title').innerText = data.title || (isEn ? 'Custom Clause' : 'বিশেষ ধারা');
        document.getElementById('ai-res-risk').innerText = (data.risk_level || 'Low') + ' Risk';
        document.getElementById('ai-res-text').innerText = data.refined_clause;
        document.getElementById('ai-clause-result').style.display = 'block';
      }
    } catch (err) {
      alert(isEn ? 'AI clause refinement failed.' : 'AI রূপান্তর করতে ব্যর্থ হয়েছে।');
    } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  });

  document.getElementById('btn-add-clause').addEventListener('click', () => {
    if (state.lastRefinedClause) {
      state.customClauses.push({
        title: state.lastRefinedClause.title,
        text: state.lastRefinedClause.refined_clause
      });
      renderCustomClausesList();
      triggerDocumentRender();
      document.getElementById('ai-clause-result').style.display = 'none';
      document.getElementById('ai-clause-input').value = '';
    }
  });

  document.getElementById('btn-explain-clause-action').addEventListener('click', () => {
    if (state.lastRefinedClause) {
      openClauseExplainer(state.lastRefinedClause.refined_clause);
    }
  });

  // Universal Modal Closers (all 8 modals)
  const allModals = [
    'explainer-modal', 'sign-modal', 'history-modal', 'upload-modal',
    'stamp-calc-modal', 'share-modal', 'notice-modal', 'verify-modal'
  ];
  const closeAllModals = () => {
    allModals.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
  };

  allModals.forEach(id => {
    const modalEl = document.getElementById(id);
    if (modalEl) {
      modalEl.addEventListener('click', (e) => {
        if (e.target.id === id) modalEl.style.display = 'none';
      });
    }
  });

  ['close-explainer', 'btn-close-explainer-footer', 'close-sign', 'btn-close-sign-footer',
   'close-history', 'btn-close-history-footer', 'close-upload', 'btn-close-upload-footer',
   'close-stamp-calc', 'btn-close-stamp-calc-footer', 'close-share', 'btn-close-share-footer',
   'close-notice', 'btn-close-notice-footer', 'close-verify', 'btn-close-verify-footer'].forEach(btnId => {
    const btn = document.getElementById(btnId);
    if (btn) btn.addEventListener('click', closeAllModals);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAllModals();
  });

  // Instant Client-Side Print & Vector PDF Export (0ms server load)
  const btnPrintInstant = document.getElementById('btn-print-instant');
  if (btnPrintInstant) {
    btnPrintInstant.addEventListener('click', () => {
      applyWatermarkToPreview();
      refreshDocumentHash();
      window.print();
    });
  }

  // Server-Side Headless Chrome PDF Export
  document.getElementById('btn-pdf').addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    const btn = document.getElementById('btn-pdf');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Generating Server PDF...' : 'সার্ভার PDF তৈরি হচ্ছে...'}`;
    btn.disabled = true;

    // Helpful progressive feedback if cloud server is waking from sleep
    const wakeTimer = setTimeout(() => {
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Server preparing (cloud instance waking)...' : 'সার্ভার প্রস্তুত হচ্ছে (ক্লাউড চালু হচ্ছে)...'}`;
    }, 3500);

    try {
      const res = await fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: state.currentTemplate,
          language: state.currentLang,
          data: state.formData
        })
      });

      clearTimeout(wakeTimer);

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${state.currentTemplate}_verified.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);
      } else {
        let errMsg = isEn ? 'Cloud server PDF generation delayed.' : 'ক্লাউড সার্ভার PDF বিলম্বিত হয়েছে।';
        try {
          const errData = await res.json();
          if (errData && errData.detail) {
            errMsg = `${isEn ? 'Cloud server notice' : 'ক্লাউড সার্ভার বার্তা'}: ${errData.detail}`;
          }
        } catch (_) {}
        const fallbackPrompt = isEn
          ? `${errMsg}\n\nWould you like to use instant browser PDF download instead?`
          : `${errMsg}\n\nআপনি কি তাত্ক্ষণিক ব্রাউজার PDF ডাউনলোড (০ সেকেন্ডে সরাসরি সেভ) ব্যবহার করতে চান?`;
        if (confirm(fallbackPrompt)) {
          window.print();
        }
      }
    } catch (err) {
      clearTimeout(wakeTimer);
      const connPrompt = isEn
        ? `Cloud server connection delayed (${err.message}).\n\nWould you like to use instant browser PDF download instead?`
        : `ক্লাউড সার্ভার সংযোগে বিলম্ব হচ্ছে (${err.message})।\n\nআপনি কি তাত্ক্ষণিক ব্রাউজার PDF ডাউনলোড (০ সেকেন্ডে সরাসরি সেভ) ব্যবহার করতে চান?`;
      if (confirm(connPrompt)) {
        window.print();
      }
    } finally {
      clearTimeout(wakeTimer);
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  });

  // Word DOCX Export
  document.getElementById('btn-docx').addEventListener('click', async () => {
    const isEn = state.currentLang === 'en';
    const btn = document.getElementById('btn-docx');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Generating Word DOCX...' : 'Word তৈরি হচ্ছে...'}`;
    btn.disabled = true;

    try {
      const res = await fetch('/api/export/docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: state.currentTemplate,
          language: state.currentLang,
          data: state.formData
        })
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${state.currentTemplate}.docx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        alert(isEn ? 'Failed to generate Word document.' : 'Word ফাইল তৈরি করতে সমস্যা হয়েছে।');
      }
    } catch (err) {
      alert(isEn ? ('DOCX download failed: ' + err.message) : ('DOCX ডাউনলোড ব্যর্থ হয়েছে: ' + err.message));
    } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  });

  // Phase 5: Watermark Toggle
  const btnWatermark = document.getElementById('btn-toggle-watermark');
  const watermarkLabel = document.getElementById('watermark-label');
  if (btnWatermark) {
    btnWatermark.addEventListener('click', () => {
      const isEn = state.currentLang === 'en';
      if (state.watermarkMode === 'none') {
        state.watermarkMode = 'draft';
        if (watermarkLabel) watermarkLabel.innerText = isEn ? 'Watermark: Draft' : 'ওয়াটারমার্ক: খসড়া';
        btnWatermark.style.background = '#fee2e2';
        btnWatermark.style.color = '#dc2626';
      } else if (state.watermarkMode === 'draft') {
        state.watermarkMode = 'confidential';
        if (watermarkLabel) watermarkLabel.innerText = isEn ? 'Watermark: Confidential' : 'ওয়াটারমার্ক: গোপনীয়';
        btnWatermark.style.background = '#fef3c7';
        btnWatermark.style.color = '#d97706';
      } else {
        state.watermarkMode = 'none';
        if (watermarkLabel) watermarkLabel.innerText = isEn ? 'Watermark: Off' : 'ওয়াটারমার্ক: বন্ধ';
        btnWatermark.style.background = '';
        btnWatermark.style.color = '';
      }
      applyWatermarkToPreview();
    });
  }

  // Phase 5: Hash Badge Click opens Verify Modal
  const hashBadge = document.getElementById('crypto-fingerprint-badge');
  if (hashBadge) {
    hashBadge.addEventListener('click', () => {
      const modal = document.getElementById('verify-modal');
      if (modal) modal.style.display = 'flex';
    });
  }

  // Phase 5: Legal Notice Generator Modal Handlers
  const btnOpenNotice = document.getElementById('btn-open-notice');
  const noticeModal = document.getElementById('notice-modal');
  const closeNotice = document.getElementById('close-notice');
  const btnCloseNoticeFooter = document.getElementById('btn-close-notice-footer');
  const btnGenerateNoticeSubmit = document.getElementById('btn-generate-notice-submit');
  const btnCopyNotice = document.getElementById('btn-copy-notice');
  const btnInjectNotice = document.getElementById('btn-inject-notice');

  let lastGeneratedNotice = null;

  if (btnOpenNotice && noticeModal) {
    btnOpenNotice.addEventListener('click', () => {
      const landlord = state.formData.landlord_name || state.formData.party1_name || state.formData.employer_name || '';
      const tenant = state.formData.tenant_name || state.formData.party2_name || state.formData.employee_name || '';
      const address = state.formData.property_address || state.formData.landlord_address || '';

      const landlordInput = document.getElementById('notice-landlord');
      const tenantInput = document.getElementById('notice-tenant');
      const addressInput = document.getElementById('notice-address');

      if (landlordInput && !landlordInput.value) landlordInput.value = landlord;
      if (tenantInput && !tenantInput.value) tenantInput.value = tenant;
      if (addressInput && !addressInput.value) addressInput.value = address;

      noticeModal.style.display = 'flex';
    });
  }

  if (closeNotice) closeNotice.addEventListener('click', () => { noticeModal.style.display = 'none'; });
  if (btnCloseNoticeFooter) btnCloseNoticeFooter.addEventListener('click', () => { noticeModal.style.display = 'none'; });

  if (btnGenerateNoticeSubmit) {
    btnGenerateNoticeSubmit.addEventListener('click', async () => {
      const isEn = state.currentLang === 'en';
      const noticeType = document.getElementById('notice-type-select').value;
      const landlord = document.getElementById('notice-landlord').value;
      const tenant = document.getElementById('notice-tenant').value;
      const address = document.getElementById('notice-address').value;
      const reason = document.getElementById('notice-reason').value;

      const originalBtnText = btnGenerateNoticeSubmit.innerHTML;
      btnGenerateNoticeSubmit.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Generating notice...' : 'নোটিশ তৈরি হচ্ছে...'}`;
      btnGenerateNoticeSubmit.disabled = true;

      try {
        const res = await fetch('/api/tools/generate-notice', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            notice_type: noticeType,
            contract_data: {
              landlord_name: landlord,
              tenant_name: tenant,
              property_address: address,
              rent_amount: state.formData.rent_amount || (isEn ? '15,000' : '১৫,০০০'),
              landlord_phone: state.formData.landlord_phone || (isEn ? '+8801XXXXXXXXX' : '০১XXXXXXXXX')
            },
            custom_reason: reason
          })
        });

        if (res.ok) {
          const data = await res.json();
          lastGeneratedNotice = data;
          document.getElementById('notice-output-title').innerText = data.title;
          document.getElementById('notice-output-body').innerText = data.body;
          document.getElementById('notice-output-container').style.display = 'block';
        } else {
          alert(isEn ? 'Failed to generate legal notice.' : 'নোটিশ তৈরি করতে সমস্যা হয়েছে।');
        }
      } catch (err) {
        alert(isEn ? ('Error: ' + err.message) : ('ত্রুটি: ' + err.message));
      } finally {
        btnGenerateNoticeSubmit.innerHTML = originalBtnText;
        btnGenerateNoticeSubmit.disabled = false;
      }
    });
  }

  if (btnCopyNotice) {
    btnCopyNotice.addEventListener('click', () => {
      const isEn = state.currentLang === 'en';
      if (!lastGeneratedNotice) return;
      const onCopied = () => {
        btnCopyNotice.innerHTML = `<i class="fa-solid fa-check"></i> ${isEn ? 'Copied!' : 'কপি হয়েছে!'}`;
        setTimeout(() => {
          btnCopyNotice.innerHTML = `<i class="fa-solid fa-copy"></i> ${isEn ? 'Copy' : 'কপি'}`;
        }, 1800);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(lastGeneratedNotice.body).then(onCopied).catch(() => {
          prompt(isEn ? 'Copy notice text:' : 'নোটিশের মূল টেক্সট কপি করুন:', lastGeneratedNotice.body);
        });
      } else {
        prompt(isEn ? 'Copy notice text:' : 'নোটিশের মূল টেক্সট কপি করুন:', lastGeneratedNotice.body);
      }
    });
  }

  if (btnInjectNotice) {
    btnInjectNotice.addEventListener('click', () => {
      const isEn = state.currentLang === 'en';
      if (!lastGeneratedNotice) return;
      const container = document.getElementById('preview-container');
      const font = isEn ? 'Inter, sans-serif' : 'Hind Siliguri, sans-serif';
      const subTitle = isEn ? 'Formal Legal Notice' : 'আইনি ও প্রথাগত উচ্ছেদ/নবায়ন নোটিশ';
      const footerText = isEn
        ? `SmartLegal AI Notice Engine • Generated Date: ${lastGeneratedNotice.date}`
        : `SmartLegal AI Notice Engine • প্রস্তুতের তারিখ: ${lastGeneratedNotice.date}`;

      container.innerHTML = `<div style="font-family: ${font}; line-height: 1.65; color: #0f172a;"><div style="border-bottom: 2px solid #991b1b; padding-bottom: 8px; margin-bottom: 20px; text-align: center;"><h2 style="font-size: 17pt; color: #991b1b; margin: 0;">${lastGeneratedNotice.title}</h2><div style="font-size: 10.5pt; color: #475569; margin-top: 4px;">${subTitle}</div></div><div style="font-weight: 700; color: #1e3a8a; margin-bottom: 14px; font-size: 11.5pt;">${lastGeneratedNotice.subject}</div><div style="white-space: pre-wrap; font-size: 11pt; line-height: 1.65; color: #1e293b; text-align: justify;">${lastGeneratedNotice.body}</div><div style="margin-top: 30px; border-top: 1px dashed #cbd5e1; padding-top: 10px; font-size: 9pt; color: #64748b; text-align: center;">${footerText}</div></div>`;
      noticeModal.style.display = 'none';
      applyWatermarkToPreview();
      refreshDocumentHash();
      updatePageGuideAndCount();
    });
  }

  // Phase 5: Tamper-Proof SHA-256 Verification Modal Handlers
  const btnVerifyTamper = document.getElementById('btn-verify-tamper');
  const verifyModal = document.getElementById('verify-modal');
  const closeVerify = document.getElementById('close-verify');
  const btnCloseVerifyFooter = document.getElementById('btn-close-verify-footer');
  const btnRunVerifySubmit = document.getElementById('btn-run-verify-submit');
  const verifyResultBox = document.getElementById('verify-result-box');

  if (btnVerifyTamper && verifyModal) {
    btnVerifyTamper.addEventListener('click', () => {
      verifyModal.style.display = 'flex';
      refreshDocumentHash();
    });
  }

  if (closeVerify) closeVerify.addEventListener('click', () => { verifyModal.style.display = 'none'; });
  if (btnCloseVerifyFooter) btnCloseVerifyFooter.addEventListener('click', () => { verifyModal.style.display = 'none'; });

  if (btnRunVerifySubmit) {
    btnRunVerifySubmit.addEventListener('click', async () => {
      const isEn = state.currentLang === 'en';
      const expectedHash = document.getElementById('verify-hash-input').value.trim();
      if (!expectedHash) {
        alert(isEn ? 'Please enter a reference hash code.' : 'অনুগ্রহ করে রেফারেন্স হ্যাশ কোড ইনপুট দিন।');
        return;
      }

      const container = document.getElementById('preview-container');
      const currentContent = container ? container.innerText : '';

      btnRunVerifySubmit.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${isEn ? 'Verifying...' : 'যাচাই হচ্ছে...'}`;
      btnRunVerifySubmit.disabled = true;

      try {
        const res = await fetch('/api/tools/verify-hash', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: currentContent,
            expected_hash: expectedHash
          })
        });

        if (res.ok) {
          const result = await res.json();
          verifyResultBox.style.display = 'block';

          if (result.is_valid) {
            verifyResultBox.innerHTML = isEn
              ? `<div style="background: #ecfdf5; border: 1.5px solid #10b981; border-radius: 8px; padding: 14px; color: #065f46;"><div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; margin-bottom: 6px;"><i class="fa-solid fa-circle-check" style="color: #10b981; font-size: 1.2rem;"></i> DOCUMENT IS 100% AUTHENTIC & UN-TAMPERED</div><p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">Cryptographic mathematical hash matches perfectly. No modifications or alterations have occurred.</p><div style="margin-top: 8px; font-family: monospace; font-size: 0.78rem; color: #047857;">Computed Hash: ${result.computed_hash}</div></div>`
              : `<div style="background: #ecfdf5; border: 1.5px solid #10b981; border-radius: 8px; padding: 14px; color: #065f46;"><div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; margin-bottom: 6px;"><i class="fa-solid fa-circle-check" style="color: #10b981; font-size: 1.2rem;"></i> দলিলটি ১০০% অবিকৃত ও খাঁটি (AUTHENTIC & UN-TAMPERED)</div><p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">ক্রিপ্টোগ্রাফিক হ্যাশ শতভাগ মিলে গেছে। স্বাক্ষরের পর দলিলে কোনো কাটছাঁট বা অবৈধ পরিবর্তন করা হয়নি।</p><div style="margin-top: 8px; font-family: monospace; font-size: 0.78rem; color: #047857;">Computed Hash: ${result.computed_hash}</div></div>`;
          } else {
            verifyResultBox.innerHTML = isEn
              ? `<div style="background: #fef2f2; border: 1.5px solid #ef4444; border-radius: 8px; padding: 14px; color: #991b1b;"><div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; margin-bottom: 6px;"><i class="fa-solid fa-triangle-exclamation" style="color: #ef4444; font-size: 1.2rem;"></i> WARNING: DOCUMENT TAMPERED / MODIFIED</div><p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">The computed hash does not match the reference hash. Document text or figures have been altered.</p><div style="margin-top: 8px; font-family: monospace; font-size: 0.78rem; color: #b91c1c;">Current Hash: ${result.computed_hash}</div></div>`
              : `<div style="background: #fef2f2; border: 1.5px solid #ef4444; border-radius: 8px; padding: 14px; color: #991b1b;"><div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; margin-bottom: 6px;"><i class="fa-solid fa-triangle-exclamation" style="color: #ef4444; font-size: 1.2rem;"></i> সতর্কতা: দলিলটি বিকৃত বা পরিবর্তিত (TAMPERED / MODIFIED)</div><p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">প্রদত্ত রেফারেন্স হ্যাশের সাথে বর্তমান দলিলের হ্যাশ মেলেনি। মূল ডকুমেন্টের তথ্য বিকৃত বা পরিবর্তন করা হয়েছে।</p><div style="margin-top: 8px; font-family: monospace; font-size: 0.78rem; color: #b91c1c;">Current Hash: ${result.computed_hash}</div></div>`;
          }
        } else {
          alert(isEn ? 'Failed to verify hash.' : 'হ্যাশ যাচাই করতে ব্যর্থ হয়েছে।');
        }
      } catch (err) {
        alert(isEn ? ('Error: ' + err.message) : ('ত্রুটি: ' + err.message));
      } finally {
        btnRunVerifySubmit.innerHTML = `<i class="fa-solid fa-shield-halved"></i> ${isEn ? 'Verify Document Authenticity' : 'দলিলের প্রমাণিকতা যাচাই করুন'}`;
        btnRunVerifySubmit.disabled = false;
      }
    });
  }

  // Active Tab Keep-Warm: prevents Render.com free instance from sleeping while user drafts
  setInterval(() => {
    if (document.visibilityState === 'visible') {
      fetch('/api/health').catch(() => {});
    }
  }, 3 * 60 * 1000);

  // Re-calculate A4 preview boundaries on viewport/font resize
  window.addEventListener('resize', () => {
    updatePageGuideAndCount();
  });
}

window.addEventListener('DOMContentLoaded', initApp);
