"""Answer generation based on retrieval context."""

from __future__ import annotations

from time import perf_counter

from pigmeu_never_forget.domain.models import AnswerResult, ProjectContext, RetrievalHit
from pigmeu_never_forget.services.retrieval import RetrievalContext, RetrievalService


class AnswerService:
    """Assemble grounded answers from retrieved context."""

    def answer_from_question(
        self,
        project: ProjectContext,
        question: str,
        top_k: int,
        retrieval: RetrievalService,
    ) -> AnswerResult:
        """Run retrieval and compose an answer."""
        start = perf_counter()
        context = retrieval.build_context(project, question, top_k=top_k)
        answer = self.answer(project, question, context.hits, context_bundle=context)
        latency_ms = int((perf_counter() - start) * 1000)
        retrieval.save_query_result(
            project=project,
            query=question,
            rewritten_query=context.rewritten_query,
            response_summary=answer.answer_short,
            sources=answer.sources,
            latency_ms=latency_ms,
        )
        retrieval.save_api_call(
            project=project,
            provider="local",
            model=str(project.settings["project_settings"]["models"]["answer_model"]),
            operation="ask",
            duration_ms=latency_ms,
            success=True,
        )
        answer.usage["latency_ms"] = latency_ms
        answer.usage["context_tokens_est"] = self._estimate_context_tokens(context)
        return answer

    def answer(
        self,
        project: ProjectContext,
        question: str,
        context: list[RetrievalHit],
        *,
        context_bundle: RetrievalContext | None = None,
    ) -> AnswerResult:
        """Return a grounded answer result."""
        if not context:
            return AnswerResult(
                answer_short=(
                    "Nao encontrei evidencias suficientes no indice do projeto. "
                    "Tente sincronizar e perguntar com mais contexto."
                ),
                sources=[],
                needs_expansion=True,
                usage={"context_tokens_est": 0},
            )

        primary = context[0]
        prefix = context_bundle.summary_short[:240].strip() if context_bundle else ""
        facts = context_bundle.facts[:3] if context_bundle else []
        fact_text = " ".join(facts)
        body = primary.preview or ""
        answer_text = (
            f"{prefix} {fact_text} Evidencia principal: {body}".strip()
            if prefix or fact_text
            else f"Evidencia principal: {body}".strip()
        )
        sources = [
            {"doc_id": hit.doc_id, "chunk_id": hit.chunk_id, "path": hit.path}
            for hit in context
        ]
        return AnswerResult(
            answer_short=answer_text[:600],
            sources=sources,
            needs_expansion=len(context) > 5,
            usage={"sources_count": len(sources)},
        )

    def _estimate_context_tokens(self, context: RetrievalContext) -> int:
        parts = [
            context.query,
            context.rewritten_query,
            context.summary_short,
            "\n".join(context.facts),
            "\n".join(hit.preview or "" for hit in context.hits),
        ]
        return max(1, sum(len(part) for part in parts) // 4)
