# Code Darasa Backend

Code Darasa is an edtech platform for sharing programming tutorials and full video-based courses. This backend is built
using **FastAPI** and **PostgreSQL**, with **SQLAlchemy** for ORM and **Alembic** for migrations.

---

## Key Features

- **Course management:** Create, list, update, and delete courses
- **Category management:** Organize courses by category; set/change category during creation and editing
- **User authentication:** Register, login, and manage user profiles (JWT-based)
- **Comments & Ratings:** Users can comment on and rate courses; comments and ratings are editable
- **API versioning:** All endpoints are under `/api/v1/`
- **Input validation:** Strong validation with Pydantic
- **Rate limiting:** Prevent API abuse
- **Testing:** Isolated test database and automated test setup via Makefile
- **Clean, modular structure:** `app/api`, `crud`, `db`, `schemas`, and `core`
- **Ready for extension:** Auth, categories, file uploads, video streaming, etc.

---

## Tech Stack

- **FastAPI** (web framework)
- **PostgreSQL** (database)
- **SQLAlchemy** (ORM)
- **Alembic** (migrations)
- **Pydantic** (data validation)
- **pytest** (testing)
- **python-dotenv** (environment management)
- **Make** (automation)

---

## API Versioning

All endpoints are prefixed with `/api/v1/` for future-proof versioning.

---

## API Endpoints (Examples)

- `POST /api/v1/auth/register` – Register a new user
- `POST /api/v1/auth/login` – Login and get JWT token
- `GET /api/v1/users/me` – Get current user profile
- `PUT /api/v1/users/me` – Update user profile

- `POST /api/v1/categories/` – Create a category
- `GET /api/v1/categories/` – List categories

- `POST /api/v1/courses/` – Create a course (with title, description, YouTube URL, and category)
- `GET /api/v1/courses/` – List available courses with pagination and filtering
- `PUT /api/v1/courses/{course_id}` – Edit a course (including changing category)
- `DELETE /api/v1/courses/{course_id}` – Delete a course

- `POST /api/v1/courses/{course_id}/comments/` – Add a comment to a course
- `PUT /api/v1/comments/{comment_id}` – Edit a comment
- `DELETE /api/v1/comments/{comment_id}` – Delete a comment
- `GET /api/v1/courses/{course_id}/comments/` – List comments for a course

- `POST /api/v1/courses/{course_id}/ratings/` – Rate a course (1-5 stars)
- `PUT /api/v1/ratings/{rating_id}` – Edit a rating
- `DELETE /api/v1/ratings/{rating_id}` – Delete a rating
- `GET /api/v1/courses/{course_id}/ratings/` – List ratings for a course

---

## Environment Setup

1. **Clone the repo and install dependencies:**
    ```bash
    git clone <repo-url>
    cd CodeDarasaBackend
    pip install -r requirements.txt
    ```

2. **Configure environment variables:**
    - Copy `.env.example` to `.env` and set your `DATABASE_URL`, `TEST_DATABASE_URL`, and `SECRET_KEY`.

3. **Initialize the database:**
    ```bash
    python -m app.init_db
    ```

4. **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

5. **Run with make (automates steps 3 & 4):**
    ```
    make run
    ```

---

## Testing

- **Test DB is isolated from dev/prod DBs.**
- Use the Makefile to initialize the test DB and run tests:
    ```bash
    make test
    ```

---

## Project Structure

```
app/
  api/         # API routers
  crud/        # CRUD logic
  db/          # DB models, session, migrations
  schemas/     # Pydantic schemas
  core/        # Core settings, security, etc.
tests/         # Test suite
Makefile       # Automation commands
.env           # Environment variables
```

---

## Notes

- All course data, comments, and ratings are stored in PostgreSQL.
- The backend is ready to power a frontend web app and mobile clients.
- Video streaming and advanced features are planned for future releases.
