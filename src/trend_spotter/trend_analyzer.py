"""Analyze scraped trends using LLM to identify the best content opportunities."""
from typing import List, Dict, Any, Optional
import openai
from ..shared.logger import log


class TrendAnalyzer:
    """Analyze trends using GPT-4 to identify content opportunities."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def analyze_trends(self, trends_data: Dict[str, Any], niche: str) -> Dict[str, Any]:
        """
        Analyze trends from all sources and identify the best content opportunity.

        Args:
            trends_data: Dictionary containing trends from various sources
            niche: The niche/topic focus (e.g., "meal prep and healthy eating")

        Returns:
            Dictionary with the selected trend and content strategy
        """
        # Prepare the data for analysis
        prompt = self._build_analysis_prompt(trends_data, niche)

        try:
            log.info("Analyzing trends with GPT-4...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media trend analyst specializing in viral content. "
                                   "Your job is to identify the single best trending topic that can be "
                                   "turned into engaging social media content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            analysis = response.choices[0].message.content
            log.info(f"Trend analysis complete: {analysis}")

            # Parse the response
            return {
                'analysis': analysis,
                'raw_data': trends_data,
                'model_used': self.model
            }

        except Exception as e:
            log.error(f"Error analyzing trends: {e}")
            raise

    def _build_analysis_prompt(self, trends_data: Dict[str, Any], niche: str) -> str:
        """Build the prompt for trend analysis."""
        prompt = f"""Analyze the following trending topics in the {niche} space.

DATA SOURCES:
"""

        # Add Reddit trends
        if 'reddit' in trends_data and trends_data['reddit']:
            prompt += "\n**REDDIT TRENDS:**\n"
            for subreddit, posts in trends_data['reddit'].items():
                if posts:
                    prompt += f"\nr/{subreddit}:\n"
                    for post in posts[:5]:  # Top 5 posts per subreddit
                        prompt += f"- {post['title']} (Score: {post['score']}, Comments: {post['num_comments']})\n"

        # Add Google Trends
        if 'google_trends' in trends_data and trends_data['google_trends']:
            prompt += "\n**GOOGLE TRENDING SEARCHES:**\n"
            for trend in trends_data['google_trends'][:10]:
                prompt += f"- {trend['title']} (Traffic: {trend.get('traffic', 'N/A')})\n"

        # Add TikTok hashtags
        if 'tiktok' in trends_data and trends_data['tiktok']:
            prompt += "\n**TIKTOK TRENDING HASHTAGS:**\n"
            for item in trends_data['tiktok'][:10]:
                prompt += f"- {item['hashtag']} ({item['category']})\n"

        prompt += """

TASK:
1. Identify the SINGLE BIGGEST trending theme, hack, or topic that appears across multiple sources
2. This should be something that's getting high engagement and is relevant to {niche}
3. It should be specific enough to create content around (not too broad)
4. It should be fresh and timely

OUTPUT FORMAT:
Provide a 2-3 sentence summary in this format:

**Trending Topic:** [One clear, specific topic]
**Why It's Hot:** [Explain why this is trending and why it resonates]
**Content Angle:** [Specific angle for creating a video about this]

Example:
**Trending Topic:** Cottage cheese protein recipes
**Why It's Hot:** People are discovering cottage cheese as a high-protein, versatile ingredient. Posts about creative cottage cheese recipes are getting 100k+ engagements.
**Content Angle:** "3 Cottage Cheese Breakfast Hacks That Changed My Meal Prep Game"
"""

        return prompt.replace('{niche}', niche)

    def extract_topic_summary(self, analysis: str) -> str:
        """Extract just the topic name from the analysis."""
        # Parse the "Trending Topic:" from the analysis
        lines = analysis.split('\n')
        for line in lines:
            if 'Trending Topic:' in line or '**Trending Topic:**' in line:
                return line.split(':')[-1].strip().strip('*').strip()

        # Fallback: return first line
        return lines[0] if lines else analysis
