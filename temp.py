# لیست اعداد شما (به صورت رشته)
data = """
total
khales
3500000/00
15000000/00
28000000/00
13000000/00
6400000/00
15180000/00
16800000/00
10950000/00
2360000/00
11770000/00
7000000/00
9910000/00
5400000/00
21000000/00
7060000/00
3530000/00
14500000/00
10200000/00
7000000/00
5010000/00
7750000/00
7000000/00

"""

def sum_numbers(raw_data):
    total = 0
    # جدا کردن اعداد با خط جدید
    lines = raw_data.strip().split('\n')
    
    for line in lines:
        # حذف بخش /00 و تبدیل به عدد صحیح
        clean_number = line.split('/')[0]
        if clean_number.isdigit():
            total += int(clean_number)
            
    return total

# اجرای تابع
result = sum_numbers(data)
print(f"مجموع اعداد: {result:,}")
