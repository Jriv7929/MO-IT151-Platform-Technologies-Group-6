from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.business_analytics import BusinessAnalytics

SEARCH_DIRECTORIES = [
    PROJECT_ROOT / 'data' / 'curated',
    PROJECT_ROOT / 'data' / 'processed',
    PROJECT_ROOT / 'data' / 'clean',
    PROJECT_ROOT / 'data' / 'cleaned',
    PROJECT_ROOT / 'data' / 'transformed',
    PROJECT_ROOT / 'data' / 'raw',
    PROJECT_ROOT / 'output',
    PROJECT_ROOT / 'data',
]

def section(title: str, width: int = 115) -> None:
    print('\n' + title)
    print('-' * width)

def find_dataset_file(names, keywords):
    for directory in SEARCH_DIRECTORIES:
        if directory.exists():
            for name in names:
                path = directory / name
                if path.exists():
                    return path
    for name in names:
        matches = list(PROJECT_ROOT.rglob(name))
        if matches:
            return matches[0]
    for csv_file in PROJECT_ROOT.rglob('*.csv'):
        normalized = csv_file.stem.lower()
        if all(k.lower() in normalized for k in keywords):
            return csv_file
    return None

def load_dataset(label, names, keywords):
    path = find_dataset_file(names, keywords)
    if path is None:
        print(f'WARNING: {label} dataset was not found.')
        return pd.DataFrame(), None
    df = pd.read_csv(path)
    print(f'{label:<22} {path}')
    print(f'{"":<22} rows={len(df):,}, columns={len(df.columns):,}')
    return df, path

def build_summary(df):
    if df.empty:
        return {'row_count': 0, 'column_count': 0, 'missing_count': 0,
                'duplicate_rows': 0, 'completeness_score': 0.0,
                'quality_score': 0.0}
    rows, cols = df.shape
    cells = rows * cols
    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())
    completeness = ((cells - missing) / cells) * 100 if cells else 0.0
    duplicate_rate = duplicates / rows if rows else 0.0
    quality = max(0.0, min(100.0, completeness - duplicate_rate * 100))
    return {'row_count': rows, 'column_count': cols, 'missing_count': missing,
            'duplicate_rows': duplicates,
            'completeness_score': round(completeness, 2),
            'quality_score': round(quality, 2)}

def main():
    section('STAGE 5 – BUSINESS ANALYTICS')
    output_directory = PROJECT_ROOT / 'output'
    output_directory.mkdir(parents=True, exist_ok=True)
    section('SEARCHING FOR STAGE 4 DATASETS')
    event_logs, _ = load_dataset('Event logs', [
        'event_logs_curated.csv','event_logs_transformed.csv','event_logs_processed.csv',
        'event_logs_cleaned.csv','cleaned_event_logs.csv','event_logs.csv'], ['event','log'])
    marketing, _ = load_dataset('Marketing summary', [
        'marketing_summary_curated.csv','marketing_summary_transformed.csv',
        'marketing_summary_processed.csv','marketing_summary_cleaned.csv',
        'cleaned_marketing_summary.csv','marketing_summary.csv'], ['marketing','summary'])
    trend, _ = load_dataset('Trend report', [
        'trend_report_curated.csv','trend_report_transformed.csv','trend_report_processed.csv',
        'trend_report_cleaned.csv','cleaned_trend_report.csv','trend_report.csv'], ['trend','report'])
    if event_logs.empty and marketing.empty and trend.empty:
        raise FileNotFoundError('No usable Stage 4 datasets were found.')
    summaries = {
        'event_logs': build_summary(event_logs),
        'marketing_summary': build_summary(marketing),
        'trend_report': build_summary(trend),
    }
    summary_df = pd.DataFrame([{'dataset': n, **v} for n, v in summaries.items()])
    section('DATASET SUMMARY')
    print(summary_df.to_string(index=False))
    quarantined = 0
    qdir = PROJECT_ROOT / 'data' / 'quarantine'
    if qdir.exists():
        for qfile in qdir.rglob('*.csv'):
            try:
                quarantined += len(pd.read_csv(qfile))
            except Exception:
                pass
    analytics = BusinessAnalytics(output_directory=output_directory)
    results = analytics.run(
        event_logs=event_logs,
        marketing_summary=marketing,
        trend_report=trend,
        dataset_summaries=summaries,
        pipeline_mode='DEGRADED' if quarantined > 0 else 'NORMAL',
        financial_kpis_enabled=quarantined == 0,
        quarantined_records=quarantined,
        warning_count=1 if quarantined > 0 else 0,
        error_count=0,
        total_processing_seconds=0.0,
    )
    section('BUSINESS KPIS')
    print(results['business_kpis'].to_string(index=False))
    section('PIPELINE HEALTH METRICS')
    print(results['pipeline_health_metrics'].to_string(index=False))
    section('EXECUTIVE SUMMARY')
    print(results['executive_summary'].to_string(index=False))
    required = ['business_kpis.csv','pipeline_health_metrics.csv',
                'executive_summary.csv','powerbi_dashboard_dataset.csv']
    section('GENERATED FILES')
    all_created = True
    for name in required:
        path = output_directory / name
        exists = path.exists(); all_created = all_created and exists
        size = path.stat().st_size if exists else 0
        print(f'{name:<40} {"CREATED" if exists else "MISSING":<10} {size:>10,} bytes')
    section('STAGE 5 TEST SUMMARY')
    print(f'Business KPI Records    : {len(results["business_kpis"])}')
    print(f'Pipeline Health Records : {len(results["pipeline_health_metrics"])}')
    print(f'Quarantined Records     : {quarantined:,}')
    print(f'Status                  : {"PASSED" if all_created else "FAILED"}')
    if not all_created:
        raise RuntimeError('One or more Stage 5 outputs were not created.')

if __name__ == '__main__':
    main()
