from flask import Flask, render_template_string, jsonify, send_file, request, Response
import random
import os
import tempfile
import base64
import json
import requests
import time

app = Flask(__name__)

storage = {}
video_storage = {}

# سيناريوهات AI (موضوع + شخصية + صوت)
scenarios = [
    {
        "title": "🖥️ مروحة الكمبيوتر",
        "character": " dusty PC fan with angry face, anthropomorphic, cartoon style, 4k",
        "lines": [
            "أنا أموت هنا!",
            "3 سنوات وما nadifوني",
            "الغبار خانقني",
            "ساعدوني يا ناس!"
        ],
        "voice_mood": "angry"
    },
    {
        "title": "🔋 البطارية",
        "character": "sad phone battery with face, low battery red, cartoon, cute",
        "lines": [
            "1% بس!",
            "لمّا تسوّلّف 3 ساعات",
            "وتقول لي: بس 5 دقايق",
            "أنا ضحية!"
        ],
        "voice_mood": "sad"
    },
    {
        "title": "💾 الـ USB",
        "character": "confused USB stick with face, trying to plug in, cartoon",
        "lines": [
            "الوجه الأول: لا",
            "اقلبني: لا",
            "ارجع الوجه الأول: ايوه!",
            "كيف؟!"
        ],
        "voice_mood": "confused"
    },
    {
        "title": "🎧 السماعة",
        "character": "tangled headphone with crying face, messy wires, cartoon",
        "lines": [
            "في الجيب 5 ثواني",
            "طلعت كذا!",
            "أنا أعقد نفسي",
            "ساعدوني أفكك!"
        ],
        "voice_mood": "crying"
    },
    {
        "title": "📱 الشاشة",
        "character": "cracked phone screen with bandages, sad face, cartoon",
        "lines": [
            "بدون كفر قال",
            "سقطت من اليد",
            "الآن أنا مكسور",
            "غيّرني بـ 2000 ريال!"
        ],
        "voice_mood": "sad"
    }
]

def get_random_scenario():
    return random.choice(scenarios)

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    scenario = get_random_scenario()
    session_id = request.headers.get('X-Session-ID', 'sess_' + str(int(time.time())))
    
    storage[session_id] = {
        "scenario": scenario,
        "images": [],  # رابط الصور من AI
        "audio": []    # روابط الصوت
    }
    
    return jsonify(scenario)

@app.route("/create_ai_video", methods=['POST'])
def create_ai_video():
    """إنشاء فيديو باستخدام AI"""
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        data = request.get_json()
        scenario = data.get('scenario')
        
        if not scenario:
            return jsonify({"error": "لا يوجد سيناريو"}), 400
        
        # هنا تضيف API keys حقيقية
        # 1. توليد صور بالـ AI (Midjourney/Stable Diffusion)
        # 2. توليد صوت (ElevenLabs)
        # 3. lip sync (D-ID أو HeyGen)
        
        # للتجربة: نرجع روابط وهمية
        video_url = f"/video_preview/{session_id}"
        
        return jsonify({
            "status": "processing",
            "message": "جاري إنشاء الفيديو بالذكاء الاصطناعي...",
            "steps": [
                "توليد الصور بالـ AI...",
                "توليد الصوت...",
                "مزامنة الشفايف...",
                "تجميع الفيديو..."
            ],
            "preview_url": video_url
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        video_path = os.path.join(temp_dir, "ai_video.webm")
        
        with open(video_path, "wb") as f:
            f.write(video_bytes)
        
        video_storage[session_id] = video_path
        
        return jsonify({"status": "done"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download")
def download():
    session_id = request.headers.get('X-Session-ID', 'default')
    path = video_storage.get(session_id)
    
    if not path or not os.path.exists(path):
        return jsonify({"error": "الفيديو غير جاهز"}), 404
    
    return send_file(
        path,
        as_attachment=True,
        download_name="ai_talking_video.webm",
        mimetype="video/webm"
    )

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Talking Videos</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
}
.container { max-width: 600px; margin: 0 auto; padding: 20px; }
.header {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: -20px -20px 30px -20px;
}
h1 { font-size: 28px; }
.ai-badge {
    display: inline-block;
    background: #10b981;
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 14px;
    margin-top: 10px;
}
.card {
    background: #1a1a2e;
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}
.scenario-card {
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 15px;
    border-right: 4px solid #667eea;
}
.scenario-title {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
}
.character-desc {
    color: #888;
    font-size: 14px;
    margin-bottom: 15px;
}
.dialogue-line {
    background: rgba(102, 126, 234, 0.1);
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
    font-size: 16px;
    position: relative;
    padding-right: 35px;
}
.dialogue-line::before {
    content: '🎭';
    position: absolute;
    right: 10px;
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
    transition: all 0.3s;
}
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.btn-ai {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}
.btn:disabled { opacity: 0.5; }
.video-container {
    background: #000;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 20px;
    display: none;
}
.video-container.active { display: block; }
video { width: 100%; display: block; }
#canvas { width: 100%; border-radius: 16px; }
.steps {
    display: none;
    margin: 20px 0;
}
.steps.active { display: block; }
.step {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    margin: 10px 0;
    opacity: 0.5;
    transition: all 0.3s;
}
.step.active {
    opacity: 1;
    background: rgba(102, 126, 234, 0.2);
    border-right: 3px solid #667eea;
}
.step-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #667eea;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.step.done .step-icon {
    background: #10b981;
}
.step-text { flex: 1; }
.api-key-input {
    width: 100%;
    padding: 15px;
    border: 2px solid #667eea;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
    color: white;
    margin: 10px 0;
    font-size: 14px;
}
.api-key-input::placeholder { color: #666; }
.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.tab {
    flex: 1;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border: none;
    border-radius: 12px;
    color: white;
    cursor: pointer;
    transition: all 0.3s;
}
.tab.active {
    background: #667eea;
}
.tab-content { display: none; }
.tab-content.active { display: block; }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎬 AI Talking Videos</h1>
        <span class="ai-badge">🤖 Powered by AI</span>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="switchTab('auto')">🎲 تلقائي</button>
        <button class="tab" onclick="switchTab('custom')">✏️ مخصص</button>
    </div>
    
    <div id="autoTab" class="tab-content active">
        <div class="card">
            <h3>🎭 اختر الشخصية</h3>
            <button class="btn btn-primary" onclick="generateScenario()" id="genBtn">
                🎲 توليد سيناريو عشوائي
            </button>
            <div id="scenarioDisplay"></div>
        </div>
        
        <div class="card" id="createCard" style="display: none;">
            <h3>🤖 إنشاء بالذكاء الاصطناعي</h3>
            
            <div class="steps" id="steps">
                <div class="step" id="step1">
                    <div class="step-icon">🖼️</div>
                    <div class="step-text">توليد صور الشخصية بالـ AI</div>
                </div>
                <div class="step" id="step2">
                    <div class="step-icon">🎙️</div>
                    <div class="step-text">توليد الصوت بالـ AI</div>
                </div>
                <div class="step" id="step3">
                    <div class="step-icon">👄</div>
                    <div class="step-text">مزامنة الشفايف (Lip Sync)</div>
                </div>
                <div class="step" id="step4">
                    <div class="step-icon">🎬</div>
                    <div class="step-text">تجميع الفيديو النهائي</div>
                </div>
            </div>
            
            <button class="btn btn-ai" onclick="createAIVideo()" id="aiBtn">
                ✨ إنشاء الفيديو بالـ AI
            </button>
        </div>
    </div>
    
    <div id="customTab" class="tab-content">
        <div class="card">
            <h3>✏️ محتوى مخصص</h3>
            <input type="text" class="api-key-input" id="customTitle" placeholder="عنوان الفيديو (مثال: مروحة الكمبيوتر)">
            <textarea class="api-key-input" id="customLines" rows="4" placeholder="الحوار (سطر لكل جملة)"></textarea>
            <button class="btn btn-primary" onclick="createCustom()">إنشاء</button>
        </div>
    </div>
    
    <div class="video-container" id="videoContainer">
        <canvas id="canvas" width="1080" height="1920"></canvas>
        <video id="preview" controls playsinline style="display: none;"></video>
    </div>
    
    <div class="card" id="downloadCard" style="display: none;">
        <button class="btn btn-primary" onclick="downloadVideo()">⬇️ تحميل الفيديو</button>
    </div>
</div>

<script>
const sessionId = 'sess_' + Date.now();
let currentScenario = null;
let mediaRecorder = null;
let recordedChunks = [];

function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tab + 'Tab').classList.add('active');
}

function generateScenario() {
    const btn = document.getElementById('genBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ جاري التوليد...';
    
    fetch('/generate', { headers: { 'X-Session-ID': sessionId } })
    .then(r => r.json())
    .then(data => {
        currentScenario = data;
        
        document.getElementById('scenarioDisplay').innerHTML = `
            <div class="scenario-card" style="margin-top: 20px;">
                <div class="scenario-title">${data.title}</div>
                <div class="character-desc">🎭 ${data.character}</div>
                <div style="margin-top: 15px;">
                    ${data.lines.map((line, i) => 
                        `<div class="dialogue-line" style="animation-delay: ${i * 0.1}s">${line}</div>`
                    ).join('')}
                </div>
                <div style="margin-top: 15px; padding: 10px; background: rgba(16, 185, 129, 0.1); border-radius: 8px; color: #10b981;">
                    😊 المزاج: ${data.voice_mood}
                </div>
            </div>
        `;
        
        document.getElementById('createCard').style.display = 'block';
        btn.innerHTML = '🎲 توليد سيناريو عشوائي';
        btn.disabled = false;
    });
}

async function createAIVideo() {
    if (!currentScenario) return;
    
    const btn = document.getElementById('aiBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ جاري الإنشاء...';
    
    // عرض خطوات العمل
    document.getElementById('steps').classList.add('active');
    
    // محاكاة خطوات AI (في الواقع هنا تستدعي APIs)
    for (let i = 1; i <= 4; i++) {
        document.getElementById('step' + i).classList.add('active');
        await new Promise(r => setTimeout(r, 1500));
        document.getElementById('step' + i).classList.add('done');
        document.getElementById('step' + i).querySelector('.step-icon').innerHTML = '✓';
    }
    
    // إنشاء الفيديو محلياً (محاكاة)
    await createLocalVideo();
    
    btn.innerHTML = '✅ تم الإنشاء!';
    document.getElementById('downloadCard').style.display = 'block';
}

async function createLocalVideo() {
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    // إعداد التسجيل
    const stream = canvas.captureStream(30);
    mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 5000000
    });
    
    recordedChunks = [];
    mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) recordedChunks.push(e.data);
    };
    
    mediaRecorder.onstop = async () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        
        document.getElementById('preview').src = url;
        document.getElementById('preview').style.display = 'block';
        canvas.style.display = 'none';
        
        // رفع للسيرفر
        const reader = new FileReader();
        reader.onloadend = () => {
            fetch('/upload_video', {
                method: 'POST',
                headers: {
                    'X-Session-ID': sessionId,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ video: reader.result })
            });
        };
        reader.readAsDataURL(blob);
    };
    
    mediaRecorder.start(100);
    document.getElementById('videoContainer').classList.add('active');
    
    // رسم الفيديو مع "شخصية" تتكلم
    await animateTalkingCharacter(ctx, canvas, currentScenario);
}

async function animateTalkingCharacter(ctx, canvas, scenario) {
    const lines = scenario.lines;
    const totalDuration = lines.length * 3000; // 3 ثواني لكل سطر
    const startTime = Date.now();
    
    // رسم الشخصية (دائرة وجه بسيطة تتحرك)
    function drawCharacter(progress, isTalking) {
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2 - 200;
        const size = 200;
        
        // جسم الشخصية (مروحة/بطارية/إلخ)
        ctx.save();
        
        // خلفية الشخصية
        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, size);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(1, '#764ba2');
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, size, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // عيون
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.ellipse(centerX - 50, centerY - 30, 30, 40, 0, 0, Math.PI * 2);
        ctx.ellipse(centerX + 50, centerY - 30, 30, 40, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // حدقة العين
        ctx.fillStyle = 'black';
        ctx.beginPath();
        ctx.arc(centerX - 50, centerY - 30, 15, 0, Math.PI * 2);
        ctx.arc(centerX + 50, centerY - 30, 15, 0, Math.PI * 2);
        ctx.fill();
        
        // فم يتحرك
        ctx.fillStyle = isTalking ? '#ff6b6b' : '#333';
        ctx.beginPath();
        const mouthOpen = isTalking ? Math.sin(Date.now() / 100) * 20 + 20 : 10;
        ctx.ellipse(centerX, centerY + 50, 40, mouthOpen, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // حواجب تعبيرية
        ctx.strokeStyle = scenario.voice_mood === 'angry' ? '#ff0000' : '#333';
        ctx.lineWidth = 8;
        ctx.beginPath();
        if (scenario.voice_mood === 'angry') {
            // حواجب مقلوبة (غاضب)
            ctx.moveTo(centerX - 80, centerY - 80);
            ctx.lineTo(centerX - 20, centerY - 60);
            ctx.moveTo(centerX + 80, centerY - 80);
            ctx.lineTo(centerX + 20, centerY - 60);
        } else if (scenario.voice_mood === 'sad') {
            // حواجب حزينة
            ctx.moveTo(centerX - 80, centerY - 70);
            ctx.lineTo(centerX - 20, centerY - 80);
            ctx.moveTo(centerX + 80, centerY - 70);
            ctx.lineTo(centerX + 20, centerY - 80);
        }
        ctx.stroke();
        
        ctx.restore();
    }
    
    function draw() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / totalDuration;
        
        // خلفية
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // جزيئات
        for (let i = 0; i < 30; i++) {
            ctx.fillStyle = `rgba(102, 126, 234, ${0.1 + Math.sin(elapsed/500 + i) * 0.1})`;
            ctx.beginPath();
            ctx.arc(
                (i * 100 + elapsed/10) % canvas.width,
                (i * 137 + elapsed/20) % canvas.height,
                3,
                0, Math.PI * 2
            );
            ctx.fill();
        }
        
        // السطر الحالي
        const currentLine = Math.min(Math.floor(elapsed / 3000), lines.length - 1);
        const isTalking = (elapsed % 3000) < 2500; // يتكلم 2.5 ثانية من كل 3
        
        // رسم الشخصية
        drawCharacter(progress, isTalking);
        
        // صندوق الكلام
        ctx.fillStyle = 'rgba(0,0,0,0.8)';
        ctx.fillRect(50, canvas.height - 400, canvas.width - 100, 250);
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 4;
        ctx.strokeRect(50, canvas.height - 400, canvas.width - 100, 250);
        
        // النص
        ctx.fillStyle = 'white';
        ctx.font = 'bold 50px -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // تقسيم النص لسطور
        const words = lines[currentLine].split(' ');
        const line1 = words.slice(0, Math.ceil(words.length/2)).join(' ');
        const line2 = words.slice(Math.ceil(words.length/2)).join(' ');
        
        ctx.fillText(line1, canvas.width/2, canvas.height - 300);
        if (line2) ctx.fillText(line2, canvas.width/2, canvas.height - 230);
        
        // مؤشر من يتكلم
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.moveTo(100, canvas.height - 420);
        ctx.lineTo(130, canvas.height - 420);
        ctx.lineTo(115, canvas.height - 400);
        ctx.fill();
        
        if (elapsed < totalDuration) {
            requestAnimationFrame(draw);
        } else {
            mediaRecorder.stop();
        }
    }
    
    draw();
}

function createCustom() {
    const title = document.getElementById('customTitle').value;
    const lines = document.getElementById('customLines').value.split('\n').filter(l => l.trim());
    
    if (!title || lines.length === 0) {
        alert('املأ جميع الحقول');
        return;
    }
    
    currentScenario = {
        title: title,
        lines: lines,
        voice_mood: 'neutral',
        character: 'custom character'
    };
    
    createLocalVideo();
}

function downloadVideo() {
    window.open(`/download?t=${Date.now()}`, '_blank');
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
