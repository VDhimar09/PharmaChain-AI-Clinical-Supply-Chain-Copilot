"""Ensures the full SQLAlchemy model registry is loaded before any test
runs, regardless of which test module pytest collects first or whether
the whole suite or a single file is run.

Individual model files reference related models by string
(e.g. `relationship("User")`) and rely on every model module having been
imported somewhere before mapper configuration runs - `app.main` already
imports the complete model set (see its own model imports), so importing
it here is the cheapest way to satisfy that for the whole test session.
It also performs the same `CREATE EXTENSION IF NOT EXISTS vector` +
`Base.metadata.create_all` schema bootstrap that a real app startup does.
"""

import app.main  # noqa: F401
