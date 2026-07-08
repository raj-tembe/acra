"""Output formatting utilities for acra."""

from typing import Any, Dict


def format_research_report(result: Dict[str, Any], output_format: str = "citations") -> Dict[str, Any]:
    report = {
        "query": result.get("user_request"),
        "summary": result.get("research_summary", ""),
        "findings": result.get("research_data", []),
        "sources": result.get("research_sources", []),
        "status": result.get("research_status", "unknown"),
    }
    if output_format == "summary":
        report = {"query": report["query"], "summary": report["summary"]}
    elif output_format == "detailed":
        report["details"] = result
    return report
