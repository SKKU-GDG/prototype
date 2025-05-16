const sentenceInput = document.getElementById('sentenceInput');
const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById('stopButton');
const feedbackDiv = document.getElementById('feedback');

let mediaRecorder;
let audioChunks = [];
let audioStream;

recordButton.addEventListener('click', async () => {
    const sentence = sentenceInput.value.trim();
    if (!sentence) {
        alert('Please enter a sentence to practice!');
        return;
    }

    try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm;codecs=opus' });

        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudioToServer(audioBlob, sentence);
        };

        mediaRecorder.start();
        recordButton.disabled = true; 
        stopButton.disabled = false;  
        feedbackDiv.innerHTML = '✨ Recording... Please pronounce the sentence clearly! ✨';

    } catch (err) {
        console.error('Microphone access error:', err);
        alert('Please allow microphone access (check browser settings)');
    }
});

// Stop recording button click event listener
stopButton.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop(); // Stop recording
        // Stop microphone stream tracks to turn off mic icon and release resources
        audioStream.getTracks().forEach(track => track.stop());
    }
    recordButton.disabled = false; // 녹음 중지 후 녹음 시작 버튼 활성화
    stopButton.disabled = true;  // 녹음 중지 버튼 비활성화
    feedbackDiv.innerHTML = '⏳ Analyzing speech... Please wait a moment! ⏳';
});

// Function to send audio data and sentence to backend server
async function sendAudioToServer(audioBlob, sentence) {
    const formData = new FormData();
    // Add audio Blob and original sentence to FormData
    formData.append('audio', audioBlob, 'pronunciation.webm'); // File name with correct extension
    formData.append('sentence', sentence);

    try {
        // Send POST request to Flask backend '/analyze-pronunciation' endpoint
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
        feedbackDiv.innerHTML = `
            <h3>🎤 인식된 발음:</h3>
            <p class="transcribed-text">${data.transcribed_text || '음성을 인식할 수 없습니다.'}</p>
            <h3>📢 Gemini의 피드백:</h3>
            <p>${data.feedback || '피드백을 받을 수 없습니다.'}</p>`;

    } catch (error) {
        console.error('음성 전송 또는 분석 오류:', error);
        feedbackDiv.innerHTML = `🚨 An error occurred. Please try again.<br>Error details: ${error.message}`;
    }
}