const sentenceInput = document.getElementById('sentenceInput');
const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById('stopButton');
const feedbackDiv = document.getElementById('feedback');

let mediaRecorder;
let audioChunks = [];
let audioStream; // 마이크 스트림을 저장할 변수

// 녹음 시작 버튼 클릭 이벤트 리스너
recordButton.addEventListener('click', async () => {
    const sentence = sentenceInput.value.trim();
    if (!sentence) {
        alert('연습할 문장을 입력해주세요!');
        return;
    }

    try {
        // 사용자 마이크 접근 권한 요청
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // MediaRecorder를 사용하여 오디오 스트림을 녹음합니다.
        // 'audio/webm;codecs=opus'는 웹에서 일반적으로 사용되는 효율적인 오디오 형식입니다.
        mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm;codecs=opus' });

        audioChunks = []; // 새로운 녹음을 위해 이전 데이터 초기화

        // 데이터가 사용 가능할 때마다 청크를 저장합니다.
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        // 녹음이 중지되었을 때 실행될 로직
        mediaRecorder.onstop = async () => {
            // 녹음된 오디오 청크들을 하나의 Blob 객체로 합칩니다.
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            // Blob과 원본 문장을 백엔드 서버로 전송합니다.
            sendAudioToServer(audioBlob, sentence);
        };

        // 녹음 시작
        mediaRecorder.start();
        recordButton.disabled = true; // 녹음 중에는 녹음 시작 버튼 비활성화
        stopButton.disabled = false;  // 녹음 중지 버튼 활성화
        feedbackDiv.innerHTML = '✨ 녹음 중... 연습할 문장을 또박또박 발음해주세요! ✨';

    } catch (err) {
        console.error('마이크 접근 오류:', err);
        alert('마이크 접근 권한을 허용해주세요. (브라우저 설정 확인)');
    }
});

// 녹음 중지 버튼 클릭 이벤트 리스너
stopButton.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop(); // 녹음 중지
        // 마이크 스트림 트랙을 정지하여 마이크 아이콘을 끄고 리소스 해제
        audioStream.getTracks().forEach(track => track.stop());
    }
    recordButton.disabled = false; // 녹음 중지 후 녹음 시작 버튼 활성화
    stopButton.disabled = true;  // 녹음 중지 버튼 비활성화
    feedbackDiv.innerHTML = '⏳ 음성 분석 중... 잠시만 기다려주세요! ⏳';
});

// 백엔드 서버로 음성 데이터와 문장 전송 함수
async function sendAudioToServer(audioBlob, sentence) {
    const formData = new FormData();
    // FormData에 오디오 Blob과 원본 문장을 추가합니다.
    formData.append('audio', audioBlob, 'pronunciation.webm'); // 파일 이름은 확장자 맞춰줍니다.
    formData.append('sentence', sentence);

    try {
        // Flask 백엔드의 '/analyze-pronunciation' 엔드포인트로 POST 요청을 보냅니다.
        const response = await fetch('/analyze-pronunciation', {
            method: 'POST',
            body: formData // FormData 객체는 자동으로 'multipart/form-data'로 설정됩니다.
        });

        // 응답 상태가 성공(2xx)이 아니면 오류를 발생시킵니다.
        if (!response.ok) {
            const errorText = await response.text(); // 서버에서 보낸 오류 메시지 확인
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }

        const data = await response.json(); // 서버 응답을 JSON 형태로 파싱합니다.
        // 받은 피드백을 화면에 표시합니다.
        feedbackDiv.innerHTML = `<h3>📢 Gemini의 피드백:</h3> ${data.feedback || '피드백을 받을 수 없습니다.'}`;

    } catch (error) {
        console.error('음성 전송 또는 분석 오류:', error);
        feedbackDiv.innerHTML = `🚨 오류가 발생했습니다. 다시 시도해주세요.<br>오류 내용: ${error.message}`;
    }
}