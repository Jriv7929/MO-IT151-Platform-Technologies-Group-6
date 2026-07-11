from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / 'src'
for path in (PROJECT_ROOT, SRC_DIRECTORY):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

def section(title: str, width: int = 110) -> None:
    print('\n' + title)
    print('-' * width)

def show(data, title: str, max_rows: int = 40, width: int = 110) -> None:
    section(title, width)
    if data is None:
        print('No data returned.')
        return
    if not isinstance(data, pd.DataFrame):
        try:
            data = pd.DataFrame(data)
        except Exception:
            print(data)
            return
    if data.empty:
        print('No records available.')
        return
    print(data.head(max_rows).to_string(index=False))
    if len(data) > max_rows:
        print(f'\nShowing {max_rows:,} of {len(data):,} records.')
