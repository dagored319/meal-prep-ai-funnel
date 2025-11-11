"""Main orchestrator for the Organic Funnel Agent system."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from src.shared.config import get_config
from src.shared.database import Database
from src.shared.logger import log

from src.trend_spotter.main import TrendSpotter
from src.content_factory.main import ContentFactory
from src.monetization.weekly_automation import WeeklyAutomation
from src.monetization.subscription_manager import SubscriptionManager
from src.sales_funnel.meal_plan_generator import MealPlanGenerator
from src.sales_funnel.email_sender import EmailSender


class OrganicFunnelAgent:
    """Main orchestrator for the automated funnel system."""

    def __init__(self):
        self.config = get_config()
        self.db = Database(self.config.database.path)

        # Initialize all modules
        self.trend_spotter = TrendSpotter(self.config, self.db)
        self.content_factory = ContentFactory(self.config, self.db)

        # Initialize monetization components
        self.meal_plan_generator = MealPlanGenerator(
            api_key=self.config.openai.api_key,
            model=self.config.openai.model
        )
        self.email_sender = EmailSender(self.config.email.model_dump())
        self.subscription_manager = SubscriptionManager(self.db)
        self.weekly_automation = WeeklyAutomation(
            self.db,
            self.meal_plan_generator,
            self.email_sender
        )

        log.info("Organic Funnel Agent initialized")

    def run_trend_spotting(self):
        """Daily task: Find trending topics."""
        try:
            log.info("Running trend spotting...")
            result = self.trend_spotter.run()
            log.info(f"Trend spotting complete. Found: {result['topic']}")
            return result
        except Exception as e:
            log.error(f"Error in trend spotting: {e}")

    def run_content_creation(self):
        """Multiple times daily: Create and publish content."""
        try:
            log.info("Running content creation...")
            results = self.content_factory.create_daily_content()
            log.info(f"Created {len(results)} pieces of content")
            return results
        except Exception as e:
            log.error(f"Error in content creation: {e}")

    def run_weekly_delivery(self):
        """Weekly task: Send meal plans to premium subscribers."""
        try:
            log.info("Running weekly meal plan delivery...")
            stats = self.weekly_automation.send_weekly_plans()
            log.info(
                f"Weekly delivery complete. "
                f"Sent: {stats['successful_deliveries']}, "
                f"Failed: {stats['failed_deliveries']}"
            )
            return stats
        except Exception as e:
            log.error(f"Error in weekly delivery: {e}")

    def print_stats(self):
        """Print system statistics."""
        stats = self.subscription_manager.get_subscription_stats()

        print("\n" + "="*60)
        print("ORGANIC FUNNEL AGENT - STATISTICS")
        print("="*60)
        print(f"Total Leads: {stats['total_leads']}")
        print(f"Free Users: {stats['free_users']}")
        print(f"Premium Users: {stats['premium_users']}")
        print(f"Conversion Rate: {stats['conversion_rate']}%")
        print(f"Recent Signups (7 days): {stats['recent_signups']}")
        print("="*60 + "\n")

    def start_scheduler(self):
        """Start the automated scheduler."""
        scheduler = BlockingScheduler()

        # Parse schedule times from config
        trend_check_time = self.config.scheduling.trend_check_time
        content_times = self.config.scheduling.content_generation_times

        # Daily trend spotting
        hour, minute = map(int, trend_check_time.split(':'))
        scheduler.add_job(
            self.run_trend_spotting,
            CronTrigger(hour=hour, minute=minute),
            id='trend_spotting',
            name='Daily Trend Spotting'
        )

        # Content creation multiple times per day
        for time_str in content_times:
            hour, minute = map(int, time_str.split(':'))
            scheduler.add_job(
                self.run_content_creation,
                CronTrigger(hour=hour, minute=minute),
                id=f'content_creation_{time_str}',
                name=f'Content Creation {time_str}'
            )

        # Weekly meal plan delivery (every Friday at 9 AM)
        scheduler.add_job(
            self.run_weekly_delivery,
            CronTrigger(day_of_week='fri', hour=9, minute=0),
            id='weekly_delivery',
            name='Weekly Meal Plan Delivery'
        )

        # Daily stats report (every day at 8 AM)
        scheduler.add_job(
            self.print_stats,
            CronTrigger(hour=8, minute=0),
            id='daily_stats',
            name='Daily Statistics Report'
        )

        log.info("Scheduler started. Waiting for scheduled tasks...")
        log.info(f"Trend spotting: Daily at {trend_check_time}")
        log.info(f"Content creation: Daily at {', '.join(content_times)}")
        log.info("Weekly delivery: Fridays at 09:00")

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            log.info("Scheduler stopped by user")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Organic Funnel Agent')
    parser.add_argument(
        'command',
        choices=['schedule', 'trend', 'content', 'weekly', 'stats', 'web'],
        help='Command to run'
    )
    parser.add_argument(
        '--trend-id',
        type=int,
        help='Specific trend ID for content creation'
    )

    args = parser.parse_args()

    agent = OrganicFunnelAgent()

    if args.command == 'schedule':
        # Start the automated scheduler
        log.info("Starting automated scheduler...")
        agent.start_scheduler()

    elif args.command == 'trend':
        # Run trend spotting once
        log.info("Running trend spotting...")
        result = agent.run_trend_spotting()
        print(f"\nTrend ID: {result['trend_id']}")
        print(f"Topic: {result['topic']}")
        print(f"\n{result['analysis']}")

    elif args.command == 'content':
        # Run content creation once
        log.info("Running content creation...")
        if args.trend_id:
            result = agent.content_factory.create_content_from_trend(
                args.trend_id,
                publish=True
            )
            print(f"\nContent ID: {result['content_id']}")
            print(f"Video: {result['video_path']}")
            print(f"Published: {result['published']}")
        else:
            results = agent.run_content_creation()
            print(f"\nCreated {len(results)} pieces of content")

    elif args.command == 'weekly':
        # Run weekly delivery once
        log.info("Running weekly delivery...")
        stats = agent.run_weekly_delivery()
        print(f"\nSent: {stats['successful_deliveries']}")
        print(f"Failed: {stats['failed_deliveries']}")

    elif args.command == 'stats':
        # Print statistics
        agent.print_stats()

    elif args.command == 'web':
        # Start the web application
        log.info("Starting web application...")
        from src.sales_funnel.web_app import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
