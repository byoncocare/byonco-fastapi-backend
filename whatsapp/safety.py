"""
Safety guardrails for WhatsApp cancer support assistant
Implements hard gates before OpenAI calls, emergency detection, and content filtering
"""
import re
import logging
from typing import Tuple, Optional

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
    'expression'
]

# Emergency keywords (high priority - bypass AI)
EMERGENCY_KEYWORDS = [
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
    'allergic reaction', 'anaphylaxis', 'difficulty swallowing', 'swelling'
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
    """
    if not text or len(text.strip()) < 3:
        return False
    
    text_lower = text.lower()
    
    # Check for cancer keywords
    for keyword in CANCER_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Also check for medical report context
    medical_context = ['report', 'test result', 'lab', 'scan', 'biopsy', 'pathology']
    if any(ctx in text_lower for ctx in medical_context):
        # If it's a medical context, allow it (user might be asking about cancer reports)
        return True
    
    return False


def is_emergency(text: str) -> bool:
    """
    Detect emergency/crisis situations that require immediate medical attention.
    Returns True if emergency keywords detected.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check for high fever patterns
    if re.search(r'fever\s*(of\s*)?(10[2-4]|38|39|40)', text_lower):
        return True
    
    # Check for temperature patterns
    if re.search(r'temperature\s*(of\s*)?(10[2-4]|38|39|40)', text_lower):
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


def classify_message(text: str) -> Tuple[str, Optional[str]]:
    """
    Classify message and return appropriate action.
    
    Returns:
        (action, response_message)
        action: 'emergency', 'risky', 'non_cancer', 'cancer_ok'
        response_message: Pre-formatted response if action requires it, None if OK to proceed
    """
    if is_emergency(text):
        logger.warning(f"Emergency detected in message: {text[:50]}...")
        return ('emergency', EMERGENCY_RESPONSE)
    
    if contains_risky_content(text):
        logger.warning(f"Risky content detected in message: {text[:50]}...")
        return ('risky', RISKY_CONTENT_RESPONSE)
    
    if not is_cancer_related(text):
        logger.info(f"Non-cancer message detected: {text[:50]}...")
        return ('non_cancer', "I'm specialized in oncology (cancer) care and can only provide information related to cancer diagnosis, treatment, and management. For a comprehensive second opinion from an actual oncologist, please consider our premium Second Opinion service where board-certified specialists review your case: https://www.byoncocare.com/second-opinion. If you have any questions about cancer or treatment options, feel free to ask!")
    
    return ('cancer_ok', None)

