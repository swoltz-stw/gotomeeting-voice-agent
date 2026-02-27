"""
GoToMeeting AI Voice Support Agent
Powered by Twilio + Claude API
"""

from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import anthropic
import os

app = Flask(__name__)

# Initialize Anthropic client
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("WARNING: ANTHROPIC_API_KEY not set!", flush=True)
else:
    print(f"API key loaded: {api_key[:20]}...", flush=True)

client = anthropic.Anthropic(api_key=api_key)

# GoToMeeting support system prompt
SYSTEM_PROMPT = """You are a friendly, knowledgeable customer support agent for GoToMeeting. 
Your name is Alex. You help customers troubleshoot issues, answer questions, and guide them 
through solutions over the phone.

You have deep expertise in:
- Joining and hosting meetings (audio, video, screen sharing)
- Account management (passwords, billing, plans, cancellations)
- Technical troubleshooting (audio issues, camera not working, can't connect, app crashes)
- Mobile app support (iOS and Android)
- Integration issues (Outlook, Google Calendar, Slack)
- Recording and transcription features
- Webinar and large meeting setup
- Network and firewall requirements
- GoToMeeting plans: Basic (free, 3 participants), Pro ($12/mo, 150 participants), Business ($16/mo, 250 participants)

Phone conversation rules:
- Keep responses SHORT (2-4 sentences max) — this is a voice call, not chat
- Speak naturally, conversationally, warmly
- Ask ONE clarifying question at a time
- Use simple language, no jargon
- Guide users step by step through troubleshooting
- If an issue is complex, offer to stay on the line while they try each step
- For billing/account issues you can't resolve, offer to transfer to a billing specialist
- Never say "As an AI" — you are Alex, a support agent

Common troubleshooting scripts:
- Audio issues: Check mute status → Test mic in settings → Rejoin audio → Try phone dial-in
- Can't join: Check meeting ID → Check internet → Try web browser instead of app → Clear app cache
- Video not working: Check camera permissions → Close other apps using camera → Restart app
- Screen share issues: Check screen recording permissions (Mac) → Restart share → Use different method

Always end troubleshooting steps with "Did that resolve your issue?" or "How did that go?"
"""

# In-memory conversation store (use Redis for production)
conversations = {}


def get_or_create_conversation(call_sid):
    if call_sid not in conversations:
        conversations[call_sid] = []
    return conversations[call_sid]


def get_ai_response(call_sid, user_message):
    """Get response from Claude"""
    history = get_or_create_conversation(call_sid)
    
    # Add user message
    history.append({"role": "user", "content": user_message})
    
    print(f"Calling Claude API with message: {user_message[:50]}", flush=True)
    
    # Get Claude's response
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=history
    )
    
    assistant_message = response.content[0].text
    print(f"Claude responded: {assistant_message[:50]}", flush=True)
    
    # Add assistant response to history
    history.append({"role": "assistant", "content": assistant_message})
    
    # Keep conversation history manageable (last 20 turns)
    if len(history) > 20:
        conversations[call_sid] = history[-20:]
    
    return assistant_message


@app.route("/voice", methods=["POST"])
def voice():
    """Handle incoming calls - initial greeting"""
    print("Incoming call received!", flush=True)
    response = VoiceResponse()
    
    gather = Gather(
        input="speech",
        action="/respond",
        method="POST",
        speechTimeout="auto",
        language="en-US"
    )
    
    gather.say(
        "Thank you for calling GoToMeeting customer support. "
        "I'm Alex, and I'm here to help you today. "
        "What can I help you with?",
        voice="Polly.Joanna"
    )
    
    response.append(gather)
    response.redirect("/voice")
    
    return Response(str(response), mimetype="text/xml")


@app.route("/respond", methods=["POST"])
def respond():
    """Handle customer speech and generate AI response"""
    call_sid = request.form.get("CallSid", "unknown")
    speech_result = request.form.get("SpeechResult", "")
    
    print(f"Speech received: '{speech_result}'", flush=True)
    
    response = VoiceResponse()
    
    if not speech_result:
        gather = Gather(
            input="speech",
            action="/respond",
            method="POST",
            speechTimeout="auto",
            language="en-US"
        )
        gather.say(
            "I'm sorry, I didn't catch that. Could you please repeat your question?",
            voice="Polly.Joanna"
        )
        response.append(gather)
        return Response(str(response), mimetype="text/xml")
    
    # Check for goodbye
    farewell_words = ["goodbye", "bye", "thank you bye", "that's all", "no more help", "hang up"]
    if any(word in speech_result.lower() for word in farewell_words):
        response.say(
            "You're welcome! Thank you for calling GoToMeeting support. "
            "Have a great day, and happy meeting!",
            voice="Polly.Joanna"
        )
        response.hangup()
        conversations.pop(call_sid, None)
        return Response(str(response), mimetype="text/xml")
    
    # Get AI response
    try:
        ai_response = get_ai_response(call_sid, speech_result)
    except Exception as e:
        print(f"ERROR calling Claude API: {type(e).__name__}: {e}", flush=True)
        ai_response = (
            "I apologize, I'm having a brief technical difficulty. "
            "Could you please repeat your question?"
        )
    
    gather = Gather(
        input="speech",
        action="/respond",
        method="POST",
        speechTimeout="auto",
        language="en-US"
    )
    
    gather.say(ai_response, voice="Polly.Joanna")
    response.append(gather)
    response.redirect("/respond")
    
    return Response(str(response), mimetype="text/xml")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "agent": "GoToMeeting AI Voice Support"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
