"""AI Chatbot for lead qualification and meal plan generation."""
from typing import Dict, Any, List, Optional
import openai
import json
from ..shared.logger import log


class MealPrepChatbot:
    """Conversational AI chatbot for meal prep lead qualification."""

    def __init__(self, api_key: str, model: str = "gpt-4", persona: str = "friendly AI nutrition assistant"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.persona = persona

        # Conversation flow states
        self.states = [
            'greeting',
            'ask_goal',
            'ask_allergies',
            'ask_meal_count',
            'ask_email',
            'generate_plan',
            'upsell'
        ]

    def start_conversation(self) -> Dict[str, Any]:
        """Start a new conversation."""
        return {
            'state': 'greeting',
            'messages': [],
            'user_data': {},
            'session_id': None
        }

    def process_message(
        self,
        user_message: str,
        conversation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Args:
            user_message: The user's message
            conversation: Current conversation state

        Returns:
            Updated conversation with bot response
        """
        # Add user message to history
        conversation['messages'].append({
            'role': 'user',
            'content': user_message
        })

        # Determine current state and generate response
        current_state = conversation.get('state', 'greeting')

        # Use GPT-4 to generate natural responses while extracting data
        bot_response = self._generate_response(user_message, conversation, current_state)

        # Add bot message to history
        conversation['messages'].append({
            'role': 'assistant',
            'content': bot_response['message']
        })

        # Update conversation state and user data
        conversation['state'] = bot_response.get('next_state', current_state)
        if 'extracted_data' in bot_response:
            conversation['user_data'].update(bot_response['extracted_data'])

        return conversation

    def _generate_response(
        self,
        user_message: str,
        conversation: Dict[str, Any],
        current_state: str
    ) -> Dict[str, Any]:
        """Generate a contextual response based on conversation state."""
        messages = conversation['messages'].copy()

        # System prompt
        system_prompt = self._get_system_prompt(current_state, conversation['user_data'])

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    *messages
                ],
                temperature=0.7,
                max_tokens=300
            )

            bot_message = response.choices[0].message.content

            # Extract structured data and determine next state
            result = self._parse_response_and_extract_data(
                user_message,
                bot_message,
                current_state,
                conversation['user_data']
            )

            return result

        except Exception as e:
            log.error(f"Error generating chatbot response: {e}")
            return {
                'message': "I'm sorry, I encountered an error. Could you please try again?",
                'next_state': current_state
            }

    def _get_system_prompt(self, state: str, user_data: Dict) -> str:
        """Get the system prompt based on conversation state."""
        base_prompt = f"""You are a {self.persona}. Your goal is to help users create personalized meal plans.

Be conversational, friendly, and empathetic. Keep responses concise (2-3 sentences max).
"""

        state_prompts = {
            'greeting': """
The user just arrived. Welcome them warmly and ask about their primary goal.
Mention that you can create a free personalized meal plan for them.
Ask: "What's your primary goal? (e.g., Lose Weight, Build Muscle, Save Time, Eat Healthier)"
""",
            'ask_goal': """
The user shared their goal. Acknowledge it positively.
Now ask about any food allergies or foods they dislike.
Ask: "Great choice! Do you have any food allergies or foods you really dislike?"
""",
            'ask_allergies': """
The user shared their dietary restrictions. Acknowledge them.
Now ask how many meals per day they prefer.
Ask: "Got it. How many meals per day would you like? (e.g., 2 meals, 3 meals, 3 meals + snacks)"
""",
            'ask_meal_count': """
The user shared their meal preferences. Acknowledge it.
Now explain you'll generate their free 3-day meal plan and need their email to send it.
Ask: "Perfect! I'll create your personalized 3-day meal plan right now. What's your email so I can send it to you?"
""",
            'ask_email': """
The user provided their email. Thank them and confirm you're generating their plan.
Tell them: "Thanks! Give me just a moment while I create your personalized plan..."
""",
            'upsell': """
The user received their free plan. Now present the premium subscription offer.
Explain: "Your 3-day starter plan is on its way to your inbox! Want to make this permanent?
For $19/month, I'll send you a new personalized 7-day plan every Friday, perfectly matched to your goals and preferences."
"""
        }

        return base_prompt + state_prompts.get(state, "")

    def _parse_response_and_extract_data(
        self,
        user_message: str,
        bot_message: str,
        current_state: str,
        user_data: Dict
    ) -> Dict[str, Any]:
        """Parse the bot response and extract structured data."""
        result = {
            'message': bot_message,
            'next_state': current_state,
            'extracted_data': {}
        }

        # State transitions and data extraction
        if current_state == 'greeting':
            result['next_state'] = 'ask_goal'

        elif current_state == 'ask_goal':
            # Extract goal from user message
            goal = self._extract_goal(user_message)
            result['extracted_data']['goal'] = goal
            result['next_state'] = 'ask_allergies'

        elif current_state == 'ask_allergies':
            # Extract allergies/dislikes
            allergies = user_message
            result['extracted_data']['allergies'] = allergies
            result['next_state'] = 'ask_meal_count'

        elif current_state == 'ask_meal_count':
            # Extract meal count
            meal_count = self._extract_meal_count(user_message)
            result['extracted_data']['meal_count'] = meal_count
            result['next_state'] = 'ask_email'

        elif current_state == 'ask_email':
            # Extract email
            email = self._extract_email(user_message)
            if email:
                result['extracted_data']['email'] = email
                result['next_state'] = 'generate_plan'
            else:
                result['message'] = "I didn't catch a valid email. Could you please provide your email address?"
                result['next_state'] = 'ask_email'

        elif current_state == 'generate_plan':
            result['next_state'] = 'upsell'

        return result

    def _extract_goal(self, text: str) -> str:
        """Extract user's goal from their message."""
        text_lower = text.lower()

        if any(word in text_lower for word in ['lose', 'weight', 'fat', 'slim']):
            return 'Lose Weight'
        elif any(word in text_lower for word in ['muscle', 'gain', 'bulk', 'strong']):
            return 'Build Muscle'
        elif any(word in text_lower for word in ['save time', 'quick', 'easy', 'busy']):
            return 'Save Time'
        elif any(word in text_lower for word in ['health', 'eat better', 'nutrition']):
            return 'Eat Healthier'
        else:
            return text  # Return raw text if no match

    def _extract_meal_count(self, text: str) -> str:
        """Extract meal count from user message."""
        text_lower = text.lower()

        if '2' in text or 'two' in text_lower:
            return '2 meals'
        elif 'snack' in text_lower:
            return '3 meals + snacks'
        elif '3' in text or 'three' in text_lower:
            return '3 meals'
        elif '4' in text or 'four' in text_lower:
            return '4 meals'
        else:
            return '3 meals'  # Default

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        import re

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)

        return match.group(0) if match else None

    def get_conversation_summary(self, conversation: Dict[str, Any]) -> str:
        """Get a summary of the conversation for debugging/logging."""
        user_data = conversation.get('user_data', {})
        return f"""
Conversation Summary:
- Goal: {user_data.get('goal', 'Not set')}
- Allergies: {user_data.get('allergies', 'Not set')}
- Meal Count: {user_data.get('meal_count', 'Not set')}
- Email: {user_data.get('email', 'Not set')}
- State: {conversation.get('state', 'Unknown')}
        """.strip()
