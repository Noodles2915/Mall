import random

from django.core.cache import cache


CODE_TTL_SECONDS = 5 * 60
RESEND_INTERVAL_SECONDS = 60


def _code_cache_key(email: str) -> str:
    return f"register_email_code:{email.lower()}"


def _resend_cache_key(email: str) -> str:
    return f"register_email_code_resend_lock:{email.lower()}"


def can_resend_email_code(email: str) -> bool:
    return cache.get(_resend_cache_key(email)) is None


def generate_email_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def store_email_code(email: str, code: str) -> None:
    cache.set(_code_cache_key(email), code, timeout=CODE_TTL_SECONDS)
    cache.set(_resend_cache_key(email), "1", timeout=RESEND_INTERVAL_SECONDS)


def validate_email_code(email: str, code: str) -> tuple[bool, str]:
    cached_code = cache.get(_code_cache_key(email))
    if not cached_code:
        return False, "验证码已过期，请重新获取"
    if str(cached_code) != code.strip():
        return False, "验证码错误"
    return True, "ok"


def consume_email_code(email: str) -> None:
    cache.delete(_code_cache_key(email))
