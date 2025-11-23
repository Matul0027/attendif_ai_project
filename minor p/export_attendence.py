import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "database/students.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM attendance", conn)
conn.close()

date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"attendance_{date_str}.xlsx"
df.to_excel(filename, index=False)
print(f"✅ Attendance exported to {filename}")
