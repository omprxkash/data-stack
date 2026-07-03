-- Claiming jobs with SKIP LOCKED
-- Two workers run this concurrently — each gets a different job, no duplicates.
-- Run after schema.sql and enqueue.sql.

-- Worker pattern: claim one job atomically.
-- SKIP LOCKED means: skip any row another transaction already locked.
-- This makes it safe to run many workers in parallel without coordination.

WITH claimed AS (
    SELECT id
    FROM   jobs
    WHERE  queue  = 'email'
      AND  status = 'pending'
    ORDER  BY id
    LIMIT  1
    FOR UPDATE SKIP LOCKED
)
UPDATE jobs
SET    status     = 'processing',
       attempts   = attempts + 1,
       claimed_at = now()
FROM   claimed
WHERE  jobs.id = claimed.id
RETURNING jobs.id, jobs.queue, jobs.payload, jobs.status;

-- Expected (first call):
--  id | queue | payload                                       | status
-- ----+-------+-----------------------------------------------+------------
--   1 | email | {"to": "alice@example.com", "subject": "..."} | processing

-- Running the same query again (simulating a second worker) picks job 2:
WITH claimed AS (
    SELECT id
    FROM   jobs
    WHERE  queue  = 'email'
      AND  status = 'pending'
    ORDER  BY id
    LIMIT  1
    FOR UPDATE SKIP LOCKED
)
UPDATE jobs
SET    status     = 'processing',
       attempts   = attempts + 1,
       claimed_at = now()
FROM   claimed
WHERE  jobs.id = claimed.id
RETURNING jobs.id, jobs.queue, jobs.payload, jobs.status;

-- Expected (second call):
--  id | queue | payload                                       | status
-- ----+-------+-----------------------------------------------+------------
--   2 | email | {"to": "bob@example.com", "subject": "..."}   | processing

-- Mark a job done
UPDATE jobs SET status = 'done', done_at = now() WHERE id = 1;

-- Full queue state
SELECT id, queue, status, attempts, claimed_at, done_at
FROM   jobs
ORDER  BY id;
