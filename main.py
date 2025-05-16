import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import speech_v1p1beta1 as speech

# .env 파일에서 환경 변수를 로드합니다. Replit의 경우 'Secrets'에 설정된 값을 자동으로 가져옵니다.
load_dotenv()

app = Flask(__name__)

# Google Cloud Speech-to-Text 클라이언트 초기화
# Replit 'Secrets'에 GOOGLE_CLOUD_SPEECH_API_KEY를 설정했다면 아래처럼 API 키로 초기화할 수 있습니다.
# (프로덕션 환경에서는 서비스 계정 키 사용이 더 권장됩니다.)
speech_client = speech.SpeechClient(
    client_options={"api_key": os.getenv("GOOGLE_CLOUD_SPEECH_API_KEY")})

# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-pro')


@app.route('/')
def index():
    # 루트 경로로 접속하면 static 폴더 안에 있는 index.html 파일을 반환합니다.
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/analyze-pronunciation', methods=['POST'])
def analyze_pronunciation():
    # 요청에 오디오 파일과 원본 문장이 모두 포함되어 있는지 확인합니다.
    if 'audio' not in request.files or 'sentence' not in request.form:
        return jsonify({"feedback":
                        "누락된 데이터입니다. 오디오 파일과 연습할 문장을 모두 제공해주세요."}), 400

    audio_file = request.files['audio']
    target_sentence = request.form['sentence']


@app.route('/app.js')
def serve_js():
    return send_from_directory('static', 'app.js')

    # 1. 녹음된 음성을 텍스트로 변환 (STT: Speech-to-Text)
    audio_content = audio_file.read()
    audio_wav = speech.RecognitionAudio(content=audio_content)

    # JavaScript에서 'audio/webm;codecs=opus'로 녹음했으므로, 그에 맞춰 설정합니다.
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,  # Opus 코덱은 일반적으로 48000Hz 샘플링 레이트를 사용합니다.
        language_code='ko-KR',  # 한국어 발음을 인식하도록 설정합니다.
    )

    try:
        stt_response = speech_client.recognize(config=config, audio=audio_wav)
        transcribed_text = ""
        # STT 결과가 있을 경우, 첫 번째 결과의 텍스트를 가져옵니다.
        if stt_response.results:
            transcribed_text = stt_response.results[0].alternatives[
                0].transcript

        if not transcribed_text:
            return jsonify(
                {"feedback": "음성을 텍스트로 변환할 수 없었습니다. 좀 더 명확하게 발음해 주세요."}), 200

        # 2. Gemini API를 호출하여 발음 피드백을 받습니다.
        prompt = f"""
        당신은 한국어 발음 전문가입니다. 주어진 원본 문장과 사용자가 발음한 문장을 비교하여 발음 정확도에 대한 피드백을 제공해주세요.
        피드백은 다음 형식을 따릅니다:
        1. **전반적인 평가:** 전반적인 발음이 어떤지 간략하게 평가해주세요. (예: "매우 정확합니다!", "몇 가지 개선할 점이 있습니다.")
        2. **구체적인 개선점:** 어떤 단어 또는 음절의 발음이 원본과 달랐는지 구체적으로 지적하고, 어떻게 수정해야 할지 설명을 덧붙여주세요. (예: " '안녕'의 '녕' 발음이 '령'처럼 들렸습니다. 혀의 위치를 조금 더 낮춰 발음해보세요.")
        3. **다음 연습 팁:** 전반적인 발음 향상을 위한 간단한 팁을 하나 제공해주세요.

        이것은 발음 연습을 위한 것이며, 사용자가 좌절하지 않도록 **긍정적이고 건설적인 피드백**을 부탁드립니다.

        원본 문장: "{target_sentence}"
        사용자가 발음한 문장: "{transcribed_text}"

        피드백:
        """
        gemini_response = gemini_model.generate_content(prompt)
        feedback = gemini_response.text

        return jsonify({"feedback": feedback}), 200

    except Exception as e:
        print(f"오류 발생: {e}")
        return jsonify({"feedback": f"처리 중 오류가 발생했습니다: {str(e)}."}), 500


if __name__ == '__main__':
    # Flask 앱을 실행합니다. Replit은 기본적으로 0.0.0.0 주소와 8080 포트를 사용합니다.
    app.run(host='0.0.0.0', port=5000)
