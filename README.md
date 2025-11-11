# Organic Funnel Agent 🚀

A fully automated AI-powered marketing funnel that runs on autopilot. Built from scratch with Python, optimized for minimal costs.

## What It Does

This system automatically:
1. 🔍 **Finds trending topics** in your niche (Reddit, Google Trends, TikTok)
2. 🎬 **Creates video content** with AI-generated scripts and voiceovers
3. 📱 **Posts to social media** (Instagram, TikTok, YouTube Shorts)
4. 💬 **Captures leads** via conversational AI chatbot
5. 📧 **Delivers personalized meal plans** via email
6. 💰 **Upsells to premium subscriptions** ($19/month automated revenue)

## Quick Start

```bash
# 1. Install
git clone <your-repo>
cd organic-funnel-agent
pip install -r requirements.txt

# 2. Configure (add your API keys)
cp config/config.example.yml config/config.yml
# Edit config.yml with your OpenAI and SendGrid keys

# 3. Run!
python main.py trend      # Find trending topics
python main.py content    # Create content
python main.py web        # Start chatbot
python main.py schedule   # Full automation
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORGANIC FUNNEL AGENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Trend Spotter│──────▶│Content Factory│                   │
│  │              │      │              │                    │
│  │ • Reddit     │      │ • GPT-4 Scripts│                   │
│  │ • Google     │      │ • TTS Audio  │                    │
│  │ • TikTok     │      │ • Video Gen  │                    │
│  └──────────────┘      │ • Auto Post  │                    │
│                        └──────────────┘                    │
│                               │                             │
│                               ▼                             │
│                        ┌──────────────┐                    │
│                        │Social Media  │                    │
│                        │(Insta/TikTok)│                    │
│                        └──────────────┘                    │
│                               │                             │
│                               │ Link in bio                 │
│                               ▼                             │
│                        ┌──────────────┐                    │
│                        │ AI Chatbot   │                    │
│                        │ (Web App)    │                    │
│                        │              │                    │
│                        │ Captures:    │                    │
│                        │ • Goal       │                    │
│                        │ • Allergies  │                    │
│                        │ • Email      │                    │
│                        └──────────────┘                    │
│                               │                             │
│                ┌──────────────┴────────────────┐            │
│                ▼                               ▼            │
│         ┌──────────────┐              ┌──────────────┐     │
│         │ Free 3-Day   │              │Premium $19/mo│     │
│         │ Meal Plan    │              │Weekly Plans  │     │
│         │(Lead Magnet) │              │(Recurring $$)│     │
│         └──────────────┘              └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 🔍 Trend Spotter
- Scrapes Reddit hot posts from configured subreddits
- Monitors Google Trends for rising searches
- Tracks TikTok trending hashtags
- Uses GPT-4 to identify the #1 content opportunity

### 🎬 Content Factory
- Generates viral-style video scripts
- Creates voiceovers with Google TTS (free)
- Assembles videos with MoviePy
- Auto-posts to Instagram/TikTok/YouTube
- Includes captions and CTAs

### 💬 AI Sales Funnel
- Beautiful chat interface (FastAPI + HTML)
- Conversational lead qualification
- GPT-4 powered meal plan generation
- Email delivery via SendGrid
- Session management and persistence

### 💰 Monetization Engine
- Automated premium upsells
- Stripe payment integration
- Weekly meal plan automation
- Subscription management
- Analytics dashboard

## Cost Breakdown

**Minimal Setup (Starting Out):**
- OpenAI GPT-4: ~$20-30/month
- SendGrid Email: Free (100 emails/day)
- Hosting: Free (Render/Railway)
- **Total: $20-30/month**

**Revenue Potential:**
- 100 leads/month × 5% conversion = 5 subscribers
- 5 × $19/month = $95/month
- **Break even at ~6-7 subscribers**

## Tech Stack

- **Language:** Python 3.9+
- **LLM:** OpenAI GPT-4 API
- **Web Framework:** FastAPI
- **Database:** SQLite
- **Video:** MoviePy + gTTS
- **Email:** SendGrid
- **Scheduling:** APScheduler
- **Scraping:** BeautifulSoup + Playwright
- **Social Media:** Instagrapi (Instagram)
- **Payments:** Stripe

## Project Structure

```
organic-funnel-agent/
├── src/
│   ├── trend_spotter/      # Module 1: Trend detection
│   │   ├── scrapers.py     # Reddit, Google, TikTok
│   │   ├── trend_analyzer.py  # GPT-4 analysis
│   │   └── main.py
│   ├── content_factory/    # Module 2: Content generation
│   │   ├── script_generator.py  # GPT-4 scripts
│   │   ├── video_creator.py     # MoviePy video
│   │   ├── publisher.py         # Social posting
│   │   └── main.py
│   ├── sales_funnel/       # Module 3: Lead capture
│   │   ├── chatbot.py           # Conversational AI
│   │   ├── meal_plan_generator.py
│   │   ├── email_sender.py
│   │   ├── web_app.py           # FastAPI app
│   │   └── templates/
│   ├── monetization/       # Module 4: Revenue
│   │   ├── payment_processor.py # Stripe
│   │   ├── subscription_manager.py
│   │   └── weekly_automation.py
│   └── shared/             # Utilities
│       ├── config.py
│       ├── database.py
│       └── logger.py
├── config/
│   └── config.example.yml  # Configuration template
├── main.py                 # Main orchestrator
├── requirements.txt
├── QUICKSTART.md          # 15-min setup guide
├── SETUP_GUIDE.md         # Full documentation
└── README.md              # This file
```

## Configuration

All settings in `config/config.yml`:

```yaml
content:
  niche: "meal prep and healthy eating"
  brand_voice: "friendly, helpful expert"
  posts_per_day: 3

scraping:
  reddit:
    subreddits: ["MealPrepSunday", "HealthyFood"]

chatbot:
  free_plan_days: 3
  premium_price: 19

scheduling:
  trend_check_time: "09:00"
  content_generation_times: ["10:00", "14:00", "18:00"]
```

## Usage

### Manual Mode

```bash
# Find trending topics
python main.py trend

# Create content
python main.py content --trend-id 1

# Start chatbot web app
python main.py web

# Send weekly plans
python main.py weekly

# View statistics
python main.py stats
```

### Automated Mode

```bash
# Run everything on autopilot
python main.py schedule
```

Scheduler runs:
- **9:00 AM daily:** Find trends
- **10:00 AM, 2:00 PM, 6:00 PM:** Create & post content
- **Fridays 9:00 AM:** Send weekly meal plans

## Deployment

### Free Tier Hosting

**Render (Recommended):**
```bash
# Web app
render.yaml config for web service

# Background jobs
render.yaml config for worker
```

**Railway:**
```bash
railway up
# Auto-detects Python, runs main.py
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for full deployment instructions.

## API Keys Needed

1. **OpenAI** (Required): https://platform.openai.com/api-keys
2. **SendGrid** (Required): https://sendgrid.com - Free tier: 100 emails/day
3. **Stripe** (Optional): For payment processing
4. **Pexels** (Optional): For free stock footage

## Customization

This system is built for meal prep, but you can adapt it to ANY niche:

1. **Update niche in config:**
   ```yaml
   content:
     niche: "your niche here"
   ```

2. **Change subreddits:**
   ```yaml
   scraping:
     reddit:
       subreddits: ["YourNiche1", "YourNiche2"]
   ```

3. **Modify chatbot flow** in `src/sales_funnel/chatbot.py`

4. **Customize meal plan** → any lead magnet (PDFs, templates, etc.)

## Security Notes

- Never commit API keys (use `.env` or config.yml)
- `.gitignore` includes sensitive files
- Use environment variables in production
- Enable webhook signature verification for Stripe

## Contributing

This is a complete, production-ready system. Feel free to:
- Fork and customize for your niche
- Add new scrapers or content formats
- Improve video generation
- Add analytics features

## License

MIT License - Free to use and modify

## Support

See documentation:
- [QUICKSTART.md](QUICKSTART.md) - Get running in 15 minutes
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup & deployment

## Roadmap

- [ ] Add YouTube API integration
- [ ] Implement A/B testing for scripts
- [ ] Add analytics dashboard
- [ ] Support for multiple languages
- [ ] Recipe database integration
- [ ] Mobile app for subscribers

---

Built with ❤️ using Claude Code and GPT-4
