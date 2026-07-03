import re
import uuid


class DocumentChunker:
    """Splits long text into overlapping chunks so nothing important falls at a boundary."""

    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _sentences(self, text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    def chunk(self, text: str, source: str = "unknown") -> list[dict]:
        sentences = self._sentences(text)
        chunks, current, current_len = [], [], 0
        chunk_index = 0

        for sent in sentences:
            words = sent.split()
            if current_len + len(words) > self.chunk_size and current:
                chunk_text = " ".join(current)
                chunks.append({
                    "id": f"{source}::chunk::{chunk_index}",
                    "text": chunk_text,
                    "metadata": {"source": source, "chunk_index": chunk_index},
                })
                chunk_index += 1
                # keep overlap
                overlap_words: list[str] = []
                for s in reversed(current):
                    if len(overlap_words) >= self.overlap:
                        break
                    overlap_words = s.split() + overlap_words
                current = overlap_words
                current_len = len(current)
            current.extend(words)
            current_len += len(words)

        if current:
            chunks.append({
                "id": f"{source}::chunk::{chunk_index}",
                "text": " ".join(current),
                "metadata": {"source": source, "chunk_index": chunk_index},
            })

        return chunks

    def chunk_documents(self, documents: list[dict]) -> list[dict]:
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk(doc["text"], source=doc.get("id", str(uuid.uuid4()))))
        return all_chunks


    def stats(self, chunks: list[dict]) -> dict:
        sizes = [len(c["text"].split()) for c in chunks]
        return {
            "count": len(chunks),
            "avg_words": round(sum(sizes) / len(sizes), 1) if sizes else 0,
            "min_words": min(sizes, default=0),
            "max_words": max(sizes, default=0),
        }
