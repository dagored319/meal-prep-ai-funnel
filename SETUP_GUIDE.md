# Setup Guide - Organic Funnel Agent

Complete step-by-step guide to set up and run your automated AI marketing funnel.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Keys Setup](#api-keys-setup)
5. [Running the System](#running-the-system)
6. [Deployment](#deployment)

## Prerequisites

### Required
- Python 3.9 or higher
- OpenAI API account (for GPT-4)
- SendGrid account (free tier works)

### Optional (for full features)
- Instagram account (for posting)
- Stripe account (for payments)
- Pexels API key (for free stock footage)
- Domain name (for custom email and web app)

## Installation

### 1. Clone/Download the Project

```bash
cd organic-funnel-agent
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright (for web scraping)

```bash
playwright install
```

## Configuration

### 1. Copy Example Config

```bash
cp config/config.example.yml config/config.yml
```

### 2. Edit Configuration

Open `config/config.yml` and customize:

```yaml
openai:
  api_key: "your-openai-api-key"
  model: "gpt-4"

content:
  niche: "meal prep and healthy eating"
  brand_voice: "friendly, helpful meal prep expert"
  call_to_action: "Want a custom meal plan? Click the link in bio!"
  posts_per_day: 3

scraping:
  reddit:
    subreddits:
      - "MealPrepSunday"
      - "EatCheapAndHealthy"
      # Add more relevant subreddits

chatbot:
  free_plan_days: 3
  premium_price: 19  # USD per month
```

## API Keys Setup

### 1. OpenAI API (Required)

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `config/config.yml` under `openai.api_key`
4. Add billing method (GPT-4 costs ~$0.03-0.06 per interaction)

**Cost Estimate:**
- Trend analysis: ~$0.05/day
- Script generation: ~$0.10/script
- Meal plan generation: ~$0.15/plan
- Monthly estimate (3 posts/day + 10 leads): ~$20-30/month

### 2. SendGrid Email (Required)

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create API key:
   - Settings → API Keys → Create API Key
   - Give it "Full Access"
3. Add to `config/config.yml` under `email.sendgrid_api_key`
4. Verify sender email address in SendGrid

### 3. Instagram (Optional - for auto-posting)

**Note:** Instagram has strict bot policies. Options:

**Option A: Manual posting (recommended for beginners)**
- System generates videos
- You manually upload to Instagram
- Safest approach

**Option B: Automated posting (use with caution)**
- Use instagrapi library
- Add credentials to config
- Risk of account restrictions
- Consider using a burner account first

### 4. Stripe (Optional - for payments)

1. Sign up at https://stripe.com
2. Get API keys from Dashboard → Developers → API keys
3. Add to config or `.env` file

**Free Alternative:**
- Start with PayPal "Buy Now" buttons
- Manual payment tracking
- Upgrade to Stripe later

### 5. Pexels (Optional - for stock footage)

1. Sign up at https://www.pexels.com/api/
2. Get free API key
3. Add to config

## Running the System

### Test Individual Components

```bash
# 1. Test trend spotting
python -m src.trend_spotter.main

# 2. Test content creation (requires a trend ID from step 1)
python main.py content --trend-id 1

# 3. Test web app (chatbot)
python main.py web
# Visit http://localhost:8000

# 4. Check stats
python main.py stats
```

### Run Full Automated System

```bash
# Start the scheduler (runs all tasks automatically)
python main.py schedule
```

This will run:
- **9:00 AM daily:** Find trending topics
- **10:00 AM, 2:00 PM, 6:00 PM:** Create and publish content
- **Every Friday 9:00 AM:** Send weekly meal plans to premium users

### Run Web Application

```bash
# Start the chatbot web app
python main.py web
```

Visit `http://localhost:8000` to see your chatbot.

## Deployment

### Option 1: Render (Free Tier)

**For the Web App:**

1. Create account at https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python main.py web`
6. Add environment variables (API keys)
7. Deploy!

**For Background Tasks (scheduler):**

1. Create Background Worker on Render
2. Set start command: `python main.py schedule`
3. Add same environment variables
4. Deploy!

**Cost:** Free tier works for starting out

### Option 2: Railway

1. Sign up at https://railway.app
2. New Project → Deploy from GitHub
3. Add environment variables
4. Railway auto-detects Python and runs

**Cost:** $5/month free credit

### Option 3: DigitalOcean / Linode VPS

For more control and scalability:

1. Create a $5/month droplet
2. SSH into server
3. Clone repo
4. Install dependencies
5. Use `systemd` or `supervisor` to keep running
6. Use nginx as reverse proxy

### Environment Variables for Production

Create `.env` file (never commit this!):

```bash
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
FROM_EMAIL=hello@yourdomain.com
STRIPE_API_KEY=sk_live_...
```

## Post-Deployment Setup

### 1. Set Up Custom Domain

- Point domain to your web app
- Update config with new domain
- Update social media bio links

### 2. Set Up Email Domain

- Verify domain in SendGrid
- Set up SPF/DKIM records
- Improves email deliverability

### 3. Monitor System

- Check logs regularly
- Monitor API costs
- Track conversion rates
- Adjust content schedule based on performance

## Troubleshooting

### Videos Not Generating

- Install ImageMagick: https://imagemagick.org/
- Check MoviePy documentation

### Instagram Posts Failing

- Use manual upload mode
- Check account isn't restricted
- Consider using Buffer/Hootsuite API instead

### Email Not Sending

- Verify sender in SendGrid
- Check spam folder
- Verify API key permissions

### High OpenAI Costs

- Reduce posts_per_day
- Use GPT-3.5 instead of GPT-4
- Cache trend analysis

## Next Steps

1. **Customize branding:** Update colors, copy, and voice
2. **Add analytics:** Track which content performs best
3. **A/B test:** Try different CTAs and content formats
4. **Scale up:** Increase posting frequency as you grow
5. **Add features:** Recipe videos, shopping list PDFs, etc.

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages
- Common issues are usually API keys or permissions

## Cost Breakdown

**Minimal Setup (Free Tier):**
- OpenAI: $20-30/month (pay as you go)
- SendGrid: Free (100 emails/day)
- Hosting: Free (Render/Railway free tier)
- **Total: ~$20-30/month**

**Growth Setup:**
- OpenAI: $50-100/month
- SendGrid: Free → $15/month (40k emails)
- Hosting: $5-10/month
- Stripe: 2.9% + $0.30 per transaction
- **Total: ~$55-125/month**

**Revenue Potential:**
- 100 free leads/month
- 5% conversion = 5 premium users
- $19/month × 5 = $95/month
- **Break even: ~6-7 premium subscribers**

Good luck building your automated funnel! 🚀
