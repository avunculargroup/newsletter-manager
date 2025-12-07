"""MJML template renderer for newsletter drafts."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import get_settings
from ..logger import get_logger
from .image_service import ImageAsset
from .llm_service import NewsletterSection

logger = get_logger(__name__)


class TemplateRenderer:
    def __init__(self) -> None:
        self.settings = get_settings()
        template_dir = Path(self.settings.mjml_template_path).parent
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(enabled_extensions=("mjml", "html")),
        )

    def render(
        self,
        sections: List[NewsletterSection],
        hero: ImageAsset | None,
        metadata: Dict[str, str],
    ) -> Tuple[str, str]:
        template = self.env.get_template(Path(self.settings.mjml_template_path).name)
        mjml_markup = template.render(sections=sections, hero=hero, metadata=metadata)
        html = self._compile_mjml(mjml_markup)
        return mjml_markup, html

    def _compile_mjml(self, markup: str) -> str:
        executable = shutil.which("mjml")
        if not executable:
            logger.warning("mjml.compiler_missing", message="MJML CLI not found; returning raw MJML")
            return markup
        with NamedTemporaryFile("w+", suffix=".mjml", delete=False) as mjml_file:
            mjml_file.write(markup)
            mjml_file.flush()
            output = subprocess.run(
                [executable, mjml_file.name, "-s"],
                check=False,
                capture_output=True,
                text=True,
            )
        if output.returncode != 0:
            logger.error("mjml.compile_failed", stderr=output.stderr)
            raise RuntimeError("MJML compilation failed")
        return output.stdout


renderer = TemplateRenderer()
