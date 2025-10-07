# Root Cause Analysis & Fix Specifications

**Analysis Date:** 2025-10-07
**Project:** EducalcClean - HESA Data Pipeline
**Status:** 4 Critical Bugs Identified, All Fixes Specified

---

## Executive Summary

**Current State:**
- Database contains 10,722 courses from 71 CSV rows
- 7 universities incorrectly mapped (Lancaster→Royal Holloway, etc.)
- 581 legitimate course variants lost to over-aggressive deduplication
- All mode/level values show "Unknown"/"Other"
- API and performance are production-ready (100% tests pass, A+ performance)

**Root Cause:** Cascading data quality failure starting with 9 incorrect UKPRNs in the TOP_50_UNIVERSITIES dictionary, amplified by missing institution filtering and suboptimal deduplication strategy.

**Fix Impact:**
- Restore 7 correct universities
- Preserve 581 legitimate course variants
- Decode mode/level correctly
- Reduce data loss from ~5% to <1%

---

## 1. Root Cause Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ROOT CAUSE #1: 9 Incorrect UKPRNs in TOP_50_UNIVERSITIES Dictionary    │
│ File: extract_top_50.py, Lines 13-65                                   │
│ Priority: CRITICAL (blocks all downstream processing)                   │
└─────────────────────────────────────────────────────────────────────────┘
        ├── SYMPTOM A: Wrong universities extracted
        │   ├─ South Wales extracted instead of Essex (rank 39)
        │   ├─ Wales Trinity St David instead of Aston (rank 52)
        │   ├─ Aberystwyth instead of St Andrews (rank 10)
        │   ├─ Wrexham instead of York (rank 22)
        │   ├─ Royal Agricultural instead of Surrey (rank 30)
        │   ├─ Canterbury Christ Church instead of Royal Holloway (rank 45)
        │   └─ Abertay instead of Sussex (rank 55)
        │
        ├── SYMPTOM B: 24 duplicate UKPRNs in universities CSV
        │   ├─ 71 CSV rows contain only 47 unique UKPRNs
        │   └─ Multiple institutions share same UKPRN
        │       Example: UKPRN 10007148 appears 3 times:
        │         • Aberystwyth University (rank 10)
        │         • University of Wales (rank 52)
        │         • Wales Trinity St David (rank 52)
        │
        └── CASCADING IMPACT: Artificial course duplicates created
            ├─ University merge (transform_courses.py line 91) creates 5,654 duplicates
            │   • Same course appears under multiple wrong university names
            │   • Example: Computer Science course duplicated 3x due to 3 institutions
            │     sharing UKPRN 10007148
            │
            └── SECONDARY DAMAGE: Over-aggressive deduplication compensates
                ├─ create_db.py line 167 uses only (ukprn, course_id) for dedup
                ├─ Drops 581 legitimate course variants to remove artificial duplicates
                └─ FINAL IMPACT: Real data loss to fix wrong data upstream

┌─────────────────────────────────────────────────────────────────────────┐
│ ROOT CAUSE #2: Missing Institution Filtering Logic                     │
│ File: extract_top_50.py, Line 90                                       │
│ Priority: HIGH (contributes to duplicate UKPRNs)                        │
└─────────────────────────────────────────────────────────────────────────┘
        ├── SYMPTOM: Partner colleges/NHS trusts extracted alongside main universities
        │   Example: UKPRN 10007148 includes:
        │     • Main: Aberystwyth University
        │     • Partner: Wales Trinity St David
        │     • Partner: University of Wales
        │
        └── IMPACT: Multiple CSV entries at same league table rank
            └─ Amplifies duplicate UKPRN problem from Root Cause #1

┌─────────────────────────────────────────────────────────────────────────┐
│ ROOT CAUSE #3: Suboptimal Deduplication Strategy                       │
│ File: create_db.py, Line 167                                           │
│ Priority: HIGH (causes legitimate data loss)                            │
└─────────────────────────────────────────────────────────────────────────┘
        ├── SYMPTOM: Uses only (ukprn, course_id) for deduplication
        │   └─ Ignores mode, level, duration differences
        │
        └── IMPACT: 581 legitimate course variants treated as duplicates
            Examples lost:
            • Full-time vs Part-time variants (same course_id)
            • 3-year vs 4-year sandwich courses
            • Foundation vs Honours levels
            • Undergraduate vs Postgraduate (different KISLEVEL)

┌─────────────────────────────────────────────────────────────────────────┐
│ ROOT CAUSE #4: Data Type Mismatch in Mode/Level Decoding               │
│ File: transform_courses.py, Lines 119-120                              │
│ Priority: MEDIUM (display issue, not data loss)                         │
└─────────────────────────────────────────────────────────────────────────┘
        ├── SYMPTOM: All courses show mode="Unknown", level="Other"
        │   └─ Decode functions expect integers, CSV contains strings
        │
        └── IMPACT: User-facing display shows no useful mode/level information
            └─ Users cannot filter by Full-time/Part-time or Undergraduate/Postgraduate
```

---

## 2. Fix Specifications

### Fix #1: Correct TOP_50_UNIVERSITIES Dictionary ⚠️ CRITICAL PATH

**File:** `/Users/oliver/projects/educalcclean/scripts/hesa/extract_top_50.py`
**Lines:** 13-65
**Priority:** CRITICAL (blocks all other fixes)
**Estimated Time:** 5 minutes

**Problem:** 9 incorrect UKPRNs cause wrong universities to be extracted and create duplicate UKPRN issues.

**Changes Required:**

| Line | University           | Rank | Current (WRONG)      | Correct UKPRN       |
|------|---------------------|------|---------------------|---------------------|
| 17   | St Andrews          | 10   | 10007148 (Aberystwyth) | 10007803           |
| 27   | York                | 22   | 10007154 (Wrexham)     | 10007167           |
| 35   | Surrey              | 30   | 10007159 (Royal Ag)    | 10007160           |
| 44   | Essex               | 39   | 10007793 (South Wales) | 10007791           |
| 50   | Royal Holloway      | 45   | 10007768 (Canterbury)  | 10005553           |
| 57   | Aston               | 52   | 10007148 (Wales TSD)   | 10007759           |
| 58   | Stirling            | 52   | 10007148 (Duplicate)   | 10007804           |
| 60   | Sussex              | 55   | 10007773 (Abertay)     | 10007806           |
| 61   | Coventry            | 57   | 10007146 (Wrong)       | 10001726           |

**Exact Code Changes:**

```python
# Line 17 - St Andrews
'St Andrews': (10007803, 10),  # WAS: 10007148

# Line 27 - York
'York': (10007167, 22),  # WAS: 10007154

# Line 35 - Surrey
'Surrey': (10007160, 30),  # WAS: 10007159

# Line 44 - Essex
'Essex': (10007791, 39),  # WAS: 10007793

# Line 50 - Royal Holloway
'Royal Holloway': (10005553, 45),  # WAS: 10007768

# Line 57 - Aston
'Aston': (10007759, 52),  # WAS: 10007148

# Line 58 - Stirling
'Stirling': (10007804, 52),  # WAS: 10007148

# Line 60 - Sussex
'Sussex': (10007806, 55),  # WAS: 10007773

# Line 61 - Coventry
'Coventry': (10001726, 57),  # WAS: 10007146
```

**Verification Commands:**

```bash
# Check that correct UKPRNs are now in the file
grep "10007803\|10007167\|10007160\|10007791\|10005553\|10007759\|10007804\|10007806\|10001726" \
  /Users/oliver/projects/educalcclean/scripts/hesa/extract_top_50.py

# Expected: Should find all 9 new UKPRNs

# Run extraction
cd /Users/oliver/projects/educalcclean
python3 scripts/hesa/extract_top_50.py

# Expected output: "✅ Extracted 50 universities" (not 71)

# Verify unique UKPRN count
tail -n +2 data/hesa/processed/top_50_universities.csv | cut -d',' -f1 | sort -u | wc -l

# Expected: 50 (not 47)
```

---

### Fix #2: Add Institution Filtering Logic 🎯 HIGH PRIORITY

**File:** `/Users/oliver/projects/educalcclean/scripts/hesa/extract_top_50.py`
**Location:** After line 90 (after UKPRN filtering, before CSV save)
**Priority:** HIGH
**Estimated Time:** 10 minutes

**Problem:** Partner colleges and NHS trusts are included alongside main universities, creating multiple entries per UKPRN.

**Code to Add:**

```python
    # Filter to primary universities only (remove partner colleges/NHS trusts)
    # This handles cases where a UKPRN has multiple institutions in HESA data
    university_indicators = [
        'University', 'College London', 'Imperial', 'LSE',
        'School of Economics', 'Royal Holloway', 'Queen Mary',
        'School of Hygiene', 'King\'s College', 'Queen\'s University',
        'School of Oriental', 'Royal Veterinary', 'Courtauld Institute'
    ]
    pattern = '|'.join(university_indicators)

    # Keep only rows with university indicators in their legal name
    top_50_df = top_50_df[
        top_50_df['LEGAL_NAME'].str.contains(pattern, case=False, na=False)
    ]

    # Remove duplicates, keeping first occurrence (main campus/primary institution)
    # This ensures exactly one row per UKPRN
    original_count = len(top_50_df)
    top_50_df = top_50_df.drop_duplicates(subset=['UKPRN'], keep='first')
    duplicates_removed = original_count - len(top_50_df)

    if duplicates_removed > 0:
        print(f"   Removed {duplicates_removed} duplicate UKPRNs (partner institutions)")

    print(f"✅ Extracted {len(top_50_df)} universities (expected: 50)")
```

**Insert Location:**

```python
# EXISTING CODE (around line 90):
    top_50_df = hesa_df[hesa_df['UKPRN'].isin(ukprn_list)].copy()

    # ADD NEW CODE HERE (Fix #2)
    # [Insert the code block above]

    # EXISTING CODE (continues):
    # Save to CSV
    output_path = DATA_DIR / 'top_50_universities.csv'
```

**Verification Commands:**

```bash
# Run extraction with new filtering
cd /Users/oliver/projects/educalcclean
python3 scripts/hesa/extract_top_50.py

# Check line count (should be exactly 51: 50 data + 1 header)
wc -l data/hesa/processed/top_50_universities.csv

# Expected: 51 data/hesa/processed/top_50_universities.csv

# Verify no duplicate UKPRNs
tail -n +2 data/hesa/processed/top_50_universities.csv | cut -d',' -f1 | sort | uniq -d

# Expected: (empty output - no duplicates)
```

---

### Fix #3: Update Deduplication Logic 🔧 HIGH PRIORITY

**File:** `/Users/oliver/projects/educalcclean/scripts/database/create_db.py`
**Line:** 167
**Priority:** HIGH
**Estimated Time:** 5 minutes

**Problem:** Current deduplication uses only `(ukprn, course_id)`, which incorrectly treats legitimate variants (Full-time vs Part-time, different durations) as duplicates.

**Current Code (Line 167):**

```python
courses_insert = courses_insert.drop_duplicates(subset=['ukprn', 'course_id'], keep='first')
```

**Replace With:**

```python
# Keep legitimate course variants (FT vs PT, different durations, different levels)
# A course is only a duplicate if ALL these fields match:
# - ukprn: Same institution
# - course_id: Same UCAS code
# - mode: Same delivery mode (Full-time/Part-time/Distance)
# - level: Same qualification level (UG/PG/Foundation)
# - duration_years: Same course length
courses_insert = courses_insert.drop_duplicates(
    subset=['ukprn', 'course_id', 'mode', 'level', 'duration_years'],
    keep='first'
)

# Log deduplication stats
original_count = len(courses_insert) + (len(courses_insert) - len(courses_insert.drop_duplicates(
    subset=['ukprn', 'course_id', 'mode', 'level', 'duration_years'],
    keep='first'
)))
deduped_count = len(courses_insert)
print(f"   Deduplication: {original_count} → {deduped_count} courses ({original_count - deduped_count} duplicates removed)")
```

**Verification Commands:**

```bash
# Run database creation with new deduplication
cd /Users/oliver/projects/educalcclean
python3 scripts/database/create_db.py

# Count courses in database
sqlite3 data/educalc.db "SELECT COUNT(*) FROM courses;"

# Expected: ~11,300 (not 10,722) - restores 581 legitimate variants

# Check that legitimate variants are preserved
sqlite3 data/educalc.db "
SELECT
    ukprn,
    course_id,
    mode,
    level,
    duration_years,
    COUNT(*) as variant_count
FROM courses
GROUP BY ukprn, course_id
HAVING COUNT(*) > 1
LIMIT 10;
"

# Expected: Should show courses with multiple legitimate variants (different modes/durations)
```

---

### Fix #4: Fix Mode/Level Decoding 🔤 MEDIUM PRIORITY

**File:** `/Users/oliver/projects/educalcclean/scripts/hesa/transform_courses.py`
**Lines:** Insert BEFORE line 119
**Priority:** MEDIUM (display issue, not data loss)
**Estimated Time:** 5 minutes

**Problem:** Decode functions expect integer values, but KISMODE/KISLEVEL columns contain strings. This causes all values to fall through to "Unknown"/"Other" defaults.

**Current Code (Lines 119-120):**

```python
df['mode'] = df['KISMODE'].apply(decode_mode)
df['level'] = df['KISLEVEL'].apply(decode_level)
```

**Add BEFORE Line 119:**

```python
    # Convert mode/level codes to strings and strip whitespace for consistent decoding
    # HESA data sometimes has leading/trailing spaces or mixed types
    df['KISMODE'] = df['KISMODE'].astype(str).str.strip()
    df['KISLEVEL'] = df['KISLEVEL'].astype(str).str.strip()

    # Apply decode functions (now work with consistent string input)
    df['mode'] = df['KISMODE'].apply(decode_mode)
    df['level'] = df['KISLEVEL'].apply(decode_level)
```

**Also Update Decode Functions (Lines 15-35):**

```python
def decode_mode(mode_code: str) -> str:
    """Decode KISMODE to readable format"""
    # Convert to string to handle mixed types
    mode_code = str(mode_code).strip()

    mode_map = {
        '1': 'Full-time',
        '2': 'Part-time',
        '3': 'Both',
        '4': 'Distance learning',
        '5': 'Flexible',
    }
    return mode_map.get(mode_code, 'Unknown')

def decode_level(level_code: str) -> str:
    """Decode KISLEVEL to readable format"""
    # Convert to string to handle mixed types
    level_code = str(level_code).strip()

    level_map = {
        '1': 'Undergraduate',
        '2': 'Postgraduate (taught)',
        '3': 'Postgraduate (research)',
        '4': 'Other undergraduate',
        '5': 'Further education',
    }
    return level_map.get(level_code, 'Other')
```

**Verification Commands:**

```bash
# Run transformation with new decoding
cd /Users/oliver/projects/educalcclean
python3 scripts/hesa/transform_courses.py

# Check that mode/level are decoded (not "Unknown"/"Other")
grep -E "Full-time|Part-time|Undergraduate|Postgraduate" data/hesa/processed/courses_unified.csv | wc -l

# Expected: >0 (should find decoded values)

# Check distribution of modes
tail -n +2 data/hesa/processed/courses_unified.csv | cut -d',' -f7 | sort | uniq -c

# Expected output should show:
#   XXXX Full-time
#   XXXX Part-time
#   XXXX Both
# Not:
#   11XXX Unknown

# Check distribution of levels
tail -n +2 data/hesa/processed/courses_unified.csv | cut -d',' -f8 | sort | uniq -c

# Expected output should show:
#   XXXX Undergraduate
#   XXXX Postgraduate (taught)
# Not:
#   11XXX Other
```

---

## 3. Fix Sequence & Verification Plan

**CRITICAL:** Fixes must be applied in this exact order due to dependencies.

### Step 1: Fix UKPRNs (CRITICAL PATH) ⚠️

**Why First:** All downstream processing depends on correct university extraction.

```bash
cd /Users/oliver/projects/educalcclean

# 1. Edit extract_top_50.py lines 13-65
# Apply all 9 UKPRN corrections from Fix #1

# 2. Verify changes were applied
grep "10007803.*St Andrews" scripts/hesa/extract_top_50.py
grep "10007167.*York" scripts/hesa/extract_top_50.py
grep "10007160.*Surrey" scripts/hesa/extract_top_50.py
grep "10007791.*Essex" scripts/hesa/extract_top_50.py
grep "10005553.*Royal Holloway" scripts/hesa/extract_top_50.py
grep "10007759.*Aston" scripts/hesa/extract_top_50.py
grep "10007804.*Stirling" scripts/hesa/extract_top_50.py
grep "10007806.*Sussex" scripts/hesa/extract_top_50.py
grep "10001726.*Coventry" scripts/hesa/extract_top_50.py

# Expected: All 9 commands should find matches

# 3. Run extraction
python3 scripts/hesa/extract_top_50.py

# Expected output:
# ✅ Extracted 50 universities (expected: 50)

# 4. Verify unique UKPRN count
tail -n +2 data/hesa/processed/top_50_universities.csv | cut -d',' -f1 | sort -u | wc -l

# Expected: 50 (not 47)

# 5. Check for duplicate UKPRNs (should be none)
tail -n +2 data/hesa/processed/top_50_universities.csv | cut -d',' -f1 | sort | uniq -d

# Expected: (empty output)
```

**Success Criteria:**
- ✅ 50 unique UKPRNs in CSV
- ✅ 0 duplicate UKPRNs
- ✅ Correct universities present (St Andrews, York, Surrey, Essex, Royal Holloway, Aston, Stirling, Sussex, Coventry)

---

### Step 2: Add Institution Filtering 🎯

**Why Second:** Reinforces Fix #1 by ensuring only primary universities are kept.

```bash
cd /Users/oliver/projects/educalcclean

# 1. Edit extract_top_50.py
# Insert filtering code from Fix #2 after line 90

# 2. Run extraction
python3 scripts/hesa/extract_top_50.py

# Expected output:
# Removed X duplicate UKPRNs (partner institutions)
# ✅ Extracted 50 universities (expected: 50)

# 3. Verify exact row count
wc -l data/hesa/processed/top_50_universities.csv

# Expected: 51 (50 data + 1 header)

# 4. Verify no duplicate UKPRNs remain
tail -n +2 data/hesa/processed/top_50_universities.csv | cut -d',' -f1 | sort | uniq -d

# Expected: (empty output)

# 5. Verify universities are present
cut -d',' -f3 data/hesa/processed/top_50_universities.csv | grep -i "university" | wc -l

# Expected: ~50 (almost all should contain "University")
```

**Success Criteria:**
- ✅ Exactly 50 universities in CSV (51 lines with header)
- ✅ 0 duplicate UKPRNs
- ✅ No partner colleges or NHS trusts

---

### Step 3: Fix Mode/Level Decoding 🔤

**Why Third:** Must happen before database creation to ensure decoded values are in database.

```bash
cd /Users/oliver/projects/educalcclean

# 1. Edit transform_courses.py
# Update decode functions (lines 15-35) from Fix #4
# Add type conversion before line 119 from Fix #4

# 2. Run transformation
python3 scripts/hesa/transform_courses.py

# Expected output:
# ✅ Transformed courses: X courses unified

# 3. Check for decoded mode values
tail -n +2 data/hesa/processed/courses_unified.csv | cut -d',' -f7 | sort | uniq -c

# Expected: Should show distribution like:
#   8500 Full-time
#   2300 Part-time
#    500 Both
# NOT:
#   11300 Unknown

# 4. Check for decoded level values
tail -n +2 data/hesa/processed/courses_unified.csv | cut -d',' -f8 | sort | uniq -c

# Expected: Should show distribution like:
#   9500 Undergraduate
#   1500 Postgraduate (taught)
#    300 Postgraduate (research)
# NOT:
#   11300 Other

# 5. Verify specific decoded values exist
grep -E "Full-time|Part-time" data/hesa/processed/courses_unified.csv | head -5

# Expected: Should show 5 example rows with decoded mode values
```

**Success Criteria:**
- ✅ Mode values decoded (Full-time, Part-time, Both, not "Unknown")
- ✅ Level values decoded (Undergraduate, Postgraduate, not "Other")
- ✅ Realistic distribution of mode/level values

---

### Step 4: Fix Deduplication Logic 🔧

**Why Fourth:** Must be last to operate on correctly transformed data.

```bash
cd /Users/oliver/projects/educalcclean

# 1. Edit create_db.py line 167
# Replace deduplication logic from Fix #3

# 2. Run database creation
python3 scripts/database/create_db.py

# Expected output:
# Deduplication: X → Y courses (Z duplicates removed)
# ✅ Database created: educalc.db

# 3. Count total courses
sqlite3 data/educalc.db "SELECT COUNT(*) FROM courses;"

# Expected: ~11,300 (not 10,722)
# Should be ~581 more courses than before

# 4. Verify legitimate variants are preserved
sqlite3 data/educalc.db "
SELECT
    u.name as university,
    c.course_id,
    c.title,
    c.mode,
    c.duration_years
FROM courses c
JOIN universities u ON c.ukprn = u.ukprn
WHERE c.course_id IN (
    SELECT course_id
    FROM courses
    GROUP BY ukprn, course_id
    HAVING COUNT(*) > 1
)
ORDER BY u.name, c.course_id, c.mode
LIMIT 20;
"

# Expected: Should show courses with multiple legitimate variants
# Example output:
# University of Bath | G100 | Computer Science | Full-time | 3
# University of Bath | G100 | Computer Science | Part-time | 4
# University of Bath | G100 | Computer Science | Full-time | 4 (sandwich)

# 5. Check for zero duplicate variants (same ukprn, course_id, mode, level, duration)
sqlite3 data/educalc.db "
SELECT
    ukprn,
    course_id,
    mode,
    level,
    duration_years,
    COUNT(*) as dupe_count
FROM courses
GROUP BY ukprn, course_id, mode, level, duration_years
HAVING COUNT(*) > 1;
"

# Expected: (empty result set - no true duplicates)
```

**Success Criteria:**
- ✅ ~11,300 courses in database (581 more than before)
- ✅ Legitimate variants preserved (same course_id, different mode/duration)
- ✅ No true duplicates (same composite key)

---

### Step 5: Full Pipeline Re-Run & Final Verification 🚀

**Why Last:** Comprehensive end-to-end test of all fixes.

```bash
cd /Users/oliver/projects/educalcclean

# Full pipeline execution
python3 scripts/hesa/extract_top_50.py && \
python3 scripts/hesa/map_subjects.py && \
python3 scripts/hesa/transform_courses.py && \
python3 scripts/database/create_db.py

# VERIFICATION CHECKLIST:

echo "=== 1. University Extraction ==="
wc -l data/hesa/processed/top_50_universities.csv
# Expected: 51 lines

tail -n +2 data/hesa/processed/top_50_universities.csv | cut -d',' -f1 | sort -u | wc -l
# Expected: 50 unique UKPRNs

echo "=== 2. Course Count ==="
sqlite3 data/educalc.db "SELECT COUNT(*) FROM courses;"
# Expected: ~11,300

echo "=== 3. Mode/Level Decoding ==="
sqlite3 data/educalc.db "SELECT mode, COUNT(*) FROM courses GROUP BY mode;"
# Expected: Distribution of Full-time, Part-time, Both (not all Unknown)

sqlite3 data/educalc.db "SELECT level, COUNT(*) FROM courses GROUP BY level;"
# Expected: Distribution of Undergraduate, Postgraduate (not all Other)

echo "=== 4. Data Quality ==="
sqlite3 data/educalc.db "
SELECT
    (SELECT COUNT(*) FROM universities) as university_count,
    (SELECT COUNT(*) FROM courses) as course_count,
    (SELECT COUNT(DISTINCT ukprn) FROM courses) as universities_with_courses,
    (SELECT COUNT(*) FROM subjects) as subject_count;
"
# Expected:
# university_count: 50
# course_count: ~11,300
# universities_with_courses: 50
# subject_count: ~20-30

echo "=== 5. Sample Course Data ==="
sqlite3 data/educalc.db "
SELECT
    u.name,
    c.course_id,
    c.title,
    c.mode,
    c.level,
    c.duration_years,
    c.annual_fee
FROM courses c
JOIN universities u ON c.ukprn = u.ukprn
LIMIT 5;
"
# Expected: Should show complete, sensible data with decoded mode/level

echo "=== 6. Correct Universities Present ==="
sqlite3 data/educalc.db "
SELECT name FROM universities
WHERE name IN (
    'University of St Andrews',
    'University of York',
    'University of Surrey',
    'University of Essex',
    'Royal Holloway, University of London',
    'Aston University',
    'University of Stirling',
    'University of Sussex',
    'Coventry University'
);
"
# Expected: All 9 corrected universities should appear

echo "=== 7. Wrong Universities Absent ==="
sqlite3 data/educalc.db "
SELECT name FROM universities
WHERE name LIKE '%Aberystwyth%'
   OR name LIKE '%South Wales%'
   OR name LIKE '%Wales Trinity%'
   OR name LIKE '%Canterbury Christ%'
   OR name LIKE '%Royal Agricultural%'
   OR name LIKE '%Wrexham%'
   OR name LIKE '%Abertay%';
"
# Expected: (empty result set - these universities should NOT be present)
```

**Success Criteria:**
- ✅ All 7 verification checks pass
- ✅ 50 correct universities
- ✅ ~11,300 courses with decoded mode/level
- ✅ 0 data loss (all legitimate variants preserved)
- ✅ Wrong universities absent

---

## 4. Risk Analysis

### Fix #1: Correct UKPRNs ✅ LOW RISK

**Risk Level:** LOW
**Complexity:** Trivial (data-only change)
**Blast Radius:** Isolated to TOP_50_UNIVERSITIES dictionary

**Risks:**
- ❌ Minimal: Pure data correction, no logic changes
- ⚠️ Typo risk: Could introduce typo in UKPRN (9-digit number)

**Mitigation:**
- Use grep verification after edit
- Cross-reference with HESA official data
- Automated validation function (see Section 5)

**Rollback Plan:**
```bash
# If issues arise, revert to original UKPRNs
git checkout HEAD -- scripts/hesa/extract_top_50.py
```

---

### Fix #2: Add Institution Filtering ⚠️ MEDIUM RISK

**Risk Level:** MEDIUM
**Complexity:** Moderate (new filtering logic)
**Blast Radius:** Could exclude legitimate universities if pattern too restrictive

**Risks:**
- ⚠️ Over-filtering: Could exclude legitimate universities that don't match pattern
  - Example: "Imperial College London" might not match if pattern only has "University"
- ⚠️ Under-filtering: Could still allow partner institutions if pattern insufficient
- ⚠️ Edge cases: Specialist institutions (LSE, Imperial) have non-standard names

**Mitigation:**
- Pattern includes edge cases: 'Imperial', 'LSE', 'School of Economics', etc.
- Verification step checks that exactly 50 universities extracted
- Manual review of CSV after extraction
- `keep='first'` ensures main campus selected if filtering fails

**Rollback Plan:**
```bash
# Remove filtering code if it excludes legitimate universities
# Fall back to Fix #1 only (corrected UKPRNs without filtering)
git diff scripts/hesa/extract_top_50.py
# Manually remove lines added in Fix #2
```

**Testing Strategy:**
```bash
# After applying fix, verify all top 10 universities present
sqlite3 data/educalc.db "
SELECT name, league_rank
FROM universities
WHERE league_rank <= 10
ORDER BY league_rank;
"
# Expected: Oxford, Cambridge, LSE, St Andrews, Imperial, Durham, UCL, Bath, Warwick, Loughborough
```

---

### Fix #3: Update Deduplication Logic ⚠️ MEDIUM RISK

**Risk Level:** MEDIUM
**Complexity:** Moderate (changes deduplication criteria)
**Blast Radius:** Could allow true duplicates if composite key insufficient

**Risks:**
- ⚠️ Duplicate creep: Could allow true duplicates if composite key doesn't capture uniqueness
  - Example: Two identical courses with same UKPRN, course_id, mode, level, duration
- ⚠️ Data explosion: If HESA data has data quality issues, could preserve bad duplicates
- ⚠️ Performance: More courses in database = slightly slower queries (minimal impact)

**Mitigation:**
- Composite key `(ukprn, course_id, mode, level, duration_years)` is comprehensive
- Verification query checks for true duplicates after fix (see Step 4, check #5)
- Agent 4 confirmed performance is still optimal even with more courses
- Can always revert to stricter deduplication if duplicates appear

**Rollback Plan:**
```bash
# If true duplicates appear, revert to original deduplication
git checkout HEAD -- scripts/database/create_db.py
python3 scripts/database/create_db.py
```

**Testing Strategy:**
```bash
# Check for true duplicates (same composite key)
sqlite3 data/educalc.db "
SELECT
    ukprn,
    course_id,
    mode,
    level,
    duration_years,
    COUNT(*) as dupe_count,
    GROUP_CONCAT(title) as titles
FROM courses
GROUP BY ukprn, course_id, mode, level, duration_years
HAVING COUNT(*) > 1;
"
# Expected: (empty result set)
```

---

### Fix #4: Fix Mode/Level Decoding ✅ LOW RISK

**Risk Level:** LOW
**Complexity:** Simple (type conversion)
**Blast Radius:** Isolated to mode/level fields

**Risks:**
- ❌ Minimal: String conversion is safe and non-destructive
- ⚠️ Decode failure: If HESA data has unexpected values, might still default to Unknown/Other

**Mitigation:**
- Type conversion handles mixed types safely
- Decode functions have fallback to "Unknown"/"Other"
- Verification checks distribution of decoded values
- Display-only issue (doesn't affect data integrity)

**Rollback Plan:**
```bash
# If decoding fails, revert changes
git checkout HEAD -- scripts/hesa/transform_courses.py
python3 scripts/hesa/transform_courses.py
```

**Testing Strategy:**
```bash
# Check that most courses are decoded (not defaulting to Unknown/Other)
sqlite3 data/educalc.db "
SELECT
    (SELECT COUNT(*) FROM courses WHERE mode = 'Unknown') * 100.0 / COUNT(*) as unknown_pct,
    (SELECT COUNT(*) FROM courses WHERE level = 'Other') * 100.0 / COUNT(*) as other_pct
FROM courses;
"
# Expected: Both percentages < 5% (most should be decoded)
```

---

### Overall Risk Assessment

**Risk Matrix:**

| Fix | Risk Level | Impact | Likelihood | Priority |
|-----|-----------|--------|-----------|----------|
| #1 UKPRNs | LOW | High | Low | CRITICAL |
| #2 Filtering | MEDIUM | High | Medium | HIGH |
| #3 Deduplication | MEDIUM | Medium | Medium | HIGH |
| #4 Mode/Level | LOW | Low | Low | MEDIUM |

**Recommended Approach:** Apply fixes sequentially with verification at each step. If any fix fails verification, rollback that fix before proceeding.

**Estimated Total Time:** 30-45 minutes (including all verification steps)

---

## 5. Regression Prevention

### Test Suite Addition

Add these validation functions to prevent regression:

#### File: `/Users/oliver/projects/educalcclean/scripts/hesa/extract_top_50.py`

```python
def validate_top_50_dict():
    """
    Ensure no duplicate UKPRNs in TOP_50_UNIVERSITIES dictionary.
    Call this at module load to catch errors before extraction runs.
    """
    ukprns = [data[0] for data in TOP_50_UNIVERSITIES.values()]

    # Check total count
    assert len(ukprns) == 50, f"Expected 50 UKPRNs in dictionary, got {len(ukprns)}"

    # Check for duplicates
    unique_ukprns = set(ukprns)
    assert len(unique_ukprns) == 50, f"Duplicate UKPRNs found! Only {len(unique_ukprns)} unique out of 50"

    # Check for known incorrect UKPRNs (from previous bugs)
    wrong_ukprns = [
        10007148,  # Was incorrectly used 3 times (St Andrews, Aston, Stirling)
        10007154,  # Was incorrectly mapped to York
        10007159,  # Was incorrectly mapped to Surrey
        10007793,  # Was incorrectly mapped to Essex
        10007768,  # Was incorrectly mapped to Royal Holloway
        10007773,  # Was incorrectly mapped to Sussex
        10007146,  # Was incorrectly mapped to Coventry
    ]

    duplicates_found = [ukprn for ukprn in ukprns if ukprns.count(ukprn) > 1]
    if duplicates_found:
        raise ValueError(f"Duplicate UKPRNs detected: {set(duplicates_found)}")

    wrong_found = [ukprn for ukprn in wrong_ukprns if ukprn in ukprns]
    if wrong_found:
        raise ValueError(f"Previously incorrect UKPRNs detected: {wrong_found}")

    print("✓ TOP_50_UNIVERSITIES dictionary validated (50 unique UKPRNs)")

# Call validation at module initialization
validate_top_50_dict()
```

#### File: `/Users/oliver/projects/educalcclean/scripts/database/create_db.py`

```python
def validate_no_data_loss():
    """
    Verify course counts match expectations and data loss is within acceptable limits.
    Acceptable loss: <10% (accounting for true duplicates in source data)
    """
    import pandas as pd
    import sqlite3

    # Count courses in source CSV
    csv_path = 'data/hesa/processed/courses_unified.csv'
    csv_count = len(pd.read_csv(csv_path))

    # Count courses in database
    conn = sqlite3.connect('data/educalc.db')
    db_count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    conn.close()

    # Calculate loss percentage
    loss_pct = (csv_count - db_count) / csv_count * 100

    # Check for excessive data loss
    assert loss_pct < 10, f"Excessive data loss detected: {loss_pct:.1f}% ({csv_count - db_count} courses)"
    assert loss_pct >= 0, f"Database has more courses than CSV! Loss: {loss_pct:.1f}% (possible duplicate bug)"

    print(f"✓ Data loss acceptable: {loss_pct:.1f}% ({csv_count} → {db_count} courses)")

def validate_no_duplicates():
    """
    Ensure no true duplicates exist in database.
    True duplicate = same (ukprn, course_id, mode, level, duration_years)
    """
    import sqlite3

    conn = sqlite3.connect('data/educalc.db')

    duplicates = conn.execute("""
        SELECT
            ukprn,
            course_id,
            mode,
            level,
            duration_years,
            COUNT(*) as dupe_count
        FROM courses
        GROUP BY ukprn, course_id, mode, level, duration_years
        HAVING COUNT(*) > 1
    """).fetchall()

    conn.close()

    if duplicates:
        print(f"WARNING: {len(duplicates)} duplicate course entries found!")
        for dupe in duplicates[:5]:  # Show first 5
            print(f"  UKPRN {dupe[0]}, Course {dupe[1]}, Mode {dupe[2]}, Level {dupe[3]}, Duration {dupe[4]}: {dupe[5]} copies")
        raise ValueError(f"Database contains {len(duplicates)} true duplicate entries")

    print("✓ No duplicate courses in database")

def validate_mode_level_decoded():
    """
    Ensure mode/level values are properly decoded (not all Unknown/Other).
    """
    import sqlite3

    conn = sqlite3.connect('data/educalc.db')

    # Check mode distribution
    mode_stats = conn.execute("""
        SELECT
            mode,
            COUNT(*) as count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM courses) as percentage
        FROM courses
        GROUP BY mode
        ORDER BY count DESC
    """).fetchall()

    # Check level distribution
    level_stats = conn.execute("""
        SELECT
            level,
            COUNT(*) as count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM courses) as percentage
        FROM courses
        GROUP BY level
        ORDER BY count DESC
    """).fetchall()

    conn.close()

    # Find Unknown/Other percentages
    unknown_pct = next((pct for mode, count, pct in mode_stats if mode == 'Unknown'), 0)
    other_pct = next((pct for level, count, pct in level_stats if level == 'Other'), 0)

    # Assert most courses are decoded
    assert unknown_pct < 50, f"Too many Unknown modes: {unknown_pct:.1f}% (decoding may have failed)"
    assert other_pct < 50, f"Too many Other levels: {other_pct:.1f}% (decoding may have failed)"

    print(f"✓ Mode/level decoded properly (Unknown: {unknown_pct:.1f}%, Other: {other_pct:.1f}%)")

def validate_correct_universities():
    """
    Ensure the 9 corrected universities are present and the 7 wrong universities are absent.
    """
    import sqlite3

    conn = sqlite3.connect('data/educalc.db')

    # Universities that SHOULD be present (after Fix #1)
    correct_universities = [
        ('10007803', 'St Andrews'),
        ('10007167', 'York'),
        ('10007160', 'Surrey'),
        ('10007791', 'Essex'),
        ('10005553', 'Royal Holloway'),
        ('10007759', 'Aston'),
        ('10007804', 'Stirling'),
        ('10007806', 'Sussex'),
        ('10001726', 'Coventry'),
    ]

    # Universities that SHOULD NOT be present (before Fix #1)
    wrong_universities = [
        'Aberystwyth',
        'South Wales',
        'Wales Trinity',
        'Canterbury Christ Church',
        'Royal Agricultural',
        'Wrexham',
        'Abertay',
    ]

    # Check correct universities present
    for ukprn, name in correct_universities:
        result = conn.execute(
            "SELECT COUNT(*) FROM universities WHERE ukprn = ? OR name LIKE ?",
            (ukprn, f'%{name}%')
        ).fetchone()[0]

        if result == 0:
            raise ValueError(f"Correct university missing: {name} (UKPRN {ukprn})")

    # Check wrong universities absent
    for name in wrong_universities:
        result = conn.execute(
            "SELECT COUNT(*) FROM universities WHERE name LIKE ?",
            (f'%{name}%',)
        ).fetchone()[0]

        if result > 0:
            raise ValueError(f"Wrong university present: {name} (should have been excluded)")

    conn.close()

    print("✓ Correct universities present, wrong universities absent")

# Add to main() function at end:
def main():
    # ... existing code ...

    # VALIDATION SUITE
    print("\n=== Running Data Validation ===")
    validate_no_data_loss()
    validate_no_duplicates()
    validate_mode_level_decoded()
    validate_correct_universities()
    print("✅ All validations passed\n")
```

#### File: `/Users/oliver/projects/educalcclean/scripts/tests/test_data_integrity.py` (NEW)

```python
"""
Data integrity test suite.
Run this after pipeline execution to verify all fixes are working.
"""
import sqlite3
import pandas as pd
from pathlib import Path

def test_ukprn_uniqueness():
    """Test that universities CSV has exactly 50 unique UKPRNs"""
    csv_path = Path('data/hesa/processed/top_50_universities.csv')
    df = pd.read_csv(csv_path)

    unique_ukprns = df['UKPRN'].nunique()
    total_rows = len(df)

    assert unique_ukprns == 50, f"Expected 50 unique UKPRNs, got {unique_ukprns}"
    assert total_rows == 50, f"Expected 50 rows, got {total_rows}"

    # Check for duplicates
    duplicates = df[df.duplicated(subset=['UKPRN'], keep=False)]
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate UKPRNs: {duplicates['UKPRN'].tolist()}"

    print("✓ UKPRN uniqueness test passed")

def test_course_variants_preserved():
    """Test that legitimate course variants are preserved (not deduplicated)"""
    conn = sqlite3.connect('data/educalc.db')

    # Find courses with multiple variants
    variants = conn.execute("""
        SELECT
            ukprn,
            course_id,
            COUNT(DISTINCT mode) as mode_variants,
            COUNT(DISTINCT duration_years) as duration_variants,
            COUNT(*) as total_variants
        FROM courses
        GROUP BY ukprn, course_id
        HAVING COUNT(*) > 1
    """).fetchall()

    conn.close()

    # Should have SOME courses with multiple variants
    assert len(variants) > 0, "No course variants found - over-deduplication may have occurred"
    assert len(variants) > 100, f"Only {len(variants)} courses with variants - expected >100"

    print(f"✓ Course variants preserved: {len(variants)} courses have multiple legitimate variants")

def test_mode_level_distribution():
    """Test that mode/level values are properly distributed (not all Unknown/Other)"""
    conn = sqlite3.connect('data/educalc.db')

    # Mode distribution
    modes = conn.execute("""
        SELECT mode, COUNT(*) as count
        FROM courses
        GROUP BY mode
    """).fetchall()

    # Level distribution
    levels = conn.execute("""
        SELECT level, COUNT(*) as count
        FROM courses
        GROUP BY level
    """).fetchall()

    conn.close()

    # Check that we have variety (not all one value)
    assert len(modes) > 1, f"Only {len(modes)} distinct mode value(s) - decoding may have failed"
    assert len(levels) > 1, f"Only {len(levels)} distinct level value(s) - decoding may have failed"

    # Check for Unknown/Other
    mode_dict = dict(modes)
    level_dict = dict(levels)

    total_courses = sum(mode_dict.values())
    unknown_pct = (mode_dict.get('Unknown', 0) / total_courses) * 100
    other_pct = (level_dict.get('Other', 0) / total_courses) * 100

    assert unknown_pct < 50, f"Too many Unknown modes: {unknown_pct:.1f}%"
    assert other_pct < 50, f"Too many Other levels: {other_pct:.1f}%"

    print(f"✓ Mode/level distribution healthy (Unknown: {unknown_pct:.1f}%, Other: {other_pct:.1f}%)")

def test_correct_universities_present():
    """Test that the 9 corrected universities are in database"""
    conn = sqlite3.connect('data/educalc.db')

    correct_ukprns = [
        '10007803',  # St Andrews
        '10007167',  # York
        '10007160',  # Surrey
        '10007791',  # Essex
        '10005553',  # Royal Holloway
        '10007759',  # Aston
        '10007804',  # Stirling
        '10007806',  # Sussex
        '10001726',  # Coventry
    ]

    for ukprn in correct_ukprns:
        result = conn.execute(
            "SELECT name FROM universities WHERE ukprn = ?",
            (ukprn,)
        ).fetchone()

        assert result is not None, f"Correct university missing: UKPRN {ukprn}"

    conn.close()

    print("✓ All 9 corrected universities present")

def test_no_data_loss():
    """Test that data loss is within acceptable limits (<10%)"""
    csv_path = Path('data/hesa/processed/courses_unified.csv')
    csv_count = len(pd.read_csv(csv_path))

    conn = sqlite3.connect('data/educalc.db')
    db_count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    conn.close()

    loss_pct = (csv_count - db_count) / csv_count * 100

    assert loss_pct < 10, f"Excessive data loss: {loss_pct:.1f}%"
    assert loss_pct >= 0, f"Database has more courses than CSV: {loss_pct:.1f}%"

    print(f"✓ Data loss acceptable: {loss_pct:.1f}% ({csv_count} → {db_count} courses)")

if __name__ == '__main__':
    print("=== Data Integrity Test Suite ===\n")

    test_ukprn_uniqueness()
    test_course_variants_preserved()
    test_mode_level_distribution()
    test_correct_universities_present()
    test_no_data_loss()

    print("\n✅ All tests passed!")
```

### Running Regression Tests

```bash
# After any code changes, run validation:
cd /Users/oliver/projects/educalcclean

# Full pipeline with validation
python3 scripts/hesa/extract_top_50.py && \
python3 scripts/hesa/map_subjects.py && \
python3 scripts/hesa/transform_courses.py && \
python3 scripts/database/create_db.py

# Run test suite
python3 scripts/tests/test_data_integrity.py

# Expected output:
# === Data Integrity Test Suite ===
# ✓ UKPRN uniqueness test passed
# ✓ Course variants preserved: 200+ courses have multiple legitimate variants
# ✓ Mode/level distribution healthy (Unknown: 2.3%, Other: 1.8%)
# ✓ All 9 corrected universities present
# ✓ Data loss acceptable: 4.2% (11500 → 11000 courses)
# ✅ All tests passed!
```

---

## 6. Post-Fix Validation Checklist

After applying all fixes, verify these metrics:

### Data Quality Metrics

| Metric | Before | After (Expected) | Status |
|--------|--------|------------------|--------|
| Universities in CSV | 71 rows | 50 rows | ⬜ |
| Unique UKPRNs | 47 | 50 | ⬜ |
| Duplicate UKPRNs | 24 | 0 | ⬜ |
| Courses in database | 10,722 | ~11,300 | ⬜ |
| Courses with mode="Unknown" | ~100% | <5% | ⬜ |
| Courses with level="Other" | ~100% | <5% | ⬜ |
| Correct universities present | 43/50 | 50/50 | ⬜ |
| Wrong universities present | 7 | 0 | ⬜ |
| Data loss percentage | ~5.0% | <1.0% | ⬜ |

### Functional Requirements

- ⬜ API tests still pass (15/15)
- ⬜ Query performance still optimal (<200ms)
- ⬜ Database size reasonable (<10MB)
- ⬜ Course variants preserved (FT/PT/sandwich)
- ⬜ No true duplicates in database
- ⬜ Mode/level decoded correctly
- ⬜ All 50 universities have courses

---

## 7. Known Limitations & Future Improvements

### Known Limitations (NOT fixed by this analysis)

1. **CAH codes not populated** (Agent 3 finding)
   - Many courses have NULL CAH subject codes
   - Not a bug - HESA data limitation
   - Future: Infer from course titles or use alternative subject taxonomy

2. **Sandwich year logic** (Design decision)
   - Sandwich courses show extended duration (e.g., 4 years instead of 3)
   - Not a bug - intentional design choice
   - Future: Add explicit `has_sandwich_year` boolean field

3. **Part-time duration complexity** (Data ambiguity)
   - PT courses may have variable durations depending on student pace
   - HESA data shows "typical" duration
   - Future: Add duration_min/duration_max ranges

### Future Improvements

1. **Automated UKPRN validation**
   - Add CI/CD check that validates TOP_50_UNIVERSITIES dict
   - Cross-reference against official HESA UKPRN register
   - Alert on any UKPRN changes

2. **Enhanced deduplication logging**
   - Log which courses are being deduplicated and why
   - Export duplicate report CSV for manual review
   - Track deduplication statistics over time

3. **Mode/level decoding coverage**
   - Monitor percentage of "Unknown"/"Other" values over time
   - Alert if percentage exceeds threshold
   - Add decode coverage to test suite

4. **Data lineage tracking**
   - Track each course from source CSV → transforms → database
   - Log why courses are dropped (duplicate, missing data, etc.)
   - Create data quality dashboard

---

## Appendix A: Quick Reference Commands

### Extract Only
```bash
python3 scripts/hesa/extract_top_50.py
wc -l data/hesa/processed/top_50_universities.csv  # Should be 51
```

### Full Pipeline
```bash
python3 scripts/hesa/extract_top_50.py && \
python3 scripts/hesa/map_subjects.py && \
python3 scripts/hesa/transform_courses.py && \
python3 scripts/database/create_db.py
```

### Quick Validation
```bash
# Count courses
sqlite3 data/educalc.db "SELECT COUNT(*) FROM courses;"

# Check mode distribution
sqlite3 data/educalc.db "SELECT mode, COUNT(*) FROM courses GROUP BY mode;"

# Check correct universities
sqlite3 data/educalc.db "SELECT name FROM universities WHERE ukprn IN ('10007803','10007167','10007160','10007791','10005553','10007759','10007804','10007806','10001726');"
```

### Run Tests
```bash
python3 scripts/tests/test_data_integrity.py
```

---

## Appendix B: File Reference

### Files Modified by Fixes

| Fix # | File | Lines | Description |
|-------|------|-------|-------------|
| 1 | `/Users/oliver/projects/educalcclean/scripts/hesa/extract_top_50.py` | 17, 27, 35, 44, 50, 57, 58, 60, 61 | Correct 9 UKPRNs |
| 2 | `/Users/oliver/projects/educalcclean/scripts/hesa/extract_top_50.py` | After 90 | Add institution filtering |
| 3 | `/Users/oliver/projects/educalcclean/scripts/database/create_db.py` | 167 | Update deduplication logic |
| 4 | `/Users/oliver/projects/educalcclean/scripts/hesa/transform_courses.py` | 15-35, before 119 | Fix mode/level decoding |

### Files Created for Testing

- `/Users/oliver/projects/educalcclean/scripts/tests/test_data_integrity.py` (NEW)

### Data Files Affected

- `/Users/oliver/projects/educalcclean/data/hesa/processed/top_50_universities.csv` (will change from 71 to 50 rows)
- `/Users/oliver/projects/educalcclean/data/hesa/processed/courses_unified.csv` (mode/level will decode properly)
- `/Users/oliver/projects/educalcclean/data/educalc.db` (will grow from 10,722 to ~11,300 courses)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-07 | Agent 5 (Root Cause Analyzer) | Initial analysis and fix specifications |

---

**END OF REPORT**
