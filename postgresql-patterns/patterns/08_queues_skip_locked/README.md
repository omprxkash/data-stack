# Queues with SKIP LOCKED

You don't always need Redis or RabbitMQ for a job queue. If your jobs table is reasonably
sized and you can tolerate at-least-once delivery, a Postgres table with `SKIP LOCKED`
gives you a reliable, transactional queue with no extra infrastructure.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | `jobs` table with status, payload, attempts, and timestamps |
| `enqueue.sql` | Inserts several jobs across two queues |
| `claim.sql` | Atomic claim pattern with `FOR UPDATE SKIP LOCKED`, plus marking done |

## The key query

```sql
WITH claimed AS (
    SELECT id
    FROM   jobs
    WHERE  queue  = 'email'
      AND  status = 'pending'
    ORDER  BY id           -- FIFO
    LIMIT  1
    FOR UPDATE SKIP LOCKED  -- the magic
)
UPDATE jobs
SET    status     = 'processing',
       attempts   = attempts + 1,
       claimed_at = now()
FROM   claimed
WHERE  jobs.id = claimed.id
RETURNING jobs.*;
```

### What `SKIP LOCKED` does

Without it, two workers trying to claim the same row would block each other.
With `SKIP LOCKED`, worker 2 simply skips any row that worker 1 already locked
and picks the next available one. No blocking. No duplicate claims.

### Why wrap it in a CTE?

The CTE `claimed` finds and locks the row; the outer `UPDATE` modifies it.
This is the standard atomic claim pattern — the whole thing runs as one statement.

## Reliability considerations

- **At-least-once delivery**: if your worker crashes before marking the job `done`, it stays `processing` forever. Add a reaper: `UPDATE jobs SET status = 'pending' WHERE status = 'processing' AND claimed_at < now() - interval '5 minutes'`.
- **Dead letters**: after N `attempts`, move jobs to a `failed` status and alert on them.
- **Throughput**: benchmarks suggest a single Postgres queue table handles thousands of jobs/second. For higher throughput, partition by `queue` name.

## How to run

```bash
docker compose up -d
python runner/run.py 08_queues_skip_locked
```

## Reaper query

```sql
-- Reset stuck processing jobs after 5 minutes
UPDATE jobs SET status = 'pending', claimed_at = NULL
WHERE status = 'processing' AND claimed_at < now() - interval '5 minutes';
```
