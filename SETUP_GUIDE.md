# SPY A++ Trading System — Setup Guide

## What This Does
This system monitors SPY (S&P 500 ETF) every hour during market hours.
When ALL trading conditions align for an A++ setup, it texts you immediately at 240-459-2841.
If conditions are not perfect — NO text is sent. Quality only.

---

## STEP 1 — Install Python on Your Computer

1. Go to: https://www.python.org/downloads
2. Click the big yellow "Download Python" button
3. Run the installer
4. **IMPORTANT:** Check the box that says "Add Python to PATH" before clicking Install
5. Click Install Now

To verify it worked, open PowerShell and type:
```
python --version
```
You should see something like: Python 3.12.x

---

## STEP 2 — Download the Project

Open PowerShell and run these commands one at a time:

```
git clone https://github.com/umargbadamosi11111990/Trading001.git
```
```
cd Trading001
```

If git is not installed, download it from: https://git-scm.com/download/win

---

## STEP 3 — Install Dependencies

In PowerShell (inside the Trading001 folder):
```
pip install -r requirements.txt
```

---

## STEP 4 — Create Your .env File

In PowerShell:
```
copy .env.example .env
```

Then open the .env file in Notepad and replace everything with this
(your real keys are already filled in below):

```
POLYGON_API_KEY=foo8xmVCzXEOPGf__3MssDkUp_C6wkEx
ALPACA_API_KEY=PKQDWM5RXXNJJSCQP4KL7WAGUA
ALPACA_SECRET_KEY=Bu8vVHikn62EuZaD4mvsd9sfJ8snAGJSK8Am4r33cXWV
ALPACA_BASE_URL=https://data.alpaca.markets
GMAIL_ADDRESS=jayjaumar1990@gmail.com
GMAIL_APP_PASSWORD=rukm mpjj narw optt
SMS_GATEWAY=2404592841@txt.att.net
```

Save and close the file.

---

## STEP 5 — Send a Test Text

Run this in PowerShell to verify everything works
(you should receive a text on 240-459-2841 within 30 seconds):

```
python -c "
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()
msg = MIMEText('TEST - SPY A++ system is live and working!')
msg['From'] = os.getenv('GMAIL_ADDRESS')
msg['To'] = os.getenv('SMS_GATEWAY')
msg['Subject'] = ''
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
    s.login(os.getenv('GMAIL_ADDRESS'), os.getenv('GMAIL_APP_PASSWORD'))
    s.sendmail(msg['From'], msg['To'], msg.as_string())
print('Text sent! Check your phone.')
"
```

---

## STEP 6 — Run the Live System

Once the test text comes through, start the real system:

```
python main.py
```

Leave this window open. The system will:
- Run automatically every hour at :31 past the hour (10:31, 11:31, 12:31... 16:31 ET)
- Check all A++ conditions on SPY
- Text you ONLY if a real signal is confirmed
- Log every cycle so you can see what it's doing

To stop it, press Ctrl + C in the PowerShell window.

---

## How the System Works

Every hour the system checks 8 conditions. ALL must pass for a signal:

1. Market not choppy (ATR filter)
2. EMA 50 above/below EMA 200 (trend direction)
3. RSI in the right zone (not overbought for LONG, not oversold for SHORT)
4. MACD histogram confirms direction
5. Stochastic oscillator confirms
6. Volume above 20-period average
7. Risk/Reward ratio at least 1:2
8. Clean price structure (breakout or retest)

Confidence score is also calculated (0-100). Signal only fires if score is 65+.

---

## What the Text Will Look Like

```
=== SPY A++ SIGNAL ===
Dir:   LONG
Entry: $542.30
SL:    $538.75
TP:    $550.10
R:R    1:2.5
Score: 78/100
---
EMA50 above EMA200 by 0.31% - trend confirmed.
RSI 57.2, MACD hist +0.0312 - momentum aligned.
Volume 1.8x avg; breakout structure present.
```

---

## Important Notes

- Keep the PowerShell window open while the system runs
- Your computer needs to stay on and connected to the internet
- The system only runs during market hours (Mon-Fri)
- No signal = no text. That is by design.
- Your API keys and passwords are in the .env file — do not share that file

---

## Questions or Issues

If something doesn't work, the most common fixes are:
- Python not added to PATH during install (reinstall Python, check the box)
- .env file not saved correctly (open it in Notepad and double-check)
- PowerShell not inside the Trading001 folder (run: cd Trading001)
