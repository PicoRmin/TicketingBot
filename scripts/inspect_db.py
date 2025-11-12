# Inspect current database schema and print tables/columns
from pathlib import Path
import sys

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine  # type: ignore
from sqlalchemy import inspect


def main() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        print("No tables found.")
        return

    print("Detected tables (database schema):")
    for t in tables:
        print(f"\n- {t}")
        try:
            cols = inspector.get_columns(t)
            for c in cols:
                name = c.get("name")
                type_ = c.get("type")
                nullable = c.get("nullable")
                default = c.get("default")
                print(f"    • {name}: {type_} | nullable={nullable} | default={default}")
        except Exception as e:
            print(f"    ! Error reading columns: {e}")


if __name__ == "__main__":
    main()
