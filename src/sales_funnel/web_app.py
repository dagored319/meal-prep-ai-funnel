"""FastAPI web application for the chatbot interface."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid
from typing import Optional
from pathlib import Path

from .chatbot import MealPrepChatbot
from .meal_plan_generator import MealPlanGenerator
from .email_sender import EmailSender
from ..shared.config import get_config
from ..shared.database import Database
from ..shared.logger import log

# Initialize FastAPI app
app = FastAPI(title="Meal Prep AI - Free Personalized Meal Plans")

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize components
config = get_config()
db = Database(config.database.path)
chatbot = MealPrepChatbot(
    api_key=config.openai.api_key,
    model=config.openai.model,
    persona=config.chatbot.persona
)
meal_plan_generator = MealPlanGenerator(
    api_key=config.openai.api_key,
    model=config.openai.model
)
email_sender = EmailSender(config.email.model_dump())

# In-memory session store (use Redis in production)
sessions = {}


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class SubscriptionRequest(BaseModel):
    email: str
    session_id: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page with chatbot interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat(chat_message: ChatMessage):
    """Handle chat messages."""
    try:
        # Get or create session
        session_id = chat_message.session_id or str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = chatbot.start_conversation()
            sessions[session_id]['session_id'] = session_id

        # Process message
        conversation = sessions[session_id]
        conversation = chatbot.process_message(chat_message.message, conversation)

        # Save conversation to database
        lead_id = None
        if 'email' in conversation.get('user_data', {}):
            lead = db.get_lead(conversation['user_data']['email'])
            if not lead:
                lead_id = db.save_lead(
                    email=conversation['user_data']['email'],
                    name=conversation['user_data'].get('name'),
                    preferences=conversation['user_data']
                )
            else:
                lead_id = lead['id']

        db.save_conversation(session_id, conversation['messages'], lead_id)

        # Check if we need to generate meal plan
        if conversation['state'] == 'generate_plan':
            # Generate the meal plan
            meal_plan = meal_plan_generator.generate_plan(
                user_data=conversation['user_data'],
                plan_type='free',
                days=config.chatbot.free_plan_days
            )

            # Save meal plan
            plan_id = db.save_meal_plan(
                lead_id=lead_id,
                plan_type='free',
                plan_data=meal_plan
            )

            # Send email
            email_sent = email_sender.send_meal_plan(
                to_email=conversation['user_data']['email'],
                user_name=conversation['user_data'].get('name'),
                meal_plan=meal_plan,
                plan_type='free'
            )

            if email_sent:
                db.mark_plan_sent(plan_id)
                # Move to upsell state
                conversation['state'] = 'upsell'
                upsell_message = (
                    f"I've sent your 3-day starter plan to {conversation['user_data']['email']}! "
                    f"Check your inbox in the next few minutes.\n\n"
                    f"Want to make this permanent? "
                    f"Sign up for the Premium Plan for ${config.chatbot.premium_price}/month, "
                    f"and I'll send you a new, fully personalized 7-day plan and shopping list "
                    f"every single Friday, perfectly matched to your goals and preferences."
                )
                conversation['messages'].append({
                    'role': 'assistant',
                    'content': upsell_message
                })

        # Update session
        sessions[session_id] = conversation

        # Get last bot message
        bot_messages = [m for m in conversation['messages'] if m['role'] == 'assistant']
        last_bot_message = bot_messages[-1]['content'] if bot_messages else ""

        return JSONResponse({
            'message': last_bot_message,
            'session_id': session_id,
            'state': conversation['state']
        })

    except Exception as e:
        log.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subscribe")
async def subscribe(subscription: SubscriptionRequest):
    """Handle premium subscription signup."""
    try:
        # Get session
        if subscription.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        conversation = sessions[subscription.session_id]

        # Get or create lead
        lead = db.get_lead(subscription.email)
        if not lead:
            lead_id = db.save_lead(
                email=subscription.email,
                preferences=conversation.get('user_data', {})
            )
        else:
            lead_id = lead['id']

        # Update subscription status
        db.update_subscription(lead_id, 'premium')

        log.info(f"New premium subscription: {subscription.email}")

        # In production, integrate with Stripe/PayPal here

        return JSONResponse({
            'success': True,
            'message': 'Subscription activated! You\'ll receive your first 7-day plan this Friday.'
        })

    except Exception as e:
        log.error(f"Error in subscription endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "meal-prep-ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
