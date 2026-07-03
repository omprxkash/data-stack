-- Enqueue a handful of jobs across two queues.
-- In real code this is a single parameterised INSERT from your application.

INSERT INTO jobs (queue, payload) VALUES
  ('email',   '{"to": "alice@example.com", "subject": "Welcome!"}'),
  ('email',   '{"to": "bob@example.com",   "subject": "Your receipt"}'),
  ('email',   '{"to": "carol@example.com", "subject": "Password reset"}'),
  ('reports', '{"report_id": 42, "format": "pdf"}'),
  ('reports', '{"report_id": 17, "format": "csv"}');

-- Verify the queue
SELECT id, queue, status, payload->>'subject' AS subject
FROM   jobs
ORDER  BY id;

-- Expected:
--  id | queue   | status  | subject
-- ----+---------+---------+------------------
--   1 | email   | pending | Welcome!
--   2 | email   | pending | Your receipt
--   3 | email   | pending | Password reset
--   4 | reports | pending | (null)
--   5 | reports | pending | (null)
