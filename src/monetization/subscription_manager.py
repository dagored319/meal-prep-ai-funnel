"""Manage subscription lifecycle and user status."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..shared.database import Database
from ..shared.logger import log


class SubscriptionManager:
    """Manage subscription status and lifecycle."""

    def __init__(self, db: Database):
        self.db = db

    def activate_subscription(
        self,
        email: str,
        subscription_id: Optional[str] = None,
        payment_method: str = 'stripe'
    ) -> Dict[str, Any]:
        """
        Activate a premium subscription for a user.

        Args:
            email: User's email
            subscription_id: Payment processor subscription ID
            payment_method: Payment method used (stripe, paypal, manual)

        Returns:
            Dictionary with activation status
        """
        try:
            # Get or create lead
            lead = self.db.get_lead(email)

            if not lead:
                lead_id = self.db.save_lead(email=email)
            else:
                lead_id = lead['id']

            # Update subscription status
            self.db.update_subscription(lead_id, 'premium')

            log.info(f"Activated premium subscription for {email}")

            return {
                'success': True,
                'lead_id': lead_id,
                'status': 'premium',
                'activated_at': datetime.now().isoformat()
            }

        except Exception as e:
            log.error(f"Error activating subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def cancel_subscription(self, email: str) -> Dict[str, Any]:
        """Cancel a subscription."""
        try:
            lead = self.db.get_lead(email)

            if not lead:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Update to free tier
            self.db.update_subscription(lead['id'], 'free')

            log.info(f"Cancelled subscription for {email}")

            return {
                'success': True,
                'status': 'free'
            }

        except Exception as e:
            log.error(f"Error cancelling subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_premium_subscribers(self) -> List[Dict[str, Any]]:
        """Get all active premium subscribers."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM leads WHERE subscription_status = 'premium'"
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_subscription_status(self, email: str) -> Dict[str, Any]:
        """Get subscription status for a user."""
        lead = self.db.get_lead(email)

        if not lead:
            return {
                'status': 'not_found',
                'email': email
            }

        return {
            'status': lead['subscription_status'],
            'email': email,
            'member_since': lead.get('subscription_start'),
            'preferences': lead.get('preferences')
        }

    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Total leads
            cursor.execute("SELECT COUNT(*) as count FROM leads")
            total_leads = cursor.fetchone()['count']

            # Free users
            cursor.execute(
                "SELECT COUNT(*) as count FROM leads WHERE subscription_status = 'free'"
            )
            free_users = cursor.fetchone()['count']

            # Premium users
            cursor.execute(
                "SELECT COUNT(*) as count FROM leads WHERE subscription_status = 'premium'"
            )
            premium_users = cursor.fetchone()['count']

            # Conversion rate
            conversion_rate = (premium_users / total_leads * 100) if total_leads > 0 else 0

            # Recent signups (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) as count FROM leads WHERE created_at >= ?",
                (week_ago,)
            )
            recent_signups = cursor.fetchone()['count']

            return {
                'total_leads': total_leads,
                'free_users': free_users,
                'premium_users': premium_users,
                'conversion_rate': round(conversion_rate, 2),
                'recent_signups': recent_signups
            }

    def get_churned_users(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get users who were premium but cancelled.

        Args:
            days: Look back period in days

        Returns:
            List of churned users
        """
        # This would require tracking cancellation dates in the database
        # For now, returning empty list
        # In production, add a 'cancelled_at' field to track this

        log.warning("Churn tracking not fully implemented")
        return []

    def send_retention_email(self, email: str) -> bool:
        """
        Send retention email to at-risk users.

        This could be triggered for:
        - Users who haven't logged in recently
        - Users who downgraded from premium
        - Users approaching subscription renewal
        """
        # Placeholder for retention email logic
        log.info(f"Retention email would be sent to: {email}")
        return True
