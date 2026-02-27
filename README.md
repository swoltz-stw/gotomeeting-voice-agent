# GoToMeeting AI Voice Support Agent

An AI-powered phone support agent for GoToMeeting customers, built with:
- **Twilio** — Phone number + call handling
- **Claude (claude-sonnet-4-20250514)** — AI brain for support conversations
- **Flask** — Web server that connects everything

---

## 🚀 Deployment Guide (30–45 minutes)

### Step 1: Get Your API Keys

#### A. Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in or create an account
3. Click **API Keys** in the left sidebar
4. Click **Create Key**, name it "GoToMeeting Voice Agent"
5. Copy the key (starts with `sk-ant-...`) — save it somewhere safe

#### B. Twilio Account
1. Go to [twilio.com](https://twilio.com) and create a free account
2. Verify your email and phone number
3. From the Twilio Console dashboard, copy:
   - **Account SID** (starts with `AC...`)
   - **Auth Token**
4. These are only needed if you add SMS features later — not required for voice

---

### Step 2: Deploy to Railway (Free & Easy)

Railway is the fastest way to get this live with a public URL.

1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Upload these project files to a new GitHub repo first:
   - Create a repo at [github.com/new](https://github.com/new), name it `gotomeeting-voice-agent`
   - Upload all files from this folder
4. Back in Railway, select your new repo
5. Railway will auto-detect it's a Python app and deploy it

#### Set Environment Variables in Railway:
1. Click your deployed service → **Variables** tab
2. Add:
   ```
   ANTHROPIC_API_KEY = sk-ant-your-key-here
   ```
3. Railway will redeploy automatically

#### Get Your Public URL:
1. Click **Settings** → **Networking** → **Generate Domain**
2. You'll get a URL like: `https://gotomeeting-voice-agent-production.up.railway.app`
3. Test it: visit `https://your-url.railway.app/health` — you should see `{"status": "ok"}`

---

### Step 3: Get a Phone Number from Twilio

1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a Number**
2. Search for a number in your area code
3. Make sure **Voice** capability is checked
4. Click **Buy** (~$1.15/month)

#### Configure the Phone Number:
1. Click on your new number
2. Under **Voice & Fax** → **A Call Comes In**:
   - Change to **Webhook**
   - Set URL to: `https://your-railway-url.railway.app/voice`
   - Method: **HTTP POST**
3. Click **Save**

---

### Step 4: Test Your Agent! 📞

1. Call your Twilio phone number from any phone
2. You should hear: *"Thank you for calling GoToMeeting customer support. I'm Alex..."*
3. Ask it anything — "I can't hear audio in my meeting" or "How do I share my screen?"
4. The AI will respond with helpful GoToMeeting support!

---

## 🎛️ Customization

### Change the Agent's Name or Personality
Edit `SYSTEM_PROMPT` in `app.py`. You can change the name "Alex", adjust the tone, or add more specific troubleshooting scripts.

### Change the Voice
In `app.py`, replace `Polly.Joanna` with another Amazon Polly voice:
- `Polly.Matthew` — Male US English
- `Polly.Amy` — Female British English  
- `Polly.Brian` — Male British English
- `Polly.Salli` — Female US English

### Add Business Hours
Wrap the `/voice` handler with time-based logic to play a "we're closed" message outside hours.

### Escalate to Human Agent
Add a phrase detection (e.g., "speak to a human") that uses Twilio's `<Dial>` verb to transfer to a real agent.

---

## 💰 Cost Estimate

| Service | Cost |
|---------|------|
| Railway hobby plan | $5/month |
| Twilio phone number | $1.15/month |
| Twilio per-minute voice | ~$0.013/min inbound |
| Claude API (claude-sonnet-4-20250514) | ~$0.003 per call turn |
| **100 calls/month (5 min avg)** | **~$10–15/month total** |

---

## 🔧 Troubleshooting Deployment

**"Application Error" on Railway:**  
→ Check the Logs tab — usually a missing environment variable

**Twilio says "Application Error" when calling:**  
→ Make sure your Railway URL ends in `/voice` in Twilio settings  
→ Check that your `/health` endpoint returns 200 OK

**Agent says "technical difficulty":**  
→ Your `ANTHROPIC_API_KEY` is probably missing or incorrect

---

## 📁 File Structure

```
gotomeeting-voice-agent/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── Procfile           # Process definition for deployment
├── railway.toml       # Railway deployment config
└── README.md          # This file
```
