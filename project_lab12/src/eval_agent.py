from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def load_test_cases(path: str | Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def compare_outputs(expected: Dict[str, Any], predicted: Dict[str, Any]) -> Dict[str, Any]:
    mismatches: List[str] = []
    for field, expected_value in expected.items():
        predicted_value = predicted.get(field)
        if predicted_value != expected_value:
            mismatches.append(field)
    matched = len(expected) - len(mismatches)
    if not mismatches:
        rating = "correct"
    elif matched >= 4:
        rating = "partly"
    else:
        rating = "wrong"
    return {
        "rating": rating,
        "semantic_ok": rating == "correct",
        "mismatches": mismatches,
        "matched_fields": matched,
    }


def summarize_case(
    case: Dict[str, Any],
    result: Dict[str, Any],
    tool_logs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    evaluation = compare_outputs(case["expected"], result["final_output"])
    tool_names = [record["tool_name"] for record in tool_logs]
    category = "showcase"
    fix = "No fix needed."
    if any(record.get("metadata", {}).get("unnecessary") for record in tool_logs):
        category = "unnecessary tool call"
        fix = "Tighten the validation heuristic so low-risk queue cases skip the validator."
    elif result.get("needs_manual_check"):
        category = "validator finds ambiguity or missing structure"
        fix = "Use a safer route or add a repair step for ambiguous or underspecified inputs."
    elif evaluation["rating"] == "wrong":
        category = "tool output not enough for final answer"
        fix = "Improve the extraction rules or add a second pass to normalize difficult fields."
    elif evaluation["rating"] == "partly":
        category = "partly correct tool-grounded answer"
        fix = "Use better post-processing so the agent consumes tool output more faithfully."
    elif len(tool_names) == 2 and "simple" in case.get("tags", []):
        category = "tool not called, although maybe optional"
        fix = "Document why the agent safely skipped validation on simple cases."

    return {
        "case_id": case["case_id"],
        "input": case["input"],
        "expected_behavior": case["expected_behavior"],
        "actual_tool_calls": tool_names,
        "final_answer": result["final_answer"],
        "error_category": category,
        "possible_fix": fix,
        "rating": evaluation["rating"],
        "mismatches": evaluation["mismatches"],
    }


def compute_metrics(
    cases: List[Dict[str, Any]],
    baseline_results: Dict[str, Dict[str, Any]],
    agent_results: Dict[str, Dict[str, Any]],
    logs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total_calls = len(logs)
    success_calls = sum(1 for record in logs if record.get("success"))
    tool_call_success_rate = success_calls / total_calls if total_calls else 0.0
    calls_per_task = Counter(record["task_id"] for record in logs)
    average_tool_calls_per_task = sum(calls_per_task.values()) / len(cases)
    unnecessary_tool_call_count = sum(1 for record in logs if record.get("metadata", {}).get("unnecessary"))

    useful_tool_tasks = 0
    tasks_both_tools = 0
    ignored_tool_output = 0
    route_contradictions = 0
    final_rating_counts = Counter()

    for case in cases:
        case_id = case["case_id"]
        baseline_eval = compare_outputs(case["expected"], baseline_results[case_id]["final_output"])
        agent_eval = compare_outputs(case["expected"], agent_results[case_id]["final_output"])
        final_rating_counts[agent_eval["rating"]] += 1
        if agent_eval["matched_fields"] > baseline_eval["matched_fields"]:
            useful_tool_tasks += 1
        used_tools = agent_results[case_id].get("used_tools", [])
        if "classify_issue_type" in used_tools and "extract_support_fields" in used_tools:
            tasks_both_tools += 1
        if agent_eval["rating"] != "correct" and agent_results[case_id].get("validation"):
            ignored_tool_output += 1
        if case["expected_route"] != agent_results[case_id]["route"]:
            route_contradictions += 1

    return {
        "tool_call_success_rate": round(tool_call_success_rate, 3),
        "average_tool_calls_per_task": round(average_tool_calls_per_task, 3),
        "tasks_with_useful_tool_use": useful_tool_tasks,
        "unnecessary_tool_call_count": unnecessary_tool_call_count,
        "final_answer_ratings": dict(final_rating_counts),
        "tool_error_rate": round(1 - tool_call_success_rate, 3) if total_calls else 0.0,
        "tasks_using_both_main_tools_rate": round(tasks_both_tools / len(cases), 3),
        "tool_output_ignored_rate": round(ignored_tool_output / len(cases), 3),
        "final_answer_contradicts_tool_output_rate": round(route_contradictions / len(cases), 3),
    }
