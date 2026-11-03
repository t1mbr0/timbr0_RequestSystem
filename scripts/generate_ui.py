from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ui"
REGULAR = os.environ.get("DAIMON_CJK_FONT_REGULAR", "C:/Windows/Fonts/arial.ttf")
BOLD = os.environ.get("DAIMON_CJK_FONT_BOLD", "C:/Windows/Fonts/arialbd.ttf")
NAVY = "#18324B"
BLUE = "#2D6FA3"
BLUE_DARK = "#245B87"
BG = "#F4F7FA"
WHITE = "#FFFFFF"
TEXT = "#1F2D38"
MUTED = "#687986"
BORDER = "#D5DFE7"
GREEN = "#24745E"
GREEN_BG = "#E6F4EE"
ORANGE = "#A9601C"
ORANGE_BG = "#FFF1DF"
GRAY_BG = "#E9EEF2"
RED = "#B44242"
RED_BG = "#FCECEC"


def f(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def text(d, xy, value, size=20, color=TEXT, bold=False):
    d.text(xy, value, font=f(size, bold), fill=color)


def wrap(d, xy, value, width, size=20, color=TEXT, bold=False, line_gap=8):
    words = value.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if d.textbbox((0, 0), candidate, font=f(size, bold))[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    x, y = xy
    for line in lines:
        text(d, (x, y), line, size, color, bold)
        y += size + line_gap
    return y


def button(d, box, label, primary=True, danger=False):
    color = RED if danger else (BLUE if primary else WHITE)
    outline = RED if danger else (BLUE if primary else BORDER)
    d.rounded_rectangle(box, radius=8, fill=color, outline=outline, width=2)
    x1, y1, x2, y2 = box
    bbox = d.textbbox((0, 0), label, font=f(19, True))
    text(d, ((x1 + x2 - bbox[2]) / 2, (y1 + y2 - 24) / 2), label, 19, WHITE if primary or danger else TEXT, True)


def input_box(d, box, label, value="", error=None):
    x1, y1, x2, y2 = box
    text(d, (x1, y1 - 32), label, 18, TEXT, True)
    d.rounded_rectangle(box, radius=7, fill=WHITE, outline=RED if error else BORDER, width=2)
    text(d, (x1 + 15, y1 + 13), value, 19, TEXT if value else MUTED)
    if error:
        text(d, (x1, y2 + 10), error, 16, RED)


def badge(d, xy, label, kind="new"):
    colors = {
        "new": (GRAY_BG, MUTED),
        "work": (ORANGE_BG, ORANGE),
        "done": (GREEN_BG, GREEN),
        "closed": ("#E8E9F4", "#55578A"),
    }
    bg, fg = colors[kind]
    x, y = xy
    width = d.textbbox((0, 0), label, font=f(16, True))[2] + 28
    d.rounded_rectangle((x, y, x + width, y + 32), radius=16, fill=bg)
    text(d, (x + 14, y + 6), label, 16, fg, True)


def base(title_value, subtitle=""):
    im = Image.new("RGB", (1440, 960), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 220, 960), fill=NAVY)
    text(d, (28, 34), "RequestSystem", 27, WHITE, True)
    text(d, (28, 76), "учёт обращений", 16, "#BCD0DF")
    nav = [(170, "Заявки"), (230, "Создать заявку"), (290, "Пользователи"), (350, "Справочники")]
    for y, label in nav:
        if label == "Заявки":
            d.rounded_rectangle((14, y - 12, 206, y + 35), radius=8, fill="#2A4A65")
        text(d, (34, y), label, 19, WHITE if label == "Заявки" else "#D6E2EB", label == "Заявки")
    text(d, (28, 890), "Гатин Тимофей", 17, WHITE, True)
    text(d, (28, 918), "Роль: оператор", 15, "#BCD0DF")
    d.rectangle((220, 0, 1440, 78), fill=WHITE)
    text(d, (260, 24), title_value, 27, NAVY, True)
    if subtitle:
        text(d, (260, 94), subtitle, 18, MUTED)
    text(d, (1170, 26), "Выход", 18, BLUE, True)
    return im, d


def login():
    im = Image.new("RGB", (1440, 960), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1440, 120), fill=NAVY)
    text(d, (70, 38), "RequestSystem", 40, WHITE, True)
    text(d, (1040, 50), "Система учёта заявок", 22, "#D6E2EB")
    d.rounded_rectangle((450, 200, 990, 790), radius=16, fill=WHITE, outline=BORDER, width=2)
    text(d, (510, 250), "Вход в систему", 34, NAVY, True)
    text(d, (510, 305), "Используйте свою учётную запись", 19, MUTED)
    input_box(d, (510, 385, 930, 440), "Логин", "timbr0")
    input_box(d, (510, 510, 930, 565), "Пароль", "••••••••••")
    d.rounded_rectangle((510, 600, 930, 657), radius=7, fill=RED_BG)
    text(d, (530, 616), "Неверный логин или пароль", 18, RED)
    button(d, (510, 690, 930, 748), "Войти")
    text(d, (510, 815), "Доступ предоставляется согласно роли пользователя.", 18, MUTED)
    return im


def request_row(d, y, number, title_value, category, status, kind, executor):
    d.line((260, y + 74, 1370, y + 74), fill=BORDER, width=2)
    text(d, (280, y + 18), number, 18, BLUE, True)
    text(d, (480, y + 18), title_value, 18, TEXT)
    text(d, (805, y + 18), category, 17, MUTED)
    badge(d, (1010, y + 14), status, kind)
    text(d, (1190, y + 18), executor, 17, TEXT)


def requests_list(empty=False):
    im, d = base("Заявки", "Поиск, фильтрация и контроль выполнения обращений")
    button(d, (1150, 100, 1370, 154), "+ Создать заявку")
    d.rounded_rectangle((260, 180, 1370, 270), radius=10, fill=WHITE, outline=BORDER, width=2)
    input_box(d, (285, 213, 690, 258), "", "Поиск по номеру или теме")
    input_box(d, (715, 213, 990, 258), "", "Статус: все")
    input_box(d, (1015, 213, 1345, 258), "", "Категория: все")
    d.rounded_rectangle((260, 295, 1370, 820), radius=10, fill=WHITE, outline=BORDER, width=2)
    d.rectangle((261, 296, 1369, 360), fill="#EDF2F6")
    for x, label in [(280, "Номер"), (480, "Тема"), (805, "Категория"), (1010, "Статус"), (1190, "Исполнитель")]:
        text(d, (x, 316), label, 17, MUTED, True)
    if not empty:
        request_row(d, 360, "REQ-2026-00001", "Не работает принтер", "Оборудование", "В работе", "work", "И. Петров")
        request_row(d, 434, "REQ-2026-00002", "Ошибка входа в 1С", "ПО", "Новая", "new", "Не назначен")
        request_row(d, 508, "REQ-2026-00003", "Настроить VPN", "Сеть", "Выполнена", "done", "А. Смирнов")
        request_row(d, 582, "REQ-2026-00004", "Заменить клавиатуру", "Оборудование", "Закрыта", "closed", "И. Петров")
        request_row(d, 656, "REQ-2026-00005", "Предоставить доступ", "Доступ", "В работе", "work", "А. Смирнов")
        text(d, (280, 770), "Показано 5 из 5 заявок", 17, MUTED)
    else:
        text(d, (665, 455), "Ничего не найдено", 30, NAVY, True)
        wrap(d, (515, 510), "Измените условия поиска или сбросьте выбранные фильтры.", 600, 20, MUTED)
        button(d, (630, 590, 1010, 650), "Сбросить фильтры", primary=False)
    return im


def create_request():
    im, d = base("Создание заявки", "Поля, отмеченные звёздочкой, обязательны для заполнения")
    d.rounded_rectangle((260, 145, 1050, 855), radius=10, fill=WHITE, outline=BORDER, width=2)
    input_box(d, (300, 205, 1010, 263), "Тема *", "Не работает принтер")
    input_box(d, (300, 335, 650, 393), "Категория *", "Оборудование")
    input_box(d, (680, 335, 1010, 393), "Заявитель *", "Гатин Тимофей")
    input_box(d, (300, 465, 1010, 620), "Описание *", "Принтер не печатает документы.", "Добавьте сведения о сообщении об ошибке и модели устройства")
    text(d, (300, 682), "После сохранения заявка получит номер и статус «Новая».", 17, MUTED)
    button(d, (300, 755, 520, 815), "Отмена", primary=False)
    button(d, (790, 755, 1010, 815), "Создать заявку")
    d.rounded_rectangle((1090, 145, 1370, 420), radius=10, fill="#EDF4F8")
    text(d, (1120, 175), "Подсказка", 22, NAVY, True)
    wrap(d, (1120, 225), "Укажите, что произошло, когда и на каком устройстве. Это ускорит назначение и выполнение.", 220, 18, MUTED)
    return im


def details():
    im, d = base("Карточка заявки")
    text(d, (260, 102), "REQ-2026-00001", 25, BLUE, True)
    badge(d, (500, 99), "В работе", "work")
    button(d, (1060, 95, 1370, 150), "Редактировать", primary=False)
    d.rounded_rectangle((260, 180, 930, 590), radius=10, fill=WHITE, outline=BORDER, width=2)
    text(d, (290, 210), "Не работает принтер", 29, NAVY, True)
    wrap(d, (290, 265), "При отправке документа на печать появляется ошибка. Проблема повторяется на двух компьютерах отдела.", 590, 19, TEXT)
    fields = [(290, 390, "Заявитель", "Гатин Тимофей"), (580, 390, "Категория", "Оборудование"), (290, 480, "Создана", "03.11.2026, 10:15"), (580, 480, "Исполнитель", "Иван Петров")]
    for x, y, label, value in fields:
        text(d, (x, y), label, 16, MUTED)
        text(d, (x, y + 28), value, 19, TEXT, True)
    d.rounded_rectangle((960, 180, 1370, 590), radius=10, fill=WHITE, outline=BORDER, width=2)
    text(d, (990, 210), "Действия", 22, NAVY, True)
    button(d, (990, 265, 1340, 320), "Изменить статус")
    button(d, (990, 340, 1340, 395), "Назначить исполнителя", primary=False)
    button(d, (990, 415, 1340, 470), "Добавить комментарий", primary=False)
    button(d, (990, 505, 1340, 555), "Удалить", primary=False, danger=True)
    d.rounded_rectangle((260, 620, 1370, 885), radius=10, fill=WHITE, outline=BORDER, width=2)
    text(d, (290, 650), "Хронология", 22, NAVY, True)
    text(d, (290, 705), "03.11.2026, 11:20  •  Иван Петров", 17, MUTED)
    text(d, (290, 738), "Проверяю сетевое подключение и драйвер принтера.", 19, TEXT)
    d.line((290, 785, 1340, 785), fill=BORDER, width=2)
    text(d, (290, 810), "03.11.2026, 10:45  •  Оператор", 17, MUTED)
    text(d, (290, 842), "Статус изменён: «Новая» → «В работе»; назначен Иван Петров.", 19, TEXT)
    return im


def edit_request():
    im, d = base("Редактирование заявки", "REQ-2026-00001 • изменения сохраняются в истории")
    d.rounded_rectangle((260, 145, 1090, 855), radius=10, fill=WHITE, outline=BORDER, width=2)
    input_box(d, (300, 205, 1050, 263), "Тема *", "Не работает принтер")
    input_box(d, (300, 335, 650, 393), "Категория *", "Оборудование")
    input_box(d, (680, 335, 1050, 393), "Статус", "В работе")
    input_box(d, (300, 465, 650, 523), "Исполнитель", "Иван Петров")
    input_box(d, (680, 465, 1050, 523), "Заявитель", "Гатин Тимофей")
    input_box(d, (300, 595, 1050, 725), "Описание *", "Принтер HP LaserJet M1132 выдаёт ошибку печати на двух компьютерах отдела.")
    button(d, (300, 770, 520, 825), "Отмена", primary=False)
    button(d, (800, 770, 1050, 825), "Сохранить")
    d.rounded_rectangle((1120, 145, 1370, 380), radius=10, fill=ORANGE_BG)
    text(d, (1145, 175), "Важно", 21, ORANGE, True)
    wrap(d, (1145, 225), "Недопустимые переходы статусов будут отклонены. Закрытая заявка недоступна для редактирования.", 200, 17, ORANGE)
    return im


def delete_confirm():
    im = details()
    d = ImageDraw.Draw(im)
    overlay = Image.new("RGBA", im.size, (14, 28, 40, 125))
    im = Image.alpha_composite(im.convert("RGBA"), overlay)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((420, 265, 1020, 665), radius=14, fill=WHITE)
    text(d, (470, 315), "Удалить заявку?", 32, NAVY, True)
    wrap(d, (470, 380), "REQ-2026-00001 «Не работает принтер» будет удалена. Это действие нельзя отменить.", 500, 21, TEXT)
    d.rounded_rectangle((470, 475, 970, 530), radius=7, fill=RED_BG)
    text(d, (490, 491), "История и комментарии также будут удалены.", 18, RED)
    button(d, (470, 575, 700, 630), "Отмена", primary=False)
    button(d, (730, 575, 970, 630), "Удалить заявку", danger=True)
    return im.convert("RGB")


def make_pdf(paths):
    out = OUT / "prototype.pdf"
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(str(out), pagesize=(page_w, page_h))
    c.setTitle("Прототип интерфейса RequestSystem — Гатин Тимофей")
    c.setAuthor("Гатин Тимофей")
    for path in paths:
        img = Image.open(path)
        ratio = min((page_w - 24) / img.width, (page_h - 24) / img.height)
        w, h = img.width * ratio, img.height * ratio
        c.drawImage(ImageReader(img), (page_w - w) / 2, (page_h - h) / 2, width=w, height=h)
        c.showPage()
    c.save()
    return out


if __name__ == "__main__":
    screens = [
        ("01_login.png", login),
        ("02_requests_list.png", lambda: requests_list(False)),
        ("03_create_request.png", create_request),
        ("04_request_details.png", details),
        ("05_edit_request.png", edit_request),
        ("06_delete_confirmation.png", delete_confirm),
        ("07_empty_state.png", lambda: requests_list(True)),
    ]
    paths = []
    for name, factory in screens:
        path = OUT / name
        factory().save(path, quality=95)
        paths.append(path)
        print(path.relative_to(ROOT))
    print(make_pdf(paths).relative_to(ROOT))
