"""
Example: Basic stock screening and analysis for wheel strategy

This example demonstrates how to:
1. Screen stocks for wheel strategy suitability
2. Analyze specific tickers for put selling opportunities
3. Compare opportunities across multiple stocks
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analyzer import WheelAnalyzer
from src.utils import setup_logging, format_currency, format_percentage


def main():
    # Setup logging
    setup_logging(log_level="INFO")
    print("=" * 70)
    print("Wheel Strategy Stock Analyzer - Example Usage")
    print("=" * 70)

    # Initialize analyzer
    analyzer = WheelAnalyzer()

    # Example 1: Screen popular stocks
    print("\n1. Screening popular stocks for wheel strategy...")
    print("-" * 70)

    screened = analyzer.screen_stocks()

    if not screened.empty:
        print(f"\nFound {len(screened)} candidates:")
        print(screened[['ticker', 'price', 'market_cap', 'options_volume', 'wheel_score']].head(10))
    else:
        print("No stocks passed screening criteria")

    # Example 2: Analyze specific ticker
    print("\n\n2. Analyzing AAPL for put selling opportunities...")
    print("-" * 70)

    try:
        aapl_analysis = analyzer.analyze_ticker('AAPL')
        put_opportunities = aapl_analysis.get_put_opportunities(
            delta_range=(0.20, 0.35),
            min_premium=1.00
        )

        if not put_opportunities.empty:
            print(f"\nCurrent AAPL price: {format_currency(aapl_analysis.current_price)}")
            print(f"Analyzing expiration: {aapl_analysis.expiration_date}")
            print("\nTop 5 Put Selling Opportunities:")
            print(put_opportunities[['strike', 'premium', 'return_pct', 'annualized_return', 'dte']].head())

            # Show detailed analysis for best opportunity
            best = put_opportunities.iloc[0]
            print("\n" + "=" * 70)
            print("Best Opportunity Details:")
            print("=" * 70)
            print(f"Strike Price: {format_currency(best['strike'])}")
            print(f"Premium: {format_currency(best['premium'])}")
            print(f"Return: {format_percentage(best['return_pct'])}")
            print(f"Annualized Return: {format_percentage(best['annualized_return'])}")
            print(f"Breakeven: {format_currency(best['breakeven'])}")
            print(f"Days to Expiration: {best['dte']}")
        else:
            print("No suitable put opportunities found")

    except Exception as e:
        print(f"Error analyzing AAPL: {e}")

    # Example 3: Compare multiple tickers
    print("\n\n3. Comparing opportunities across multiple tickers...")
    print("-" * 70)

    comparison_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMD']
    comparison = analyzer.compare_opportunities(
        comparison_tickers,
        strategy='put',
        target_dte=30
    )

    if not comparison.empty:
        print("\nPut Selling Comparison (30 DTE):")
        print(comparison)
    else:
        print("No opportunities found for comparison")

    # Example 4: Find best wheel candidates
    print("\n\n4. Finding best wheel strategy candidates...")
    print("-" * 70)

    best_candidates = analyzer.find_best_wheel_candidates(
        min_annual_return=15.0,
        max_results=5
    )

    if not best_candidates.empty:
        print("\nTop 5 Wheel Strategy Candidates:")
        print(best_candidates)
    else:
        print("No candidates meet the minimum return criteria")

    # Example 5: Covered call analysis
    print("\n\n5. Analyzing covered call opportunities for SPY...")
    print("-" * 70)

    try:
        spy_analysis = analyzer.analyze_ticker('SPY')
        call_opportunities = spy_analysis.get_call_opportunities(
            delta_range=(0.20, 0.35),
            min_premium=0.50
        )

        if not call_opportunities.empty:
            print(f"\nCurrent SPY price: {format_currency(spy_analysis.current_price)}")
            print("\nTop 5 Covered Call Opportunities:")
            print(call_opportunities[['strike', 'premium', 'total_return_pct', 'annualized_return', 'dte']].head())
        else:
            print("No suitable call opportunities found")

    except Exception as e:
        print(f"Error analyzing SPY: {e}")

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
