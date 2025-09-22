"""
Data quality utilities for education savings calculator.
Provides transparency features and data quality indicators.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class DataQuality(Enum):
    """Data quality levels based on years of historical data"""
    EXCELLENT = "excellent"      # 5+ years of data
    GOOD = "good"               # 3-4 years of data
    LIMITED = "limited"         # 2 years of data
    INSUFFICIENT = "insufficient"  # 1 year only


class ConfidenceLevel(Enum):
    """Confidence levels for projections"""
    HIGH = "high"       # Course-specific CAGR with good data
    MEDIUM = "medium"   # Course-specific CAGR with limited data
    LOW = "low"         # University average CAGR used


@dataclass
class DataTransparency:
    """Complete transparency information for a course analysis"""
    data_quality: DataQuality
    confidence_level: ConfidenceLevel
    years_of_data: int
    actual_data_years: List[int]
    latest_actual_year: int
    is_using_university_average: bool
    university_average_cagr: float
    course_specific_cagr: Optional[float]
    calculation_method: str
    source_verification: str


def assess_data_quality(years_of_data: int) -> DataQuality:
    """Assess data quality based on number of years"""
    if years_of_data >= 5:
        return DataQuality.EXCELLENT
    elif years_of_data >= 3:
        return DataQuality.GOOD
    elif years_of_data == 2:
        return DataQuality.LIMITED
    else:
        return DataQuality.INSUFFICIENT


def determine_confidence_level(data_quality: DataQuality, using_university_average: bool) -> ConfidenceLevel:
    """Determine confidence level based on data quality and calculation method"""
    if using_university_average:
        return ConfidenceLevel.LOW
    elif data_quality in [DataQuality.EXCELLENT, DataQuality.GOOD]:
        return ConfidenceLevel.HIGH
    else:
        return ConfidenceLevel.MEDIUM


def get_data_quality_badge(data_quality: DataQuality) -> tuple[str, str]:
    """Get emoji and color for data quality badge"""
    badges = {
        DataQuality.EXCELLENT: ("🟢", "#22c55e"),
        DataQuality.GOOD: ("🟡", "#eab308"),
        DataQuality.LIMITED: ("🟠", "#f97316"),
        DataQuality.INSUFFICIENT: ("🔴", "#ef4444")
    }
    return badges[data_quality]


def get_confidence_indicator(confidence_level: ConfidenceLevel) -> tuple[str, str]:
    """Get emoji and description for confidence level"""
    indicators = {
        ConfidenceLevel.HIGH: ("💎", "High confidence - course-specific data"),
        ConfidenceLevel.MEDIUM: ("⚡", "Medium confidence - limited course data"),
        ConfidenceLevel.LOW: ("⚠️", "Low confidence - university average used")
    }
    return indicators[confidence_level]


def get_projection_disclaimer(transparency: DataTransparency) -> str:
    """Generate appropriate disclaimer based on data transparency"""
    if transparency.confidence_level == ConfidenceLevel.LOW:
        return (
            f"⚠️ **Limited Course Data**: Only {transparency.years_of_data} year(s) of data available. "
            f"Using {transparency.calculation_method.lower()} for projections. "
            f"Actual fees may vary significantly."
        )
    elif transparency.confidence_level == ConfidenceLevel.MEDIUM:
        return (
            f"ℹ️ **Limited Historical Data**: Based on {transparency.years_of_data} years of course data "
            f"({min(transparency.actual_data_years)}-{max(transparency.actual_data_years)}). "
            f"Projections may have higher uncertainty."
        )
    else:
        return (
            f"✅ **Reliable Projections**: Based on {transparency.years_of_data} years of course-specific data "
            f"({min(transparency.actual_data_years)}-{max(transparency.actual_data_years)}). "
            f"Good confidence in projections."
        )


def get_calculation_explanation(transparency: DataTransparency) -> str:
    """Generate detailed explanation of how calculations are performed"""
    explanation = f"""
    **📊 Calculation Methodology:**

    **Data Source:** {transparency.years_of_data} years of historical fee data ({min(transparency.actual_data_years) if transparency.actual_data_years else 'N/A'}-{max(transparency.actual_data_years) if transparency.actual_data_years else 'N/A'})

    **Fee Growth Calculation:**
    """

    if not transparency.is_using_university_average:
        explanation += f"""
        - **Method:** Course-specific CAGR (Compound Annual Growth Rate)
        - **CAGR:** {transparency.course_specific_cagr*100:.2f}% annually
        - **Formula:** (Final Fee / Initial Fee)^(1/years) - 1
        - **Projection:** Latest fee × (1 + CAGR)^years_ahead
        """
    else:
        explanation += f"""
        - **Method:** University average CAGR (insufficient course data)
        - **University Average:** {transparency.university_average_cagr*100:.2f}% annually
        - **Note:** Course-specific data limited, using university-wide average
        - **Projection:** Latest available fee × (1 + Avg CAGR)^years_ahead
        """

    explanation += f"""

    **Exchange Rate Modeling:**
    - **Historical Trend:** 4.18% annual INR depreciation vs GBP (2017-2025)
    - **Projection Method:** Base rate × (1.0418)^years_ahead
    - **Base Rate (Sep 2025):** ₹119.14/£

    **Savings Calculation:**
    - **Early Conversion:** Fee × Early_FX_Rate
    - **Late Conversion:** Fee × Education_FX_Rate
    - **Savings:** Late_Cost - Early_Cost
    """

    return explanation


def generate_parent_verification_guide(university: str, programme: str) -> str:
    """Generate verification guide for parents"""
    guides = {
        'Oxford': f"""
**📋 How to Verify {university} {programme} Fees:**

1. **Official Oxford Website:**
   - Visit: www.ox.ac.uk/admissions/undergraduate/fees-and-funding
   - Search for: "overseas student fees {programme.lower()}"
   - Check: Current academic year fee schedules

2. **Direct Programme Pages:**
   - Search: "Oxford {programme} fees" in Google
   - Look for: Official ox.ac.uk domain links
   - Verify: Course-specific fee information

3. **Admissions Office Contact:**
   - Email: undergraduate.admissions@ox.ac.uk
   - Phone: +44 (0)1865 288000
   - Request: Current and projected fee information

**🔍 What to Look For:**
- "Overseas/International student" fee categories
- Academic year format (e.g., "2025/26")
- Any course-specific fee variations
""",

        'Cambridge': f"""
**📋 How to Verify {university} {programme} Fees:**

1. **Official Cambridge Website:**
   - Visit: www.undergraduate.study.cam.ac.uk/fees-and-costs
   - Search for: "overseas fees {programme.lower()}"
   - Check: Current fee tables and projections

2. **College-Specific Information:**
   - Note: Cambridge fees may vary slightly by college
   - Visit: Individual college websites for specific costs
   - Check: Additional college fees beyond university fees

3. **Admissions Contact:**
   - Email: admissions@cam.ac.uk
   - Phone: +44 (0)1223 333308
   - Request: Detailed fee breakdown for your programme

**🔍 What to Look For:**
- "Overseas student" fee schedules
- College fee supplements
- Laboratory/practical fees for science courses
""",

        'LSE': f"""
**📋 How to Verify {university} {programme} Fees:**

1. **Official LSE Website:**
   - Visit: info.lse.ac.uk/current-students/services/fees-and-funding
   - Search for: "overseas undergraduate fees"
   - Check: Programme-specific fee information

2. **Programme Pages:**
   - Search: "LSE {programme} fees" directly
   - Look for: Department-specific fee schedules
   - Note: Some programmes have premium pricing

3. **Student Services Contact:**
   - Email: studentservices@lse.ac.uk
   - Phone: +44 (0)20 7955 7162
   - Request: Current and projected fee information

**🔍 What to Look For:**
- "Non-EU/International" fee categories
- Programme-specific pricing tiers
- Additional costs for certain courses
"""
    }

    return guides.get(university, f"""
**📋 How to Verify {university} {programme} Fees:**

1. **Official University Website:**
   - Visit the official {university.lower()}.ac.uk website
   - Search for "international student fees" or "overseas fees"
   - Look for programme-specific fee information

2. **Direct Contact:**
   - Contact the admissions office directly
   - Request current and projected fee schedules
   - Ask for programme-specific cost breakdowns

3. **Verification Points:**
   - Confirm you're looking at "international/overseas" rates
   - Check the academic year format
   - Verify any course-specific variations
""")