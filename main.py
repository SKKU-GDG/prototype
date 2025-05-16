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
                        "누락된 데이터입니다. 오디오 파일과 연습할 문장을 모두 제공해주세요."}), 400

    audio_file = request.files['audio']
    target_sentence = request.form['sentence']

    try:
        # 1. 녹음된 음성을 텍스트로 변환 (STT)
        audio_content = audio_file.read()
        audio_wav = speech.RecognitionAudio(content=audio_content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code='ko-KR',
        )

        stt_response = speech_client.recognize(config=config, audio=audio_wav)
        transcribed_text = ""

        if stt_response.results:
            transcribed_text = stt_response.results[0].alternatives[
                0].transcript

        if not transcribed_text:
            return jsonify(
                {"feedback": "음성을 텍스트로 변환할 수 없었습니다. 좀 더 명확하게 발음해 주세요."}), 200

        # 2. Gemini API를 사용한 피드백
        prompt = f"""
        당신은 한국어 발음 전문가입니다. 주어진 원본 문장과 사용자가 발음한 문장을 비교하여 발음 정확도에 대한 피드백을 제공해주세요.
        피드백은 다음 형식을 따릅니다:
        1. **전반적인 평가:** 전반적인 발음이 어떤지 간략하게 평가해주세요.
        2. **구체적인 개선점:** 어떤 단어 또는 음절의 발음이 원본과 달랐는지 구체적으로 지적하고, 어떻게 수정해야 할지 설명을 덧붙여주세요.
        3. **다음 연습 팁:** 전반적인 발음 향상을 위한 간단한 팁을 하나 제공해주세요.

        원본 문장: "{target_sentence}"
        사용자가 발음한 문장: "{transcribed_text}"

        피드백:
        """
        gemini_response = gemini_model.generate_content(prompt)
        feedback = gemini_response.text

        return jsonify({
            "feedback": feedback,
            "transcribed_text": transcribed_text
        }), 200

    except Exception as e:
        print(f"오류 발생: {e}")
        return jsonify({"feedback": f"처리 중 오류가 발생했습니다: {str(e)}."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
