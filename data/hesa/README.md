# HESA Course Catalog Integration

This directory contains processed data from the HESA (Higher Education Statistics Agency) Discover Uni dataset, integrated into the educalcclean application.

## Overview

The HESA integration provides comprehensive course discovery and subject classification for the **top 50 UK universities** according to the 2026 Complete University Guide rankings.

### Data Coverage

- **Universities**: 47 institutions (top 50, with some variations due to data availability)
- **Courses**: 10,722 courses across all 47 universities
- **Subject Classifications**: 1,092 HECoS codes mapped to 166 CAH categories
- **Fee Data**: Integrated with existing fee data for Cambridge, Oxford, and LSE

## Directory Structure

```
data/hesa/
├── raw/                                    # Original HESA data files
│   ├── INSTITUTION.csv                     # All UK institutions
│   ├── KISCOURSE.csv                       # All UK courses
│   ├── SBJ.csv                             # Subject data
│   └── HECoS_CAH_Version_1.3.4.xlsx       # Subject classification mappings
│
├── processed/                              # Processed and filtered data
│   ├── top_50_universities.csv             # 47 universities with rankings
│   ├── courses_raw.csv                     # Filtered courses for top 50
│   ├── courses_unified.csv                 # Transformed courses with classifications
│   ├── subject_mappings.csv                # HECoS → CAH mappings
│   └── cah_hierarchy.csv                   # CAH hierarchy reference
│
└── README.md                               # This file
```

## Data Files

### top_50_universities.csv

Contains the top 50 UK universities with:
- `UKPRN`: UK Provider Reference Number (unique identifier)
- `LEGAL_NAME`: Official university name
- `short_name`: Short name used in UI (e.g., "Cambridge", "Oxford")
- `PROVURL`: Official website URL
- `COUNTRY`: Country code (XF=England, XG=Wales, XH=Scotland, XI=N. Ireland)
- `league_rank`: Position in 2026 Complete University Guide rankings

### courses_unified.csv

Contains 10,722 courses with:

**Basic Information:**
- `ukprn`: University identifier
- `course_id`: Unique course identifier within institution
- `title`: Course title
- `mode`: Full-time, Part-time, or Both available
- `level`: Undergraduate, Postgraduate taught, etc.

**Course Details:**
- `duration_years`: Programme length
- `honours`: Whether honours degree
- `foundation`: Foundation year availability
- `sandwich`: Sandwich year availability
- `year_abroad`: Year abroad availability

**Subject Classifications:**
- `hecos_primary`: Primary HECoS subject code
- `hecos_secondary`: Secondary HECoS code (if applicable)
- `hecos_name`: Human-readable subject name
- `cah_l1_code`, `cah_l1_name`: CAH Level 1 (broad subject area)
- `cah_l2_code`, `cah_l2_name`: CAH Level 2 (subject category)
- `cah_l3_code`, `cah_l3_name`: CAH Level 3 (specific subject)

**URLs:**
- `course_url`: Official course page
- `fees_url`: Official fees page
- `teaching_url`: Teaching methods page
- `employment_url`: Employment outcomes page
- `support_url`: Student support page

**Other:**
- `ucas_code`: UCAS programme code
- `updated_date`: Data extraction date

### subject_mappings.csv

Maps 1,092 HECoS codes to CAH classifications:
- `hecos_code`: HECoS subject code (e.g., "100403")
- `hecos_name`: Subject name (e.g., "economics")
- `cah_l1_code` to `cah_l3_name`: Three-level CAH hierarchy

## Subject Classification System

### HECoS (Higher Education Classification of Subjects)

- Granular subject coding system with 1,092 codes
- Used by UK universities since 2019
- Provides detailed subject identification

### CAH (Common Aggregation Hierarchy)

Three-level hierarchy bridging HECoS and legacy JACS codes:

**Level 1** (26 categories): Broad subject areas
- Examples: "medicine and dentistry", "engineering and technology", "social sciences"

**Level 2** (56 categories): Subject groups
- Examples: "economics", "mechanical engineering", "nursing and midwifery"

**Level 3** (166 categories): Specific subjects
- Examples: "economics (non-specific)", "medical engineering", "adult nursing"

## Database Schema

Data is loaded into SQLite database at `data/educalc.db`:

### Tables

**universities**
- Primary key: `ukprn`
- Contains: name, short_name, website, country, league_rank

**courses**
- Primary key: `id` (auto-increment)
- Foreign key: `ukprn` → universities
- Unique constraint: (ukprn, course_id)
- Contains: All course data from courses_unified.csv

**subject_mappings**
- Primary key: `hecos_code`
- Contains: HECoS → CAH mappings

**fees**
- Primary key: `id` (auto-increment)
- Foreign key: `ukprn` → universities
- Contains: Historical fee data (integrated with existing data)

### Indices

- `idx_courses_ukprn`: Fast lookup by university
- `idx_courses_title`: Fast lookup by course name
- `idx_courses_level`: Fast filtering by level
- `idx_courses_hecos`: Fast lookup by subject
- `idx_courses_cah_l1`: Fast filtering by subject area
- `idx_fees_ukprn`: Fast fee lookup by university
- `idx_fees_year`: Fast fee lookup by year

## ETL Pipeline

Data processing scripts in `scripts/hesa/`:

### 1. extract_top_50.py

Extracts top 50 universities and their courses:
```bash
python scripts/hesa/extract_top_50.py
```

**Output:**
- `processed/top_50_universities.csv`
- `processed/courses_raw.csv`

### 2. map_subjects.py

Creates HECoS → CAH subject mappings:
```bash
python scripts/hesa/map_subjects.py
```

**Output:**
- `processed/subject_mappings.csv`
- `processed/cah_hierarchy.csv`

### 3. transform_courses.py

Transforms courses into unified format:
```bash
python scripts/hesa/transform_courses.py
```

**Output:**
- `processed/courses_unified.csv`

### 4. create_db.py

Creates SQLite database and loads all data:
```bash
python scripts/database/create_db.py
```

**Output:**
- `data/educalc.db`

## API Usage

### CourseCatalog Class

Located in `modules/data/course_catalog.py`:

```python
from modules.data.course_catalog import CourseCatalog

catalog = CourseCatalog()

# Get all universities
unis = catalog.get_all_universities()

# Get courses for a university
ukprn = 10007788  # Cambridge
courses = catalog.get_university_courses(ukprn)

# Find specific course
course_info = catalog.find_course_by_title(ukprn, "Economics")

# Search courses
results = catalog.search_courses("Computer Science")

# Get courses by subject
economics_courses = catalog.get_courses_by_subject("CAH15")
```

## UI Integration

### User Experience

The HESA integration enhances the existing UI without disruption:

**University Selector:**
- Before: 3 universities (Cambridge, LSE, Oxford)
- After: 47 universities (top 50)

**Course Selector:**
- ✅ = Course has fee data (ready for calculations)
- 📋 = HESA course (fee data needed, metadata available)

**Course Display:**
1. **Course Classification** (new)
   - Subject Area (CAH Level 1)
   - Subject Category (CAH Level 2)
   - Specific Subject (CAH Level 3)
   - Metadata: HECoS code, mode, duration, UCAS code
   - Links: Course details, fees page, teaching info

2. **Course Fee Information** (existing)
   - Shows for ✅ courses only
   - Annual fee, 3-year total, growth rate, data coverage

### Modified Files

**gui/core/compute.py:**
- `get_universities()`: Returns 47 universities from HESA
- `get_courses()`: Combines fee data + HESA courses
- `get_course_info()`: Adds HESA metadata to fee data

**gui/core/sections.py:**
- `course_selector_section()`: Displays subject classification and links

**gui/core/data_sources.py:**
- Added HESA datasets to downloadable sources

## Statistics

### Course Counts by University (Top 10)

| Rank | University | Courses |
|------|------------|---------|
| 31 | Glasgow | 692 |
| 40 | Swansea | 477 |
| 41 | Kent | 455 |
| 13 | UCL | 447 |
| 35 | Royal Holloway | 420 |
| 28 | Manchester | 418 |
| 30 | Aberdeen | 383 |
| 18 | Edinburgh | 379 |
| 17 | Southampton | 369 |
| 26 | UEA | 350 |

### Subject Distribution (Top 10)

| CAH Level 1 | Subjects |
|-------------|----------|
| Language and area studies | 174 |
| Engineering and technology | 109 |
| Design, creative and performing arts | 93 |
| Historical, philosophical and religious studies | 85 |
| Social sciences | 79 |
| Subjects allied to medicine | 75 |
| Biological and sport sciences | 63 |
| Business and management | 63 |
| Physical sciences | 52 |
| Geography, earth and environmental studies | 48 |

### Fee Data Coverage

| University | Programmes with Fees |
|------------|---------------------|
| LSE | 184 |
| Oxford | 61 |
| Cambridge | 40 |

**Total fee records**: 2,687 spanning 2020/21 to 2026/27

## Data Sources

### HESA Discover Uni

- **Source**: Higher Education Statistics Agency (HESA)
- **Collection**: C24061 (2024/25 academic year)
- **URL**: https://www.hesa.ac.uk/collection/c24061/
- **Downloaded**: September 2025
- **Format**: CSV exports from kis.xml

### HECoS/CAH Classifications

- **Source**: HESA
- **Version**: 1.3.4
- **URL**: https://www.hesa.ac.uk/innovation/hecos
- **Format**: Excel file

### University Rankings

- **Source**: The Complete University Guide
- **Year**: 2026 rankings
- **URL**: https://www.thecompleteuniversityguide.co.uk/league-tables/rankings

## Future Enhancements

### Fee Data Collection

With this integration complete, the next step is systematic fee scraping:

**Priority 1** (Immediate expansion):
- Universities #4-10: St Andrews, Durham, Imperial, Loughborough, Bath, Warwick, Lancaster

**Priority 2** (Next 10):
- Universities #11-20: Exeter, York, UCL, Birmingham, Bristol, Sheffield, Southampton, Edinburgh, King's, Surrey

**Priority 3** (Remaining 30):
- Universities #21-50: Leeds through Portsmouth

**Approach:**
Each course in HESA data includes `fees_url` - direct link to official fees page for scraping.

### Additional HESA Data

Future integration possibilities:
- Employment outcomes (LEO3, LEO5 salary data)
- Student satisfaction (NSS results)
- Continuation rates
- Entry tariffs
- Graduate destinations

## Maintenance

### Updating HESA Data

1. Download latest Discover Uni dataset from HESA
2. Extract CSV files to `data/hesa/raw/`
3. Run ETL pipeline:
   ```bash
   python scripts/hesa/extract_top_50.py
   python scripts/hesa/map_subjects.py
   python scripts/hesa/transform_courses.py
   python scripts/database/create_db.py
   ```
4. Test Streamlit app

### Adding Universities

To expand beyond top 50:
1. Update `TOP_50_UNIVERSITIES` dict in `scripts/hesa/extract_top_50.py`
2. Re-run ETL pipeline
3. Add fee data for new universities

## Notes

- HESA data is updated annually (typically July/August)
- HECoS/CAH mappings are periodically revised
- UKPRN is stable and can be used for long-term tracking
- Fee data in HESA is not included (links only)
- Course availability changes annually

## Support

For issues or questions:
- HESA data: https://www.hesa.ac.uk/support
- Application: https://github.com/anthropics/claude-code/issues
