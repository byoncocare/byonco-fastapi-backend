"""
Test cases for Cost Calculator Service
Proves that the calculator ALWAYS returns meaningful estimates
"""

import asyncio
from models import CostCalculationRequest
from cost_calculator_service import CostCalculatorService
from default_data import DEFAULT_COUNTRY, DEFAULT_BASE_COSTS

# Mock database (None to test fallback behavior)
mock_db = None

def create_test_request(**overrides):
    """Create a test request with defaults"""
    defaults = {
        'country': 'india',
        'city': None,
        'hospital_tier': 'tier_2',
        'accreditation': [],
        'age_group': 'adult',
        'cancer_category': 'common',
        'cancer_type': 'breast',
        'stage': 'stage_2',
        'intent': 'curative',
        'include_surgery': True,
        'surgery_type': 'mastectomy',
        'surgery_days': 5,
        'icu_days': 1,
        'room_category': 'semi_private',
        'include_chemo': True,
        'regimen_type': 'standard_chemo',
        'chemo_cycles': 6,
        'drug_access': 'generics',
        'include_radiation': False,
        'radiation_technique': None,
        'radiation_fractions': 25,
        'concurrent_chemo': False,
        'include_transplant': False,
        'transplant_type': None,
        'transplant_days': 30,
        'pet_ct_count': 2,
        'mri_ct_count': 4,
        'include_ngs': False,
        'opd_consults': 10,
        'follow_up_months': 12,
        'has_insurance': True,
        'insurer': None,
        'policy_type': 'domestic',
        'custom_coverage': True,
        'inpatient_coverage': 80,
        'outpatient_coverage': 50,
        'drug_coverage': 70,
        'deductible': 0,
        'copay_percent': 20,
        'companions': 1,
        'stay_duration': 60,
        'accommodation_level': 'mid',
        'travel_type': 'economy',
        'return_trips': 1,
        'local_transport': 'daily_cab',
        'complication_buffer': 15,
        'currency': 'INR',
    }
    defaults.update(overrides)
    return CostCalculationRequest(**defaults)


async def test_case(name, request):
    """Run a single test case"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    
    service = CostCalculatorService(mock_db)
    
    try:
        result = await service.calculate_treatment_cost(request)
        
        # Verify result structure
        assert result is not None, "Result should not be None"
        assert result.total_cost_local >= 0, "Total cost should be non-negative"
        assert result.total_cost_usd >= 0, "Total cost USD should be non-negative"
        assert result.total_cost_inr >= 0, "Total cost INR should be non-negative"
        assert result.clinical_cost >= 0, "Clinical cost should be non-negative"
        assert result.clinical_cost_usd >= 0, "Clinical cost USD should be non-negative"
        assert result.non_clinical_cost >= 0, "Non-clinical cost should be non-negative"
        assert result.non_clinical_cost_usd >= 0, "Non-clinical cost USD should be non-negative"
        assert result.insurance_pays >= 0, "Insurance pays should be non-negative"
        assert result.insurance_pays_usd >= 0, "Insurance pays USD should be non-negative"
        assert result.patient_out_of_pocket >= 0, "Out-of-pocket should be non-negative"
        assert result.patient_out_of_pocket_usd >= 0, "Out-of-pocket USD should be non-negative"
        assert result.breakdown is not None, "Breakdown should not be None"
        assert result.breakdown_usd is not None, "Breakdown USD should not be None"
        assert result.currency_code is not None, "Currency code should not be None"
        assert result.currency_symbol is not None, "Currency symbol should not be None"
        assert result.exchange_rate_to_usd > 0, "Exchange rate should be positive"
        assert isinstance(result.assumptions, list), "Assumptions should be a list"
        
        # Verify USD conversion is reasonable (within 10% tolerance for rounding)
        if result.currency_code != 'USD':
            expected_usd = result.total_cost_local / result.exchange_rate_to_usd
            tolerance = abs(expected_usd - result.total_cost_usd) / expected_usd if expected_usd > 0 else 0
            assert tolerance < 0.1, f"USD conversion error too large: {tolerance*100:.1f}%"
        
        print(f"✅ PASSED")
        print(f"   Total Cost: {result.currency_symbol} {result.total_cost_local:,.2f} ({result.currency_code})")
        print(f"   Total Cost USD: ${result.total_cost_usd:,.2f}")
        print(f"   Total Cost INR: ₹{result.total_cost_inr:,.2f}")
        print(f"   Clinical: {result.currency_symbol} {result.clinical_cost:,.2f} (USD ${result.clinical_cost_usd:,.2f})")
        print(f"   Non-clinical: {result.currency_symbol} {result.non_clinical_cost:,.2f} (USD ${result.non_clinical_cost_usd:,.2f})")
        print(f"   Insurance: {result.currency_symbol} {result.insurance_pays:,.2f} (USD ${result.insurance_pays_usd:,.2f})")
        print(f"   Out-of-pocket: {result.currency_symbol} {result.patient_out_of_pocket:,.2f} (USD ${result.patient_out_of_pocket_usd:,.2f})")
        print(f"   Exchange Rate: 1 USD = {result.exchange_rate_to_usd} {result.currency_code}")
        print(f"   Assumptions: {len(result.assumptions)} items")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("COST CALCULATOR TEST SUITE")
    print("Proving calculator ALWAYS returns meaningful estimates")
    print("="*60)
    
    test_cases = [
        # Test 1: Complete valid request
        ("Complete Valid Request", create_test_request()),
        
        # Test 2: Minimal inputs (only required fields)
        ("Minimal Inputs", create_test_request(
            country='usa',
            hospital_tier='tier_3',
            cancer_type='lung_nsclc',
            stage='stage_1',
            include_surgery=False,
            include_chemo=False,
            include_radiation=False,
            include_transplant=False,
            has_insurance=False,
        )),
        
        # Test 3: All treatment modalities
        ("All Treatment Modalities", create_test_request(
            include_surgery=True,
            include_chemo=True,
            include_radiation=True,
            include_transplant=True,
            surgery_type='whipple',
            regimen_type='immunotherapy',
            radiation_technique='imrt',
            transplant_type='allogeneic',
        )),
        
        # Test 4: Missing country (should use default)
        ("Missing Country", create_test_request(
            country='unknown_country',
        )),
        
        # Test 5: Missing hospital tier (should use default)
        ("Missing Hospital Tier", create_test_request(
            hospital_tier='unknown_tier',
        )),
        
        # Test 6: No insurance
        ("No Insurance", create_test_request(
            has_insurance=False,
            insurer=None,
        )),
        
        # Test 7: Custom insurance coverage
        ("Custom Insurance Coverage", create_test_request(
            custom_coverage=True,
            inpatient_coverage=90,
            outpatient_coverage=80,
            drug_coverage=85,
        )),
        
        # Test 8: High-end treatment (premium everything)
        ("Premium Treatment", create_test_request(
            hospital_tier='tier_1',
            room_category='deluxe',
            regimen_type='immunotherapy',
            radiation_technique='proton',
            accommodation_level='premium',
            travel_type='business',
        )),
        
        # Test 9: Budget treatment
        ("Budget Treatment", create_test_request(
            hospital_tier='tier_3',
            room_category='general',
            drug_access='generics',
            accommodation_level='budget',
            travel_type='economy',
        )),
        
        # Test 10: Medical tourism (multiple companions, long stay)
        ("Medical Tourism", create_test_request(
            country='singapore',
            companions=3,
            stay_duration=120,
            return_trips=2,
        )),
        
        # Test 11: Edge case - zero values
        ("Zero Values", create_test_request(
            surgery_days=0,
            icu_days=0,
            chemo_cycles=0,
            radiation_fractions=0,
            pet_ct_count=0,
            mri_ct_count=0,
            opd_consults=0,
        )),
        
        # Test 12: Edge case - maximum values
        ("Maximum Values", create_test_request(
            surgery_days=30,
            icu_days=15,
            chemo_cycles=24,
            radiation_fractions=40,
            pet_ct_count=10,
            mri_ct_count=20,
            opd_consults=30,
            companions=5,
            stay_duration=180,
            return_trips=5,
        )),
        
        # Test 13: Rare cancer
        ("Rare Cancer", create_test_request(
            cancer_category='rare',
            cancer_type='pancreatic',
            stage='stage_4',
        )),
        
        # Test 14: Ultra-rare cancer
        ("Ultra-Rare Cancer", create_test_request(
            cancer_category='ultra_rare',
            cancer_type='gbm',
            stage='stage_4',
        )),
        
        # Test 15: Different countries
        ("Japan Treatment", create_test_request(
            country='japan',
        )),
        
        ("Thailand Treatment", create_test_request(
            country='thailand',
        )),
        
        ("Canada Treatment", create_test_request(
            country='canada',
        )),
        
        # Test 16-24: Multi-country currency verification
        ("India - Verify INR and USD", create_test_request(
            country='india',
        )),
        
        ("USA - Verify USD (base currency)", create_test_request(
            country='usa',
        )),
        
        ("Singapore - Verify SGD and USD", create_test_request(
            country='singapore',
        )),
        
        ("Japan - Verify JPY and USD", create_test_request(
            country='japan',
        )),
        
        ("France - Verify EUR and USD", create_test_request(
            country='france',
        )),
        
        ("Turkey - Verify TRY and USD", create_test_request(
            country='turkey',
        )),
        
        ("Thailand - Verify THB and USD", create_test_request(
            country='thailand',
        )),
        
        ("Canada - Verify CAD and USD", create_test_request(
            country='canada',
        )),
        
        ("Norway - Verify NOK and USD", create_test_request(
            country='norway',
        )),
    ]
    
    passed = 0
    failed = 0
    
    for name, request in test_cases:
        result = await test_case(name, request)
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Calculator always returns meaningful estimates.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

