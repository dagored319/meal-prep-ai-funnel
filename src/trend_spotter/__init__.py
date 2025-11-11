"""Trend Spotter module for detecting trending topics."""
from .trend_analyzer import TrendAnalyzer
from .scrapers import RedditScraper, GoogleTrendsScraper

__all__ = ['TrendAnalyzer', 'RedditScraper', 'GoogleTrendsScraper']
