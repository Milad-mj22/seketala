import pandas as pd

def fix_persian_text(text):
    if isinstance(text, str):
        try:
            fixed = text.encode("latin1").decode("utf-8")
            if any('\u0600' <= ch <= '\u06FF' for ch in fixed):
                return fixed
            else:
                return text
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text

def repair_excel(input_file, output_file):
    # Read the Excel file
    df = pd.read_excel(input_file)

    # Fix first name and last name columns
    df['first name'] = df['first name'].apply(fix_persian_text)
    df['last name'] = df['last name'].apply(fix_persian_text)

    # Save to a new Excel file
    df.to_excel(output_file, index=False)
    #print(f"✅ Fixed file saved to: {output_file}")




def repair_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Fix first name and last name columns
    if 'first name' in df.columns:
        df['first name'] = df['first name'].apply(fix_persian_text)
    if 'last name' in df.columns:
        df['last name'] = df['last name'].apply(fix_persian_text)

    # Save to a new CSV file
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    df.to_excel(output_file, index=False)


    #print(f"✅ Fixed CSV file saved to: {output_file}")


import re
import gender_guesser.detector as gender
from persian_gender_detection import get_gender
d = gender.Detector()

def detect_gender(name):
    # تشخیص اینکه فارسیه یا نه
    if re.search(r'[\u0600-\u06FF]', name):  # حروف فارسی
        return get_gender(name)
    else:
        return d.get_gender(name)







