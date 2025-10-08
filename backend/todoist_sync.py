#!/usr/bin/env python3
"""
Todoist Synchronisierung
Lädt Uni-Abgaben aus Todoist-Projekt
"""
import requests
from datetime import datetime
from typing import List, Dict


class TodoistSync:
    """Synchronisiert Todoist-Projekt mit lokalem Cache"""

    def __init__(self, api_token: str, project_name: str = 'UNI', assignment_label: str = 'abgabe'):
        self.api_token = api_token
        self.project_name = project_name
        self.assignment_label = assignment_label
        self.base_url = 'https://api.todoist.com/rest/v2'
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.project_id = None
        self.sections = {}
        self.assignments = []

    def _get(self, endpoint: str) -> dict:
        """Führt GET-Request zur Todoist API aus"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _find_project(self) -> str:
        """Findet Projekt-ID anhand des Namens"""
        projects = self._get('projects')

        for project in projects:
            if project['name'].lower() == self.project_name.lower():
                return project['id']

        raise ValueError(f"Project '{self.project_name}' not found in Todoist")

    def _load_sections(self):
        """Lädt alle Sections (= Uni-Module) des Projekts"""
        sections = self._get(f'sections?project_id={self.project_id}')

        self.sections = {
            section['id']: {
                'id': section['id'],
                'name': section['name'],
                'order': section['order']
            }
            for section in sections
        }

        print(f"Loaded {len(self.sections)} sections (modules)")

    def _load_tasks(self) -> List[Dict]:
        """Lädt alle Tasks aus dem Projekt (optional mit Label-Filter)"""
        tasks = self._get(f'tasks?project_id={self.project_id}')

        assignments = []

        for task in tasks:
            # Optional: Nur Tasks mit dem Assignment-Label
            # Wenn assignment_label leer ist, alle Tasks nehmen
            if self.assignment_label:
                if self.assignment_label not in [label.lower() for label in task.get('labels', [])]:
                    continue

            # Section (Modul) auslesen
            section_id = task.get('section_id')
            module_name = self.sections.get(section_id, {}).get('name', 'Unbekannt')

            assignment = {
                'id': task['id'],
                'title': task['content'],
                'description': task.get('description', ''),
                'due_date': task.get('due', {}).get('date'),
                'module_id': section_id,
                'module_name': module_name,
                'priority': task.get('priority', 1),
                'completed': task.get('is_completed', False),
                'url': task.get('url', ''),
                'created_at': task.get('created_at'),
                'labels': task.get('labels', [])
            }

            assignments.append(assignment)

        # Sortiere nach Datum
        assignments.sort(key=lambda x: x.get('due_date') or '9999-99-99')

        print(f"Loaded {len(assignments)} assignments")
        return assignments

    def sync(self) -> List[Dict]:
        """Führt vollständige Synchronisation durch"""
        print(f"Syncing Todoist project: {self.project_name}")

        # Projekt finden
        self.project_id = self._find_project()
        print(f"Project ID: {self.project_id}")

        # Sections (Module) laden
        self._load_sections()

        # Tasks (Abgaben) laden
        self.assignments = self._load_tasks()

        return self.assignments

    def get_module_stats(self) -> List[Dict]:
        """Berechnet Statistiken pro Modul"""
        module_stats = {}

        for assignment in self.assignments:
            module_id = assignment.get('module_id')

            if module_id not in module_stats:
                module_stats[module_id] = {
                    'id': module_id,
                    'name': assignment.get('module_name', 'Unbekannt'),
                    'total': 0,
                    'completed': 0,
                    'upcoming': 0
                }

            stats = module_stats[module_id]
            stats['total'] += 1

            if assignment.get('completed'):
                stats['completed'] += 1
            else:
                stats['upcoming'] += 1

        # In Liste umwandeln und sortieren
        modules = list(module_stats.values())
        modules.sort(key=lambda x: x['name'])

        return modules

    def get_week_assignments(self) -> List[Dict]:
        """Gibt Abgaben der nächsten 7 Tage zurück"""
        from datetime import timedelta

        now = datetime.now()
        week_later = now + timedelta(days=7)

        week_assignments = [
            a for a in self.assignments
            if a.get('due_date') and
            not a.get('completed') and
            now <= datetime.fromisoformat(a['due_date']) <= week_later
        ]

        return week_assignments


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv('TODOIST_API_TOKEN')
    if not token:
        print("❌ TODOIST_API_TOKEN not set")
        exit(1)

    # Test sync
    sync = TodoistSync(token)
    assignments = sync.sync()

    print(f"\n✅ Sync completed!")
    print(f"Found {len(assignments)} assignments")

    if assignments:
        print("\nNext 3 assignments:")
        for a in assignments[:3]:
            print(f"  - {a['title']} ({a['module_name']}) - Due: {a['due_date']}")

    modules = sync.get_module_stats()
    print(f"\nModules: {len(modules)}")
    for m in modules:
        print(f"  - {m['name']}: {m['completed']}/{m['total']} completed")
