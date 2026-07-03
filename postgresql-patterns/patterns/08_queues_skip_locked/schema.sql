-- Queues with SKIP LOCKED demo schema
-- A dead-simple jobs table that doubles as a reliable work queue.

DROP TABLE IF EXISTS jobs CASCADE;

CREATE TABLE jobs (
    id          BIGSERIAL   PRIMARY KEY,
    queue       TEXT        NOT NULL DEFAULT 'default',
    payload     JSONB       NOT NULL DEFAULT '{}',
    status      TEXT        NOT NULL DEFAULT 'pending',  -- pending | processing | done | failed
    attempts    INTEGER     NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    claimed_at  TIMESTAMPTZ,
    done_at     TIMESTAMPTZ
);

CREATE INDEX ON jobs (queue, status) WHERE status = 'pending';
