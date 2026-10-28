-- Tables for the risk register and remediation actions.
-- Loaded into an in-memory SQLite database by grc/data.py.

CREATE TABLE risks (
    risk_id              TEXT PRIMARY KEY,
    title                TEXT NOT NULL,
    asset                TEXT,
    threat               TEXT,
    vulnerability        TEXT,
    existing_controls    TEXT,
    csf_function         TEXT,
    csf_refs             TEXT,
    iso_refs             TEXT,
    inherent_likelihood  INTEGER,
    inherent_impact      INTEGER,
    residual_likelihood  INTEGER,
    residual_impact      INTEGER,
    target_likelihood    INTEGER,
    target_impact        INTEGER,
    treatment            TEXT,
    owner                TEXT,
    status               TEXT,
    last_reviewed        TEXT,
    accepted_by          TEXT,
    accepted_on          TEXT
);

CREATE TABLE actions (
    action_id       TEXT PRIMARY KEY,
    risk_id         TEXT REFERENCES risks (risk_id),
    action          TEXT NOT NULL,
    owner           TEXT,
    due_date        TEXT,
    status          TEXT,
    completed_date  TEXT
);

-- Scores are likelihood x impact on a 5 x 5 matrix (1 to 25).
-- Bands: Low 1-4, Medium 5-9, High 10-16, Critical 20-25.
CREATE VIEW risk_scores AS
SELECT
    risk_id,
    title,
    owner,
    status,
    treatment,
    csf_function,
    residual_likelihood,
    residual_impact,
    inherent_likelihood * inherent_impact AS inherent_score,
    residual_likelihood * residual_impact AS residual_score,
    target_likelihood   * target_impact   AS target_score,
    CASE
        WHEN residual_likelihood * residual_impact >= 20 THEN 'Critical'
        WHEN residual_likelihood * residual_impact >= 10 THEN 'High'
        WHEN residual_likelihood * residual_impact >= 5  THEN 'Medium'
        ELSE 'Low'
    END AS residual_rating,
    last_reviewed
FROM risks;
