# Nalewka Project Refactoring Plan

This document outlines the plan for refactoring the `nalewka` project to improve its structure, maintainability, and alignment with current best practices.

---

### Phase 1: Foundational Improvements (Enhancing Code Quality and Consistency)

- [ ] **1. Introduce Code Formatting and Linting:**
    - [ ] Integrate `black` for automated code formatting.
    - [ ] Integrate `ruff` for linting to enforce a consistent style and catch potential errors.

- [ ] **2. Enhance Dependency Management:**
    - [ ] Migrate from `requirements.txt` to `poetry` or `pip-tools`.
    - [ ] Create a `pyproject.toml` file and a lock file.

- [ ] **3. Implement a Comprehensive Test Suite:**
    - [ ] Create a `tests/` directory.
    - [ ] Implement unit and integration tests for models, services, and routes using `pytest`.

---

### Phase 2: Code and Structure Refactoring (Improving Separation of Concerns)

- [ ] **4. Strengthen the Service Layer and Introduce a Repository Pattern:**
    - [ ] Move all business logic from routes to the service layer.
    - [ ] Create a `app/repositories` directory for all database interactions.

- [ ] **5. Improve Configuration Management:**
    - [ ] Refactor `config.py` to use `pydantic` for settings management.

- [ ] **6. Enforce Static Typing:**
    - [ ] Add type hints throughout the codebase.
    - [ ] Use `mypy` to enforce static typing.

---

### Phase 3: Advanced Improvements (Future-Proofing the Application)

- [ ] **7. Refactor to a REST API:**
    - [ ] Create a dedicated `/api` blueprint to expose the application's functionality as a RESTful API.

- [ ] **8. Centralize Error Handling:**
    - [ ] Implement custom exception classes and a centralized error handler for consistent JSON error responses.
