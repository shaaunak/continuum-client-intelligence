# 07 — Non-Functional Requirements

| NFR ID | Category | Requirement | Implementation |
| --- | --- | --- | --- |
| `NFR-001` | Performance | Dashboard API responses should complete in <500ms locally on 12,000 clients / ~48,000 cases. | Server-side SQL aggregation, composite PostgreSQL indexes, paginated tables. |
| `NFR-002` | Security | Prevent SQL injection and avoid exposing real PII. | Parameterized SQLAlchemy `text()` bindings; 100% synthetic identifiers (`C-000001`). |
| `NFR-003` | Analytical Rigor | Eliminate immortal-time bias and avoid claiming unproven causality. | Day-90 landmarking, right-censoring, Cox PH adjustment, mandatory caveat panels. |
| `NFR-004` | Reproducibility | Synthetic dataset must be deterministic across runs. | Fixed seed (`20270101`) with `numpy.random.default_rng`. |
| `NFR-005` | Accessibility | Responsive layout, semantic HTML, tabular numerals, and high-contrast light-mode palette. | Tailwind CSS responsive grids, `tabular-nums`, keyboard-accessible controls. |
