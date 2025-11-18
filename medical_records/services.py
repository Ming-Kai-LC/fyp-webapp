"""
Service layer for medical records business logic
"""
from datetime import date, datetime
from typing import Dict, Tuple
from django.db.models import Q
from .models import COVIDRiskScore


class RiskAssessmentService:
    """
    Calculate COVID-19 risk scores based on patient medical history
    """

    # High-risk conditions that increase COVID-19 severity
    HIGH_RISK_CONDITIONS = {
        'diabetes', 'heart disease', 'hypertension', 'copd', 'asthma',
        'chronic kidney disease', 'chronic liver disease', 'cancer',
        'immunocompromised', 'obesity', 'sickle cell', 'cerebrovascular disease'
    }

    @staticmethod
    def calculate_age_score(patient) -> Tuple[int, str]:
        """
        Calculate age-based risk score
        Returns: (score, description)
        """
        if not patient.date_of_birth:
            return 0, "Age not available"

        age = (date.today() - patient.date_of_birth).days // 365

        if age >= 80:
            return 30, f"Age {age} - Very High Risk"
        elif age >= 70:
            return 20, f"Age {age} - High Risk"
        elif age >= 60:
            return 15, f"Age {age} - Moderate Risk"
        elif age >= 50:
            return 10, f"Age {age} - Mild Risk"
        else:
            return 0, f"Age {age} - Low Risk"

    @staticmethod
    def calculate_comorbidity_score(patient) -> Tuple[int, Dict]:
        """
        Calculate comorbidity-based risk score
        Returns: (score, details)
        """
        score = 0
        details = {
            'high_risk_conditions': [],
            'other_conditions': [],
            'severe_conditions_count': 0
        }

        # Get active and chronic conditions
        conditions = patient.medical_conditions.filter(
            Q(status='active') | Q(status='chronic')
        )

        for condition in conditions:
            condition_lower = condition.condition_name.lower()

            # Check if it's a high-risk condition
            is_high_risk = any(
                risk_cond in condition_lower
                for risk_cond in RiskAssessmentService.HIGH_RISK_CONDITIONS
            )

            if is_high_risk or condition.increases_covid_risk:
                if condition.severity == 'severe':
                    score += 15
                    details['severe_conditions_count'] += 1
                elif condition.severity == 'moderate':
                    score += 10
                else:
                    score += 5

                details['high_risk_conditions'].append({
                    'name': condition.condition_name,
                    'severity': condition.severity,
                    'score_added': 15 if condition.severity == 'severe' else (10 if condition.severity == 'moderate' else 5)
                })
            else:
                details['other_conditions'].append(condition.condition_name)

        return score, details

    @staticmethod
    def calculate_lifestyle_score(patient) -> Tuple[int, Dict]:
        """
        Calculate lifestyle-based risk score
        Returns: (score, details)
        """
        score = 0
        details = {
            'smoking': 'No data',
            'exercise': 'No data',
            'occupational_risk': False
        }

        try:
            lifestyle = patient.lifestyle_info
        except:
            return 0, details

        # Smoking risk
        if lifestyle.smoking_status == 'current':
            score += 15
            details['smoking'] = f'Current smoker - {lifestyle.cigarettes_per_day or "unknown"} per day'
        elif lifestyle.smoking_status == 'former':
            score += 5
            details['smoking'] = 'Former smoker'
        else:
            details['smoking'] = 'Never smoked'

        # Exercise level (sedentary increases risk)
        if lifestyle.exercise_level == 'sedentary':
            score += 10
            details['exercise'] = 'Sedentary lifestyle'
        elif lifestyle.exercise_level == 'light':
            score += 5
            details['exercise'] = 'Light activity'
        else:
            details['exercise'] = f'{lifestyle.get_exercise_level_display()}'

        # Occupational exposure
        if lifestyle.occupational_exposure_risk:
            score += 10
            details['occupational_risk'] = True

        return score, details

    @staticmethod
    def calculate_vaccination_score(patient) -> Tuple[int, Dict]:
        """
        Calculate vaccination protection score (negative score = protection)
        Returns: (score, details)
        """
        score = 0
        details = {
            'covid_doses': 0,
            'latest_dose': None,
            'protection_level': 'None'
        }

        # Get COVID-19 vaccinations
        covid_vaccines = patient.vaccinations.filter(
            vaccine_name__startswith='covid19'
        ).order_by('-administered_date')

        covid_dose_count = covid_vaccines.count()
        details['covid_doses'] = covid_dose_count

        if covid_dose_count >= 4:
            score = -20  # Good protection
            details['protection_level'] = 'Excellent'
        elif covid_dose_count == 3:
            score = -15
            details['protection_level'] = 'Good'
        elif covid_dose_count == 2:
            score = -10
            details['protection_level'] = 'Moderate'
        elif covid_dose_count == 1:
            score = -5
            details['protection_level'] = 'Basic'
        else:
            score = 15  # Not vaccinated increases risk
            details['protection_level'] = 'None - Increased Risk'

        if covid_vaccines.exists():
            latest = covid_vaccines.first()
            details['latest_dose'] = latest.administered_date.isoformat()

            # Check if vaccination is recent (within 6 months)
            days_since_vaccination = (date.today() - latest.administered_date).days
            if days_since_vaccination > 180:
                score += 5  # Waning immunity
                details['protection_level'] += ' (Waning)'

        return score, details

    @staticmethod
    def determine_risk_level(total_score: int) -> str:
        """
        Determine risk level based on total score
        """
        if total_score >= 50:
            return 'very_high'
        elif total_score >= 30:
            return 'high'
        elif total_score >= 15:
            return 'moderate'
        else:
            return 'low'

    @staticmethod
    def generate_recommendations(total_score: int, risk_level: str, details: Dict) -> str:
        """
        Generate personalized recommendations based on risk assessment
        """
        recommendations = []

        # Vaccination recommendations
        vacc_details = details.get('vaccination', {})
        if vacc_details.get('covid_doses', 0) < 2:
            recommendations.append("⚠️ PRIORITY: Complete COVID-19 vaccination series immediately")
        elif vacc_details.get('protection_level', '').endswith('(Waning)'):
            recommendations.append("🔄 Consider getting a COVID-19 booster shot")

        # High-risk conditions
        comorb_details = details.get('comorbidity', {})
        if comorb_details.get('high_risk_conditions'):
            recommendations.append("🏥 Regular monitoring required due to high-risk conditions")
            recommendations.append("💊 Ensure all chronic conditions are well-managed")

        # Lifestyle modifications
        lifestyle_details = details.get('lifestyle', {})
        if 'Current smoker' in lifestyle_details.get('smoking', ''):
            recommendations.append("🚭 Smoking cessation strongly recommended")

        if lifestyle_details.get('exercise') == 'Sedentary lifestyle':
            recommendations.append("🏃 Increase physical activity to improve overall health")

        if lifestyle_details.get('occupational_risk'):
            recommendations.append("😷 Use appropriate PPE at work due to occupational exposure risk")

        # General recommendations based on risk level
        if risk_level in ['high', 'very_high']:
            recommendations.append("🛡️ Maintain strict preventive measures (masking, distancing)")
            recommendations.append("🩺 Consult with healthcare provider about antiviral medications")
            recommendations.append("📞 Have a plan for immediate medical care if symptoms develop")
        elif risk_level == 'moderate':
            recommendations.append("😷 Consider masking in crowded indoor settings")
            recommendations.append("🧼 Practice good hand hygiene")
        else:
            recommendations.append("✅ Continue standard preventive measures")
            recommendations.append("🧼 Maintain good hygiene practices")

        return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))

    @classmethod
    def calculate_risk_score(cls, patient, user) -> COVIDRiskScore:
        """
        Main method to calculate comprehensive COVID-19 risk score
        Returns: COVIDRiskScore instance
        """
        # Calculate individual scores
        age_score, age_details = cls.calculate_age_score(patient)
        comorbidity_score, comorbidity_details = cls.calculate_comorbidity_score(patient)
        lifestyle_score, lifestyle_details = cls.calculate_lifestyle_score(patient)
        vaccination_score, vaccination_details = cls.calculate_vaccination_score(patient)

        # Calculate total score
        total_score = age_score + comorbidity_score + lifestyle_score + vaccination_score

        # Determine risk level
        risk_level = cls.determine_risk_level(total_score)

        # Compile details
        risk_factors = {
            'age': {
                'score': age_score,
                'details': age_details
            },
            'comorbidity': {
                'score': comorbidity_score,
                'details': comorbidity_details
            },
            'lifestyle': {
                'score': lifestyle_score,
                'details': lifestyle_details
            },
            'vaccination': {
                'score': vaccination_score,
                'details': vaccination_details
            }
        }

        # Generate recommendations
        recommendations = cls.generate_recommendations(total_score, risk_level, risk_factors)

        # Create and save risk score
        risk_score = COVIDRiskScore.objects.create(
            patient=patient,
            calculated_by=user,
            age_score=age_score,
            comorbidity_score=comorbidity_score,
            lifestyle_score=lifestyle_score,
            vaccination_score=vaccination_score,
            total_score=total_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations
        )

        return risk_score
