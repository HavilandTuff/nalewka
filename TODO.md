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

- [ ] **7. Refactor to a REST API:**
    - [ ] Create a dedicated `/api` blueprint to expose the application's functionality as a RESTful API.

- [ ] **8. Centralize Error Handling:**
    - [ ] Implement custom exception classes and a centralized error handler for consistent JSON error responses.
