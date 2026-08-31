import resend

from django.conf import settings


class EmailService:
    """
    Handles transactional emails through Resend.
    """

    @staticmethod
    def send_employee_invitation(
        recipient_email,
        employee_name,
        verification_token,
    ):
        """
        Send an employee account activation email.
        """

        activation_url = (
            f"{settings.FRONTEND_URL}"
            f"/activate-account?token={verification_token}"
        )

        resend.api_key = settings.RESEND_API_KEY

        response = resend.Emails.send(
            {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [recipient_email],
                "subject": "Activate your EMS employee account",
                "html": f"""
                    <h2>Welcome to EMS</h2>

                    <p>Hello {employee_name},</p>

                    <p>
                        Your employee account has been created.
                        Please activate your account and set your
                        password using the button below.
                    </p>

                    <p>
                        <a href="{activation_url}">
                            Activate Account
                        </a>
                    </p>

                    <p>
                        This activation link is valid for 24 hours.
                    </p>

                    <p>
                        If you did not expect this email,
                        you can safely ignore it.
                    </p>
                """,
            }
        )

        return response