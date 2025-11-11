"""Create videos from scripts using TTS and simple visuals."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from gtts import gTTS
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip, ImageClip
)
from ..shared.logger import log
import textwrap


class VideoCreator:
    """Create social media videos from scripts."""

    def __init__(self, output_dir: str = "output/videos"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def create_video(
        self,
        script: Dict[str, Any],
        video_id: str,
        background_video: Optional[str] = None,
        background_color: str = "#1a1a1a"
    ) -> str:
        """
        Create a video from a script.

        Args:
            script: Dictionary containing script content and metadata
            video_id: Unique identifier for this video
            background_video: Path to background video (optional)
            background_color: Hex color for background if no video provided

        Returns:
            Path to the created video file
        """
        log.info(f"Creating video {video_id}")

        try:
            # Step 1: Generate voiceover
            audio_path = self._generate_voiceover(script['parsed']['full_text'], video_id)

            # Step 2: Create visual content
            if background_video and os.path.exists(background_video):
                video_path = self._create_video_with_background(
                    script, audio_path, background_video, video_id
                )
            else:
                video_path = self._create_text_based_video(
                    script, audio_path, background_color, video_id
                )

            log.info(f"Video created successfully: {video_path}")
            return video_path

        except Exception as e:
            log.error(f"Error creating video: {e}")
            raise

    def _generate_voiceover(self, text: str, video_id: str) -> str:
        """Generate voiceover using Google Text-to-Speech."""
        audio_path = os.path.join(self.output_dir, f"{video_id}_voiceover.mp3")

        log.info("Generating voiceover...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(audio_path)

        return audio_path

    def _create_text_based_video(
        self,
        script: Dict[str, Any],
        audio_path: str,
        background_color: str,
        video_id: str
    ) -> str:
        """Create a simple text-based video with captions."""
        # Get audio duration
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        # Create background
        background = ColorClip(
            size=(1080, 1920),  # Vertical video for TikTok/Reels
            color=self._hex_to_rgb(background_color),
            duration=duration
        )

        # Create text clips
        clips = [background]

        # Add hook text (first 3 seconds)
        if script['parsed']['hook']:
            hook_text = self._create_text_clip(
                script['parsed']['hook'],
                duration=min(3, duration),
                fontsize=70,
                color='white',
                position='center'
            )
            clips.append(hook_text)

        # Add main content text (scrolling or static)
        if script['parsed']['main_content']:
            main_text = self._create_text_clip(
                script['parsed']['main_content'],
                duration=max(0, duration - 3),
                fontsize=50,
                color='white',
                position='center',
                start_time=3
            )
            clips.append(main_text)

        # Composite all clips
        final = CompositeVideoClip(clips, size=(1080, 1920))
        final = final.set_audio(audio)

        # Export
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        final.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(self.output_dir, f"{video_id}_temp_audio.m4a"),
            remove_temp=True
        )

        # Cleanup
        audio.close()
        final.close()

        return output_path

    def _create_video_with_background(
        self,
        script: Dict[str, Any],
        audio_path: str,
        background_video: str,
        video_id: str
    ) -> str:
        """Create video with background video footage."""
        # Load background video
        bg_video = VideoFileClip(background_video)

        # Get audio duration
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        # Loop or trim background video to match audio duration
        if bg_video.duration < duration:
            # Loop the video
            loops = int(duration / bg_video.duration) + 1
            bg_video = concatenate_videoclips([bg_video] * loops)

        bg_video = bg_video.subclip(0, duration)

        # Resize to vertical format (1080x1920)
        bg_video = bg_video.resize(height=1920)
        bg_video = bg_video.crop(x_center=bg_video.w/2, width=1080, height=1920)

        # Add captions
        clips = [bg_video]

        # Add hook text with background
        if script['parsed']['hook']:
            hook_text = self._create_text_clip(
                script['parsed']['hook'],
                duration=min(3, duration),
                fontsize=70,
                color='yellow',
                position='center',
                bg_color='black'
            )
            clips.append(hook_text)

        # Composite
        final = CompositeVideoClip(clips, size=(1080, 1920))
        final = final.set_audio(audio)

        # Export
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        final.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac'
        )

        # Cleanup
        audio.close()
        bg_video.close()
        final.close()

        return output_path

    def _create_text_clip(
        self,
        text: str,
        duration: float,
        fontsize: int = 50,
        color: str = 'white',
        position: str = 'center',
        start_time: float = 0,
        bg_color: Optional[str] = None
    ) -> TextClip:
        """Create a text clip with specified styling."""
        # Wrap text to fit in frame
        wrapped_text = textwrap.fill(text, width=30)

        clip = TextClip(
            wrapped_text,
            fontsize=fontsize,
            color=color,
            font='Arial-Bold',
            size=(1000, None),
            method='caption',
            align='center',
            bg_color=bg_color
        )

        clip = clip.set_duration(duration).set_start(start_time).set_position(position)

        return clip

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class FreeStockFootageFinder:
    """
    Helper class to find free stock footage.

    Recommended free sources:
    - Pexels (pexels.com) - Free API available
    - Pixabay (pixabay.com) - Free API available
    - Coverr (coverr.co) - Free videos, no API
    """

    def __init__(self, pexels_api_key: Optional[str] = None):
        self.pexels_api_key = pexels_api_key

    def search_pexels(self, query: str, per_page: int = 5) -> list:
        """Search for free stock videos on Pexels."""
        if not self.pexels_api_key:
            log.warning("Pexels API key not provided. Using manual method.")
            return []

        import requests

        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {"query": query, "per_page": per_page}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            videos = []
            for video in data.get('videos', []):
                # Get HD video file
                video_files = video.get('video_files', [])
                hd_file = next(
                    (f for f in video_files if f.get('quality') == 'hd'),
                    video_files[0] if video_files else None
                )

                if hd_file:
                    videos.append({
                        'id': video['id'],
                        'url': hd_file['link'],
                        'width': hd_file['width'],
                        'height': hd_file['height']
                    })

            return videos

        except Exception as e:
            log.error(f"Error fetching from Pexels: {e}")
            return []

    def download_video(self, url: str, output_path: str) -> str:
        """Download a video from a URL."""
        import requests

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return output_path

        except Exception as e:
            log.error(f"Error downloading video: {e}")
            raise
