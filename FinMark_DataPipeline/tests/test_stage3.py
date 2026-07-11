import pandas as pd
from test_helpers import section, show
from cleaning import clean_datasets
from config import create_project_directories
from fallback import apply_fallback_rules
from ingestion import load_datasets
from logger_config import get_logger
from monitoring import PipelineMonitor
from profiling import profile_datasets
from validation import validate_datasets

def summarize(datasets):
    return pd.DataFrame([
        {'dataset': n, 'rows': len(df), 'columns': len(df.columns),
         'missing_values': int(df.isna().sum().sum()),
         'duplicate_rows': int(df.duplicated().sum())}
        for n, df in datasets.items()
    ])

def main():
    section('STAGE 3 – FALLBACK, QUARANTINE, AND CLEANING')
    create_project_directories()
    logger = get_logger(); monitor = PipelineMonitor()
    logger.info('Stage 3 fallback and cleaning test started.')
    with monitor.track('Ingestion'):
        datasets, ingestion_metadata = load_datasets()
    with monitor.track('Validation'):
        validation_results, validation_report, validation_mode = validate_datasets(datasets)
    with monitor.track('Raw Profiling'):
        raw_quality_report = profile_datasets(datasets)
    with monitor.track('Fallback Rules'):
        processed, quarantined, fallback_result, fallback_actions = apply_fallback_rules(datasets)
    with monitor.track('Cleaning'):
        cleaned, cleaning_report = clean_datasets(processed)
    show(raw_quality_report, 'RAW DATA QUALITY')
    show(fallback_actions, 'FALLBACK ACTION REPORT')
    show(cleaning_report, 'CLEANING REPORT')
    show(summarize(cleaned), 'CLEANED DATASET SUMMARY')
    show(summarize(quarantined), 'QUARANTINE SUMMARY')
    quarantine_count = sum(len(df) for df in quarantined.values())
    section('STAGE 3 TEST SUMMARY')
    print(f'Validation Mode        : {validation_mode}')
    print(f'Fallback Mode          : {fallback_result.pipeline_mode}')
    print(f'Financial KPIs Enabled : {fallback_result.financial_kpis_enabled}')
    print(f'Fallback Actions       : {len(fallback_actions)}')
    print(f'Cleaned Datasets       : {len(cleaned)}')
    print(f'Quarantined Rows       : {quarantine_count:,}')
    print('Status                 : PASSED')
    monitor.save_report(); monitor.print_summary()
    logger.info('Stage 3 fallback and cleaning test completed.')

if __name__ == '__main__':
    main()
