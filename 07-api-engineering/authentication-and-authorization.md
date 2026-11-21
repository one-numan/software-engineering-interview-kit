# API Authentication & Authorization Architectures

## Module Overview
This guide covers **Session-based vs Token-based Authentication**, **Role-Based Access Control (RBAC)**, and **Attribute-Based Access Control (ABAC)**.

---

## RBAC vs ABAC

| Dimension | Role-Based Access Control (RBAC) | Attribute-Based Access Control (ABAC) |
| :--- | :--- | :--- |
| **Logic** | Grants access based on user role (`Admin`, `Editor`, `Viewer`) | Evaluates dynamic boolean policy on subject, action, resource, and environment |
| **Granularity** | Coarse-grained | **Fine-grained** (e.g. *"Doctors can read records ONLY if assigned to the patient AND during hospital shift hours"*) |
| **Complexity** | Simple to model in relational DBs (`user_roles` table) | Requires specialized policy evaluation engines (e.g. Open Policy Agent - OPA) |
