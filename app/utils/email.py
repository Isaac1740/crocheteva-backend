import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(to_email, subject, body):

    try:

        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "subject": subject,
            "html": f"<pre>{body}</pre>"
        })

        print(f"EMAIL SENT TO: {to_email}")
        print("RESEND RESPONSE:", response)

    except Exception as e:

        print("EMAIL ERROR:", str(e))
        raise