"""
Markdown-aware chunker — splits on headings first, then falls back to
the sentence-based chunker for each section. Good for README-style docs
and structured wikis.
"""
import re
from .chunker import DocumentChunker


class MarkdownChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self._base = DocumentChunker(chunk_size=chunk_size, overlap=overlap)

    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        """Return [(heading, body)] pairs."""
        pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
        positions = [(m.start(), m.group(2)) for m in pattern.finditer(text)]
        if not positions:
            return [("", text)]
        sections = []
        for i, (pos, heading) in enumerate(positions):
            end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
            body = text[pos:end].strip()
            sections.append((heading, body))
        return sections

    def chunk(self, text: str, source: str = "unknown") -> list[dict]:
        sections = self._split_sections(text)
        all_chunks = []
        for heading, body in sections:
            section_chunks = self._base.chunk(body, source=source)
            for c in section_chunks:
                c["metadata"]["heading"] = heading
            all_chunks.extend(section_chunks)
        return all_chunks
