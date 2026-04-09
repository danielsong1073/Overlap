# Overlap

A REST API for discovering people who share your taste in books, movies, TV, and games.

Users build a personal shelf of media entries. Titles are matched using external IDs from
Open Library, OMDb, and RAWG — so "Dune" always means the same Dune. A suggested users
feature ranks other users by how many titles overlap with yours.

**Live API:** https://overlap-bcom.onrender.com/docs

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL + SQLAlchemy + Alembic
- **Auth:** JWT (python-jose) + Argon2 password hashing (pwdlib)
- **External APIs:** Open Library, OMDb, RAWG

---

## Prerequisites

- Python 3.11+
- PostgreSQL

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/overlap.git
cd overlap
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root**
```
DATABASE_URL=postgresql://localhost/overlap
SECRET_KEY=yoursecretkey
OMDB_API_KEY=youromdbkey
RAWG_API_KEY=yourawgkey
```

**5. Start the server**
```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Running Tests
```bash
pytest
```

Tests use an in-memory SQLite database and do not touch your local PostgreSQL instance.
This project uses GitHub Actions for CI/CD. On every push to main, the test suite runs automatically against an isolated enviornment, and the app deploys to Render only if all tests pass.

---

## API Overview

### Users
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/register` | No | Create an account |
| POST | `/users/login` | No | Log in, receive JWT |
| GET | `/users/me` | Yes | Get current user |
| GET | `/users/suggested` | Yes | Users ranked by overlapping titles |
| GET | `/users/{username}/shelf` | No | View a user's public shelf |

### Entries
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/entries/` | Yes | Add a title to your shelf |
| GET | `/entries/me` | Yes | Get your entries |
| PUT | `/entries/{entry_id}` | Yes | Update an entry |
| DELETE | `/entries/{entry_id}` | Yes | Delete an entry |
| GET | `/entries/{external_id}/users` | Yes | See who else has a title |

### Connections
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/connections/{username}/send` | Yes | Send a connection request |
| PUT | `/connections/{username}/accept` | Yes | Accept a request |
| PUT | `/connections/{username}/decline` | Yes | Decline a request |
| GET | `/connections/` | Yes | Get connections by status |
| DELETE | `/connections/{username}` | Yes | Remove a connection |

### Other
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |