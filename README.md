# Coderr Backend

Dies ist das Backend für das **Coderr-Projekt**, ein Django-basiertes System, das verschiedene APIs und Funktionen bereitstellt. Es wurde entwickelt, um eine robuste und skalierbare Grundlage für Webanwendungen zu bieten.

---

## 🚀 Features

- **Benutzerverwaltung**: Registrierung, Authentifizierung und Profilerstellung.
- **Angebotsverwaltung**: CRUD-Operationen für Angebote und Angebotsdetails.
- **Filter- und Suchfunktionen**: Unterstützung für Filterung, Suche und Sortierung von Angeboten.
- **Paginierung**: Paginierte API-Antworten für eine bessere Benutzererfahrung.
- **Sichere API**: Token-basierte Authentifizierung mit Django REST Framework.

---

## 🛠️ Voraussetzungen

Stelle sicher, dass die folgenden Tools installiert sind:

- **Python**: Version 3.12 oder höher
- **Django**: Version 5.1.1
- **SQLite**: Standardmäßig in Django enthalten (oder ein anderes Datenbanksystem deiner Wahl)

---

## 📦 Installation

1. **Repository klonen**:
   ```sh
   git clone <repository-url>
   cd coderr-backend

2. **Virtuele Umgebung erstelle und aktivieren**:

python3 -m venv venv source venv/bin/activate für Mac 

venv\Scripts\activate für Windows

3. **Abhängigkeiten installieren**:

pip3 install -r requirements.txt

4. **Datenbank migrieren**:

python3 manage.py migrate

5. **Superuser erstellen**:

python3 manage.py createsuperuser

6. **Entwicklungsserver starten**:

python3 manage.py runserver
