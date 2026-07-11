from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

# ingestion.py is located inside:
# FinMark_DataPipeline/src/ingestion.py
#
# parents[1] points to:
# FinMark_DataPipeline/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIRECTORY = PROJECT_ROOT / "data"
RAW_DIRECTORY = DATA_DIRECTORY / "raw"
LOG_DIRECTORY = PROJECT_ROOT / "logs"


# ============================================================
# REQUIRED DATASETS
# ============================================================

DATASET_FILES: dict[str, Path] = {
    "event_logs": RAW_DIRECTORY / "event_logs.csv",
    "marketing_summary": RAW_DIRECTORY / "marketing_summary.csv",
    "trend_report": RAW_DIRECTORY / "trend_report.csv",
}


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class DataIngestionError(Exception):
    """
    Raised when a required dataset cannot be loaded.
    """


# ============================================================
# LOGGING
# ============================================================

def get_logger() -> logging.Logger:
    """
    Creates or retrieves the ingestion logger.
    """

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(
        "finmark_pipeline.ingestion"
    )

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        LOG_DIRECTORY / "pipeline.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


LOGGER = get_logger()


# ============================================================
# DIRECTORY PREPARATION
# ============================================================

def create_required_directories() -> None:
    """
    Ensures that the project directories needed by ingestion exist.
    """

    required_directories = [
        DATA_DIRECTORY,
        RAW_DIRECTORY,
        DATA_DIRECTORY / "processed",
        DATA_DIRECTORY / "curated",
        DATA_DIRECTORY / "quarantine",
        PROJECT_ROOT / "output",
        LOG_DIRECTORY,
    ]

    for directory in required_directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


# ============================================================
# CSV READER
# ============================================================

def read_csv_safely(
    file_path: str | Path,
    dataset_name: str,
    required: bool = True,
    **read_csv_options: Any,
) -> pd.DataFrame:
    """
    Safely reads a CSV file and provides clear ingestion errors.

    Parameters
    ----------
    file_path:
        Full path to the CSV file.

    dataset_name:
        Logical dataset name used in logs and error messages.

    required:
        When True, a missing or unreadable file raises
        DataIngestionError. When False, an empty DataFrame is returned.

    read_csv_options:
        Additional keyword arguments passed to pandas.read_csv().

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    path = Path(file_path).resolve()

    LOGGER.info(
        "Loading dataset | Name: %s | Path: %s",
        dataset_name,
        path,
    )

    if not path.exists():
        message = (
            f"Required dataset was not found: {path}"
            if required
            else f"Optional dataset was not found: {path}"
        )

        if required:
            LOGGER.error(message)
            raise DataIngestionError(message)

        LOGGER.warning(message)
        return pd.DataFrame()

    if not path.is_file():
        message = (
            f"Dataset path is not a file: {path}"
        )

        if required:
            LOGGER.error(message)
            raise DataIngestionError(message)

        LOGGER.warning(message)
        return pd.DataFrame()

    try:
        dataframe = pd.read_csv(
            path,
            **read_csv_options,
        )

    except pd.errors.EmptyDataError as error:
        message = (
            f"Dataset is empty: {path}"
        )

        if required:
            LOGGER.error(message)
            raise DataIngestionError(
                message
            ) from error

        LOGGER.warning(message)
        return pd.DataFrame()

    except pd.errors.ParserError as error:
        message = (
            f"Dataset contains invalid CSV formatting: {path}"
        )

        LOGGER.error(message)

        raise DataIngestionError(
            message
        ) from error

    except UnicodeDecodeError as error:
        message = (
            f"Dataset encoding could not be read: {path}"
        )

        LOGGER.error(message)

        raise DataIngestionError(
            message
        ) from error

    except PermissionError as error:
        message = (
            f"Permission denied while reading dataset: {path}"
        )

        LOGGER.error(message)

        raise DataIngestionError(
            message
        ) from error

    except OSError as error:
        message = (
            f"Operating-system error while reading "
            f"dataset {path}: {error}"
        )

        LOGGER.error(message)

        raise DataIngestionError(
            message
        ) from error

    except Exception as error:
        message = (
            f"Unexpected error while reading "
            f"dataset {path}: {error}"
        )

        LOGGER.exception(message)

        raise DataIngestionError(
            message
        ) from error

    LOGGER.info(
        "Dataset loaded successfully | "
        "Name: %s | Rows: %s | Columns: %s",
        dataset_name,
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe


# ============================================================
# INGESTION METADATA
# ============================================================

def build_ingestion_record(
    dataset_name: str,
    file_path: Path,
    dataframe: pd.DataFrame,
    status: str = "LOADED",
    error_message: str = "",
) -> dict[str, Any]:
    """
    Creates one ingestion-summary record.
    """

    file_size_bytes = (
        file_path.stat().st_size
        if file_path.exists()
        and file_path.is_file()
        else 0
    )

    return {
        "dataset": dataset_name,
        "row_count": int(len(dataframe)),
        "column_count": int(
            len(dataframe.columns)
        ),
        "file_size_bytes": int(
            file_size_bytes
        ),
        "status": status,
        "source_path": str(file_path),
        "error_message": error_message,
    }


# ============================================================
# DATASET LOADER
# ============================================================

def load_datasets(
    dataset_files: dict[str, str | Path] | None = None,
) -> tuple[
    dict[str, pd.DataFrame],
    pd.DataFrame,
]:
    """
    Loads all required FinMark datasets.

    Returns
    -------
    tuple
        datasets:
            Dictionary containing event_logs, marketing_summary,
            and trend_report DataFrames.

        ingestion_metadata:
            DataFrame containing row counts, column counts,
            file sizes, source paths, and ingestion status.
    """

    create_required_directories()

    selected_files = (
        dataset_files
        if dataset_files is not None
        else DATASET_FILES
    )

    datasets: dict[str, pd.DataFrame] = {}
    ingestion_records: list[
        dict[str, Any]
    ] = []

    LOGGER.info(
        "Stage started: Data Ingestion"
    )

    for dataset_name, configured_path in (
        selected_files.items()
    ):
        file_path = Path(
            configured_path
        ).resolve()

        try:
            dataframe = read_csv_safely(
                file_path=file_path,
                dataset_name=dataset_name,
                required=True,
            )

            datasets[dataset_name] = dataframe

            ingestion_records.append(
                build_ingestion_record(
                    dataset_name=dataset_name,
                    file_path=file_path,
                    dataframe=dataframe,
                    status="LOADED",
                )
            )

        except DataIngestionError as error:
            datasets[dataset_name] = (
                pd.DataFrame()
            )

            ingestion_records.append(
                build_ingestion_record(
                    dataset_name=dataset_name,
                    file_path=file_path,
                    dataframe=pd.DataFrame(),
                    status="FAILED",
                    error_message=str(error),
                )
            )

            LOGGER.error(
                "Dataset ingestion failed | "
                "Name: %s | Error: %s",
                dataset_name,
                error,
            )

            raise

    ingestion_metadata = pd.DataFrame(
        ingestion_records
    )

    total_rows = sum(
        len(dataframe)
        for dataframe in datasets.values()
    )

    LOGGER.info(
        "Stage finished: Data Ingestion | "
        "Status: SUCCESS | "
        "Datasets: %s | Total Rows: %s",
        len(datasets),
        total_rows,
    )

    return datasets, ingestion_metadata


# ============================================================
# STANDALONE EXECUTION
# ============================================================

def main() -> int:
    """
    Allows ingestion.py to be run directly for verification.
    """

    try:
        datasets, ingestion_metadata = (
            load_datasets()
        )

        print(
            "\nINGESTION SUMMARY"
        )
        print("-" * 100)

        display_columns = [
            "dataset",
            "row_count",
            "column_count",
            "file_size_bytes",
            "status",
        ]

        print(
            ingestion_metadata[
                display_columns
            ].to_string(index=False)
        )

        print(
            "\nDATASET LOCATIONS"
        )
        print("-" * 100)

        for dataset_name, file_path in (
            DATASET_FILES.items()
        ):
            print(
                f"{dataset_name:<25} "
                f"{file_path}"
            )

        print(
            "\nStage 1 ingestion completed successfully."
        )

        return 0

    except DataIngestionError as error:
        print(
            "\nStage 1 ingestion failed."
        )
        print(
            f"Reason: {error}"
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())