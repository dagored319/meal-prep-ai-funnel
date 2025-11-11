"""Automated weekly meal plan delivery for premium subscribers."""
from typing import List, Dict, Any
from datetime import datetime
from ..sales_funnel.meal_plan_generator import MealPlanGenerator
from ..sales_funnel.email_sender import EmailSender
from ..shared.database import Database
from ..shared.logger import log
import json


class WeeklyAutomation:
    """Automate weekly meal plan generation and delivery."""

    def __init__(
        self,
        db: Database,
        meal_plan_generator: MealPlanGenerator,
        email_sender: EmailSender
    ):
        self.db = db
        self.meal_plan_generator = meal_plan_generator
        self.email_sender = email_sender

    def send_weekly_plans(self) -> Dict[str, Any]:
        """
        Generate and send weekly meal plans to all premium subscribers.

        This should be run once per week (e.g., every Friday).

        Returns:
            Dictionary with delivery statistics
        """
        log.info("Starting weekly meal plan delivery...")

        # Get all premium subscribers
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM leads WHERE subscription_status = 'premium'"
            )
            subscribers = [dict(row) for row in cursor.fetchall()]

        log.info(f"Found {len(subscribers)} premium subscribers")

        stats = {
            'total_subscribers': len(subscribers),
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'errors': []
        }

        for subscriber in subscribers:
            try:
                # Parse preferences
                preferences = json.loads(subscriber.get('preferences', '{}')) if subscriber.get('preferences') else {}

                # Generate meal plan
                log.info(f"Generating plan for {subscriber['email']}")
                meal_plan = self.meal_plan_generator.generate_premium_plan(preferences)

                # Save to database
                plan_id = self.db.save_meal_plan(
                    lead_id=subscriber['id'],
                    plan_type='premium',
                    plan_data=meal_plan
                )

                # Send email
                sent = self.email_sender.send_meal_plan(
                    to_email=subscriber['email'],
                    user_name=subscriber.get('name'),
                    meal_plan=meal_plan,
                    plan_type='premium'
                )

                if sent:
                    self.db.mark_plan_sent(plan_id)
                    stats['successful_deliveries'] += 1
                    log.info(f"Successfully sent plan to {subscriber['email']}")
                else:
                    stats['failed_deliveries'] += 1
                    stats['errors'].append({
                        'email': subscriber['email'],
                        'error': 'Email send failed'
                    })

            except Exception as e:
                log.error(f"Error processing {subscriber['email']}: {e}")
                stats['failed_deliveries'] += 1
                stats['errors'].append({
                    'email': subscriber['email'],
                    'error': str(e)
                })

        log.info(
            f"Weekly delivery complete. "
            f"Success: {stats['successful_deliveries']}, "
            f"Failed: {stats['failed_deliveries']}"
        )

        return stats

    def send_plan_to_user(self, email: str) -> Dict[str, Any]:
        """
        Send a weekly plan to a specific user.

        Args:
            email: User's email address

        Returns:
            Dictionary with delivery status
        """
        try:
            # Get user
            lead = self.db.get_lead(email)

            if not lead:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            if lead['subscription_status'] != 'premium':
                return {
                    'success': False,
                    'error': 'User is not a premium subscriber'
                }

            # Parse preferences
            preferences = json.loads(lead.get('preferences', '{}')) if lead.get('preferences') else {}

            # Generate meal plan
            meal_plan = self.meal_plan_generator.generate_premium_plan(preferences)

            # Save to database
            plan_id = self.db.save_meal_plan(
                lead_id=lead['id'],
                plan_type='premium',
                plan_data=meal_plan
            )

            # Send email
            sent = self.email_sender.send_meal_plan(
                to_email=email,
                user_name=lead.get('name'),
                meal_plan=meal_plan,
                plan_type='premium'
            )

            if sent:
                self.db.mark_plan_sent(plan_id)

            return {
                'success': sent,
                'plan_id': plan_id
            }

        except Exception as e:
            log.error(f"Error sending plan to {email}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_delivery_history(self, email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get meal plan delivery history for a user.

        Args:
            email: User's email
            limit: Maximum number of records to return

        Returns:
            List of meal plan deliveries
        """
        lead = self.db.get_lead(email)

        if not lead:
            return []

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM meal_plans
                WHERE lead_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (lead['id'], limit)
            )

            plans = []
            for row in cursor.fetchall():
                plan_dict = dict(row)
                # Parse JSON plan_data
                plan_dict['plan_data'] = json.loads(plan_dict['plan_data'])
                plans.append(plan_dict)

            return plans

    def get_next_delivery_date(self) -> str:
        """Get the next scheduled delivery date (next Friday)."""
        from datetime import datetime, timedelta

        today = datetime.now()
        # Friday is weekday 4
        days_until_friday = (4 - today.weekday()) % 7

        if days_until_friday == 0 and today.hour >= 9:
            # If it's Friday after 9 AM, schedule for next Friday
            days_until_friday = 7

        next_friday = today + timedelta(days=days_until_friday)
        return next_friday.strftime('%Y-%m-%d')


def run_weekly_delivery():
    """Standalone function to run weekly delivery."""
    from ..shared.config import get_config

    config = get_config()
    db = Database(config.database.path)

    meal_plan_generator = MealPlanGenerator(
        api_key=config.openai.api_key,
        model=config.openai.model
    )

    email_sender = EmailSender(config.email.model_dump())

    automation = WeeklyAutomation(db, meal_plan_generator, email_sender)
    return automation.send_weekly_plans()


if __name__ == "__main__":
    result = run_weekly_delivery()

    print("\n" + "="*60)
    print("WEEKLY DELIVERY REPORT")
    print("="*60)
    print(f"Total Subscribers: {result['total_subscribers']}")
    print(f"Successful: {result['successful_deliveries']}")
    print(f"Failed: {result['failed_deliveries']}")

    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error['email']}: {error['error']}")

    print("="*60)
