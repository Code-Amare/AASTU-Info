# utils/emails.py

from django.conf import settings

from .send_email import send_email
from console.models import PlatformSettings

FRONTEND_URL = settings.FRONTEND_URL

_BRAND = "#4F46E5"
_BRAND_DARK = "#3730A3"
_BG = "#F4F5F7"
_TEXT = "#1F2937"
_MUTED = "#6B7280"


def _site_name() -> str:
    return PlatformSettings.get_solo().site_name


def _icon_block(kind: str) -> str:
    if kind == "danger":
        color = "#DC2626"
        bg = "#FEE2E2"
        svg = f"""
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7v6c0 5.25 3.75 9.75 10 11 6.25-1.25 10-5.75 10-11V7l-10-5z" fill="{color}"/>
          <rect x="11" y="7" width="2" height="7" rx="1" fill="#ffffff"/>
          <circle cx="12" cy="16.5" r="1.2" fill="#ffffff"/>
        </svg>
        """
    elif kind == "success":
        color = "#16A34A"
        bg = "#DCFCE7"
        svg = f"""
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="{color}"/>
          <path d="M7 12.5l3 3 7-7" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        """
    else:
        color = "#D97706"
        bg = "#FEF3C7"
        svg = f"""
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L1 21h22L12 2z" fill="{color}"/>
          <rect x="11" y="9" width="2" height="6" rx="1" fill="#ffffff"/>
          <circle cx="12" cy="17.5" r="1.1" fill="#ffffff"/>
        </svg>
        """
    return f"""
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 18px;">
          <tr>
            <td style="background:{bg}; border-radius:50%; width:52px; height:52px; text-align:center; vertical-align:middle;">
              <div style="padding-top:12px;">{svg}</div>
            </td>
          </tr>
        </table>
    """


def _wrapper(inner_html: str) -> str:
    site_name = _site_name()
    return f"""
    <body style="margin:0; padding:0; background-color:{_BG}; font-family:'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{_BG}; padding:40px 16px;">
        <tr>
          <td align="center">
            <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:14px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,0.06);">

              <tr>
                <td style="background:{_BRAND}; padding:28px 32px;">
                  <span style="font-size:20px; font-weight:700; color:#ffffff; letter-spacing:0.5px;">{site_name}</span>
                </td>
              </tr>

              <tr>
                <td style="padding:36px 32px 24px;">
                  {inner_html}
                </td>
              </tr>

              <tr>
                <td style="padding:20px 32px; background:#FAFAFB; border-top:1px solid #EEEEEE;">
                  <p style="margin:0; font-size:12px; color:{_MUTED}; line-height:1.6;">
                    If you didn't request this, you can safely ignore this email.<br>
                    &copy; {site_name}. All rights reserved.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    """


def _heading_block(greeting_name: str, heading: str, intro: str = "") -> str:
    intro_html = (
        f'<p style="margin:0 0 20px; font-size:14px; color:{_MUTED}; line-height:1.6;">{intro}</p>'
        if intro
        else ""
    )
    return f"""
        <p style="margin:0 0 4px; font-size:14px; color:{_MUTED};">Hi {greeting_name},</p>
        <h1 style="margin:0 0 16px; font-size:20px; color:{_TEXT}; font-weight:700;">{heading}</h1>
        {intro_html}
    """


def _code_block(code: str) -> str:
    return f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 20px;">
          <tr>
            <td align="center">
              <div style="display:inline-block; background:{_BG}; border:1px dashed {_BRAND}; border-radius:10px; padding:16px 32px;">
                <span style="font-size:30px; font-weight:700; letter-spacing:10px; color:{_BRAND_DARK};">{code}</span>
              </div>
            </td>
          </tr>
        </table>
        <p style="margin:0; font-size:13px; color:{_MUTED}; text-align:center;">This code will expire shortly.</p>
    """


def _button_block(url: str, label: str) -> str:
    return f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 20px;">
          <tr>
            <td align="center">
              <a href="{url}" style="display:inline-block; background:{_BRAND}; color:#ffffff; text-decoration:none; font-size:15px; font-weight:600; padding:14px 32px; border-radius:8px;">
                {label}
              </a>
            </td>
          </tr>
        </table>
        <p style="margin:0 0 4px; font-size:12px; color:{_MUTED}; text-align:center; word-break:break-all;">{url}</p>
        <p style="margin:0; font-size:13px; color:{_MUTED}; text-align:center;">This link will expire shortly.</p>
    """


def send_verification_code_email(user, code: str):
    site_name = _site_name()
    inner = _heading_block(
        greeting_name=user.first_name or user.email,
        heading="Verify your email address",
        intro="Enter this code to confirm it's really you.",
    ) + _code_block(code)

    return send_email(
        to_email=user.email,
        subject=f"Verify your {site_name} email",
        html_content=_wrapper(inner),
        tags=["email-verification"],
    )


def send_login_link_email(user, code: str):
    site_name = _site_name()
    login_url = f"{FRONTEND_URL}/login/email/{code}"
    inner = _heading_block(
        greeting_name=user.first_name or user.email,
        heading="Your login link",
        intro="Click below to securely log in to your account.",
    ) + _button_block(login_url, f"Log in to {site_name}")

    return send_email(
        to_email=user.email,
        subject=f"Your {site_name} login link",
        html_content=_wrapper(inner),
        tags=["login-link"],
    )


def send_login_alert_email(user, request):
    site_name = _site_name()
    ip = request.META.get("REMOTE_ADDR", "unknown")
    user_agent = request.META.get("HTTP_USER_AGENT", "unknown")

    details_table = f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:4px 0 20px; background:{_BG}; border-radius:8px;">
          <tr>
            <td style="padding:14px 18px; font-size:13px; color:{_MUTED}; width:130px;">IP address</td>
            <td style="padding:14px 18px; font-size:13px; color:{_TEXT}; font-weight:600;">{ip}</td>
          </tr>
          <tr>
            <td style="padding:0 18px 14px; font-size:13px; color:{_MUTED};">Device / browser</td>
            <td style="padding:0 18px 14px; font-size:13px; color:{_TEXT}; font-weight:600;">{user_agent}</td>
          </tr>
        </table>
        <p style="margin:0; font-size:13px; color:#B91C1C; font-weight:600;">
          If this wasn't you, reset your password immediately.
        </p>
    """

    inner = (
        _heading_block(
            greeting_name=user.first_name or user.email,
            heading="New login detected",
        )
        + details_table
    )

    return send_email(
        to_email=user.email,
        subject=f"New login to your {site_name} account",
        html_content=_wrapper(inner),
        tags=["login-alert"],
    )


def send_password_reset_link_email(user, code: str):
    site_name = _site_name()
    reset_url = f"{FRONTEND_URL}/password/reset/{code}/"
    inner = _heading_block(
        greeting_name=user.first_name or user.email,
        heading="Reset your password",
        intro="Click below to choose a new password.",
    ) + _button_block(reset_url, "Reset password")

    return send_email(
        to_email=user.email,
        subject=f"Reset your {site_name} password",
        html_content=_wrapper(inner),
        tags=["password-reset"],
    )
