"""
Course Catalog API - Access layer for HESA course data.

Provides clean interface for querying university courses, subject classifications,
and integrating with fee data.
"""

import sqlite3
import pandas as pd
from typing import List, Optional, Dict
from pathlib import Path


class CourseCatalog:
    """Access layer for HESA course catalog data."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize course catalog.

        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "educalc.db"

        self.db_path = str(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def get_all_universities(self) -> pd.DataFrame:
        """
        Get all top 50 universities.

        Returns:
            DataFrame with university information sorted by league rank.
        """
        conn = self._get_connection()
        df = pd.read_sql(
            'SELECT * FROM universities ORDER BY league_rank',
            conn
        )
        conn.close()
        return df

    def get_university_by_name(self, name: str) -> Optional[Dict]:
        """
        Get university by name (short_name or full name).

        Args:
            name: University name (e.g., 'Cambridge', 'Oxford')

        Returns:
            Dictionary with university info or None if not found.
        """
        conn = self._get_connection()
        query = '''
            SELECT * FROM universities
            WHERE short_name = ? OR name LIKE ?
            LIMIT 1
        '''
        df = pd.read_sql(query, conn, params=(name, f'%{name}%'))
        conn.close()

        if df.empty:
            return None
        return df.to_dict('records')[0]

    def get_ukprn_by_name(self, name: str) -> Optional[int]:
        """
        Map university name to UKPRN.

        Args:
            name: University name

        Returns:
            UKPRN or None if not found
        """
        uni = self.get_university_by_name(name)
        return uni['ukprn'] if uni else None

    def get_university_courses(self, ukprn: int) -> pd.DataFrame:
        """
        Get all courses for a university.

        Args:
            ukprn: University UKPRN

        Returns:
            DataFrame of courses with subject classifications.
        """
        conn = self._get_connection()
        query = '''
            SELECT c.*, u.name as university_name, u.short_name,
                   s.hecos_name, s.cah_l3_name
            FROM courses c
            JOIN universities u ON c.ukprn = u.ukprn
            LEFT JOIN subject_mappings s ON c.hecos_primary = s.hecos_code
            WHERE c.ukprn = ?
            ORDER BY c.title
        '''
        df = pd.read_sql(query, conn, params=(ukprn,))
        conn.close()
        return df

    def find_course_by_title(self, ukprn: int, title: str) -> Optional[Dict]:
        """
        Find course by title (exact or fuzzy match).

        Args:
            ukprn: University UKPRN
            title: Course title

        Returns:
            Dictionary with course details or None if not found.
        """
        conn = self._get_connection()
        query = '''
            SELECT c.*, s.hecos_name, s.cah_l1_name, s.cah_l2_name, s.cah_l3_name
            FROM courses c
            LEFT JOIN subject_mappings s ON c.hecos_primary = s.hecos_code
            WHERE c.ukprn = ? AND (c.title = ? OR c.title LIKE ?)
            LIMIT 1
        '''
        df = pd.read_sql(query, conn, params=(ukprn, title, f'%{title}%'))
        conn.close()

        if df.empty:
            return None
        return df.to_dict('records')[0]

    def get_courses_by_subject(self, cah_code: str) -> pd.DataFrame:
        """
        Get all courses in a subject area.

        Args:
            cah_code: CAH code (any level, e.g., 'CAH15' or 'CAH15-01-01')

        Returns:
            DataFrame of matching courses.
        """
        conn = self._get_connection()
        query = '''
            SELECT c.*, u.short_name, s.cah_l3_name
            FROM courses c
            JOIN universities u ON c.ukprn = u.ukprn
            LEFT JOIN subject_mappings s ON c.hecos_primary = s.hecos_code
            WHERE c.cah_l1_code = ? OR c.cah_l2_code = ? OR c.cah_l3_code = ?
            ORDER BY u.league_rank, c.title
        '''
        df = pd.read_sql(query, conn, params=(cah_code, cah_code, cah_code))
        conn.close()
        return df

    def search_courses(self, search_term: str, limit: int = 100) -> pd.DataFrame:
        """
        Full-text search across course titles.

        Args:
            search_term: Search term
            limit: Maximum results to return

        Returns:
            DataFrame of matching courses.
        """
        conn = self._get_connection()
        query = f'''
            SELECT c.*, u.short_name as university_name
            FROM courses c
            JOIN universities u ON c.ukprn = u.ukprn
            WHERE c.title LIKE ?
            ORDER BY u.league_rank, c.title
            LIMIT {limit}
        '''
        df = pd.read_sql(query, conn, params=(f'%{search_term}%',))
        conn.close()
        return df

    def get_course_with_fees(self, ukprn: int, course_id: str) -> Dict:
        """
        Get course details including fee history.

        Args:
            ukprn: University UKPRN
            course_id: Course ID

        Returns:
            Dictionary with 'course' and 'fees' keys.
        """
        conn = self._get_connection()

        # Get course info
        course_query = '''
            SELECT c.*, u.short_name, s.hecos_name, s.cah_l3_name
            FROM courses c
            JOIN universities u ON c.ukprn = u.ukprn
            LEFT JOIN subject_mappings s ON c.hecos_primary = s.hecos_code
            WHERE c.ukprn = ? AND c.course_id = ?
        '''
        course = pd.read_sql(course_query, conn, params=(ukprn, course_id))

        # Get fee history
        fees_query = '''
            SELECT academic_year, fee_status, fee_gbp
            FROM fees
            WHERE ukprn = ? AND course_id = ?
            ORDER BY academic_year, fee_status
        '''
        fees = pd.read_sql(fees_query, conn, params=(ukprn, course_id))

        conn.close()

        return {
            'course': course.to_dict('records')[0] if not course.empty else None,
            'fees': fees.to_dict('records') if not fees.empty else []
        }

    def get_subject_mapping(self, hecos_code: str) -> Optional[Dict]:
        """
        Get subject classification for a HECoS code.

        Args:
            hecos_code: HECoS code

        Returns:
            Dictionary with CAH classifications or None.
        """
        conn = self._get_connection()
        query = 'SELECT * FROM subject_mappings WHERE hecos_code = ?'
        df = pd.read_sql(query, conn, params=(hecos_code,))
        conn.close()

        if df.empty:
            return None
        return df.to_dict('records')[0]

    def has_fee_data(self, ukprn: int, programme: str) -> bool:
        """
        Check if fee data exists for a programme.

        Args:
            ukprn: University UKPRN
            programme: Programme name

        Returns:
            True if fees exist, False otherwise.
        """
        conn = self._get_connection()
        query = '''
            SELECT COUNT(*) as count
            FROM fees
            WHERE ukprn = ? AND programme LIKE ?
        '''
        cursor = conn.cursor()
        cursor.execute(query, (ukprn, f'%{programme}%'))
        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def get_universities_with_fee_data(self) -> pd.DataFrame:
        """
        Get list of universities that have fee data.

        Returns:
            DataFrame with universities and programme counts.
        """
        conn = self._get_connection()
        query = '''
            SELECT u.ukprn, u.short_name, u.league_rank,
                   COUNT(DISTINCT f.programme) as programmes_with_fees
            FROM universities u
            INNER JOIN fees f ON u.ukprn = f.ukprn
            GROUP BY u.ukprn
            ORDER BY programmes_with_fees DESC
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        return df


# Convenience functions for backward compatibility
def get_universities() -> List[str]:
    """Get list of all university short names."""
    catalog = CourseCatalog()
    unis = catalog.get_all_universities()
    return unis['short_name'].tolist()


def get_ukprn(university_name: str) -> Optional[int]:
    """Get UKPRN for a university name."""
    catalog = CourseCatalog()
    return catalog.get_ukprn_by_name(university_name)
