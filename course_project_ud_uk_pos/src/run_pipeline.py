from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_step(step_name: str, command: list[str], cwd: Path, trace: list[dict[str, str]]) -> None:
    started = datetime.now(timezone.utc).isoformat()
    completed = ""
    status = "ok"
    try:
        subprocess.run(command, cwd=str(cwd), check=True)
    except subprocess.CalledProcessError:
        status = "failed"
        completed = datetime.now(timezone.utc).isoformat()
        trace.append(
            {
                "step": step_name,
                "status": status,
                "started_at_utc": started,
                "completed_at_utc": completed,
                "command": " ".join(command),
            }
        )
        raise
    completed = datetime.now(timezone.utc).isoformat()
    trace.append(
        {
            "step": step_name,
            "status": status,
            "started_at_utc": started,
            "completed_at_utc": completed,
            "command": " ".join(command),
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run reproducible end-to-end pipeline with trace logging.")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--python-bin", type=str, default=sys.executable)
    parser.add_argument("--label-field", choices=("upos", "joint"), default="upos")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    trace: list[dict[str, str]] = []

    run_step("load_data", [args.python_bin, "-m", "src.load_data"], root, trace)
    run_step("preprocess", [args.python_bin, "-m", "src.preprocess"], root, trace)
    run_step("train_baselines", [args.python_bin, "-m", "src.train_baselines", "--label-field", args.label_field], root, trace)
    run_step("train_crf", [args.python_bin, "-m", "src.train_crf", "--label-field", args.label_field], root, trace)

    outputs_dir = root / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    trace_path = outputs_dir / f"pipeline_trace_{args.label_field}.json"
    trace_path.write_text(json.dumps({"trace": trace}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved trace: {trace_path}")


if __name__ == "__main__":
    main()

