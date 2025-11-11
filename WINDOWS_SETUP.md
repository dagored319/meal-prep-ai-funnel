# Windows Setup Guide

Quick guide for running the Organic Funnel Agent on Windows.

## Prerequisites

✅ Python 3.9+ installed
✅ Virtual environment created
✅ Dependencies installed
✅ Config file set up

## Important: Always Use the Virtual Environment!

The packages are installed in the `venv` folder, not in your system Python.

### Option 1: Use the Helper Scripts (Easiest)

Just double-click these files:

- **`start_web.bat`** - Start the chatbot web app
- **`find_trends.bat`** - Find trending topics
- **`run.bat trend`** - Run any command (examples below)

### Option 2: Activate Virtual Environment

Open Command Prompt in the project folder and run:

```cmd
venv\Scripts\activate
```

You'll see `(venv)` appear in your prompt. Now you can run:

```cmd
python main.py trend
python main.py web
python main.py stats
python main.py content --trend-id 1
```

When you're done, type `deactivate` to exit the virtual environment.

### Option 3: Use Full Path (No Activation Needed)

```cmd
venv\Scripts\python.exe main.py trend
venv\Scripts\python.exe main.py web
venv\Scripts\python.exe main.py stats
```

## Quick Start Commands

### Start the Chatbot
```cmd
start_web.bat
```
Or:
```cmd
venv\Scripts\activate
python main.py web
```
Then visit: http://localhost:8000

### Find Trending Topics
```cmd
find_trends.bat
```
Or:
```cmd
venv\Scripts\activate
python main.py trend
```

### Create Content
```cmd
venv\Scripts\activate
python main.py content --trend-id 1
```

### Check Stats
```cmd
venv\Scripts\activate
python main.py stats
```

### Run on Schedule (Full Automation)
```cmd
venv\Scripts\activate
python main.py schedule
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'apscheduler'"

**Problem:** You're using system Python instead of the virtual environment.

**Solution:** Use one of the helper scripts or activate the venv first:
```cmd
venv\Scripts\activate
```

### "Config file not found"

**Problem:** No config.yml file

**Solution:**
```cmd
copy config\config.example.yml config\config.yml
```
Then edit `config\config.yml` with your API keys.

### Virtual Environment Not Found

**Problem:** The venv folder doesn't exist

**Solution:** Create it:
```cmd
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## All Commands Reference

After activating the venv:

```cmd
# Trend spotting
python main.py trend

# Content creation
python main.py content
python main.py content --trend-id 1

# Web app (chatbot)
python main.py web

# Weekly delivery
python main.py weekly

# Statistics
python main.py stats

# Full automation
python main.py schedule
```

## Tips

1. **Always activate the venv first** or use the helper `.bat` files
2. **To exit the venv**, type `deactivate`
3. **Keep Command Prompt open** when running the web app or scheduler
4. **Press Ctrl+C** to stop the web app or scheduler

## Next Steps

1. ✅ Venv activated
2. 🎯 Test chatbot: `start_web.bat` or `python main.py web`
3. 🚀 Find trends: `find_trends.bat` or `python main.py trend`
4. 📝 Create content: `python main.py content --trend-id 1`

Happy automating! 🤖
