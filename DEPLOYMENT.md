# Deployment Guide

## Quick Deploy to Render.com

### Prerequisites
- GitHub account
- Render.com account (free)
- OpenAI API key
- SendGrid API key with verified sender email

### Step 1: Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit - ready for deployment"

# Create GitHub repo and push
# Follow GitHub instructions to create a new repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Or manually configure:
   - **Name**: meal-prep-ai-chatbot
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && playwright install chromium && playwright install-deps`
   - **Start Command**: `python main.py web`

### Step 3: Add Environment Variables

In Render dashboard, add these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (starts with sk-)
- `SENDGRID_API_KEY`: Your SendGrid API key (starts with SG.)
- `FROM_EMAIL`: Your verified sender email (e.g., hello@yourdomain.com)

### Step 4: Deploy!

Click "Create Web Service" and wait for deployment (5-10 minutes first time).

Your app will be live at: `https://your-app-name.onrender.com`

### Step 5: Verify SendGrid Sender

**IMPORTANT**: Before your app can send emails, you must verify your sender email in SendGrid:

1. Go to SendGrid Dashboard
2. Settings → Sender Authentication
3. Verify a Single Sender
4. Add your FROM_EMAIL and verify via email
5. Wait for verification (usually instant)

### Step 6: Test

Visit your deployed URL and:
1. Start a conversation with the chatbot
2. Complete the questionnaire
3. Provide your email
4. Check that you receive the meal plan email

## Optional: Deploy Background Worker

To run automated content creation and weekly delivery:

1. In Render, create a new "Background Worker"
2. Use same repository
3. **Start Command**: `python main.py schedule`
4. Add same environment variables
5. Deploy

This will:
- Find trends daily at 9 AM
- Create content 3x per day
- Send weekly meal plans to premium users every Friday

## Troubleshooting

### Emails not sending
- Verify your sender email in SendGrid
- Check SendGrid dashboard for error logs
- Ensure SENDGRID_API_KEY and FROM_EMAIL are set correctly

### Build fails
- Check Render build logs
- Common issue: playwright installation
- May need to increase instance size for playwright

### App crashes on startup
- Check application logs in Render
- Verify all environment variables are set
- Check database path is writable

## Cost

**Free Tier on Render**:
- Web service sleeps after 15 min of inactivity
- 750 hours/month free
- Perfect for testing and low traffic

**Paid Tier** ($7/month):
- Always on
- No sleep time
- Better for production with regular traffic

## Monitoring

- Check Render dashboard for logs
- Monitor OpenAI API usage at platform.openai.com
- Monitor SendGrid email delivery in SendGrid dashboard

## Scaling Up

When you get traction:
1. Upgrade Render to paid tier ($7/month)
2. Add custom domain
3. Enable background worker for automation
4. Consider Redis for session management
5. Add Stripe integration for payments

## Support

Check logs in Render dashboard if issues occur.
Most common issues are:
- Missing environment variables
- Unverified SendGrid sender
- playwright installation (increase instance size if needed)
