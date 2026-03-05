# 📝 Flask Notes App (With Authentication)

A simple and secure **Notes Management Web Application** built using **Flask** and **SQLite**, featuring **user authentication**, categories, tags, and pinning functionality.  
This project is suitable for beginners learning **Flask, SQLAlchemy, and authentication concepts**.

---

🔗 **Live Demo:** https://flask-notes-lmlw.onrender.com

A full-stack Flask Notes application with authentication, categories, tags, and pin functionality.


## 🚀 Features

### 🔐 Authentication
- User Registration
- User Login & Logout
- Secure password hashing
- Session-based authentication

### 🗒️ Notes
- Create, edit, and delete notes
- Pin / unpin important notes
- Add tags to notes
- View notes by category

### 📂 Categories & Tags
- Create custom categories
- Assign colors to categories
- Add multiple tags to notes

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Frontend:** HTML, CSS, Jinja2
- **Authentication:** Flask Sessions, Werkzeug Security

---

## 📁 Project Structure

```
Flask_Notes_app/
notes-app/
├── app.py 
├── templates/
│   ├── login.html
│   ├── register.html 
│   ├── base.html
│   ├── index.html
│   ├── create_note.html
│   ├── edit_note.html
│   ├── view_note.html
│   ├── categories.html
│   └── create_category.html
├── static/
│   └── css/
│       └── style.css
└── instance/
    └── notes.db
├── requirements.txt
└── README.md

```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```
git clone https://github.com/Mahii0107/flask-notes.git
cd flask-notes
```

2️⃣ Create a Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```

3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

4️⃣ Run the Application
```
python app.py
```

The app will run at:
http://127.0.0.1:5000/

## 🌍 Deployment

The application can be easily deployed on cloud platforms.

Supported platforms:

- 🚀 Render
- 🚂 Railway

Make sure the following files exist before deployment:

- `requirements.txt`
- `app.py`

📌 Future Enhancements

- 🔍 Search functionality  
- 🔑 Password reset system  
- 👤 User profile page  
- 🐘 PostgreSQL database integration  
- 🌐 REST API version

