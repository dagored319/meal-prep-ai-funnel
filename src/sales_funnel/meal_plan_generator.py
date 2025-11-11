"""Generate personalized meal plans using GPT-4."""
from typing import Dict, Any
import openai
import json
from ..shared.logger import log


class MealPlanGenerator:
    """Generate personalized meal plans based on user preferences."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def generate_plan(
        self,
        user_data: Dict[str, Any],
        plan_type: str = 'free',
        days: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a personalized meal plan.

        Args:
            user_data: Dictionary with user preferences (goal, allergies, meal_count)
            plan_type: 'free' or 'premium'
            days: Number of days for the plan

        Returns:
            Dictionary containing the meal plan
        """
        log.info(f"Generating {days}-day {plan_type} meal plan for user")

        prompt = self._build_meal_plan_prompt(user_data, days)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are an expert nutritionist and meal prep specialist. '
                                   'You create practical, delicious, and nutritionally balanced meal plans.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            meal_plan_text = response.choices[0].message.content

            # Structure the plan
            plan = {
                'plan_type': plan_type,
                'days': days,
                'user_preferences': user_data,
                'meal_plan': meal_plan_text,
                'shopping_list': self._extract_shopping_list(meal_plan_text)
            }

            log.info("Meal plan generated successfully")
            return plan

        except Exception as e:
            log.error(f"Error generating meal plan: {e}")
            raise

    def _build_meal_plan_prompt(self, user_data: Dict[str, Any], days: int) -> str:
        """Build the prompt for meal plan generation."""
        goal = user_data.get('goal', 'Eat Healthier')
        allergies = user_data.get('allergies', 'none')
        meal_count = user_data.get('meal_count', '3 meals')

        prompt = f"""Create a {days}-day personalized meal prep plan with the following requirements:

USER PROFILE:
- Primary Goal: {goal}
- Dietary Restrictions/Dislikes: {allergies}
- Meals per Day: {meal_count}

REQUIREMENTS:
1. Each day should have {meal_count} clearly defined
2. Meals should be practical and easy to prep in advance
3. Include approximate prep time and calories per meal
4. Meals should align with the goal of "{goal}"
5. Avoid all mentioned allergens and disliked foods
6. Use simple, accessible ingredients
7. Include meal prep tips where helpful

FORMAT:
# {days}-Day Personalized Meal Plan

## Day 1
**Meal 1: [Name]**
- Ingredients: ...
- Prep: ...
- Calories: ~XXX
- Prep Time: XX min

**Meal 2: [Name]**
...

[Continue for all days]

## Shopping List
Organize ingredients by category (Proteins, Vegetables, etc.)

## Meal Prep Tips
Provide 2-3 tips for batch cooking and storage.

Make it personal, practical, and delicious!
"""
        return prompt

    def _extract_shopping_list(self, meal_plan_text: str) -> str:
        """Extract the shopping list section from the meal plan."""
        # Simple extraction - find the shopping list section
        if '## Shopping List' in meal_plan_text:
            parts = meal_plan_text.split('## Shopping List')
            if len(parts) > 1:
                # Get everything after "Shopping List" up to next ## or end
                shopping_section = parts[1].split('##')[0]
                return shopping_section.strip()

        return "See meal plan for ingredient details."

    def generate_premium_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a premium 7-day plan with more features."""
        plan = self.generate_plan(user_data, plan_type='premium', days=7)

        # Add premium features
        plan['includes_shopping_list'] = True
        plan['includes_prep_schedule'] = True
        plan['includes_storage_tips'] = True

        return plan
