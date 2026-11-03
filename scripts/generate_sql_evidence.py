from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = json.loads((DOCS / "database" / "results.json").read_text(encoding="utf-8"))
REGULAR = os.environ.get("DAIMON_CJK_FONT_REGULAR", "C:/Windows/Fonts/arial.ttf")
BOLD = os.environ.get("DAIMON_CJK_FONT_BOLD", "C:/Windows/Fonts/arialbd.ttf")
BG = "#101820"
PANEL = "#17242F"
FG = "#E6EDF3"
MUTED = "#9FB2C1"
GREEN = "#69D39B"
BLUE = "#7CC7F2"
ORANGE = "#F0B86E"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def txt(d, x, y, value, size=24, color=FG, bold=False):
    d.text((x, y), str(value), font=font(size, bold), fill=color)


def base(title, height=1200):
    im = Image.new("RGB", (1800, height), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1800, 80), fill=PANEL)
    txt(d, 40, 22, title, 30, FG, True)
    txt(d, 40, 105, "PS C:\\...\\RequestSystem> python scripts\\verify_database.py", 24, BLUE)
    return im, d


def results_image():
    im, d = base("SQLite — фактические результаты SELECT")
    q1 = DATA["queries"][0]
    y = 170
    txt(d, 40, y, "Q01 | Список заявок (JOIN Categories, Statuses, Users)", 25, ORANGE, True)
    y += 55
    widths = [280, 420, 330, 230, 300]
    headers = ["number", "title", "category", "status", "executor"]
    x = 40
    d.rectangle((30, y - 8, 1760, y + 43), fill=PANEL)
    for width, header in zip(widths, headers):
        txt(d, x, y, header, 21, MUTED, True)
        x += width
    y += 58
    for row in q1["rows"]:
        x = 40
        values = [row[h] for h in headers]
        for width, value in zip(widths, values):
            txt(d, x, y, value, 19, FG)
            x += width
        y += 48
    y += 30
    q2 = DATA["queries"][1]
    txt(d, 40, y, "Q02 | Новые заявки (WHERE)", 25, ORANGE, True)
    y += 50
    for row in q2["rows"]:
        txt(d, 55, y, f"{row['number']} | {row['title']} | {row['created_at']}", 22)
        y += 42
    y += 25
    q7 = DATA["queries"][-1]
    txt(d, 40, y, "Q07 | Итог после INSERT / UPDATE / DELETE", 25, ORANGE, True)
    y += 52
    txt(d, 55, y, " | ".join(q7["columns"]), 22, MUTED, True)
    y += 43
    txt(d, 55, y, " | ".join(str(q7["rows"][0][c]) for c in q7["columns"]), 25, GREEN, True)
    txt(d, 40, 1115, "Результат получен из database/requests.db; таблицы не заполнены вручную.", 21, MUTED)
    path = DOCS / "screenshots" / "sql_results.png"
    im.save(path)
    return path


def integrity_image():
    im, d = base("SQLite — проверка целостности и автотесты", 1050)
    y = 180
    txt(d, 40, y, "DML-операции", 28, ORANGE, True)
    y += 60
    operations = {}
    for item in DATA["operations"]:
        operations[item["operation"]] = operations.get(item["operation"], 0) + 1
    for op in ("INSERT", "UPDATE", "DELETE"):
        txt(d, 60, y, f"{op:<8} выполнено в queries.sql: {operations.get(op, 0)}", 25)
        y += 48
    y += 35
    txt(d, 40, y, f"PRAGMA integrity_check  →  {DATA['integrity']}", 28, GREEN, True)
    y += 60
    txt(d, 40, y, f"PRAGMA foreign_key_check  →  {len(DATA['foreign_key_errors'])} нарушений", 28, GREEN, True)
    y += 75
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    output = (proc.stderr + proc.stdout).strip().splitlines()
    txt(d, 40, y, "PYTHONPATH=src python -m unittest discover -s tests", 23, BLUE)
    y += 48
    for line in output[-4:]:
        txt(d, 60, y, line, 23, GREEN if line.strip() == "OK" else FG)
        y += 40
    if proc.returncode != 0:
        raise RuntimeError("Автотесты завершились с ошибкой")
    path = DOCS / "screenshots" / "sql_integrity.png"
    im.save(path)
    return path


if __name__ == "__main__":
    print(results_image().relative_to(ROOT))
    print(integrity_image().relative_to(ROOT))
