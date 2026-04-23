"""Chunking service for normalized documents."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from pigmeu_never_forget.domain.models import ChunkRecord, ProjectContext


@dataclass(slots=True)
class ChunkingConfig:
    """Effective chunking configuration."""

    chunk_size_chars: int
    overlap_chars: int
    min_chunk_chars: int


class ChunkingService:
    """Build retrieval chunks using heading- and paragraph-aware splitting."""

    def chunk_document(
        self,
        project: ProjectContext,
        doc_id: str,
        path: str,
        text: str,
        section_hint: str | None = None,
    ) -> list[ChunkRecord]:
        """Chunk a normalized document text into stable records."""
        config = self._resolve_config(project)
        sections = self._split_by_heading(text)
        chunks: list[ChunkRecord] = []
        position = 0
        for section_name, section_text in sections:
            paragraphs = self._split_paragraphs(section_text)
            for piece in self._build_windowed_chunks(paragraphs, config):
                if len(piece.strip()) < config.min_chunk_chars:
                    continue
                chunk_hash = hashlib.sha256(
                    f"{doc_id}|{position}|{section_name}|{piece}".encode("utf-8")
                ).hexdigest()
                chunk_id = f"{doc_id}__{position}__{chunk_hash[:12]}"
                chunks.append(
                    ChunkRecord(
                        chunk_id=chunk_id,
                        doc_id=doc_id,
                        text=piece,
                        position=position,
                        section=section_name or section_hint,
                        token_count=self._estimate_tokens(piece),
                        metadata={"source_path": path, "chunk_hash": chunk_hash},
                    )
                )
                position += 1
        if not chunks and text.strip():
            chunk_hash = hashlib.sha256(f"{doc_id}|0|{text}".encode("utf-8")).hexdigest()
            chunks.append(
                ChunkRecord(
                    chunk_id=f"{doc_id}__0__{chunk_hash[:12]}",
                    doc_id=doc_id,
                    text=text.strip(),
                    position=0,
                    section=section_hint,
                    token_count=self._estimate_tokens(text),
                    metadata={"source_path": path, "chunk_hash": chunk_hash},
                )
            )
        return chunks

    def _resolve_config(self, project: ProjectContext) -> ChunkingConfig:
        workspace_chunking = project.settings.get("chunking", {})
        project_chunking = project.settings["project_settings"].get("chunking", {})
        chunk_size = int(project_chunking.get("chunk_size_chars", workspace_chunking.get("chunk_size_chars", 1200)))
        overlap = int(project_chunking.get("overlap_chars", workspace_chunking.get("overlap_chars", 180)))
        min_chunk = int(workspace_chunking.get("min_chunk_chars", 300))
        return ChunkingConfig(
            chunk_size_chars=max(256, chunk_size),
            overlap_chars=max(0, min(overlap, chunk_size // 2)),
            min_chunk_chars=max(64, min_chunk),
        )

    def _split_by_heading(self, text: str) -> list[tuple[str | None, str]]:
        lines = text.splitlines()
        sections: list[tuple[str | None, str]] = []
        current_heading: str | None = None
        current_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                if current_lines:
                    sections.append((current_heading, "\n".join(current_lines).strip()))
                    current_lines = []
                current_heading = stripped.lstrip("#").strip() or None
            else:
                current_lines.append(line)
        if current_lines or not sections:
            sections.append((current_heading, "\n".join(current_lines).strip()))
        return sections

    def _split_paragraphs(self, text: str) -> list[str]:
        if not text.strip():
            return []
        return [part.strip() for part in text.split("\n\n") if part.strip()]

    def _build_windowed_chunks(self, paragraphs: list[str], config: ChunkingConfig) -> list[str]:
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= config.chunk_size_chars:
                current = candidate
                continue
            if current:
                chunks.append(current)
                current = self._with_overlap(current, paragraph, config.overlap_chars)
            else:
                chunks.extend(self._split_large_paragraph(paragraph, config))
                current = ""
        if current:
            chunks.append(current)
        return chunks

    def _split_large_paragraph(self, paragraph: str, config: ChunkingConfig) -> list[str]:
        result: list[str] = []
        step = max(1, config.chunk_size_chars - config.overlap_chars)
        start = 0
        while start < len(paragraph):
            result.append(paragraph[start : start + config.chunk_size_chars].strip())
            start += step
        return [item for item in result if item]

    def _with_overlap(self, previous_chunk: str, paragraph: str, overlap_chars: int) -> str:
        if overlap_chars <= 0:
            return paragraph
        tail = previous_chunk[-overlap_chars:]
        return f"{tail}\n\n{paragraph}".strip()

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
