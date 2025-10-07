"""
Extract top 50 universities and their courses from HESA data.

This script extracts the top 50 UK universities from the Complete University Guide
rankings and filters HESA data to include only these institutions.
"""

import pandas as pd
from pathlib import Path
import sys

# Top 50 UK Universities (2026 Rankings) with their UKPRNs
TOP_50_UNIVERSITIES = {
    # Rank: (UKPRN, Official Name, Short Name)
    1: (10007788, "University of Cambridge", "Cambridge"),
    2: (10007774, "University of Oxford", "Oxford"),
    3: (10004063, "The London School of Economics and Political Science", "LSE"),
    4: (10007803, "University of St Andrews", "St Andrews"),
    5: (10007143, "Durham University", "Durham"),
    6: (10003270, "Imperial College of Science, Technology and Medicine", "Imperial College London"),
    7: (10004113, "Loughborough University", "Loughborough"),
    8: (10007850, "University of Bath", "Bath"),
    9: (10007163, "The University of Warwick", "Warwick"),
    10: (10007768, "Lancaster University", "Lancaster"),
    11: (10007792, "University of Exeter", "Exeter"),
    12: (10007167, "University of York", "York"),
    13: (10007784, "University College London", "UCL"),
    14: (10006840, "University of Birmingham", "Birmingham"),
    15: (10007786, "University of Bristol", "Bristol"),
    16: (10007157, "The University of Sheffield", "Sheffield"),
    17: (10007158, "University of Southampton", "Southampton"),
    18: (10007790, "The University of Edinburgh", "Edinburgh"),
    19: (10003645, "King's College London", "King's College London"),
    20: (10007160, "University of Surrey", "Surrey"),
    21: (10007795, "University of Leeds", "Leeds"),
    22: (10007814, "Cardiff University", "Cardiff"),
    23: (10006842, "University of Liverpool", "Liverpool"),
    24: (10005343, "Queen's University Belfast", "Queen's Belfast"),
    25: (10007764, "Heriot-Watt University", "Heriot-Watt"),
    26: (10007789, "University of East Anglia", "UEA"),
    27: (10007154, "University of Nottingham", "Nottingham"),
    28: (10007798, "The University of Manchester", "Manchester"),
    29: (10007791, "University of Essex", "Essex"),
    30: (10007783, "University of Aberdeen", "Aberdeen"),
    31: (10007794, "University of Glasgow", "Glasgow"),
    32: (10007799, "Newcastle University", "Newcastle"),
    33: (10007796, "University of Leicester", "Leicester"),
    34: (10007162, "University of the Arts, London", "Arts London"),
    35: (10005553, "Royal Holloway, University of London", "Royal Holloway"),
    36: (10007802, "University of Reading", "Reading"),
    37: (10007832, "University of Northumbria at Newcastle", "Northumbria"),
    38: (10007805, "University of Strathclyde", "Strathclyde"),
    39: (10007852, "University of Dundee", "Dundee"),
    40: (10007855, "Swansea University", "Swansea"),
    41: (10007150, "University of Kent", "Kent"),
    42: (10007759, "Aston University", "Aston"),
    43: (10007804, "University of Stirling", "Stirling"),
    44: (10003861, "Queen Mary University of London", "Queen Mary"),
    45: (10007806, "University of Sussex", "Sussex"),
    46: (10001726, "Coventry University", "Coventry"),
    47: (10007787, "The University of Buckingham", "Buckingham"),
    48: (10007800, "Nottingham Trent University", "Nottingham Trent"),
    49: (10007151, "University of Lincoln", "Lincoln"),
    50: (10007801, "University of Portsmouth", "Portsmouth"),
}


def extract_institutions():
    """Extract top 50 university records from HESA INSTITUTION data."""
    print("📊 Extracting top 50 universities...")

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    raw_data = project_root / "data" / "hesa" / "raw"
    processed_data = project_root / "data" / "hesa" / "processed"

    # Load INSTITUTION data
    inst_path = raw_data / "INSTITUTION.csv"
    if not inst_path.exists():
        print(f"❌ Error: {inst_path} not found")
        sys.exit(1)

    inst_df = pd.read_csv(inst_path)
    print(f"   Loaded {len(inst_df)} institutions from HESA")

    # Extract UKPRNs
    top_50_ukprns = [data[0] for data in TOP_50_UNIVERSITIES.values()]

    # Filter to top 50
    top_50_df = inst_df[inst_df['UKPRN'].isin(top_50_ukprns)].copy()

    # Filter to primary universities only (remove partner colleges/NHS trusts)
    university_indicators = [
        'University', 'College London', 'Imperial', 'LSE',
        'School of Economics', 'Royal Holloway', 'Queen Mary'
    ]
    pattern = '|'.join(university_indicators)
    top_50_df = top_50_df[
        top_50_df['LEGAL_NAME'].str.contains(pattern, case=False, na=False)
    ]

    # Remove duplicates, keeping first (main campus)
    top_50_df = top_50_df.drop_duplicates(subset=['UKPRN'], keep='first')

    # Add ranking and short names
    ranking_map = {data[0]: rank for rank, data in TOP_50_UNIVERSITIES.items()}
    short_name_map = {data[0]: data[2] for data in TOP_50_UNIVERSITIES.values()}

    top_50_df['league_rank'] = top_50_df['UKPRN'].map(ranking_map)
    top_50_df['short_name'] = top_50_df['UKPRN'].map(short_name_map)

    # Sort by rank
    top_50_df = top_50_df.sort_values('league_rank')

    # Save processed data
    output_path = processed_data / "top_50_universities.csv"
    top_50_df.to_csv(output_path, index=False)

    print(f"✅ Extracted {len(top_50_df)} universities")
    print(f"   Saved to: {output_path}")

    return top_50_df


def extract_courses():
    """Extract all courses for top 50 universities from KISCOURSE data."""
    print("\n📚 Extracting courses for top 50 universities...")

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    raw_data = project_root / "data" / "hesa" / "raw"
    processed_data = project_root / "data" / "hesa" / "processed"

    # Load KISCOURSE data
    course_path = raw_data / "KISCOURSE.csv"
    if not course_path.exists():
        print(f"❌ Error: {course_path} not found")
        sys.exit(1)

    # Read with proper handling of mixed types
    courses_df = pd.read_csv(course_path, low_memory=False)
    print(f"   Loaded {len(courses_df)} total courses from HESA")

    # Extract UKPRNs for top 50
    top_50_ukprns = [data[0] for data in TOP_50_UNIVERSITIES.values()]

    # Filter to top 50 universities
    top_courses = courses_df[courses_df['UKPRN'].isin(top_50_ukprns)].copy()

    # Save processed data
    output_path = processed_data / "courses_raw.csv"
    top_courses.to_csv(output_path, index=False)

    print(f"✅ Extracted {len(top_courses)} courses")
    print(f"   Saved to: {output_path}")

    # Show breakdown by university
    print("\n📊 Course counts by university:")
    course_counts = top_courses.groupby('UKPRN').size().reset_index(name='count')

    # Add university names
    ukprn_to_name = {data[0]: data[2] for data in TOP_50_UNIVERSITIES.values()}
    course_counts['university'] = course_counts['UKPRN'].map(ukprn_to_name)
    course_counts = course_counts.sort_values('count', ascending=False)

    for _, row in course_counts.head(10).iterrows():
        print(f"   {row['university']}: {row['count']} courses")

    return top_courses


def main():
    """Main extraction pipeline."""
    print("=" * 60)
    print("HESA Top 50 Universities Data Extraction")
    print("=" * 60)

    # Extract institutions
    universities = extract_institutions()

    # Extract courses
    courses = extract_courses()

    print("\n" + "=" * 60)
    print("✅ Extraction complete!")
    print("=" * 60)
    print(f"Universities: {len(universities)}")
    print(f"Courses: {len(courses)}")


if __name__ == "__main__":
    main()
