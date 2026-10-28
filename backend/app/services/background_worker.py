import asyncio

from app.core.database import SessionLocal
from app.core.logging import logger
from app.services.review_orchestrator import ReviewOrchestrator


class BackgroundWorker:
    """
    Manages non-blocking asynchronous review tasks.
    In cloud or distributed deployments, this can also interface with a Redis queue.
    """

    @classmethod
    def schedule_review(
        cls,
        repo_full_name: str,
        pull_number: int,
        mode: str = "deterministic"
    ):
        async def _run_in_background():
            db = SessionLocal()
            try:
                await ReviewOrchestrator.run_review(
                    db=db,
                    repo_full_name=repo_full_name,
                    pull_number=pull_number,
                    mode=mode
                )
            except Exception as e:
                logger.error(f"Background review job failed for {repo_full_name}#{pull_number}: {e}")
            finally:
                db.close()

        asyncio.create_task(_run_in_background())
