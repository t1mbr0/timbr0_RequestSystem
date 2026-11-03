from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REGULAR = os.environ.get("DAIMON_CJK_FONT_REGULAR", "C:/Windows/Fonts/arial.ttf")
BOLD = os.environ.get("DAIMON_CJK_FONT_BOLD", "C:/Windows/Fonts/arialbd.ttf")
NAVY = "#17324D"
BLUE = "#2F6B9A"
LIGHT = "#EDF4F8"
PALE = "#F7F9FB"
GRAY = "#5D6B78"
LINE = "#8FA6B8"
GREEN = "#2D7B65"
ORANGE = "#B66A2C"
WHITE = "#FFFFFF"
BLACK = "#1D2730"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def centered(draw, box, text, fnt, fill=BLACK, spacing=8):
    x1, y1, x2, y2 = box
    max_width = x2 - x1 - 28
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    line_h = fnt.size + spacing
    total = len(lines) * line_h - spacing
    y = (y1 + y2 - total) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((x1 + x2 - (bbox[2] - bbox[0])) / 2, y), line, font=fnt, fill=fill)
        y += line_h


def arrow(draw, start, end, fill=LINE, width=4, head=14):
    draw.line([start, end], fill=fill, width=width)
    import math
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (end[0] - head * math.cos(angle - math.pi / 6), end[1] - head * math.sin(angle - math.pi / 6))
    right = (end[0] - head * math.cos(angle + math.pi / 6), end[1] - head * math.sin(angle + math.pi / 6))
    draw.polygon([end, left, right], fill=fill)


def actor(draw, x, y, label):
    draw.ellipse((x - 22, y - 100, x + 22, y - 56), outline=NAVY, width=4)
    draw.line((x, y - 56, x, y + 10), fill=NAVY, width=4)
    draw.line((x - 42, y - 28, x + 42, y - 28), fill=NAVY, width=4)
    draw.line((x, y + 10, x - 35, y + 65), fill=NAVY, width=4)
    draw.line((x, y + 10, x + 35, y + 65), fill=NAVY, width=4)
    bbox = draw.textbbox((0, 0), label, font=font(26, True))
    draw.text((x - (bbox[2] - bbox[0]) / 2, y + 82), label, font=font(26, True), fill=NAVY)


def use_case():
    im = Image.new("RGB", (1800, 1240), WHITE)
    d = ImageDraw.Draw(im)
    d.text((70, 38), "Use Case: система учёта заявок", font=font(46, True), fill=NAVY)
    d.rectangle((340, 120, 1470, 1150), outline=NAVY, width=4)
    d.rectangle((340, 120, 1470, 180), fill=LIGHT)
    d.text((370, 132), "Граница системы RequestSystem", font=font(28, True), fill=NAVY)
    boxes = {
        "login": (500, 225, 910, 335),
        "create": (970, 225, 1380, 335),
        "search": (500, 425, 910, 535),
        "assign": (970, 425, 1380, 535),
        "status": (500, 625, 910, 735),
        "comment": (970, 625, 1380, 735),
        "close": (500, 825, 910, 935),
        "admin": (970, 825, 1380, 935),
    }
    labels = {
        "login": "UC-01\nВойти в систему",
        "create": "UC-02\nСоздать заявку",
        "search": "UC-03\nНайти и отфильтровать",
        "assign": "UC-04\nНазначить исполнителя",
        "status": "UC-05\nИзменить статус",
        "comment": "UC-06\nДобавить комментарий",
        "close": "UC-07\nПроверить и закрыть",
        "admin": "UC-08\nУправлять справочниками",
    }
    for key, box in boxes.items():
        d.ellipse(box, fill=PALE, outline=BLUE, width=4)
        centered(d, box, labels[key].replace("\n", " "), font(25, True), NAVY)
    actor(d, 160, 300, "Заявитель")
    actor(d, 160, 760, "Оператор")
    actor(d, 1630, 300, "Исполнитель")
    actor(d, 1630, 790, "Администратор")
    connections = [
        ((220, 290), (500, 280)), ((220, 310), (970, 280)), ((220, 330), (500, 480)),
        ((220, 350), (970, 680)), ((220, 370), (500, 880)),
        ((220, 740), (500, 280)), ((220, 750), (970, 280)), ((220, 760), (500, 480)),
        ((220, 770), (970, 480)), ((220, 780), (500, 680)), ((220, 790), (970, 680)),
        ((1570, 290), (500, 280)), ((1570, 310), (500, 480)), ((1570, 330), (500, 680)),
        ((1570, 350), (970, 680)),
        ((1570, 760), (500, 280)), ((1570, 770), (500, 480)), ((1570, 780), (970, 480)),
        ((1570, 790), (500, 680)), ((1570, 800), (970, 680)), ((1570, 810), (500, 880)),
        ((1570, 820), (970, 880)),
    ]
    for start, end in connections:
        d.line((start, end), fill="#B7C5CF", width=3)
    # Перерисовываем узлы поверх линий связей.
    for key, box in boxes.items():
        d.ellipse(box, fill=PALE, outline=BLUE, width=4)
        centered(d, box, labels[key].replace("\n", " "), font(25, True), NAVY)
    d.text((480, 1050), "Все варианты использования выполняются после аутентификации и с учётом прав роли.", font=font(25), fill=GRAY)
    path = DOCS / "use_case.png"
    im.save(path, quality=95)
    return path


def architecture():
    im = Image.new("RGB", (1700, 1200), WHITE)
    d = ImageDraw.Draw(im)
    d.text((70, 40), "Слоистая архитектура RequestSystem", font=font(46, True), fill=NAVY)
    d.text((70, 105), "Зависимости направлены сверху вниз; обратных вызовов из базы в интерфейс нет", font=font(25), fill=GRAY)
    layers = [
        ("1. Presentation / Controller", "HTTP-запросы, проверка формата, вызов сервиса, формирование ответа", "Не содержит SQL и бизнес-правил", BLUE),
        ("2. Service", "Права доступа, переходы статусов, назначение исполнителя, транзакции", "Не рисует интерфейс и не работает с HTTP", GREEN),
        ("3. Repository / Data Access", "CRUD, параметризованные SQL-запросы, преобразование записей в объекты", "Не принимает бизнес-решений", ORANGE),
        ("4. Database", "SQLite: таблицы, ключи, ограничения, индексы и хранение истории", "Не содержит UI-логику", NAVY),
    ]
    y = 200
    for idx, (title, responsibility, forbidden, color) in enumerate(layers):
        d.rounded_rectangle((190, y, 1510, y + 175), radius=14, fill=PALE, outline=color, width=4)
        d.rectangle((190, y, 205, y + 175), fill=color)
        d.text((240, y + 22), title, font=font(31, True), fill=color)
        d.text((240, y + 75), responsibility, font=font(24), fill=BLACK)
        d.text((240, y + 120), "Запрет: " + forbidden, font=font(23), fill=GRAY)
        if idx < len(layers) - 1:
            arrow(d, (850, y + 177), (850, y + 218), fill=BLUE, width=4)
        y += 225
    d.text((190, 1115), "Поперечные компоненты: конфигурация, журналирование, обработка ошибок, миграции и тесты.", font=font(24), fill=GRAY)
    path = DOCS / "architecture" / "architecture.png"
    im.save(path, quality=95)
    return path


def components():
    im = Image.new("RGB", (1800, 1260), WHITE)
    d = ImageDraw.Draw(im)
    d.text((70, 38), "Диаграмма компонентов", font=font(46, True), fill=NAVY)
    groups = [
        (80, 130, 1720, 340, "Controller", LIGHT),
        (80, 390, 1720, 650, "Service", "#EDF7F2"),
        (80, 700, 1720, 910, "Repository", "#FBF4EB"),
        (80, 960, 1720, 1170, "Database", "#EEF1F4"),
    ]
    for x1, y1, x2, y2, title, color in groups:
        d.rectangle((x1, y1, x2, y2), fill=color, outline=LINE, width=3)
        d.text((x1 + 20, y1 + 12), title, font=font(25, True), fill=NAVY)
    top = [(150, "AuthController"), (570, "RequestController"), (990, "CatalogController"), (1370, "UserController")]
    middle = [(110, "AuthService"), (450, "RequestService"), (790, "AssignmentService"), (1130, "CommentService"), (1450, "UserService")]
    repos = [(150, "UserRepository"), (570, "RequestRepository"), (990, "CatalogRepository"), (1370, "HistoryRepository")]
    for x, label in top:
        box = (x, 215, x + 280, 305)
        d.rounded_rectangle(box, radius=10, fill=WHITE, outline=BLUE, width=3)
        centered(d, box, label, font(22, True), NAVY)
    for x, label in middle:
        box = (x, 490, x + 260, 590)
        d.rounded_rectangle(box, radius=10, fill=WHITE, outline=GREEN, width=3)
        centered(d, box, label, font(21, True), GREEN)
    for x, label in repos:
        box = (x, 780, x + 280, 870)
        d.rounded_rectangle(box, radius=10, fill=WHITE, outline=ORANGE, width=3)
        centered(d, box, label, font(21, True), ORANGE)
    tables = [(100, "Roles / Users"), (390, "Requests"), (680, "Statuses / Categories"), (1020, "Comments"), (1350, "RequestHistory")]
    for x, label in tables:
        box = (x, 1030, x + 270, 1120)
        d.rectangle(box, fill=WHITE, outline=NAVY, width=3)
        centered(d, box, label, font(22, True), NAVY)
    # Основной поток вызовов.
    for x in (710,):
        arrow(d, (x, 340), (x, 485), fill=BLUE)
        arrow(d, (x, 650), (x, 775), fill=GREEN)
        arrow(d, (x, 910), (x, 1025), fill=ORANGE)
    d.text((100, 1195), "RequestService координирует репозитории; контроллеры не обращаются к базе напрямую.", font=font(24), fill=GRAY)
    path = DOCS / "architecture" / "components.png"
    im.save(path, quality=95)
    return path


def er():
    im = Image.new("RGB", (2000, 1450), WHITE)
    d = ImageDraw.Draw(im)
    d.text((70, 35), "ER-диаграмма базы данных RequestSystem", font=font(46, True), fill=NAVY)
    d.text((70, 100), "Первичные ключи — PK, внешние ключи — FK; связи показаны как 1:M", font=font(25), fill=GRAY)
    entities = {
        "Roles": (80, 210, 430, 430, ["PK id", "name UNIQUE NOT NULL", "description"]),
        "Users": (570, 180, 1010, 500, ["PK id", "FK role_id", "full_name", "login UNIQUE", "password_hash", "is_active"]),
        "Statuses": (1450, 180, 1880, 390, ["PK id", "name UNIQUE NOT NULL"]),
        "Categories": (1450, 480, 1880, 710, ["PK id", "name UNIQUE NOT NULL", "description"]),
        "Requests": (570, 650, 1080, 1120, ["PK id", "number UNIQUE", "title / description", "FK applicant_id", "FK executor_id NULL", "FK category_id", "FK status_id", "created_at / updated_at", "closed_at NULL"]),
        "Comments": (80, 850, 450, 1170, ["PK id", "FK request_id", "FK author_id", "body NOT NULL", "created_at"]),
        "RequestHistory": (1330, 900, 1900, 1320, ["PK id", "FK request_id", "FK old_status_id NULL", "FK new_status_id", "FK old_executor_id NULL", "FK new_executor_id NULL", "FK changed_by", "changed_at"]),
    }
    # Связи проводим до блоков, чтобы они не пересекали текст.
    relations = [
        ((430, 320), (570, 320), "1", "M"),
        ((800, 500), (800, 650), "1", "M"),
        ((1080, 770), (1450, 590), "M", "1"),
        ((1010, 410), (1330, 1000), "1", "M"),
        ((570, 880), (450, 1000), "1", "M"),
        ((570, 420), (300, 850), "1", "M"),
        ((1080, 930), (1330, 1080), "1", "M"),
        ((1450, 390), (1600, 900), "1", "M"),
    ]
    for start, end, c1, c2 in relations:
        d.line((start, end), fill=LINE, width=4)
        if c1:
            d.text((start[0] + 8, start[1] - 32), c1, font=font(23, True), fill=BLUE)
            d.text((end[0] - 28, end[1] - 32), c2, font=font(23, True), fill=BLUE)
    for name, (x1, y1, x2, y2, fields) in entities.items():
        d.rectangle((x1, y1, x2, y2), fill=PALE, outline=NAVY, width=3)
        d.rectangle((x1, y1, x2, y1 + 54), fill=NAVY)
        d.text((x1 + 16, y1 + 11), name, font=font(27, True), fill=WHITE)
        y = y1 + 70
        for field in fields:
            d.text((x1 + 18, y), field, font=font(21), fill=BLACK)
            y += 36
    d.text((80, 1360), "Ограничения: Requests.applicant_id ≠ NULL; исполнитель и дата закрытия допускают NULL; история сохраняется отдельными строками.", font=font(23), fill=GRAY)
    path = DOCS / "database" / "er_diagram.png"
    im.save(path, quality=95)
    return path


if __name__ == "__main__":
    for generated in (use_case(), architecture(), components(), er()):
        print(generated.relative_to(ROOT))
