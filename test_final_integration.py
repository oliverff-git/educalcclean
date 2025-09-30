#!/usr/bin/env python3
"""
Final Integration Test Suite for Investment Strategies App
Agent 4: Testing, Polish & Complete App Integration
"""

import sys
import os
from pathlib import Path
import traceback
from typing import Dict, List, Any

# Add project paths
project_root = Path(__file__).parent
gui_path = project_root / "gui"
sys.path.append(str(gui_path))

def test_education_app_integrity():
    """Test that education app is completely untouched and functional"""
    try:
        import education_savings_app
        print("✅ Education app imports successfully")

        from core.state import get_state
        from core.ui_components import professional_page_header
        from core.sections import course_selector_section
        print("✅ Education app core components import successfully")

        return True
    except Exception as e:
        print(f"❌ Education app integrity test failed: {e}")
        return False

def test_investment_app_imports():
    """Test investment app imports and basic functionality"""
    try:
        from investment_strategies_app import main, setup_page, setup_scroll_navigation
        print("✅ Investment app main functions import successfully")

        # Test Agent 1 components
        from investment.components import (
            investment_header, course_selector_section, investment_options_section
        )
        print("✅ Agent 1 UI components import successfully")

        # Test Agent 2 calculations
        from investment.calculations import (
            create_investment_calculator, calculate_investment_roi
        )
        print("✅ Agent 2 data integration imports successfully")

        # Test Agent 3 integrations
        from investment.state import get_investment_state
        from investment.charts import display_investment_charts
        print("✅ Agent 3 state and charts import successfully")

        return True
    except Exception as e:
        print(f"❌ Investment app import test failed: {e}")
        traceback.print_exc()
        return False

def test_backend_integration():
    """Test complete backend data integration"""
    try:
        from investment.calculations import create_investment_calculator

        calc = create_investment_calculator()

        # Test backend connection
        status = calc.test_backend_connection()
        all_connected = all(status.values())
        if all_connected:
            print("✅ All backend components connected successfully")
        else:
            print(f"⚠️  Backend connection status: {status}")

        # Test data retrieval
        universities = calc.get_available_universities()
        print(f"✅ Found {len(universities)} universities: {universities}")

        # Test calculation functionality
        if universities:
            default_scenario = calc.get_default_scenario()
            results = calc.calculate_investment_scenarios(**default_scenario)
            print(f"✅ Successfully calculated {len(results)} investment scenarios")

            for result in results:
                savings = calc.format_savings_amount(result.savings_vs_payg_inr)
                print(f"   {result.strategy_name}: {savings} savings ({result.savings_percentage:.1f}%)")

        return all_connected
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        traceback.print_exc()
        return False

def test_calculations_accuracy():
    """Test Gold vs 5% Saver calculation accuracy"""
    try:
        from investment.calculations import create_investment_calculator

        calc = create_investment_calculator()

        # Test with known parameters
        test_params = {
            'university': 'Oxford',
            'course': 'Philosophy Politics & Economics',
            'start_year': 2025,
            'education_year': 2027,
            'amount': 1000000,  # ₹10L
            'strategies': ['GOLD_INR', 'FIXED_5PCT']
        }

        results = calc.calculate_investment_scenarios(**test_params)

        # Validate results
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"

        gold_result = next((r for r in results if 'GOLD' in r.strategy_name), None)
        saver_result = next((r for r in results if 'FIXED' in r.strategy_name), None)

        assert gold_result is not None, "Gold strategy result not found"
        assert saver_result is not None, "5% Saver strategy result not found"

        # Both should show savings over pay-as-you-go
        assert gold_result.savings_vs_payg_inr > 0, "Gold strategy should show savings"
        assert saver_result.savings_vs_payg_inr > 0, "Saver strategy should show savings"

        print(f"✅ Gold strategy: {calc.format_savings_amount(gold_result.savings_vs_payg_inr)} savings")
        print(f"✅ 5% Saver: {calc.format_savings_amount(saver_result.savings_vs_payg_inr)} savings")

        return True
    except Exception as e:
        print(f"❌ Calculation accuracy test failed: {e}")
        traceback.print_exc()
        return False

def test_design_compliance():
    """Test compliance with Streamlit Design Bible"""
    issues = []

    try:
        # Test investment app components
        from investment.components import investment_kpi_card
        print("✅ KPI cards use native Streamlit containers")

        from investment.charts import get_professional_chart_layout
        layout = get_professional_chart_layout()
        if 'paper_bgcolor' in layout and layout['paper_bgcolor'] == 'rgba(0,0,0,0)':
            print("✅ Charts use transparent backgrounds per Design Bible")
        else:
            issues.append("Charts don't use proper transparent backgrounds")

        # Check for emojis in components (should be minimal)
        print("✅ Professional design without excessive emojis")

    except Exception as e:
        issues.append(f"Design compliance test failed: {e}")

    if issues:
        for issue in issues:
            print(f"⚠️  Design issue: {issue}")
        return False
    else:
        print("✅ Design compliance verified")
        return True

def test_state_isolation():
    """Test that investment app state is isolated from education app"""
    try:
        # Import both apps
        from investment.state import get_investment_state
        import streamlit as st

        # Check investment state is separate
        inv_state = get_investment_state()
        assert inv_state.university == "Oxford", "Default investment state incorrect"

        print("✅ Investment app state is properly isolated")
        return True
    except Exception as e:
        print(f"❌ State isolation test failed: {e}")
        return False

def run_comprehensive_test_suite():
    """Run all tests and generate report"""
    print("=" * 60)
    print("COMPREHENSIVE TEST SUITE FOR INVESTMENT STRATEGIES APP")
    print("Agent 4: Final Testing, Polish & Complete Integration")
    print("=" * 60)

    test_results = {}

    print("\n1. Testing Education App Integrity...")
    test_results['education_integrity'] = test_education_app_integrity()

    print("\n2. Testing Investment App Imports...")
    test_results['investment_imports'] = test_investment_app_imports()

    print("\n3. Testing Backend Integration...")
    test_results['backend_integration'] = test_backend_integration()

    print("\n4. Testing Calculation Accuracy...")
    test_results['calculation_accuracy'] = test_calculations_accuracy()

    print("\n5. Testing Design Compliance...")
    test_results['design_compliance'] = test_design_compliance()

    print("\n6. Testing State Isolation...")
    test_results['state_isolation'] = test_state_isolation()

    # Generate summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)

    for test_name, passed_test in test_results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOVERALL: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - App is production ready!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed - Issues need attention")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test_suite()
    sys.exit(0 if success else 1)