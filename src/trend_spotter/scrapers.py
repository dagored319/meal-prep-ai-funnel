"""Web scrapers for trending content from various platforms."""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from datetime import datetime
import json


class RedditScraper:
    """Scrape trending posts from Reddit subreddits."""

    def __init__(self, subreddits: List[str]):
        self.subreddits = subreddits
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_subreddit(self, subreddit: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape hot posts from a subreddit using Reddit's JSON API."""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            posts = []
            for post in data['data']['children']:
                post_data = post['data']
                posts.append({
                    'title': post_data['title'],
                    'score': post_data['score'],
                    'num_comments': post_data['num_comments'],
                    'url': f"https://reddit.com{post_data['permalink']}",
                    'created_utc': post_data['created_utc'],
                    'selftext': post_data.get('selftext', ''),
                    'subreddit': subreddit
                })

            return posts

        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
            return []

    def scrape_all(self, limit_per_sub: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all configured subreddits."""
        results = {}

        for subreddit in self.subreddits:
            print(f"Scraping r/{subreddit}...")
            results[subreddit] = self.scrape_subreddit(subreddit, limit_per_sub)
            time.sleep(2)  # Be respectful to Reddit's servers

        return results


class GoogleTrendsScraper:
    """Scrape trending searches from Google Trends."""

    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def get_trends(self, geo: str = 'US') -> List[Dict[str, Any]]:
        """
        Get trending topics using Google Trends RSS feed.
        Note: For more advanced features, consider using the pytrends library.
        """
        url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')

            trends = []
            items = soup.find_all('item')

            for item in items[:20]:  # Get top 20 trending searches
                title = item.find('title').text if item.find('title') else ''
                traffic = item.find('ht:approx_traffic').text if item.find('ht:approx_traffic') else '0'
                description = item.find('description').text if item.find('description') else ''

                # Check if trend is relevant to our keywords
                relevant = any(keyword.lower() in title.lower() or
                              keyword.lower() in description.lower()
                              for keyword in self.keywords)

                if relevant:
                    trends.append({
                        'title': title,
                        'traffic': traffic,
                        'description': description,
                        'timestamp': datetime.now().isoformat()
                    })

            return trends

        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
            return []

    def get_related_queries(self) -> List[Dict[str, Any]]:
        """
        Get related queries for our keywords.
        This is a simplified version - for production, use pytrends library.
        """
        # For cost minimization, we'll use the free RSS feed
        # For more advanced features, install pytrends and use:
        # from pytrends.request import TrendReq
        # pytrends = TrendReq(hl='en-US', tz=360)
        # pytrends.build_payload(self.keywords, timeframe='now 7-d')
        # return pytrends.related_queries()

        return self.get_trends()


class TikTokScraper:
    """
    Scrape trending content from TikTok.
    Note: TikTok scraping is challenging without official API access.
    This is a simplified version using publicly available data.
    """

    def __init__(self, categories: List[str]):
        self.categories = categories
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_trending_hashtags(self) -> List[Dict[str, Any]]:
        """
        Get trending hashtags related to our categories.

        Note: For production use, consider:
        1. Using unofficial TikTok API libraries (use with caution)
        2. Using web scraping with Playwright for JavaScript-rendered content
        3. Using paid TikTok API access if available
        4. Manually curating trending hashtags
        """
        # Placeholder for trending hashtags
        # In production, you would:
        # 1. Use Playwright to scrape TikTok's discover page
        # 2. Use an unofficial API library
        # 3. Or manually update this list regularly

        trending_hashtags = {
            'Food': [
                '#foodtok', '#cookinghacks', '#easyrecipes', '#mealprep',
                '#healthyeating', '#cottagerecipe', '#proteinhacks'
            ],
            'Health': [
                '#wellness', '#healthylifestyle', '#nutrition',
                '#weightloss', '#fitness', '#healthtips'
            ]
        }

        results = []
        for category in self.categories:
            if category in trending_hashtags:
                results.extend([
                    {'hashtag': tag, 'category': category, 'source': 'curated'}
                    for tag in trending_hashtags[category]
                ])

        return results

    def scrape_with_playwright(self):
        """
        Advanced scraping using Playwright for JavaScript-rendered content.
        Uncomment and implement if you need real-time TikTok data.
        """
        # from playwright.sync_api import sync_playwright
        #
        # with sync_playwright() as p:
        #     browser = p.chromium.launch()
        #     page = browser.new_page()
        #     page.goto('https://www.tiktok.com/discover')
        #     # Wait for content to load
        #     page.wait_for_selector('.trending-item')
        #     # Extract trending items
        #     items = page.query_selector_all('.trending-item')
        #     # Process items...
        #     browser.close()

        pass
