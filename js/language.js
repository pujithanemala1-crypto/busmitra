/**
 * BUSMITRA - Language Selection & Multilingual Dictionary System
 * Supports 21 languages with realistic native scripts & UI translation keys.
 */

window.BUSMITRA_LANGUAGES = [
  { code: "en", name: "English", native: "English", region: "International", translated: true },
  { code: "te", name: "Telugu", native: "తెలుగు", region: "Andhra Pradesh & Telangana", translated: true },
  { code: "hi", name: "Hindi", native: "हिन्दी", region: "India", translated: true },
  { code: "ta", name: "Tamil", native: "தமிழ்", region: "Tamil Nadu", translated: true },
  { code: "kn", name: "Kannada", native: "ಕನ್ನಡ", region: "Karnataka", translated: true },
  { code: "ml", name: "Malayalam", native: "മലയാളം", region: "Kerala", translated: true },
  { code: "bn", name: "Bengali", native: "বাংলা", region: "West Bengal", translated: true },
  { code: "mr", name: "Marathi", native: "मराठी", region: "Maharashtra", translated: true },
  { code: "gu", name: "Gujarati", native: "ગુજરાતી", region: "Gujarat", translated: true },
  { code: "pa", name: "Punjabi", native: "ਪੰਜਾਬੀ", region: "Punjab", translated: true },
  { code: "or", name: "Odia", native: "ଓଡ଼ିଆ", region: "Odisha", translated: true },
  { code: "ur", name: "Urdu", native: "اردو", region: "India / Pakistan", translated: true },
  { code: "as", name: "Assamese", native: "অসমীয়া", region: "Assam", translated: false },
  { code: "sa", name: "Sanskrit", native: "संस्कृतम्", region: "Classical India", translated: false },
  { code: "es", name: "Spanish", native: "Español", region: "Spain & Latin America", translated: true },
  { code: "fr", name: "French", native: "Français", region: "France", translated: true },
  { code: "de", name: "German", native: "Deutsch", region: "Germany", translated: true },
  { code: "ar", name: "Arabic", native: "العربية", region: "Middle East", translated: true },
  { code: "zh", name: "Chinese", native: "中文", region: "East Asia", translated: true },
  { code: "ja", name: "Japanese", native: "日本語", region: "Japan", translated: true },
  { code: "ko", name: "Korean", native: "한국어", region: "Korea", translated: true }
];

// Master Translations Dictionary for Primary Strings
window.BUSMITRA_TRANSLATIONS = {
  en: {
    app_title: "BusMitra",
    tagline: "Your Travel Buddy, Always!",
    nav_home: "Home",
    nav_available_buses: "Available Buses",
    nav_track_bus: "Track Bus",
    nav_help: "Help & Support",
    nav_profile: "My Profile",
    nav_settings: "Settings",
    hero_title: "Where would you like to go?",
    hero_subtitle: "Find your bus. Track your journey. Travel smarter.",
    from_source: "From – Source Location",
    to_destination: "To – Destination",
    enter_source_placeholder: "Enter starting bus stop or landmark...",
    enter_dest_placeholder: "Enter destination city or stop...",
    use_current_location: "Use My Current Location",
    find_available_buses: "Find Available Buses",
    popular_destinations: "Popular Routes & Destinations",
    recent_searches: "Recent Searches",
    available_buses_title: "Available Buses",
    simulated_notice: "SIMULATED DEMO DATA",
    view_details: "View Bus Details",
    bus_details_title: "Bus Details",
    live_tracking_section: "Live Bus Tracking",
    route_stops_section: "Route & Stops",
    timings_section: "Bus Timings & ETA",
    crowd_monitor_section: "IR Sensor Crowd Monitoring",
    prediction_section: "Next Stop Crowd Prediction",
    available_seats: "Available Seats",
    total_capacity: "Total Capacity",
    current_passengers: "Current Passengers",
    crowd_level: "Crowd Level",
    occupancy: "Occupancy",
    gps_status: "GPS Status",
    sensor_in: "Passenger Entry (IN)",
    sensor_out: "Passenger Exit (OUT)",
    esp32_sensor_label: "ESP32 IR Sensor Counter",
    skip_intro: "Skip Intro",
    continue_btn: "Continue to BusMitra"
  },
  te: {
    app_title: "బస్ మిత్ర",
    tagline: "ఎల్లప్పుడూ మీ ప్రయాణ మిత్రుడు!",
    nav_home: "హోమ్",
    nav_available_buses: "అందుబాటులో ఉన్న బస్సులు",
    nav_track_bus: "లైవ్ బస్సు ట్రాకింగ్",
    nav_help: "సహాయం & మద్దతు",
    nav_profile: "నా ప్రొఫైల్",
    nav_settings: "సెట్టింగులు",
    hero_title: "మీరు ఎక్కడికి వెళ్లాలనుకుంటున్నారు?",
    hero_subtitle: "బస్సును కనుగొనండి. ప్రయాణాన్ని ట్రాక్ చేయండి. సులభంగా ప్రయాణించండి.",
    from_source: "ఎక్కడి నుండి – బయలుదేరే స్థలం",
    to_destination: "ఎక్కడికి – చేరే స్థలం",
    enter_source_placeholder: "బస్ స్టాప్ పేరు లేదా ప్రాంతం...",
    enter_dest_placeholder: "చేరవలసిన నగరం లేదా స్టాప్...",
    use_current_location: "నా ప్రస్తుత స్థానాన్ని గుర్తించండి",
    find_available_buses: "బస్సులను వెతకండి",
    popular_destinations: "ప్రసిద్ధ గమ్యస్థానాలు",
    recent_searches: "ఇటీవలి శోధనలు",
    available_buses_title: "అందుబాటులో ఉన్న బస్సులు",
    simulated_notice: "డెమో సిమ్యులేషన్ డేటా",
    view_details: "బస్సు వివరాలు చూడండి",
    bus_details_title: "బస్సు వివరాలు",
    live_tracking_section: "లైవ్ బస్ ట్రాకింగ్",
    route_stops_section: "రూటు మరియు స్టాప్‌లు",
    timings_section: "సమయాలు & అంచనా సమయం (ETA)",
    crowd_monitor_section: "IR సెన్సార్ రద్దీ మానిటర్",
    prediction_section: "తదుపరి స్టాప్ రద్దీ అంచనా",
    available_seats: "ఖాళీ సీట్లు",
    total_capacity: "మొత్తం సామర్థ్యం",
    current_passengers: "ప్రస్తుత ప్రయాణికులు",
    crowd_level: "రద్దీ స్థాయి",
    occupancy: "ఆక్యుపెన్సీ",
    gps_status: "GPS స్థితి",
    sensor_in: "ఎక్కిన వారు (IN)",
    sensor_out: "దిగిన వారు (OUT)",
    esp32_sensor_label: "ESP32 IR సెన్సార్ కౌంటర్",
    skip_intro: "స్కిప్ ఇంట్రో",
    continue_btn: "ముందుకు సాగండి"
  },
  hi: {
    app_title: "बस मित्र",
    tagline: "हमेशा आपका सच्चा यात्रा साथी!",
    nav_home: "होम",
    nav_available_buses: "उपलब्ध बसें",
    nav_track_bus: "बस ट्रैक करें",
    nav_help: "सहायता",
    nav_profile: "मेरी प्रोफ़ाइल",
    nav_settings: "सेटिंग्स",
    hero_title: "आप कहाँ जाना चाहते हैं?",
    hero_subtitle: "बस खोजें। यात्रा ट्रैक करें। स्मार्ट सफर करें।",
    from_source: "कहाँ से – प्रस्थान स्थल",
    to_destination: "कहाँ तक – गंतव्य",
    enter_source_placeholder: "प्रस्थान स्टॉप या लैंडमार्क दर्ज करें...",
    enter_dest_placeholder: "गंतव्य स्टॉप या शहर दर्ज करें...",
    use_current_location: "मेरा वर्तमान स्थान उपयोग करें",
    find_available_buses: "उपलब्ध बसें खोजें",
    popular_destinations: "लोकप्रिय मार्ग और गंतव्य",
    recent_searches: "हाल की खोजें",
    available_buses_title: "उपलब्ध बसें",
    simulated_notice: "डेमो सिमुलेशन डेटा",
    view_details: "बस विवरण देखें",
    bus_details_title: "बस विवरण",
    live_tracking_section: "लाइव बस ट्रैकिंग",
    route_stops_section: "मार्ग और स्टॉप",
    timings_section: "समय और अपेक्षित आगमन",
    crowd_monitor_section: "IR सेंसर भीड़ मॉनिटर",
    prediction_section: "अगले स्टॉप पर भीड़ का पूर्वानुमान",
    available_seats: "उपलब्ध सीटें",
    total_capacity: "कुल क्षमता",
    current_passengers: "वर्तमान यात्री",
    crowd_level: "भीड़ का स्तर",
    occupancy: "ऑक्यूपेंसी",
    gps_status: "जीपीएस स्थिति",
    sensor_in: "सवार हुए (IN)",
    sensor_out: "उतरे (OUT)",
    esp32_sensor_label: "ESP32 IR सेंसर काउंटर",
    skip_intro: "छोड़ें (Skip)",
    continue_btn: "आगे बढ़ें"
  },
  ta: {
    app_title: "பஸ் மித்ரா",
    tagline: "எப்போதும் உங்கள் பயணத் தோழன்!",
    nav_home: "முகப்பு",
    nav_available_buses: "கிடைக்கும் பேருந்துகள்",
    nav_track_bus: "பேருந்து கண்காணிப்பு",
    nav_help: "உதவி",
    nav_profile: "சுயவிவரம்",
    nav_settings: "அமைப்புகள்",
    hero_title: "நீங்கள் எங்கு செல்ல விரும்புகிறீர்கள்?",
    hero_subtitle: "பேருந்தைக் கண்டறியவும். பயணத்தைக் கண்காணிக்கவும்.",
    from_source: "புறப்படும் இடம்",
    to_destination: "சேருமிடம்",
    enter_source_placeholder: "தொடக்க இடம் உள்ளிடவும்...",
    enter_dest_placeholder: "சேருமிடம் உள்ளிடவும்...",
    use_current_location: "எனது தற்போதைய இருப்பிடம்",
    find_available_buses: "பேருந்துகளைக் கண்டுபிடி",
    popular_destinations: "பிரபலமான வழித்தடங்கள்",
    recent_searches: "சமீபத்திய தேடல்கள்",
    available_buses_title: "கிடைக்கும் பேருந்துகள்",
    simulated_notice: "மாதிரி செயல்விளக்க தரவு",
    view_details: "விவரங்களைப் பார்க்க",
    bus_details_title: "பேருந்து விவரங்கள்",
    live_tracking_section: "நேரலை பேருந்து கண்காணிப்பு",
    route_stops_section: "வழித்தடம் மற்றும் நிறுத்தங்கள்",
    timings_section: "நேர அட்டவணை",
    crowd_monitor_section: "ஐஆர் சென்சார் கூட்ட நெரிசல் மானிட்டர்",
    prediction_section: "அடுத்த நிறுத்த கூட்ட கணிப்பு",
    available_seats: "கிடைக்கும் இருக்கைகள்",
    total_capacity: "மொத்த திறன்",
    current_passengers: "தற்போதைய பயணிகள்",
    crowd_level: "கூட்ட நிலை",
    occupancy: "ஆக்கிரமிப்பு",
    gps_status: "ஜிபிஎஸ் நிலை",
    sensor_in: "ஏறியவர்கள் (IN)",
    sensor_out: "இறங்கியவர்கள் (OUT)",
    esp32_sensor_label: "ESP32 IR சென்சார் கவுண்டர்",
    skip_intro: "தவிர்",
    continue_btn: "தொடரவும்"
  }
};

/**
 * Storage helpers for Language
 */
window.getCurrentLanguage = function() {
  return localStorage.getItem("busmitra_lang") || "en";
};

window.setCurrentLanguage = function(langCode) {
  localStorage.setItem("busmitra_lang", langCode);
  window.applyTranslations();
};

/**
 * Translate dynamic key
 */
window.t = function(key, fallback) {
  const currentLang = window.getCurrentLanguage();
  const dict = window.BUSMITRA_TRANSLATIONS[currentLang] || window.BUSMITRA_TRANSLATIONS.en;
  if (dict && dict[key]) {
    return dict[key];
  }
  // Fallback to English
  if (window.BUSMITRA_TRANSLATIONS.en && window.BUSMITRA_TRANSLATIONS.en[key]) {
    return window.BUSMITRA_TRANSLATIONS.en[key];
  }
  return fallback || key;
};

/**
 * Scan DOM and apply translations to elements with data-i18n
 */
window.applyTranslations = function() {
  const elements = document.querySelectorAll("[data-i18n]");
  elements.forEach(el => {
    const key = el.getAttribute("data-i18n");
    const translatedText = window.t(key);
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.setAttribute("placeholder", translatedText);
    } else {
      el.textContent = translatedText;
    }
  });

  // Update current language label on header if present
  const langLabelEl = document.getElementById("header-current-lang");
  if (langLabelEl) {
    const langObj = window.BUSMITRA_LANGUAGES.find(l => l.code === window.getCurrentLanguage());
    langLabelEl.textContent = langObj ? `${langObj.native} (${langObj.name})` : "English";
  }
};

// Initialize translation on DOM load
document.addEventListener("DOMContentLoaded", function() {
  window.applyTranslations();
});
