import pandas as pd
from pathlib import Path
from rapidfuzz import process, fuzz
from user_management.utils import check_server

# -----------------------------
# Normalization
# -----------------------------
def normalize_fa(text: str) -> str:
    return (
        text.replace("ي", "ی")
            .replace("ك", "ک")
            .replace("\u200c", "")
            .strip()
    )


# Load once at import time
SERVER = check_server()

if SERVER:
    EXCEL_PATH = Path(r"/home/seketal1/Seketala_Kitchen_Flow/cache/sepidar_food_code.xlsx")  # adjust path
else:
    EXCEL_PATH = Path(r"cache\sepidar_food_code.xlsx")

_df = pd.read_excel(EXCEL_PATH, dtype=str)

_df["كد"] = _df["كد"].astype(str).str.strip()
_df["عنوان"] = _df["عنوان"].apply(normalize_fa)

# Build NAME -> CODE map
_NAME_TO_CODE = dict(zip(_df["عنوان"], _df["كد"]))
_NAMES = list(_NAME_TO_CODE.keys())

# -----------------------------
# Fuzzy lookup (≥ 90%)

# -----------------------------
def get_code_by_name(name: str, threshold: int = 90) -> str | None:
    if not name:
        return None

    name = normalize_fa(name)

    match = process.extractOne(
        name,
        _NAMES,
        scorer=fuzz.ratio
    )

    if match and match[1] >= threshold:
        matched_name = match[0]
        return _NAME_TO_CODE[matched_name]


    return None

# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    print(get_code_by_name("ماشروم برگر"))      # exact
    print(get_code_by_name("ماشرومبرگر"))       # missing space
    print(get_code_by_name("ماشروم برکر"))      # typo
