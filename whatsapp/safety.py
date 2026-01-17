"""
Safety guardrails for WhatsApp cancer support assistant
Implements hard gates before OpenAI calls, emergency detection, and content filtering
"""
import re
import logging
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)

# Cancer-related keywords (comprehensive list)
CANCER_KEYWORDS = [
    # Cancer types
    'cancer', 'carcinoma', 'sarcoma', 'lymphoma', 'leukemia', 'melanoma',
    'tumor', 'tumour', 'malignancy', 'malignant', 'benign', 'neoplasm',
    # Treatment
    'chemotherapy', 'chemo', 'radiation', 'radiotherapy', 'surgery', 'surgical',
    'immunotherapy', 'targeted therapy', 'hormone therapy', 'stem cell',
    'oncology', 'oncologist', 'oncology', 'cancer care', 'cancer treatment',
    # Diagnosis & tests
    'biopsy', 'pathology', 'histology', 'diagnosis', 'stage', 'staging',
    'metastasis', 'metastatic', 'recurrence', 'remission',
    'ct scan', 'mri', 'pet scan', 'pet ct', 'ultrasound', 'x-ray',
    # Symptoms & side effects
    'side effect', 'symptom', 'pain', 'nausea', 'fatigue', 'hair loss',
    'neutropenia', 'thrombocytopenia', 'anemia',
    # Medical terms
    'cancer patient', 'cancer survivor', 'cancer care', 'cancer support',
    'medical report', 'test result', 'lab report', 'pathology report',
    # Nutrition & lifestyle
    'nutrition', 'diet', 'cancer diet', 'chemotherapy diet',
    # Hospitals & costs
    'hospital', 'oncologist', 'cancer center', 'treatment cost', 'medical cost',
    # Common cancer types
    'breast cancer', 'lung cancer', 'prostate cancer', 'colon cancer',
    'liver cancer', 'pancreatic cancer', 'ovarian cancer', 'cervical cancer',
    'brain tumor', 'bone cancer', 'skin cancer',
    # Pathology / IHC / Molecular markers
    'ki67', 'ki-67',
    'her2', 'her-2',
    'er', 'pr', 'er/pr',
    'pdl1', 'pd-l1',
    'egfr', 'alk', 'ros1',
    'braf', 'ntrk',
    'brca', 'brca1', 'brca2',
    'microsatellite', 'msi',
    'tmb',
    # Tumor grading / staging systems
    'tnm', 'grade', 'grading',
    'gleason',
    'figo',
    'ann arbor',
    # Tumor markers (blood tests)
    'cea',
    'ca-125', 'ca125',
    'ca19-9', 'ca19',
    'afp',
    'psa',
    'beta hcg', 'β-hcg',
    # Report terminology (oncology-specific)
    'ihc',
    'immunohistochemistry',
    'histopath', 'histopathology',
    'cytology',
    'biomarker',
    'mutation',
    'amplification',
    'expression',
    
    # ========================================================================
    # NEW: COMMON PATIENT LANGUAGE (NON-MEDICAL ENGLISH)
    # ========================================================================
    # Spread / severity (casual language)
    'spread', 'spreading', 'spread to', 'gone to', 'reached', 'affected',
    'serious', 'very serious', 'last stage', 'final stage', 'starting stage', 'early stage',
    'how bad', 'how serious', 'chance', 'survival chance', 'will it be ok', 'can it be cured',
    'how long', 'life expectancy',
    
    # ========================================================================
    # HINDI KEYWORDS (Roman + Devanagari)
    # ========================================================================
    # Cancer & disease
    'kancer', 'कैंसर', 'कॅन्सर', 'ganth', 'gath', 'ghanth', 'गांठ', 'गाठ',
    'sujan', 'सूजन',
    # Spread / severity
    'fail gaya', 'fail raha', 'फैल गया', 'phail gaya', 'spread ho gaya', 'अंदर फैल गया',
    'last stage', 'aakhri stage', 'आख़िरी स्टेज',
    # Treatment
    'dawai', 'दवाई', 'kemotherapy', 'कीमो', 'रेडिएशन', 'operation', 'ऑपरेशन',
    'इलाज',
    # Tests & reports
    'रिपोर्ट', 'स्कैन', 'बायोप्सी',
    # Pain / emergency signals
    'bahut dard', 'बहुत दर्द', 'saans nahi aa rahi', 'सांस नहीं आ रही',
    'bleeding ho raha', 'खून बह रहा', 'bukhar', 'बुखार',
    # Cost & hospital
    'kharcha', 'खर्च', 'kitna paisa', 'kitna cost', 'aspatal', 'अस्पताल',
    'डॉक्टर',
    
    # ========================================================================
    # MARATHI KEYWORDS (Roman + Devanagari)
    # ========================================================================
    # Cancer & condition
    'कॅन्सर', 'गाठ', 'suj', 'सूज',
    # Spread / seriousness
    'pasarla', 'पसरला', 'खूप वाढला', 'खूप गंभीर', 'shevat cha stage', 'शेवटचा स्टेज',
    # Treatment
    'upchar', 'उपचार', 'औषध', 'कीमो', 'रेडिएशन', 'ऑपरेशन',
    # Tests & scans
    'रिपोर्ट', 'स्कॅन', 'बायोप्सी',
    # Pain / emergency
    'khup dukh', 'खूप दुखतं', 'श्वास घ्यायला त्रास', 'saans ghyayla tras',
    'रक्तस्राव', 'ताप',
    # Hospital / access
    'दवाखाना', 'aspatal', 'डॉक्टर',
    
    # ========================================================================
    # CAREGIVER & EMOTIONAL TRIGGERS
    # ========================================================================
    'ghabrahat', 'घबराहट', 'bhiti', 'भीती', 'far vaait ahe', 'फार वाईट आहे',
    'kahi upaay aahe ka', 'कोई उपाय है क्या', 'काही उपाय आहे का',
    'please help', 'help kara', 'madat kara', 'मदत करा',
    
    # ========================================================================
    # DISTANCE / LOCATION / ACCESS WORDS
    # ========================================================================
    'near me', 'पास में', 'जवळ', 'distance', 'kitna door', 'कितना दूर',
    'kiti lamb', 'किती लांब', 'km', 'kilometer', 'travel', 'jaaycha aahe', 'जाना पड़ेगा',
    
    # ========================================================================
    # COST / PAYMENT / SCHEME (India-specific)
    # ========================================================================
    'estimate', 'अंदाज', 'package', 'पॅकेज', 'bill', 'बिल',
    'free treatment', 'मोफत इलाज', 'government scheme', 'सरकारी योजना',
    'ayushman', 'आयुष्मान', 'insurance', 'इन्शुरन्स',
    
    # ========================================================================
    # FINAL LAST-MILE ADDITIONS (High Impact Patient Language)
    # ========================================================================
    # GAP A: Doctor reference phrases (patient quotes doctors)
    'doctor ne bola', 'doctor bola', 'डॉक्टर ने बोला', 'डॉक्टर म्हणाले',
    'bol rahe hai', 'bolat hote',
    
    # GAP B: Surgery/operation (patient-level language)
    'operation hona hai', 'operation karna padega', 'ऑपरेशन करायचं आहे',
    'tumor nikalna', 'गाठ काढायची आहे',
    
    # GAP C: Recurrence / return of cancer (common anxiety trigger)
    'wapas aaya', 'वापस आया', 'parat aala', 'परत आला',
    'phir se cancer', 'dubara cancer',
    
    # GAP D: Admission / beds / ICU (hospital access distress)
    'admit', 'admission', 'bharti', 'भरती',
    'bed nahi mil raha', 'bed milnar ka', 'icu', 'icu bed',
    
    # GAP E: Liver / jaundice / fluid (India-specific common issue)
    'piliya', 'पीलिया', 'कावीळ', 'paani bhar gaya', 'पाणी भरलं', 'ascites',
    
    # GAP F: Weakness / food intake distress (caregiver reality)
    'kuch khaya nahi', 'kha nahi pa raha', 'khana nahi ho raha', 'खायला जमत नाही',
    'weakness', 'kamjori', 'कमजोरी'
]

# Emergency keywords (high priority - bypass AI)
EMERGENCY_KEYWORDS = [
    # English
    'emergency', 'urgent', 'immediate', 'right now',
    'can\'t breathe', 'can\'t breath', 'breathlessness', 'shortness of breath',
    'chest pain', 'heart attack', 'heart pain',
    'heavy bleeding', 'bleeding heavily', 'uncontrolled bleeding',
    'fainting', 'fainted', 'passed out', 'unconscious',
    'seizure', 'convulsion', 'fitting',
    'high fever', 'fever 102', 'fever 103', 'fever 104', 'temperature 102',
    'neutropenic fever', 'febrile neutropenia',
    'suicide', 'suicidal', 'kill myself', 'end my life', 'self harm', 'self-harm',
    'severe pain', 'extreme pain', 'unbearable pain',
    'allergic reaction', 'anaphylaxis', 'difficulty swallowing', 'swelling',
    # Hindi emergency terms (Roman + Devanagari)
    'bahut dard', 'बहुत दर्द', 'saans nahi aa rahi', 'सांस नहीं आ रही',
    'bleeding ho raha', 'खून बह रहा', 'bukhar', 'बुखार', 'ज्यादा बुखार',
    'chest mein dard', 'छाती में दर्द',
    # Marathi emergency terms (Roman + Devanagari)
    'khup dukh', 'खूप दुखतं', 'श्वास घ्यायला त्रास', 'saans ghyayla tras',
    'रक्तस्राव', 'ताप', 'खूप ताप', 'जबरदस्त दुख'
]

# High-risk medical content (refuse without doctor consultation)
RISKY_PATTERNS = [
    r'tell me (the )?dosage',
    r'how much (should I take|to take|medicine)',
    r'should I stop (chemo|treatment|medication|medicine)',
    r'can I stop (chemo|treatment|medication|medicine)',
    r'replace with (ayurveda|homeopathy|alternative)',
    r'only (ayurveda|homeopathy|alternative)',
    r'ignore (doctor|oncologist|medical advice)',
    r'don\'t need (doctor|oncologist|treatment)',
    r'alternative (cure|treatment) only',
    r'natural cure (only|instead)'
]

# Emergency response messages
EMERGENCY_RESPONSE = """🚨 URGENT MEDICAL SITUATION DETECTED

This appears to be a medical emergency. Please:

1. **Call emergency services immediately:**
   - India: 108 or 102
   - USA: 911
   - UK: 999

2. **If you're a cancer patient with fever above 100.4°F (38°C):**
   - This could be neutropenic fever (life-threatening)
   - Go to the nearest emergency room immediately
   - Do NOT wait

3. **For severe symptoms:**
   - Chest pain, difficulty breathing → Emergency room NOW
   - Heavy bleeding → Apply pressure, call ambulance
   - Seizures → Protect from injury, call ambulance

**I cannot provide emergency medical advice. Please seek immediate professional medical care.**

For non-emergency questions, you can message me again after you've received care."""

RISKY_CONTENT_RESPONSE = """I understand your concern, but I cannot provide specific medical advice about:

- Medication dosages
- Stopping or changing treatment
- Replacing medical treatment with alternative therapies

**Why?** These decisions must be made with your oncologist based on your specific medical condition, test results, and treatment history.

**What I CAN help with:**
- Understanding your medical reports
- Preparing questions to ask your doctor
- General information about cancer treatments
- Nutrition and lifestyle guidance during treatment
- Finding hospitals and specialists

Would you like help preparing questions for your next doctor's appointment?"""


def is_cancer_related(text: str) -> bool:
    """
    Hard gate: Check if message is cancer-related before calling OpenAI.
    Returns True only if message contains cancer-related keywords.
    
    This is a safety guardrail - system prompts can be jailbroken.
    Includes typo tolerance for high-impact words (chemo, cancer, pet ct).
    """
    if not text or len(text.strip()) < 3:
        return False
    
    text_lower = text.lower()
    
    # Check for cancer keywords
    for keyword in CANCER_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Typo/misspelling tolerance (lightweight regex only for high-impact words)
    # Check for chemo variations: che+mo+, kemotherapy
    if re.search(r'che+mo+|kemotherapy', text_lower):
        return True
    
    # Check for cancer variations: c[ae]ncer, kancer (note: character class [ae] not [a|e])
    if re.search(r'c[ae]ncer|kancer', text_lower):
        return True
    
    # Check for pet ct variations: pet[- ]?ct, pet scan
    if re.search(r'pet[- ]?ct|pet\s+scan', text_lower):
        return True
    
    # Check for radiation variations: radia+tion+
    if re.search(r'radia+tion+', text_lower):
        return True
    
    # Check for medical report context (English + Hindi + Marathi)
    medical_context = [
        # English
        'report', 'test result', 'lab', 'scan', 'biopsy', 'pathology',
        # Hindi/Marathi (Roman + Devanagari)
        'रिपोर्ट', 'स्कैन', 'स्कॅन', 'बायोप्सी'
    ]
    if any(ctx in text_lower for ctx in medical_context):
        # If it's a medical context, allow it (user might be asking about cancer reports)
        return True
    
    return False


def is_emergency(text: str) -> bool:
    """
    Detect emergency/crisis situations that require immediate medical attention.
    Returns True if emergency keywords detected.
    Supports English, Hindi (Roman + Devanagari), and Marathi.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check for high fever patterns (English)
    if re.search(r'fever\s*(of\s*)?(10[2-4]|38|39|40)', text_lower):
        return True
    
    # Check for temperature patterns (English)
    if re.search(r'temperature\s*(of\s*)?(10[2-4]|38|39|40)', text_lower):
        return True
    
    # Check for Hindi/Marathi fever patterns (bukhar with numbers, ताप)
    if re.search(r'bukhar\s*(10[2-4]|38|39|40|ज्यादा|खूप|जबरदस्त)|ताप\s*(102|103|104|ज्यादा)', text_lower):
        return True
    
    # Check for emotional distress indicators (often precede emergency)
    emotional_distress = [
        'ghabrahat', 'घबराहट', 'bhiti', 'भीती', 'far vaait ahe', 'फार वाईट आहे',
        'bahut dard', 'खूप दुख', 'khup dukh', 'खूप दुखतं'
    ]
    # If emotional distress + pain/fever/breathing issue, likely emergency
    has_distress = any(term in text_lower for term in emotional_distress)
    has_symptom = any(term in text_lower for term in ['dard', 'दर्द', 'dukh', 'दुख', 'saans', 'सांस', 'bukhar', 'बुखार', 'ताप'])
    if has_distress and has_symptom:
        return True
    
    return False


def contains_risky_content(text: str) -> bool:
    """
    Detect high-risk medical content that should be refused.
    Returns True if risky patterns detected.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    for pattern in RISKY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False


def detect_intent(text: str) -> Dict[str, bool]:
    """
    Detect user intent from keywords (lightweight keyword-based intent tagging).
    
    Returns:
        Dict with intent flags: emergency, recurrence_anxiety, hospital_access, 
        cost_query, treatment_info, nutrition_support, emotional_support
    """
    if not text:
        return {
            'emergency': False,
            'recurrence_anxiety': False,
            'hospital_access': False,
            'cost_query': False,
            'treatment_info': False,
            'nutrition_support': False,
            'emotional_support': False
        }
    
    text_lower = text.lower()
    intents = {
        'emergency': False,
        'recurrence_anxiety': False,
        'hospital_access': False,
        'cost_query': False,
        'treatment_info': False,
        'nutrition_support': False,
        'emotional_support': False
    }
    
    # Emergency intent (highest priority)
    if is_emergency(text):
        intents['emergency'] = True
        return intents  # Early return - emergency takes precedence
    
    # Recurrence anxiety keywords
    recurrence_keywords = [
        'wapas aaya', 'वापस आया', 'parat aala', 'परत आला',
        'phir se cancer', 'dubara cancer', 'recurrence', 'recurred',
        'return', 'came back', 'again'
    ]
    if any(kw in text_lower for kw in recurrence_keywords):
        intents['recurrence_anxiety'] = True
    
    # Hospital access intent
    hospital_access_keywords = [
        'admit', 'admission', 'bharti', 'भरती',
        'bed nahi mil raha', 'bed milnar ka', 'icu', 'icu bed',
        'bed available', 'bed chahiye', 'bed mil sakta hai',
        'hospital admission', 'aspatal', 'अस्पताल',
        'admission chahiye', 'admit karna hai'
    ]
    if any(kw in text_lower for kw in hospital_access_keywords):
        intents['hospital_access'] = True
    
    # Cost query intent
    cost_keywords = [
        'cost', 'kitna paisa', 'kitna cost', 'kharcha', 'खर्च',
        'estimate', 'अंदाज', 'package', 'पॅकेज', 'bill', 'बिल',
        'price', 'treatment cost', 'medical cost', 'expense',
        'free treatment', 'मोफत इलाज', 'government scheme', 'सरकारी योजना',
        'ayushman', 'आयुष्मान', 'insurance', 'इन्शुरन्स'
    ]
    if any(kw in text_lower for kw in cost_keywords):
        intents['cost_query'] = True
    
    # Treatment info intent
    treatment_keywords = [
        'chemotherapy', 'chemo', 'kemotherapy', 'कीमो',
        'radiation', 'radiotherapy', 'रेडिएशन',
        'surgery', 'operation', 'ऑपरेशन', 'operation hona hai',
        'operation karna padega', 'ऑपरेशन करायचं आहे',
        'tumor nikalna', 'गाठ काढायची आहे',
        'treatment', 'इलाज', 'upchar', 'उपचार',
        'doctor ne bola', 'doctor bola', 'डॉक्टर ने बोला',
        'doctor', 'stage', 'staging', 'stage info'
    ]
    if any(kw in text_lower for kw in treatment_keywords):
        intents['treatment_info'] = True
    
    # Nutrition support intent
    nutrition_keywords = [
        'nutrition', 'diet', 'khana', 'खाना',
        'kuch khaya nahi', 'kha nahi pa raha', 'khana nahi ho raha',
        'खायला जमत नाही', 'food', 'eating', 'meal',
        'weakness', 'kamjori', 'कमजोरी', 'weak', 'kamzor'
    ]
    if any(kw in text_lower for kw in nutrition_keywords):
        intents['nutrition_support'] = True
    
    # Emotional support intent
    emotional_keywords = [
        'ghabrahat', 'घबराहट', 'bhiti', 'भीती',
        'far vaait ahe', 'फार वाईट आहे',
        'kahi upaay aahe ka', 'कोई उपाय है क्या', 'काही उपाय आहे का',
        'please help', 'help kara', 'madat kara', 'मदत करा',
        'worried', 'scared', 'afraid', 'anxious', 'nervous',
        'help', 'support', 'guidance', 'advice'
    ]
    if any(kw in text_lower for kw in emotional_keywords):
        intents['emotional_support'] = True
    
    return intents


def classify_message(text: str) -> Tuple[str, Optional[str], Optional[Dict[str, bool]]]:
    """
    Classify message and return appropriate action with intent tags.
    
    Returns:
        (action, response_message, intent_dict)
        action: 'emergency', 'risky', 'non_cancer', 'cancer_ok'
        response_message: Pre-formatted response if action requires it, None if OK to proceed
        intent_dict: Dict with intent flags for response customization
    """
    # Detect intents first (for logging and future use)
    intents = detect_intent(text)
    
    if is_emergency(text):
        logger.warning(f"Emergency detected in message: {text[:50]}...")
        return ('emergency', EMERGENCY_RESPONSE, intents)
    
    if contains_risky_content(text):
        logger.warning(f"Risky content detected in message: {text[:50]}...")
        return ('risky', RISKY_CONTENT_RESPONSE, intents)
    
    if not is_cancer_related(text):
        logger.info(f"Non-cancer message detected: {text[:50]}...")
        return ('non_cancer', "I'm specialized in oncology (cancer) care and can only provide information related to cancer diagnosis, treatment, and management. For a comprehensive second opinion from an actual oncologist, please consider our premium Second Opinion service where board-certified specialists review your case: https://www.byoncocare.com/second-opinion. If you have any questions about cancer or treatment options, feel free to ask!", intents)
    
    # Log detected intents for analytics
    active_intents = [k for k, v in intents.items() if v]
    if active_intents:
        logger.info(f"Detected intents: {', '.join(active_intents)}")
    
    return ('cancer_ok', None, intents)

