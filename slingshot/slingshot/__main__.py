"""
CLI interface for Slingshot stock scanner.
"""
import argparse
import json
from datetime import datetime

from .scoring_engine import ScoringEngine
from .theme_manager import ThemeManager


def print_score_table(scores, limit=None):
    """Print scores in a formatted table."""
    if not scores:
        print("No results found.")
        return

    if limit:
        scores = scores[:limit]

    # Header
    print("\n" + "="*120)
    print(f"{'Ticker':<8} {'Total':<8} {'Compress':<10} {'SmartMoney':<12} {'Theme':<8} {'Themes':<40} {'Status':<15}")
    print("="*120)

    # Rows
    for score in scores:
        status = "🎯 SLINGSHOT" if score.is_slingshot_candidate else ""
        themes_str = ", ".join(score.theme.themes[:3])  # Show first 3 themes
        if len(score.theme.themes) > 3:
            themes_str += "..."

        print(
            f"{score.ticker:<8} "
            f"{score.total_score:>6.1f}  "
            f"{score.compression.overall_compression_score:>8.1f}  "
            f"{score.smart_money.overall_smart_money_score:>10.1f}  "
            f"{score.theme.overall_theme_score:>6.1f}  "
            f"{themes_str:<40} "
            f"{status:<15}"
        )

    print("="*120 + "\n")


def print_deep_dive(data):
    """Print detailed analysis for a single ticker."""
    if 'error' in data:
        print(f"Error: {data['error']}")
        return

    score = data['score']
    info = data['info']
    breakdown = data['breakdown']
    context = data['context']

    print("\n" + "="*80)
    print(f"DEEP DIVE: {score['ticker']}")
    print("="*80)

    # Company info
    print(f"\n📊 Company: {info.get('name', score['ticker'])}")
    print(f"   Sector: {info.get('sector', 'Unknown')}")
    print(f"   Industry: {info.get('industry', 'Unknown')}")

    # Overall score
    print(f"\n🎯 Total Score: {score['total_score']:.1f}/100")
    if score['is_slingshot_candidate']:
        print("   ✅ SLINGSHOT CANDIDATE!")
    print(f"   Themes: {', '.join(score['themes'])}")

    # Compression breakdown
    comp = breakdown['compression']
    print(f"\n🔧 Compression: {comp['overall']:.1f}/100")
    print(f"   BB Squeeze: {comp['bb_squeeze']:.1f}")
    print(f"   ATR Compression: {comp['atr_compression']:.1f}")
    print(f"   Volume Dry-up: {comp['volume_dryup']:.1f}")
    print(f"   Price Range: {comp['price_range_compression']:.1f}")
    print(f"   Status: {'✅ COMPRESSED' if comp['is_compressed'] else '❌ Not compressed'}")

    # Smart money breakdown
    sm = breakdown['smart_money']
    print(f"\n💰 Smart Money: {sm['overall']:.1f}/100")
    print(f"   Institutional: {sm['institutional_buying']:.1f}")
    print(f"   Insider: {sm['insider_buying']:.1f}")
    print(f"   Options Flow: {sm['options_flow']:.1f}")
    print(f"   Status: {'✅ ACCUMULATING' if sm['is_accumulating'] else '❌ Not accumulating'}")

    # Theme breakdown
    th = breakdown['theme']
    print(f"\n📰 Theme/Narrative: {th['overall']:.1f}/100")
    print(f"   Narrative Score: {th['narrative_score']:.1f}")
    print(f"   Theme Momentum: {th['theme_momentum']:.1f}")
    print(f"   Status: {'✅ TRENDING' if th['is_trending'] else '❌ Not trending'}")

    # Recent news
    if context['recent_news']:
        print(f"\n📰 Recent News ({len(context['recent_news'])} articles):")
        for news in context['recent_news'][:5]:
            sentiment_icon = "🟢" if news['sentiment'] > 0.2 else "🔴" if news['sentiment'] < -0.2 else "⚪"
            print(f"   {sentiment_icon} [{news['source']}] {news['headline'][:80]}")

    print("\n" + "="*80 + "\n")


def cmd_scan(args):
    """Run a market scan."""
    engine = ScoringEngine()

    if args.tickers:
        # Scan specific tickers
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
        result = engine.scan_tickers(tickers)
    elif args.theme:
        # Scan theme
        result = engine.scan_theme(args.theme, limit=args.top)
    else:
        # Scan popular stocks
        result = engine.scan_popular(limit=args.top)

    print(f"\nScan completed at {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scanned {len(result.tickers_scanned)} tickers")

    if args.candidates_only:
        print_score_table(result.top_candidates)
    else:
        print_score_table(result.scores, limit=args.limit)

    # Save to file if requested
    if args.output:
        output_data = {
            'timestamp': result.timestamp.isoformat(),
            'tickers_scanned': result.tickers_scanned,
            'scores': [s.to_dict() for s in result.scores]
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to {args.output}")


def cmd_ticker(args):
    """Analyze a single ticker in depth."""
    engine = ScoringEngine()
    data = engine.deep_dive(args.ticker.upper())

    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print_deep_dive(data)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Analysis saved to {args.output}")


def cmd_themes(args):
    """List or analyze themes."""
    manager = ThemeManager()

    if args.theme:
        # Show specific theme
        info = manager.get_theme_info(args.theme)
        print(f"\n📁 Theme: {info['name']}")
        print(f"   Tickers: {info['ticker_count']}")
        print(f"   Members: {', '.join(info['tickers'][:20])}")
        if info['ticker_count'] > 20:
            print(f"   ... and {info['ticker_count'] - 20} more")
    else:
        # List all themes
        themes = manager.list_themes()
        print("\n📁 Available Themes:\n")
        for theme in themes:
            info = manager.get_theme_info(theme)
            print(f"   {theme:<20} ({info['ticker_count']} tickers)")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Slingshot - Stock Scanner for High-Probability Setups',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan top 10 popular stocks
  python -m slingshot scan --top 10

  # Scan specific tickers
  python -m slingshot scan --tickers NVDA,AMD,TSLA

  # Scan AI theme
  python -m slingshot scan --theme AI

  # Show only slingshot candidates
  python -m slingshot scan --top 50 --candidates-only

  # Deep dive on a single ticker
  python -m slingshot ticker NVDA

  # List all themes
  python -m slingshot themes

  # Show theme details
  python -m slingshot themes --theme AI
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan stocks')
    scan_parser.add_argument('--top', type=int, help='Number of popular stocks to scan')
    scan_parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    scan_parser.add_argument('--theme', type=str, help='Scan specific theme')
    scan_parser.add_argument('--limit', type=int, default=20, help='Max results to display')
    scan_parser.add_argument('--candidates-only', action='store_true',
                           help='Show only slingshot candidates')
    scan_parser.add_argument('--output', type=str, help='Save results to JSON file')
    scan_parser.set_defaults(func=cmd_scan)

    # Ticker command
    ticker_parser = subparsers.add_parser('ticker', help='Deep dive on a single ticker')
    ticker_parser.add_argument('ticker', type=str, help='Ticker symbol')
    ticker_parser.add_argument('--json', action='store_true', help='Output as JSON')
    ticker_parser.add_argument('--output', type=str, help='Save to file')
    ticker_parser.set_defaults(func=cmd_ticker)

    # Themes command
    themes_parser = subparsers.add_parser('themes', help='List or view themes')
    themes_parser.add_argument('--theme', type=str, help='View specific theme details')
    themes_parser.set_defaults(func=cmd_themes)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == '__main__':
    main()
