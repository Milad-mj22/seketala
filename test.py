import pandas as pd

df2 = pd.read_excel(r"cache\food_soft_food_code.xls")
df1 = pd.read_excel(r"c:\Users\milad\Desktop\new_sepidar.xlsx")

# فرض می‌کنیم اسم ستون name هست
only_in_file1 = df1[~df1["عنوان"].isin(df2["kname"])]

print(list(only_in_file1['عنوان']))
