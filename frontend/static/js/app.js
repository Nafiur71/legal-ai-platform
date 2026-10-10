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
  currentDocHash: '',
  isViewingNotice: false,
  zoomLevel: 1.0
};

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function showToast(message, type = 'info', duration = 3200) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-item toast-${type}`;

  const iconMap = {
    success: 'fa-circle-check',
    error: 'fa-circle-exclamation',
    warning: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };
  const icon = iconMap[type] || 'fa-circle-info';

  toast.innerHTML = `
    <i class="fa-solid ${icon} toast-icon"></i>
    <div class="toast-msg">${escapeHtml(message)}</div>
    <button class="toast-close" title="বন্ধ করুন">✕</button>
  `;

  const closeBtn = toast.querySelector('.toast-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      toast.classList.add('toast-fade-out');
      setTimeout(() => toast.remove(), 250);
    });
  }

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.classList.add('toast-fade-out');
      setTimeout(() => toast.remove(), 250);
    }
  }, duration);
}

const sampleContractsData = {
  tenancy_agreement: {
    execution_date: '১০ অক্টোবর ২০২৬',
    landlord_name: 'মোহাম্মদ রফিকুল ইসলাম',
    landlord_father: 'মরহুম আব্দুল হামিদ',
    landlord_address: 'বাড়ি নং ১২, রোড নং ৫, ধানমন্ডি, ঢাকা-১২০৫',
    landlord_nid: '১৯৮৫২৬৯২৪৭৮১২',
    landlord_phone: '০১৭১১-২২৩৩৪৪',
    tenant_name: 'তানভীর আহমেদ চৌধুরী',
    tenant_father: 'আনোয়ারুল ইসলাম চৌধুরী',
    tenant_address: 'গ্রাম: সুখপুর, থানা: সোনারগাঁও, জেলা: নারায়ণগঞ্জ',
    tenant_nid: '১৯৯২০৩৪৫৬৭৮৯০',
    tenant_phone: '০১৮২২-৩৩৪৪৫৫',
    property_address: 'ফ্ল্যাট নং ৪/বি (৪র্থ তলা), বাড়ি নং ১২, রোড নং ৫, ধানমন্ডি আ/এ, ঢাকা',
    property_type: 'আবাসিক ফ্ল্যাট (৩ বেডরুম, ৩ বাথরুম, ড্রয়িং-ডাইনিং)',
    start_date: '০১ নভেম্বর ২০২৬',
    duration_months: 24,
    rent_amount: '৩৫০০০',
    rent_in_words: 'পঁয়ত্রিশ হাজার টাকা মাত্র',
    payment_due_day: 7,
    deposit_amount: '১০০০০০',
    notice_period_months: 2,
    utility_terms: 'বিদ্যুৎ ও গ্যাস বিল ভাড়াটিয়া মিটার রিডিং অনুযায়ী পরিশোধ করিবেন। পানি ও সার্ভিস চার্জ মাসিক ৫,০০০ টাকা মালিককে প্রদান করিবেন।',
    witness1_name: 'কাজী মশিউর রহমান',
    witness1_address: 'ধানমন্ডি, ঢাকা',
    witness2_name: 'সাকিব আল হাসান',
    witness2_address: 'লালমাটিয়া, ঢাকা'
  },
  nda_agreement: {
    execution_date: '১০ অক্টোবর ২০২৬',
    disclosing_party_name: 'নেক্সটজেন টেকনোলজিস লিমিটেড',
    disclosing_party_address: 'লেভেল ৭, গুলশান-২, ঢাকা-১২১২',
    disclosing_party_rep: 'রাশেদ করিম (ব্যবস্থাপনা পরিচালক)',
    receiving_party_name: 'আইটি সলিউশনস বাংলাদেশ',
    receiving_party_address: 'বাড়ি নং ৪৫, বনানী, ঢাকা-১২১৩',
    receiving_party_rep: 'ফারহানা আহমেদ (প্রধান নির্বাহী কর্মকর্তা)',
    purpose: 'এআই অ্যালগরিদম ও ফিনটেক সফটওয়্যার ডেভেলপমেন্ট প্রজেক্টের কারিগরি ও ব্যবসায়িক গোপনীয় তথ্য পারস্পরিক পর্যালোচনা।',
    duration_years: 3
  },
  freelance_contract: {
    execution_date: '১০ অক্টোবর ২০২৬',
    client_name: 'গ্লোবাল ক্রিয়েটিভ মিডিয়া',
    client_address: 'উত্তরা সেক্টর ৩, ঢাকা-১২৩০',
    client_email: 'contact@globalcreative.com',
    freelancer_name: 'আরিফুল হক',
    freelancer_title: 'Full-Stack Web Developer & UI Designer',
    freelancer_address: 'মিরপুর ডিওএইচএস, ঢাকা',
    freelancer_email: 'ariful.dev@gmail.com',
    scope_of_work: 'সম্পূর্ণ রেসপনসিভ ই-কমার্স ওয়েব প্ল্যাটফর্ম ও অ্যাডমিন ড্যাশবোর্ড তৈরি, পেমেন্ট গেটওয়ে ইন্টিগ্রেশন এবং ক্লাউড ডিপ্লয়মেন্ট।',
    currency: '৳',
    total_amount: '১,৫০,০০০',
    payment_milestones: 'প্রকল্প শুরুর পূর্বে ৩০% অগ্রিম, UI/UX অনুমোদনের পর ৪০% এবং চূড়ান্ত সফল হ্যান্ডওভারের পর অবশিষ্ট ৩০% পরিশোধ।',
    deadline: '১৫ ডিসেম্বর ২০২৬',
    free_revisions: 3
  },
  partnership_agreement: {
    execution_date: '১০ অক্টোবর ২০২৬',
    partner1_name: 'মাহমুদুল হাসান',
    partner1_father: 'সামসুল হক',
    partner1_address: 'ধানমন্ডি, ঢাকা',
    partner1_nid: '১৯৮৮২৬৯১২২৩৩৪',
    partner1_phone: '০১৭০০-১১২২৩৩',
    partner2_name: 'আহমেদ জুবায়ের',
    partner2_father: 'রেজাউল করিম',
    partner2_address: 'বনশ্রী, ঢাকা',
    partner2_nid: '১৯৯০২৬৯৫৫৬৬৭৭',
    partner2_phone: '০১৮০০-৪৪৫৫৬৬',
    firm_name: 'ইনোভেক্স কনসাল্টিং পার্টনার্স',
    firm_address: 'কাওরান বাজার, ঢাকা-১২১৫',
    total_capital: '১০,০০,০০০ (দশ লক্ষ টাকা)',
    partner1_share: 60,
    partner2_share: 40,
    bank_operation: 'যেকোনো তপশিলি ব্যাংকে উভয় অংশীদারের যৌথ স্বাক্ষরে ব্যাংক হিসাব পরিচালিত হইবে।',
    notice_period_months: 3
  },
  employment_agreement: {
    execution_date: '১০ অক্টোবর ২০২৬',
    company_name: 'প্রাইম সফটওয়্যার সলিউশনস লিমিটেড',
    company_address: 'তেজগাঁও শিল্প এলাকা, ঢাকা-১২০৮',
    company_rep: 'মোস্তাফিজুর রহমান (হেড অব এইচআর)',
    employee_name: 'মেহেদী হাসান সুমন',
    employee_father: 'নুরুল ইসলাম',
    employee_address: 'পল্লবী, মিরপুর, ঢাকা-১২১৬',
    employee_nid: '১৯৯৪২৬৯৮৮৭৭৬৬',
    employee_phone: '০১৯১১-৮৮৯৯০০',
    designation: 'Senior Software Engineer',
    department: 'Software Engineering & Cloud Architecture',
    salary_amount: '৮৫,০০০ (পঁচাশি হাজার টাকা মাত্র)'
  }
};

const sampleContractsData_en = {
  tenancy_agreement: {
    execution_date: 'October 10, 2026',
    landlord_name: 'Mohammad Rafiqul Islam',
    landlord_father: 'Late Abdul Hamid',
    landlord_address: 'House 12, Road 5, Dhanmondi, Dhaka-1205',
    landlord_nid: '1985269247812',
    landlord_phone: '01711-223344',
    tenant_name: 'Tanvir Ahmed Chowdhury',
    tenant_father: 'Anwarul Islam Chowdhury',
    tenant_address: 'Village: Sukhpur, Thana: Sonargaon, Narayanganj',
    tenant_nid: '1992034567890',
    tenant_phone: '01822-334455',
    property_address: 'Flat 4/B (4th Floor), House 12, Road 5, Dhanmondi R/A, Dhaka',
    property_type: 'Residential Apartment (3 Bed, 3 Bath, Drawing-Dining)',
    start_date: 'November 01, 2026',
    duration_months: 24,
    rent_amount: '35000',
    rent_in_words: 'Thirty-Five Thousand BDT Only',
    payment_due_day: 7,
    deposit_amount: '100000',
    notice_period_months: 2,
    utility_terms: 'Electricity, gas, and utility bills shall be borne directly by the Tenant per monthly meter reading. Service and security charges of BDT 5,000 shall be paid monthly to the Landlord.',
    witness1_name: 'Kazi Moshiur Rahman',
    witness1_address: 'Dhanmondi, Dhaka',
    witness2_name: 'Shakib Al Hasan',
    witness2_address: 'Lalmatia, Dhaka'
  },
  nda_agreement: {
    execution_date: 'October 10, 2026',
    disclosing_party_name: 'NextGen Technologies Ltd.',
    disclosing_party_address: 'Level 7, Gulshan-2, Dhaka-1212',
    disclosing_party_rep: 'Rashed Karim (Managing Director)',
    receiving_party_name: 'IT Solutions Bangladesh Ltd.',
    receiving_party_address: 'House 45, Banani, Dhaka-1213',
    receiving_party_rep: 'Farhana Ahmed (Chief Executive Officer)',
    purpose: 'Mutual evaluation and confidential due diligence regarding proprietary AI algorithms, cloud microservices codebase, and enterprise fintech architecture.',
    duration_years: 3
  },
  freelance_contract: {
    execution_date: 'October 10, 2026',
    client_name: 'Global Creative Media Inc.',
    client_address: 'Uttara Sector 3, Dhaka-1230',
    client_email: 'contact@globalcreative.com',
    freelancer_name: 'Ariful Haque',
    freelancer_title: 'Full-Stack Web Developer & UI Designer',
    freelancer_address: 'Mirpur DOHS, Dhaka',
    freelancer_email: 'ariful.dev@gmail.com',
    scope_of_work: 'End-to-end development of responsive web application, interactive client portal, Stripe & SSLCommerz gateway integration, and production cloud deployment.',
    currency: 'BDT',
    total_amount: '150000',
    payment_milestones: '30% advance deposit upon signing, 40% milestone release upon UI/UX approval, and remaining 30% upon final acceptance & source code handover.',
    deadline: 'December 15, 2026',
    free_revisions: 3
  },
  partnership_agreement: {
    execution_date: 'October 10, 2026',
    partner1_name: 'Mahmudul Hasan',
    partner1_father: 'Shamsul Haque',
    partner1_address: 'Dhanmondi, Dhaka',
    partner1_nid: '1988269122334',
    partner1_phone: '01700-112233',
    partner2_name: 'Ahmed Zubair',
    partner2_father: 'Rezaul Karim',
    partner2_address: 'Banasree, Dhaka',
    partner2_nid: '1990269556677',
    partner2_phone: '01800-445566',
    firm_name: 'Innovex Consulting Partners',
    firm_address: 'Kawran Bazar, Dhaka-1215',
    total_capital: '1000000',
    partner1_share: 60,
    partner2_share: 40,
    bank_operation: 'Joint signatures of both partners in any scheduled commercial bank.',
    notice_period_months: 3
  },
  employment_agreement: {
    execution_date: 'October 10, 2026',
    company_name: 'Prime Software Solutions Ltd.',
    company_address: 'Tejgaon Industrial Area, Dhaka-1208',
    company_rep: 'Mostafizur Rahman (Head of HR)',
    employee_name: 'Mehedi Hasan Sumon',
    employee_father: 'Nurul Islam',
    employee_address: 'Pallabi, Mirpur, Dhaka-1216',
    employee_nid: '1994269887766',
    employee_phone: '01911-889900',
    designation: 'Senior Software Engineer',
    department: 'Software Engineering & Cloud Architecture',
    salary_amount: '85000',
    probation_months: 3,
    notice_period_days: 30
  }
};

const formDefinitions = {
  tenancy_agreement: {
    step1: [
      { id: 'execution_date', label: 'চুক্তির তারিখ / Execution Date', label_en: 'Date of Execution', type: 'text' },
      { id: 'landlord_name', label: '১ম পক্ষ: বাড়িওয়ালার নাম', label_en: 'Landlord Full Name (First Party)', type: 'text' },
      { id: 'landlord_father', label: 'বাড়িওয়ালার পিতা/স্বামীর নাম', label_en: "Landlord's Father / Spouse Name", type: 'text' },
      { id: 'landlord_address', label: 'বাড়িওয়ালার ঠিকানা', label_en: 'Landlord Address', type: 'text' },
      { id: 'landlord_nid', label: 'এনআইডি / পাসপোর্ট নং', label_en: 'Landlord NID / Passport', type: 'text' },
      { id: 'landlord_phone', label: 'মোবাইল নম্বর', label_en: 'Landlord Phone Number', type: 'text' },
      { id: 'tenant_name', label: '২য় পক্ষ: ভাড়াটিয়ার নাম', label_en: 'Tenant Full Name (Second Party)', type: 'text' },
      { id: 'tenant_father', label: 'ভাড়াটিয়ার পিতা/স্বামীর নাম', label_en: "Tenant's Father / Spouse Name", type: 'text' },
      { id: 'tenant_address', label: 'ভাড়াটিয়ার স্থায়ী ঠিকানা', label_en: 'Tenant Permanent Address', type: 'text' },
      { id: 'tenant_nid', label: 'ভাড়াটিয়ার এনআইডি নং', label_en: 'Tenant NID / Passport', type: 'text' },
      { id: 'tenant_phone', label: 'ভাড়াটিয়ার মোবাইল নম্বর', label_en: 'Tenant Phone Number', type: 'text' }
    ],
    step2: [
      { id: 'property_address', label: 'ভাড়াকৃত সম্পত্তির ঠিকানা ও পূর্ণ বিবরণ', label_en: 'Premises Address & Detailed Description', type: 'textarea' },
      { id: 'property_type', label: 'সম্পত্তির ধরণ (যেমন: আবাসিক ফ্ল্যাট / দোকান / বাণিজ্যিক স্পেস)', label_en: 'Property Type (e.g., Residential Apartment / Commercial Space)', type: 'text' },
      { id: 'start_date', label: 'চুক্তি কার্যকরের তারিখ', label_en: 'Tenancy Commencement Date', type: 'text' },
      { id: 'duration_months', label: 'চুক্তির মেয়াদ (মাসে)', label_en: 'Duration of Tenancy (Months)', type: 'number' },
      { id: 'rent_amount', label: 'মাসিক ভাড়া (টাকায়)', label_en: 'Monthly Rent (in BDT)', type: 'text' },
      { id: 'rent_in_words', label: 'ভাড়ার পরিমাণ (কথায়)', label_en: 'Rent Amount in Words', type: 'text' },
      { id: 'payment_due_day', label: 'প্রতি মাসের কত তারিখের মধ্যে পরিশোধযোগ্য', label_en: 'Payment Due Day of the Month (e.g. 7th)', type: 'number' },
      { id: 'deposit_amount', label: 'অগ্রিম জামানতের পরিমাণ (টাকায়)', label_en: 'Advance Security Deposit (in BDT)', type: 'text' },
      { id: 'notice_period_months', label: 'চুক্তি বাতিলের নোটিশ পিরিয়ড (মাসে)', label_en: 'Termination Notice Period (Months)', type: 'number' },
      { id: 'utility_terms', label: 'ইউটিলিটি ও সার্ভিস চার্জ শর্ত', label_en: 'Utility & Maintenance Terms', type: 'textarea' }
    ],
    step4: [
      { id: 'witness1_name', label: '১ম সাক্ষীর নাম', label_en: '1st Witness Name', type: 'text' },
      { id: 'witness1_address', label: '১ম সাক্ষীর ঠিকানা', label_en: '1st Witness Address', type: 'text' },
      { id: 'witness2_name', label: '২য় সাক্ষীর নাম', label_en: '2nd Witness Name', type: 'text' },
      { id: 'witness2_address', label: '২য় সাক্ষীর ঠিকানা', label_en: '2nd Witness Address', type: 'text' }
    ]
  },
  nda_agreement: {
    step1: [
      { id: 'execution_date', label: 'চুক্তির তারিখ / Date', label_en: 'Date of Execution', type: 'text' },
      { id: 'disclosing_party_name', label: 'তথ্য প্রকাশকারী (Disclosing Party) নাম/প্রতিষ্ঠান', label_en: 'Disclosing Party Name / Entity', type: 'text' },
      { id: 'disclosing_party_address', label: 'প্রকাশকারীর ঠিকানা', label_en: 'Disclosing Party Address', type: 'text' },
      { id: 'disclosing_party_rep', label: 'অনুমোদিত প্রতিনিধি ও পদবি', label_en: 'Authorized Representative & Title', type: 'text' },
      { id: 'receiving_party_name', label: 'তথ্য গ্রহণকারী (Receiving Party) নাম/প্রতিষ্ঠান', label_en: 'Receiving Party Name / Entity', type: 'text' },
      { id: 'receiving_party_address', label: 'গ্রহণকারীর ঠিকানা', label_en: 'Receiving Party Address', type: 'text' },
      { id: 'receiving_party_rep', label: 'অনুমোদিত প্রতিনিধি ও পদবি', label_en: 'Authorized Representative & Title', type: 'text' }
    ],
    step2: [
      { id: 'purpose', label: 'তথ্য বিনিময়ের মূল উদ্দেশ্য (Business Purpose)', label_en: 'Authorized Business Purpose', type: 'textarea' },
      { id: 'duration_years', label: 'গোপনীয়তার মেয়াদ (বছরে)', label_en: 'Confidentiality Term (Years)', type: 'number' }
    ],
    step4: []
  },
  freelance_contract: {
    step1: [
      { id: 'execution_date', label: 'চুক্তির তারিখ / Date', label_en: 'Date of Execution', type: 'text' },
      { id: 'client_name', label: 'গ্রাহকের নাম / ক্লায়েন্ট কোম্পানি', label_en: 'Client Name / Organization', type: 'text' },
      { id: 'client_address', label: 'গ্রাহকের ঠিকানা', label_en: 'Client Address', type: 'text' },
      { id: 'client_email', label: 'গ্রাহকের অফিসিয়াল ইমেইল', label_en: 'Client Email', type: 'text' },
      { id: 'freelancer_name', label: 'ফ্রিল্যান্সার / পরামর্শকের নাম', label_en: 'Freelancer / Consultant Name', type: 'text' },
      { id: 'freelancer_title', label: 'পেশাগত পদবি (যেমন: Full-Stack Developer)', label_en: 'Professional Title (e.g., Full-Stack Developer)', type: 'text' },
      { id: 'freelancer_address', label: 'ঠিকানা', label_en: 'Freelancer Address', type: 'text' },
      { id: 'freelancer_email', label: 'ইমেইল', label_en: 'Freelancer Email', type: 'text' }
    ],
    step2: [
      { id: 'scope_of_work', label: 'কাজের পরিধি ও ডেলিভারেবলস (Scope of Work)', label_en: 'Scope of Work & Deliverables', type: 'textarea' },
      { id: 'currency', label: 'কারেন্সি প্রতীক (যেমন: ৳ বা $)', label_en: 'Currency Symbol (e.g., BDT or USD)', type: 'text' },
      { id: 'total_amount', label: 'মোট পারিশ্রমিকের পরিমাণ', label_en: 'Total Fee / Compensation', type: 'text' },
      { id: 'payment_milestones', label: 'পেমেন্ট মাইলস্টোন ও শর্তাবলি', label_en: 'Payment Milestones & Schedule', type: 'textarea' },
      { id: 'deadline', label: 'কাজের চূড়ান্ত সমাপ্তির তারিখ', label_en: 'Project Completion Deadline', type: 'text' },
      { id: 'free_revisions', label: 'বিনামূল্যে রিভিশন সংখ্যা', label_en: 'Included Revisions Count', type: 'number' }
    ],
    step4: []
  },
  partnership_agreement: {
    step1: [
      { id: 'execution_date', label: 'চুক্তির তারিখ / Date', label_en: 'Date of Execution', type: 'text' },
      { id: 'partner1_name', label: '১ম অংশীদারের নাম', label_en: '1st Partner Full Name', type: 'text' },
      { id: 'partner1_father', label: '১ম অংশীদারের পিতা/স্বামীর নাম', label_en: "1st Partner Father/Spouse Name", type: 'text' },
      { id: 'partner1_address', label: '১ম অংশীদারের ঠিকানা', label_en: '1st Partner Address', type: 'text' },
      { id: 'partner1_nid', label: '১ম অংশীদারের এনআইডি নং', label_en: '1st Partner NID No', type: 'text' },
      { id: 'partner1_phone', label: '১ম অংশীদারের মোবাইল', label_en: '1st Partner Phone', type: 'text' },
      { id: 'partner2_name', label: '২য় অংশীদারের নাম', label_en: '2nd Partner Full Name', type: 'text' },
      { id: 'partner2_father', label: '২য় অংশীদারের পিতা/স্বামীর নাম', label_en: "2nd Partner Father/Spouse Name", type: 'text' },
      { id: 'partner2_address', label: '২য় অংশীদারের ঠিকানা', label_en: '2nd Partner Address', type: 'text' },
      { id: 'partner2_nid', label: '২য় অংশীদারের এনআইডি নং', label_en: '2nd Partner NID No', type: 'text' },
      { id: 'partner2_phone', label: '২য় অংশীদারের মোবাইল', label_en: '2nd Partner Phone', type: 'text' }
    ],
    step2: [
      { id: 'firm_name', label: 'অংশীদারি প্রতিষ্ঠানের নাম', label_en: 'Partnership Firm Name', type: 'text' },
      { id: 'firm_address', label: 'প্রধান কার্যালয়ের ঠিকানা', label_en: 'Principal Place of Business', type: 'text' },
      { id: 'total_capital', label: 'প্রাথমিক মোট মূলধন (টাকায়)', label_en: 'Total Initial Capital (BDT)', type: 'text' },
      { id: 'partner1_share', label: '১ম অংশীদারের শেয়ার/মুনাফার হার (%)', label_en: '1st Partner Profit/Loss Share (%)', type: 'number' },
      { id: 'partner2_share', label: '২য় অংশীদারের শেয়ার/মুনাফার হার (%)', label_en: '2nd Partner Profit/Loss Share (%)', type: 'number' },
      { id: 'bank_operation', label: 'ব্যাংক হিসাব পরিচালনা পদ্ধতি', label_en: 'Bank Operation Terms', type: 'text' },
      { id: 'notice_period_months', label: 'অংশীদারি অবসানের নোটিশ (মাসে)', label_en: 'Dissolution Notice Period (Months)', type: 'number' }
    ],
    step4: []
  },
  employment_agreement: {
    step1: [
      { id: 'execution_date', label: 'যোগদানের তারিখ / Execution Date', label_en: 'Appointment / Commencement Date', type: 'text' },
      { id: 'company_name', label: 'প্রতিষ্ঠানের নাম (Employer)', label_en: 'Employer / Company Name', type: 'text' },
      { id: 'company_address', label: 'কোম্পানির ঠিকানা', label_en: 'Office Address', type: 'text' },
      { id: 'company_rep', label: 'কর্তৃপক্ষের নাম ও পদবি', label_en: 'Authorized Signatory & Designation', type: 'text' },
      { id: 'employee_name', label: 'কর্মচারী / কর্মকর্তার নাম', label_en: 'Employee Full Name', type: 'text' },
      { id: 'employee_father', label: 'পিতা/স্বামীর নাম', label_en: "Father / Spouse Name", type: 'text' },
      { id: 'employee_address', label: 'স্থায়ী ঠিকানা', label_en: 'Residential Address', type: 'text' },
      { id: 'employee_nid', label: 'এনআইডি নং', label_en: 'Employee NID No', type: 'text' },
      { id: 'employee_phone', label: 'মোবাইল নম্বর', label_en: 'Employee Phone Number', type: 'text' }
    ],
    step2: [
      { id: 'designation', label: 'পদবি (Designation)', label_en: 'Job Title / Designation', type: 'text' },
      { id: 'department', label: 'বিভাগ (Department)', label_en: 'Department / Unit', type: 'text' },
      { id: 'salary_amount', label: 'মাসিক সর্বসাকুল্যে বেতন (টাকায়)', label_en: 'Gross Monthly Remuneration (BDT)', type: 'text' },
      { id: 'probation_months', label: 'শিক্ষানবিসকাল (মাসে)', label_en: 'Probationary Period (Months)', type: 'number' },
      { id: 'notice_period_days', label: 'চাকরি অবসানের নোটিশ পিরিয়ড (দিনে)', label_en: 'Notice Period for Separation (Days)', type: 'number' }
    ],
    step4: []
  }
};

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
      if (item.language) {
        state.currentLang = item.language;
        const langSel = document.getElementById('lang-select');
        if (langSel) langSel.value = item.language;
        updateUILanguage(item.language);
      }
      document.getElementById('template-select').value = item.document_type;
      setupTemplate(item.document_type, item.data);
      
      // Auto prompt 2nd party to sign
      setTimeout(() => {
        state.sigTarget = 'p2';
        document.getElementById('sign-target-p2').className = 'btn btn-primary';
        document.getElementById('sign-target-p1').className = 'btn btn-secondary';
        document.getElementById('sign-modal').style.display = 'flex';
      }, 600);
    }
  } catch (e) {
    console.error('Failed to load shared contract:', e);
  }
}

function isDefaultOrSampleData() {
  if (!state.formData || Object.keys(state.formData).length === 0) return true;
  const d = state.formData;
  const bnKeywords = ['১০ অক্টোবর', '১২ সেপ্টেম্বর', 'রফিকুল ইসলাম', 'তানভীর আহমেদ', 'নেক্সটজেন', 'টেকনোভেশন', 'গ্লোবাল ক্রিয়েটিভ', 'নেক্সাস ডিজিটাল', 'মাহমুদুল হাসান', 'প্রাইম সফটওয়্যার', 'ইনোভেক্স', 'ধানমন্ডি', 'উত্তরা'];
  const enKeywords = ['October 10', 'September 12', 'Rafiqul Islam', 'Tanvir Ahmed', 'NextGen Technologies', 'Global Creative', 'Mahmudul Hasan', 'Prime Software', 'Dhanmondi', 'Uttara'];
  
  for (const k in d) {
    if (typeof d[k] === 'string') {
      if (bnKeywords.some(w => d[k].includes(w)) || enKeywords.some(w => d[k].includes(w))) {
        return true;
      }
    }
  }
  return false;
}

function updateUILanguage(lang) {
  state.currentLang = lang;
  const isEn = lang === 'en';

  // Synchronize language dropdown
  const langSel = document.getElementById('lang-select');
  if (langSel && langSel.value !== lang) langSel.value = lang;

  // Auto-switch demo data if the current data is sample/default
  if (isDefaultOrSampleData()) {
    state.formData = isEn 
      ? JSON.parse(JSON.stringify(sampleContractsData_en[state.currentTemplate] || {}))
      : JSON.parse(JSON.stringify(sampleContractsData[state.currentTemplate] || {}));
    state.customClauses = state.formData.custom_clauses || [];
  }

  // 1. Top Navbar & Brand
  const brandSub = document.getElementById('brand-subtitle');
  if (brandSub) brandSub.textContent = isEn ? 'Intelligent Legal Automation & Document Generator' : 'বুদ্ধিমান আইনি অটোমেশন ও ডকুমেন্ট জেনারেটর';

  const btnDemoFill = document.getElementById('btn-demo-fill');
  if (btnDemoFill) {
    btnDemoFill.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> ${isEn ? 'Load Demo Data' : 'নমুনা ডেটা পূরণ'}`;
    btnDemoFill.title = isEn ? 'Fill form with realistic demo data in 1-click' : 'এক ক্লিকে বাস্তবসম্মত আইনি নমুনা তথ্য দিয়ে ফর্ম পূরণ করুন';
  }

  const btnToolsMenu = document.getElementById('btn-tools-menu');
  if (btnToolsMenu) btnToolsMenu.innerHTML = `<i class="fa-solid fa-toolbox" style="color: #6366f1;"></i> ${isEn ? 'Legal Tools' : 'আইনি টুলস'} <i class="fa-solid fa-chevron-down" style="font-size: 0.72rem; margin-left: 2px;"></i>`;

  const btnStampCalc = document.getElementById('btn-open-stamp-calc');
  if (btnStampCalc) btnStampCalc.innerHTML = `<i class="fa-solid fa-calculator" style="color: #ea580c;"></i> ${isEn ? 'Stamp Duty Calculator' : 'স্ট্যাম্প ডিউটি ক্যালকুলেটর'}`;

  const btnNotice = document.getElementById('btn-open-notice');
  if (btnNotice) btnNotice.innerHTML = `<i class="fa-solid fa-bullhorn" style="color: #dc2626;"></i> ${isEn ? 'Legal Notice Generator' : 'আইনি নোটিশ জেনারেটর'}`;

  const btnUploadAudit = document.getElementById('btn-upload-audit');
  if (btnUploadAudit) btnUploadAudit.innerHTML = `<i class="fa-solid fa-file-arrow-up" style="color: #7c3aed;"></i> ${isEn ? 'File Upload & AI Audit' : 'ফাইল আপলোড ও AI অডিট'}`;

  const btnVerifyTamper = document.getElementById('btn-verify-tamper');
  if (btnVerifyTamper) btnVerifyTamper.innerHTML = `<i class="fa-solid fa-fingerprint" style="color: #0d9488;"></i> ${isEn ? 'SHA-256 Hash Authenticity' : 'SHA-256 হ্যাশ প্রমাণিকতা'}`;

  const btnHistory = document.getElementById('btn-history');
  if (btnHistory) btnHistory.innerHTML = `<i class="fa-solid fa-clock-rotate-left"></i> ${isEn ? 'History' : 'হিস্ট্রি'}`;

  const btnShare = document.getElementById('btn-share-contract');
  if (btnShare) btnShare.innerHTML = `<i class="fa-solid fa-share-nodes" style="color: #0284c7;"></i> ${isEn ? 'Share & Sign' : 'শেয়ার ও সাইন'}`;

  const btnOpenSign = document.getElementById('btn-open-sign');
  if (btnOpenSign) btnOpenSign.innerHTML = `<i class="fa-solid fa-signature" style="color: #059669;"></i> ${isEn ? 'E-Signature' : 'ই-স্বাক্ষর'}`;

  const btnSaveDraft = document.getElementById('btn-save-draft');
  if (btnSaveDraft) btnSaveDraft.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> ${isEn ? 'Save' : 'সেভ'}`;

  const btnExportMenu = document.getElementById('btn-export-menu');
  if (btnExportMenu) btnExportMenu.innerHTML = `<i class="fa-solid fa-download"></i> ${isEn ? 'Download' : 'ডাউনলোড'} <i class="fa-solid fa-chevron-down" style="font-size: 0.72rem; margin-left: 2px;"></i>`;

  const btnPdf = document.getElementById('btn-pdf');
  if (btnPdf) btnPdf.innerHTML = `<i class="fa-solid fa-file-pdf" style="color: #ef4444;"></i> ${isEn ? 'PDF Format (Official Print)' : 'PDF ফরম্যাট (অফিসিয়াল প্রিন্ট)'}`;

  const btnDocx = document.getElementById('btn-docx');
  if (btnDocx) btnDocx.innerHTML = `<i class="fa-solid fa-file-word" style="color: #2563eb;"></i> ${isEn ? 'Word / DOCX Format' : 'Word / DOCX ফরম্যাট'}`;

  // 2. Mobile View Switcher
  const btnMobWizard = document.getElementById('btn-mobile-tab-wizard');
  if (btnMobWizard) btnMobWizard.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> ${isEn ? 'Contract Editor' : 'চুক্তি এডিটর'}`;
  const btnMobPreview = document.getElementById('btn-mobile-tab-preview');
  if (btnMobPreview) btnMobPreview.innerHTML = `<i class="fa-solid fa-file-lines"></i> ${isEn ? 'Live Preview' : 'লাইভ প্রিভিউ'}`;

  // 3. Template Bar
  const tmplLabel = document.getElementById('template-bar-label');
  if (tmplLabel) tmplLabel.textContent = isEn ? 'Document:' : 'চুক্তিপত্র:';

  const tmplOptions = {
    tenancy_agreement: isEn ? '🏠 Residential / Commercial Tenancy Agreement' : '🏠 বাড়ি / ফ্ল্যাট / দোকান ভাড়ার চুক্তি',
    nda_agreement: isEn ? '🔒 Non-Disclosure Agreement (NDA)' : '🔒 নন-ডিসক্লোজার চুক্তি (NDA)',
    freelance_contract: isEn ? '💼 Freelance & Service Contract' : '💼 ফ্রিল্যান্স ও সার্ভিস চুক্তি',
    partnership_agreement: isEn ? '🤝 Partnership Business Deed' : '🤝 অংশীদারি কারবার চুক্তিপত্র (Partnership Deed)',
    employment_agreement: isEn ? '👔 Employment & Appointment Contract' : '👔 কর্মসংস্থান ও চাকরির চুক্তি (Employment Contract)'
  };
  const tmplSelect = document.getElementById('template-select');
  if (tmplSelect) {
    Array.from(tmplSelect.options).forEach(opt => {
      if (tmplOptions[opt.value]) opt.textContent = tmplOptions[opt.value];
    });
  }

  // 4. Wizard Step Navigation Tabs
  const stepTabs = document.querySelectorAll('.step-tab');
  if (stepTabs.length >= 4) {
    stepTabs[0].innerHTML = `<i class="fa-solid fa-users"></i> ${isEn ? '1. Parties Info' : '১. পক্ষের তথ্য'}`;
    stepTabs[1].innerHTML = `<i class="fa-solid fa-file-contract"></i> ${isEn ? '2. Core Terms' : '২. মূল শর্তাবলি'}`;
    stepTabs[2].innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> ${isEn ? '3. AI Custom Clauses' : '৩. AI কাস্টম ধারা'}`;
    stepTabs[3].innerHTML = `<i class="fa-solid fa-signature"></i> ${isEn ? '4. Signature & Finish' : '৪. স্বাক্ষর ও সমাপ্তি'}`;
  }

  // 5. Wizard Step Footers
  const step1Next = document.querySelector('#step-1 .btn-next-step');
  if (step1Next) step1Next.innerHTML = isEn ? 'Next: Core Terms <i class="fa-solid fa-arrow-right"></i>' : 'পরবর্তী: মূল শর্তাবলি <i class="fa-solid fa-arrow-right"></i>';

  const step2Prev = document.querySelector('#step-2 .btn-prev-step');
  if (step2Prev) step2Prev.innerHTML = isEn ? '<i class="fa-solid fa-arrow-left"></i> Previous Step' : '<i class="fa-solid fa-arrow-left"></i> পূর্ববর্তী ধাপ';

  const step2Next = document.querySelector('#step-2 .btn-next-step');
  if (step2Next) step2Next.innerHTML = isEn ? 'Next: AI Custom Clauses <i class="fa-solid fa-arrow-right"></i>' : 'পরবর্তী: AI কাস্টম ধারা <i class="fa-solid fa-arrow-right"></i>';

  const step3Prev = document.querySelector('#step-3 .btn-prev-step');
  if (step3Prev) step3Prev.innerHTML = isEn ? '<i class="fa-solid fa-arrow-left"></i> Previous Step' : '<i class="fa-solid fa-arrow-left"></i> পূর্ববর্তী ধাপ';

  const step3Next = document.querySelector('#step-3 .btn-next-step');
  if (step3Next) step3Next.innerHTML = isEn ? 'Next: Signature & Finish <i class="fa-solid fa-arrow-right"></i>' : 'পরবর্তী: স্বাক্ষর ও সমাপ্তি <i class="fa-solid fa-arrow-right"></i>';

  const step4Prev = document.querySelector('#step-4 .btn-prev-step');
  if (step4Prev) step4Prev.innerHTML = isEn ? '<i class="fa-solid fa-arrow-left"></i> Previous Step' : '<i class="fa-solid fa-arrow-left"></i> পূর্ববর্তী ধাপ';

  const step4Finish = document.getElementById('btn-finish-save');
  if (step4Finish) step4Finish.innerHTML = isEn ? '<i class="fa-solid fa-floppy-disk"></i> Save Contract' : '<i class="fa-solid fa-floppy-disk"></i> চুক্তি সংরক্ষণ করুন';

  // 6. Step 3 AI Clause Refiner Section
  const aiTitle = document.querySelector('.ai-card-title');
  if (aiTitle) aiTitle.innerHTML = `<i class="fa-solid fa-brain"></i> AI Legal Clause Refiner`;
  const aiSub = document.querySelector('.ai-card p');
  if (aiSub) aiSub.textContent = isEn 
    ? 'Write your custom conditions in plain words. Our AI will draft them into legally binding contract clauses.' 
    : 'আপনার কাস্টম কোনো শর্ত সাধারণ ভাষায় লিখুন। আমাদের AI তা আদালত ও চুক্তি আইনসম্মত ভাষায় রূপান্তর করবে।';

  const aiInput = document.getElementById('ai-clause-input');
  if (aiInput) {
    aiInput.placeholder = isEn 
      ? "e.g., 'Tenant cannot bring outsiders after 11 PM and no pets allowed...'" 
      : "যেমন: 'ভাড়াটিয়া রাত ১১টার পর কোনো বহিরাগত আনতে পারবে না এবং ফ্ল্যাটে কোনো পোষা বিড়াল বা কুকুর রাখা যাবে না...'";
  }

  const btnRefine = document.getElementById('btn-refine-clause');
  if (btnRefine) btnRefine.innerHTML = isEn ? '<i class="fa-solid fa-wand-magic-sparkles"></i> Polish into Legal Language with AI' : '<i class="fa-solid fa-wand-magic-sparkles"></i> AI দিয়ে আইনি ভাষায় পলিশ করুন';

  const btnAddClause = document.getElementById('btn-add-clause');
  if (btnAddClause) btnAddClause.innerHTML = isEn ? '<i class="fa-solid fa-plus"></i> Add Clause to Contract' : '<i class="fa-solid fa-plus"></i> চুক্তিতে ধারাটি যুক্ত করুন';

  const btnExplainAction = document.getElementById('btn-explain-clause-action');
  if (btnExplainAction) btnExplainAction.innerHTML = isEn ? '<i class="fa-solid fa-lightbulb"></i> View Plain Explanation' : '<i class="fa-solid fa-lightbulb"></i> সহজ ব্যাখ্যা দেখুন';

  const customHeader = document.querySelector('#step-3 label.form-label');
  if (customHeader) customHeader.textContent = isEn ? 'Attached Custom Clauses:' : 'সংযুক্ত কাস্টম শর্তাবলি:';

  const chipContainer = document.getElementById('clause-chips-container');
  if (chipContainer) {
    if (isEn) {
      chipContainer.innerHTML = `
        <button type="button" class="prompt-chip" data-prompt="Strictly no pets, dogs or cats allowed on the demised premises."><i class="fa-solid fa-paw"></i> No Pets Allowed</button>
        <button type="button" class="prompt-chip" data-prompt="Late rent payments beyond due day shall incur a delay penalty of BDT 100 per day."><i class="fa-solid fa-clock"></i> Delay Penalty</button>
        <button type="button" class="prompt-chip" data-prompt="Subletting or transferring the demised premises in whole or part is strictly prohibited without prior written consent."><i class="fa-solid fa-ban"></i> No Subletting</button>
        <button type="button" class="prompt-chip" data-prompt="The premises shall strictly be used for residential purposes only and never for political or unauthorized commercial activities."><i class="fa-solid fa-building-circle-xmark"></i> Non-Commercial Only</button>
      `;
    } else {
      chipContainer.innerHTML = `
        <button type="button" class="prompt-chip" data-prompt="ফ্ল্যাটে কোনো প্রকার কুকুর, বিড়াল বা পোষা প্রাণী পালন করা সম্পূর্ণরূপে নিষিদ্ধ থাকিবে।"><i class="fa-solid fa-paw"></i> পোষা প্রাণী নিষিদ্ধ</button>
        <button type="button" class="prompt-chip" data-prompt="নির্ধারিত তারিখের পর ভাড়া পরিশোধ করিলে দৈনিক ১০০ টাকা হারে বিলম্ব জরিমানা প্রদান করিতে হইবে।"><i class="fa-solid fa-clock"></i> বিলম্বে জরিমানা</button>
        <button type="button" class="prompt-chip" data-prompt="মালিকের লিখিত পূর্বানুমতি ব্যতীত ভাড়াকৃত স্পেস কোনো তৃতীয় পক্ষকে সাবলেট বা উপভাড়া দেওয়া যাইবে না।"><i class="fa-solid fa-ban"></i> সাবলেট নিষিদ্ধ</button>
        <button type="button" class="prompt-chip" data-prompt="আবাসিক ফ্ল্যাট কোনো বাণিজ্যিক, রাজনৈতিক বা আইনবহির্ভূত কাজে ব্যবহার করা যাইবে না।"><i class="fa-solid fa-building-circle-xmark"></i> বাণিজ্যিক ব্যবহার নিষেধ</button>
      `;
    }
    chipContainer.querySelectorAll('.prompt-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        if (aiInput) {
          aiInput.value = chip.getAttribute('data-prompt');
          aiInput.focus();
        }
      });
    });
  }

  // 7. Step 4 E-Signature Section
  const step4H4 = document.querySelector('#step-4 h4');
  if (step4H4) step4H4.innerHTML = `<i class="fa-solid fa-signature"></i> ${isEn ? 'Digital E-Signature' : 'ডিজিটাল ই-স্বাক্ষর (E-Signature)'}`;
  const step4P = document.querySelector('#step-4 p');
  if (step4P) step4P.textContent = isEn ? 'Sign directly on screen or send a link to collect signatures remotely.' : 'স্ক্রিনে সরাসরি স্বাক্ষর করুন অথবা লিংক পাঠিয়ে অপর পক্ষের স্বাক্ষর সংগ্রহ করুন।';
  const step4SignBtn = document.getElementById('btn-step4-sign');
  if (step4SignBtn) step4SignBtn.innerHTML = `<i class="fa-solid fa-pen-nib"></i> ${isEn ? 'Open Signature Canvas' : 'স্বাক্ষর ক্যানভাস খুলুন'}`;

  // 8. Live Paper Preview Toolbar
  const editModeLabel = document.getElementById('edit-mode-label');
  if (editModeLabel) {
    editModeLabel.innerText = isEn ? (state.isDirectEdit ? '✅ Direct Edit Active' : 'Direct Edit on Paper') : (state.isDirectEdit ? '✅ এডিট মোড চলছে' : 'সরাসরি পেপারে এডিট');
  }
  const stampBtn = document.getElementById('btn-toggle-stamp');
  if (stampBtn) stampBtn.innerHTML = `<i class="fa-solid fa-stamp"></i> ${isEn ? '300 Tk Stamp' : '৩০০ টাকার স্ট্যাম্প'}`;
  const watermarkLabel = document.getElementById('watermark-label');
  if (watermarkLabel) {
    const wmText = state.watermarkMode === 'none' 
      ? (isEn ? 'Watermark: Off' : 'ওয়াটারমার্ক: বন্ধ') 
      : (state.watermarkMode === 'draft' ? (isEn ? 'Watermark: Draft' : 'ওয়াটারমার্ক: খসড়া') : (isEn ? 'Watermark: Confidential' : 'ওয়াটারমার্ক: গোপনীয়'));
    watermarkLabel.innerText = wmText;
  }
  const tamperBadge = document.getElementById('tamper-status-badge');
  if (tamperBadge) tamperBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${isEn ? 'SECURED' : 'সিকিউরড'}`;

  // 9. Floating Chatbot
  const fabChatbot = document.getElementById('fab-chatbot');
  if (fabChatbot) fabChatbot.title = isEn ? 'Chat with SmartLegal AI Assistant' : 'আইনAI সহকারী সাথে চ্যাট করুন';
  const chatHeaderStrong = document.querySelector('#chatbot-window .chat-header strong');
  if (chatHeaderStrong) chatHeaderStrong.textContent = isEn ? 'SmartLegal AI Advisor' : 'আইনAI সহকারী (Advisor)';
  const chatFirstBubble = document.querySelector('#chat-body .chat-bubble-ai');
  if (chatFirstBubble) {
    if (isEn) {
      chatFirstBubble.innerHTML = `
        👋 Hello! I am your <strong>SmartLegal AI Advisor</strong>.<br>
        Ask any legal question regarding Bangladesh contract laws, 300 Tk stamp duty, tenancy acts, or notices.
        <div class="prompt-chips-container" style="margin-top: 10px; margin-bottom: 2px;">
          <button type="button" class="prompt-chip chat-suggestion-chip" data-query="How much stamp duty is required for house rent in Bangladesh?">💰 Stamp Duty Rates</button>
          <button type="button" class="prompt-chip chat-suggestion-chip" data-query="What are the legal rules for tenant eviction notice?">📜 Eviction Notice Law</button>
          <button type="button" class="prompt-chip chat-suggestion-chip" data-query="What is the law regarding refund of security deposit?">⚖️ Security Deposit Law</button>
        </div>
      `;
    } else {
      chatFirstBubble.innerHTML = `
        👋 নমস্কার! আমি আপনার <strong>আইনAI সহকারী</strong>।<br>
        চুক্তিপত্র, স্ট্যাম্পের নিয়ম, ভাড়া নিয়ন্ত্রণ আইন বা নোটিশ বিষয়ে যেকোনো আইনি প্রশ্ন আমাকে বাংলায় জিজ্ঞেস করতে পারেন।
        <div class="prompt-chips-container" style="margin-top: 10px; margin-bottom: 2px;">
          <button type="button" class="prompt-chip chat-suggestion-chip" data-query="বাড়ি ভাড়া চুক্তির জন্য কত টাকার স্ট্যাম্প প্রয়োজন?">💰 স্ট্যাম্প ফি কত?</button>
          <button type="button" class="prompt-chip chat-suggestion-chip" data-query="ভাড়াটিয়াকে উচ্ছেদের জন্য নোটিশের নিয়ম কি?">📜 উচ্ছেদ নোটিশের নিয়ম</button>
          <button type="button" class="prompt-chip chat-suggestion-chip" data-query="চুক্তির জামানত বা সিকিউরিটি ডিপোজিট ফেরতের আইন কি?">⚖️ জামানত ফেরত আইন</button>
        </div>
      `;
    }
    chatFirstBubble.querySelectorAll('.chat-suggestion-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const q = chip.getAttribute('data-query');
        const input = document.getElementById('chat-input');
        if (input && q) {
          input.value = q;
          const sendBtn = document.getElementById('btn-chat-send');
          if (sendBtn) sendBtn.click();
        }
      });
    });
  }
  const chatInput = document.getElementById('chat-input');
  if (chatInput) chatInput.placeholder = isEn ? 'Ask your legal question...' : 'আইনি প্রশ্নটি লিখুন...';

  // 10. Modals: Stamp Duty Calculator Modal
  const stampModalH3 = document.querySelector('#stamp-calc-modal h3');
  if (stampModalH3) stampModalH3.innerHTML = isEn 
    ? '<i class="fa-solid fa-calculator"></i> Bangladesh Stamp Duty Calculator' 
    : '<i class="fa-solid fa-calculator"></i> বাংলাদেশ স্ট্যাম্প ডিউটি ক্যালকুলেটর';
  const calcDocType = document.getElementById('calc-doc-type');
  if (calcDocType) {
    calcDocType.options[0].textContent = isEn ? 'Residential / Commercial Tenancy' : 'বাড়ি / দোকান ভাড়ার চুক্তি';
    calcDocType.options[1].textContent = isEn ? 'Partnership Business Deed' : 'অংশীদারি কারবার চুক্তি (Partnership)';
    calcDocType.options[2].textContent = isEn ? 'Non-Disclosure Agreement (NDA)' : 'নন-ডিসক্লোজার চুক্তি (NDA)';
    calcDocType.options[3].textContent = isEn ? 'Freelance Service Contract' : 'ফ্রিল্যান্স সার্ভিস চুক্তি';
    calcDocType.options[4].textContent = isEn ? 'Employment Agreement' : 'কর্মসংস্থান ও চাকরির চুক্তি';
  }
  const calcLabels = document.querySelectorAll('#stamp-calc-modal label.form-label');
  if (calcLabels.length >= 3) {
    calcLabels[0].textContent = isEn ? 'Document Type:' : 'চুক্তির ধরণ:';
    calcLabels[1].textContent = isEn ? 'Amount (Monthly Rent / Capital):' : 'টাকার পরিমাণ (ভাড়া / মূলধন):';
    calcLabels[2].textContent = isEn ? 'Duration (Months):' : 'মেয়াদ (মাসে):';
  }
  const btnRunCalc = document.getElementById('btn-run-stamp-calc');
  if (btnRunCalc) btnRunCalc.innerHTML = isEn ? '<i class="fa-solid fa-calculator"></i> Calculate Stamp Duty' : '<i class="fa-solid fa-calculator"></i> হিসাব করুন';
  const btnCloseCalc = document.getElementById('btn-close-stamp-calc-footer');
  if (btnCloseCalc) btnCloseCalc.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 11. Modals: Share & Remote Signing
  const shareH3 = document.querySelector('#share-modal h3');
  if (shareH3) shareH3.innerHTML = isEn ? '<i class="fa-solid fa-share-nodes"></i> Remote Signing & Shareable Link' : '<i class="fa-solid fa-share-nodes"></i> দূরবর্তী স্বাক্ষর ও শেয়ারিং লিংক';
  const shareDesc = document.querySelector('#share-modal .modal-body p');
  if (shareDesc) shareDesc.textContent = isEn 
    ? 'Send the link below to your tenant, client, or partner. They can review and sign the contract directly from their phone or PC:' 
    : 'নিচের লিংকটি ভাড়াটিয়া, ক্লায়েন্ট বা অংশীদারের কাছে পাঠান। তারা তাদের মোবাইল বা কম্পিউটার থেকেই চুক্তি পড়ে সরাসরি ডিজিটাল সই করতে পারবেন:';
  const btnCopyShare = document.getElementById('btn-copy-share-url');
  if (btnCopyShare) btnCopyShare.innerHTML = isEn ? '<i class="fa-solid fa-copy"></i> Copy' : '<i class="fa-solid fa-copy"></i> কপি';
  const btnWaShare = document.getElementById('btn-whatsapp-share');
  if (btnWaShare) btnWaShare.innerHTML = isEn ? '<i class="fa-brands fa-whatsapp"></i> Send via WhatsApp' : '<i class="fa-brands fa-whatsapp"></i> হোয়াটসঅ্যাপে পাঠান';
  const btnCloseShare = document.getElementById('btn-close-share-footer');
  if (btnCloseShare) btnCloseShare.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 12. Modals: E-Signature Canvas
  const signH3 = document.querySelector('#sign-modal h3');
  if (signH3) signH3.innerHTML = isEn ? '<i class="fa-solid fa-pen-nib" style="color: #059669;"></i> Digital Signature Pad' : '<i class="fa-solid fa-pen-nib" style="color: #059669;"></i> ডিজিটাল স্বাক্ষর প্যাড';
  const signTargetP1 = document.getElementById('sign-target-p1');
  if (signTargetP1) signTargetP1.textContent = isEn ? '1st Party (Landlord / Client)' : '১ম পক্ষ (মালিক/ক্লায়েন্ট)';
  const signTargetP2 = document.getElementById('sign-target-p2');
  if (signTargetP2) signTargetP2.textContent = isEn ? '2nd Party (Tenant / Employee)' : '২য় পক্ষ (ভাড়াটিয়া/কর্মী)';
  const btnClearCanvas = document.getElementById('btn-clear-canvas');
  if (btnClearCanvas) btnClearCanvas.innerHTML = isEn ? '<i class="fa-solid fa-eraser"></i> Clear' : '<i class="fa-solid fa-eraser"></i> মুছুন';
  const btnCloseSign = document.getElementById('btn-close-sign-footer');
  if (btnCloseSign) btnCloseSign.textContent = isEn ? 'Cancel' : 'বাতিল';
  const btnApplySig = document.getElementById('btn-apply-signature');
  if (btnApplySig) btnApplySig.innerHTML = isEn ? '<i class="fa-solid fa-check"></i> Attach Signature' : '<i class="fa-solid fa-check"></i> স্বাক্ষর সংযুক্ত করুন';

  // 13. Modals: History Modal
  const histH3 = document.querySelector('#history-modal h3');
  if (histH3) histH3.innerHTML = isEn ? '<i class="fa-solid fa-clock-rotate-left"></i> Saved Contracts (Database History)' : '<i class="fa-solid fa-clock-rotate-left"></i> সংরক্ষিত চুক্তিসমূহ (Database History)';
  const btnCloseHist = document.getElementById('btn-close-history-footer');
  if (btnCloseHist) btnCloseHist.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 14. Modals: External Document Upload & AI Audit
  const uploadH3 = document.querySelector('#upload-modal h3');
  if (uploadH3) uploadH3.innerHTML = isEn ? '<i class="fa-solid fa-file-shield"></i> External Document Upload & AI Audit' : '<i class="fa-solid fa-file-shield"></i> বাইরের ডকুমেন্ট আপলোড ও AI অডিট';
  const uploadText = document.getElementById('upload-text-input');
  if (uploadText) uploadText.placeholder = isEn ? 'Paste full contract text here...' : 'চুক্তিপত্রের সম্পূর্ণ টেক্সট এখানে পেস্ট করুন...';
  const btnRunAudit = document.getElementById('btn-run-upload-audit');
  if (btnRunAudit) btnRunAudit.innerHTML = isEn ? '<i class="fa-solid fa-magnifying-glass-chart"></i> Audit Full Contract with AI' : '<i class="fa-solid fa-magnifying-glass-chart"></i> AI দিয়ে সম্পূর্ণ চুক্তি অডিট করুন';
  const btnCloseUpload = document.getElementById('btn-close-upload-footer');
  if (btnCloseUpload) btnCloseUpload.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 15. Modals: AI Clause Explainer
  const explainerH3 = document.querySelector('#explainer-modal h3');
  if (explainerH3) explainerH3.innerHTML = isEn ? '<i class="fa-solid fa-lightbulb" style="color: #eab308;"></i> Plain Language Legal Meaning' : '<i class="fa-solid fa-lightbulb" style="color: #eab308;"></i> সহজ ভাষায় আইনি ধারার অর্থ';
  const btnCloseExplainer = document.getElementById('btn-close-explainer-footer');
  if (btnCloseExplainer) btnCloseExplainer.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 16. Modals: Legal Notice Generator
  const noticeH3 = document.querySelector('#notice-modal h3');
  if (noticeH3) noticeH3.innerHTML = isEn ? '<i class="fa-solid fa-bullhorn"></i> Legal Notice Generator Engine' : '<i class="fa-solid fa-bullhorn"></i> আইনি নোটিশ জেনারেটর (Legal Notice Engine)';
  const noticeDesc = document.querySelector('#notice-modal .modal-body p');
  if (noticeDesc) noticeDesc.textContent = isEn ? 'Instantly draft legally sound vacate notices, lease renewals, or payment demand notices.' : 'ভাড়াটিয়া বা সংশ্লিষ্ট পক্ষের অনুকূলে এক ক্লিকে আইনি নোটিশ, উচ্ছেদ পত্র অথবা বকেয়া তাগিদপত্র প্রস্তুত করুন।';
  const noticeTypeSelect = document.getElementById('notice-type-select');
  if (noticeTypeSelect) {
    noticeTypeSelect.options[0].textContent = isEn ? '🏠 Tenancy Vacate Notice' : '🏠 বাসা / দোকান ছাড়ার আইনি নোটিশ (Vacate Notice)';
    noticeTypeSelect.options[1].textContent = isEn ? '📄 Contract Renewal & Terms Proposition' : '📄 চুক্তি নবায়ন ও শর্ত প্রস্তাবনা পত্র (Contract Renewal)';
    noticeTypeSelect.options[2].textContent = isEn ? '⚠️ Rent Arrears Demand Notice' : '⚠️ বকেয়া ভাড়া ও পাওনা নিষ্পত্তির তাগিদপত্র (Demand Notice)';
  }
  const noticeLandlord = document.getElementById('notice-landlord');
  if (noticeLandlord) noticeLandlord.placeholder = isEn ? 'Sender Name (Landlord)' : 'মালিকের নাম';
  const noticeTenant = document.getElementById('notice-tenant');
  if (noticeTenant) noticeTenant.placeholder = isEn ? 'Recipient Name (Tenant)' : 'ভাড়াটিয়ার নাম';
  const noticeAddress = document.getElementById('notice-address');
  if (noticeAddress) noticeAddress.placeholder = isEn ? 'Premises Address' : 'ঠিকানা';
  const noticeReason = document.getElementById('notice-reason');
  if (noticeReason) noticeReason.placeholder = isEn ? 'e.g. personal requirement or 3 months overdue rent...' : 'যেমন: ব্যক্তিগত প্রয়োজনে প্রাঙ্গণ প্রয়োজন অথবা বিগত ৩ মাসের ভাড়া বকেয়া...';
  const btnGenNotice = document.getElementById('btn-generate-notice-submit');
  if (btnGenNotice) btnGenNotice.innerHTML = isEn ? '<i class="fa-solid fa-file-pen"></i> Generate Professional Legal Notice' : '<i class="fa-solid fa-file-pen"></i> প্রফেশনাল আইনি নোটিশ তৈরি করুন';
  const btnCloseNotice = document.getElementById('btn-close-notice-footer');
  if (btnCloseNotice) btnCloseNotice.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 17. Modals: SHA-256 Tamper Verification
  const verifyH3 = document.querySelector('#verify-modal h3');
  if (verifyH3) verifyH3.innerHTML = isEn ? '<i class="fa-solid fa-fingerprint"></i> SHA-256 Cryptographic Hash & Verification' : '<i class="fa-solid fa-fingerprint"></i> SHA-256 ক্রিপ্টোগ্রাফিক হ্যাশ ও প্রমাণিকতা যাচাই';
  const verifyDesc = document.querySelector('#verify-modal .modal-body p');
  if (verifyDesc) verifyDesc.textContent = isEn 
    ? 'Each document generates a unique cryptographic hash. If a single character is altered after signing, this hash immediately changes.' 
    : 'প্রতিটি দলিলের জন্য একটি অনন্য গাণিতিক হ্যাশ তৈরি হয়। চুক্তি স্বাক্ষরের পর কোনো একটি অক্ষরও পরিবর্তন হলে এই হ্যাশ পরিবর্তিত হয়ে যায়।';
  const verifyHashInput = document.getElementById('verify-hash-input');
  if (verifyHashInput) verifyHashInput.placeholder = isEn ? 'e.g. e3b0c44298fc1c149afbf4c8996fb92427ae...' : 'যেমন: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
  const btnRunVerify = document.getElementById('btn-run-verify-submit');
  if (btnRunVerify) btnRunVerify.innerHTML = isEn ? '<i class="fa-solid fa-shield-halved"></i> Verify Document Authenticity' : '<i class="fa-solid fa-shield-halved"></i> দলিলের প্রমাণিকতা যাচাই করুন';
  const btnCloseVerify = document.getElementById('btn-close-verify-footer');
  if (btnCloseVerify) btnCloseVerify.textContent = isEn ? 'Close' : 'বন্ধ করুন';

  // 18. Refresh Active Step & Form Fields
  const activeTab = document.querySelector('.step-tab.active');
  const currentStep = activeTab ? activeTab.getAttribute('data-step') : 1;
  switchStep(currentStep);

  renderFormFields();
  renderCustomClausesList();
  triggerDocumentRender();
}

function setupTemplate(docType, loadedData = null) {
  state.currentTemplate = docType;
  state.isViewingNotice = false;
  
  if (loadedData) {
    state.formData = loadedData;
    state.customClauses = loadedData.custom_clauses || [];
  } else {
    const isEn = state.currentLang === 'en';
    const sourceData = (isEn && sampleContractsData_en[docType])
      ? sampleContractsData_en[docType]
      : sampleContractsData[docType];
    if (sourceData) {
      state.formData = JSON.parse(JSON.stringify(sourceData));
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
  const def = formDefinitions[state.currentTemplate] || formDefinitions.tenancy_agreement;

  const buildFields = (fields) => {
    return fields.map(f => {
      const val = state.formData[f.id] || '';
      const label = (state.currentLang === 'en' && f.label_en) ? f.label_en : f.label;
      if (f.type === 'textarea') {
        return `
          <div class="form-group">
            <label class="form-label">${label}</label>
            <textarea id="${f.id}" class="form-textarea field-input" data-key="${f.id}" rows="2">${val}</textarea>
          </div>
        `;
      }
      return `
        <div class="form-group">
          <label class="form-label">${label}</label>
          <input type="${f.type}" id="${f.id}" class="form-input field-input" data-key="${f.id}" value="${val}">
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
    step4Container.innerHTML = state.currentLang === 'en'
      ? '<p style="color: #64748b; font-size: 0.9rem;">Separate witness details are not required for this document. Signatures of the primary parties are sufficient.</p>'
      : '<p style="color: #64748b; font-size: 0.9rem;">এই চুক্তির জন্য পৃথক সাক্ষীর ফর্ম প্রযোজ্য নয়। মূল পক্ষদ্বয়ের সরাসরি স্বাক্ষরই যথেষ্ট।</p>';
  }

  document.querySelectorAll('.field-input').forEach(input => {
    input.addEventListener('input', (e) => {
      state.isViewingNotice = false;
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
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_type: state.currentTemplate,
        language: state.currentLang,
        data: state.formData,
        watermark_type: state.watermarkMode,
        show_stamp: state.showStamp
      })
    });
    if (res.ok) {
      const data = await res.json();
      const container = document.getElementById('preview-container');
      container.innerHTML = data.rendered_html;

      const stamp = document.getElementById('stamp-header');
      if (stamp) {
        stamp.style.display = state.showStamp ? 'flex' : 'none';
      }

      attachClauseExplainerButtons();
      applyWatermarkToPreview();
      refreshDocumentHash();
    }
  } catch (err) {
    console.error('Render error:', err);
  }
}

function applyWatermarkToPreview() {
  const container = document.getElementById('preview-container');
  if (!container) return;

  const existingOverlay = container.querySelector('.sla-watermark-overlay');
  if (existingOverlay) existingOverlay.remove();

  if (state.watermarkMode === 'none') return;

  const labels = {
    draft: 'খসড়া • DRAFT COPY',
    confidential: 'গোপনীয় • CONFIDENTIAL'
  };

  const overlay = document.createElement('div');
  overlay.className = 'sla-watermark-overlay';
  overlay.innerText = labels[state.watermarkMode] || 'খসড়া • DRAFT COPY';
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
  const clauses = document.querySelectorAll('#preview-container .clause-item');
  clauses.forEach((cl) => {
    const existingBtn = cl.querySelector('.clause-explain-btn');
    if (!existingBtn) {
      const btn = document.createElement('span');
      btn.className = 'clause-explain-btn';
      btn.innerHTML = '<i class="fa-solid fa-lightbulb"></i> ব্যাখ্যা';
      btn.title = 'ক্লিক করুন: এই ধারাটির সহজ অর্থ ও ঝুঁকি দেখতে';
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openClauseExplainer(cl.innerText);
      });
      cl.appendChild(btn);
    }
  });
}

function renderCustomClausesList() {
  const list = document.getElementById('custom-clauses-list');
  if (state.customClauses.length === 0) {
    list.innerHTML = '<p style="color: #94a3b8; font-size: 0.85rem;">কোনো কাস্টম শর্ত যুক্ত করা হয়নি।</p>';
    return;
  }

  list.innerHTML = state.customClauses.map((c, idx) => `
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <strong style="font-size: 0.85rem; color: #1e3a8a;">${c.title || 'কাস্টম ধারা'}</strong>
        <button class="btn btn-secondary" style="padding: 2px 8px; font-size: 0.75rem; color: #ef4444;" onclick="deleteCustomClause(${idx})">
          <i class="fa-solid fa-trash"></i> মুছে ফেলুন
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
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
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
    e.preventDefault();
  }

  function stopDraw() {
    state.isDrawing = false;
  }

  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('mousemove', draw);
  window.addEventListener('mouseup', stopDraw);

  canvas.addEventListener('touchstart', startDraw, { passive: false });
  canvas.addEventListener('touchmove', draw, { passive: false });
  window.addEventListener('touchend', stopDraw);

  document.getElementById('btn-clear-canvas').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  });

  const targetP1 = document.getElementById('sign-target-p1');
  const targetP2 = document.getElementById('sign-target-p2');

  targetP1.addEventListener('click', () => {
    state.sigTarget = 'p1';
    targetP1.className = 'btn btn-primary';
    targetP2.className = 'btn btn-secondary';
  });

  targetP2.addEventListener('click', () => {
    state.sigTarget = 'p2';
    targetP2.className = 'btn btn-primary';
    targetP1.className = 'btn btn-secondary';
  });

  document.getElementById('btn-apply-signature').addEventListener('click', async () => {
    const dataUrl = canvas.toDataURL('image/png');
    if (state.sigTarget === 'p1') {
      state.formData.party1_signature = dataUrl;
    } else {
      state.formData.party2_signature = dataUrl;
    }

    // If in remote signing mode, submit back to server
    if (state.currentContractId) {
      fetch(`/api/contracts/share/${state.currentContractId}/sign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signature_data: dataUrl, target: state.sigTarget === 'p1' ? 'party1' : 'party2' })
      });
    }

    triggerDocumentRender();
    document.getElementById('sign-modal').style.display = 'none';
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  });
}

// Database History Modal
async function openHistoryModal() {
  const modal = document.getElementById('history-modal');
  const container = document.getElementById('history-list-container');
  modal.style.display = 'flex';
  container.innerHTML = '<p style="text-align: center; color: #0284c7; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> লোড হচ্ছে...</p>';

  try {
    const res = await fetch('/api/contracts');
    const list = await res.json();

    if (list.length === 0) {
      container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 20px;">ডাটাবেসে কোনো সংরক্ষিত চুক্তি নেই।</p>';
      return;
    }

    container.innerHTML = list.map(item => `
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h4 style="color: #0f172a; font-size: 0.95rem; margin-bottom: 4px;">${item.title}</h4>
          <span style="font-size: 0.8rem; color: #64748b;">
            <i class="fa-regular fa-clock"></i> ${item.updated_at} | <strong>${item.document_type}</strong>
          </span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-primary" style="padding: 4px 10px; font-size: 0.8rem;" onclick="loadContractById('${item.id}', '${item.document_type}')">
            <i class="fa-solid fa-folder-open"></i> লোড
          </button>
          <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.8rem; color: #ef4444;" onclick="deleteContractById('${item.id}')">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<p style="color: #ef4444;">হিস্ট্রি লোড করতে ব্যর্থ হয়েছে।</p>';
  }
}

window.loadContractById = async function(id, docType) {
  try {
    const res = await fetch(`/api/contracts/${id}`);
    const item = await res.json();
    state.currentContractId = item.id;
    if (item.language) {
      state.currentLang = item.language;
      const langSel = document.getElementById('lang-select');
      if (langSel) langSel.value = item.language;
      updateUILanguage(item.language);
    }
    document.getElementById('template-select').value = item.document_type;
    setupTemplate(item.document_type, item.data);
    document.getElementById('history-modal').style.display = 'none';
    showToast('চুক্তিটি সফলভাবে লোড করা হয়েছে!', 'success');
  } catch (err) {
    showToast('চুক্তি লোড করতে ব্যর্থ হয়েছে: ' + err.message, 'error');
  }
};

window.deleteContractById = async function(id) {
  if (!confirm('আপনি কি নিশ্চিত এই চুক্তিটি মুছে ফেলতে চান?')) return;
  try {
    await fetch(`/api/contracts/${id}`, { method: 'DELETE' });
    showToast('চুক্তিটি মুছে ফেলা হয়েছে।', 'info');
    openHistoryModal();
  } catch (err) {
    showToast('মুছতে ব্যর্থ হয়েছে: ' + err.message, 'error');
  }
};

async function openClauseExplainer(clauseText) {
  const modal = document.getElementById('explainer-modal');
  const content = document.getElementById('explainer-content');
  modal.style.display = 'flex';
  const isEn = state.currentLang === 'en';
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
        <h4 style="color: #1e3a8a; margin-bottom: 6px; font-size: 0.95rem;">${isEn ? 'Plain Summary:' : 'সহজ সারসংক্ষেপ:'}</h4>
        <p style="font-size: 0.92rem; color: #1e293b; line-height: 1.6;">${data.simple_explanation}</p>
      </div>
      <div style="margin-bottom: 16px;">
        <h4 style="color: #0f172a; margin-bottom: 8px; font-size: 0.9rem;"><i class="fa-solid fa-circle-check" style="color: #10b981;"></i> ${isEn ? 'Key Obligations:' : 'মূল দায়িত্ব:'}</h4>
        <ul style="padding-left: 20px; font-size: 0.88rem; color: #334155;">
          ${(data.key_obligations || []).map(o => `<li style="margin-bottom: 4px;">${o}</li>`).join('')}
        </ul>
      </div>
      <div>
        <h4 style="color: #b91c1c; margin-bottom: 8px; font-size: 0.9rem;"><i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i> ${isEn ? 'Potential Risks:' : 'সম্ভাব্য ঝুঁকি:'}</h4>
        <ul style="padding-left: 20px; font-size: 0.88rem; color: #7f1d1d;">
          ${(data.potential_risks || []).map(r => `<li style="margin-bottom: 4px;">${r}</li>`).join('')}
        </ul>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<p style="color: #ef4444;">${isEn ? 'Failed to load AI explanation.' : 'AI ব্যাখ্যা লোড করতে ব্যর্থ হয়েছে।'}</p>`;
  }
}

function switchStep(stepNum) {
  stepNum = parseInt(stepNum, 10);
  if (isNaN(stepNum) || stepNum < 1 || stepNum > 4) return;

  document.querySelectorAll('.step-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.step-content').forEach(c => c.style.display = 'none');

  const activeTab = document.querySelector(`.step-tab[data-step="${stepNum}"]`);
  if (activeTab) activeTab.classList.add('active');

  const stepEl = document.getElementById(`step-${stepNum}`);
  if (stepEl) stepEl.style.display = 'block';

  // Update progress bar
  const percent = stepNum * 25;
  const isEn = state.currentLang === 'en';
  const stepTitles = isEn ? {
    1: 'Parties Information',
    2: 'Core Terms & Conditions',
    3: 'AI Custom Clauses',
    4: 'Signatures & Finish'
  } : {
    1: 'পক্ষের তথ্য',
    2: 'মূল শর্তাবলি',
    3: 'AI কাস্টম ধারা',
    4: 'স্বাক্ষর ও সমাপ্তি'
  };
  const progText = document.getElementById('wizard-progress-text');
  const progPct = document.getElementById('wizard-progress-percent');
  const progFill = document.getElementById('wizard-progress-fill');
  if (progText) progText.innerText = isEn 
    ? `Step ${stepNum} / 4 : ${stepTitles[stepNum]} (${percent}% completed)`
    : `ধাপ ${stepNum} / ৪ : ${stepTitles[stepNum]} (${percent}% সম্পন্ন)`;
  if (progPct) progPct.innerText = `${percent}%`;
  if (progFill) progFill.style.width = `${percent}%`;

  const scrollContainer = document.querySelector('.form-scroll-container');
  if (scrollContainer) scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
}

function attachEvents() {
  document.querySelectorAll('.step-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      switchStep(tab.getAttribute('data-step'));
    });
  });

  document.querySelectorAll('.btn-next-step').forEach(btn => {
    btn.addEventListener('click', () => {
      switchStep(btn.getAttribute('data-target'));
    });
  });

  document.querySelectorAll('.btn-prev-step').forEach(btn => {
    btn.addEventListener('click', () => {
      switchStep(btn.getAttribute('data-target'));
    });
  });

  const btnFinishSave = document.getElementById('btn-finish-save');
  if (btnFinishSave) {
    btnFinishSave.addEventListener('click', () => {
      document.getElementById('btn-save-draft').click();
    });
  }

  // 1-Click Demo Fill
  const btnDemoFill = document.getElementById('btn-demo-fill');
  if (btnDemoFill) {
    btnDemoFill.addEventListener('click', () => {
      const isEn = state.currentLang === 'en';
      const demoData = (isEn && sampleContractsData_en[state.currentTemplate]) 
        ? sampleContractsData_en[state.currentTemplate] 
        : sampleContractsData[state.currentTemplate];
      if (!demoData) return;
      state.formData = { ...state.formData, ...demoData };
      renderFormFields();
      triggerDocumentRender();
      showToast(isEn ? '✨ Realistic English demo data filled successfully!' : '✨ নমুনা বাস্তবসম্মত তথ্য সফলভাবে পূরণ করা হয়েছে!', 'success');
    });
  }

  // Dropdown menus toggle & outside click
  document.querySelectorAll('.dropdown').forEach(dd => {
    const toggle = dd.querySelector('.dropdown-toggle');
    if (toggle) {
      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        document.querySelectorAll('.dropdown').forEach(other => {
          if (other !== dd) other.classList.remove('active');
        });
        dd.classList.toggle('active');
      });
    }
  });

  window.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown')) {
      document.querySelectorAll('.dropdown').forEach(dd => dd.classList.remove('active'));
    }
  });

  // AI Prompt Suggestion Chips in Step 3
  document.querySelectorAll('.prompt-chip[data-prompt]').forEach(chip => {
    chip.addEventListener('click', () => {
      const input = document.getElementById('ai-clause-input');
      if (input) {
        input.value = chip.getAttribute('data-prompt');
        input.focus();
        showToast('ধারাটি ইনপুটে যুক্ত করা হয়েছে', 'info', 1800);
      }
    });
  });

  // Chatbot Suggestion Chips
  document.querySelectorAll('.chat-suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-query');
      const input = document.getElementById('chat-input');
      if (input && q) {
        input.value = q;
        const sendBtn = document.getElementById('btn-chat-send');
        if (sendBtn) sendBtn.click();
      }
    });
  });

  // Preview Zoom & Fullscreen Controls
  const updateZoom = (newZoom) => {
    state.zoomLevel = Math.max(0.6, Math.min(1.5, Math.round(newZoom * 10) / 10));
    const wrapper = document.getElementById('preview-wrapper');
    const levelText = document.getElementById('zoom-level-text');
    if (wrapper) wrapper.style.transform = `scale(${state.zoomLevel})`;
    if (levelText) levelText.innerText = `${Math.round(state.zoomLevel * 100)}%`;
  };

  const btnZoomIn = document.getElementById('btn-zoom-in');
  const btnZoomOut = document.getElementById('btn-zoom-out');
  const btnZoomReset = document.getElementById('btn-zoom-reset');
  if (btnZoomIn) btnZoomIn.addEventListener('click', () => updateZoom(state.zoomLevel + 0.1));
  if (btnZoomOut) btnZoomOut.addEventListener('click', () => updateZoom(state.zoomLevel - 0.1));
  if (btnZoomReset) btnZoomReset.addEventListener('click', () => updateZoom(1.0));

  const btnFsReader = document.getElementById('btn-fullscreen-reader');
  if (btnFsReader) {
    btnFsReader.addEventListener('click', () => {
      const isFs = document.body.classList.toggle('reader-fullscreen-active');
      btnFsReader.innerHTML = isFs ? '<i class="fa-solid fa-compress"></i>' : '<i class="fa-solid fa-expand"></i>';
      if (isFs) {
        showToast('পূর্ণাঙ্গ পেপার রিডিং মোড চালু হয়েছে (Esc চাপুন বন্ধ করতে)', 'info', 2500);
      }
    });
  }

  // Mobile View Switcher (Tabs)
  const btnMobWizard = document.getElementById('btn-mobile-tab-wizard');
  const btnMobPreview = document.getElementById('btn-mobile-tab-preview');
  if (btnMobWizard && btnMobPreview) {
    btnMobWizard.addEventListener('click', () => {
      btnMobWizard.classList.add('active');
      btnMobPreview.classList.remove('active');
      document.body.classList.remove('mobile-hide-wizard');
      document.body.classList.add('mobile-hide-preview');
    });
    btnMobPreview.addEventListener('click', () => {
      btnMobPreview.classList.add('active');
      btnMobWizard.classList.remove('active');
      document.body.classList.remove('mobile-hide-preview');
      document.body.classList.add('mobile-hide-wizard');
    });
  }

  document.getElementById('template-select').addEventListener('change', (e) => {
    state.currentContractId = null;
    setupTemplate(e.target.value);
  });

  document.getElementById('lang-select').addEventListener('change', (e) => {
    state.currentLang = e.target.value;
    updateUILanguage(state.currentLang);
    triggerDocumentRender();
  });

  // Direct Edit Mode
  const btnToggleEdit = document.getElementById('btn-toggle-edit');
  const previewContainer = document.getElementById('preview-container');
  const editLabel = document.getElementById('edit-mode-label');

  btnToggleEdit.addEventListener('click', () => {
    state.isDirectEdit = !state.isDirectEdit;
    previewContainer.contentEditable = state.isDirectEdit ? 'true' : 'false';
    if (state.isDirectEdit) {
      previewContainer.style.outline = '2px dashed #2563eb';
      btnToggleEdit.style.background = '#dbeafe';
      btnToggleEdit.style.color = '#1d4ed8';
      editLabel.innerText = '✅ এডিট মোড চলছে';
    } else {
      previewContainer.style.outline = 'none';
      btnToggleEdit.style.background = '';
      btnToggleEdit.style.color = '';
      editLabel.innerText = 'সরাসরি পেপারে এডিট';
    }
  });

  // Toggle 300 Tk Stamp
  document.getElementById('btn-toggle-stamp').addEventListener('click', () => {
    state.showStamp = !state.showStamp;
    const stamp = document.getElementById('stamp-header');
    if (stamp) {
      stamp.style.display = state.showStamp ? 'flex' : 'none';
    }
  });

  // Stamp Duty Calculator Modal
  document.getElementById('btn-open-stamp-calc').addEventListener('click', () => {
    document.getElementById('stamp-calc-modal').style.display = 'flex';
  });

  document.getElementById('btn-run-stamp-calc').addEventListener('click', async () => {
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
          <strong style="color:#9a3412;">প্রয়োজনীয় স্ট্যাম্প ডিউটি:</strong>
          <span style="font-size:1.3rem; font-weight:800; color:#c2410c;">${data.formatted_stamp}</span>
        </div>
        <p style="font-size:0.86rem; color:#7c2d12; margin-bottom:6px;">${data.explanation}</p>
        <span style="font-size:0.8rem; color:#64748b;"><strong>আইনি রেফারেন্স:</strong> ${data.legal_basis}</span>
        ${data.is_registration_mandatory ? '<div style="margin-top:8px; padding:6px 8px; background:#fee2e2; color:#991b1b; border-radius:4px; font-size:0.8rem; font-weight:bold;">⚠️ ১ বছরের অধিক হওয়ায় সাব-রেজিস্ট্রি অফিসে রেজিস্ট্রেশন বাধ্যতামূলক।</div>' : ''}
      `;
    } catch (e) {
      showToast('স্ট্যাম্প হিসাব করতে ব্যর্থ হয়েছে।', 'error');
    }
  });

  // Share & Remote Signing Modal
  document.getElementById('btn-share-contract').addEventListener('click', async () => {
    // If not yet saved to DB, save now to generate ID
    if (!state.currentContractId) {
      state.formData.custom_clauses = state.customClauses;
      const currentMeta = state.templates.find(t => t.id === state.currentTemplate);
      const title = `${currentMeta ? currentMeta.title_bn : 'চুক্তিপত্র'} - ${new Date().toLocaleDateString('bn-BD')}`;
      const res = await fetch('/api/contracts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: null,
          title: title,
          document_type: state.currentTemplate,
          language: state.currentLang,
          data: state.formData
        })
      });
      const resData = await res.json();
      state.currentContractId = resData.id;
    }

    const shareUrl = `${window.location.origin}/?share_id=${state.currentContractId}`;
    document.getElementById('share-url-input').value = shareUrl;
    document.getElementById('btn-whatsapp-share').href = `https://api.whatsapp.com/send?text=${encodeURIComponent('SmartLegal AI এর মাধ্যমে আপনার চুক্তিপত্রে স্বাক্ষরের আমন্ত্রণ: ' + shareUrl)}`;
    document.getElementById('share-modal').style.display = 'flex';
  });

  document.getElementById('btn-copy-share-url').addEventListener('click', () => {
    const input = document.getElementById('share-url-input');
    input.select();
    navigator.clipboard.writeText(input.value);
    showToast('শেয়ারিং লিংক ক্লিপবোর্ডে কপি করা হয়েছে!', 'success');
    const btn = document.getElementById('btn-copy-share-url');
    btn.innerHTML = '<i class="fa-solid fa-check"></i> কপিড!';
    setTimeout(() => { btn.innerHTML = '<i class="fa-solid fa-copy"></i> কপি'; }, 1500);
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
    const q = chatInput.value.trim();
    if (!q) return;

    const cleanQ = escapeHtml(q);
    chatBody.innerHTML += `<div class="chat-bubble-user">${cleanQ}</div>`;
    chatInput.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    const loaderId = 'loader_' + Date.now();
    chatBody.innerHTML += `<div class="chat-bubble-ai" id="${loaderId}"><i class="fa-solid fa-spinner fa-spin"></i> আইনAI লিখছে...</div>`;
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
        loader.innerHTML = escapeHtml(data.answer).replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      }
      chatBody.scrollTop = chatBody.scrollHeight;
    } catch (e) {
      const loader = document.getElementById(loaderId);
      if (loader) loader.innerHTML = 'উত্তর পেতে সমস্যা হয়েছে।';
    }
  };

  chatSend.addEventListener('click', sendChatMessage);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChatMessage();
  });

  // History & Sign buttons
  document.getElementById('btn-history').addEventListener('click', openHistoryModal);
  const openSign = () => { document.getElementById('sign-modal').style.display = 'flex'; };
  document.getElementById('btn-open-sign').addEventListener('click', openSign);
  const step4SignBtn = document.getElementById('btn-step4-sign');
  if (step4SignBtn) step4SignBtn.addEventListener('click', openSign);

  // Upload Audit
  document.getElementById('btn-upload-audit').addEventListener('click', () => {
    document.getElementById('upload-modal').style.display = 'flex';
  });

  document.getElementById('upload-file-input').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => { document.getElementById('upload-text-input').value = evt.target.result; };
      reader.readAsText(file);
    }
  });

  document.getElementById('btn-run-upload-audit').addEventListener('click', async () => {
    const text = document.getElementById('upload-text-input').value.trim();
    if (!text) return showToast('অনুগ্রহ করে টেক্সট বা ফাইল প্রদান করুন।', 'warning');

    const btn = document.getElementById('btn-run-upload-audit');
    const oldText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> অডিট চলছে...';
    btn.disabled = true;

    try {
      const res = await fetch('/api/ai/audit-upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: text, filename: 'Uploaded_Contract.txt' })
      });
      const data = await res.json();
      const resContainer = document.getElementById('upload-audit-result');
      resContainer.style.display = 'block';

      resContainer.innerHTML = `
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <strong style="color: #1e3a8a;">${data.detected_type}</strong>
            <span class="badge ${data.score >= 80 ? 'badge-low' : 'badge-medium'}">নিরাপত্তা স্কোর: ${data.score}/100</span>
          </div>
          <p style="font-size: 0.88rem; color: #334155;">${data.summary}</p>
        </div>
        <h4 style="font-size: 0.9rem; color: #0f172a; margin-bottom: 8px;">চিহ্নিত ঝুঁকিপূর্ণ শর্ত:</h4>
        ${data.risks_found.map(r => `
          <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px; border-radius: 0 6px 6px 0; margin-bottom: 8px;">
            <strong style="font-size: 0.85rem; color: #991b1b;">${r.clause_topic}</strong>
            <p style="font-size: 0.82rem; color: #7f1d1d; margin: 4px 0;">${r.issue}</p>
            <span style="font-size: 0.8rem; color: #1e40af;"><strong>পরামর্শ:</strong> ${r.recommendation}</span>
          </div>
        `).join('')}
      `;
      showToast('ডকুমেন্ট অডিট সম্পন্ন হয়েছে!', 'success');
    } catch (err) {
      showToast('অডিট করতে সমস্যা হয়েছে।', 'error');
    } finally {
      btn.innerHTML = oldText;
      btn.disabled = false;
    }
  });

  // Save Contract to SQLite Database
  document.getElementById('btn-save-draft').addEventListener('click', async () => {
    state.formData.custom_clauses = state.customClauses;
    const currentMeta = state.templates.find(t => t.id === state.currentTemplate);
    const title = `${currentMeta ? currentMeta.title_bn : 'চুক্তিপত্র'} - ${new Date().toLocaleDateString('bn-BD')}`;

    try {
      const res = await fetch('/api/contracts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: state.currentContractId,
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
      btn.innerHTML = '<i class="fa-solid fa-check" style="color: #10b981;"></i> সেভ হয়েছে!';
      setTimeout(() => { btn.innerHTML = oldText; }, 2000);
      showToast('চুক্তিটি ডেটাবেসে সফলভাবে সংরক্ষিত হয়েছে!', 'success');
    } catch (err) {
      showToast('ডাটাবেসে সেভ করতে সমস্যা হয়েছে।', 'error');
    }
  });

  // AI Refine Clause Button
  document.getElementById('btn-refine-clause').addEventListener('click', async () => {
    const rawInput = document.getElementById('ai-clause-input').value.trim();
    if (!rawInput) return showToast('অনুগ্রহ করে শর্তটি লিখুন।', 'warning');

    const btn = document.getElementById('btn-refine-clause');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> AI পলিশ করছে...';
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
        document.getElementById('ai-res-title').innerText = data.title || 'বিশেষ ধারা';
        document.getElementById('ai-res-risk').innerText = (data.risk_level || 'Low') + ' Risk';
        document.getElementById('ai-res-text').innerText = data.refined_clause;
        document.getElementById('ai-clause-result').style.display = 'block';
        showToast('ধারাটি আইনি ভাষায় পলিশ করা হয়েছে!', 'success');
      }
    } catch (err) {
      showToast('AI রূপান্তর করতে ব্যর্থ হয়েছে।', 'error');
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

  // Universal Modal Closers
  const allModals = ['explainer-modal', 'sign-modal', 'history-modal', 'upload-modal', 'stamp-calc-modal', 'share-modal', 'notice-modal', 'verify-modal'];
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

  // PDF Export
  document.getElementById('btn-pdf').addEventListener('click', async () => {
    if (state.isViewingNotice) {
      window.print();
      return;
    }

    const btn = document.getElementById('btn-pdf');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> তৈরি হচ্ছে...';
    btn.disabled = true;

    try {
      const res = await fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: state.currentTemplate,
          language: state.currentLang,
          data: state.formData,
          watermark_type: state.watermarkMode,
          show_stamp: state.showStamp
        })
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${state.currentTemplate}_verified.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('PDF সফলভাবে ডাউনলোড হয়েছে!', 'success');
      } else {
        showToast('PDF তৈরি করতে সমস্যা হয়েছে।', 'error');
      }
    } catch (err) {
      showToast('PDF ডাউনলোড ব্যর্থ হয়েছে: ' + err.message, 'error');
    } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  });

  // Word DOCX Export
  document.getElementById('btn-docx').addEventListener('click', async () => {
    const btn = document.getElementById('btn-docx');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Word তৈরি হচ্ছে...';
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
        showToast('Word ফাইল সফলভাবে ডাউনলোড হয়েছে!', 'success');
      } else {
        showToast('Word ফাইল তৈরি করতে সমস্যা হয়েছে।', 'error');
      }
    } catch (err) {
      showToast('DOCX ডাউনলোড ব্যর্থ হয়েছে: ' + err.message, 'error');
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
      if (state.watermarkMode === 'none') {
        state.watermarkMode = 'draft';
        if (watermarkLabel) watermarkLabel.innerText = 'ওয়াটারমার্ক: খসড়া';
        btnWatermark.style.background = '#fee2e2';
        btnWatermark.style.color = '#dc2626';
      } else if (state.watermarkMode === 'draft') {
        state.watermarkMode = 'confidential';
        if (watermarkLabel) watermarkLabel.innerText = 'ওয়াটারমার্ক: গোপনীয়';
        btnWatermark.style.background = '#fef3c7';
        btnWatermark.style.color = '#d97706';
      } else {
        state.watermarkMode = 'none';
        if (watermarkLabel) watermarkLabel.innerText = 'ওয়াটারমার্ক: বন্ধ';
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
      const landlord = state.formData.landlord_name || state.formData.company_name || state.formData.partner1_name || state.formData.client_name || state.formData.disclosing_party_name || '';
      const tenant = state.formData.tenant_name || state.formData.employee_name || state.formData.partner2_name || state.formData.freelancer_name || state.formData.receiving_party_name || '';
      const address = state.formData.property_address || state.formData.landlord_address || state.formData.company_address || state.formData.firm_address || '';

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
      const noticeType = document.getElementById('notice-type-select').value;
      const landlord = document.getElementById('notice-landlord').value;
      const tenant = document.getElementById('notice-tenant').value;
      const address = document.getElementById('notice-address').value;
      const reason = document.getElementById('notice-reason').value;

      const originalBtnText = btnGenerateNoticeSubmit.innerHTML;
      btnGenerateNoticeSubmit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> নোটিশ তৈরি হচ্ছে...';
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
              rent_amount: state.formData.rent_amount || '15,000',
              landlord_phone: state.formData.landlord_phone || '০১XXXXXXXXX'
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
          showToast('আইনি নোটিশ সফলভাবে তৈরি হয়েছে!', 'success');
        } else {
          showToast('নোটিশ তৈরি করতে সমস্যা হয়েছে।', 'error');
        }
      } catch (err) {
        showToast('ত্রুটি: ' + err.message, 'error');
      } finally {
        btnGenerateNoticeSubmit.innerHTML = originalBtnText;
        btnGenerateNoticeSubmit.disabled = false;
      }
    });
  }

  if (btnCopyNotice) {
    btnCopyNotice.addEventListener('click', () => {
      if (!lastGeneratedNotice) return;
      navigator.clipboard.writeText(lastGeneratedNotice.body).then(() => {
        showToast('আইনি নোটিশ ক্লিপবোর্ডে কপি হয়েছে!', 'success');
        btnCopyNotice.innerHTML = '<i class="fa-solid fa-check"></i> কপি হয়েছে!';
        setTimeout(() => {
          btnCopyNotice.innerHTML = '<i class="fa-solid fa-copy"></i> কপি';
        }, 1800);
      });
    });
  }

  if (btnInjectNotice) {
    btnInjectNotice.addEventListener('click', () => {
      if (!lastGeneratedNotice) return;
      state.isViewingNotice = true;
      const safeTitle = escapeHtml(lastGeneratedNotice.title);
      const safeSubject = escapeHtml(lastGeneratedNotice.subject);
      const safeBody = escapeHtml(lastGeneratedNotice.body);
      const safeDate = escapeHtml(lastGeneratedNotice.date);
      const container = document.getElementById('preview-container');
      container.innerHTML = '<div style="font-family: Hind Siliguri, sans-serif; padding: 20px; line-height: 1.8; color: #0f172a;"><div style="border-bottom: 2px solid #991b1b; padding-bottom: 8px; margin-bottom: 20px; text-align: center;"><h2 style="font-size: 18pt; color: #991b1b; margin: 0;">' + safeTitle + '</h2><div style="font-size: 11pt; color: #475569; margin-top: 4px;">আইনি ও প্রথাগত উচ্ছেদ/নবায়ন নোটিশ</div></div><div style="font-weight: 700; color: #1e3a8a; margin-bottom: 14px;">' + safeSubject + '</div><div style="white-space: pre-wrap; font-size: 13pt; color: #1e293b;">' + safeBody + '</div><div style="margin-top: 30px; border-top: 1px dashed #cbd5e1; padding-top: 10px; font-size: 9pt; color: #64748b; text-align: center;">SmartLegal AI Notice Engine • প্রস্তুতের তারিখ: ' + safeDate + '</div></div>';
      noticeModal.style.display = 'none';
      applyWatermarkToPreview();
      refreshDocumentHash();
      showToast('আইনি নোটিশ প্রিভিউতে প্রদর্শিত হচ্ছে', 'info');
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
      const expectedHash = document.getElementById('verify-hash-input').value.trim();
      if (!expectedHash) {
        showToast('অনুগ্রহ করে রেফারেন্স হ্যাশ কোড ইনপুট দিন।', 'warning');
        return;
      }

      const container = document.getElementById('preview-container');
      const currentContent = container ? container.innerText : '';

      btnRunVerifySubmit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> যাচাই হচ্ছে...';
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
            verifyResultBox.innerHTML = '<div style="background: #ecfdf5; border: 1.5px solid #10b981; border-radius: 8px; padding: 14px; color: #065f46;"><div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; margin-bottom: 6px;"><i class="fa-solid fa-circle-check" style="color: #10b981; font-size: 1.2rem;"></i> দলিলটি ১০০% অবিকৃত ও খাঁটি (AUTHENTIC & UN-TAMPERED)</div><p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">ক্রিপ্টোগ্রাফিক হ্যাশ শতভাগ মিলে গেছে। স্বাক্ষরের পর দলিলে কোনো কাটছাঁট বা অবৈধ পরিবর্তন করা হয়নি।</p><div style="margin-top: 8px; font-family: monospace; font-size: 0.78rem; color: #047857;">Computed Hash: ' + result.computed_hash + '</div></div>';
            showToast('দলিলটি ১০০% অবিকৃত ও খাঁটি!', 'success');
          } else {
            verifyResultBox.innerHTML = '<div style="background: #fef2f2; border: 1.5px solid #ef4444; border-radius: 8px; padding: 14px; color: #991b1b;"><div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; margin-bottom: 6px;"><i class="fa-solid fa-triangle-exclamation" style="color: #ef4444; font-size: 1.2rem;"></i> সতর্কতা: দলিলটি বিকৃত বা পরিবর্তিত (TAMPERED / MODIFIED)</div><p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">প্রদত্ত রেফারেন্স হ্যাশের সাথে বর্তমান দলিলের হ্যাশ মেলেনি। মূল ডকুমেন্টের তথ্য বিকৃত বা পরিবর্তন করা হয়েছে।</p><div style="margin-top: 8px; font-family: monospace; font-size: 0.78rem; color: #b91c1c;">Current Hash: ' + result.computed_hash + '</div></div>';
            showToast('সতর্কতা: দলিলটিতে তথ্য পরিবর্তন পাওয়া গেছে!', 'error');
          }
        } else {
          showToast('হ্যাশ যাচাই করতে ব্যর্থ হয়েছে।', 'error');
        }
      } catch (err) {
        showToast('ত্রুটি: ' + err.message, 'error');
      } finally {
        btnRunVerifySubmit.innerHTML = '<i class="fa-solid fa-shield-halved"></i> দলিলের প্রমাণিকতা যাচাই করুন';
        btnRunVerifySubmit.disabled = false;
      }
    });
  }

  // Global Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      const btnSave = document.getElementById('btn-save-draft');
      if (btnSave) btnSave.click();
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'p') {
      e.preventDefault();
      const btnPdf = document.getElementById('btn-pdf');
      if (btnPdf) btnPdf.click();
    }
    if (e.key === 'Escape') {
      if (document.body.classList.contains('reader-fullscreen-active')) {
        document.body.classList.remove('reader-fullscreen-active');
        const fsBtn = document.getElementById('btn-fullscreen-reader');
        if (fsBtn) fsBtn.innerHTML = '<i class="fa-solid fa-expand"></i>';
      }
      document.querySelectorAll('.dropdown').forEach(dd => dd.classList.remove('active'));
      const chatbotWin = document.getElementById('chatbot-window');
      if (chatbotWin) chatbotWin.style.display = 'none';
      closeAllModals();
    }
  });

}

window.addEventListener('DOMContentLoaded', initApp);
