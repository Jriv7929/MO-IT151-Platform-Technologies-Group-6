from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
PIPELINE_RUNNER = PROJECT_ROOT / "run_pipeline.py"
DASHBOARD_APP = PROJECT_ROOT / "dashboard" / "app.py"


def run_complete_pipeline() -> bool:
    """
    Executes run_pipeline.py using the same Python interpreter
    currently running main.py.
    """

    if not PIPELINE_RUNNER.exists():
        print(
            "ERROR: run_pipeline.py was not found."
        )
        print(f"Expected location: {PIPELINE_RUNNER}")
        return False

    print("=" * 88)
    print("FINMARK DATA ANALYTICS PIPELINE")
    print("=" * 88)
    print(f"Project folder: {PROJECT_ROOT}")
    print(f"Python: {sys.executable}")
    print()

    command = [
        sys.executable,
        str(PIPELINE_RUNNER),
    ]

    completed_process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if completed_process.returncode != 0:
        print()
        print("=" * 88)
        print("PIPELINE EXECUTION FAILED")
        print("=" * 88)
        print(
            "Review the stage error shown above."
        )
        return False

    print()
    print("=" * 88)
    print("PIPELINE EXECUTION COMPLETED")
    print("=" * 88)

    return True


def launch_dashboard() -> int:
    """
    Starts the Streamlit dashboard after the pipeline succeeds.
    """

    if not DASHBOARD_APP.exists():
        print(
            "ERROR: dashboard/app.py was not found."
        )
        print(f"Expected location: {DASHBOARD_APP}")
        return 1

    print()
    print("=" * 88)
    print("STARTING FINMARK DASHBOARD")
    print("=" * 88)
    print(
        "Open the following address in your browser:"
    )
    print("http://localhost:8501")
    print()
    print(
        "Keep this window open while using the dashboard."
    )
    print(
        "Press Ctrl + C to stop the dashboard."
    )
    print()

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(DASHBOARD_APP),
    ]

    try:
        return subprocess.call(
            command,
            cwd=PROJECT_ROOT,
        )

    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        return 0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete FinMark data pipeline "
            "and optionally launch the dashboard."
        )
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help=(
            "Launch the Streamlit dashboard after "
            "the pipeline completes successfully."
        ),
    )

    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help=(
            "Launch the dashboard without running "
            "the pipeline."
        ),
    )

    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    if arguments.dashboard_only:
        return launch_dashboard()

    pipeline_succeeded = run_complete_pipeline()

    if not pipeline_succeeded:
        return 1

    if arguments.dashboard:
        return launch_dashboard()

    print()
    print("To launch the dashboard, run:")
    print(
        f'"{sys.executable}" main.py --dashboard-only'
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())