"""Main orchestrator for the Content Factory module."""
from typing import Dict, Any, Optional
from .script_generator import ScriptGenerator
from .video_creator import VideoCreator
from .publisher import SocialMediaPublisher
from ..shared.config import get_config
from ..shared.database import Database
from ..shared.logger import log


class ContentFactory:
    """Main class for generating and publishing content."""

    def __init__(self, config=None, db=None):
        self.config = config or get_config()
        self.db = db or Database(self.config.database.path)

        # Initialize components
        self.script_generator = ScriptGenerator(
            api_key=self.config.openai.api_key,
            model=self.config.openai.model,
            brand_voice=self.config.content.brand_voice,
            cta=self.config.content.call_to_action
        )

        self.video_creator = VideoCreator()

        self.publisher = SocialMediaPublisher(
            config=self.config.social_media.model_dump()
        )

    def create_content_from_trend(self, trend_id: int, publish: bool = False) -> Dict[str, Any]:
        """
        Create content from a specific trend.

        Args:
            trend_id: Database ID of the trend to use
            publish: Whether to publish immediately or save as draft

        Returns:
            Dictionary with content creation results
        """
        log.info(f"Creating content from trend ID: {trend_id}")

        # Get trend from database
        trends = self.db.get_unused_trends(limit=100)
        trend = next((t for t in trends if t['id'] == trend_id), None)

        if not trend:
            raise ValueError(f"Trend {trend_id} not found or already used")

        # Generate script
        log.info("Generating script...")
        script = self.script_generator.generate_script(
            trend_topic=trend['topic'],
            trend_analysis=trend['summary'],
            platform='tiktok',
            duration=30
        )

        # Save script to database
        content_id = self.db.save_content(
            trend_id=trend_id,
            script=script['full_script']
        )

        # Create video
        log.info("Creating video...")
        video_path = self.video_creator.create_video(
            script=script,
            video_id=f"content_{content_id}"
        )

        # Update database with video path
        self.db.update_content_status(content_id, 'created')

        result = {
            'content_id': content_id,
            'trend_id': trend_id,
            'script': script,
            'video_path': video_path,
            'published': False
        }

        # Publish if requested
        if publish:
            log.info("Publishing content...")
            caption = self._generate_caption(trend['topic'], script)

            publish_results = self.publisher.publish(
                video_path=video_path,
                caption=caption,
                platforms=['instagram']  # Start with Instagram
            )

            if any(r['success'] for r in publish_results['results']):
                self.db.update_content_status(content_id, 'published')
                self.db.mark_trend_used(trend_id)
                result['published'] = True
                result['publish_results'] = publish_results

        log.info(f"Content creation complete. Content ID: {content_id}")
        return result

    def create_daily_content(self, posts_count: Optional[int] = None) -> list:
        """
        Create the configured number of daily posts.

        Args:
            posts_count: Number of posts to create (defaults to config value)

        Returns:
            List of content creation results
        """
        if posts_count is None:
            posts_count = self.config.content.posts_per_day

        log.info(f"Creating {posts_count} posts for today...")

        # Get unused trends
        trends = self.db.get_unused_trends(limit=posts_count)

        if len(trends) < posts_count:
            log.warning(f"Only {len(trends)} unused trends available. Run trend spotter first!")

        results = []
        for trend in trends[:posts_count]:
            try:
                result = self.create_content_from_trend(
                    trend_id=trend['id'],
                    publish=True
                )
                results.append(result)
            except Exception as e:
                log.error(f"Error creating content for trend {trend['id']}: {e}")
                results.append({
                    'trend_id': trend['id'],
                    'error': str(e),
                    'published': False
                })

        log.info(f"Created {len(results)} pieces of content")
        return results

    def _generate_caption(self, topic: str, script: Dict[str, Any]) -> str:
        """Generate a caption for social media post."""
        hook = script['parsed'].get('hook', '')
        cta = self.config.content.call_to_action

        # Add relevant hashtags
        hashtags = self._generate_hashtags(topic)

        caption = f"{hook}\n\n{cta}\n\n{hashtags}"
        return caption[:2200]  # Instagram caption limit

    def _generate_hashtags(self, topic: str) -> str:
        """Generate relevant hashtags."""
        # Base hashtags
        base_tags = ['mealprep', 'healthyeating', 'nutrition', 'wellness']

        # Add topic-specific tags
        topic_words = topic.lower().split()
        topic_tags = [''.join(word.split()) for word in topic_words if len(word) > 3]

        all_tags = base_tags + topic_tags[:3]
        return ' '.join(f'#{tag}' for tag in all_tags)


def run_content_factory(trend_id: Optional[int] = None):
    """Standalone function to run the content factory."""
    factory = ContentFactory()

    if trend_id:
        # Create content from specific trend
        return factory.create_content_from_trend(trend_id, publish=True)
    else:
        # Create daily content
        return factory.create_daily_content()


if __name__ == "__main__":
    import sys

    trend_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    results = run_content_factory(trend_id)

    print("\n" + "="*60)
    print("CONTENT CREATION RESULTS")
    print("="*60)

    if isinstance(results, list):
        for result in results:
            print(f"\nContent ID: {result.get('content_id', 'N/A')}")
            print(f"Published: {result.get('published', False)}")
            if 'video_path' in result:
                print(f"Video: {result['video_path']}")
    else:
        print(f"\nContent ID: {results['content_id']}")
        print(f"Video: {results['video_path']}")
        print(f"Published: {results['published']}")

    print("\n" + "="*60)
