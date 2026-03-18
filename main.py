from flask import Flask, render_template_string, jsonify, send_file, request, Response
import random
import os
import tempfile
import base64
import time

app = Flask(__name__)

storage = {}
video_storage = {}

# محتوى متنوع وطويل
content_database = {
    "facts": [
        {"title": "🧠 أذكى حيوان في العالم", "lines": ["الدلفين يستخدم أسماء", "كل دلفين له اسم خاص", "يتعرف على أصدقائه بعد 20 سنة!"]},
        {"title": "🌊 أعمق نقطة في المحيط", "lines": ["خندق ماريانا", "عمقها 11,000 متر", "فيها مخلوقات غريبة جداً"]},
        {"title": "🚀 سرعة الضوء", "lines": ["299,792 كم/ثانية", "تستطيع الدوران حول الأرض", "7 مرات في الثانية!"]},
        {"title": "🦕 عصر الديناصورات", "lines": ["استمر 165 مليون سنة", "الإنسان موجود من 300 ألف سنة فقط", "الديناصورات كانت تحكم الأرض"]},
        {"title": "🧬 DNA الإنسان", "lines": ["99.9% متشابه بين جميع البشر", "0.1% هي التي تجعلك فريداً", "طوله 2 متر إذا فُرِد!"]},
        {"title": "⚡ البرق", "lines": ["حرارته 5 أضعاف حرارة الشمس", "يضرب 8 مليون مرة يومياً", "الرعد صوت موجات صدمة"]},
        {"title": "🌋 البراكين", "lines": ["80% من البراكين تحت البحر", "أكبر بركان في المريخ", "أولمبوس مونس"]},
        {"title": "🐝 النحل", "lines": ["يزور 50-100 زهرة في الرحلة", "يحتاج لـ 2 مليون رحلة", "لكيلو عسل واحد!"]}
    ],
    "stories": [
        {"title": "📖 قصة النجاح", "lines": ["توماس إديسون فشل 1000 مرة", "قالوا له: استسلم", "قال: اكتشفت 1000 طريقة لا تعمل", "ثم اخترع المصباح الكهربائي!"]},
        {"title": "🏆 من الفشل للقمة", "lines": ["مايكل جوردن طرد من فريقه", "قالوا له: قصير للسلة", "صار أسطورة كرة السلة", "الأفضل في التاريخ!"]},
        {"title": "🎬 حلم هوليوود", "lines": ["ستيفن سبيلبرغ رُفض 3 مرات", "من كلية السينما", "صار أشهر مخرج في العالم", "جائزة الأوسكار 3 مرات!"]}
    ],
    "tips": [
        {"title": "💡 سر الإنتاجية", "lines": ["قاعدة 2 دقيقة", "لو ياخذ أقل من دقيقتين", "سويه الآن!", "ما تتراكم المهام"]},
        {"title": "🧘‍♂️ التركيز", "lines": ["تقنية البومودورو", "25 دقيقة تركيز", "5 دقائق راحة", "كرر 4 مرات"]},
        {"title": "💪 العادة السحرية", "lines": ["30 يوم متواصلة", "تكفي لتغيير حياتك", "ابدأ صغير", "استمر بثبات"]}
    ]
}

def get_random_content():
    category = random.choice(list(content_database.keys()))
    item = random.choice(content_database[category])
    return {
        "category": category,
        "title": item["title"],
        "lines": item["lines"],
        "duration": len(item["lines"]) * 3 + 2  # 3 ثواني لكل سطر + 2 ثواني مقدمة
    }

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    content = get_random_content()
    session_id = request.headers.get('X-Session-ID', 'default_' + str(int(time.time())))
    storage[session_id] = content
    video_storage[session_id] = None
    return jsonify(content)

@app.route("/upload_video", methods=['POST'])
def upload_video():
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        data = request.get_json()
        
        if not data or 'video' not in data:
            return jsonify({"error": "لا يوجد فيديو"}), 400
        
        video_data = data['video'].split(',')[1] if ',' in data['video'] else data['video']
        video_bytes = base64.b64decode(video_data)
        
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        video_path = os.path.join(temp_dir, "video.webm")
        
        with open(video_path, "wb") as f:
            f.write(video_bytes)
        
        video_storage[session_id] = {
            "path": video_path,
            "duration": data.get('duration', 0)
        }
        
        return jsonify({"status": "done", "duration": data.get('duration', 0)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video_file")
def video_file():
    session_id = request.headers.get('X-Session-ID', 'default')
    stored = video_storage.get(session_id)
    
    if not stored or not os.path.exists(stored["path"]):
        return "الفيديو غير موجود", 404
    
    def generate():
        with open(stored["path"], 'rb') as f:
            while chunk := f.read(8192):
                yield chunk
    
    return Response(generate(), mimetype='video/webm')

@app.route("/download")
def download():
    session_id = request.headers.get('X-Session-ID', 'default')
    stored = video_storage.get(session_id)
    
    if not stored or not os.path.exists(stored["path"]):
        return jsonify({"error": "الفيديو غير جاهز"}), 404
    
    return send_file(
        stored["path"],
        as_attachment=True,
        download_name="tiktok_video.webm",
        mimetype="video/webm"
    )

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>TikTok Pro Creator</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
    overflow-x: hidden;
}
.container { max-width: 600px; margin: 0 auto; padding: 20px; }
.header {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: -20px -20px 30px -20px;
    position: relative;
    overflow: hidden;
}
.header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    animation: move 20s linear infinite;
}
@keyframes move { from { transform: translate(0,0); } to { transform: translate(50px,50px); } }
h1 { font-size: 32px; position: relative; z-index: 1; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
.card {
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    padding: 25px;
    border-radius: 24px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.card h3 {
    font-size: 18px;
    color: #a78bfa;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.content-preview {
    background: rgba(102, 126, 234, 0.1);
    padding: 20px;
    border-radius: 16px;
    border-right: 4px solid #667eea;
}
.content-title {
    font-size: 24px;
    font-weight: bold;
    color: #fff;
    margin-bottom: 15px;
    line-height: 1.4;
}
.content-line {
    background: rgba(255,255,255,0.05);
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
    font-size: 16px;
    color: #e0e0e0;
    position: relative;
    padding-right: 30px;
}
.content-line::before {
    content: '→';
    position: absolute;
    right: 10px;
    color: #667eea;
}
.btn {
    width: 100%;
    padding: 18px 24px;
    border: none;
    border-radius: 16px;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    margin: 10px 0;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    position: relative;
    overflow: hidden;
}
.btn::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}
.btn:hover::before { left: 100%; }
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}
.btn-secondary {
    background: rgba(255,255,255,0.1);
    color: white;
    border: 2px solid #667eea;
}
.btn-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
.btn:active:not(:disabled) { transform: scale(0.98); }
.video-section {
    background: #000;
    border-radius: 24px;
    padding: 20px;
    margin-top: 20px;
    display: none;
}
.video-section.active { display: block; }
#canvas {
    width: 100%;
    border-radius: 16px;
    background: #000;
}
#previewVideo {
    width: 100%;
    border-radius: 16px;
    display: none;
}
.progress-bar {
    width: 100%;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    margin: 20px 0;
    overflow: hidden;
    display: none;
}
.progress-bar.active { display: block; }
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    width: 0%;
    transition: width 0.3s;
}
.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
}
.stat {
    text-align: center;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
}
.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #667eea;
}
.stat-label {
    font-size: 12px;
    color: #888;
    margin-top: 5px;
}
.recording-indicator {
    display: none;
    align-items: center;
    gap: 10px;
    color: #ef4444;
    font-weight: bold;
    margin-bottom: 15px;
}
.recording-indicator.active { display: flex; }
.rec-dot {
    width: 12px;
    height: 12px;
    background: #ef4444;
    border-radius: 50%;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎬 TikTok Pro</h1>
    </div>
    
    <div class="card">
        <h3>✨ المحتوى</h3>
        <button class="btn btn-primary" onclick="generateContent()" id="genBtn">
            🎲 توليد محتوى جديد
        </button>
        <div id="contentDisplay" style="display: none; margin-top: 20px;">
            <div class="content-preview">
                <div class="content-title" id="contentTitle"></div>
                <div id="contentLines"></div>
            </div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="durationStat">0</div>
                    <div class="stat-label">ثانية</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="linesStat">0</div>
                    <div class="stat-label">مشاهد</div>
                </div>
                <div class="stat">
                    <div class="stat-value">1080p</div>
                    <div class="stat-label">جودة</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card" id="createCard" style="display: none;">
        <h3>🎥 إنشاء الفيديو</h3>
        <div class="recording-indicator" id="recIndicator">
            <span class="rec-dot"></span>
            <span>يتم التسجيل...</span>
        </div>
        <button class="btn btn-success" onclick="createVideo()" id="createBtn">
            🎬 ابدأ الإنشاء
        </button>
        <div class="progress-bar" id="progressBar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
    </div>
    
    <div class="video-section" id="videoSection">
        <canvas id="canvas" width="1080" height="1920"></canvas>
        <video id="previewVideo" controls playsinline></video>
    </div>
    
    <div class="card" id="downloadCard" style="display: none;">
        <h3>⬇️ التحميل</h3>
        <button class="btn btn-secondary" onclick="downloadVideo()" id="downloadBtn">
            💾 تحميل الفيديو
        </button>
        <button class="btn btn-primary" onclick="shareVideo()" id="shareBtn" style="display: none;">
            📤 مشاركة
        </button>
    </div>
</div>

<script>
const sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
let currentContent = null;
let mediaRecorder = null;
let recordedChunks = [];
let animationId = null;

// إعدادات الفيديو
const CONFIG = {
    width: 1080,
    height: 1920,
    fps: 60,
    sceneDuration: 3000, // 3 ثواني لكل مشهد
    transitionDuration: 500 // 0.5 ثانية انتقال
};

function generateContent() {
    const btn = document.getElementById('genBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ جاري التوليد...';
    
    fetch('/generate', { headers: { 'X-Session-ID': sessionId } })
    .then(r => r.json())
    .then(data => {
        currentContent = data;
        
        document.getElementById('contentTitle').innerText = data.title;
        document.getElementById('contentLines').innerHTML = data.lines.map((line, i) => 
            `<div class="content-line" style="animation-delay: ${i * 0.1}s">${line}</div>`
        ).join('');
        
        document.getElementById('durationStat').innerText = data.duration;
        document.getElementById('linesStat').innerText = data.lines.length;
        
        document.getElementById('contentDisplay').style.display = 'block';
        document.getElementById('createCard').style.display = 'block';
        
        btn.innerHTML = '🎲 توليد محتوى جديد';
        btn.disabled = false;
        
        // Scroll to content
        document.getElementById('contentDisplay').scrollIntoView({ behavior: 'smooth' });
    });
}

async function createVideo() {
    if (!currentContent) return;
    
    const btn = document.getElementById('createBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ جاري التحضير...';
    
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    // إعداد التسجيل
    const stream = canvas.captureStream(CONFIG.fps);
    const options = {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 8000000 // 8 Mbps جودة عالية
    };
    
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'video/webm;codecs=vp8';
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
        const video = document.getElementById('previewVideo');
        video.src = url;
        video.style.display = 'block';
        canvas.style.display = 'none';
        
        document.getElementById('recIndicator').classList.remove('active');
        document.getElementById('progressBar').classList.remove('active');
        
        btn.innerHTML = '✅ تم الإنشاء!';
        
        // رفع للسيرفر
        await uploadVideo(blob);
    };
    
    // بدء التسجيل
    mediaRecorder.start(100);
    document.getElementById('videoSection').classList.add('active');
    document.getElementById('recIndicator').classList.add('active');
    document.getElementById('progressBar').classList.add('active');
    
    // تشغيل الرسم والأنيميشن
    await animateVideo(ctx, canvas, currentContent);
}

async function animateVideo(ctx, canvas, content) {
    const lines = [content.title, ...content.lines];
    const totalDuration = content.duration * 1000; // بالملي ثانية
    const startTime = Date.now();
استمر بثبات"]}
    ]
}

def get_random_content():
    category = random.choice(list(content_database.keys()))
    item = random.choice(content_database[category])
    return {
        "category": category,
        "title": item["title"],
        "lines": item["lines"],
        "duration": len(item["lines"]) * 3 + 2  # 3 ثواني لكل سطر + 2 ثواني مقدمة
    }

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    content = get_random_content()
    session_id = request.headers.get('X-Session-ID', 'default_' + str(int(time.time())))
    storage[session_id] = content
    video_storage[session_id] = None
    return jsonify(content)

@app.route("/upload_video", methods=['POST'])
def upload_video():
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        data = request.get_json()
        
        if not data or 'video' not in data:
            return jsonify({"error": "لا يوجد فيديو"}), 400
        
        video_data = data['video'].split(',')[1] if ',' in data['video'] else data['video']
        video_bytes = base64.b64decode(video_data)
        
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        video_path = os.path.join(temp_dir, "video.webm")
        
        with open(video_path, "wb") as f:
            f.write(video_bytes)
        
        video_storage[session_id] = {
            "path": video_path,
            "duration": data.get('duration', 0)
        }
        
        return jsonify({"status": "done", "duration": data.get('duration', 0)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video_file")
def video_file():
    session_id = request.headers.get('X-Session-ID', 'default')
    stored = video_storage.get(session_id)
    
    if not stored or not os.path.exists(stored["path"]):
        return "الفيديو غير موجود", 404
    
    def generate():
        with open(stored["path"], 'rb') as f:
            while chunk := f.read(8192):
                yield chunk
    
    return Response(generate(), mimetype='video/webm')

@app.route("/download")
def download():
    session_id = request.headers.get('X-Session-ID', 'default')
    stored = video_storage.get(session_id)
    
    if not stored or not os.path.exists(stored["path"]):
        return jsonify({"error": "الفيديو غير جاهز"}), 404
    
    return send_file(
        stored["path"],
        as_attachment=True,
        download_name="tiktok_video.webm",
        mimetype="video/webm"
    )

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>TikTok Pro Creator</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
    overflow-x: hidden;
}
.container { max-width: 600px; margin: 0 auto; padding: 20px; }
.header {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: -20px -20px 30px -20px;
    position: relative;
    overflow: hidden;
}
.header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    animation: move 20s linear infinite;
}
@keyframes move { from { transform: translate(0,0); } to { transform: translate(50px,50px); } }
h1 { font-size: 32px; position: relative; z-index: 1; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
.card {
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    padding: 25px;
    border-radius: 24px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.card h3 {
    font-size: 18px;
    color: #a78bfa;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.content-preview {
    background: rgba(102, 126, 234, 0.1);
    padding: 20px;
    border-radius: 16px;
    border-right: 4px solid #667eea;
}
.content-title {
    font-size: 24px;
    font-weight: bold;
    color: #fff;
    margin-bottom: 15px;
    line-height: 1.4;
}
.content-line {
    background: rgba(255,255,255,0.05);
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
    font-size: 16px;
    color: #e0e0e0;
    position: relative;
    padding-right: 30px;
}
.content-line::before {
    content: '→';
    position: absolute;
    right: 10px;
    color: #667eea;
}
.btn {
    width: 100%;
    padding: 18px 24px;
    border: none;
    border-radius: 16px;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    margin: 10px 0;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    position: relative;
    overflow: hidden;
}
.btn::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}
.btn:hover::before { left: 100%; }
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}
.btn-secondary {
    background: rgba(255,255,255,0.1);
    color: white;
    border: 2px solid #667eea;
}
.btn-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
.btn:active:not(:disabled) { transform: scale(0.98); }
.video-section {
    background: #000;
    border-radius: 24px;
    padding: 20px;
    margin-top: 20px;
    display: none;
}
.video-section.active { display: block; }
#canvas {
    width: 100%;
    border-radius: 16px;
    background: #000;
}
#previewVideo {
    width: 100%;
    border-radius: 16px;
    display: none;
}
.progress-bar {
    width: 100%;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    margin: 20px 0;
    overflow: hidden;
    display: none;
}
.progress-bar.active { display: block; }
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    width: 0%;
    transition: width 0.3s;
}
.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
}
.stat {
    text-align: center;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
}
.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #667eea;
}
.stat-label {
    font-size: 12px;
    color: #888;
    margin-top: 5px;
}
.recording-indicator {
    display: none;
    align-items: center;
    gap: 10px;
    color: #ef4444;
    font-weight: bold;
    margin-bottom: 15px;
}
.recording-indicator.active { display: flex; }
.rec-dot {
    width: 12px;
    height: 12px;
    background: #ef4444;
    border-radius: 50%;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎬 TikTok Pro</h1>
    </div>
    
    <div class="card">
        <h3>✨ المحتوى</h3>
        <button class="btn btn-primary" onclick="generateContent()" id="genBtn">
            🎲 توليد محتوى جديد
        </button>
        <div id="contentDisplay" style="display: none; margin-top: 20px;">
            <div class="content-preview">
                <div class="content-title" id="contentTitle"></div>
                <div id="contentLines"></div>
            </div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="durationStat">0</div>
                    <div class="stat-label">ثانية</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="linesStat">0</div>
                    <div class="stat-label">مشاهد</div>
                </div>
                <div class="stat">
                    <div class="stat-value">1080p</div>
                    <div class="stat-label">جودة</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card" id="createCard" style="display: none;">
        <h3>🎥 إنشاء الفيديو</h3>
        <div class="recording-indicator" id="recIndicator">
            <span class="rec-dot"></span>
            <span>يتم التسجيل...</span>
        </div>
        <button class="btn btn-success" onclick="createVideo()" id="createBtn">
            🎬 ابدأ الإنشاء
        </button>
        <div class="progress-bar" id="progressBar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
    </div>
    
    <div class="video-section" id="videoSection">
        <canvas id="canvas" width="1080" height="1920"></canvas>
        <video id="previewVideo" controls playsinline></video>
    </div>
    
    <div class="card" id="downloadCard" style="display: none;">
        <h3>⬇️ التحميل</h3>
        <button class="btn btn-secondary" onclick="downloadVideo()" id="downloadBtn">
            💾 تحميل الفيديو
        </button>
        <button class="btn btn-primary" onclick="shareVideo()" id="shareBtn" style="display: none;">
            📤 مشاركة
        </button>
    </div>
</div>

<script>
const sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
let currentContent = null;
let mediaRecorder = null;
let recordedChunks = [];
let animationId = null;

// إعدادات الفيديو
const CONFIG = {
    width: 1080,
    height: 1920,
    fps: 60,
    sceneDuration: 3000, // 3 ثواني لكل مشهد
    transitionDuration: 500 // 0.5 ثانية انتقال
};

function generateContent() {
    const btn = document.getElementById('genBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ جاري التوليد...';
    
    fetch('/generate', { headers: { 'X-Session-ID': sessionId } })
    .then(r => r.json())
    .then(data => {
        currentContent = data;
        
        document.getElementById('contentTitle').innerText = data.title;
        document.getElementById('contentLines').innerHTML = data.lines.map((line, i) => 
            `<div class="content-line" style="animation-delay: ${i * 0.1}s">${line}</div>`
        ).join('');
        
        document.getElementById('durationStat').innerText = data.duration;
        document.getElementById('linesStat').innerText = data.lines.length;
        
        document.getElementById('contentDisplay').style.display = 'block';
        document.getElementById('createCard').style.display = 'block';
        
        btn.innerHTML = '🎲 توليد محتوى جديد';
        btn.disabled = false;
        
        // Scroll to content
        document.getElementById('contentDisplay').scrollIntoView({ behavior: 'smooth' });
    });
}

async function createVideo() {
    if (!currentContent) return;
    
    const btn = document.getElementById('createBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ جاري التحضير...';
    
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    // إعداد التسجيل
    const stream = canvas.captureStream(CONFIG.fps);
    const options = {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 8000000 // 8 Mbps جودة عالية
    };
    
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'video/webm;codecs=vp8';
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
        const video = document.getElementById('previewVideo');
        video.src = url;
        video.style.display = 'block';
        canvas.style.display = 'none';
        
        document.getElementById('recIndicator').classList.remove('active');
        document.getElementById('progressBar').classList.remove('active');
        
        btn.innerHTML = '✅ تم الإنشاء!';
        
        // رفع للسيرفر
        await uploadVideo(blob);
    };
    
    // بدء التسجيل
    mediaRecorder.start(100);
    document.getElementById('videoSection').classList.add('active');
    document.getElementById('recIndicator').classList.add('active');
    document.getElementById('progressBar').classList.add('active');
    
    // تشغيل الرسم والأنيميشن
    await animateVideo(ctx, canvas, currentContent);
}

async function animateVideo(ctx, canvas, content) {
    const lines = [content.title, ...content.lines];
    const totalDuration = content.duration * 1000; // بالملي ثانية
    const startTime = Date.now();
    let currentScene = 0;
    
    function render() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / totalDuration, 1);
        
        // تحديث شريط التقدم
        document.getElementById('progressFill').style.width = (progress * 100) + '%';
        
        // حساب المشهد الحالي
        const sceneIndex = Math.min(
            Math.floor(elapsed / CONFIG.sceneDuration),
            lines.length - 1
        );
        
        // رسم المشهد
        drawScene(ctx, canvas, lines, sceneIndex, elapsed);
        
        if (elapsed < totalDuration) {
            animationId = requestAnimationFrame(render);
        } else {
            // إيقاف التسجيل
            setTimeout(() => {
                if (mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                }
                document.getElementById('downloadCard').style.display = 'block';
                document.getElementById('downloadCard').scrollIntoView({ behavior: 'smooth' });
            }, 500);
        }
    }
    
    render();
}

function drawScene(ctx, canvas, lines, sceneIndex, elapsed) {
    const w = canvas.width;
    const h = canvas.height;
    const sceneElapsed = elapsed % CONFIG.sceneDuration;
    const transitionProgress = Math.min(sceneElapsed / CONFIG.transitionDuration, 1);
    
    // خلفية متدرجة متحركة
    const hue = (elapsed / 50) % 360;
    const gradient = ctx.createLinearGradient(0, 0, w, h);
    gradient.addColorStop(0, `hsl(${hue}, 70%, 20%)`);
    gradient.addColorStop(0.5, `hsl(${(hue + 60) % 360}, 70%, 15%)`);
    gradient.addColorStop(1, `hsl(${(hue + 120) % 360}, 70%, 20%)`);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, w, h);
    
    // جزيئات متحركة
    drawParticles(ctx, w, h, elapsed);
    
    // تأثير الانتقال
    const easeOut = 1 - Math.pow(1 - transitionProgress, 3);
    
    // رسم النص الرئيسي (العنوان)
    if (sceneIndex === 0) {
        drawText(ctx, lines[0], w/2, h/2, 80, '#fff', easeOut, true);
    } else {
        // رسم العنوان بشكل أصغر في الأعلى
        drawText(ctx, lines[0], w/2, 200, 50, 'rgba(255,255,255,0.5)', 1, false);
        
        // رسم السطر الحالي
        const lineIndex = sceneIndex;
        if (lineIndex < lines.length) {
            drawText(ctx, lines[lineIndex], w/2, h/2, 70, '#a78bfa', easeOut, true);
        }
    }
    
    // رسم شريط التقدم في الأسفل
    const totalScenes = lines.length;
    const progress = sceneIndex / (totalScenes - 1);
    ctx.fillStyle = 'rgba(255,255,255,0.1)';
    ctx.fillRect(100, h - 100, w - 200, 10);
    ctx.fillStyle = '#667eea';
    ctx.fillRect(100, h - 100, (w - 200) * progress, 10);
    
    // رقم المشهد
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.font = '30px -apple-system, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${sceneIndex + 1}/${totalScenes}`, w - 100, h - 140);
}

function drawParticles(ctx, w, h, elapsed) {
    const particleCount = 50;
    ctx.save();
    
    for (let i = 0; i < particleCount; i++) {
        const x = ((elapsed * 0.05) + (i * 100)) % w;
        const y = ((elapsed * 0.03) + (i * 137.5)) % h;
        const size = 2 + Math.sin(elapsed * 0.01 + i) * 2;
        const alpha = 0.3 + Math.sin(elapsed * 0.005 + i) * 0.2;
        
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(167, 139, 250, ${alpha})`;
        ctx.fill();
    }
    
    ctx.restore();
}

function drawText(ctx, text, x, y, fontSize, color, progress, shadow) {
    ctx.save();
    
    // تأثير الدخول
    const offsetY = (1 - progress) * 50;
    const alpha = progress;
    
    ctx.translate(x, y + offsetY);
    ctx.globalAlpha = alpha;
    
    if (shadow) {
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 20;
        ctx.shadowOffsetY = 10;
    }
    
    ctx.fillStyle = color;
    ctx.font = `bold ${fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // تقسيم النص لسطور إذا كان طويل
    const maxWidth = 900;
    const words = text.split(' ');
    const lines = [];
    let currentLine = words[0];
    
    for (let i = 1; i < words.length; i++) {
        const width = ctx.measureText(currentLine + ' ' + words[i]).width;
        if (width < maxWidth) {
            currentLine += ' ' + words[i];
        } else {
            lines.push(currentLine);
            currentLine = words[i];
        }
    }
    lines.push(currentLine);
    
    // رسم السطور
    const lineHeight = fontSize * 1.4;
    const totalHeight = lines.length * lineHeight;
    const startY = -(totalHeight / 2) + (lineHeight / 2);
    
    lines.forEach((line, i) => {
        ctx.fillText(line, 0, startY + (i * lineHeight));
    });
    
    ctx.restore();
}

async function uploadVideo(blob) {
    const reader = new FileReader();
    reader.onloadend = async () => {
        const base64 = reader.result;
        
        await fetch('/upload_video', {
            method: 'POST',
            headers: {
                'X-Session-ID': sessionId,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                video: base64,
                duration: currentContent.duration
            })
        });
    };
    reader.readAsDataURL(blob);
}

function downloadVideo() {
    window.open(`/download?t=${Date.now()}`, '_blank');
}

function shareVideo() {
    if (navigator.share) {
        navigator.share({
            title: 'TikTok Pro Video',
            text: 'شاهد هذا الفيديو الرائع!',
            url: window.location.href
        });
    }
}

// توليد تلقائي
window.onload = () => setTimeout(generateContent, 500);
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
