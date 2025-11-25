Short checklist to enable SendGrid and verify OTP email delivery

- Create a SendGrid account (https://sendgrid.com) and sign in.
- In SendGrid UI: Settings → API Keys → Create API Key.
  - Name: `multibliz-pos-prod` (or any name)
  - Scope: Restricted → enable `Mail Send` (or Full Access if preferred).
  - Copy the API key immediately (shown only once).
- In SendGrid: Settings → Sender Authentication → verify a sender email (Single Sender) or set up Domain Authentication for production.
- In Render dashboard for your service:
  - Add environment variable `SENDGRID_API_KEY` with the key value (mark secret).
  - Optionally set `DEFAULT_FROM_EMAIL` to your verified sender (e.g. `noreply@yourdomain.com`).
- Redeploy the service (trigger a deploy) so the app installs `sendgrid-django` and picks up env vars.
- Test the forgot-password flow in production:
  - Check Render logs for send activity and absence of network errors.
  - Check the SendGrid dashboard Activity for the API request and delivery status.
  - Confirm the recipient receives the OTP email.
- After successful production verification: ensure no OTP is exposed in UI and remove any temporary debug code (already removed).

If SendGrid isn't an option, consider other transactional providers (Resend, Mailgun, Amazon SES) that provide API-based sending.

Notes:
- Keep the API key secret; do not commit it to git.
- For best deliverability, set up Domain Authentication in SendGrid and use a matching `DEFAULT_FROM_EMAIL`.
