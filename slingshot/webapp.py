"""
Slingshot Web UI - Simple Flask web interface for stock scanning.

Run with: python webapp.py
Then open: http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify
import sys
from datetime import datetime
from slingshot.scoring_engine import ScoringEngine
from slingshot.theme_manager import ThemeManager

app = Flask(__name__)

# Initialize engines
engine = ScoringEngine()
theme_manager = ThemeManager()

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/themes')
def themes():
    """List all themes."""
    all_themes = theme_manager.list_themes()
    theme_data = []

    for theme in all_themes:
        info = theme_manager.get_theme_info(theme)
        theme_data.append(info)

    return render_template('themes.html', themes=theme_data)

@app.route('/theme/<theme_name>')
def theme_detail(theme_name):
    """View specific theme."""
    info = theme_manager.get_theme_info(theme_name)
    return render_template('theme_detail.html', theme=info)

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    """Scan stocks."""
    if request.method == 'GET':
        return render_template('scan.html')

    # POST - perform scan
    scan_type = request.form.get('scan_type', 'top')

    try:
        if scan_type == 'top':
            limit = int(request.form.get('limit', 10))
            result = engine.scan_popular(limit=limit)
        elif scan_type == 'theme':
            theme = request.form.get('theme', 'AI')
            limit = int(request.form.get('limit', 20))
            result = engine.scan_theme(theme, limit=limit)
        elif scan_type == 'tickers':
            tickers_str = request.form.get('tickers', '')
            tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
            result = engine.scan_tickers(tickers)
        else:
            return jsonify({'error': 'Invalid scan type'}), 400

        # Convert to dict for JSON
        scores_data = [s.to_dict() for s in result.scores[:20]]  # Limit to top 20
        candidates_data = [s.to_dict() for s in result.top_candidates]

        return render_template('scan_results.html',
                             timestamp=result.timestamp,
                             total_scanned=len(result.tickers_scanned),
                             scores=scores_data,
                             candidates=candidates_data)

    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/ticker/<symbol>')
def ticker_detail(symbol):
    """Deep dive on a ticker."""
    try:
        data = engine.deep_dive(symbol.upper())

        if 'error' in data:
            return render_template('error.html', error=data['error'])

        return render_template('ticker_detail.html', data=data)

    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/themes')
def api_themes():
    """API endpoint for themes."""
    all_themes = theme_manager.list_themes()
    return jsonify({'themes': all_themes})

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint for scanning."""
    data = request.get_json()
    scan_type = data.get('type', 'top')

    try:
        if scan_type == 'top':
            limit = data.get('limit', 10)
            result = engine.scan_popular(limit=limit)
        elif scan_type == 'theme':
            theme = data.get('theme', 'AI')
            limit = data.get('limit', 20)
            result = engine.scan_theme(theme, limit=limit)
        elif scan_type == 'tickers':
            tickers = data.get('tickers', [])
            result = engine.scan_tickers(tickers)
        else:
            return jsonify({'error': 'Invalid scan type'}), 400

        return jsonify({
            'timestamp': result.timestamp.isoformat(),
            'total_scanned': len(result.tickers_scanned),
            'scores': [s.to_dict() for s in result.scores],
            'candidates': [s.to_dict() for s in result.top_candidates]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🎯 Slingshot Stock Scanner - Web UI")
    print("=" * 60)
    print("\n📍 Starting server at http://localhost:5000")
    print("\n🌐 Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("\n⚠️  Press CTRL+C to stop the server\n")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
