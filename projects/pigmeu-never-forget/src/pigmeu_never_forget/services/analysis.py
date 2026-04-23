"""Heuristic-first document analysis."""

from __future__ import annotations

import re

from pigmeu_never_forget.domain.models import AnalysisResult, SourceDocument


class AnalysisService:
    """Analyze normalized documents and suggest chunking strategy."""

    def analyze(self, document: SourceDocument) -> AnalysisResult:
        """Return a heuristic analysis result."""
        text = document.raw_text
        lower = text.lower()
        has_headings = bool(re.search(r"^\s{0,3}#{1,6}\s+", text, flags=re.MULTILINE))
        has_code = "```" in text or bool(re.search(r"\b(def|class|function|import)\b", lower))

        if has_code and document.path and document.path.endswith((".py", ".js", ".ts")):
            doc_type = "source_code"
            strategy = "by_code_block_then_size"
        elif has_headings:
            doc_type = "technical_doc"
            strategy = "by_heading_then_paragraph"
        else:
            doc_type = "plain_text"
            strategy = "by_paragraph_then_size"

        entities = self._extract_entities(text)
        return AnalysisResult(
            doc_type=doc_type,
            language="pt-BR",
            has_headings=has_headings,
            has_code=has_code,
            recommended_chunking=strategy,
            priority_sections=[],
            entities=entities,
        )

    def _extract_entities(self, text: str) -> list[str]:
        matches = re.findall(r"\b[A-Z]{2,}(?:[-_][A-Z0-9]+)?\b", text)
        unique: list[str] = []
        seen: set[str] = set()
        for value in matches:
            if value not in seen:
                unique.append(value)
                seen.add(value)
            if len(unique) >= 10:
                break
        return unique
