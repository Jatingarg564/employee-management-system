from django.conf import settings

from brevo import Brevo
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)


class EmailService:
    """
    Handles transactional email delivery through Brevo.
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
            f"/activate/{verification_token}"
        )

        client = Brevo(
            api_key=settings.BREVO_API_KEY,
        )

        response = client.transactional_emails.send_transac_email(
            sender=SendTransacEmailRequestSender(
                email=settings.BREVO_SENDER_EMAIL,
                name=settings.BREVO_SENDER_NAME,
            ),
            to=[
                SendTransacEmailRequestToItem(
                    email=recipient_email,
                    name=employee_name,
                )
            ],
            subject="Activate your EMS employee account",
            html_content=f"""
                <html>
                    <body>
                        <h2>Welcome to EMS</h2>

                        <p>
                            Hello {employee_name},
                        </p>

                        <p>
                            Your Employee Management System
                            account has been created.
                        </p>

                        <p>
                            Please activate your account
                            and set your password.
                        </p>

                        <p>
                            <a href="{activation_url}">
                                Activate Account
                            </a>
                        </p>

                        <p>
                            This activation link will expire
                            after the configured verification period.
                        </p>
                    </body>
                </html>
            """,
        )

        return response