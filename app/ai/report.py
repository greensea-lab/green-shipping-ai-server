from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa


def _render_html(template_dir: str, template_name: str, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        enable_async=False,
    )
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)


def _save_pdf_from_html(html: str, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        pisa.CreatePDF(html, dest=f)
    return out_path


def generate_esg_report_pdf(
    scenarios: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    title: str = "ESG Report",
    language: str = "ko",
    reports_dir: str = "reports",
    templates_dir: str = "app/ai/templates",
    ei_results: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Render ESG report to PDF and return file path."""
    now = datetime.now()
    slug = title.lower().replace(" ", "-")[:40] or "esg-report"
    filename = f"ESG-{now.strftime('%Y%m%d-%H%M%S')}-{slug}.pdf"
    out_path = os.path.join(reports_dir, filename)

    context = {
        "title": title,
        "language": language,
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "scenarios": scenarios,
        "results": results,
        "ei_results": ei_results or [],
    }
    html = _render_html(templates_dir, "esg_report.html.j2", context)
    return _save_pdf_from_html(html, out_path)
