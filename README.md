# 📚 Reading Tracker API (FastAPI Backend)

A backend service for tracking books, reading progress, and user analytics.  
Built with **FastAPI**, **SQLAlchemy**, **JWT authentication**, and **Redis caching**.

---

## 🚀 Features

- **User Authentication**
  - Register and login
  - JWT access tokens
  - Secure password hashing (argon2)

- **Book Management**
  - Add, update, delete books
  - Store metadata (title, author, total pages)

- **Reading Progress**
  - Log daily reading entries
  - Track pages read per session

- **Analytics**
  - Total books
  - Total pages read
  - Total progress entries
  - Last reading date
  - Redis‑based caching for performance

- **Clean Architecture**
  - Routers
  - Services
  - Schemas
  - Database layer
  - Environment‑based configuration

---

## 🛠️ Tech Stack

- FastAPI  
- SQLAlchemy Core  
- Databases (async)  
- SQLite  
- Redis  
- Pydantic v2  
- Uvicorn  
- argon2‑cffi  
- python‑dotenv  

---

## 📁 Project Structure

```
reading_tracker/
│
├── app/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── redis_client.py
│   ├── create_tables.py
│   ├── routers/
│   └── services/
│
├── venv/
├── .env
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the **project root**:

```
DATABASE_URL=sqlite:///./reading.db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## ▶️ Running the App

### 1. Activate virtual environment

```
source venv/bin/activate
```

### 2. Start Redis (in another terminal)

```
redis-server
```

### 3. Run FastAPI

```
python3 -m uvicorn app.main:app --reload
```

### 4. Open API docs

```
http://127.0.0.1:8000/docs
```

---

## 📊 Example Analytics Response

```json
{
  "user_id": 1,
  "total_books": 3,
  "total_pages": 420,
  "total_progress_entries": 12,
  "last_read_date": "2025-02-10"
}
```

---

## 🧪 Creating Tables

If running for the first time:

```
python3 app/create_tables.py
```

---

## 🧹 .gitignore (recommended)

```
venv/
__pycache__/
*.db
.env
.DS_Store
```

---

## 📦 What to Upload to GitHub

### Upload:
- `app/` (all Python files)
- `requirements.txt`
- `.gitignore`
- `README.md`
- `create_tables.py` (if outside app)

### Do NOT upload:
- `venv/`
- `.env`
- `reading.db`
- `__pycache__/`
- `.DS_Store`

---

