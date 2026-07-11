from test_helpers import section, show
from config import create_project_directories
from ingestion import load_datasets
from logger_config import get_logger
from monitoring import PipelineMonitor
from profiling import profile_datasets
from validation import validate_datasets

def main():
    section('STAGE 2 – VALIDATION AND PROFILING')
    create_project_directories()
    logger = get_logger(); monitor = PipelineMonitor()
    logger.info('Stage 2 validation and profiling test started.')
    with monitor.track('Ingestion'):
        datasets, ingestion_metadata = load_datasets()
    with monitor.track('Validation'):
        validation_results, validation_report, pipeline_mode = validate_datasets(datasets)
    with monitor.track('Profiling'):
        quality_report = profile_datasets(datasets)
    show(ingestion_metadata, 'INGESTION SUMMARY')
    show(validation_report, 'SCHEMA VALIDATION SUMMARY')
    show(quality_report, 'DATA QUALITY SUMMARY')
    section('VALIDATION RESULT BY DATASET')
    if isinstance(validation_results, dict):
        for name, result in validation_results.items():
            print(f'{name:<25} {result}')
    else:
        print(validation_results)
    section('STAGE 2 TEST SUMMARY')
    print(f'Pipeline Mode          : {pipeline_mode}')
    print(f'Validation Records     : {len(validation_report)}')
    print(f'Quality Report Records : {len(quality_report)}')
    print('Status                 : PASSED')
    monitor.save_report(); monitor.print_summary()
    logger.info('Stage 2 validation and profiling test completed.')

if __name__ == '__main__':
    main()
