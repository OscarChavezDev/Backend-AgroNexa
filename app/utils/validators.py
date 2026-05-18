import re


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))


def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\d{9,15}$", phone))


def required_fields(data: dict, fields: list) -> list:
    return [f for f in fields if not data.get(f)]
