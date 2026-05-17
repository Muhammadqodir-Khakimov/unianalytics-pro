"""Check OLAP/OLTP DB schema state."""
import sqlite3
from pathlib import Path

base = Path(__file__).resolve().parents[1]
for name in ("student_olap.db", "student_oltp.db"):
    path = base / name
    if not path.exists():
        print(f"{name}: MISSING")
        continue
    print(f"\n{name}:")
    c = sqlite3.connect(str(path))
    rows = c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for r in rows:
        try:
            cnt = c.execute(f"SELECT COUNT(*) FROM {r[0]}").fetchone()[0]
        except Exception as e:
            cnt = f"err: {e}"
        print(f"  {r[0]}: {cnt}")
    c.close()
