"""
Transform raw HESA courses into unified format with subject mappings.

This script combines course data with subject classifications and enriches
with human-readable labels for all categorical fields.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys


def decode_mode(kismode):
    """Decode KISMODE to human readable."""
    mode_map = {
        '01': 'Full-time',
        '02': 'Part-time',
        '03': 'Both available',
        '1': 'Full-time',
        '2': 'Part-time',
        '3': 'Both available',
        1: 'Full-time',
        2: 'Part-time',
        3: 'Both available'
    }
    if pd.isna(kismode):
        return 'Unknown'
    return mode_map.get(str(kismode).strip(), 'Unknown')


def decode_level(kislevel):
    """Decode KISLEVEL."""
    level_map = {
        '03': 'Undergraduate',
        '04': 'Other undergraduate',
        '06': 'Postgraduate taught',
        '07': 'Postgraduate research',
        '3': 'Undergraduate',
        '4': 'Other undergraduate',
        '6': 'Postgraduate taught',
        '7': 'Postgraduate research',
        3: 'Undergraduate',
        4: 'Other undergraduate',
        6: 'Postgraduate taught',
        7: 'Postgraduate research'
    }
    if pd.isna(kislevel):
        return 'Unknown'
    return level_map.get(str(kislevel).strip(), 'Other')


def decode_boolean(value):
    """Decode 0/1 to Yes/No."""
    if pd.isna(value):
        return 'No'
    try:
        return 'Yes' if int(value) == 1 else 'No'
    except:
        return 'No'


def parse_hecos_codes(row):
    """Extract HECoS codes from multiple columns."""
    # KISCOURSE has 5 HECOS columns (can have up to 5 subject codes per course)
    hecos_cols = [f'HECOS.{i}' if i > 0 else 'HECOS' for i in range(5)]
    codes = []

    for col in hecos_cols:
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip() != '':
            codes.append(str(row[col]).strip())

    return codes


def transform_courses():
    """Main transformation pipeline."""
    print("=" * 60)
    print("HESA Courses Transformation Pipeline")
    print("=" * 60)

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    processed_data = project_root / "data" / "hesa" / "processed"

    # Load raw data
    print("\n📊 Loading raw data...")
    courses_raw = pd.read_csv(processed_data / "courses_raw.csv", low_memory=False)
    universities = pd.read_csv(processed_data / "top_50_universities.csv")
    subjects = pd.read_csv(processed_data / "subject_mappings.csv")

    print(f"   Courses: {len(courses_raw)}")
    print(f"   Universities: {len(universities)}")
    print(f"   Subject mappings: {len(subjects)}")

    # Merge university names
    print("\n🔗 Merging university data...")
    df = courses_raw.merge(
        universities[['UKPRN', 'LEGAL_NAME', 'short_name', 'league_rank']],
        on='UKPRN',
        how='left'
    )

    # Parse HECoS codes
    print("\n📚 Parsing HECoS subject codes...")
    df['hecos_codes'] = df.apply(parse_hecos_codes, axis=1)
    df['hecos_primary'] = df['hecos_codes'].apply(lambda x: x[0] if len(x) > 0 else None)
    df['hecos_secondary'] = df['hecos_codes'].apply(lambda x: x[1] if len(x) > 1 else None)

    # Map to CAH subjects
    print("\n🗺️  Mapping to CAH classifications...")
    # Convert both columns to string for consistent joining
    df['hecos_primary'] = df['hecos_primary'].astype(str)
    subjects['hecos_code'] = subjects['hecos_code'].astype(str)

    df = df.merge(
        subjects[['hecos_code', 'hecos_name', 'cah_l1_code', 'cah_l1_name',
                  'cah_l2_code', 'cah_l2_name', 'cah_l3_code', 'cah_l3_name']],
        left_on='hecos_primary',
        right_on='hecos_code',
        how='left'
    )

    # Decode categorical fields
    print("\n🔤 Decoding categorical fields...")
    # Convert to string for consistent decoding (fixes data type mismatch)
    df['KISMODE'] = df['KISMODE'].astype(str).str.strip()
    df['KISLEVEL'] = df['KISLEVEL'].astype(str).str.strip()

    df['mode_readable'] = df['KISMODE'].apply(decode_mode)
    df['level_readable'] = df['KISLEVEL'].apply(decode_level)
    df['honours'] = df['HONOURS'].apply(decode_boolean)
    df['foundation'] = df['FOUNDATION'].apply(decode_boolean)
    df['sandwich'] = df['SANDWICH'].apply(decode_boolean)
    df['year_abroad'] = df['YEARABROAD'].apply(decode_boolean)

    # Create final unified format
    print("\n✨ Creating unified course catalog...")
    df_final = pd.DataFrame({
        'ukprn': df['UKPRN'],
        'university_name': df['LEGAL_NAME'],
        'short_name': df['short_name'],
        'league_rank': df['league_rank'],
        'course_id': df['KISCOURSEID'],
        'title': df['TITLE'],
        'title_welsh': df['TITLEW'] if 'TITLEW' in df.columns else None,
        'mode': df['mode_readable'],
        'level': df['level_readable'],
        'duration_years': df['NUMSTAGE'],
        'honours': df['honours'],
        'foundation': df['foundation'],
        'sandwich': df['sandwich'],
        'year_abroad': df['year_abroad'],
        'hecos_primary': df['hecos_primary'],
        'hecos_secondary': df['hecos_secondary'],
        'hecos_name': df['hecos_name'],
        'cah_l1_code': df['cah_l1_code'],
        'cah_l1_name': df['cah_l1_name'],
        'cah_l2_code': df['cah_l2_code'],
        'cah_l2_name': df['cah_l2_name'],
        'cah_l3_code': df['cah_l3_code'],
        'cah_l3_name': df['cah_l3_name'],
        'ucas_code': df['UCASPROGID'],
        'course_url': df['CRSEURL'],
        'fees_url': df['CRSECSTURL'],
        'teaching_url': df['LTURL'],
        'employment_url': df['EMPLOYURL'],
        'support_url': df['SUPPORTURL'],
        'updated_date': pd.Timestamp.now().date()
    })

    # Remove courses without titles
    df_final = df_final[df_final['title'].notna()].copy()

    # Save processed data
    output_path = processed_data / "courses_unified.csv"
    df_final.to_csv(output_path, index=False)

    print(f"\n✅ Created unified course catalog")
    print(f"   Total courses: {len(df_final)}")
    print(f"   Saved to: {output_path}")

    # Statistics
    print("\n📊 Course Statistics:")
    print(f"   - By level:")
    for level, count in df_final['level'].value_counts().head(5).items():
        print(f"     {level}: {count}")

    print(f"\n   - By mode:")
    for mode, count in df_final['mode'].value_counts().items():
        print(f"     {mode}: {count}")

    print(f"\n   - With HECoS mapping: {df_final['hecos_primary'].notna().sum()}")
    print(f"   - With CAH L1 mapping: {df_final['cah_l1_code'].notna().sum()}")
    print(f"   - With CAH L3 mapping: {df_final['cah_l3_code'].notna().sum()}")

    # Top 10 universities by course count
    print(f"\n📊 Top 10 universities by course count:")
    course_counts = df_final.groupby(['short_name', 'league_rank']).size().reset_index(name='count')
    course_counts = course_counts.sort_values('count', ascending=False)

    for _, row in course_counts.head(10).iterrows():
        print(f"   {row['short_name']} (#{row['league_rank']}): {row['count']} courses")

    return df_final


def main():
    """Main execution."""
    courses_unified = transform_courses()

    print("\n" + "=" * 60)
    print("✅ Transformation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
