from flask import Flask, Response
from flask_socketio import SocketIO
import subprocess
import queue

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# طابور لتخزين الصوت المستلم من المتصفح
audio_queue = queue.Queue()

# معالجة الصوت وتحويله إلى MP3 باستخدام FFmpeg
def process_audio():
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-f", "s16le",
            "-ar", "44100",
            "-ac", "1",
            "-i", "pipe:0",
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            "-f", "mp3",
            "pipe:1"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    while True:
        if not audio_queue.empty():
            chunk = audio_queue.get()
            process.stdin.write(chunk)
            yield process.stdout.read(1024)

@app.route("/stream")
def stream():
    return Response(process_audio(), mimetype="audio/mpeg")

@socketio.on("audio")
def handle_audio(data):
    audio_queue.put(data)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
