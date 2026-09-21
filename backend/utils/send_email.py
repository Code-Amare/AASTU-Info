from __future__ import annotations

import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional, Sequence, Union

from brevo import Brevo
from brevo.core.api_error import ApiError
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(
    max_workers=getattr(settings, "EMAIL_THREAD_POOL_SIZE", 5),
    thread_name_prefix="brevo-email",
)

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 1.5


def _validate_recipients(recipients: Sequence[str]) -> None:
    if not recipients:
        raise ValueError("At least one recipient email is required")

    for addr in recipients:
        try:
            validate_email(addr)
        except ValidationError:
            raise ValueError(f"Invalid recipient email address: {addr!r}")


def _do_send(
    api_key: str,
    to_emails: Sequence[str],
    subject: str,
    html_content: str,
    sender_name: str,
    sender_email: str,
    reply_to: Optional[str],
    tags: Optional[Sequence[str]],
) -> bool:
    client = Brevo(api_key=api_key)

    to = [SendTransacEmailRequestToItem(email=addr) for addr in to_emails]
    sender = SendTransacEmailRequestSender(
        email=sender_email,
        name=sender_name,
    )

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            client.transactional_emails.send_transac_email(
                to=to,
                sender=sender,
                subject=subject,
                html_content=html_content,
                reply_to={"email": reply_to} if reply_to else None,
                tags=list(tags) if tags else None,
            )
            return True

        except ApiError as exc:
            if exc.status_code in _RETRYABLE_STATUS_CODES and attempt < _MAX_ATTEMPTS:
                wait = _BACKOFF_SECONDS * attempt

                logger.warning(
                    "Brevo send failed (attempt %s/%s, status %s) for %s. "
                    "Retrying in %.1fs",
                    attempt,
                    _MAX_ATTEMPTS,
                    exc.status_code,
                    to_emails,
                    wait,
                )

                time.sleep(wait)
                continue

            logger.error(
                "Brevo send failed permanently for %s: %s",
                to_emails,
                exc,
            )
            return False

        except Exception:
            logger.exception(
                "Unexpected error sending email to %s",
                to_emails,
            )
            return False

    return False


def send_email(
    to_email: Union[str, Sequence[str]],
    subject: str,
    html_content: str,
    sender_name: Optional[str] = None,
    sender_email: Optional[str] = None,
    reply_to: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
) -> Future:
    if not subject:
        raise ValueError("subject is required")

    if not html_content:
        raise ValueError("html_content is required")

    to_emails = [to_email] if isinstance(to_email, str) else list(to_email)
    _validate_recipients(to_emails)

    sender_name = sender_name or getattr(
        settings,
        "DEFAULT_SENDER_NAME",
        None,
    )

    sender_email = sender_email or getattr(
        settings,
        "BREVO_SENDER_EMAIL",
        None,
    )

    api_key = getattr(settings, "BREVO_API_KEY", None)

    if not sender_email:
        raise ValueError(
            "BREVO_SENDER_EMAIL must be set in settings or passed to send_email()"
        )

    if not api_key:
        raise ValueError("BREVO_API_KEY must be set in settings")

    future = _EXECUTOR.submit(
        _do_send,
        api_key,
        to_emails,
        subject,
        html_content,
        sender_name,
        sender_email,
        reply_to,
        tags,
    )

    def _log_unexpected(f: Future) -> None:
        exc = f.exception()
    
        if exc:
            logger.exception(
                "Unhandled exception in email send worker",
                exc_info=exc,
            )

    future.add_done_callback(_log_unexpected)

    return future
