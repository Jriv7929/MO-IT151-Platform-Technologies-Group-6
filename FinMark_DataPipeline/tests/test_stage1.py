from test_helpers import section, show
from config import create_project_directories
from ingestion import load_datasets
from logger_config import get_logger
from monitoring import PipelineMonitor

def main():
    section('STAGE 1 – DATA INGESTION')
    create_project_directories()
    logger = get_logger(); monitor = PipelineMonitor()
    logger.info('Stage 1 ingestion test started.')
    with monitor.track('Ingestion'):
        datasets, ingestion_metadata = load_datasets()
    show(ingestion_metadata, 'INGESTION SUMMARY')
    section('DATASETS AVAILABLE')
    total_rows = 0
    for name, df in datasets.items():
        total_rows += len(df)
        print(f'{name:<25} rows={len(df):>6,}  columns={len(df.columns):>3,}')
    section('STAGE 1 TEST SUMMARY')
    print(f'Datasets loaded : {len(datasets)}')
    print(f'Total rows      : {total_rows:,}')
    print('Status          : PASSED')
    monitor.save_report(); monitor.print_summary()
    logger.info('Stage 1 ingestion test completed.')

if __name__ == '__main__':
    main()
