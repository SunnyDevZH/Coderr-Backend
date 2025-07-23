# Coderr Backend

Dies ist das Backend für das **Coderr-Projekt**, ein Django-basiertes System, das verschiedene APIs und Funktionen bereitstellt. Es wurde entwickelt, um eine robuste und skalierbare Grundlage für Webanwendungen zu bieten.

---

## 🚀 Funktionen

- Benutzerverwaltung: Registrierung, Authentifizierung und Profilerstellung.
- Angebotsverwaltung: CRUD-Operationen für Angebote und Angebotsdetails.
- Filter- und Suchfunktionen: Unterstützung für Filterung, Suche und Sortierung von Angeboten.
- Paginierung: Paginierte API-Antworten für eine bessere Benutzererfahrung.
- Sichere API: Token-basierte Authentifizierung mit Django REST Framework.

---

## 🛠️ Technologie

- **Python**: Programmiersprache
- **Django**: Web-Framework
- **Django REST Framework**: API-Entwicklung
- **SQLite**: Datenbank
- **Auth Token**: Authentifizierung über Token-System 

---

## ⚙️ Installation

### 1. Repository klonen
```bash
git clone https://github.com/SunnyDevZH/Coderr-Backend
```
```bash
cd Backend
```
### 2. Virtuelle Umgebung anlegen & aktivieren
```bash
python3 -m venv env
```
```bash
source env/bin/activate
```
### 3. Abhängigkeiten installieren
```bash
pip3 install -r requirements.txt
```
### 4. Migrationen ausführen
```bash
python3 manage.py migrate
```
### 5. Entwicklungsserver starten
```bash
python3 manage.py runserver
```
### 6. Anwendung im Browser öffnen
```bash
http://localhost:8000/admin
```
### 7. Superuser anlegen
```bash
python3 manage.py createsuperuser
```


