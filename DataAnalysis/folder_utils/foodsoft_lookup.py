import pandas as pd
from pathlib import Path
import os
from user_management.utils import check_server

# Load once at import time
SERVER = check_server()
if SERVER:
    EXCEL_PATH = Path(r"/home/seketal1/Seketala_Kitchen_Flow/cache/food_soft_food_code.xls")  # adjust path
else:
    EXCEL_PATH = Path(r"cache\food_soft_food_code.xls")  # adjust path
_df = pd.read_excel(EXCEL_PATH, dtype=str)

# Optional: normalize
_df["kcod"] = _df["kcod"].str.strip()
_df["kname"] = _df["kname"].str.strip()

# Build dict for O(1) lookup
_KCOD_MAP = dict(zip(_df["kcod"], _df["kname"]))


def get_kname_by_kcod(kcod: str) -> str | None:
    if not kcod:
        return None
    return _KCOD_MAP.get(str(kcod).strip())



if __name__=='__main__':
    a = get_kname_by_kcod(111)
    print(a)