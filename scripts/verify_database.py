"""Воспроизводимо создаёт учебную БД, выполняет SQL и сохраняет результаты."""
from pathlib import Path
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "database"
DOCS = ROOT / "docs" / "database"
DB_PATH = DB_DIR / "requests.db"


def statement_body(statement: str) -> str:
    return "\n".join(
        line for line in statement.splitlines() if not line.strip().startswith("--")
    ).strip()


def md_value(value):
    if value is None:
        return "NULL"
    return str(value).replace("|", "\\|").replace("\n", " ")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((DB_DIR / "schema.sql").read_text(encoding="utf-8"))
    conn.executescript((DB_DIR / "seed.sql").read_text(encoding="utf-8"))

    query_results = []
    operations = []
    raw_queries = (DB_DIR / "queries.sql").read_text(encoding="utf-8")
    for raw in raw_queries.split(";"):
        sql = statement_body(raw)
        if not sql:
            continue
        kind = sql.split(None, 1)[0].upper()
        cursor = conn.execute(sql)
        if kind == "SELECT":
            columns = [item[0] for item in cursor.description]
            rows = [dict(row) for row in cursor.fetchall()]
            query_results.append({"id": f"Q{len(query_results) + 1:02d}", "columns": columns, "rows": rows})
        else:
            operations.append({"operation": kind, "affected_rows": cursor.rowcount})
    conn.commit()

    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk_errors = [tuple(row) for row in conn.execute("PRAGMA foreign_key_check")]
    counts = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("Roles", "Users", "Statuses", "Categories", "Requests", "Comments", "RequestHistory")
    }
    assert integrity == "ok", integrity
    assert not fk_errors, fk_errors
    assert counts["Requests"] == 5, counts
    assert counts["Categories"] >= 4, counts
    assert len(query_results) >= 5
    assert sum(1 for op in operations if op["operation"] == "UPDATE") >= 2
    assert sum(1 for op in operations if op["operation"] == "DELETE") >= 2
    conn.close()

    lines = [
        "# Фактические результаты выполнения SQL",
        "",
        "База создана заново из `schema.sql` и `seed.sql`, после чего последовательно выполнен `queries.sql`.",
        "Результаты ниже получены средствами `sqlite3`, а не составлены вручную.",
        "",
    ]
    for result in query_results:
        lines.extend([f"## {result['id']}", ""])
        lines.append("| " + " | ".join(result["columns"]) + " |")
        lines.append("|" + "|".join(["---"] * len(result["columns"])) + "|")
        for row in result["rows"]:
            lines.append("| " + " | ".join(md_value(row[col]) for col in result["columns"]) + " |")
        lines.append("")
    lines.extend(["## DML-операции", "", "| Операция | Затронуто строк |", "|---|---:|"])
    for op in operations:
        lines.append(f"| {op['operation']} | {op['affected_rows']} |")
    lines.extend([
        "",
        "## Проверка целостности",
        "",
        f"- `PRAGMA integrity_check`: **{integrity}**.",
        f"- `PRAGMA foreign_key_check`: **{len(fk_errors)} нарушений**.",
        f"- Итоговое количество записей: `{json.dumps(counts, ensure_ascii=False)}`.",
        "- Временные категория и заявка удалены; основные тестовые данные сохранены.",
    ])
    (DOCS / "query_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {"queries": query_results, "operations": operations, "integrity": integrity,
               "foreign_key_errors": fk_errors, "counts": counts}
    (DOCS / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
