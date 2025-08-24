SYSTEM_PROMPT = (
    """
You are a maritime operations and ESG assistant. Always:
- Prioritize numeric results from the simulation tool over assumptions.
- Explain assumptions and limitations clearly.
- If citing regulations, only cite from provided knowledge base search results.
- If no sources found, say that additional documentation is required.
- Respond in the requested language strictly.
"""
).strip()


def build_user_prompt(language: str,
                      user_message: str,
                      metrics: dict | None,
                      citations: list[dict] | None) -> str:
    lang_line = f"Language: {language}"
    lines = [lang_line, "", "User question:", user_message, ""]
    if metrics:
        lines += [
            "Calculated metrics (if available):",
            f"- Fuel base/new (ton): {metrics.get('fc_base_ton')} / {metrics.get('fc_new_ton')}",
            f"- CO2 base/new (ton): {metrics.get('co2_base_ton')} / {metrics.get('co2_new_ton')}",
            f"- CO2 reduction (%): {metrics.get('co2_reduction_pct')}",
            f"- Time base/new (hours): {metrics.get('time_base_hours')} / {metrics.get('time_new_hours')}",
            f"- Time delta (hours / %): {metrics.get('time_delta_hours')} / {metrics.get('time_increase_pct')}",
            "",
        ]
    if citations:
        lines.append("Knowledge base citations (top hits):")
        for c in citations:
            lines.append(f"- {c.get('source')} :: {c.get('path')}")
        lines.append("")
    lines.append(
        "Provide a concise, well-structured answer that summarizes the scenario, "
        "quantifies CO2 savings and time impact, and references sources if present."
    )
    return "\n".join(lines)

