# Full-Text Search

PostgreSQL's built-in full-text search is genuinely good for most applications.
You get stemming, stop-word removal, ranking, and highlighted snippets — all without
adding a separate search service. For many apps it's all you need.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | `articles` table with a generated `tsvector` column |
| `seed.sql` | 6 articles on different database topics |
| `search.sql` | `@@ to_tsquery`, `plainto_tsquery`, and `phraseto_tsquery` examples |
| `ranking.sql` | `ts_rank`, `ts_rank_cd`, and `ts_headline` for relevance and snippets |

## How the pieces fit together

```
raw text → to_tsvector() → tsvector (indexed)
query    → to_tsquery()  → tsquery
tsvector @@ tsquery      → true/false (match)
ts_rank(tsvector, tsquery) → float (relevance score)
```

## Generated tsvector column — the right way to do it

Instead of calling `to_tsvector()` in every query, store it as a generated column:

```sql
search_vec TSVECTOR
    GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
    ) STORED
```

Postgres updates it automatically on every insert/update. Then add a GIN index:

```sql
CREATE INDEX idx_articles_search ON articles USING GIN (search_vec);
```

Now `WHERE search_vec @@ query` is index-accelerated — no maintenance required.

## Query building

| Function | Best for |
|----------|----------|
| `to_tsquery('english', 'index & search')` | Precise queries with boolean operators (`&`, `\|`, `!`) |
| `plainto_tsquery('english', 'index search')` | Plain text — words are AND'd automatically |
| `phraseto_tsquery('english', 'full text')` | Preserves word order / adjacency |
| `websearch_to_tsquery('english', 'index -old')` | Google-style: minus for NOT, quotes for phrases |

## Ranking and highlighting

```sql
-- Sort by relevance
ORDER BY ts_rank(search_vec, query) DESC

-- Show a short snippet with matched terms highlighted
ts_headline('english', body, query, 'MaxFragments=1, MaxWords=25')
```

## How to run

```bash
docker compose up -d
python runner/run.py 05_full_text_search
```

## Postgres 11+ tip

`websearch_to_tsquery` understands Google-style syntax: `-word` for NOT, `"phrase"` for exact match.
It never throws a syntax error, so it's safe to pass raw user input directly.

## Full-text search vs LIKE

| | Full-text search | LIKE / ILIKE |
|-|-----------------|-------------|
| Stemming | Yes (running → run) | No |
| Stop words | Yes (the, a, is stripped) | No |
| Indexable | GIN / GiST | Only prefix: `LIKE 'word
## Full-text search vs LIKE

|  | Full-text search | LIKE / ILIKE |
|--|-----------------|-------------|
| Stemming | Yes (running → run) | No |
| Stop words | Yes (the/a/is stripped) | No |
| Indexable | GIN / GiST | Only prefix patterns |
| Multi-word | Boolean operators | None built-in |
