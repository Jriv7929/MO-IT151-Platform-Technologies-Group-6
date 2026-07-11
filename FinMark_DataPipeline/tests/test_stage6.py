from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard_monitoring import DashboardMonitoring

def section(title: str, width: int = 115):
    print('\n' + title)
    print('-' * width)

def main():
    section('STAGE 6 – DASHBOARD MONITORING')
    output = PROJECT_ROOT / 'output'
    kpi_path = output / 'business_kpis.csv'
    health_path = output / 'pipeline_health_metrics.csv'
    section('INPUT FILE VERIFICATION')
    for path in (kpi_path, health_path):
        print(f'{path.name:<40} {"FOUND" if path.exists() else "MISSING"}')
    missing = [p for p in (kpi_path, health_path) if not p.exists()]
    if missing:
        raise FileNotFoundError('Missing Stage 5 outputs: ' + ', '.join(p.name for p in missing))
    business_kpis = pd.read_csv(kpi_path)
    pipeline_health = pd.read_csv(health_path)
    monitoring = DashboardMonitoring(output_directory=output)
    results = monitoring.run(
        business_kpis=business_kpis,
        pipeline_health_metrics=pipeline_health,
        fallback_summary={'pipeline_mode': 'DEGRADED', 'financial_kpis_enabled': False},
    )
    section('DASHBOARD STATUS')
    print(results['dashboard_status'].to_string(index=False))
    section('DASHBOARD ALERTS')
    print(results['dashboard_alerts'].to_string(index=False))
    generated = [output / 'dashboard_status.csv', output / 'dashboard_alerts.csv']
    section('GENERATED FILES')
    all_created = True
    for path in generated:
        exists = path.exists(); all_created = all_created and exists
        print(f'{path.name:<40} {"CREATED" if exists else "MISSING"}')
    section('STAGE 6 TEST SUMMARY')
    print(f'Status Records : {len(results["dashboard_status"])}')
    print(f'Alert Records  : {len(results["dashboard_alerts"])}')
    print(f'Status         : {"PASSED" if all_created else "FAILED"}')
    if not all_created:
        raise RuntimeError('Stage 6 outputs were not created.')

if __name__ == '__main__':
    main()
