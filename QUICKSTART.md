# Quick Start Guide

Get your AI funnel running in 15 minutes!

## Step 1: Install (5 minutes)

```bash
# 1. Navigate to project
cd organic-funnel-agent

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (5 minutes)

### Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Get Your SendGrid API Key

1. Go to https://sendgrid.com (sign up for free)
2. Settings → API Keys → Create API Key
3. Select "Full Access"
4. Copy the key (starts with `SG.`)

### Update Config

```bash
# Copy example config
cp config/config.example.yml config/config.yml
```

Edit `config/config.yml`:

```yaml
openai:
  api_key: "sk-your-key-here"  # ← Add your OpenAI key

email:
  sendgrid_api_key: "SG.your-key-here"  # ← Add your SendGrid key
  from_email: "your-email@gmail.com"  # ← Your email
  from_name: "Meal Prep AI"
```

## Step 3: Test (5 minutes)

### Test 1: Find a Trend

```bash
python main.py trend
```

You should see trending topics from Reddit and Google Trends!

### Test 2: Create Content

```bash
# Use the trend ID from step 1 (usually 1)
python main.py content --trend-id 1
```

This generates a video script! (Video creation takes a few minutes)

### Test 3: Try the Chatbot

```bash
python main.py web
```

Visit http://localhost:8000 and chat with your AI!

## What's Next?

### Option A: Manual Mode (Recommended for Learning)

Run each step manually:

```bash
# Morning: Find trends
python main.py trend

# Afternoon: Create content
python main.py content --trend-id 1

# Evening: Check stats
python main.py stats
```

### Option B: Full Automation

Let it run automatically:

```bash
python main.py schedule
```

This runs everything on autopilot!

## Customize Your Funnel

Edit `config/config.yml`:

```yaml
content:
  niche: "YOUR NICHE HERE"  # Change this!
  brand_voice: "YOUR VOICE HERE"  # Your style
  posts_per_day: 3  # How often to post

scraping:
  reddit:
    subreddits:
      - "YourSubreddit1"  # Add your niche subreddits
      - "YourSubreddit2"
```

## Common First-Time Issues

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### "Config file not found"
```bash
# Make sure you copied the example config
cp config/config.example.yml config/config.yml
```

### "Invalid API key"
- Check that you copied the full key
- OpenAI keys start with `sk-`
- SendGrid keys start with `SG.`

### Videos not creating
- Install ImageMagick: https://imagemagick.org/
- Or use text-only mode initially

## Free Trial Tips

**Minimize Costs While Testing:**

1. Start with `posts_per_day: 1` in config
2. Use GPT-3.5 instead of GPT-4 (change in config)
3. Test with manual mode first
4. Only run weekly delivery when you have subscribers

**OpenAI Free Credits:**
- New accounts get $5 free credit
- This is enough for ~200 operations
- Perfect for testing!

## Getting Your First Subscriber

1. **Run the web app:**
   ```bash
   python main.py web
   ```

2. **Test it yourself:**
   - Visit http://localhost:8000
   - Go through the full conversation
   - Use your own email
   - You'll receive a real meal plan!

3. **Share the link:**
   - Use ngrok for a public URL (free)
   - Or deploy to Render (free tier)
   - Put the link in your social bio

## Next Steps

1. ✅ System is running locally
2. 📱 Create social media accounts
3. 🎨 Customize branding and voice
4. 🚀 Deploy to production
5. 💰 Add payment processing
6. 📈 Scale up posting frequency

See SETUP_GUIDE.md for full deployment instructions!

## Quick Commands Reference

```bash
# Find trending topics
python main.py trend

# Create content from trend
python main.py content --trend-id 1

# Start chatbot web app
python main.py web

# Check statistics
python main.py stats

# Run weekly delivery (for premium users)
python main.py weekly

# Full automation mode
python main.py schedule
```

Happy automating! 🤖
