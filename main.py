import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import speech_v1p1beta1 as speech

load_dotenv()

app = Flask(__name__)

speech_client = speech.SpeechClient(
    client_options={"api_key": os.getenv("GOOGLE_CLOUD_SPEECH_API_KEY")})

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/app.js')
def serve_js():
    return send_from_directory('static', 'app.js')


@app.route('/analyze-pronunciation', methods=['POST'])
def analyze_pronunciation():
    if 'audio' not in request.files or 'sentence' not in request.form:
        return jsonify({"feedback":
                        "Missing data. Please provide both audio file and practice sentence."}), 400

    audio_file = request.files['audio']
    target_sentence = request.form['sentence']

    try:
        # 1. Convert recorded audio to text (STT)
        audio_content = audio_file.read()
        audio_wav = speech.RecognitionAudio(content=audio_content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code='en-US',
        )

        stt_response = speech_client.recognize(config=config, audio=audio_wav)
        transcribed_text = ""

        if stt_response.results:
            transcribed_text = stt_response.results[0].alternatives[
                0].transcript

        if not transcribed_text:
            return jsonify(
                {"feedback": "Could not convert speech to text. Please speak more clearly."}), 200

        # 2. Generate feedback using Gemini API
        prompt = f"""
        I want you to act as a pronunciation coach.

        Here's the target sentence:
        Original: "{target_sentence}"

        Here's the user's pronunciation attempt:
        UserPronunciation: "{transcribed_text}"

        Please identify the pronunciation differences between the user's attempt and the original. For each mispronounced word or phoneme, provide:
        1. The correct phonetic transcription (IPA)
        2. A comparison with the user's mispronunciation
        3. Specific articulation tips — including mouth shape, tongue position, voicing, and airflow
        4. Optional visualizations or example comparisons, if useful

        The goal is to help the user pronounce the sentence naturally. Be clear and educational, using simple explanations if possible.
        """
        gemini_response = gemini_model.generate_content(prompt)
        feedback = gemini_response.text

        return jsonify({
            "feedback": feedback,
            "transcribed_text": transcribed_text
        }), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"feedback": f"An error occurred during processing: {str(e)}."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
