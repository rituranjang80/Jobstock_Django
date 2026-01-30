# AI Coding & Project Structure Guidelines

This document defines strict rules for AI-generated code and project structure. **All instructions must be followed exactly.**

---

## 1. Generic T-Type Utility Functions
- **Always use or write reusable generic T-type functions** in:
  - `config/Message.json` (for message templates and responses)
  - `App/utils/common_utils.py` (for general utilities)
  - `App/utils/django_utils.py` (for Django-specific utilities)
- **Never hardcode response messages**. Always fetch from `config/Message.json`.

## 2. Schema & Validation
- **All schemas must include validation** for messages and data.
- **Message validation and maintenance** must use `config/Message.json`.

## 3. Django Project Patterns
- **Always follow Django best practices** for:
  - Routers (urls)
  - Service layer
  - Schema/serializers
  - Repository/data access
  - Models
  - Configurable, lazy-loading queries (see `config/constant.py`)
- **Constants** must be defined as enums in `config/constant.py`.

## 4. Database Access
- **Minimize database hits**:
  - Retrieve only required fields.
  - Combine queries where possible, but keep code readable.

## 5. File & Folder Usage
- **All rough or experimental work** must be placed in the `ruf-work/` folder.
- **All code and files must be Docker-compatible** (run in Docker containers).

## 6. Additional Rules
- **Never hardcode program constants**; always use enums from `config/constant.py`.
- **All new or reused code must be generic and reusable where possible.**
- **Strictly follow these rules for all AI-generated code and reviews.**

---

> **Note:** Any deviation from these rules is not allowed. All code, structure, and configuration must comply for maintainability, scalability, and team consistency.
