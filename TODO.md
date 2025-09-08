# Nalewka Project Refactoring Plan

This document outlines the plan for refactoring the `nalewka` project to improve its structure, maintainability, and alignment with current best practices.

---

### Phase 1: Foundational Improvements (Enhancing Code Quality and Consistency)

- [x] **1. Introduce Code Formatting and Linting:**
    - [x] Integrate `black` for automated code formatting.
    - [x] Integrate `ruff` for linting to enforce a consistent style and catch potential errors.

- [x] **2. Enhance Dependency Management:**
    - [x] Migrate from `requirements.txt` to `pip-tools`.
    - [x] Create a `pyproject.toml` file and a lock file.

- [x] **3. Implement a Comprehensive Test Suite:**
    - [x] Create a `tests/` directory.
    - [x] Implement unit and integration tests for models, services, and routes using `pytest`.

---

### Phase 2: Code and Structure Refactoring (Improving Separation of Concerns)

- [x] **4. Strengthen the Service Layer and Introduce a Repository Pattern:**
    - [x] Move all business logic from routes to the service layer.
    - [x] Create a `app/repositories` directory for all database interactions.

- [x] **5. Improve Configuration Management:**
    - [x] Refactor `config.py` to use `pydantic` for settings management.

- [x] **6. Enforce Static Typing:**
    - [x] Add type hints throughout the codebase.
    - [x] Use `mypy` to enforce static typing.

---

### Phase 3: Advanced Improvements (Future-Proofing the Application)

- [x] **7. Refactor to a REST API:**
    - [x] Create a dedicated `/api` blueprint to expose the application's functionality as a RESTful API.
    - **API Blueprint Implementation:**
        - [x] Create `app/api.py` with a new Flask Blueprint for API endpoints
        - [x] Register the API blueprint in `app/__init__.py`
        - [x] Implement versioned API endpoints (e.g., `/api/v1/`)
    - **Authentication & Authorization:**
        - [x] Implement token-based authentication for API access
        - [x] Create API key management for third-party integrations
        - [ ] Ensure proper permission checks for all API endpoints
    - **Core API Endpoints:**
        - [x] **Users API:**
            - [x] `GET /api/v1/users/me` - Get current user profile
            - [x] `PUT /api/v1/users/me` - Update current user profile
        - [x] **Liquors API:**
            - [x] `GET /api/v1/liquors` - List all liquors for current user
            - [x] `POST /api/v1/liquors` - Create a new liquor
            - [x] `GET /api/v1/liquors/<id>` - Get details of a specific liquor
            - [x] `PUT /api/v1/liquors/<id>` - Update a specific liquor
            - [x] `DELETE /api/v1/liquors/<id>` - Delete a specific liquor
        - [ ] **Ingredients API:**
            - [ ] `GET /api/v1/ingredients` - List all ingredients
            - [ ] `POST /api/v1/ingredients` - Create a new ingredient
            - [ ] `GET /api/v1/ingredients/<id>` - Get details of a specific ingredient
            - [ ] `PUT /api/v1/ingredients/<id>` - Update a specific ingredient
            - [ ] `DELETE /api/v1/ingredients/<id>` - Delete a specific ingredient
        - [ ] **Batches API:**
            - [ ] `GET /api/v1/liquors/<liquor_id>/batches` - List all batches for a liquor
            - [ ] `POST /api/v1/liquors/<liquor_id>/batches` - Create a new batch
            - [ ] `GET /api/v1/batches/<id>` - Get details of a specific batch
            - [ ] `PUT /api/v1/batches/<id>` - Update a specific batch
            - [ ] `DELETE /api/v1/batches/<id>` - Delete a specific batch
            - [ ] `PUT /api/v1/batches/<id>/bottles` - Update bottle information for a batch
        - [ ] **Batch Formulas API:**
            - [ ] `GET /api/v1/batches/<batch_id>/formulas` - List all formulas for a batch
            - [ ] `POST /api/v1/batches/<batch_id>/formulas` - Add a formula to a batch
            - [ ] `PUT /api/v1/formulas/<id>` - Update a specific formula
            - [ ] `DELETE /api/v1/formulas/<id>` - Delete a specific formula
    - **Response Standards:**
        - [ ] Implement consistent JSON response format for all API endpoints
        - [ ] Use appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
        - [ ] Add pagination for list endpoints
        - [ ] Implement proper error responses with detailed messages
    - **Documentation:**
        - [ ] Create API documentation using OpenAPI/Swagger
        - [ ] Add examples for all endpoints
        - [ ] Document authentication requirements

- [ ] **8. Centralize Error Handling:**
    - [ ] Implement custom exception classes and a centralized error handler for consistent JSON error responses.
