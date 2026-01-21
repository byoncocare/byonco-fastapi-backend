# Multi-Country Cost Calculator - Current State Analysis

## A) 9 Countries Currently Supported

1. **India** (INR) - fx_rate: 83.0
2. **United States** (USD) - fx_rate: 1.0
3. **Singapore** (SGD) - fx_rate: 1.35
4. **Japan** (JPY) - fx_rate: 150.0
5. **France** (EUR) - fx_rate: 0.92
6. **Turkey** (TRY) - fx_rate: 32.0
7. **Thailand** (THB) - fx_rate: 35.0
8. **Canada** (CAD) - fx_rate: 1.38
9. **Norway** (NOK) - fx_rate: 11.0

## B) Current Baseline Gap Analysis

### ✅ What's Working
- All 9 countries have base costs defined in `DEFAULT_BASE_COSTS`
- All 9 countries have accommodation costs defined
- Exchange rates are defined for all countries
- Costs are already in local currency

### ❌ Critical Issues Found

1. **`get_country_data()` Bug**: 
   - Always returns `DEFAULT_COUNTRY` (India) regardless of input
   - Line 219: `return DEFAULT_COUNTRY` (hardcoded!)
   - This means ALL countries are treated as India

2. **Missing USD Conversion**:
   - Response model only has `total_cost_inr` (India-specific)
   - No `total_cost_usd` field
   - No USD breakdown

3. **Exchange Rate Source**:
   - Rates are hardcoded, no documentation of source
   - Need to document: "Reference exchange rates as of Dec 2025"

4. **Country Data Structure**:
   - No comprehensive country metadata
   - Missing: country-specific multipliers, city tier data

## C) Proposed Country-Cost Schema

```python
COUNTRY_DATA = {
    'india': {
        'id': 'india',
        'name': 'India',
        'currency_code': 'INR',
        'currency_symbol': '₹',
        'exchange_rate_to_usd': 83.0,  # 1 USD = 83 INR
        'exchange_rate_source': 'Reference rate as of Dec 2025',
        'data_quality': 'high',  # Most detailed
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
        'city_tier_available': False,  # Use national averages
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
            'default': 1.0,  # No city differentiation
        },
        'accommodation': {
            'budget': 80,
            'mid': 150,
            'premium': 300,
        },
    },
    # ... (similar structure for all 9 countries)
}
```

## D) Response Model Enhancement

Current:
```python
class CostCalculationResponse(BaseModel):
    total_cost_local: float
    total_cost_inr: float  # ❌ India-specific!
    ...
```

Proposed:
```python
class CostCalculationResponse(BaseModel):
    total_cost_local: float
    total_cost_usd: float  # ✅ USD conversion
    total_cost_inr: float  # ✅ Keep for backward compat
    currency_code: str
    currency_symbol: str
    breakdown_local: CostBreakdown
    breakdown_usd: CostBreakdown  # ✅ USD breakdown
    ...
```

## E) Implementation Plan

1. ✅ Create comprehensive `COUNTRY_DATA` structure
2. ✅ Fix `get_country_data()` to return correct country
3. ✅ Update response model to include USD fields
4. ✅ Update service to calculate USD values
5. ✅ Update frontend to display both currencies
6. ✅ Add country-specific tests
7. ✅ Document exchange rate source





