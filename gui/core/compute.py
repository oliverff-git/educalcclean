"""
Compute layer for the multipage refactor.
Contains chart functions and wrapper functions for clean interfaces between pages and calculators.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .state import get_state, init_processors
from .ui import format_inr, format_gbp, format_percentage


@st.cache_data(ttl=3600)  # Cache charts for 1 hour
def create_fee_projection_chart(projections_data):
    """Create professional chart showing fee projections over time"""
    course_info = projections_data['course_info']
    fee_projections = projections_data['fee_projections']

    # Prepare data for chart
    years = list(fee_projections.keys())
    fees = list(fee_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data with professional colors
    if historical_years:
        historical_fees = [fee_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_fees,
            mode='lines+markers',
            name='Historical Data',
            line=dict(color='#1E40AF', width=3),  # Professional blue
            marker=dict(size=6, color='#1E40AF'),
            hovertemplate='<b>%{x}</b><br>Fee: £%{y:,.0f}<extra></extra>'
        ))

    # Projected data with professional styling
    if projected_years:
        # Connect last historical to first projected
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_fees = [fee_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_fees,
            mode='lines+markers',
            name='Projected',
            line=dict(color='#059669', width=3, dash='dash'),  # Professional green
            marker=dict(size=6, color='#059669'),
            hovertemplate='<b>%{x}</b><br>Projected Fee: £%{y:,.0f}<extra></extra>'
        ))

    # Professional layout styling
    fig.update_layout(
        title=dict(
            text=f"<b>{course_info['university']} - {course_info['programme']}</b><br><sub>Annual Fee Projections (CAGR: {course_info['cagr_pct']:.1f}%)</sub>",
            font=dict(size=16, color='#0F172A'),
            x=0.05
        ),
        xaxis=dict(
            title=dict(
                text="Year",
                font=dict(color='#374151', size=14)
            ),
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickfont=dict(color='#6B7280', size=12)
        ),
        yaxis=dict(
            title=dict(
                text="Annual Fee (GBP)",
                font=dict(color='#374151', size=14)
            ),
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickfont=dict(color='#6B7280', size=12),
            tickformat='£,.0f'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="system-ui, -apple-system, sans-serif", size=12),
        margin=dict(l=60, r=40, t=80, b=60),
        height=450,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            y=-0.15,
            font=dict(color='#374151', size=12)
        )
    )

    return fig


@st.cache_data(ttl=3600)  # Cache charts for 1 hour
def create_fx_projection_chart(projections_data):
    """Create professional FX projection chart"""
    fx_projections = projections_data['fx_projections']

    years = list(fx_projections.keys())
    rates = list(fx_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data with professional colors
    if historical_years:
        historical_rates = [fx_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_rates,
            mode='lines+markers',
            name='Historical Rates',
            line=dict(color='#DC2626', width=3),  # Professional red for exchange rates
            marker=dict(size=6, color='#DC2626'),
            hovertemplate='<b>%{x}</b><br>Rate: ₹%{y:,.2f}/£<extra></extra>'
        ))

    # Projected data with professional styling
    if projected_years:
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_rates = [fx_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_rates,
            mode='lines+markers',
            name='Projected Rates',
            line=dict(color='#EA580C', width=3, dash='dash'),  # Professional orange
            marker=dict(size=6, color='#EA580C'),
            hovertemplate='<b>%{x}</b><br>Projected Rate: ₹%{y:,.2f}/£<extra></extra>'
        ))

    # Professional layout styling
    fig.update_layout(
        title=dict(
            text="<b>GBP/INR Exchange Rate Projections</b><br><sub>Historical CAGR: 4.18% (Conservative Estimate)</sub>",
            font=dict(size=16, color='#0F172A'),
            x=0.05
        ),
        xaxis=dict(
            title=dict(
                text="Year",
                font=dict(color='#374151', size=14)
            ),
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickfont=dict(color='#6B7280', size=12)
        ),
        yaxis=dict(
            title=dict(
                text="Exchange Rate (₹ per £)",
                font=dict(color='#374151', size=14)
            ),
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickfont=dict(color='#6B7280', size=12),
            tickformat='₹,.0f'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="system-ui, -apple-system, sans-serif", size=12),
        margin=dict(l=60, r=40, t=80, b=60),
        height=450,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            y=-0.15,
            font=dict(color='#374151', size=12)
        )
    )

    return fig


def get_payg_projection(university: str, course: str, start_year: int, edu_year: int, duration: int = 3):
    """Get pay-as-you-go projection data"""
    data_processor, calculator = init_processors()
    clean_course = clean_course_name(course)
    return calculator.get_projection_details(university, clean_course, edu_year)


def compare_strategies(university: str, course: str, conversion_year: int, education_year: int):
    """Compare all savings strategies"""
    data_processor, calculator = init_processors()
    clean_course = clean_course_name(course)
    return calculator.compare_all_strategies(university, clean_course, conversion_year, education_year)


def get_roi_scenarios(university: str, course: str, conversion_year: int, education_year: int,
                     investment_amount: float, strategies: List[str]):
    """Get ROI investment scenarios"""
    data_processor, calculator = init_processors()
    clean_course = clean_course_name(course)
    return calculator.calculate_all_roi_scenarios(
        university, clean_course, conversion_year, education_year, investment_amount, strategies
    )


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def create_strategy_comparison_chart(scenarios):
    """Create professional bar chart comparing strategy costs"""
    if not scenarios:
        return None

    strategy_names = [scenario.strategy_name for scenario in scenarios]
    total_costs = [scenario.total_cost_inr for scenario in scenarios]

    # Format costs in lakhs for better readability
    formatted_costs = [cost / 100000 for cost in total_costs]  # Convert to lakhs
    hover_texts = [f"<b>{name}</b><br>Cost: ₹{cost:,.0f}<br>({cost/100000:.1f}L)"
                   for name, cost in zip(strategy_names, total_costs)]

    # Professional color scheme - highlight best strategy
    colors = ['#059669' if i == 0 else '#1E40AF' if i == 1 else '#374151'
              for i in range(len(scenarios))]

    fig = go.Figure(data=[go.Bar(
        x=strategy_names,
        y=formatted_costs,
        marker_color=colors,
        hovertemplate='%{text}<extra></extra>',
        text=hover_texts,
        textposition='none'
    )])

    # Professional layout styling
    fig.update_layout(
        title=dict(
            text="<b>Strategy Cost Comparison</b><br><sub>Total Education Cost by Strategy</sub>",
            font=dict(size=16, color='#0F172A'),
            x=0.05
        ),
        xaxis=dict(
            title=dict(
                text="Strategy",
                font=dict(color='#374151', size=14)
            ),
            gridcolor='#E2E8F0',
            showgrid=False,
            linecolor='#E2E8F0',
            tickfont=dict(color='#6B7280', size=12),
            tickangle=-45
        ),
        yaxis=dict(
            title=dict(
                text="Total Cost (Lakhs ₹)",
                font=dict(color='#374151', size=14)
            ),
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickfont=dict(color='#6B7280', size=12),
            tickformat='₹.1f'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="system-ui, -apple-system, sans-serif", size=12),
        margin=dict(l=60, r=40, t=80, b=100),  # Extra bottom margin for rotated labels
        height=450,
        showlegend=False
    )

    # Add value labels on bars for better readability
    for i, (cost_lakhs, cost_total) in enumerate(zip(formatted_costs, total_costs)):
        fig.add_annotation(
            x=strategy_names[i],
            y=cost_lakhs + max(formatted_costs) * 0.08,  # Raised higher above bars for better readability
            text=f"₹{cost_lakhs:.1f}L",
            showarrow=False,
            font=dict(color='#374151', size=12, family="system-ui"),
            xanchor='center'
        )

    return fig


def get_course_info(university: str, course: str):
    """Get course information from data processor + HESA metadata"""
    from modules.data.course_catalog import CourseCatalog

    try:
        catalog = CourseCatalog()
        data_processor, calculator = init_processors()

        # Clean course name for lookups
        clean_course = clean_course_name(course)
        has_fee_data = course.startswith('✅')

        # Initialize result dictionary
        result = {}

        # Get fee info if available
        if has_fee_data:
            try:
                course_data = data_processor.get_course_info(university, clean_course)
                result = {
                    'latest_fee': course_data.get('latest_fee', 0),
                    'cagr_pct': course_data.get('cagr_pct', 0),
                    'data_points': course_data.get('data_points', 0),
                    'transparency': course_data.get('transparency'),
                    'latest_actual_year': course_data.get('latest_actual_year', '2024/25'),
                    'has_fee_data': True
                }
            except:
                result = {'has_fee_data': False}
        else:
            result = {'has_fee_data': False}

        # Get HESA metadata
        ukprn = catalog.get_ukprn_by_name(university)
        if ukprn:
            hesa_data = catalog.find_course_by_title(ukprn, clean_course)

            if hesa_data:
                result.update({
                    'hecos_code': hesa_data.get('hecos_primary'),
                    'hecos_name': hesa_data.get('hecos_name'),
                    'cah_subject': hesa_data.get('cah_l3_name'),
                    'cah_category': hesa_data.get('cah_l2_name'),
                    'cah_level1': hesa_data.get('cah_l1_name'),
                    'mode': hesa_data.get('mode'),
                    'level': hesa_data.get('level'),
                    'duration': hesa_data.get('duration_years'),
                    'honours': hesa_data.get('honours'),
                    'ucas_code': hesa_data.get('ucas_code'),
                    'course_url': hesa_data.get('course_url'),
                    'fees_url': hesa_data.get('fees_url'),
                    'teaching_url': hesa_data.get('teaching_url'),
                    'employment_url': hesa_data.get('employment_url'),
                    'has_hesa_data': True
                })
            else:
                result['has_hesa_data'] = False

        return result

    except Exception as e:
        # Fallback to original method
        st.warning(f"Could not load HESA metadata: {e}")
        data_processor, calculator = init_processors()
        return data_processor.get_course_info(university, course)


@st.cache_data(ttl=86400)  # Cache for 24 hours (universities change very rarely)
def get_universities():
    """Get list of available universities from HESA data"""
    from modules.data.course_catalog import CourseCatalog

    try:
        catalog = CourseCatalog()
        unis_df = catalog.get_all_universities()

        # Return short names sorted by league rank
        return unis_df['short_name'].tolist()
    except Exception as e:
        # Fallback to original 3 universities if HESA data not available
        st.warning(f"HESA data not available, using limited dataset: {e}")
        data_processor, calculator = init_processors()
        return data_processor.get_universities()


def clean_course_name(course_name: str) -> str:
    """
    Clean course name for database lookups by removing emoji markers and metadata.

    Example: "✅ Economics (BA, 3 years)" -> "Economics"
    """
    import re
    # Remove emoji markers
    clean = course_name.replace('✅ ', '').replace('📋 ', '')
    # Remove metadata suffix like "(BA, 3 years)" or "(MSc, 1 years)"
    clean = re.sub(r'\s*\([^)]*\)\s*$', '', clean).strip()
    return clean


def infer_degree_type(subject_area: str, level: str, duration: int) -> str:
    """
    Infer degree type (BA, BSc, BEng, MEng, MSci, MA, MSc, MBA, PhD)
    based on subject area, level, and duration.

    Args:
        subject_area: CAH Level 1 subject classification (e.g., "Engineering and technology")
        level: Course level (e.g., "Undergraduate", "Postgraduate taught")
        duration: Duration in years

    Returns:
        Degree type abbreviation (e.g., "BSc", "MEng", "MA")
    """
    if not subject_area or not level:
        return ''

    subject_lower = subject_area.lower()

    # Undergraduate degrees
    if 'undergraduate' in level.lower():
        # 4-year integrated master's degrees
        if duration == 4:
            if any(word in subject_lower for word in ['engineering', 'technology', 'computer']):
                return 'MEng'
            elif any(word in subject_lower for word in ['science', 'mathematical', 'physical']):
                return 'MSci'
            else:
                return 'BA/BSc'  # Could be either

        # Standard 3-year bachelor's degrees
        elif duration == 3:
            # Science/Tech subjects → BSc
            if any(word in subject_lower for word in [
                'science', 'engineering', 'technology', 'computer',
                'mathematical', 'physical', 'biological', 'medicine', 'health'
            ]):
                return 'BSc'
            # Arts/Humanities/Social Sciences → BA
            elif any(word in subject_lower for word in [
                'arts', 'humanities', 'social', 'business', 'law', 'education',
                'language', 'history', 'philosophy', 'creative'
            ]):
                return 'BA'
            else:
                return 'BA/BSc'  # Ambiguous

        # 5-6 year medical/vet degrees
        elif duration >= 5:
            if 'medicine' in subject_lower or 'veterinary' in subject_lower:
                return 'MBBS'
            else:
                return 'BSc'

        else:
            return 'BA/BSc'

    # Postgraduate taught (Master's)
    elif 'postgraduate taught' in level.lower():
        if 'business' in subject_lower:
            return 'MBA'
        elif any(word in subject_lower for word in [
            'science', 'engineering', 'technology', 'computer', 'mathematical'
        ]):
            return 'MSc'
        elif any(word in subject_lower for word in [
            'arts', 'humanities', 'social', 'education', 'law'
        ]):
            return 'MA'
        else:
            return 'MSc/MA'  # Ambiguous

    # Postgraduate research (PhD)
    elif 'postgraduate research' in level.lower():
        return 'PhD'

    return ''


def simplify_course_name(course_name: str) -> str:
    """
    Simplify course names by removing common variants for cleaner display.
    Removes: Foundation Year, Year Abroad, Industrial Placement, Sandwich, etc.
    """
    # Remove emoji markers first
    base_name = course_name.replace('✅ ', '').replace('📋 ', '')

    # Common suffixes to remove (case-insensitive)
    suffixes_to_remove = [
        ' with a Foundation Year',
        ' with Foundation Year',
        ' with a Year Abroad',
        ' with Year Abroad',
        ' with Industrial Placement',
        ' with Placement Year',
        ' (with Foundation Year)',
        ' (with Year Abroad)',
        ' (with Industrial Placement)',
        ' (with Placement)',
        ' with Professional Experience',
        ' (Sandwich)',
        ' - Sandwich',
        ' (4 years)',
        ' (3 years)',
        ' - 4 years',
        ' - 3 years'
    ]

    simplified = base_name
    for suffix in suffixes_to_remove:
        if simplified.endswith(suffix):
            simplified = simplified[:-len(suffix)]

    return simplified.strip()


@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_courses(university: str):
    """Get deduplicated courses for a specific university from HESA + fee data"""
    from modules.data.course_catalog import CourseCatalog

    try:
        catalog = CourseCatalog()
        data_processor, calculator = init_processors()

        # Get UKPRN from university name
        ukprn = catalog.get_ukprn_by_name(university)

        if ukprn is None:
            # Fallback to original method
            return data_processor.get_courses(university)

        # Get courses with fee data
        fee_courses = set(data_processor.get_courses(university))

        # Get all HESA courses
        hesa_courses = catalog.get_university_courses(ukprn)

        # Build course dictionary: simplified_name -> (marker, original_name, priority)
        course_dict = {}

        # Priority system: with_fee=100, full_time=10, shorter_duration=5
        def calculate_priority(row=None, has_fee=False):
            priority = 0
            if has_fee:
                priority += 100
            if row is not None:
                # Prefer full-time over part-time
                if row.get('mode') == 'Full-time':
                    priority += 10
                # Prefer shorter durations (3-year over 4-year)
                duration = row.get('duration_years', 3)
                if duration == 3:
                    priority += 5
            return priority

        # Add fee courses (high priority)
        for course in fee_courses:
            simplified = simplify_course_name(course)
            priority = calculate_priority(has_fee=True)

            # Only add if not exists or has higher priority
            if simplified not in course_dict or priority > course_dict[simplified][2]:
                course_dict[simplified] = ('✅', course, priority)

        # Add HESA courses (lower priority)
        for _, row in hesa_courses.iterrows():
            original_name = row['title']
            simplified = simplify_course_name(original_name)

            # Skip if already in fee courses
            if simplified in fee_courses:
                continue

            priority = calculate_priority(row=row, has_fee=False)

            # Only add if not exists or has higher priority
            if simplified not in course_dict or priority > course_dict[simplified][2]:
                course_dict[simplified] = ('📋', original_name, priority, row)

        # Build final list with metadata: "marker simplified_name (level, duration)"
        all_courses = []
        for simplified, data in sorted(course_dict.items()):
            marker = data[0]
            original = data[1]
            priority = data[2]
            row = data[3] if len(data) > 3 else None

            # Add metadata if available from HESA
            if row is not None:
                level = row.get('level', '')
                duration = row.get('duration_years', '')
                cah_category = row.get('cah_l1_name', '')  # Top-level subject area

                # Infer degree type based on subject + level + duration
                degree_type = infer_degree_type(cah_category, level, duration)

                # Format: "Economics (BA, 3 years)" or "Engineering (MEng, 4 years)"
                if degree_type and duration:
                    display_name = f"{marker} {simplified} ({degree_type}, {duration} years)"
                elif degree_type:
                    display_name = f"{marker} {simplified} ({degree_type})"
                else:
                    display_name = f"{marker} {simplified}"
            else:
                # Fee courses without HESA data (Cambridge/Oxford/LSE)
                display_name = f"{marker} {simplified}"

            all_courses.append(display_name)

        return all_courses

    except Exception as e:
        # Fallback to original method
        st.warning(f"Could not load HESA courses: {e}")
        data_processor, calculator = init_processors()
        return data_processor.get_courses(university)


def project_fee(university: str, course: str, year: int):
    """Project fee for a specific year"""
    data_processor, calculator = init_processors()
    clean_course = clean_course_name(course)
    return data_processor.project_fee(university, clean_course, year)


def project_fx_rate(year: int):
    """Project exchange rate for a specific year"""
    data_processor, calculator = init_processors()
    return data_processor.project_fx_rate(year)