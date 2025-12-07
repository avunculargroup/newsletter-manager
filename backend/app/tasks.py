from __future__ import annotations

from celery import shared_task

from .workflows.pipeline import pipeline


@shared_task(name="pipeline.generate_newsletter")
def generate_newsletter(topics: list[str], metadata: dict[str, str]) -> dict[str, object]:
    return pipeline.run(topics, metadata)
