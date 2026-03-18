from flask import Flask, render_template_string, jsonify, send_file, request, Response
import random
import os
import tempfile
import base64
import subprocess
from gtts import gTTS

app = Flask(__name__)

storage = {}
video_storage = {}

scenarios = [
    {
        "title": "🖥️ المروحة المتسخة",
        "image": "https://images.unsplash.com/photo-1587202372634-32705e3e568e?w=1080&h=1920&fit=crop",
        "lines": ["أنا أموت هنا!", "3 سنوات وما نظفوني", "الغبار خانقني", "ساعدوني يا ناس!"]
    },
    {
        "title": "🔋 البطارية المحتضرة",
        "image": "https://images.unsplash.com/photo-1622436232671-e77f3c1ce909?w=1080&h=1920&fit=crop",
        "lines": ["واحد بالمية!", "تتكلم 3 ساعات", "وتقول بس 5 دقايق", "أنا ضحية!"]
    },
    {
        "title": "💾 الـ USB المحتار",
        "image": "https://images.unsplash.com/photo-1527430253228-e93688616381?w=1080&h=1920&fit=crop",
        "lines": ["الوجه الأول لا", "اقلبني لا", "ارجع الوجه الأول ايوه", "كيف؟!"]
    }
]

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    scenario = random.choice(scenarios)
    session_id = request.headers.get('X-Session-ID', 'sess_' + str(int(os.urandom(4).hex(), 16)))
    storage[session_id] = scenario
    return jsonify(scenario)

@app.route("/create_video", methods=['POST'])
def create_video():
    """إنشاء فيديو كامل في السيرفر (Render)"""
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        scenario = storage.get(session_id)
        
        if not scenario:
            return jsonify({"error": "لا يوجد سيناريو"}), 400
        
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        
        # 1. تحميل الصورة
        img_path = os.path.join(temp_dir, "image.jpg")
        os.system(f"curl -L -o {img_path} '{scenario['image']}'")
        
        # 2. إنشاء الصوت لكل سطر (gTTS - مجاني)
        audio_files = []
        for i, line in enumerate(scenario['lines']):
            audio_path = os.path.join(temp_dir, f"audio_{i}.mp3")
            tts = gTTS(text=line, lang='ar', slow=False)
            tts.save(audio_path)
            audio_files.append(audio_path)
        
        # 3. دمج الصوت في ملف واحد
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for audio in audio_files:
                f.write(f"file '{audio}'\n")
        
        full_audio = os.path.join(temp_dir, "full_audio.mp3")
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0", 
            "-i", concat_file, "-y", full_audio
        ], check=True, capture_output=True)
        
        # 4. إنشاء فيديو من الصورة + الصوت
        output_path = os.path.join(temp_dir, "output.mp4")
        
        # مدة كل سطر (نقدر نحسبها من حجم الملف الصوتي)
        # بشكل مبسط: كل سطر 3 ثواني
        duration = len(scenario['lines']) * 3
        
        ffmpeg_cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", img_path,
            "-i", full_audio,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-t", str(duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-movflags", "+faststart",
            "-y",
            output_path
        ]
        
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        
        # 5. إضافة نصوص على الفيديو (اختياري)
        final_output = os.path.join(temp_dir, "final.mp4")
        
        # فلتر drawtext لكل سطر
        drawtext_filters = []
        for i, line in enumerate(scenario['lines']):
            start = i * 3
            end = start + 3
            # تخطي النص العربي (FFmpeg ما يدعم العربي بشكل كامل)
            # بديل: نستخدم الصور أو نترك بدون نص
        
        video_storage[session_id] = output_path
        
        return jsonify({
            "status": "done",
            "duration": duration,
            "url": f"/video_file?session={session_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video_file")
def video_file():
    session_id = request.args.get('session', 'default')
    path = video_storage.get(session_id)
    
    if not path or not os.path.exists(path):
        return "الفيديو غير موجود", 404
    
    def generate():
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                yield chunk
    
    return Response(generate(), mimetype='video/mp4')

@app.route("/download")
def download():
    session_id = request.args.get('session', 'default')
    path = video_storage.get(session_id)
    
    if not path or not os.path.exists(path):
        return jsonify({"error": "الفيديو غير جاهز"}), 404
    
    return send_file(
        path,
        as_attachment=True,
        download_name="talking_video.mp4",
        mimetype="video/mp4"
    )

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Videos - Render</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
}
.container { max-width: 500px; margin: 0 auto; padding: 20px; }
.header {
    text-align: center;
    padding: 30px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: -20px -20px 30px -20px;
}
h1 { font-size: 24px; }
.card {
    background: #1a1a1a;
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
}
.btn {
    width: 100%;
    padding: 18px;
    border: none;
    border-radius: 16px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    margin: 10px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.btn:disabled { opacity: 0.5; }
.scenario-img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 12px;
    margin-bottom: 15px;
}
.line {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
}
video { width: 100%; border-radius: 16px; margin-top: 20px; }
.status {
    text-align: center;
    padding: 20px;
    background: rgba(102, 126, 234, 0.2);
    border-radius: 12px;
    margin: 15px 0;
    display: none;
}
.status.active { display: block; }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎭 AI Talking Videos</h1>
        <p style="opacity: 0.9; margin-top: 10px;">يعمل على Render ✅</p>
    </div>
    
    <div class="card">
        <button class="btn" onclick="generate()" id="genBtn">🎲 توليد سيناريو</button>
        <div id="scenarioDisplay"></div>
    </div>
    
    <div class="card" id="createCard" style="display: none;">
        <button class="btn" onclick="createVideo()" id="createBtn">🎬 إنشاء الفيديو</button>
        <div class="status" id="status">⏳ جاري إنشاء الفيديو في السيرفر...</div>
    </div>
    
    <div class="card" id="videoCard" style="display: none;">
        <video id="videoPlayer" controls playsinline></video>
        <button class="btn" onclick="downloadVideo()" style="margin-top: 15px;">⬇️ تحميل الفيديو</button>
    </div>
</div>

<script>
const sessionId = 'sess_' + Date.now();
let currentScenario = null;

function generate() {
    const btn = document.getElementById('genBtn');
    btn.disabled = true;
    btn.innerText = '⏳...';
    
    fetch('/generate', { headers: { 'X-Session-ID': sessionId } })
    .then(r => r.json())
    .then(data => {
        currentScenario = data;
        
        document.getElementById('scenarioDisplay').innerHTML = `
            <div style="margin-top: 15px;">
                <img src="${data.image}" class="scenario-img">
                <h3 style="margin-bottom: 15px;">${data.title}</h3>
                ${data.lines.map(l => `<div class="line">💬 ${l}</div>`).join('')}
            </div>
        `;
        
        document.getElementById('createCard').style.display = 'block';
        btn.innerText = '🎲 توليد سيناريو';
        btn.disabled = false;
    });
}

async function createVideo() {
    const btn = document.getElementById('createBtn');
    const status = document.getElementById('status');
    
    btn.disabled = true;
    status.classList.add('active');
    status.innerText = '⏳ جاري إنشاء الصوت والفيديو... (قد يستغرق 30-60 ثانية)';
    
    const res = await fetch('/create_video', {
        method: 'POST',
        headers: {
            'X-Session-ID': sessionId,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scenario: currentScenario })
    });
    
    const data = await res.json();
    
    if (data.status === 'done') {
        status.innerText = '✅ تم الإنشاء!';
        
        const video = document.getElementById('videoPlayer');
        video.src = data.url;
        document.getElementById('videoCard').style.display = 'block';
        
        setTimeout(() => {
            document.getElementById('videoCard').scrollIntoView({ behavior: 'smooth' });
        }, 100);
    } else {
        status.innerText = '❌ خطأ: ' + (data.error || 'فشل الإنشاء');
    }
    
    btn.disabled = false;
}

function downloadVideo() {
    window.open(`/download?session=${sessionId}&t=${Date.now()}`, '_blank');
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
