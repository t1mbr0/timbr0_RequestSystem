from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
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


def run(*args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def render(name, title, command, lines, accent=GREEN):
    height = max(650, 190 + len(lines) * 39)
    im = Image.new("RGB", (1800, height), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1800, 82), fill=PANEL)
    d.text((40, 22), title, font=font(31, True), fill=FG)
    d.text((40, 110), "PS C:\\...\\RequestSystem> " + command, font=font(23), fill=BLUE)
    y = 170
    for line in lines:
        color = accent if any(token in line for token in ("merge:", "OK", "* main", "develop")) else FG
        d.text((45, y), line, font=font(21), fill=color)
        y += 39
    path = OUT / name
    im.save(path)
    return path


if __name__ == "__main__":
    history = run("git", "log", "--graph", "--all", "--oneline", "--decorate", "-n", "18").splitlines()
    print(render("git_history.png", "Git — история коммитов и слияние", "git log --graph --all --oneline --decorate -n 18", history).relative_to(ROOT))

    branches = run("git", "branch", "-avv").splitlines()
    branches += [""]
    branches += run("git", "status", "--short", "--branch").splitlines()
    branches += ["user.name=" + run("git", "config", "--local", "user.name"), "user.email=" + run("git", "config", "--local", "user.email")]
    print(render("git_branches.png", "Git — ветки main и develop", "git branch -avv && git status", branches).relative_to(ROOT))

    merge = run("git", "show", "--no-patch", "--format=commit %h%nparents %p%nauthor %an <%ae>%nsubject %s", "b928ac5").splitlines()
    merge += ["", "Конфликт: одна строка docs/git_workflow.md изменена в main и develop.", "HEAD: main — основная стабильная ветка, доступная преподавателю.", "develop: изменения попадают в main после проверки в develop.", "", "Ручное разрешение: объединены обе формулировки; маркеры удалены.", "Проверка: merge-коммит b928ac5 имеет двух родителей.", "Опасные команды reset --hard и push --force не применялись."]
    print(render("git_conflict.png", "Git — факт разрешённого конфликта", "git show --no-patch b928ac5", merge, ORANGE).relative_to(ROOT))
