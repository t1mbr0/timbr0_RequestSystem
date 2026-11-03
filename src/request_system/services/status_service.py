"""Правила жизненного цикла заявки, не зависящие от UI и SQL."""
from enum import StrEnum


class Status(StrEnum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    DONE = "Выполнена"
    CLOSED = "Закрыта"


_ALLOWED = {
    (Status.NEW, Status.IN_PROGRESS): {"operator", "admin"},
    (Status.IN_PROGRESS, Status.DONE): {"executor", "admin"},
    (Status.DONE, Status.IN_PROGRESS): {"operator", "admin"},
    (Status.DONE, Status.CLOSED): {"applicant", "admin"},
}


def can_transition(current: Status, new: Status, role: str, *, is_owner: bool = False,
                   is_assigned: bool = False, has_executor: bool = False) -> tuple[bool, str]:
    """Возвращает разрешение перехода и машиночитаемую причину отказа."""
    if current == new:
        return False, "same_status"
    allowed_roles = _ALLOWED.get((current, new))
    if allowed_roles is None:
        return False, "transition_forbidden"
    if role not in allowed_roles:
        return False, "role_forbidden"
    if (current, new) == (Status.NEW, Status.IN_PROGRESS) and not has_executor:
        return False, "executor_required"
    if role == "executor" and not is_assigned:
        return False, "executor_not_assigned"
    if role == "applicant" and not is_owner:
        return False, "not_request_owner"
    return True, "allowed"
