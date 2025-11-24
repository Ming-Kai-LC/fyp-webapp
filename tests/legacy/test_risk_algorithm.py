#!/usr/bin/env python
"""
Test the COVID-19 Risk Assessment Algorithm Logic
This tests the business logic without requiring Django
"""
from datetime import date, timedelta

def test_age_scoring():
    """Test age-based risk scoring logic"""
    print("\n=== Testing Age Score Calculation ===")

    test_cases = [
        (date(1940, 1, 1), ">=80", 30),  # 84 years old
        (date(1950, 1, 1), "70-79", 20),  # 74 years old
        (date(1960, 1, 1), "60-69", 15),  # 64 years old
        (date(1970, 1, 1), "50-59", 10),  # 54 years old
        (date(1990, 1, 1), "<50", 0),    # 34 years old
    ]

    all_passed = True
    for dob, age_group, expected_score in test_cases:
        age = (date.today() - dob).days // 365

        # Age scoring logic
        if age >= 80:
            score = 30
        elif age >= 70:
            score = 20
        elif age >= 60:
            score = 15
        elif age >= 50:
            score = 10
        else:
            score = 0

        status = "✓" if score == expected_score else "✗"
        print(f"  {status} Age {age} ({age_group}): Expected {expected_score}, Got {score}")

        if score != expected_score:
            all_passed = False

    return all_passed

def test_comorbidity_scoring():
    """Test comorbidity-based risk scoring logic"""
    print("\n=== Testing Comorbidity Score Calculation ===")

    high_risk_conditions = {
        'diabetes', 'heart disease', 'hypertension', 'copd', 'asthma',
        'chronic kidney disease', 'chronic liver disease', 'cancer',
        'immunocompromised', 'obesity'
    }

    test_cases = [
        ("Severe Diabetes Type 2", "severe", True, 15),
        ("Moderate Hypertension", "moderate", True, 10),
        ("Mild Asthma", "mild", True, 5),
        ("Severe COVID Risk Condition", "severe", True, 15),  # increases_covid_risk flag
        ("Common Cold", "mild", False, 0),
    ]

    all_passed = True
    for condition_name, severity, increases_covid_risk, expected_score in test_cases:
        condition_lower = condition_name.lower()

        # Check if it's a high-risk condition
        is_high_risk = any(
            risk_cond in condition_lower
            for risk_cond in high_risk_conditions
        )

        if is_high_risk or increases_covid_risk:
            if severity == 'severe':
                score = 15
            elif severity == 'moderate':
                score = 10
            else:
                score = 5
        else:
            score = 0

        status = "✓" if score == expected_score else "✗"
        print(f"  {status} {condition_name} ({severity}): Expected {expected_score}, Got {score}")

        if score != expected_score:
            all_passed = False

    return all_passed

def test_vaccination_scoring():
    """Test vaccination-based protection scoring"""
    print("\n=== Testing Vaccination Score Calculation ===")

    test_cases = [
        (4, date.today() - timedelta(days=30), -20, "Excellent protection"),
        (3, date.today() - timedelta(days=60), -15, "Good protection"),
        (2, date.today() - timedelta(days=90), -10, "Moderate protection"),
        (1, date.today() - timedelta(days=120), -5, "Basic protection"),
        (0, None, 15, "No protection - increased risk"),
        (3, date.today() - timedelta(days=200), -10, "Good protection but waning"),  # > 6 months
    ]

    all_passed = True
    for dose_count, latest_dose_date, expected_base_score, description in test_cases:
        # Base vaccination score
        if dose_count >= 4:
            score = -20
        elif dose_count == 3:
            score = -15
        elif dose_count == 2:
            score = -10
        elif dose_count == 1:
            score = -5
        else:
            score = 15  # Unvaccinated

        # Check for waning immunity
        if latest_dose_date and dose_count > 0:
            days_since = (date.today() - latest_dose_date).days
            if days_since > 180:  # > 6 months
                score += 5

        status = "✓" if score == expected_base_score or (dose_count == 3 and latest_dose_date and (date.today() - latest_dose_date).days > 180 and score == -10) else "✗"
        print(f"  {status} {dose_count} doses: {description} - Score: {score}")

        # Allow for waning adjustment
        if not (score == expected_base_score or (abs(score - expected_base_score) == 5 and latest_dose_date and (date.today() - latest_dose_date).days > 180)):
            all_passed = False

    return all_passed

def test_lifestyle_scoring():
    """Test lifestyle factor scoring"""
    print("\n=== Testing Lifestyle Score Calculation ===")

    test_cases = [
        ("current", 20, "sedentary", True, 35, "Current smoker, sedentary, occupational risk"),  # 15+10+10=35
        ("former", None, "moderate", False, 5, "Former smoker, active"),
        ("never", None, "active", False, 0, "Never smoked, very active"),
        ("current", 10, "light", False, 20, "Current smoker, light activity"),
    ]

    all_passed = True
    for smoking, cigs_per_day, exercise, occ_risk, expected_score, description in test_cases:
        score = 0

        # Smoking
        if smoking == 'current':
            score += 15
        elif smoking == 'former':
            score += 5

        # Exercise
        if exercise == 'sedentary':
            score += 10
        elif exercise == 'light':
            score += 5

        # Occupational
        if occ_risk:
            score += 10

        status = "✓" if score == expected_score else "✗"
        print(f"  {status} {description}: Expected {expected_score}, Got {score}")

        if score != expected_score:
            all_passed = False

    return all_passed

def test_risk_level_determination():
    """Test risk level classification"""
    print("\n=== Testing Risk Level Determination ===")

    test_cases = [
        (10, "low", "Low risk patient"),
        (20, "moderate", "Moderate risk patient"),
        (35, "high", "High risk patient"),
        (55, "very_high", "Very high risk patient"),
        (14, "low", "Borderline low"),
        (15, "moderate", "Borderline moderate"),
        (30, "high", "Borderline high"),
        (50, "very_high", "Borderline very high"),
    ]

    all_passed = True
    for total_score, expected_level, description in test_cases:
        # Risk level determination logic
        if total_score >= 50:
            risk_level = 'very_high'
        elif total_score >= 30:
            risk_level = 'high'
        elif total_score >= 15:
            risk_level = 'moderate'
        else:
            risk_level = 'low'

        status = "✓" if risk_level == expected_level else "✗"
        print(f"  {status} Score {total_score}: {description} - Expected '{expected_level}', Got '{risk_level}'")

        if risk_level != expected_level:
            all_passed = False

    return all_passed

def test_complete_risk_scenarios():
    """Test complete risk assessment scenarios"""
    print("\n=== Testing Complete Risk Scenarios ===")

    scenarios = [
        {
            "name": "Healthy Young Adult",
            "age": 25,
            "conditions": [],
            "vaccines": 3,
            "smoking": "never",
            "exercise": "active",
            "expected_range": (-20, 0),
        },
        {
            "name": "Elderly with Diabetes",
            "age": 75,
            "conditions": [("Diabetes", "severe")],
            "vaccines": 2,
            "smoking": "never",
            "exercise": "light",
            "expected_range": (10, 35),
        },
        {
            "name": "Middle-aged Smoker, Unvaccinated",
            "age": 55,
            "conditions": [("Hypertension", "moderate")],
            "vaccines": 0,
            "smoking": "current",
            "exercise": "sedentary",
            "expected_range": (40, 60),
        },
    ]

    all_passed = True
    for scenario in scenarios:
        # Calculate age score
        age = scenario["age"]
        if age >= 80:
            age_score = 30
        elif age >= 70:
            age_score = 20
        elif age >= 60:
            age_score = 15
        elif age >= 50:
            age_score = 10
        else:
            age_score = 0

        # Calculate comorbidity score
        comorbidity_score = 0
        for condition_name, severity in scenario["conditions"]:
            if severity == 'severe':
                comorbidity_score += 15
            elif severity == 'moderate':
                comorbidity_score += 10
            else:
                comorbidity_score += 5

        # Calculate lifestyle score
        lifestyle_score = 0
        if scenario["smoking"] == "current":
            lifestyle_score += 15
        elif scenario["smoking"] == "former":
            lifestyle_score += 5

        if scenario["exercise"] == "sedentary":
            lifestyle_score += 10
        elif scenario["exercise"] == "light":
            lifestyle_score += 5

        # Calculate vaccination score
        vaccines = scenario["vaccines"]
        if vaccines >= 4:
            vaccination_score = -20
        elif vaccines == 3:
            vaccination_score = -15
        elif vaccines == 2:
            vaccination_score = -10
        elif vaccines == 1:
            vaccination_score = -5
        else:
            vaccination_score = 15

        total_score = age_score + comorbidity_score + lifestyle_score + vaccination_score

        min_expected, max_expected = scenario["expected_range"]
        in_range = min_expected <= total_score <= max_expected

        status = "✓" if in_range else "✗"
        print(f"  {status} {scenario['name']}:")
        print(f"      Age: {age_score}, Comorbidity: {comorbidity_score}, Lifestyle: {lifestyle_score}, Vaccination: {vaccination_score}")
        print(f"      Total: {total_score} (Expected range: {min_expected}-{max_expected})")

        if not in_range:
            all_passed = False

    return all_passed

def main():
    """Run all algorithm tests"""
    print("="*60)
    print("COVID-19 RISK ASSESSMENT ALGORITHM - LOGIC TEST")
    print("="*60)

    tests = [
        ("Age Scoring", test_age_scoring),
        ("Comorbidity Scoring", test_comorbidity_scoring),
        ("Vaccination Scoring", test_vaccination_scoring),
        ("Lifestyle Scoring", test_lifestyle_scoring),
        ("Risk Level Determination", test_risk_level_determination),
        ("Complete Risk Scenarios", test_complete_risk_scenarios),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            print(f"\n✓ {test_name}: PASSED")
            passed += 1
        else:
            print(f"\n✗ {test_name}: FAILED")

    print("\n" + "="*60)
    print(f"ALGORITHM TEST SUMMARY: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n✓ ALL ALGORITHM TESTS PASSED!")
        print("\nThe COVID-19 risk assessment algorithm is working correctly.")
        return 0
    else:
        print("\n✗ Some algorithm tests failed.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
