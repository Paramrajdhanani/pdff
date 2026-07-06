# PDF ↔ Word Converter Pro 🚀

A complete Flask web application featuring a futuristic, anti-gravity-inspired glassmorphic UI design. Translate documents weightlessly with animated backgrounds, real-time drag-and-drop actions, and customizable database logs.

---

## 🌌 Tech Stack

- **Backend**: Python Flask, SQLite, SQLAlchemy Database, Flask-Login, Flask-WTF (CSRF Protection)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphic styles), Bootstrap 5 Grid, Vanilla Javascript
- **Conversion Modules**: `pdf2docx` (PDF to Word) and `docx2pdf` (Word to PDF)

---

## ⚡ Main Features

1. **User Accounts & Session Registry**: Multi-user registration, secure password hashing using SHA256 PBKDF2 algorithm, and login sessions.
2. **Translation Terminal**: High-performance Drag & Drop file drop zone or file browser, with real-time neon upload tracking.
3. **Weightless UI Design**: Floating cards, neon gradients (purple/cyan/pink), dark space void grid layout, and canvas-animated micro-particle dust.
4. **Auto-Purge Retention Systems**: Keeps files isolated on the server, automatically deleting uploads/converted files older than 2 hours to conserve space and ensure privacy.
5. **Smart Fallback Engine**: If your host machine lacks conversion binaries (like MS Word, which is needed by `docx2pdf` on Windows), the app generates a simulated conversion file with metadata and diagnostic info, enabling you to test the complete dashboard, download, and log system without local COM exceptions.

---

## 🗃️ Project Architecture

```
project/
├── app.py              # Application factory bootstrap & database creation
├── config.py           # Settings for paths, upload file limits (16MB), and retention
├── requirements.txt    # Python package dependencies
├── models.py           # SQLite schemas (Users & ConversionHistory)
├── verify_app.py       # Automated testing harness
├── auth/
│   ├── __init__.py     # Authentication blueprint registration
│   └── routes.py       # Signup, login, logout controllers & WTForms
├── converter/
│   ├── __init__.py     # Converter blueprint registration
│   └── routes.py       # Upload handlers, conversion runners, downloads & clear actions
├── static/
│   ├── css/
│   │   └── style.css   # Neon glassmorphic dark mode rules & float animations
│   ├── js/
│   │   └── main.js     # Canvas particle float loops & AJAX upload progress bars
│   └── uploads/        # Directory containing temporary file uploads (gitignored/auto-purged)
├── templates/          # HTML templates extending base.html
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── converter.html
│   ├── history.html
│   └── success.html
└── README.md           # Deployment manual
```

---

## 🚀 Getting Started

Follow these steps to configure and run the Converter Pro terminal locally.

### 1. Initialize Virtual Environment (Recommended)

In your terminal or PowerShell within the project workspace, run:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Project Dependencies

Install the requirements:

```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests

To check for route stability, database schemas, and blueprint imports, execute the test script:

```bash
python verify_app.py
```

### 4. Launch Development Server

Start the application factory runner:

```bash
python app.py
```

Open your browser and navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

---

## 🔧 Database Details

The app creates an SQLite database in the `./instance/site.db` file automatically on start.
- **`users` Table**: Stores credentials. Passwords are encrypted before database insertion.
- **`conversion_history` Table**: Stores records of file transactions (original and target name, file size metrics, type of conversion, and success/failure statuses).
