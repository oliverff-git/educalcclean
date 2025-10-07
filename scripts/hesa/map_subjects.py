"""
Map HECoS subject codes to CAH (Common Aggregation Hierarchy) classifications.

This script processes the HECoS/CAH mapping Excel file to create a unified
subject classification lookup table.
"""

import pandas as pd
from pathlib import Path
import sys


def load_hecos_cah_mapping():
    """Load HECoS to CAH mapping from Excel file."""
    print("📊 Loading HECoS/CAH mapping data...")

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    raw_data = project_root / "data" / "hesa" / "raw"

    # Load Excel file
    excel_path = raw_data / "HECoS_CAH_Version_1.3.4.xlsx"
    if not excel_path.exists():
        print(f"❌ Error: {excel_path} not found")
        sys.exit(1)

    try:
        # Read the mapping sheet
        mapping_df = pd.read_excel(
            excel_path,
            sheet_name='HECoS_CAH_Mapping (V1.3.4)',
            engine='openpyxl'
        )
        print(f"   Loaded {len(mapping_df)} HECoS mappings")

        return mapping_df

    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        sys.exit(1)


def create_subject_lookup():
    """Create flattened subject classification table."""
    print("\n📚 Creating subject classification lookup...")

    # Load mapping data
    mapping_df = load_hecos_cah_mapping()

    # Extract relevant columns
    subjects = pd.DataFrame({
        'hecos_code': mapping_df['HECoS (Code only)'],
        'hecos_name': mapping_df['HECoS'].str.replace(r'\(\d+\)\s*', '', regex=True).str.strip(),
        'cah_l1_code': mapping_df['CAH1 (Code only)'],
        'cah_l1_name': mapping_df['CAH1'].str.replace(r'\(CAH\d+\)\s*', '', regex=True).str.strip(),
        'cah_l2_code': mapping_df['CAH2 (Code only)'],
        'cah_l2_name': mapping_df['CAH2'].str.replace(r'\(CAH\d+-\d+\)\s*', '', regex=True).str.strip(),
        'cah_l3_code': mapping_df['CAH3 (Code only)'],
        'cah_l3_name': mapping_df['CAH3'].str.replace(r'\(CAH\d+-\d+-\d+\)\s*', '', regex=True).str.strip(),
    })

    # Remove duplicates (keep first occurrence)
    subjects = subjects.drop_duplicates(subset=['hecos_code'])

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    processed_data = project_root / "data" / "hesa" / "processed"

    # Save processed data
    output_path = processed_data / "subject_mappings.csv"
    subjects.to_csv(output_path, index=False)

    print(f"✅ Created {len(subjects)} subject classifications")
    print(f"   Saved to: {output_path}")

    # Show breakdown
    cah_l1_counts = subjects['cah_l1_name'].value_counts()
    print("\n📊 Top 10 CAH Level 1 categories:")
    for category, count in cah_l1_counts.head(10).items():
        print(f"   {category}: {count} subjects")

    return subjects


def load_cah_hierarchy():
    """Load CAH hierarchy for reference."""
    print("\n📊 Loading CAH hierarchy...")

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    raw_data = project_root / "data" / "hesa" / "raw"

    # Load Excel file
    excel_path = raw_data / "HECoS_CAH_Version_1.3.4.xlsx"

    try:
        # Read the CAH sheet
        cah_df = pd.read_excel(
            excel_path,
            sheet_name='CAH (V1.3.4)',
            engine='openpyxl'
        )

        print(f"   Loaded {len(cah_df)} CAH classifications")

        # Get project paths
        processed_data = project_root / "data" / "hesa" / "processed"

        # Save for reference
        output_path = processed_data / "cah_hierarchy.csv"
        cah_df.to_csv(output_path, index=False)

        print(f"   Saved to: {output_path}")

        return cah_df

    except Exception as e:
        print(f"⚠️  Warning: Could not load CAH hierarchy: {e}")
        return None


def main():
    """Main subject mapping pipeline."""
    print("=" * 60)
    print("HECoS/CAH Subject Classification Mapping")
    print("=" * 60)

    # Create subject lookup
    subjects = create_subject_lookup()

    # Load CAH hierarchy (optional, for reference)
    cah_hierarchy = load_cah_hierarchy()

    print("\n" + "=" * 60)
    print("✅ Subject mapping complete!")
    print("=" * 60)
    print(f"HECoS codes mapped: {len(subjects)}")
    if cah_hierarchy is not None:
        print(f"CAH hierarchy levels: {len(cah_hierarchy)}")


if __name__ == "__main__":
    main()
