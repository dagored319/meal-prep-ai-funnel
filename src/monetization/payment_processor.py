"""Payment processing integration (Stripe)."""
from typing import Dict, Any, Optional
from ..shared.logger import log


class PaymentProcessor:
    """
    Handle payment processing for subscriptions.

    Uses Stripe for payment processing.
    """

    def __init__(self, stripe_api_key: Optional[str] = None):
        self.stripe_api_key = stripe_api_key

        if stripe_api_key:
            try:
                import stripe
                self.stripe = stripe
                stripe.api_key = stripe_api_key
                self.enabled = True
            except ImportError:
                log.warning("Stripe library not installed. Payment processing disabled.")
                self.enabled = False
        else:
            log.warning("Stripe API key not provided. Payment processing disabled.")
            self.enabled = False

    def create_subscription(
        self,
        email: str,
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for subscription.

        Args:
            email: Customer email
            price_id: Stripe price ID for the subscription
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled

        Returns:
            Dictionary with checkout session details
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Payment processing not configured'
            }

        try:
            # Create checkout session
            session = self.stripe.checkout.Session.create(
                customer_email=email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    'trial_period_days': 0,  # No trial, or set to 7 for a free trial
                }
            )

            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url
            }

        except Exception as e:
            log.error(f"Error creating Stripe subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_price(
        self,
        amount: int,
        currency: str = 'usd',
        product_name: str = 'Premium Meal Plan'
    ) -> Dict[str, Any]:
        """
        Create a recurring price in Stripe.

        Args:
            amount: Amount in cents (e.g., 1900 for $19.00)
            currency: Currency code
            product_name: Name of the product

        Returns:
            Dictionary with price details
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Payment processing not configured'
            }

        try:
            # Create product
            product = self.stripe.Product.create(
                name=product_name,
                description='Weekly personalized meal plans delivered to your inbox'
            )

            # Create price
            price = self.stripe.Price.create(
                product=product.id,
                unit_amount=amount,
                currency=currency,
                recurring={'interval': 'month'}
            )

            return {
                'success': True,
                'price_id': price.id,
                'product_id': product.id
            }

        except Exception as e:
            log.error(f"Error creating Stripe price: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def handle_webhook(self, payload: bytes, signature: str, webhook_secret: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.

        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            webhook_secret: Webhook signing secret

        Returns:
            Dictionary with event details
        """
        if not self.enabled:
            return {'success': False, 'error': 'Stripe not configured'}

        try:
            event = self.stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )

            event_type = event['type']
            data = event['data']['object']

            log.info(f"Received Stripe webhook: {event_type}")

            # Handle different event types
            if event_type == 'checkout.session.completed':
                # Payment successful
                return {
                    'success': True,
                    'event': 'subscription_created',
                    'customer_email': data.get('customer_email'),
                    'subscription_id': data.get('subscription')
                }

            elif event_type == 'customer.subscription.deleted':
                # Subscription cancelled
                return {
                    'success': True,
                    'event': 'subscription_cancelled',
                    'subscription_id': data.get('id')
                }

            elif event_type == 'invoice.payment_failed':
                # Payment failed
                return {
                    'success': True,
                    'event': 'payment_failed',
                    'customer_email': data.get('customer_email')
                }

            return {
                'success': True,
                'event': event_type
            }

        except Exception as e:
            log.error(f"Error handling webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription."""
        if not self.enabled:
            return {'success': False, 'error': 'Stripe not configured'}

        try:
            self.stripe.Subscription.delete(subscription_id)
            return {'success': True}
        except Exception as e:
            log.error(f"Error cancelling subscription: {e}")
            return {'success': False, 'error': str(e)}


class FreePaymentAlternative:
    """
    Alternative payment methods for minimal cost setup.

    Options:
    1. PayPal Subscribe buttons (free, but less automated)
    2. Buy Me a Coffee (simple, but not true subscriptions)
    3. Manual invoicing via email
    """

    @staticmethod
    def generate_paypal_button_html(price: float, currency: str = "USD") -> str:
        """
        Generate HTML for a PayPal Subscribe button.

        Note: You need to create this in your PayPal account first.
        """
        return f"""
        <!-- PayPal Subscribe Button -->
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
            <input type="hidden" name="cmd" value="_s-xclick">
            <input type="hidden" name="hosted_button_id" value="YOUR_BUTTON_ID">
            <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_subscribe_LG.gif"
                   border="0" name="submit" alt="Subscribe with PayPal">
        </form>
        """

    @staticmethod
    def generate_manual_payment_instructions(price: float, email: str) -> str:
        """Generate instructions for manual payment."""
        return f"""
        Thank you for your interest in the Premium Plan!

        To activate your subscription:
        1. Send ${price:.2f} per month via PayPal to: {email}
        2. Reply to this email with your PayPal transaction ID
        3. You'll receive your first 7-day plan within 24 hours

        Your subscription will auto-renew each month. Cancel anytime by replying to any email.
        """
