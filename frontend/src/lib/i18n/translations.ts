/**
 * All UI copy for both supported languages (English / Bahasa Melayu).
 * Pure data — no React/context logic lives here. See LanguageProvider.tsx
 * for the context that consumes this dictionary.
 */
export type Lang = "en" | "bm";

export const t = {
  nav_login: { en: "Login", bm: "Log Masuk" },
  nav_get_started: { en: "Get Started", bm: "Mula Sekarang" },
  nav_logout: { en: "Logout", bm: "Log Keluar" },
  nav_admin: { en: "Admin", bm: "Admin" },

  hero_badge: { en: "AI-Powered Compliance Assistant", bm: "Pembantu Kepatuhan Berkuasa AI" },
  hero_title: {
    en: "Understand Malaysian Business Laws. Without the Jargon.",
    bm: "Faham Undang-Undang Perniagaan Malaysia. Tanpa Kerumitan.",
  },
  hero_sub: {
    en: "MyKepatuhan turns complex government regulations — from SSM to KKM to local municipal bylaws — into simple, step-by-step answers. Grounded in verified documents. Cited every time.",
    bm: "MyKepatuhan tukarkan peraturan kerajaan yang kompleks — dari SSM hingga KKM hingga undang-undang pihak berkuasa tempatan — kepada jawapan mudah langkah demi langkah. Berdasarkan dokumen yang disahkan. Dipetik setiap masa.",
  },
  cta_start: { en: "Start For Free", bm: "Mula Percuma" },
  cta_how: { en: "See How It Works", bm: "Lihat Cara Berfungsi" },
  trust_line: {
    en: "Free to use · No legal background required · Answers in English & BM",
    bm: "Percuma · Tiada latar belakang undang-undang diperlukan · Jawapan dalam BI & BM",
  },
  stat_docs: { en: "Official documents indexed", bm: "Dokumen rasmi diindeks" },
  stat_authorities: { en: "Government authorities", bm: "Pihak berkuasa kerajaan" },
  stat_answers: { en: "Cited answers delivered", bm: "Jawapan dengan rujukan" },
  mock_q: { en: "How do I register an Sdn Bhd?", bm: "Bagaimana saya mendaftar Sdn Bhd?" },
  mock_a: {
    en: "1. Reserve a company name with SSM via MyCoID.\n2. Prepare your Superform (Section 14) and pay RM1,010.\n3. Receive your Notice of Registration — usually within 1 business day.",
    bm: "1. Tempah nama syarikat dengan SSM melalui MyCoID.\n2. Sediakan Superform (Seksyen 14) dan bayar RM1,010.\n3. Terima Notis Pendaftaran — biasanya dalam 1 hari bekerja.",
  },
  mock_cite: { en: "Sourced from SSM Companies Act 2016", bm: "Sumber: Akta Syarikat SSM 2016" },

  how_title: { en: "How It Works", bm: "Cara Ia Berfungsi" },
  how_1: { en: "We ingest official government documents", bm: "Kami muatkan dokumen kerajaan rasmi" },
  how_2: { en: "You ask in plain language", bm: "Anda bertanya dalam bahasa biasa" },
  how_3: { en: "Get cited, step-by-step answers", bm: "Dapatkan jawapan langkah demi langkah dengan rujukan" },

  who_title: { en: "Built for Malaysian Entrepreneurs", bm: "Dibina untuk Usahawan Malaysia" },
  who_1_t: { en: "New Business Owners", bm: "Pemilik Perniagaan Baharu" },
  who_1_d: { en: "Cut through the maze of SSM, licensing and tax registrations on day one.", bm: "Lalui kerumitan pendaftaran SSM, lesen dan cukai dari hari pertama." },
  who_2_t: { en: "F&B / Retail Operators", bm: "Pengusaha F&B / Runcit" },
  who_2_d: { en: "Know exactly which health, halal and municipal approvals you need before opening.", bm: "Ketahui kelulusan kesihatan, halal dan majlis tempatan yang anda perlukan sebelum dibuka." },
  who_3_t: { en: "Freelancers & Sole Proprietors", bm: "Pekerja Bebas & Pemilik Tunggal" },
  who_3_d: { en: "Stay compliant on income tax, SST and ROB renewals without a lawyer on retainer.", bm: "Patuhi cukai pendapatan, SST dan pembaharuan ROB tanpa peguam tetap." },

  auth_title: { en: "Documents We Cover", bm: "Dokumen Yang Kami Liputi" },
  auth_note: { en: "Sourced directly from official government portals", bm: "Diambil terus dari portal kerajaan rasmi" },

  footer_disclaimer: {
    en: "MyKepatuhan provides informational summaries only. This is not legal advice.",
    bm: "MyKepatuhan menyediakan ringkasan maklumat sahaja. Ini bukan nasihat undang-undang.",
  },

  // Auth pages
  login_title: { en: "Welcome back", bm: "Selamat kembali" },
  login_sub: { en: "Sign in to your account to continue", bm: "Log masuk untuk teruskan" },
  login_email: { en: "Email", bm: "E-mel" },
  login_password: { en: "Password", bm: "Kata Laluan" },
  login_submit: { en: "Sign in", bm: "Log Masuk" },
  login_no_account: { en: "Don't have an account?", bm: "Belum ada akaun?" },
  login_register_link: { en: "Create one", bm: "Daftar sekarang" },
  login_error: { en: "Incorrect email or password.", bm: "E-mel atau kata laluan salah." },

  register_title: { en: "Create your account", bm: "Cipta akaun anda" },
  register_sub: { en: "Free to use. No credit card required.", bm: "Percuma. Tiada kad kredit diperlukan." },
  register_name: { en: "Full Name", bm: "Nama Penuh" },
  register_email: { en: "Email", bm: "E-mel" },
  register_password: { en: "Password", bm: "Kata Laluan" },
  register_confirm: { en: "Confirm Password", bm: "Sahkan Kata Laluan" },
  register_submit: { en: "Create Account", bm: "Cipta Akaun" },
  register_has_account: { en: "Already have an account?", bm: "Sudah ada akaun?" },
  register_login_link: { en: "Sign in", bm: "Log masuk" },
  register_pw_hint: { en: "Minimum 8 characters", bm: "Minimum 8 aksara" },
  register_pw_mismatch: { en: "Passwords do not match.", bm: "Kata laluan tidak sepadan." },

  // Chat
  chat_convos: { en: "Conversations", bm: "Perbualan" },
  chat_no_convos: { en: "No saved conversations yet.", bm: "Belum ada perbualan disimpan." },
  chat_new: { en: "New Chat", bm: "Perbualan Baharu" },
  chat_empty_title: { en: "What would you like to know?", bm: "Apa yang anda ingin ketahui?" },
  chat_sugg_1: { en: "How do I register an Sdn Bhd?", bm: "Bagaimana saya mendaftar Sdn Bhd?" },
  chat_sugg_2: { en: "What licenses do I need to open a restaurant?", bm: "Lesen apa yang saya perlukan untuk buka restoran?" },
  chat_sugg_3: { en: "How do I register for SST?", bm: "Bagaimana saya mendaftar SST?" },
  chat_placeholder: { en: "Ask about Malaysian business compliance...", bm: "Tanya tentang pematuhan perniagaan Malaysia..." },
  chat_disclaimer: { en: "Answers are based on official documents. Not legal advice.", bm: "Jawapan berdasarkan dokumen rasmi. Bukan nasihat undang-undang." },
  chat_show_sources: { en: "Show sources", bm: "Tunjuk sumber" },
  chat_hide_sources: { en: "Hide sources", bm: "Sembunyikan sumber" },
  chat_error: { en: "Something went wrong. Please try again.", bm: "Sesuatu tidak kena. Sila cuba lagi." },
  chat_no_results: {
    en: "I couldn't find any information matching your query under {filters}. Try searching across 'All Authorities' and 'All Topics' instead, or rephrase your question.",
    bm: "Saya tidak menemui sebarang maklumat yang sepadan dengan pertanyaan anda di bawah {filters}. Cuba cari merentas 'Semua Pihak Berkuasa' dan 'Semua Topik', atau ubah soalan anda.",
  },
  chat_no_results_join: { en: "and", bm: "dan" },
  filter_authority: { en: "Authority", bm: "Pihak Berkuasa" },
  filter_topic: { en: "Topic", bm: "Topik" },
  filter_all: { en: "All", bm: "Semua" },

  // Admin
  admin_title: { en: "Document Management", bm: "Pengurusan Dokumen" },
  admin_drop: { en: "Drag and drop a PDF here, or click to browse", bm: "Seret dan lepaskan PDF di sini, atau klik untuk pilih" },
  admin_upload: { en: "Upload & Ingest", bm: "Muat Naik & Proses" },
  admin_wrong_type: { en: "Only .pdf files are allowed.", bm: "Hanya fail .pdf dibenarkan." },
  admin_ingested: { en: "Ingested Documents", bm: "Dokumen Yang Telah Dimuatkan" },
  admin_empty: { en: "No documents ingested yet.", bm: "Belum ada dokumen dimuatkan." },
  admin_col_name: { en: "Document Name", bm: "Nama Dokumen" },
  admin_col_file: { en: "Filename", bm: "Nama Fail" },
  admin_col_at: { en: "Ingested At", bm: "Dimuat Pada" },
  admin_col_hash: { en: "Hash", bm: "Hash" },
  status_queued: { en: "Queued", bm: "Dalam Giliran" },
  status_processing: { en: "Processing", bm: "Memproses" },
  status_done: { en: "Done", bm: "Selesai" },
  status_failed: { en: "Failed", bm: "Gagal" },
} as const;

export type TranslationKey = keyof typeof t;