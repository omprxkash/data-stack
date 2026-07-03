-- Articles covering several topics so searches return varied results.

INSERT INTO articles (title, body, author, published) VALUES
  ('Getting started with PostgreSQL',
   'PostgreSQL is a powerful open-source relational database. It supports advanced SQL, full-text search, JSONB storage, and much more. Installing it locally takes about five minutes.',
   'omprxkash', '2024-01-10'),

  ('Understanding database indexes',
   'An index speeds up reads at the cost of slightly slower writes. B-tree indexes handle equality and range queries. GIN indexes are ideal for full-text search and JSONB containment. Choosing the right index type matters enormously for query performance.',
   'omprxkash', '2024-02-03'),

  ('Row-level security in multi-tenant apps',
   'Row-level security lets you enforce data isolation at the database layer rather than relying on application code. Each tenant sets a session variable and Postgres filters rows automatically using a policy you define once.',
   'omprxkash', '2024-03-15'),

  ('Partitioning large tables by date',
   'Declarative partitioning in Postgres lets you split a huge table into smaller child tables by range, list, or hash. The query planner prunes irrelevant partitions automatically, making scans on date-ranged data dramatically faster.',
   'omprxkash', '2024-04-22'),

  ('Building a reliable job queue with SKIP LOCKED',
   'You can use a plain Postgres table as a reliable work queue. The trick is SELECT ... FOR UPDATE SKIP LOCKED, which lets multiple workers claim rows atomically without blocking each other or producing duplicates.',
   'omprxkash', '2024-05-08'),

  ('Optimistic locking and concurrent updates',
   'Optimistic locking avoids holding locks during long operations. Each row carries a version counter. An update only succeeds if the version it read is still current — otherwise the application retries. This pattern works well when conflicts are rare.',
   'omprxkash', '2024-06-01');
