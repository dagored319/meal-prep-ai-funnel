# Usage Examples

Real-world examples of how to use the Organic Funnel Agent.

## Example 1: First Time Setup

```bash
# Install and configure
cd organic-funnel-agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set up config
cp config/config.example.yml config/config.yml
# Edit config.yml with your API keys

# Test trend spotting
python main.py trend
```

**Expected Output:**
```
Starting trend spotting workflow...
Scraping Reddit...
Scraping r/MealPrepSunday...
Scraping Google Trends...
Analyzing trends with AI...

TREND ANALYSIS RESULTS
============================================================

Trend ID: 1

**Trending Topic:** Cottage cheese protein recipes
**Why It's Hot:** People are discovering cottage cheese as a high-protein,
versatile ingredient. Posts about creative cottage cheese recipes are
getting 100k+ engagements.
**Content Angle:** "3 Cottage Cheese Breakfast Hacks That Changed My
Meal Prep Game"

============================================================
```

## Example 2: Creating Your First Video

```bash
# Use the trend ID from above (usually 1)
python main.py content --trend-id 1
```

**Expected Output:**
```
Creating content from trend ID: 1
Generating script...
Script generated successfully
Creating video...
Generating voiceover...
Video created successfully: output/videos/content_1.mp4

Content ID: 1
Video: output/videos/content_1.mp4
Published: False  # Set to True in config to auto-post
```

**What You Get:**
- A 30-second vertical video (1080x1920)
- AI-generated voiceover
- Text captions
- Ready to post to TikTok/Instagram/YouTube Shorts

## Example 3: Testing the Chatbot

```bash
# Start the web app
python main.py web
```

Visit `http://localhost:8000` and try this conversation:

**Bot:** Welcome! What's your primary goal?

**You:** Lose weight

**Bot:** Great choice! Do you have any food allergies?

**You:** I'm allergic to peanuts and hate olives

**Bot:** Got it. How many meals per day would you like?

**You:** 3 meals and 1 snack

**Bot:** Perfect! What's your email?

**You:** your-email@gmail.com

**Bot:** Give me just a moment...
*[Bot generates meal plan]*
I've sent your 3-day starter plan to your email! Check your inbox.

Want to make this permanent? For $19/month, I'll send you a new 7-day plan every Friday!

**Expected Email:**
You'll receive a personalized 3-day meal plan:
- Day 1: Breakfast, Lunch, Dinner, Snack (with recipes)
- Day 2: ...
- Day 3: ...
- Shopping list
- Prep tips

## Example 4: Running on a Schedule

```bash
python main.py schedule
```

**What Happens:**
```
Scheduler started. Waiting for scheduled tasks...
Trend spotting: Daily at 09:00
Content creation: Daily at 10:00, 14:00, 18:00
Weekly delivery: Fridays at 09:00

[2024-01-15 09:00:00] Running trend spotting...
[2024-01-15 09:01:23] Trend spotting complete. Found: Cottage cheese recipes

[2024-01-15 10:00:00] Running content creation...
[2024-01-15 10:03:45] Created 3 pieces of content

[2024-01-15 14:00:00] Running content creation...
[2024-01-15 14:03:22] Created 3 pieces of content
```

The system now runs fully automated! Press Ctrl+C to stop.

## Example 5: Checking Statistics

```bash
python main.py stats
```

**Output:**
```
============================================================
ORGANIC FUNNEL AGENT - STATISTICS
============================================================
Total Leads: 47
Free Users: 42
Premium Users: 5
Conversion Rate: 10.64%
Recent Signups (7 days): 12
============================================================
```

## Example 6: Sending Weekly Plans

```bash
python main.py weekly
```

**Output:**
```
============================================================
WEEKLY DELIVERY REPORT
============================================================
Total Subscribers: 5
Successful: 5
Failed: 0
============================================================
```

Each premium subscriber receives:
- New 7-day personalized meal plan
- Shopping list
- Meal prep schedule
- Storage tips

## Example 7: Custom Niche (Fitness)

Edit `config/config.yml`:

```yaml
content:
  niche: "home fitness and workout routines"
  brand_voice: "motivating fitness coach"
  call_to_action: "Get your free workout plan! Link in bio 👆"
  posts_per_day: 3

scraping:
  reddit:
    subreddits:
      - "bodyweightfitness"
      - "Fitness"
      - "homegym"
  google_trends:
    keywords:
      - "home workout"
      - "fitness"
      - "exercise"
```

Modify chatbot questions in `src/sales_funnel/chatbot.py`:
- "What's your fitness goal?" (Lose Fat, Build Muscle, Get Toned)
- "Do you have any injuries or limitations?"
- "How many days per week can you work out?"

The meal plan generator becomes a workout plan generator!

## Example 8: Deploying to Render

```bash
# Create render.yaml
services:
  - type: web
    name: meal-prep-chatbot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py web
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: SENDGRID_API_KEY
        sync: false

  - type: worker
    name: meal-prep-scheduler
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py schedule
    envVars:
      - key: OPENAI_API_KEY
        sync: false
```

Then:
```bash
# Push to GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# Deploy on Render
# 1. Go to render.com
# 2. New → Blueprint
# 3. Connect repo
# 4. Add environment variables
# 5. Deploy!
```

Your chatbot will be live at: `https://your-app.onrender.com`

## Example 9: A/B Testing Content

Create multiple scripts and compare performance:

```python
# In src/content_factory/script_generator.py
scripts = script_generator.generate_multiple_scripts(
    trend_topic="cottage cheese recipes",
    trend_analysis=analysis,
    count=3  # Generate 3 variations
)

# Post all 3 at different times
# Track which gets the most engagement
# Use the winning style for future content
```

## Example 10: Analyzing Costs

After running for a month:

```python
# Check OpenAI usage
# Dashboard: https://platform.openai.com/usage

# Typical costs for 100 leads + 90 posts:
# - Trend analysis: 30 days × $0.05 = $1.50
# - Scripts: 90 × $0.10 = $9.00
# - Meal plans: 100 × $0.15 = $15.00
# Total: ~$25.50/month

# Revenue (at 5% conversion):
# - 100 leads × 5% = 5 premium
# - 5 × $19 = $95/month
# Profit: $69.50/month
```

## Example 11: Handling Errors

**If trend spotting fails:**
```bash
# Check logs
cat logs/agent.log

# Common issue: Rate limiting
# Solution: Add delays in scrapers.py

# Manual fallback
python -c "from src.trend_spotter.scrapers import RedditScraper; \
           s = RedditScraper(['MealPrepSunday']); \
           print(s.scrape_all())"
```

**If video creation fails:**
```bash
# Check MoviePy/ImageMagick installation
python -c "from moviepy.editor import *; print('MoviePy OK')"

# Fallback: Use text-only mode
# Set background_video=None in video_creator.py
```

## Example 12: Scaling Up

Once you have 50+ subscribers:

```yaml
# config/config.yml
content:
  posts_per_day: 5  # Increase frequency

scheduling:
  content_generation_times:
    - "08:00"
    - "11:00"
    - "14:00"
    - "17:00"
    - "20:00"  # Optimal posting times
```

**Add content variety:**
- Recipes
- Tips
- Behind-the-scenes
- User testimonials
- Meal prep hacks

**Upgrade to premium APIs:**
- TikTok Official API (when available)
- Buffer for scheduling
- Professional video stock footage

## Tips & Tricks

### Get Better Trends
```python
# Add more subreddits for your niche
# Look at subscriber count and activity
# Mix big and small communities
```

### Improve Conversion
```python
# Make free plan more valuable (5 days instead of 3)
# Add shopping list and prep schedule
# Send follow-up emails
# Add urgency ("Limited spots available")
```

### Reduce Costs
```python
# Use GPT-3.5-turbo instead of GPT-4
# Cache trend analysis for 24 hours
# Reduce posts_per_day while testing
# Use free tier everything initially
```

### Increase Quality
```python
# Add real voiceover (using Eleven Labs API)
# Use professional video editing
# Add music and effects
# Higher quality stock footage
```

## Common Workflows

### Daily Routine (Manual Mode)
```bash
# 9 AM: Find trends
python main.py trend

# 10 AM, 2 PM, 6 PM: Create content
python main.py content

# Evening: Check stats and respond to leads
python main.py stats
```

### Weekly Routine
```bash
# Monday: Review last week's performance
# Tuesday-Thursday: Create content
# Friday: Send weekly plans
python main.py weekly

# Weekend: Plan next week, adjust strategy
```

### Monthly Review
```bash
# Check conversion rates
python main.py stats

# Review costs
# Check OpenAI dashboard
# Check SendGrid usage

# Optimize:
# - Which content performed best?
# - Which trends got most engagement?
# - What's the conversion rate?
# - How to improve?
```

---

These examples should get you up and running quickly. Experiment, iterate, and scale! 🚀
