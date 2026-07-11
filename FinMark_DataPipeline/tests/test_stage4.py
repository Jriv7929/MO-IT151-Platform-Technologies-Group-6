import pandas as pd
from test_helpers import section, show
from cleaning import clean_datasets
from config import create_project_directories
from fallback import apply_fallback_rules
from ingestion import load_datasets
from logger_config import get_logger
from monitoring import PipelineMonitor
from profiling import profile_datasets
from storage import save_all_zones
from transformation import transform_datasets
from validation import validate_datasets

def summarize(datasets, zone):
    return pd.DataFrame([
        {'zone': zone, 'dataset': n, 'rows': len(df), 'columns': len(df.columns),
         'missing_values': int(df.isna().sum().sum())}
        for n, df in datasets.items()
    ])

def main():
    section('STAGE 4 – TRANSFORMATION AND STORAGE')
    create_project_directories()
    logger = get_logger(); monitor = PipelineMonitor()
    logger.info('Stage 4 transformation and storage test started.')
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
    with monitor.track('Transformation'):
        transformed, curated = transform_datasets(cleaned)
    with monitor.track('Storage'):
        storage_report = save_all_zones(
            transformed_datasets=transformed,
            curated_datasets=curated,
            quarantined_datasets=quarantined,
        )
    zone_summary = pd.concat([
        summarize(transformed, 'transformed'),
        summarize(curated, 'curated'),
        summarize(quarantined, 'quarantine'),
    ], ignore_index=True)
    show(zone_summary, 'DATASET ZONE SUMMARY')
    show(storage_report, 'STORAGE REPORT')
    section('STAGE 4 TEST SUMMARY')
    print(f'Validation Mode        : {validation_mode}')
    print(f'Fallback Mode          : {fallback_result.pipeline_mode}')
    print(f'Financial KPIs Enabled : {fallback_result.financial_kpis_enabled}')
    print(f'Transformed Datasets   : {len(transformed)}')
    print(f'Curated Datasets       : {len(curated)}')
    print(f'Storage Records        : {len(storage_report)}')
    print('Status                 : PASSED')
    monitor.save_report(); monitor.print_summary()
    logger.info('Stage 4 transformation and storage test completed.')

if __name__ == '__main__':
    main()
