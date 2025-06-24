# Webanwendung – Projektbeschreibung

Dieses Projekt ist eine Webanwendung, die in Python entwickelt wurde. Zur Verwaltung der Abhängigkeiten kann entweder Conda oder ein virtuelles `venv`-Umfeld verwendet werden.

## 📦 Voraussetzungen

- Python 3.8 oder höher
- venv oder Anaconda

---

## 🚀 Schnellstart

### Option A: Installation mit anaconda
#### 1. Conda-Umgebung erstellen

Im Projektverzeichnis:

```bash
conda env create -f environment.yml
```

#### 2. Umgebung aktivieren

```bash
conda activate webprogramming
```

---

### Option B: Installation mit venv und requirements.txt

Falls du kein Conda verwenden möchtest, kannst du stattdessen `venv` und `requirements.txt` nutzen:

#### 1. Virtuelle Umgebung erstellen

```bash
python -m venv venv
```

#### 2. Umgebung aktivieren

- **Windows (cmd):**
  ```cmd
  venv\Scripts\activate
  ```

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

#### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

---

### 4. Anwendung starten

```bash
python run.py
```

---

### 5. Zugriff auf die Anwendung

Nach dem Start erscheint im Terminal ein Link, in der Regel:

```
http://127.0.0.1:5000
```

Mit **Strg + Rechtsklick** kann der Link im Browser geöffnet werden.

---

### 6. Login
Es wurde ein Testaccount angelegt:

Login-Name: Controller <br>
Login-Passwort: like
