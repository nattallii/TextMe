import httpx
from src.security.config import settings  # your existing settings

RESEND_API_URL = "https://api.resend.com/emails"

async def send_password_reset_email(to_email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    html = f"""
    <div style="font-family: 'DM Sans', sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 24px; background: #f0f4f5;">
      <div style="background: #ffffff; border-radius: 16px; padding: 40px; box-shadow: 0 4px 24px rgba(29,84,109,0.08);">
        <div style="text-align: center; margin-bottom: 32px;">
          <div style="display: inline-block; background: #5F9598; border-radius: 13px; padding: 12px;">
            <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
              <path d="M10 14C10 12.343 11.343 11 13 11H35C36.657 11 38 12.343 38 14V28C38 29.657 36.657 31 35 31H27L20 37V31H13C11.343 31 10 29.657 10 28V14Z"
                    fill="white" fill-opacity="0.92"/>
              <circle cx="18" cy="21" r="2.2" fill="#1D546D"/>
              <circle cx="24" cy="21" r="2.2" fill="#1D546D"/>
              <circle cx="30" cy="21" r="2.2" fill="#1D546D"/>
            </svg>
          </div>
          <h1 style="margin: 16px 0 4px; font-size: 22px; font-weight: 700; color: #061E29;">
            Reset your password
          </h1>
          <p style="margin: 0; color: #4a7a8a; font-size: 14px;">
            This link expires in <strong>15 minutes</strong>.
          </p>
        </div>

        <a href="{reset_url}"
           style="display: block; text-align: center; background: #1D546D; color: #ffffff;
                  text-decoration: none; padding: 14px 24px; border-radius: 12px;
                  font-size: 15px; font-weight: 600; margin-bottom: 24px;">
          Reset Password
        </a>

        <p style="font-size: 12px; color: #8ab8bc; text-align: center; margin: 0;">
          If you didn't request this, you can safely ignore this email.<br/>
          Or copy this link: <span style="color: #1D546D;">{reset_url}</span>
        </p>
      </div>
      <p style="text-align: center; font-size: 11px; color: #8ab8bc; margin-top: 16px;">
        TextMe © 2025
      </p>
    </div>
    """

    async with httpx.AsyncClient() as client:
        print("RESEND_API_KEY =", settings.RESEND_API_KEY)
        print("HEADERS =", {
            "Authorization": f"Bearer {settings.RESEND_API_KEY}"
        })
        response = await client.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "onboarding@resend.dev",   # e.g. "TextMe <noreply@yourdomain.com>"
                "to": ["nataliashyngelska25@gmail.com"],
                "subject": "Reset your TextMe password",
                "html": html,
            },
            timeout=10.0,
        )
        print(response.status_code)
        print(response.text)
        response.raise_for_status()