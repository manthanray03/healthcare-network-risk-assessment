-- Queries behind the key risk indicators (KRIs).
-- Each query starts with a "-- name:" line. :as_of is the report date (YYYY-MM-DD).
-- "Active" risks are the ones still being worked: status Open or In treatment.

-- name: active_by_rating
SELECT residual_rating, COUNT(*) AS risks
FROM risk_scores
WHERE status IN ('Open', 'In treatment')
GROUP BY residual_rating;

-- name: accepted_risks
SELECT risk_id, title, residual_score, residual_rating
FROM risk_scores
WHERE status = 'Accepted'
ORDER BY residual_score DESC;

-- name: top_risks
SELECT risk_id, title, owner, status, inherent_score, residual_score, target_score, residual_rating
FROM risk_scores
WHERE status IN ('Open', 'In treatment')
ORDER BY residual_score DESC, inherent_score DESC, risk_id
LIMIT 5;

-- name: heatmap
SELECT residual_likelihood AS likelihood, residual_impact AS impact, COUNT(*) AS risks
FROM risk_scores
WHERE status <> 'Closed'
GROUP BY residual_likelihood, residual_impact;

-- name: by_function
SELECT csf_function,
       COUNT(*) AS risks,
       ROUND(AVG(residual_score), 1) AS avg_residual
FROM risk_scores
WHERE status IN ('Open', 'In treatment')
GROUP BY csf_function
ORDER BY risks DESC, csf_function;

-- name: score_totals
SELECT SUM(inherent_score) AS inherent,
       SUM(residual_score) AS residual,
       SUM(target_score)   AS target
FROM risk_scores
WHERE status <> 'Closed';

-- name: overdue_actions
SELECT a.action_id, a.risk_id, r.title AS risk_title, a.action, a.owner, a.due_date, a.status,
       CAST(julianday(:as_of) - julianday(a.due_date) AS INTEGER) AS days_overdue
FROM actions a
JOIN risks r ON r.risk_id = a.risk_id
WHERE a.status <> 'Done' AND a.due_date < :as_of
ORDER BY days_overdue DESC, a.action_id;

-- name: due_soon_actions
SELECT a.action_id, a.risk_id, r.title AS risk_title, a.action, a.owner, a.due_date, a.status,
       CAST(julianday(a.due_date) - julianday(:as_of) AS INTEGER) AS days_left
FROM actions a
JOIN risks r ON r.risk_id = a.risk_id
WHERE a.status <> 'Done'
  AND a.due_date >= :as_of
  AND a.due_date <= date(:as_of, '+14 days')
ORDER BY a.due_date, a.action_id;

-- name: action_counts
SELECT COUNT(*) AS total,
       SUM(CASE WHEN status <> 'Done' THEN 1 ELSE 0 END) AS open_actions,
       SUM(CASE WHEN status = 'Done' THEN 1 ELSE 0 END) AS done,
       SUM(CASE WHEN status = 'Done' AND completed_date <= due_date THEN 1 ELSE 0 END) AS done_on_time
FROM actions;

-- name: stale_reviews
SELECT risk_id, title, owner, last_reviewed,
       CAST(julianday(:as_of) - julianday(last_reviewed) AS INTEGER) AS days_since_review
FROM risks
WHERE status <> 'Closed'
  AND last_reviewed < date(:as_of, '-90 days')
ORDER BY last_reviewed;

-- name: actions_by_owner
SELECT owner,
       SUM(CASE WHEN status <> 'Done' THEN 1 ELSE 0 END) AS open_actions,
       SUM(CASE WHEN status <> 'Done' AND due_date < :as_of THEN 1 ELSE 0 END) AS overdue
FROM actions
GROUP BY owner
HAVING open_actions > 0
ORDER BY overdue DESC, open_actions DESC, owner;
