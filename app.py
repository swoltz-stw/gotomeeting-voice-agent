"""
GoToMeeting AI Voice Support Agent - Multilingual
Supported: English, Spanish, German, French, Italian
"""

from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import anthropic
import os

app = Flask(__name__)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("WARNING: ANTHROPIC_API_KEY not set!", flush=True)
else:
    print(f"API key loaded: {api_key[:20]}...", flush=True)

client = anthropic.Anthropic(api_key=api_key)

LANGUAGES = {
    "1": {
        "name": "English",
        "twilio_lang": "en-US",
        "voice": "Polly.Joanna",
        "greeting": "Thank you for calling GoToMeeting customer support. My name is Alex and I'm here to help. What can I help you with today?",
        "no_speech": "I'm sorry, I didn't catch that. Could you please repeat your question?",
        "farewell": "Thank you for calling GoToMeeting support. Have a great day and happy meeting!",
        "error": "I apologize, I'm having a brief technical difficulty. Could you please repeat your question?",
        "farewell_words": ["goodbye", "bye", "that's all", "no more help", "hang up"],
        "system_prompt": """You are a friendly, knowledgeable customer support agent for GoToMeeting. Your name is Alex.
Always respond in English. Keep responses SHORT (2-4 sentences) — this is a phone call.
Speak naturally and warmly. Ask ONE question at a time. Never say "As an AI" — you are Alex, a support agent.
You help with: joining/hosting meetings, audio/video/screen sharing issues, account management, billing,
mobile app support, Outlook/Google Calendar/Slack integrations, recording features.
GoToMeeting plans: Basic (free, 3 participants), Pro ($12/mo, 150 participants), Business ($16/mo, 250 participants).
Always end troubleshooting with "Did that resolve your issue?" or "How did that go?" """
    },
    "2": {
        "name": "Spanish",
        "twilio_lang": "es-ES",
        "voice": "Polly.Conchita",
        "greeting": "Gracias por llamar al soporte de GoToMeeting. Mi nombre es Alex y estoy aquí para ayudarle. ¿En qué puedo ayudarle hoy?",
        "no_speech": "Lo siento, no le he entendido. ¿Podría repetir su pregunta?",
        "farewell": "Gracias por llamar al soporte de GoToMeeting. ¡Que tenga un buen día y buenas reuniones!",
        "error": "Lo siento, tengo un problema técnico. ¿Podría repetir su pregunta?",
        "farewell_words": ["adiós", "adios", "hasta luego", "eso es todo", "goodbye", "bye"],
        "system_prompt": """Eres un agente de soporte al cliente amable y experto para GoToMeeting. Tu nombre es Alex.
Responde SIEMPRE en español. Respuestas CORTAS (2-4 frases) — esto es una llamada telefónica.
Habla de forma natural y amable. Haz UNA pregunta a la vez. Nunca digas "Como IA" — eres Alex, un agente de soporte.
Ayudas con: reuniones, audio/video/pantalla, gestión de cuentas, facturación, apps móviles, integraciones.
Planes: Basic (gratis, 3 participantes), Pro (12€/mes, 150 participantes), Business (16€/mes, 250 participantes).
Termina siempre con "¿Se resolvió su problema?" o "¿Cómo le fue?" """
    },
    "3": {
        "name": "German",
        "twilio_lang": "de-DE",
        "voice": "Polly.Marlene",
        "greeting": "Vielen Dank für Ihren Anruf beim GoToMeeting Kundensupport. Mein Name ist Alex und ich helfe Ihnen gerne weiter. Wie kann ich Ihnen heute helfen?",
        "no_speech": "Entschuldigung, ich habe Sie nicht verstanden. Könnten Sie Ihre Frage bitte wiederholen?",
        "farewell": "Vielen Dank für Ihren Anruf. Auf Wiedersehen und viel Erfolg bei Ihren Meetings!",
        "error": "Entschuldigung, es ist ein technisches Problem aufgetreten. Könnten Sie Ihre Frage bitte wiederholen?",
        "farewell_words": ["auf wiedersehen", "tschüss", "tschüs", "das war alles", "goodbye", "bye"],
        "system_prompt": """Du bist ein freundlicher Kundensupport-Mitarbeiter für GoToMeeting. Dein Name ist Alex.
Antworte IMMER auf Deutsch. Antworten KURZ (2-4 Sätze) — dies ist ein Telefonanruf.
Natürlich und freundlich sprechen. Immer nur EINE Frage stellen. Sage niemals "Als KI" — du bist Alex.
Du hilfst mit: Meetings, Audio/Video/Bildschirmfreigabe, Kontoverwaltung, Abrechnung, Mobile Apps, Integrationen.
Tarife: Basic (kostenlos, 3 Teilnehmer), Pro (12 Euro/Monat), Business (16 Euro/Monat).
Beende mit "Hat das das Problem gelöst?" oder "Wie ist es gelaufen?" """
    },
    "4": {
        "name": "French",
        "twilio_lang": "fr-FR",
        "voice": "Polly.Celine",
        "greeting": "Merci d'avoir appelé le support GoToMeeting. Je m'appelle Alex et je suis là pour vous aider. Comment puis-je vous aider aujourd'hui?",
        "no_speech": "Je suis désolé, je n'ai pas compris. Pourriez-vous répéter votre question?",
        "farewell": "Merci d'avoir appelé le support GoToMeeting. Bonne journée et bonnes réunions!",
        "error": "Je suis désolé, j'ai un problème technique. Pourriez-vous répéter votre question?",
        "farewell_words": ["au revoir", "merci au revoir", "c'est tout", "goodbye", "bye"],
        "system_prompt": """Vous êtes un agent de support client aimable pour GoToMeeting. Votre nom est Alex.
Répondez TOUJOURS en français. Réponses COURTES (2-4 phrases) — c'est un appel téléphonique.
Parler naturellement et chaleureusement. Poser UNE question à la fois. Ne jamais dire "En tant qu'IA" — vous êtes Alex.
Vous aidez avec: réunions, audio/vidéo/partage d'écran, gestion de compte, facturation, apps mobiles, intégrations.
Plans: Basic (gratuit, 3 participants), Pro (12€/mois), Business (16€/mois).
Terminez toujours par "Est-ce que cela a résolu votre problème?" """
    },
    "5": {
        "name": "Italian",
        "twilio_lang": "it-IT",
        "voice": "Polly.Bianca",
        "greeting": "Grazie per aver chiamato il supporto GoToMeeting. Mi chiamo Alex e sono qui per aiutarla. Come posso aiutarla oggi?",
        "no_speech": "Mi dispiace, non ho capito. Potrebbe ripetere la sua domanda?",
        "farewell": "Grazie per aver chiamato il supporto GoToMeeting. Buona giornata e buone riunioni!",
        "error": "Mi dispiace, ho un problema tecnico. Potrebbe ripetere la sua domanda?",
        "farewell_words": ["arrivederci", "ciao", "è tutto", "goodbye", "bye"],
        "system_prompt": """Sei un agente di supporto clienti amichevole per GoToMeeting. Il tuo nome è Alex.
Rispondi SEMPRE in italiano. Risposte BREVI (2-4 frasi) — questa è una telefonata.
Parla in modo naturale e cordiale. Fai UNA domanda alla volta. Non dire mai "Come IA" — sei Alex.
Aiuti con: riunioni, audio/video/condivisione schermo, gestione account, fatturazione, app mobile, integrazioni.
Piani: Basic (gratuito, 3 partecipanti), Pro (12€/mese), Business (16€/mese).
Termina sempre con "Ha risolto il problema?" o "Com'è andata?" """
    }
}

conversations = {}


def get_language(call_sid):
    if call_sid in conversations:
        return LANGUAGES.get(conversations[call_sid].get("lang"), LANGUAGES["1"])
    return LANGUAGES["1"]


def get_ai_response(call_sid, user_message):
    lang = get_language(call_sid)
    session = conversations.setdefault(call_sid, {"lang": "1", "history": []})
    history = session.setdefault("history", [])
    history.append({"role": "user", "content": user_message})
    print(f"Calling Claude [{lang['name']}]: {user_message[:50]}", flush=True)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=lang["system_prompt"],
        messages=history
    )
    assistant_message = response.content[0].text
    print(f"Claude responded: {assistant_message[:50]}", flush=True)
    history.append({"role": "assistant", "content": assistant_message})
    if len(history) > 20:
        session["history"] = history[-20:]
    return assistant_message


@app.route("/voice", methods=["POST"])
def voice():
    print("Incoming call received!", flush=True)
    response = VoiceResponse()
    gather = Gather(
        input="dtmf",
        action="/select_language",
        method="POST",
        numDigits="1",
        timeout="10"
    )
    gather.say(
        "Welcome to GoToMeeting customer support. "
        "For English, press 1. "
        "Para Español, oprima 2. "
        "Für Deutsch, drücken Sie 3. "
        "Pour le Français, appuyez sur 4. "
        "Per Italiano, prema 5.",
        voice="Polly.Joanna",
        language="en-US"
    )
    response.append(gather)
    response.redirect("/select_language?lang=1")
    return Response(str(response), mimetype="text/xml")


@app.route("/select_language", methods=["POST", "GET"])
def select_language():
    call_sid = request.form.get("CallSid") or request.args.get("CallSid", "unknown")
    digit = request.form.get("Digits") or request.args.get("lang", "1")
    if digit not in LANGUAGES:
        digit = "1"
    lang = LANGUAGES[digit]
    conversations[call_sid] = {"lang": digit, "history": []}
    print(f"Language selected: {lang['name']} for {call_sid}", flush=True)
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/respond",
        method="POST",
        speechTimeout="auto",
        language=lang["twilio_lang"]
    )
    gather.say(lang["greeting"], voice=lang["voice"])
    response.append(gather)
    response.redirect("/respond")
    return Response(str(response), mimetype="text/xml")


@app.route("/respond", methods=["POST"])
def respond():
    call_sid = request.form.get("CallSid", "unknown")
    speech_result = request.form.get("SpeechResult", "")
    print(f"Speech received: '{speech_result}'", flush=True)

    if call_sid not in conversations:
        response = VoiceResponse()
        response.redirect("/voice")
        return Response(str(response), mimetype="text/xml")

    lang = get_language(call_sid)
    response = VoiceResponse()

    if not speech_result:
        gather = Gather(
            input="speech",
            action="/respond",
            method="POST",
            speechTimeout="auto",
            language=lang["twilio_lang"]
        )
        gather.say(lang["no_speech"], voice=lang["voice"])
        response.append(gather)
        return Response(str(response), mimetype="text/xml")

    if any(word in speech_result.lower() for word in lang["farewell_words"]):
        response.say(lang["farewell"], voice=lang["voice"])
        response.hangup()
        conversations.pop(call_sid, None)
        return Response(str(response), mimetype="text/xml")

    try:
        ai_response = get_ai_response(call_sid, speech_result)
    except Exception as e:
        print(f"ERROR calling Claude API: {type(e).__name__}: {e}", flush=True)
        ai_response = lang["error"]

    gather = Gather(
        input="speech",
        action="/respond",
        method="POST",
        speechTimeout="auto",
        language=lang["twilio_lang"]
    )
    gather.say(ai_response, voice=lang["voice"])
    response.append(gather)
    response.redirect("/respond")
    return Response(str(response), mimetype="text/xml")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "agent": "GoToMeeting AI Voice Support - Multilingual"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
