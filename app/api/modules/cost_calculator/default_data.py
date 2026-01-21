"""
Default cost data for fallback when MongoDB data is unavailable.
This ensures the calculator ALWAYS returns meaningful estimates.

Multi-country pricing data with country-specific baselines.
Exchange rates: Reference rates as of December 2025
Source: Conservative national averages for each country
"""

# ============================================================================
# COMPREHENSIVE COUNTRY DATA
# ============================================================================
# Each country has complete metadata including currency, exchange rates,
# base costs, multipliers, and data quality indicators

COUNTRY_DATA = {
    'india': {
        'id': 'india',
        'name': 'India',
        'currency_code': 'INR',
        'currency_symbol': '₹',
        'exchange_rate_to_usd': 89.899376,  # 1 USD = 89.899376 INR (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'high',  # Most detailed dataset
        'city_tier_available': True,
        'base_costs': {
            'surgery': 300000,
            'chemo_per_cycle': 50000,
            'radiation_per_fraction': 3000,
            'transplant': 1500000,
            'pet_ct': 25000,
            'mri_ct': 8000,
            'ngsp_panel': 100000,
            'opd_consult': 1500,
            'room_per_day': 3000,
            'icu_per_day': 8000,
        },
        'city_tier_multipliers': {
            'metro': 1.2,      # Delhi, Mumbai, Bangalore
            'tier1': 1.0,      # Chennai, Hyderabad, Pune
            'tier2': 0.9,      # Tier-2 cities
            'tier3': 0.85,     # Tier-3 cities
        },
        'accommodation': {
            'budget': 1500,
            'mid': 3500,
            'premium': 8000,
        },
    },
    'usa': {
        'id': 'usa',
        'name': 'United States',
        'currency_code': 'USD',
        'currency_symbol': '$',
        'exchange_rate_to_usd': 1.0,
        'exchange_rate_source': 'USD is base currency',
        'data_quality': 'medium',  # National averages
        'city_tier_available': False,
        'base_costs': {
            'surgery': 50000,
            'chemo_per_cycle': 10000,
            'radiation_per_fraction': 500,
            'transplant': 250000,
            'pet_ct': 5000,
            'mri_ct': 1500,
            'ngsp_panel': 15000,
            'opd_consult': 300,
            'room_per_day': 2000,
            'icu_per_day': 5000,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 80,
            'mid': 150,
            'premium': 300,
        },
    },
    'singapore': {
        'id': 'singapore',
        'name': 'Singapore',
        'currency_code': 'SGD',
        'currency_symbol': 'S$',
        'exchange_rate_to_usd': 1.285576,  # 1 USD = 1.285576 SGD (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 30000,
            'chemo_per_cycle': 6000,
            'radiation_per_fraction': 350,
            'transplant': 150000,
            'pet_ct': 3000,
            'mri_ct': 1000,
            'ngsp_panel': 10000,
            'opd_consult': 200,
            'room_per_day': 1200,
            'icu_per_day': 3000,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 60,
            'mid': 120,
            'premium': 250,
        },
    },
    'japan': {
        'id': 'japan',
        'name': 'Japan',
        'currency_code': 'JPY',
        'currency_symbol': '¥',
        'exchange_rate_to_usd': 156.087734,  # 1 USD = 156.087734 JPY (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 4500000,
            'chemo_per_cycle': 750000,
            'radiation_per_fraction': 45000,
            'transplant': 20000000,
            'pet_ct': 400000,
            'mri_ct': 120000,
            'ngsp_panel': 1500000,
            'opd_consult': 30000,
            'room_per_day': 150000,
            'icu_per_day': 400000,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 8000,
            'mid': 15000,
            'premium': 30000,
        },
    },
    'france': {
        'id': 'france',
        'name': 'France',
        'currency_code': 'EUR',
        'currency_symbol': '€',
        'exchange_rate_to_usd': 0.849550,  # 1 USD = 0.849550 EUR (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 25000,
            'chemo_per_cycle': 5000,
            'radiation_per_fraction': 300,
            'transplant': 120000,
            'pet_ct': 2500,
            'mri_ct': 800,
            'ngsp_panel': 8000,
            'opd_consult': 150,
            'room_per_day': 1000,
            'icu_per_day': 2500,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 70,
            'mid': 130,
            'premium': 280,
        },
    },
    'turkey': {
        'id': 'turkey',
        'name': 'Turkey',
        'currency_code': 'TRY',
        'currency_symbol': '₺',
        'exchange_rate_to_usd': 42.930601,  # 1 USD = 42.930601 TRY (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 400000,
            'chemo_per_cycle': 80000,
            'radiation_per_fraction': 5000,
            'transplant': 2000000,
            'pet_ct': 40000,
            'mri_ct': 15000,
            'ngsp_panel': 150000,
            'opd_consult': 3000,
            'room_per_day': 20000,
            'icu_per_day': 50000,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 1500,
            'mid': 3000,
            'premium': 7000,
        },
    },
    'thailand': {
        'id': 'thailand',
        'name': 'Thailand',
        'currency_code': 'THB',
        'currency_symbol': '฿',
        'exchange_rate_to_usd': 31.686234,  # 1 USD = 31.686234 THB (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 350000,
            'chemo_per_cycle': 70000,
            'radiation_per_fraction': 4500,
            'transplant': 1800000,
            'pet_ct': 35000,
            'mri_ct': 12000,
            'ngsp_panel': 140000,
            'opd_consult': 2500,
            'room_per_day': 18000,
            'icu_per_day': 45000,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 1200,
            'mid': 2500,
            'premium': 6000,
        },
    },
    'canada': {
        'id': 'canada',
        'name': 'Canada',
        'currency_code': 'CAD',
        'currency_symbol': 'C$',
        'exchange_rate_to_usd': 1.369706,  # 1 USD = 1.369706 CAD (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 45000,
            'chemo_per_cycle': 9000,
            'radiation_per_fraction': 450,
            'transplant': 230000,
            'pet_ct': 4500,
            'mri_ct': 1400,
            'ngsp_panel': 14000,
            'opd_consult': 280,
            'room_per_day': 1800,
            'icu_per_day': 4500,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 75,
            'mid': 140,
            'premium': 280,
        },
    },
    'norway': {
        'id': 'norway',
        'name': 'Norway',
        'currency_code': 'NOK',
        'currency_symbol': 'kr',
        'exchange_rate_to_usd': 10.044163,  # 1 USD = 10.044163 NOK (Dec 29, 2025)
        'exchange_rate_source': 'Reference rate as of Dec 29, 2025 21:01 UTC',
        'data_quality': 'medium',
        'city_tier_available': False,
        'base_costs': {
            'surgery': 400000,
            'chemo_per_cycle': 80000,
            'radiation_per_fraction': 4000,
            'transplant': 2000000,
            'pet_ct': 40000,
            'mri_ct': 15000,
            'ngsp_panel': 120000,
            'opd_consult': 3000,
            'room_per_day': 25000,
            'icu_per_day': 60000,
        },
        'city_tier_multipliers': {
            'default': 1.0,
        },
        'accommodation': {
            'budget': 900,
            'mid': 1500,
            'premium': 3000,
        },
    },
}

# Legacy support - maintain backward compatibility
DEFAULT_COUNTRY = COUNTRY_DATA['india']

# Legacy support - extract base costs for backward compatibility
DEFAULT_BASE_COSTS = {
    country_id: country_data['base_costs']
    for country_id, country_data in COUNTRY_DATA.items()
}

# Default hospital tier multipliers
HOSPITAL_TIER_MULTIPLIERS = {
    'tier_1': 1.3,
    'tier_2': 1.1,
    'tier_3': 1.0,
}

DEFAULT_HOSPITAL_TIER_MULTIPLIER = 1.0

# Default room category multipliers
ROOM_CATEGORY_MULTIPLIERS = {
    'general': 0.8,
    'semi_private': 1.0,
    'private': 1.5,
    'deluxe': 2.0,
}

# Default regimen multipliers
REGIMEN_MULTIPLIERS = {
    'standard_chemo': 1.0,
    'targeted': 2.5,
    'immunotherapy': 3.5,
    'oral_tki': 2.0,
    'combination': 4.0,
}

# Default drug access multipliers
DRUG_ACCESS_MULTIPLIERS = {
    'originator': 1.0,
    'generics': 0.6,
    'biosimilars': 0.7,
}

# Default radiation technique multipliers
RADIATION_TECHNIQUE_MULTIPLIERS = {
    '2d': 0.5,
    '3d_crt': 1.0,
    'imrt': 1.5,
    'vmat': 1.8,
    'sbrt': 2.5,
    'proton': 5.0,
}

# Default transplant type multipliers
TRANSPLANT_TYPE_MULTIPLIERS = {
    'autologous': 1.0,
    'allogeneic': 1.8,
}

# Legacy support - extract accommodation costs for backward compatibility
DEFAULT_ACCOMMODATION_COSTS = {
    country_id: country_data['accommodation']
    for country_id, country_data in COUNTRY_DATA.items()
}

# Default travel multipliers
TRAVEL_TYPE_MULTIPLIERS = {
    'economy': 1.0,
    'premium': 1.8,
    'business': 3.5,
}

BASE_FLIGHT_COST_USD = 500

# Default local transport costs (per day, in USD)
LOCAL_TRANSPORT_COSTS = {
    'daily_cab': 30,
    'public': 10,
    'hospital_shuttle': 5,
}

FOOD_COST_PER_DAY_USD = 50

# Default insurance coverage
DEFAULT_INSURANCE_COVERAGE = {
    'inpatient_coverage': 80,
    'outpatient_coverage': 50,
    'drug_coverage': 70,
}


def get_country_data(country_id: str = None):
    """Get country data with fallback - FIXED to return correct country"""
    if not country_id:
        return COUNTRY_DATA.get('india', DEFAULT_COUNTRY)
    # Return the actual country data, not always India!
    return COUNTRY_DATA.get(country_id, DEFAULT_COUNTRY)


def get_base_costs(country_id: str = None):
    """Get base costs with fallback"""
    if not country_id:
        country_id = 'india'
    country_data = COUNTRY_DATA.get(country_id, COUNTRY_DATA['india'])
    return country_data.get('base_costs', DEFAULT_BASE_COSTS.get('india', {}))


def get_accommodation_costs(country_id: str = None):
    """Get accommodation costs with fallback"""
    if not country_id:
        country_id = 'india'
    country_data = COUNTRY_DATA.get(country_id, COUNTRY_DATA['india'])
    return country_data.get('accommodation', DEFAULT_ACCOMMODATION_COSTS.get('india', {}))


def normalize_number(value, default=0, min_val=0):
    """Normalize a number (handle NaN, null, negative)"""
    try:
        num = float(value) if value is not None else default
        if num != num:  # Check for NaN
            num = default
        return max(min_val, num)
    except (ValueError, TypeError):
        return default


def clamp_number(value, min_val, max_val):
    """Clamp a number to a range"""
    return min(max(value, min_val), max_val)

