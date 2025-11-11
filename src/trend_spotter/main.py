"""Main orchestrator for the Trend Spotter module."""
from typing import Dict, Any
from .scrapers import RedditScraper, GoogleTrendsScraper, TikTokScraper
from .trend_analyzer import TrendAnalyzer
from ..shared.config import get_config
from ..shared.database import Database
from ..shared.logger import log


class TrendSpotter:
    """Main class for detecting and analyzing trends."""

    def __init__(self, config=None, db=None):
        self.config = config or get_config()
        self.db = db or Database(self.config.database.path)

        # Initialize scrapers
        self.reddit_scraper = RedditScraper(
            self.config.scraping.reddit.get('subreddits', [])
        )
        self.google_scraper = GoogleTrendsScraper(
            self.config.scraping.google_trends.get('keywords', [])
        )
        self.tiktok_scraper = TikTokScraper(
            self.config.scraping.tiktok.get('categories', [])
        )

        # Initialize analyzer
        self.analyzer = TrendAnalyzer(
            api_key=self.config.openai.api_key,
            model=self.config.openai.model
        )

    def run(self) -> Dict[str, Any]:
        """
        Run the complete trend spotting workflow.

        Returns:
            Dictionary with trend analysis and metadata
        """
        log.info("Starting trend spotting workflow...")

        # Step 1: Scrape all sources
        log.info("Scraping Reddit...")
        reddit_data = self.reddit_scraper.scrape_all()

        log.info("Scraping Google Trends...")
        google_data = self.google_scraper.get_trends()

        log.info("Getting TikTok trending hashtags...")
        tiktok_data = self.tiktok_scraper.get_trending_hashtags()

        # Combine all data
        trends_data = {
            'reddit': reddit_data,
            'google_trends': google_data,
            'tiktok': tiktok_data
        }

        # Step 2: Analyze with GPT-4
        log.info("Analyzing trends with AI...")
        analysis = self.analyzer.analyze_trends(
            trends_data,
            self.config.content.niche
        )

        # Step 3: Save to database
        topic = self.analyzer.extract_topic_summary(analysis['analysis'])
        trend_id = self.db.save_trend(
            source='multi-source',
            topic=topic,
            summary=analysis['analysis'],
            raw_data=trends_data
        )

        log.info(f"Trend saved with ID: {trend_id}")
        log.info(f"Trending Topic: {topic}")

        return {
            'trend_id': trend_id,
            'topic': topic,
            'analysis': analysis['analysis'],
            'sources_data': trends_data
        }


def run_trend_spotter():
    """Standalone function to run the trend spotter."""
    spotter = TrendSpotter()
    return spotter.run()


if __name__ == "__main__":
    result = run_trend_spotter()
    print("\n" + "="*60)
    print("TREND ANALYSIS RESULTS")
    print("="*60)
    print(f"\nTrend ID: {result['trend_id']}")
    print(f"\n{result['analysis']}")
    print("\n" + "="*60)
