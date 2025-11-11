"""Send emails to leads with meal plans."""
from typing import Dict, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..shared.logger import log


class EmailSender:
    """Send emails using SendGrid or SMTP."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'sendgrid')

        if self.provider == 'sendgrid':
            self.client = SendGridAPIClient(config.get('sendgrid_api_key'))

        self.from_email = config.get('from_email')
        self.from_name = config.get('from_name')

    def send_meal_plan(
        self,
        to_email: str,
        user_name: Optional[str],
        meal_plan: Dict[str, Any],
        plan_type: str = 'free'
    ) -> bool:
        """
        Send a meal plan to a user.

        Args:
            to_email: Recipient email address
            user_name: Recipient name (optional)
            meal_plan: The generated meal plan
            plan_type: 'free' or 'premium'

        Returns:
            True if sent successfully, False otherwise
        """
        subject = self._get_subject(plan_type)
        html_content = self._generate_email_html(user_name, meal_plan, plan_type)
        text_content = meal_plan['meal_plan']

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None
    ) -> bool:
        """Send an email."""
        try:
            if self.provider == 'sendgrid':
                return self._send_via_sendgrid(to_email, subject, html_content, text_content)
            else:
                return self._send_via_smtp(to_email, subject, html_content, text_content)

        except Exception as e:
            log.error(f"Error sending email: {e}")
            return False

    def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str]
    ) -> bool:
        """Send email via SendGrid."""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_content or html_content),
                html_content=Content("text/html", html_content)
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                log.info(f"Email sent successfully to {to_email}")
                return True
            else:
                log.error(f"Failed to send email: {response.status_code}")
                return False

        except Exception as e:
            log.error(f"SendGrid error: {e}")
            return False

    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str]
    ) -> bool:
        """Send email via SMTP."""
        # This is a basic SMTP implementation
        # You'll need to configure SMTP settings in config
        smtp_config = self.config.get('smtp', {})

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Send via SMTP
            with smtplib.SMTP(smtp_config.get('host', 'smtp.gmail.com'),
                            smtp_config.get('port', 587)) as server:
                server.starttls()
                server.login(smtp_config.get('username'), smtp_config.get('password'))
                server.send_message(msg)

            log.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            log.error(f"SMTP error: {e}")
            return False

    def _get_subject(self, plan_type: str) -> str:
        """Get email subject based on plan type."""
        if plan_type == 'premium':
            return "Your Weekly Personalized Meal Plan is Here!"
        else:
            return "Your Free 3-Day Meal Plan is Ready!"

    def _generate_email_html(
        self,
        user_name: Optional[str],
        meal_plan: Dict[str, Any],
        plan_type: str
    ) -> str:
        """Generate HTML email content."""
        greeting = f"Hi {user_name}!" if user_name else "Hi there!"

        if plan_type == 'free':
            intro = """
            <p>Congratulations! Your personalized 3-day meal plan is ready.</p>
            <p>I've created this plan based on your specific goals and preferences.
            It includes all the recipes, ingredients, and prep tips you need to get started.</p>
            """

            footer = """
            <div style="background-color: #f0f8ff; padding: 20px; margin-top: 30px; border-radius: 10px;">
                <h3>Want More?</h3>
                <p>Love your plan? Upgrade to our Premium Plan for just $19/month and get:</p>
                <ul>
                    <li>Fresh 7-day plans delivered every Friday</li>
                    <li>Complete shopping lists organized by store section</li>
                    <li>Meal prep schedules to save you time</li>
                    <li>Ongoing adjustments based on your feedback</li>
                </ul>
                <a href="YOUR_UPGRADE_LINK" style="display: inline-block; background-color: #4CAF50; color: white;
                   padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                    Upgrade to Premium
                </a>
            </div>
            """
        else:
            intro = """
            <p>Your weekly personalized meal plan has arrived!</p>
            <p>Here's your fresh 7-day plan, customized to your goals and preferences.</p>
            """
            footer = ""

        # Convert meal plan markdown to HTML (simple conversion)
        meal_plan_html = meal_plan['meal_plan'].replace('\n', '<br>')
        meal_plan_html = meal_plan_html.replace('##', '</h2><h2>').replace('**', '<strong>').replace('**', '</strong>')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                ul {{ padding-left: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{greeting}</h1>
                {intro}

                <div style="margin-top: 30px;">
                    {meal_plan_html}
                </div>

                {footer}

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    <p>Questions? Just reply to this email - I'm here to help!</p>
                    <p>- {self.from_name}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_upsell_email(self, to_email: str, user_name: Optional[str]) -> bool:
        """Send a follow-up upsell email."""
        subject = "Ready to take your meal prep to the next level?"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Hi {user_name or 'there'}!</h2>

                <p>How's your 3-day meal plan working out?</p>

                <p>If you're enjoying the structure and convenience, I have something special for you...</p>

                <h3>Never Run Out of Meal Ideas Again</h3>

                <p>With our Premium Plan ($19/month), you'll get:</p>
                <ul>
                    <li><strong>Weekly 7-day plans</strong> delivered every Friday</li>
                    <li><strong>Complete shopping lists</strong> organized by store section</li>
                    <li><strong>Meal prep schedules</strong> to maximize your time</li>
                    <li><strong>Unlimited adjustments</strong> based on your feedback</li>
                </ul>

                <p>That's just $2.71 per day of personalized nutrition planning!</p>

                <a href="YOUR_UPGRADE_LINK" style="display: inline-block; background-color: #4CAF50;
                   color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                    Start My Premium Plan
                </a>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    Not ready yet? No problem! Keep enjoying your free plan and upgrade whenever you're ready.
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)
