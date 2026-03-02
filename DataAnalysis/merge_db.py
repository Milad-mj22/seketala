import sqlite3
import pandas as pd
import os

# === CONFIG ===
db_files = [r"DataAnalysis\Factors\Factors_140301.db", r"DataAnalysis\Factors\Factors_140302.db", r"DataAnalysis\Factors\Factors_140401.db"]  # your 3 dbs
output_db = "factor.db"
table_name = "facts"  # name of your common table
# ==============

# remove output db if exists
if os.path.exists(output_db):
    os.remove(output_db)

# create output db connection
merged_conn = sqlite3.connect(output_db)

for db_file in db_files:
    #print(f"Processing {db_file} ...")
    conn = sqlite3.connect(db_file)

    # Read table into pandas DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    #print(f" - Rows: {len(df)}")
    conn.close()

    # Append data into output database
    df.to_sql(table_name, merged_conn, if_exists="append", index=False)

merged_conn.close()
#print("\n✅ All databases merged successfully into:", output_db)
