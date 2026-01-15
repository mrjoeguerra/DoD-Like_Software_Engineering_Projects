# DoD-Style Flask Portfolio Projects (Sanitized)

This bundle contains **two** Python + Flask projects designed to resemble common
work patterns in a DoD-like environment **without** copying or revealing any classified
details.

Projects:
1) `secure-mission-tasking-portal/` — RBAC + JWT + audit logging + hardening patterns
2) `secure-sensor-data-gateway/` — HMAC signed ingest + anti-replay + quarantine lanes

Unzip, run locally, then push each folder as its own GitHub repo (recommended).

---

## **Secure Mission Tasking Portal (DoD-Style, Sanitized)**

**Short Description (GitHub subtitle):**
A role-based, auditable mission tasking API demonstrating secure enterprise patterns used in defense environments.

**Full Repository Summary (README or About section):**

> This repository is a **sanitized portfolio replica** of a mission tasking and workflow system similar to those used in U.S. Department of Defense cyber and operations environments.
>
> It demonstrates how senior software engineers design **secure, accountable, and role-controlled platforms** where every action must be authenticated, authorized, and auditable.
>
> While the original systems I worked on were classified, this public implementation reproduces the **architecture, security patterns, and operational rigor** without exposing any sensitive logic, data, or workflows.

### What this project showcases

* JWT-based authentication with role-based access control (RBAC)
* Secure task lifecycle management (create, assign, update, close)
* Immutable audit logging with request correlation IDs
* API hardening (rate limiting, security headers, strict validation)
* Enterprise Flask architecture (blueprints, factories, CI, tests)

### What it demonstrates:

> I can build **secure, compliance-ready backend systems** where trust, traceability, and operational control are mandatory — exactly how production systems are built inside government and regulated enterprise environments.

---

## **Secure Sensor Data Gateway (DoD-Style, Sanitized)**

**Short Description (GitHub subtitle):**
A cryptographically secured ingestion API for high-integrity data pipelines with replay protection and quarantine lanes.

**Full Repository Summary (README or About section):**

> This repository is a **public-safe analog** of ingestion and gateway services used in defense and intelligence systems to receive high-value data from distributed sources.
>
> In classified environments, these systems are responsible for ensuring **data authenticity, integrity, and accountability** before any information is allowed into protected networks.
>
> This project recreates those same engineering patterns — including cryptographic signing, replay protection, policy enforcement, and audit trails — without revealing any classified details.

### What this project showcases

* API key + HMAC-signed message authentication
* Anti-replay controls (timestamp + nonce)
* Schema validation and policy-based authorization
* Accepted vs Quarantine data lanes
* Audit trails for ingest decisions
* Testable, CI-ready microservice design

### What it demonstrates:

> I can engineer **zero-trust, high-integrity data pipelines** where every inbound message must prove its identity, authenticity, and authorization before being trusted — the same standards used in defense, banking, and critical infrastructure.
