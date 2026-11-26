"""Қолданушыға түсінікті қателер."""


class AppError(Exception):
    """Интерфейсте қауіпсіз көрсетуге болатын қате."""


class ValidationError(AppError):
    """Енгізілген мән талапқа сәйкес емес."""


class AccessError(AppError):
    """Қолданушының әрекетке құқығы жеткіліксіз."""


class NotFoundError(AppError):
    """Жазба табылмады."""


class LoginError(AppError):
    """Жүйеге кіру қатесі."""
