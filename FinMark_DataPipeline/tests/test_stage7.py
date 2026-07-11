from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.data_loader import load_dashboard_data

def section(title: str, width: int = 105):
    print('\n' + title)
    print('-' * width)

def main():
    section('STAGE 7 – PROFESSIONAL DASHBOARD DATA VALIDATION')
    data = load_dashboard_data()
    required = ['event_logs','marketing_summary','trend_report','business_kpis',
                'pipeline_health','dashboard_alerts','dashboard_status']
    section('DASHBOARD DATASET INVENTORY')
    for name, df in data.items():
        status = 'READY' if not df.empty else 'EMPTY'
        print(f'{name:<28} rows={len(df):>6,}  columns={len(df.columns):>3,}  status={status}')
    missing = [name for name in required if data[name].empty]
    section('REQUIRED DATASET CHECK')
    for name in required:
        print(f'{name:<28} {"PASSED" if not data[name].empty else "FAILED"}')
    files = [
        PROJECT_ROOT / 'dashboard' / 'app.py',
        PROJECT_ROOT / 'dashboard' / 'data_loader.py',
        PROJECT_ROOT / 'dashboard' / 'components.py',
        PROJECT_ROOT / 'dashboard' / 'styles.py',
    ]
    section('DASHBOARD APPLICATION CHECK')
    app_ready = True
    for path in files:
        exists = path.exists(); app_ready = app_ready and exists
        print(f'{path.name:<28} {"FOUND" if exists else "MISSING"}')
    passed = not missing and app_ready
    section('STAGE 7 TEST SUMMARY')
    print(f'Datasets checked : {len(data)}')
    print(f'Required datasets: {len(required)}')
    print(f'Missing datasets : {len(missing)}')
    print(f'Dashboard files  : {"READY" if app_ready else "INCOMPLETE"}')
    print(f'Status           : {"PASSED" if passed else "FAILED"}')
    if missing:
        raise RuntimeError('Empty dashboard datasets: ' + ', '.join(missing))
    if not app_ready:
        raise FileNotFoundError('One or more dashboard files are missing.')

if __name__ == '__main__':
    main()
