from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
TESTS_DIRECTORY = PROJECT_ROOT / "tests"
OUTPUT_DIRECTORY = PROJECT_ROOT / "output"


@dataclass
class PipelineStage:
    number: int
    name: str
    possible_files: list[Path]


PIPELINE_STAGES = [
    PipelineStage(
        number=1,
        name="Data Ingestion",
        possible_files=[
            TESTS_DIRECTORY / "test_stage1.py",
            PROJECT_ROOT / "test_stage1.py",
        ],
    ),
    PipelineStage(
        number=2,
        name="Validation and Profiling",
        possible_files=[
            TESTS_DIRECTORY / "test_stage2.py",
            PROJECT_ROOT / "test_stage2.py",
        ],
    ),
    PipelineStage(
        number=3,
        name="Cleaning and Transformation",
        possible_files=[
            TESTS_DIRECTORY / "test_stage3.py",
            PROJECT_ROOT / "test_stage3.py",
        ],
    ),
    PipelineStage(
        number=4,
        name="Storage Layer",
        possible_files=[
            TESTS_DIRECTORY / "test_stage4.py",
            PROJECT_ROOT / "test_stage4.py",
        ],
    ),
    PipelineStage(
        number=5,
        name="Business Analytics Layer",
        possible_files=[
            TESTS_DIRECTORY / "test_stage5.py",
            PROJECT_ROOT / "test_stage5.py",
        ],
    ),
    PipelineStage(
        number=6,
        name="Dashboard Monitoring",
        possible_files=[
            TESTS_DIRECTORY / "test_stage6.py",
            PROJECT_ROOT / "test_stage6.py",
        ],
    ),
    PipelineStage(
        number=7,
        name="Professional Dashboard Validation",
        possible_files=[
            TESTS_DIRECTORY / "test_stage7.py",
            PROJECT_ROOT / "test_stage7.py",
        ],
    ),
]


REQUIRED_OUTPUT_FILES = [
    "business_kpis.csv",
    "pipeline_health_metrics.csv",
    "executive_summary.csv",
    "powerbi_dashboard_dataset.csv",
    "dashboard_alerts.csv",
    "dashboard_status.csv",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


def build_environment() -> dict[str, str]:
    """
    Builds the environment used by every pipeline stage.

    The project root and src directory are added to PYTHONPATH so imports
    such as `from config import ...` and `from src.module import ...`
    can both work when stage files are inside the tests directory.
    """

    environment = os.environ.copy()

    python_paths = [
        str(PROJECT_ROOT),
        str(PROJECT_ROOT / "src"),
    ]

    existing_python_path = environment.get(
        "PYTHONPATH",
        "",
    )

    if existing_python_path:
        python_paths.append(existing_python_path)

    environment["PYTHONPATH"] = os.pathsep.join(
        python_paths
    )

    return environment


def find_stage_file(
    stage: PipelineStage,
) -> Path | None:
    """
    Finds the first available file for a pipeline stage.
    """

    for file_path in stage.possible_files:
        if file_path.exists():
            return file_path

    return None


def run_python_file(
    file_path: Path,
) -> tuple[bool, float]:
    """
    Executes one Python stage using the same interpreter that launched
    this pipeline runner.
    """

    start_time = time.perf_counter()

    command = [
        sys.executable,
        str(file_path),
    ]

    print(f"Command: {' '.join(command)}")
    print("-" * 88)

    try:
        completed_process = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=build_environment(),
            check=False,
        )

        elapsed_seconds = (
            time.perf_counter() - start_time
        )

        succeeded = (
            completed_process.returncode == 0
        )

        return succeeded, elapsed_seconds

    except KeyboardInterrupt:
        print(
            "\nPipeline execution was cancelled by the user."
        )
        raise

    except Exception as error:
        elapsed_seconds = (
            time.perf_counter() - start_time
        )

        print(
            f"\nUnable to execute {file_path.name}: "
            f"{error}"
        )

        return False, elapsed_seconds


def verify_output_files() -> bool:
    """
    Verifies the output files produced by Stages 5 and 6.
    """

    print_header(
        "PIPELINE OUTPUT VERIFICATION"
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_files_exist = True

    for filename in REQUIRED_OUTPUT_FILES:
        file_path = OUTPUT_DIRECTORY / filename

        if file_path.exists():
            file_size = file_path.stat().st_size

            print(
                f"[FOUND]   "
                f"{filename:<40}"
                f"{file_size:>12,} bytes"
            )
        else:
            print(
                f"[MISSING] {filename}"
            )

            all_files_exist = False

    return all_files_exist


def launch_dashboard() -> int:
    """
    Launches the Streamlit dashboard.
    """

    dashboard_file = (
        PROJECT_ROOT
        / "dashboard"
        / "app.py"
    )

    if not dashboard_file.exists():
        print(
            "\nDashboard file was not found:"
        )
        print(dashboard_file)
        return 1

    print_header(
        "STARTING FINMARK DASHBOARD"
    )

    print(
        "The dashboard will stay active while "
        "this Command Prompt window remains open."
    )

    print(
        "\nOpen this address in your browser:"
    )
    print(
        "http://localhost:8501"
    )

    print(
        "\nPress Ctrl + C to stop the dashboard.\n"
    )

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard_file),
    ]

    try:
        return subprocess.call(
            command,
            cwd=PROJECT_ROOT,
            env=build_environment(),
        )

    except KeyboardInterrupt:
        print(
            "\nDashboard stopped."
        )
        return 0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete FinMark data "
            "analytics pipeline."
        )
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help=(
            "Launch the Streamlit dashboard after "
            "the pipeline completes."
        ),
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help=(
            "Continue to later stages even when a "
            "previous stage fails or is missing."
        ),
    )

    parser.add_argument(
        "--start-stage",
        type=int,
        choices=range(1, 8),
        default=1,
        metavar="1-7",
        help=(
            "Start execution from a specific stage."
        ),
    )

    parser.add_argument(
        "--end-stage",
        type=int,
        choices=range(1, 8),
        default=7,
        metavar="1-7",
        help=(
            "Stop execution after a specific stage."
        ),
    )

    return parser.parse_args()


def print_execution_summary(
    results: list[dict[str, object]],
    total_elapsed_seconds: float,
) -> None:
    """
    Prints the result of every executed pipeline stage.
    """

    print_header(
        "PIPELINE EXECUTION SUMMARY"
    )

    print(
        f"{'Stage':<8}"
        f"{'Name':<42}"
        f"{'Status':<12}"
        f"{'Seconds':>10}"
    )

    print("-" * 72)

    for result in results:
        print(
            f"{int(result['stage']):<8}"
            f"{str(result['name']):<42}"
            f"{str(result['status']):<12}"
            f"{float(result['seconds']):>10.2f}"
        )

    print("-" * 72)

    print(
        f"{'Total processing time':<62}"
        f"{total_elapsed_seconds:>10.2f}"
    )


def main() -> int:
    arguments = parse_arguments()

    if (
        arguments.start_stage
        > arguments.end_stage
    ):
        print(
            "Error: --start-stage cannot be greater "
            "than --end-stage."
        )
        return 1

    print_header(
        "FINMARK DATA ANALYTICS PIPELINE"
    )

    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Python:       {sys.executable}"
    )

    print(
        f"PYTHONPATH:   "
        f"{build_environment().get('PYTHONPATH', '')}"
    )

    selected_stages = [
        stage
        for stage in PIPELINE_STAGES
        if (
            arguments.start_stage
            <= stage.number
            <= arguments.end_stage
        )
    ]

    results: list[dict[str, object]] = []

    pipeline_start = time.perf_counter()
    pipeline_failed = False

    for stage in selected_stages:
        print_header(
            f"STAGE {stage.number} – {stage.name}"
        )

        stage_file = find_stage_file(
            stage
        )

        if stage_file is None:
            print(
                "Stage file was not found."
            )

            print(
                "Searched:"
            )

            for possible_file in (
                stage.possible_files
            ):
                print(
                    f"- {possible_file}"
                )

            results.append(
                {
                    "stage": stage.number,
                    "name": stage.name,
                    "status": "MISSING",
                    "seconds": 0.0,
                }
            )

            pipeline_failed = True

            if not arguments.continue_on_error:
                print(
                    "\nPipeline stopped because a "
                    "required stage file is missing."
                )
                break

            continue

        print(
            f"Stage file: {stage_file}"
        )

        succeeded, elapsed_seconds = (
            run_python_file(stage_file)
        )

        status = (
            "PASSED"
            if succeeded
            else "FAILED"
        )

        results.append(
            {
                "stage": stage.number,
                "name": stage.name,
                "status": status,
                "seconds": elapsed_seconds,
            }
        )

        if succeeded:
            print(
                f"\nStage {stage.number} completed "
                f"successfully in "
                f"{elapsed_seconds:.2f} seconds."
            )
        else:
            print(
                f"\nStage {stage.number} failed after "
                f"{elapsed_seconds:.2f} seconds."
            )

            pipeline_failed = True

            if not arguments.continue_on_error:
                print(
                    "\nPipeline stopped because the "
                    "stage failed."
                )
                break

    total_elapsed_seconds = (
        time.perf_counter()
        - pipeline_start
    )

    print_execution_summary(
        results=results,
        total_elapsed_seconds=(
            total_elapsed_seconds
        ),
    )

    outputs_available = (
        verify_output_files()
    )

    if pipeline_failed:
        print(
            "\nFINAL STATUS: PIPELINE FAILED"
        )

        print(
            "Review the failed or missing stage "
            "output above."
        )

        return 1

    if not outputs_available:
        print(
            "\nFINAL STATUS: COMPLETED WITH "
            "MISSING OUTPUTS"
        )

        print(
            "The stages completed, but one or more "
            "expected output files were not found."
        )

        return 1

    print(
        "\nFINAL STATUS: PIPELINE COMPLETED "
        "SUCCESSFULLY"
    )

    if arguments.dashboard:
        return launch_dashboard()

    print(
        "\nTo launch the dashboard, run:"
    )

    print(
        f'"{sys.executable}" -m streamlit '
        "run dashboard\\app.py"
    )

    print(
        "\nOr run the pipeline and dashboard together:"
    )

    print(
        f'"{sys.executable}" '
        "run_pipeline.py --dashboard"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )