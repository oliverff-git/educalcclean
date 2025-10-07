"""
Create SQLite database and load processed HESA data.

This script creates a relational database structure for efficient querying
of university and course information.
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys


def create_database():
    """Create SQLite database with proper schema."""
    print("=" * 60)
    print("Creating SQLite Database")
    print("=" * 60)

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "educalc.db"

    # Remove existing database if it exists
    if db_path.exists():
        print(f"\n⚠️  Removing existing database: {db_path}")
        db_path.unlink()

    # Create new database
    print(f"\n📁 Creating new database: {db_path}")
    conn = sqlite3.connect(str(db_path))

    # Universities table
    print("\n🏛️  Creating universities table...")
    conn.execute('''
        CREATE TABLE universities (
            ukprn INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            short_name TEXT,
            website TEXT,
            country TEXT,
            league_rank INTEGER
        )
    ''')

    # Courses table
    print("📚 Creating courses table...")
    conn.execute('''
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ukprn INTEGER,
            course_id TEXT,
            title TEXT NOT NULL,
            title_welsh TEXT,
            mode TEXT,
            level TEXT,
            duration_years INTEGER,
            honours TEXT,
            foundation TEXT,
            sandwich TEXT,
            year_abroad TEXT,
            hecos_primary TEXT,
            hecos_secondary TEXT,
            hecos_name TEXT,
            cah_l1_code TEXT,
            cah_l1_name TEXT,
            cah_l2_code TEXT,
            cah_l2_name TEXT,
            cah_l3_code TEXT,
            cah_l3_name TEXT,
            ucas_code TEXT,
            course_url TEXT,
            fees_url TEXT,
            teaching_url TEXT,
            employment_url TEXT,
            support_url TEXT,
            updated_date DATE,
            FOREIGN KEY (ukprn) REFERENCES universities(ukprn),
            UNIQUE(ukprn, course_id, mode, level, duration_years)
        )
    ''')

    # Subject mappings table
    print("🗺️  Creating subject_mappings table...")
    conn.execute('''
        CREATE TABLE subject_mappings (
            hecos_code TEXT PRIMARY KEY,
            hecos_name TEXT,
            cah_l1_code TEXT,
            cah_l1_name TEXT,
            cah_l2_code TEXT,
            cah_l2_name TEXT,
            cah_l3_code TEXT,
            cah_l3_name TEXT
        )
    ''')

    # Fees table (placeholder for future)
    print("💷 Creating fees table...")
    conn.execute('''
        CREATE TABLE fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ukprn INTEGER,
            course_id TEXT,
            programme TEXT,
            academic_year TEXT,
            fee_status TEXT,
            fee_gbp REAL,
            source TEXT,
            extraction_date DATE,
            FOREIGN KEY (ukprn) REFERENCES universities(ukprn)
        )
    ''')

    # Create indices for better query performance
    print("🔍 Creating indices...")
    conn.execute('CREATE INDEX idx_courses_ukprn ON courses(ukprn)')
    conn.execute('CREATE INDEX idx_courses_title ON courses(title)')
    conn.execute('CREATE INDEX idx_courses_level ON courses(level)')
    conn.execute('CREATE INDEX idx_courses_hecos ON courses(hecos_primary)')
    conn.execute('CREATE INDEX idx_courses_cah_l1 ON courses(cah_l1_code)')
    conn.execute('CREATE INDEX idx_fees_ukprn ON fees(ukprn)')
    conn.execute('CREATE INDEX idx_fees_year ON fees(academic_year)')

    conn.commit()
    print("\n✅ Database schema created successfully")

    return conn


def load_data_to_db(conn):
    """Load processed CSVs into database."""
    print("\n" + "=" * 60)
    print("Loading Data into Database")
    print("=" * 60)

    # Get project paths
    project_root = Path(__file__).parent.parent.parent
    processed_data = project_root / "data" / "hesa" / "processed"
    fees_data = project_root / "data" / "fees"

    # Load universities
    print("\n🏛️  Loading universities...")
    unis_path = processed_data / "top_50_universities.csv"
    if unis_path.exists():
        unis = pd.read_csv(unis_path)
        unis_insert = unis[['UKPRN', 'LEGAL_NAME', 'short_name', 'PROVURL', 'COUNTRY', 'league_rank']].copy()
        unis_insert.columns = ['ukprn', 'name', 'short_name', 'website', 'country', 'league_rank']

        # Remove duplicates (keep first occurrence)
        unis_insert = unis_insert.drop_duplicates(subset=['ukprn'], keep='first')

        unis_insert.to_sql('universities', conn, if_exists='append', index=False)
        print(f"   ✅ Loaded {len(unis_insert)} universities")
    else:
        print(f"   ⚠️  {unis_path} not found")

    # Load courses
    print("\n📚 Loading courses...")
    courses_path = processed_data / "courses_unified.csv"
    if courses_path.exists():
        courses = pd.read_csv(courses_path)
        # Drop columns not in schema
        courses_insert = courses.drop(columns=['short_name', 'league_rank', 'university_name'], errors='ignore')

        # Keep legitimate course variants (FT vs PT, different durations, etc.)
        courses_insert = courses_insert.drop_duplicates(
            subset=['ukprn', 'course_id', 'mode', 'level', 'duration_years'],
            keep='first'
        )

        courses_insert.to_sql('courses', conn, if_exists='append', index=False)
        print(f"   ✅ Loaded {len(courses_insert)} courses")
    else:
        print(f"   ⚠️  {courses_path} not found")

    # Load subjects
    print("\n🗺️  Loading subject mappings...")
    subjects_path = processed_data / "subject_mappings.csv"
    if subjects_path.exists():
        subjects = pd.read_csv(subjects_path)
        subjects.to_sql('subject_mappings', conn, if_exists='append', index=False)
        print(f"   ✅ Loaded {len(subjects)} subject mappings")
    else:
        print(f"   ⚠️  {subjects_path} not found")

    # Load existing fees
    print("\n💷 Loading existing fee data...")
    fees_path = fees_data / "comprehensive_fees_2020_2026.csv"
    if fees_path.exists():
        fees = pd.read_csv(fees_path)

        # Map university names to UKPRNs
        uni_mapping = {
            'Cambridge': 10007788,
            'Oxford': 10007774,
            'LSE': 10004063
        }

        fees['ukprn'] = fees['university'].map(uni_mapping)
        fees['course_id'] = None  # Will be mapped later

        # Insert fees
        fees_insert = fees[['ukprn', 'course_id', 'programme', 'academic_year',
                            'fee_status', 'fee_gbp', 'source', 'extraction_date']].copy()
        fees_insert.to_sql('fees', conn, if_exists='append', index=False)
        print(f"   ✅ Loaded {len(fees_insert)} fee records")
    else:
        print(f"   ⚠️  {fees_path} not found")

    conn.commit()


def verify_database(conn):
    """Verify database contents."""
    print("\n" + "=" * 60)
    print("Database Verification")
    print("=" * 60)

    # Count records
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM universities")
    uni_count = cursor.fetchone()[0]
    print(f"\n📊 Universities: {uni_count}")

    cursor.execute("SELECT COUNT(*) FROM courses")
    course_count = cursor.fetchone()[0]
    print(f"📊 Courses: {course_count}")

    cursor.execute("SELECT COUNT(*) FROM subject_mappings")
    subject_count = cursor.fetchone()[0]
    print(f"📊 Subject mappings: {subject_count}")

    cursor.execute("SELECT COUNT(*) FROM fees")
    fee_count = cursor.fetchone()[0]
    print(f"📊 Fee records: {fee_count}")

    # Sample queries
    print("\n📊 Sample queries:")

    # Top universities by course count
    query = '''
        SELECT u.short_name, u.league_rank, COUNT(c.id) as course_count
        FROM universities u
        LEFT JOIN courses c ON u.ukprn = c.ukprn
        GROUP BY u.ukprn
        ORDER BY course_count DESC
        LIMIT 10
    '''
    cursor.execute(query)
    print("\n   Top 10 universities by course count:")
    for row in cursor.fetchall():
        print(f"      {row[0]} (#{row[1]}): {row[2]} courses")

    # Courses by level
    query = '''
        SELECT level, COUNT(*) as count
        FROM courses
        GROUP BY level
        ORDER BY count DESC
    '''
    cursor.execute(query)
    print("\n   Courses by level:")
    for row in cursor.fetchall():
        print(f"      {row[0]}: {row[1]}")

    # Universities with fee data
    query = '''
        SELECT DISTINCT u.short_name, COUNT(DISTINCT f.programme) as programmes
        FROM universities u
        INNER JOIN fees f ON u.ukprn = f.ukprn
        GROUP BY u.ukprn
        ORDER BY programmes DESC
    '''
    cursor.execute(query)
    print("\n   Universities with fee data:")
    for row in cursor.fetchall():
        print(f"      {row[0]}: {row[1]} programmes with fees")


def main():
    """Main execution."""
    # Create database and schema
    conn = create_database()

    # Load data
    load_data_to_db(conn)

    # Verify
    verify_database(conn)

    # Close connection
    conn.close()

    print("\n" + "=" * 60)
    print("✅ Database creation complete!")
    print("=" * 60)
    print(f"Database location: /Users/oliver/projects/educalcclean/data/educalc.db")


if __name__ == "__main__":
    main()
