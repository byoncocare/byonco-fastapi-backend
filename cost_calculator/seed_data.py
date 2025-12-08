# Seed data for ByOnco database

COUNTRIES_DATA = [
    {'id': 'india', 'name': 'India', 'currency': 'INR', 'fx_rate': 83.0},
    {'id': 'usa', 'name': 'United States', 'currency': 'USD', 'fx_rate': 1.0},
    {'id': 'singapore', 'name': 'Singapore', 'currency': 'SGD', 'fx_rate': 1.35},
    {'id': 'japan', 'name': 'Japan', 'currency': 'JPY', 'fx_rate': 150.0},
    {'id': 'france', 'name': 'France', 'currency': 'EUR', 'fx_rate': 0.92},
    {'id': 'turkey', 'name': 'Turkey', 'currency': 'TRY', 'fx_rate': 32.0},
    {'id': 'thailand', 'name': 'Thailand', 'currency': 'THB', 'fx_rate': 35.0},
    {'id': 'canada', 'name': 'Canada', 'currency': 'CAD', 'fx_rate': 1.38},
    {'id': 'norway', 'name': 'Norway', 'currency': 'NOK', 'fx_rate': 11.0}
]

INSURERS_DATA = {
    'india': [
        {'id': 'india_1', 'country_id': 'india', 'name': 'Aditya Birla Health Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 50, 'drug_coverage': 70},
        {'id': 'india_2', 'country_id': 'india', 'name': 'ManipalCigna Health Insurance', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 60, 'drug_coverage': 75},
        {'id': 'india_3', 'country_id': 'india', 'name': 'Niva Bupa Health Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 55, 'drug_coverage': 70},
        {'id': 'india_4', 'country_id': 'india', 'name': 'Care Health Insurance', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 50, 'drug_coverage': 65},
        {'id': 'india_5', 'country_id': 'india', 'name': 'Star Health & Allied Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 55, 'drug_coverage': 70},
        {'id': 'india_6', 'country_id': 'india', 'name': 'HDFC ERGO General Insurance', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 60, 'drug_coverage': 75},
        {'id': 'india_7', 'country_id': 'india', 'name': 'ICICI Lombard General Insurance', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 60, 'drug_coverage': 75},
        {'id': 'india_8', 'country_id': 'india', 'name': 'Bajaj Allianz General Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 55, 'drug_coverage': 70},
        {'id': 'india_9', 'country_id': 'india', 'name': 'Reliance General Insurance', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 50, 'drug_coverage': 65},
        {'id': 'india_10', 'country_id': 'india', 'name': 'New India Assurance', 'is_global': False, 'inpatient_coverage': 70, 'outpatient_coverage': 45, 'drug_coverage': 60},
        {'id': 'india_11', 'country_id': 'india', 'name': 'National Insurance Co. Ltd.', 'is_global': False, 'inpatient_coverage': 70, 'outpatient_coverage': 45, 'drug_coverage': 60},
        {'id': 'india_12', 'country_id': 'india', 'name': 'Future Generali India Insurance', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 50, 'drug_coverage': 65}
    ],
    'usa': [
        {'id': 'usa_1', 'country_id': 'usa', 'name': 'UnitedHealthcare', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'usa_2', 'country_id': 'usa', 'name': 'Aetna (CVS Health)', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'usa_3', 'country_id': 'usa', 'name': 'Centene (Ambetter)', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 65, 'drug_coverage': 70},
        {'id': 'usa_4', 'country_id': 'usa', 'name': 'Humana', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'usa_5', 'country_id': 'usa', 'name': 'Anthem (Elevance Health)', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'usa_6', 'country_id': 'usa', 'name': 'Kaiser Permanente', 'is_global': False, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'usa_7', 'country_id': 'usa', 'name': 'BCBS (Blue Cross Blue Shield)', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'usa_8', 'country_id': 'usa', 'name': 'Cigna Healthcare', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'usa_9', 'country_id': 'usa', 'name': 'Molina Healthcare', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 65, 'drug_coverage': 70},
        {'id': 'usa_10', 'country_id': 'usa', 'name': 'Highmark', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'usa_11', 'country_id': 'usa', 'name': 'GuideWell (Florida Blue)', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'usa_12', 'country_id': 'usa', 'name': 'Regence (Cambia Health)', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75}
    ],
    'singapore': [
        {'id': 'singapore_1', 'country_id': 'singapore', 'name': 'AIA Singapore', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'singapore_2', 'country_id': 'singapore', 'name': 'Great Eastern Life', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'singapore_3', 'country_id': 'singapore', 'name': 'HSBC Life Singapore', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'singapore_4', 'country_id': 'singapore', 'name': 'Raffles Health Insurance', 'is_global': False, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'singapore_5', 'country_id': 'singapore', 'name': 'Income Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'singapore_6', 'country_id': 'singapore', 'name': 'Allianz Insurance Singapore', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'singapore_7', 'country_id': 'singapore', 'name': 'AIG Asia Pacific Insurance', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'singapore_8', 'country_id': 'singapore', 'name': 'AXA Singapore', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'singapore_9', 'country_id': 'singapore', 'name': 'Cigna Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'singapore_10', 'country_id': 'singapore', 'name': 'China Life Insurance (Singapore)', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'singapore_11', 'country_id': 'singapore', 'name': 'Etiqa Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'singapore_12', 'country_id': 'singapore', 'name': 'Sompo Insurance Singapore', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75}
    ],
    'japan': [
        {'id': 'japan_1', 'country_id': 'japan', 'name': 'AXA Japan', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'japan_2', 'country_id': 'japan', 'name': 'Bupa Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'japan_3', 'country_id': 'japan', 'name': 'Allianz Care', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'japan_4', 'country_id': 'japan', 'name': 'Cigna Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'japan_5', 'country_id': 'japan', 'name': 'William Russell', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'japan_6', 'country_id': 'japan', 'name': 'VUMI', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'japan_7', 'country_id': 'japan', 'name': 'IMG', 'is_global': True, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'japan_8', 'country_id': 'japan', 'name': 'DavidShield', 'is_global': True, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'japan_9', 'country_id': 'japan', 'name': 'GeoBlue', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'japan_10', 'country_id': 'japan', 'name': 'Sompo Japan', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'japan_11', 'country_id': 'japan', 'name': 'Nippon Life (Nissay)', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'japan_12', 'country_id': 'japan', 'name': 'Dai-ichi Life', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70}
    ],
    'france': [
        {'id': 'france_1', 'country_id': 'france', 'name': 'AXA France', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'france_2', 'country_id': 'france', 'name': 'Allianz France', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'france_3', 'country_id': 'france', 'name': 'CNP Assurances', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'france_4', 'country_id': 'france', 'name': 'MGEN', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'france_5', 'country_id': 'france', 'name': 'Macif', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'france_6', 'country_id': 'france', 'name': 'Malakoff Humanis', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'france_7', 'country_id': 'france', 'name': 'Generali France', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'france_8', 'country_id': 'france', 'name': 'Groupama', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'france_9', 'country_id': 'france', 'name': 'Harmonie Mutuelle', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'france_10', 'country_id': 'france', 'name': 'April International', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'france_11', 'country_id': 'france', 'name': 'AG2R La Mondiale', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'france_12', 'country_id': 'france', 'name': 'Bupa Global (France)', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85}
    ],
    'turkey': [
        {'id': 'turkey_1', 'country_id': 'turkey', 'name': 'Allianz Türkiye', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'turkey_2', 'country_id': 'turkey', 'name': 'AXA Sigorta', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'turkey_3', 'country_id': 'turkey', 'name': 'Anadolu Sigorta', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'turkey_4', 'country_id': 'turkey', 'name': 'Zurich Sigorta', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'turkey_5', 'country_id': 'turkey', 'name': 'Bupa Acıbadem Sigorta', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'turkey_6', 'country_id': 'turkey', 'name': 'Cigna Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'turkey_7', 'country_id': 'turkey', 'name': 'Demir Sağlık ve Hayat Sigorta', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'turkey_8', 'country_id': 'turkey', 'name': 'Mapfre Sigorta', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'turkey_9', 'country_id': 'turkey', 'name': 'Anadolu Hayat Emeklilik', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'turkey_10', 'country_id': 'turkey', 'name': 'Quick Sigorta', 'is_global': False, 'inpatient_coverage': 70, 'outpatient_coverage': 55, 'drug_coverage': 65},
        {'id': 'turkey_11', 'country_id': 'turkey', 'name': 'Sompo Sigorta', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'turkey_12', 'country_id': 'turkey', 'name': 'April International', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80}
    ],
    'thailand': [
        {'id': 'thailand_1', 'country_id': 'thailand', 'name': 'AXA Thailand', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'thailand_2', 'country_id': 'thailand', 'name': 'Aetna International', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'thailand_3', 'country_id': 'thailand', 'name': 'Bupa Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'thailand_4', 'country_id': 'thailand', 'name': 'AIA Thailand', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'thailand_5', 'country_id': 'thailand', 'name': 'Thai Life Insurance', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'thailand_6', 'country_id': 'thailand', 'name': 'Thai Health Insurance PLC', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'thailand_7', 'country_id': 'thailand', 'name': 'Pacific Cross', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'thailand_8', 'country_id': 'thailand', 'name': 'Luma Health', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80},
        {'id': 'thailand_9', 'country_id': 'thailand', 'name': 'Allianz Ayudhya', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 65, 'drug_coverage': 75},
        {'id': 'thailand_10', 'country_id': 'thailand', 'name': 'MSIG Thailand', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 60, 'drug_coverage': 70},
        {'id': 'thailand_11', 'country_id': 'thailand', 'name': 'Cigna', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'thailand_12', 'country_id': 'thailand', 'name': 'April International', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 70, 'drug_coverage': 80}
    ],
    'canada': [
        {'id': 'canada_1', 'country_id': 'canada', 'name': 'Blue Cross (Ontario)', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'canada_2', 'country_id': 'canada', 'name': 'Manulife', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'canada_3', 'country_id': 'canada', 'name': 'Canada Life', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'canada_4', 'country_id': 'canada', 'name': 'Sun Life Financial', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'canada_5', 'country_id': 'canada', 'name': 'Desjardins', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'canada_6', 'country_id': 'canada', 'name': 'IA Financial Group', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'canada_7', 'country_id': 'canada', 'name': 'Green Shield Canada (GSC)', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'canada_8', 'country_id': 'canada', 'name': 'GMS (Group Medical Services)', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'canada_9', 'country_id': 'canada', 'name': 'RBC Insurance', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'canada_10', 'country_id': 'canada', 'name': 'Equitable Life of Canada', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'canada_11', 'country_id': 'canada', 'name': 'Empire Life', 'is_global': False, 'inpatient_coverage': 75, 'outpatient_coverage': 65, 'drug_coverage': 70},
        {'id': 'canada_12', 'country_id': 'canada', 'name': 'SSQ / Beneva', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75}
    ],
    'norway': [
        {'id': 'norway_1', 'country_id': 'norway', 'name': 'Bupa Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'norway_2', 'country_id': 'norway', 'name': 'AXA – Global Healthcare', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'norway_3', 'country_id': 'norway', 'name': 'If P&C Insurance', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'norway_4', 'country_id': 'norway', 'name': 'Gjensidige Forsikring', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'norway_5', 'country_id': 'norway', 'name': 'Storebrand', 'is_global': False, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80},
        {'id': 'norway_6', 'country_id': 'norway', 'name': 'DNB Livsforsikring', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'norway_7', 'country_id': 'norway', 'name': 'Protector Forsikring', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'norway_8', 'country_id': 'norway', 'name': 'Tryg Forsikring', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'norway_9', 'country_id': 'norway', 'name': 'Fremtind', 'is_global': False, 'inpatient_coverage': 80, 'outpatient_coverage': 70, 'drug_coverage': 75},
        {'id': 'norway_10', 'country_id': 'norway', 'name': 'Cigna Global', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'norway_11', 'country_id': 'norway', 'name': 'Allianz Care', 'is_global': True, 'inpatient_coverage': 90, 'outpatient_coverage': 80, 'drug_coverage': 85},
        {'id': 'norway_12', 'country_id': 'norway', 'name': 'April International', 'is_global': True, 'inpatient_coverage': 85, 'outpatient_coverage': 75, 'drug_coverage': 80}
    ]
}

CANCER_TYPES_DATA = [
    {'id': 'breast', 'name': 'Breast Cancer', 'category': 'common'},
    {'id': 'lung_nsclc', 'name': 'Lung Cancer (NSCLC)', 'category': 'common'},
    {'id': 'lung_sclc', 'name': 'Lung Cancer (SCLC)', 'category': 'common'},
    {'id': 'colorectal', 'name': 'Colorectal Cancer', 'category': 'common'},
    {'id': 'prostate', 'name': 'Prostate Cancer', 'category': 'common'},
    {'id': 'pancreatic', 'name': 'Pancreatic Cancer', 'category': 'common'},
    {'id': 'ovarian', 'name': 'Ovarian Cancer', 'category': 'common'},
    {'id': 'head_neck', 'name': 'Head & Neck Cancer', 'category': 'common'},
    {'id': 'leukemia_all', 'name': 'Leukemia (ALL)', 'category': 'rare'},
    {'id': 'leukemia_aml', 'name': 'Leukemia (AML)', 'category': 'rare'},
    {'id': 'leukemia_cll', 'name': 'Leukemia (CLL)', 'category': 'rare'},
    {'id': 'lymphoma', 'name': 'Lymphoma', 'category': 'common'},
    {'id': 'multiple_myeloma', 'name': 'Multiple Myeloma', 'category': 'rare'},
    {'id': 'gbm', 'name': 'Glioblastoma (GBM)', 'category': 'rare'},
    {'id': 'sarcoma', 'name': 'Sarcoma', 'category': 'rare'}
]

STAGES_DATA = [
    {'id': 'stage_1', 'name': 'Stage I (Localized)', 'description': 'Early stage, localized cancer'},
    {'id': 'stage_2', 'name': 'Stage II (Regional)', 'description': 'Cancer spread to nearby tissues'},
    {'id': 'stage_3', 'name': 'Stage III (Locally Advanced)', 'description': 'Cancer spread to nearby lymph nodes'},
    {'id': 'stage_4', 'name': 'Stage IV (Metastatic)', 'description': 'Cancer spread to distant organs'}
]

HOSPITAL_TIERS_DATA = [
    {'id': 'tier_1', 'name': 'Tier 1 - Quaternary Cancer Centre', 'multiplier': 1.3},
    {'id': 'tier_2', 'name': 'Tier 2 - Speciality Hospital', 'multiplier': 1.1},
    {'id': 'tier_3', 'name': 'Tier 3 - Regional Private Hospital', 'multiplier': 1.0}
]

BASE_COSTS_DATA = [
    {'country_id': 'india', 'surgery': 300000, 'chemo_per_cycle': 50000, 'radiation_per_fraction': 3000, 'transplant': 1500000, 'pet_ct': 25000, 'mri_ct': 8000, 'ngsp_panel': 100000, 'opd_consult': 1500, 'room_per_day': 3000, 'icu_per_day': 8000},
    {'country_id': 'usa', 'surgery': 50000, 'chemo_per_cycle': 10000, 'radiation_per_fraction': 500, 'transplant': 250000, 'pet_ct': 5000, 'mri_ct': 1500, 'ngsp_panel': 15000, 'opd_consult': 300, 'room_per_day': 2000, 'icu_per_day': 5000},
    {'country_id': 'singapore', 'surgery': 30000, 'chemo_per_cycle': 6000, 'radiation_per_fraction': 350, 'transplant': 150000, 'pet_ct': 3000, 'mri_ct': 1000, 'ngsp_panel': 10000, 'opd_consult': 200, 'room_per_day': 1200, 'icu_per_day': 3000},
    {'country_id': 'japan', 'surgery': 4500000, 'chemo_per_cycle': 750000, 'radiation_per_fraction': 45000, 'transplant': 20000000, 'pet_ct': 400000, 'mri_ct': 120000, 'ngsp_panel': 1500000, 'opd_consult': 30000, 'room_per_day': 150000, 'icu_per_day': 400000},
    {'country_id': 'france', 'surgery': 25000, 'chemo_per_cycle': 5000, 'radiation_per_fraction': 300, 'transplant': 120000, 'pet_ct': 2500, 'mri_ct': 800, 'ngsp_panel': 8000, 'opd_consult': 150, 'room_per_day': 1000, 'icu_per_day': 2500},
    {'country_id': 'turkey', 'surgery': 400000, 'chemo_per_cycle': 80000, 'radiation_per_fraction': 5000, 'transplant': 2000000, 'pet_ct': 40000, 'mri_ct': 15000, 'ngsp_panel': 150000, 'opd_consult': 3000, 'room_per_day': 20000, 'icu_per_day': 50000},
    {'country_id': 'thailand', 'surgery': 350000, 'chemo_per_cycle': 70000, 'radiation_per_fraction': 4500, 'transplant': 1800000, 'pet_ct': 35000, 'mri_ct': 12000, 'ngsp_panel': 140000, 'opd_consult': 2500, 'room_per_day': 18000, 'icu_per_day': 45000},
    {'country_id': 'canada', 'surgery': 45000, 'chemo_per_cycle': 9000, 'radiation_per_fraction': 450, 'transplant': 230000, 'pet_ct': 4500, 'mri_ct': 1400, 'ngsp_panel': 14000, 'opd_consult': 280, 'room_per_day': 1800, 'icu_per_day': 4500},
    {'country_id': 'norway', 'surgery': 400000, 'chemo_per_cycle': 80000, 'radiation_per_fraction': 4000, 'transplant': 2000000, 'pet_ct': 40000, 'mri_ct': 15000, 'ngsp_panel': 120000, 'opd_consult': 3000, 'room_per_day': 25000, 'icu_per_day': 60000}
]

ACCOMMODATION_COSTS_DATA = [
    {'country_id': 'india', 'budget': 1500, 'mid': 3500, 'premium': 8000},
    {'country_id': 'usa', 'budget': 80, 'mid': 150, 'premium': 300},
    {'country_id': 'singapore', 'budget': 60, 'mid': 120, 'premium': 250},
    {'country_id': 'japan', 'budget': 8000, 'mid': 15000, 'premium': 30000},
    {'country_id': 'france', 'budget': 70, 'mid': 130, 'premium': 280},
    {'country_id': 'turkey', 'budget': 1500, 'mid': 3000, 'premium': 7000},
    {'country_id': 'thailand', 'budget': 1200, 'mid': 2500, 'premium': 6000},
    {'country_id': 'canada', 'budget': 75, 'mid': 140, 'premium': 280},
    {'country_id': 'norway', 'budget': 900, 'mid': 1500, 'premium': 3000}
]
