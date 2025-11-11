"""Generate video scripts based on trending topics."""
from typing import Dict, Any, Optional
import openai
from ..shared.logger import log


class ScriptGenerator:
    """Generate engaging video scripts for social media."""

    def __init__(self, api_key: str, model: str = "gpt-4", brand_voice: str = "friendly", cta: str = ""):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.brand_voice = brand_voice
        self.cta = cta

    def generate_script(
        self,
        trend_topic: str,
        trend_analysis: str,
        platform: str = "tiktok",
        duration: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a video script based on a trend.

        Args:
            trend_topic: The trending topic to create content about
            trend_analysis: Detailed analysis of why this trend is hot
            platform: Target platform (tiktok, instagram, youtube_shorts)
            duration: Target duration in seconds

        Returns:
            Dictionary containing script, hook, and metadata
        """
        prompt = self._build_script_prompt(trend_topic, trend_analysis, platform, duration)

        try:
            log.info(f"Generating script for topic: {trend_topic}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert social media content creator with a {self.brand_voice} "
                                   f"voice. You create viral short-form video scripts that hook viewers immediately "
                                   f"and provide genuine value."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )

            script_content = response.choices[0].message.content

            # Parse the script
            parsed_script = self._parse_script(script_content)

            log.info("Script generated successfully")

            return {
                'full_script': script_content,
                'parsed': parsed_script,
                'topic': trend_topic,
                'platform': platform,
                'duration': duration
            }

        except Exception as e:
            log.error(f"Error generating script: {e}")
            raise

    def _build_script_prompt(self, topic: str, analysis: str, platform: str, duration: int) -> str:
        """Build the prompt for script generation."""
        platform_specs = {
            'tiktok': 'TikTok video with quick cuts and energetic pacing',
            'instagram': 'Instagram Reel with visual appeal',
            'youtube_shorts': 'YouTube Short with clear value proposition'
        }

        platform_style = platform_specs.get(platform, 'social media video')

        prompt = f"""Create a {duration}-second {platform_style} script about: {topic}

CONTEXT:
{analysis}

REQUIREMENTS:
1. **HOOK (First 3 seconds):** Must grab attention immediately with a question, bold statement, or surprising fact
2. **VALUE DELIVERY:** Provide 3-5 actionable tips, hacks, or insights
3. **PACING:** Keep it fast-paced, conversational, and energetic
4. **CALL-TO-ACTION:** End with: "{self.cta}"
5. **LENGTH:** Approximately {duration} seconds when spoken (around {duration * 3} words)

FORMAT YOUR RESPONSE AS:

**HOOK:**
[First 3 seconds - attention grabber]

**MAIN CONTENT:**
[The core value - tips, hacks, or information]

**CTA:**
[Call to action]

**VISUAL NOTES:**
[Brief suggestions for what to show on screen]

Write in a {self.brand_voice} tone that feels authentic and helpful, not salesy.
"""
        return prompt

    def _parse_script(self, script_content: str) -> Dict[str, str]:
        """Parse the generated script into components."""
        sections = {
            'hook': '',
            'main_content': '',
            'cta': '',
            'visual_notes': '',
            'full_text': ''
        }

        lines = script_content.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            line_upper = line.strip().upper()

            if '**HOOK:**' in line or line_upper.startswith('HOOK:'):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'hook'
                section_content = []
            elif '**MAIN CONTENT:**' in line or line_upper.startswith('MAIN CONTENT:'):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'main_content'
                section_content = []
            elif '**CTA:**' in line or line_upper.startswith('CTA:'):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'cta'
                section_content = []
            elif '**VISUAL NOTES:**' in line or line_upper.startswith('VISUAL'):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'visual_notes'
                section_content = []
            elif current_section and line.strip() and not line.startswith('**'):
                section_content.append(line)

        # Save the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()

        # Create full text for voiceover
        sections['full_text'] = f"{sections['hook']} {sections['main_content']} {sections['cta']}".strip()

        return sections

    def generate_multiple_scripts(self, trend_topic: str, trend_analysis: str, count: int = 3) -> list:
        """Generate multiple script variations for A/B testing."""
        scripts = []

        for i in range(count):
            script = self.generate_script(trend_topic, trend_analysis)
            scripts.append(script)

        return scripts
