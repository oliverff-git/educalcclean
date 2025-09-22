"""
Data processor for education savings calculator.
Handles loading fees data and calculating course-specific CAGRs.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import data quality utilities
from gui.data_quality_utils import (
    DataQuality, ConfidenceLevel, DataTransparency,
    assess_data_quality, determine_confidence_level,
    generate_parent_verification_guide
)


class EducationDataProcessor:
    """Processes education fees and exchange rate data for the GUI."""

    def __init__(self, data_dir: str = "data"):
        """Initialize with data directory path."""
        self.data_dir = Path(project_root) / data_dir
        self.fees_df = None
        self.fx_df = None
        self.savings_df = None
        self.course_cagrs = {}
        self.university_cagrs = {}

    def load_data(self):
        """Load all required data files."""
        print("Loading education data...")

        # Load fees data
        fees_path = self.data_dir / "fees" / "comprehensive_fees_2020_2026.csv"
        self.fees_df = pd.read_csv(fees_path)

        # Filter for overseas students only
        self.fees_df = self.fees_df[self.fees_df['fee_status'] == 'overseas'].copy()

        # Convert academic year to numeric year
        self.fees_df['year'] = self.fees_df['academic_year'].str[:4].astype(int)

        # Load exchange rate data
        fx_path = self.data_dir / "fx" / "twelvedata" / "GBPINR_monthly_twelvedata.csv"
        self.fx_df = pd.read_csv(fx_path)
        self.fx_df['month'] = pd.to_datetime(self.fx_df['month'])
        self.fx_df['year'] = self.fx_df['month'].dt.year

        # Load UK interest rates
        savings_path = self.data_dir / "savings" / "boe_official_rates_corrected.csv"
        self.savings_df = pd.read_csv(savings_path)
        self.savings_df['month'] = pd.to_datetime(self.savings_df['month'] + '-01')
        self.savings_df['year'] = self.savings_df['month'].dt.year

        print(f"Loaded {len(self.fees_df)} fee records")
        print(f"Universities: {self.fees_df['university'].unique()}")

    def get_universities(self) -> List[str]:
        """Get list of available universities."""
        if self.fees_df is None:
            self.load_data()
        return sorted(self.fees_df['university'].unique())

    def get_courses(self, university: str) -> List[str]:
        """Get list of courses for a specific university."""
        if self.fees_df is None:
            self.load_data()

        uni_data = self.fees_df[self.fees_df['university'] == university]
        return sorted(uni_data['programme'].unique())

    def calculate_course_cagr(self, university: str, programme: str) -> float:
        """Calculate CAGR for a specific course over available data period."""
        if self.fees_df is None:
            self.load_data()

        # Filter for specific course
        course_data = self.fees_df[
            (self.fees_df['university'] == university) &
            (self.fees_df['programme'] == programme)
        ].sort_values('year')

        if len(course_data) < 2:
            # If insufficient data, use university average
            return self.get_university_cagr(university)

        # Calculate CAGR from first to last available year
        initial_fee = course_data.iloc[0]['fee_gbp']
        final_fee = course_data.iloc[-1]['fee_gbp']
        years = course_data.iloc[-1]['year'] - course_data.iloc[0]['year']

        if years <= 0 or initial_fee <= 0:
            return self.get_university_cagr(university)

        cagr = (final_fee / initial_fee) ** (1 / years) - 1

        # Cache the result
        key = f"{university}_{programme}"
        self.course_cagrs[key] = cagr

        return cagr

    def get_university_cagr(self, university: str) -> float:
        """Calculate average CAGR for all courses in a university."""
        if university in self.university_cagrs:
            return self.university_cagrs[university]

        if self.fees_df is None:
            self.load_data()

        uni_data = self.fees_df[self.fees_df['university'] == university]
        course_cagrs = []

        for programme in uni_data['programme'].unique():
            course_data = uni_data[uni_data['programme'] == programme].sort_values('year')

            if len(course_data) >= 2:
                initial_fee = course_data.iloc[0]['fee_gbp']
                final_fee = course_data.iloc[-1]['fee_gbp']
                years = course_data.iloc[-1]['year'] - course_data.iloc[0]['year']

                if years > 0 and initial_fee > 0:
                    cagr = (final_fee / initial_fee) ** (1 / years) - 1
                    course_cagrs.append(cagr)

        if course_cagrs:
            avg_cagr = np.mean(course_cagrs)
        else:
            # Fallback to default university CAGRs from analysis
            fallback_cagrs = {
                'Cambridge': 0.0501,  # 5.01%
                'Oxford': 0.0845,     # 8.45%
                'LSE': 0.0505         # 5.05%
            }
            avg_cagr = fallback_cagrs.get(university, 0.06)  # 6% default

        self.university_cagrs[university] = avg_cagr
        return avg_cagr

    def get_latest_fee(self, university: str, programme: str) -> float:
        """Get the most recent fee for a course (typically 2025)."""
        if self.fees_df is None:
            self.load_data()

        course_data = self.fees_df[
            (self.fees_df['university'] == university) &
            (self.fees_df['programme'] == programme)
        ].sort_values('year', ascending=False)

        if len(course_data) > 0:
            return course_data.iloc[0]['fee_gbp']

        # Fallback to university average if course not found
        uni_data = self.fees_df[self.fees_df['university'] == university]
        latest_year = uni_data['year'].max()
        latest_fees = uni_data[uni_data['year'] == latest_year]['fee_gbp']

        return latest_fees.mean() if len(latest_fees) > 0 else 40000  # £40k fallback

    def project_fee(self, university: str, programme: str, target_year: int) -> float:
        """Project fee for a specific course in a target year."""
        # Get course-specific data to find actual latest year
        course_data = self.fees_df[
            (self.fees_df['university'] == university) &
            (self.fees_df['programme'] == programme)
        ].sort_values('year', ascending=False)

        if len(course_data) > 0:
            # Use actual latest year for this course
            base_year = course_data.iloc[0]['year']
            base_fee = course_data.iloc[0]['fee_gbp']
        else:
            # Fallback if course not found
            base_fee = self.get_latest_fee(university, programme)
            base_year = self.fees_df['year'].max()

        # Get course-specific CAGR
        cagr = self.calculate_course_cagr(university, programme)

        years_ahead = target_year - base_year

        if years_ahead <= 0:
            return base_fee

        # Project using CAGR
        projected_fee = base_fee * (1 + cagr) ** years_ahead

        return projected_fee

    def get_september_fx_rate(self, year: int) -> float:
        """Get September exchange rate for a specific year."""
        if self.fx_df is None:
            self.load_data()

        # Get September rate for the year
        sept_data = self.fx_df[
            (self.fx_df['year'] == year) &
            (self.fx_df['month'].dt.month == 9)
        ]

        if len(sept_data) > 0:
            return sept_data.iloc[0]['gbp_inr']

        # If September data not available, get closest rate
        year_data = self.fx_df[self.fx_df['year'] == year]
        if len(year_data) > 0:
            return year_data['gbp_inr'].mean()

        # Fallback to projection based on historical trend
        return self.project_fx_rate(year)

    def project_fx_rate(self, target_year: int) -> float:
        """Project exchange rate for future years based on historical trend."""
        if self.fx_df is None:
            self.load_data()

        # Use historical CAGR of 4.18% (2017-2025 analysis - conservative)
        fx_cagr = 0.0418

        # Base rate (September 2025)
        base_rate = 119.14  # From analysis
        base_year = 2025

        years_ahead = target_year - base_year

        if years_ahead <= 0:
            return self.get_september_fx_rate(target_year)

        projected_rate = base_rate * (1 + fx_cagr) ** years_ahead

        return projected_rate

    def get_uk_interest_rate(self, year: int) -> float:
        """Get UK Bank Base Rate for a specific year."""
        if self.savings_df is None:
            self.load_data()

        # Get average rate for the year
        year_data = self.savings_df[self.savings_df['year'] == year]
        if len(year_data) > 0:
            return year_data['bank_base_rate'].mean()

        # If no data for year, get most recent rate
        latest_data = self.savings_df.sort_values('year', ascending=False)
        if len(latest_data) > 0:
            return latest_data['bank_base_rate'].iloc[0]

        # Fallback
        return 0.04  # 4% fallback

    def get_course_info(self, university: str, programme: str) -> Dict:
        """Get comprehensive information about a course with full transparency."""
        if self.fees_df is None:
            self.load_data()

        # Get historical data
        course_data = self.fees_df[
            (self.fees_df['university'] == university) &
            (self.fees_df['programme'] == programme)
        ].sort_values('year')

        # Calculate metrics
        course_cagr = None
        is_using_university_average = False

        if len(course_data) >= 2:
            # Can calculate course-specific CAGR
            initial_fee = course_data.iloc[0]['fee_gbp']
            final_fee = course_data.iloc[-1]['fee_gbp']
            years = course_data.iloc[-1]['year'] - course_data.iloc[0]['year']
            if years > 0:
                course_cagr = (final_fee / initial_fee) ** (1 / years) - 1

        # Determine what CAGR to use
        if course_cagr is not None:
            used_cagr = course_cagr
            is_using_university_average = False
        else:
            used_cagr = self.get_university_cagr(university)
            is_using_university_average = True

        # Get latest fee information
        latest_fee = self.get_latest_fee(university, programme)
        latest_actual_year = course_data['year'].max() if len(course_data) > 0 else None

        # Historical fees by year
        historical_fees = {}
        actual_data_years = []
        for _, row in course_data.iterrows():
            historical_fees[row['year']] = row['fee_gbp']
            actual_data_years.append(row['year'])

        # Assess data quality
        years_of_data = len(course_data)
        data_quality = assess_data_quality(years_of_data)
        confidence_level = determine_confidence_level(data_quality, is_using_university_average)

        # Create transparency object
        transparency = DataTransparency(
            data_quality=data_quality,
            confidence_level=confidence_level,
            years_of_data=years_of_data,
            actual_data_years=actual_data_years,
            latest_actual_year=latest_actual_year or 2020,  # Fallback if no data
            is_using_university_average=is_using_university_average,
            university_average_cagr=self.get_university_cagr(university),
            course_specific_cagr=course_cagr,
            calculation_method="Course-specific CAGR" if not is_using_university_average else "University average CAGR",
            source_verification=generate_parent_verification_guide(university, programme)
        )

        return {
            'university': university,
            'programme': programme,
            'cagr': used_cagr,
            'cagr_pct': used_cagr * 100,
            'latest_fee': latest_fee,
            'latest_actual_year': latest_actual_year,
            'historical_fees': historical_fees,
            'data_points': len(course_data),
            'degree_level': course_data['degree_level'].iloc[0] if len(course_data) > 0 else 'Unknown',
            'transparency': transparency,
            'is_using_university_average': is_using_university_average,
            'course_specific_cagr': course_cagr,
            'university_average_cagr': self.get_university_cagr(university)
        }