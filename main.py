from flask import Flask, render_template_string, jsonify, send_file, request, Response
import random
import os
import tempfile
import base64
import subprocess

app = Flask(__name__)

storage = {}
video_storage = {}

ideas = [
    "3 أشياء مستحيل تعرفها",
    "سر خطير محد يقولك", 
    "وش يصير لو ما نمت يومين؟",
    "أغرب حقيقة في العالم",
    "لماذا نتثاءب؟",
    "سر النجاح في 30 ثانية",
    "أغرب طعام في العالم",
    "هل تعلم؟",
    "خطأ فادح يرتكبه الجميع",
    "السر اللي ما يعرفه أحد",
    "لا تسوي كذا أبداً",
    "معلومة صادمة"
]

scripts = [
    ["واحد...", "اثنين...", "ثلاثة... انتهى!"],
    ["هل تعلم أن...", "في شيء غريب...", "تابع للنهاية"],
    ["99% ما يعرفون...", "لكن الحقيقة...", "صدمة"],
    ["هذا الشيء خطير...", "انتبه له...", "لا تسوي كذا"],
    ["انتبه...", "الحين جاي الصدمة...", "شوف بنفسك"],
    ["الكل يظن...", "بس الواقع...", "غير كذا تماماً"]
]

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    idea = random.choice(ideas)
    script = random.choice(scripts)
    
    session_id = request.headers.get('X-Session-ID', 'default')
    storage[session_id] = {"idea": idea, "script": script}
    video_storage[session_id] = None
    
    return jsonify({"idea": idea, "script": script})

@app.route("/upload_video", methods=['POST'])
def upload_video():
    """استقبال الفيديو من المتصفح"""
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        data = request.get_json()
        
        if not data or 'video' not in data:
            return jsonify({"error": "لا يوجد فيديو"}), 400
        
        # فك تشفير base64
        video_data = data['video'].split(',')[1] if ',' in data['video'] else data['video']
        video_bytes = base64.b64decode(video_data)
        
        # حفظ في /tmp
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        webm_path = os.path.join(temp_dir, "video.webm")
        mp4_path = os.path.join(temp_dir, "video.mp4")
        
        with open(webm_path, "wb") as f:
            f.write(video_bytes)
        
        # محاولة تحويل لـ MP4 باستخدام FFmpeg لو موجود
        try:
            subprocess.run([
                "ffmpeg", "-i", webm_path, 
                "-c:v", "libx264", "-preset", "fast",
                "-movflags", "+faststart",
                "-y", mp4_path
            ], check=True, capture_output=True, timeout=30)
            
            if os.path.exists(mp4_path) and os.path.getsize(mp4_path) > 1000:
                final_path = mp4_path
                os.remove(webm_path)  # مسح الـ webm
            else:
                final_path = webm_path
        except:
            # لو FFmpeg ما اشتغل، نرجع WebM
            final_path = webm_path
        
        video_storage[session_id] = final_path
        
        return jsonify({
            "status": "done",
            "duration": data.get('duration', 0)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video_file")
def video_file():
    session_id = request.headers.get('X-Session-ID', 'default')
    path = video_storage.get(session_id)
    
    if not path or not os.path.exists(path):
        return "الفيديو غير موجود", 404
    
    def generate():
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                yield chunk
    
    mime = 'video/mp4' if path.endswith('.mp4') else 'video/webm'
    return Response(generate(), mimetype=mime)

@app.route("/download")
def download():
    session_id = request.headers.get('X-Session-ID', 'default')
    path = video_storage.get(session_id)
    
    if not path or not os.path.exists(path):
        return jsonify({"error": "الفيديو غير جاهز"}), 404
    
    ext = 'mp4' if path.endswith('.mp4') else 'webm'
    return send_file(
        path,
        as_attachment=True,
        download_name=f"tiktok_video.{ext}",
        mimetype=f"video/{ext}"
    )

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>TikTok Bot</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    color: #fff;
    min-height: 100vh;
    padding-bottom: 30px;
}
.container { max-width: 500px; margin: auto; padding: 20px; }
.header {
    text-align: center;
    padding: 30px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 0 0 30px 30px;
    margin: -20px -20px 30px -20px;
}
h1 { font-size: 28px; font-weight: bold; }
.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}
.card h3 { font-size: 20px; margin-bottom: 15px; color: #a78bfa; }
.idea-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 15px;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
}
.script-line {
    background: rgba(102, 126, 234, 0.2);
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    font-size: 18px;
    border-right: 4px solid #667eea;
    text-align: center;
}
.btn {
    width: 100%;
    padding: 18px;
    border: none;
    border-radius: 15px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    margin: 10px 0;
    transition: all 0.3s;
}
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.btn-secondary {
    background: rgba(255,255,255,0.1);
    color: white;
    border: 2px solid #667eea;
}
.btn:disabled { opacity: 0.5; }
.video-container {
    margin-top: 20px;
    border-radius: 20px;
    overflow: hidden;
    background: black;
    display: none;
    position: relative;
}
video { width: 100%; display: block; }
#canvas { display: none; }
.status-bar {
    padding: 15px;
    border-radius: 12px;
    margin: 15px 0;
    text-align: center;
    font-weight: bold;
    display: none;
}
.status-bar.show { display: block; }
.status-bar.success { background: #10b981; }
.status-bar.error { background: #ef4444; }
.status-bar.loading { background: #3b82f6; }
.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-left: 10px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.recording-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background: red;
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    display: none;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎬 TikTok Bot</h1>
    </div>
    
    <div class="card">
        <h3>💡 الفكرة</h3>
        <button class="btn btn-primary" onclick="generate()" id="genBtn">🔄 توليد فكرة</button>
        <div class="idea-box" id="idea">اضغط "توليد" للبدء</div>
    </div>
    
    <div class="card">
        <h3>📝 السكربت</h3>
        <div id="script"><div class="script-line" style="opacity: 0.5;">...</div></div>
    </div>
    
    <div class="card">
        <h3>🎥 الفيديو</h3>
        <button class="btn btn-primary" onclick="startRecording()" id="recordBtn" disabled>
            🎬 تسجيل الفيديو
        </button>
        <button class="btn btn-secondary" onclick="downloadVideo()" id="downloadBtn" disabled>
            ⬇️ تحميل الفيديو
        </button>
        
        <div id="status" class="status-bar"></div>
        
        <div id="videoContainer" class="video-container">
            <div class="recording-badge" id="recBadge">🔴 يتم التسجيل</div>
            <video id="preview" controls playsinline></video>
        </div>
        
        <canvas id="canvas" width="720" height="1280"></canvas>
    </div>
</div>

<script>
const sessionId = 'sess_' + Date.now();
let currentData = null;
let mediaRecorder = null;
let recordedChunks = [];

function showStatus(msg, type) {
    const s = document.getElementById('status');
    s.innerHTML = type === 'loading' ? msg + '<span class="spinner"></span>' : msg;
    s.className = 'status-bar show ' + type;
}

function generate() {
    document.getElementById('genBtn').disabled = true;
    showStatus('جاري التوليد...', 'loading');
    
    fetch('/generate', { headers: { 'X-Session-ID': sessionId } })
    .then(r => r.json())
    .then(data => {
        currentData = data;
        document.getElementById('idea').innerText = data.idea;
        document.getElementById('script').innerHTML = data.script.map(line => 
            `<div class="script-line">${line}</div>`
        ).join('');
        
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('videoContainer').style.display = 'none';
        
        showStatus('✅ تم التوليد!', 'success');
        setTimeout(() => document.getElementById('status').className = 'status-bar', 2000);
        document.getElementById('genBtn').disabled = false;
    });
}

async function startRecording() {
    if (!currentData) return;
    
    const btn = document.getElementById('recordBtn');
    btn.disabled = true;
    showStatus('جاري تحضير التسجيل...', 'loading');
    
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const stream = canvas.captureStream(30); // 30 FPS
    
    // إعدادات التسجيل
    const options = { mimeType: 'video/webm;codecs=vp9' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'video/webm;codecs=vp8';
    }
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'video/webm';
    }
    
    mediaRecorder = new MediaRecorder(stream, options);
    recordedChunks = [];
    
    mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) recordedChunks.push(e.data);
    };
    
    mediaRecorder.onstop = async () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        
        // عرض الفيديو
        const video = document.getElementById('preview');
        video.src = url;
        document.getElementById('videoContainer').style.display = 'block';
        document.getElementById('recBadge').style.display = 'none';
        
        showStatus('⬆️ جاري رفع الفيديو...', 'loading');
        
        // تحويل لـ base64 ورفعه
        const reader = new FileReader();
        reader.onloadend = async () => {
            const base64 = reader.result;
            
            const res = await fetch('/upload_video', {
                method: 'POST',
                headers: {
                    'X-Session-ID': sessionId,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    video: base64,
                    duration: 8
                })
            });
            
            const result = await res.json();
            if (result.status === 'done') {
                showStatus('✅ تم حفظ الفيديو!', 'success');
                document.getElementById('downloadBtn').disabled = false;
                btn.disabled = false;
            } else {
                showStatus('❌ فشل الرفع', 'error');
                btn.disabled = false;
            }
        };
        reader.readAsDataURL(blob);
    };
    
    // بدء التسجيل
    mediaRecorder.start(100); // جمع البيانات كل 100ms
    
    // رسم الفيديو
    await renderVideo(ctx, canvas, currentData);
    
    // إيقاف التسجيل بعد 8 ثواني
    setTimeout(() => {
        if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    }, 8000);
}

async function renderVideo(ctx, canvas, data) {
    const lines = [data.idea, ...data.script];
    const frameDuration = 2000; // 2 ثانية لكل سطر
    const startTime = Date.now();
    
    document.getElementById('recBadge').style.display = 'block';
    document.getElementById('videoContainer').style.display = 'block';
    
    function draw() {
        const elapsed = Date.now() - startTime;
        const currentIndex = Math.min(Math.floor(elapsed / frameDuration), lines.length - 1);
        
        // خلفية متدرجة
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, '#0f0c29');
        gradient.addColorStop(0.5, '#302b63');
        gradient.addColorStop(1, '#24243e');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // تأثيرات خفيفة
        ctx.save();
        ctx.globalAlpha = 0.1;
        for (let i = 0; i < 5; i++) {
            ctx.beginPath();
            ctx.arc(
                Math.random() * canvas.width,
                Math.random() * canvas.height,
                Math.random() * 100 + 50,
                0, Math.PI * 2
            );
            ctx.fillStyle = '#9d50bb';
            ctx.fill();
        }
        ctx.restore();
        
        // رسم النص
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // العنوان الرئيسي
        ctx.font = 'bold 60px -apple-system, sans-serif';
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 10;
        ctx.fillText(lines[0], canvas.width/2, canvas.height/2 - 100);
        
        // السطر الحالي من السكربت
        if (currentIndex > 0) {
            ctx.font = '50px -apple-system, sans-serif';
            ctx.fillStyle = '#a78bfa';
            ctx.fillText(lines[currentIndex], canvas.width/2, canvas.height/2 + 100);
        }
        
        // مؤشر التقدم
        const progress = (elapsed % frameDuration) / frameDuration;
        ctx.fillStyle = '#9d50bb';
        ctx.fillRect(50, canvas.height - 50, (canvas.width - 100) * progress, 10);
        
        if (elapsed < 8000) {
            requestAnimationFrame(draw);
        }
    }
    
    draw();
}

function downloadVideo() {
    // فتح الفيديو في تبويب جديد للتحميل
    window.open(`/download?t=${Date.now()}`, '_blank');
    showStatus('⬇️ جاري التحميل...', 'success');
}

// توليد تلقائي
window.onload = () => setTimeout(generate, 500);
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
