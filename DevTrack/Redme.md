# DevTrack

A minimal backend API for tracking engineering issues, built with Django. Engineers file bugs, assign priorities, and track status, like a stripped-down GitHub Issues. Data is stored in two JSON files, with no database setup required.

## Project structure

```
devtrack/
├── manage.py
├── issues.json          # issue storage (created automatically)
├── reporters.json       # reporter storage (created automatically)
├── devtrack/
│   ├── settings.py
│   └── urls.py          # includes issues.urls under /api/
└── issues/
    ├── models.py        # OOP classes (BaseEntity, Reporter, Issue, ...)
    ├── views.py         # request handling and JSON file storage
    └── urls.py          # /reporters/ and /issues/ routes
```

## How to run

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd devtrack
   ```

2. **Create a virtual environment and install Django**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install django
   ```

3. **Start the server**
   ```bash
   python manage.py runserver
   ```

4. **Open Postman** and send requests to `http://127.0.0.1:8000/api/...`
   For POST requests, set the body to **raw → JSON** and add the header `Content-Type: application/json`.

`reporters.json` and `issues.json` are created in the project root (next to `manage.py`) on the first successful POST.

## Data model

**Reporter**: a person who files issues.

| Field | Description |
|-------|-------------|
| id | unique integer |
| name | full name |
| email | contact email |
| team | e.g. backend, frontend, devops |

**Issue**: a bug report or task filed by a Reporter.

| Field | Description |
|-------|-------------|
| id | unique integer |
| title | short summary |
| description | full details |
| status | `open`, `in_progress`, `resolved`, `closed` |
| priority | `low`, `medium`, `high`, `critical` |
| reporter_id | ID of the Reporter who filed the issue |
| created_at | timestamp, set automatically |

One Reporter can file many Issues (1:many). The link is stored as `reporter_id` inside the Issue.

## OOP design

- **`BaseEntity`** is an abstract base class (`ABC`) with an abstract `validate()` and a shared `to_dict()`.
- **`Reporter`** and **`Issue`** inherit from `BaseEntity` and implement `validate()`.
- **`CriticalIssue`** and **`LowPriorityIssue`** subclass `Issue` and override `describe()`. `POST /api/issues/` picks the right class from the `priority` field (`critical` → `CriticalIssue`, `low` → `LowPriorityIssue`, anything else → `Issue`) and returns `describe()` as `message`.

## Endpoints

### Reporters: `/api/reporters/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/reporters/` | Create a new reporter |
| GET | `/api/reporters/` | Get all reporters |
| GET | `/api/reporters/?id=1` | Get a single reporter by ID |

**POST example**
```json
{
  "id": 1,
  "name": "Aarav Sharma",
  "email": "aarav@devtrack.com",
  "team": "backend"
}
```

### Issues: `/api/issues/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/issues/` | Create a new issue |
| GET | `/api/issues/` | Get all issues |
| GET | `/api/issues/?id=1` | Get a single issue by ID |
| GET | `/api/issues/?status=open` | Get all issues with the given status |

**POST example**
```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

**201 Created**
```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1,
  "created_at": "2026-10-01 17:51:59.123456",
  "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

### Error responses

| Status | When | Example body |
|--------|------|--------------|
| 400 | Validation fails, missing field, invalid JSON, duplicate id, unknown `reporter_id` | `{"error": "Title cannot be empty"}` |
| 404 | No record matches the requested id | `{"error": "Issue not found"}` |
| 405 | Unsupported HTTP method | `{"error": "Only GET and POST methods are allowed"}` |

## Postman screenshots

> Replace these placeholders with your own screenshots (save them in `screenshots/`).

| Endpoint | Result | Screenshot |
|----------|--------|------------|
| POST `/api/reporters/` | 201 success | ![Create reporter](screenshots/post-reporter-201.png) |
| GET `/api/reporters/?id=99` | 404 failure | ![Reporter not found](screenshots/get-reporter-404.png) |
| POST `/api/issues/` | 201 success | ![Create issue](screenshots/post-issue-201.png) |
| POST `/api/issues/` (empty title) | 400 failure | ![Validation error](screenshots/post-issue-400.png) |
| GET `/api/issues/?status=open` | 200 success | ![Filter by status](screenshots/get-issues-status-200.png) |

## Design decision

**I kept the OOP classes as plain Python classes instead of Django ORM models.**
The brief stores data in JSON files, not a database, so Django models would add migrations and a database that nothing uses. They would also change the output shape: a `ForeignKey` serializes as `reporter` instead of `reporter_id`. With plain classes, `to_dict()` returns exactly the fields in the spec, and the classes can be tested without Django.

Validation lives on the objects (`validate()`), and the views only translate `ValueError` into a `400` response. This keeps `models.py` free of HTTP code and `views.py` free of business rules. The views also check that a `reporter_id` refers to an existing reporter and that ids are unique, so the 1:many link can't point at a missing record.