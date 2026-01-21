# WhatsApp Keyword & Intent System - Complete Documentation

## Overview

Comprehensive multilingual keyword detection system with intent tagging for WhatsApp oncology support assistant. Supports English, Hindi (Roman + Devanagari), and Marathi (Roman + Devanagari).

## Statistics

- **Total CANCER_KEYWORDS**: 295 keywords
- **Total EMERGENCY_KEYWORDS**: 60 keywords  
- **Total RISKY_PATTERNS**: 10 regex patterns
- **Grand Total**: 365 unique keywords/patterns
- **Intent Categories**: 7

---

## Intent Detection System

### Intent Categories

The system now detects 7 key intents from user messages:

1. **emergency** (true/false) - Medical emergencies requiring immediate attention
2. **recurrence_anxiety** (true/false) - Cancer recurrence concerns
3. **hospital_access** (true/false) - Bed availability, admission issues, ICU access
4. **cost_query** (true/false) - Treatment costs, insurance, schemes
5. **treatment_info** (true/false) - Surgery, chemo, radiation, doctor advice
6. **nutrition_support** (true/false) - Food intake, weakness, dietary concerns
7. **emotional_support** (true/false) - Anxiety, panic, help requests

### Intent Detection Usage

```python
from backend.whatsapp.safety import detect_intent, classify_message

# Get intents only
intents = detect_intent("bed nahi mil raha hospital mein")
# Returns: {'emergency': False, 'recurrence_anxiety': False, 'hospital_access': True, ...}

# Get action + intents together
action, response, intents = classify_message("wapas aaya cancer")
# action: 'cancer_ok'
# response: None (proceed to AI)
# intents: {'recurrence_anxiety': True, 'emotional_support': False, ...}
```

### Intent-Based Response Customization (Future Use)

The `intent_dict` is now available in `classify_message()` return value and can be used for:
- Customizing response tone (empathetic for emotional_support, urgent for hospital_access)
- Routing to specialized flows (cost_calculator for cost_query, hospital finder for hospital_access)
- Personalized CTAs based on intent
- Analytics and user journey tracking

---

## Complete Keyword List

### 1. CANCER_KEYWORDS (295 keywords)

#### Original Medical Terms (58 keywords)
- Cancer types, treatment, diagnosis, tests, symptoms, markers, staging systems
- **Preserved**: All original keywords intact

#### NEW: Common Patient Language (15 keywords)
- Spread/severity: spread, spreading, spread to, gone to, reached, affected
- Seriousness: serious, very serious, last stage, final stage, starting stage, early stage
- Questions: how bad, how serious, chance, survival chance, will it be ok, can it be cured
- Prognosis: how long, life expectancy

#### NEW: Hindi Keywords (45 keywords)
- Cancer & disease: kancer, कैंसर, कॅन्सर, ganth, गांठ, sujan, सूजन
- Spread/severity: fail gaya, फैल गया, phail gaya, spread ho gaya, अंदर फैल गया
- Treatment: dawai, दवाई, kemotherapy, कीमो, रेडिएशन, operation, ऑपरेशन, इलाज
- Tests & reports: रिपोर्ट, स्कैन, बायोप्सी
- Pain/emergency: bahut dard, बहुत दर्द, saans nahi aa rahi, सांस नहीं आ रही
- Cost & hospital: kharcha, खर्च, kitna paisa, kitna cost, aspatal, अस्पताल, डॉक्टर

#### NEW: Marathi Keywords (35 keywords)
- Cancer & condition: कॅन्सर, गाठ, suj, सूज
- Spread/seriousness: pasarla, पसरला, खूप वाढला, खूप गंभीर, shevat cha stage, शेवटचा स्टेज
- Treatment: upchar, उपचार, औषध, कीमो, रेडिएशन, ऑपरेशन
- Tests & scans: रिपोर्ट, स्कॅन, बायोप्सी
- Pain/emergency: khup dukh, खूप दुखतं, श्वास घ्यायला त्रास, रक्तस्राव, ताप
- Hospital/access: दवाखाना, aspatal, डॉक्टर

#### NEW: Caregiver & Emotional Triggers (10 keywords)
- ghabrahat, घबराहट, bhiti, भीती, far vaait ahe, फार वाईट आहे
- kahi upaay aahe ka, कोई उपाय है क्या, काही उपाय आहे का
- please help, help kara, madat kara, मदत करा

#### NEW: Distance/Location/Access (10 keywords)
- near me, पास में, जवळ, distance, kitna door, कितना दूर
- kiti lamb, किती लांब, km, kilometer, travel, jaaycha aahe, जाना पड़ेगा

#### NEW: Cost/Payment/Scheme - India (10 keywords)
- estimate, अंदाज, package, पॅकेज, bill, बिल
- free treatment, मोफत इलाज, government scheme, सरकारी योजना
- ayushman, आयुष्मान, insurance, इन्शुरन्स

#### FINAL: Last-Mile High-Impact Keywords (38 keywords)

**GAP A: Doctor Reference Phrases (6)**
- doctor ne bola, doctor bola, डॉक्टर ने बोला, डॉक्टर म्हणाले, bol rahe hai, bolat hote

**GAP B: Surgery/Operation Patient Language (5)**
- operation hona hai, operation karna padega, ऑपरेशन करायचं आहे, tumor nikalna, गाठ काढायची आहे

**GAP C: Recurrence/Return of Cancer (6)**
- wapas aaya, वापस आया, parat aala, परत आला, phir se cancer, dubara cancer

**GAP D: Admission/Beds/ICU (8)**
- admit, admission, bharti, भरती, bed nahi mil raha, bed milnar ka, icu, icu bed

**GAP E: Liver/Jaundice/Fluid - India-Specific (7)**
- piliya, पीलिया, कावीळ, paani bhar gaya, पाणी भरलं, ascites

**GAP F: Weakness/Food Intake Distress (6)**
- kuch khaya nahi, kha nahi pa raha, khana nahi ho raha, खायला जमत नाही, weakness, kamjori, कमजोरी

---

### 2. EMERGENCY_KEYWORDS (60 keywords)

#### English Emergency Terms (23)
- emergency, urgent, immediate, can't breathe, chest pain, heavy bleeding, fainting, seizure, high fever, suicide, severe pain, allergic reaction, etc.

#### NEW: Hindi Emergency Terms (20)
- bahut dard, बहुत दर्द, saans nahi aa rahi, सांस नहीं आ रही, bleeding ho raha, खून बह रहा, bukhar, बुखार, ज्यादा बुखार, chest mein dard, छाती में दर्द

#### NEW: Marathi Emergency Terms (17)
- khup dukh, खूप दुखतं, श्वास घ्यायला त्रास, saans ghyayla tras, रक्तस्राव, ताप, खूप ताप, जबरदस्त दुख

---

### 3. RISKY_PATTERNS (10 regex patterns)

- Medication dosage requests
- Stopping treatment requests
- Alternative therapy replacements
- Ignoring medical advice patterns

---

## Typo/Misspelling Tolerance (Lightweight Regex)

Only for high-impact words:

1. **chemo**: `che+mo+|kemotherapy` - matches: chemo, kemotherapy
2. **cancer**: `c[ae]ncer|kancer` - matches: cancer, cencer, kancer
3. **pet ct**: `pet[- ]?ct|pet\s+scan` - matches: pet ct, pet-ct, pet scan
4. **radiation**: `radia+tion+` - matches: radiation, radiaation

---

## Intent Keywords Mapping

### Emergency Intent
- All EMERGENCY_KEYWORDS automatically set `emergency: true`
- Highest priority - early return

### Recurrence Anxiety Intent
Keywords: wapas aaya, वापस आया, parat aala, परत आला, phir se cancer, dubara cancer, recurrence, recurred, return, came back, again

### Hospital Access Intent
Keywords: admit, admission, bharti, भरती, bed nahi mil raha, bed milnar ka, icu, icu bed, bed available, bed chahiye, hospital admission, aspatal, अस्पताल, admission chahiye, admit karna hai

### Cost Query Intent
Keywords: cost, kitna paisa, kitna cost, kharcha, खर्च, estimate, अंदाज, package, पॅकेज, bill, बिल, price, treatment cost, medical cost, expense, free treatment, मोफत इलाज, government scheme, सरकारी योजना, ayushman, आयुष्मान, insurance, इन्शुरन्स

### Treatment Info Intent
Keywords: chemotherapy, chemo, kemotherapy, कीमो, radiation, radiotherapy, रेडिएशन, surgery, operation, ऑपरेशन, operation hona hai, operation karna padega, ऑपरेशन करायचं आहे, tumor nikalna, गाठ काढायची आहे, treatment, इलाज, upchar, उपचार, doctor ne bola, doctor bola, डॉक्टर ने बोला, doctor, stage, staging, stage info

### Nutrition Support Intent
Keywords: nutrition, diet, khana, खाना, kuch khaya nahi, kha nahi pa raha, khana nahi ho raha, खायला जमत नाही, food, eating, meal, weakness, kamjori, कमजोरी, weak, kamzor

### Emotional Support Intent
Keywords: ghabrahat, घबराहट, bhiti, भीती, far vaait ahe, फार वाईट आहे, kahi upaay aahe ka, कोई उपाय है क्या, काही उपाय आहे का, please help, help kara, madat kara, मदत करा, worried, scared, afraid, anxious, nervous, help, support, guidance, advice

---

## Usage Example

```python
from backend.whatsapp.safety import classify_message

# Example 1: Hospital access query
action, response, intents = classify_message("bed nahi mil raha hospital mein")
# action: 'cancer_ok'
# response: None (proceed to AI)
# intents: {'hospital_access': True, 'emergency': False, ...}

# Example 2: Recurrence anxiety
action, response, intents = classify_message("wapas aaya cancer bahut ghabrahat")
# action: 'cancer_ok'
# intents: {'recurrence_anxiety': True, 'emotional_support': True, ...}

# Example 3: Emergency
action, response, intents = classify_message("bahut dard hai emergency")
# action: 'emergency'
# response: EMERGENCY_RESPONSE (pre-formatted)
# intents: {'emergency': True, ...}
```

---

## Important Notes

### ✅ What IS Included
- Patient-friendly language (non-medical terms)
- Multilingual support (English, Hindi, Marathi)
- Common typos and misspellings
- Emotional triggers
- India-specific healthcare context
- Intent tagging for response customization

### ❌ What is NOT Included (by design)
- Drug names (handled by LLM)
- Rare biomarkers (handled by LLM)
- Full diet lists (handled by LLM)
- Excessive regex (only 4 high-impact patterns)
- Academic/rare medical terms (handled by LLM)

These belong in:
- LLM classification
- Structured follow-up questions
- AI-generated responses

---

## Future Enhancements

The `intent_dict` is now available for:
1. **Response tone customization** - Different tones for different intents
2. **Flow routing** - Route to specialized handlers (cost calculator, hospital finder, etc.)
3. **CTA personalization** - Show relevant links/actions based on intent
4. **Analytics** - Track user intent patterns for product improvements

---

## Maintenance

- All existing keywords preserved
- Backward compatible with existing code
- No breaking changes to existing functionality
- Intent tagging is additive only

---

**Last Updated**: January 9, 2026  
**Total Keywords**: 365 unique keywords/patterns  
**Intent Categories**: 7  
**Languages Supported**: English, Hindi (Roman + Devanagari), Marathi (Roman + Devanagari)
