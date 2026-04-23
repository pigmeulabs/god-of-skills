"""Application bootstrap for the local-first RAG foundation."""

from pigmeu_never_forget.config.loader import load_workspace_settings
from pigmeu_never_forget.services.answering import AnswerService
from pigmeu_never_forget.services.indexing import IndexingService
from pigmeu_never_forget.services.jobs import JobService
from pigmeu_never_forget.services.memory import MemoryConsolidationService
from pigmeu_never_forget.services.project import ProjectService
from pigmeu_never_forget.services.retrieval import RetrievalService
from pigmeu_never_forget.services.workspace import WorkspaceService


def create_application(config_path: str | None = None) -> WorkspaceService:
    """Create the root workspace service from configuration."""
    settings = load_workspace_settings(config_path)
    job_service = JobService()
    project_service = ProjectService(job_service=job_service)
    indexing_service = IndexingService()
    retrieval_service = RetrievalService()
    answer_service = AnswerService()
    memory_service = MemoryConsolidationService()
    return WorkspaceService(
        settings=settings,
        project_service=project_service,
        indexing_service=indexing_service,
        retrieval_service=retrieval_service,
        answer_service=answer_service,
        memory_consolidation_service=memory_service,
    )
