#!/usr/bin/env python3
"""
Flask Backend für MMM-UniAssignments
Synchronisiert Todoist-Projekt mit MagicMirror²
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from todoist_sync import TodoistSync
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Konfiguration
TODOIST_TOKEN = os.getenv('TODOIST_API_TOKEN', '')
PROJECT_NAME = os.getenv('TODOIST_PROJECT', 'UNI')
ASSIGNMENT_LABEL = os.getenv('ASSIGNMENT_LABEL', 'abgabe')
DATA_FILE = 'assignments.json'

# Todoist Sync initialisieren
todoist = TodoistSync(TODOIST_TOKEN, PROJECT_NAME, ASSIGNMENT_LABEL)


def load_cached_data():
    """Lädt gecachte Daten aus JSON-Datei"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading cached data: {e}")

    return {
        'assignments': [],
        'modules': [],
        'last_sync': None
    }


def save_cached_data(data):
    """Speichert Daten in JSON-Datei"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving cached data: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'MMM-UniAssignments Backend',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/assignments', methods=['GET'])
def get_all_assignments():
    """Gibt alle Abgaben zurück"""
    try:
        data = load_cached_data()
        return jsonify({
            'success': True,
            'assignments': data.get('assignments', []),
            'modules': data.get('modules', []),
            'last_sync': data.get('last_sync')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/assignments/week', methods=['GET'])
def get_week_assignments():
    """Gibt Abgaben der nächsten 7 Tage zurück"""
    try:
        data = load_cached_data()
        assignments = data.get('assignments', [])

        # Filter für nächste 7 Tage
        now = datetime.now()
        week_later = now + timedelta(days=7)

        week_assignments = [
            a for a in assignments
            if a.get('due_date') and
            now <= datetime.fromisoformat(a['due_date']) <= week_later
        ]

        # Sortiere nach Datum
        week_assignments.sort(key=lambda x: x.get('due_date', ''))

        return jsonify({
            'success': True,
            'assignments': week_assignments,
            'count': len(week_assignments),
            'last_sync': data.get('last_sync')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/assignments/module/<module_id>', methods=['GET'])
def get_module_assignments(module_id):
    """Gibt Abgaben eines spezifischen Moduls zurück"""
    try:
        data = load_cached_data()
        assignments = data.get('assignments', [])

        module_assignments = [
            a for a in assignments
            if a.get('module_id') == module_id
        ]

        return jsonify({
            'success': True,
            'module_id': module_id,
            'assignments': module_assignments,
            'count': len(module_assignments),
            'last_sync': data.get('last_sync')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sync', methods=['POST'])
def sync_todoist():
    """Synchronisiert mit Todoist und aktualisiert Cache"""
    try:
        if not TODOIST_TOKEN:
            return jsonify({
                'success': False,
                'error': 'TODOIST_API_TOKEN not configured'
            }), 500

        # Synchronisiere mit Todoist
        print("Starting Todoist sync...")
        assignments = todoist.sync()
        modules = todoist.get_module_stats()

        # Speichere in Cache
        data = {
            'assignments': assignments,
            'modules': modules,
            'last_sync': datetime.now().isoformat()
        }
        save_cached_data(data)

        print(f"Sync completed: {len(assignments)} assignments, {len(modules)} modules")

        return jsonify({
            'success': True,
            'assignments_count': len(assignments),
            'modules_count': len(modules),
            'last_sync': data['last_sync']
        })
    except Exception as e:
        print(f"Sync error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Gibt aktuelle Konfiguration zurück (ohne sensible Daten)"""
    return jsonify({
        'success': True,
        'config': {
            'project_name': PROJECT_NAME,
            'assignment_label': ASSIGNMENT_LABEL,
            'token_configured': bool(TODOIST_TOKEN)
        }
    })


if __name__ == '__main__':
    # Initiales Sync beim Start
    if TODOIST_TOKEN:
        print("Performing initial sync...")
        try:
            assignments = todoist.sync()
            modules = todoist.get_module_stats()
            save_cached_data({
                'assignments': assignments,
                'modules': modules,
                'last_sync': datetime.now().isoformat()
            })
            print(f"Initial sync completed: {len(assignments)} assignments")
        except Exception as e:
            print(f"Initial sync failed: {e}")
    else:
        print("⚠️  TODOIST_API_TOKEN not set. Please configure in .env file")

    # Server starten
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"\n🚀 Starting MMM-UniAssignments Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
