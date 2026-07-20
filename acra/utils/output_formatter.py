"""Output formatting utilities for acra."""

from typing import Any, Dict, List


def _message_text(msg: Any) -> str:
    """Pull plain text content out of a LangChain message object or dict."""
    content = getattr(msg, "content", None)
    if content is None and isinstance(msg, dict):
        content = msg.get("content")
    return str(content) if content else ""


def _activity_log(messages: List[Any]) -> List[str]:
    """Turn the raw messages list into a readable log, collapsing consecutive
    duplicate entries (e.g. the same retry error repeated several times)."""
    lines: List[str] = []
    last = None
    for msg in messages or []:
        text = _message_text(msg)
        if not text or text == last:
            continue
        lines.append(text)
        last = text
    return lines


def format_task_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a full OmniAgent graph state into what a user actually wants to
    see after `acra ask/build/fix/review/explain/run`: the answer, whether it
    succeeded, and a short trail of what happened -- not the raw internal
    state (message objects, retry counts, review dataclasses, etc.)."""
    if not isinstance(result, dict):
        return {"answer": str(result)}

    activity_log = _activity_log(result.get("messages", []))
    answer = (
        result.get("research_summary")
        or result.get("coding_explanation")
        or (activity_log[-1] if activity_log else None)
    )

    generated_files = sorted((result.get("generated_files") or {}).keys())

    summary: Dict[str, Any] = {}
    if result.get("user_request"):
        summary["request"] = result["user_request"]
    if answer:
        summary["answer"] = answer
    if result.get("workflow_status"):
        summary["status"] = result["workflow_status"]
    if result.get("quality_score") is not None:
        summary["quality_score"] = f"{result['quality_score']}/10"
    if result.get("execution_success") is False and result.get("error_message"):
        summary["execution_error"] = result["error_message"].strip()
    if generated_files:
        summary["generated_files"] = ", ".join(generated_files)
    if result.get("critic_summary"):
        summary["critic_summary"] = result["critic_summary"]
    if activity_log:
        summary["activity_log"] = activity_log

    # Nothing recognizable in this dict (e.g. a stub/test result) -- fall
    # back to showing it as-is rather than returning an empty panel.
    return summary or result


def _format_finding(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    topic = str(item.get("topic", "")).strip()
    finding = str(item.get("finding", "")).strip()
    if topic and finding:
        return f"{topic}: {finding}"
    return finding or topic or str(item)


def _format_source(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    title = str(item.get("title", "")).strip()
    source_type = str(item.get("source_type", "")).strip()
    relevance = item.get("relevance_score")
    url = str(item.get("url", "")).strip()

    label = f"{title} ({source_type})" if title and source_type else (title or source_type or "Source")
    if relevance is not None:
        label += f" \u2014 relevance {relevance}/10"
    return f"{label}\n  {url}" if url else label


def format_research_report(result: Dict[str, Any], output_format: str = "citations") -> Dict[str, Any]:
    """Shape a research graph result for display: the summary becomes the
    headline answer, and findings/sources (lists of dicts in the raw state)
    become readable bullet lines instead of raw Python dict reprs."""
    findings = [_format_finding(f) for f in (result.get("research_data") or [])]
    sources = [_format_source(s) for s in (result.get("research_sources") or [])]

    report: Dict[str, Any] = {
        "request": result.get("user_request"),
        "answer": result.get("research_summary", ""),
        "status": result.get("research_status", "unknown"),
    }
    if findings:
        report["findings"] = findings
    if sources:
        report["sources"] = sources

    if output_format == "summary":
        report = {"request": report["request"], "answer": report["answer"]}
    elif output_format == "detailed":
        report["details"] = result
    return report