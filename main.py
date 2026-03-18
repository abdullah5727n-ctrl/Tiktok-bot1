from flask import Flask, render_template_string, jsonify, send_file, request
import random
import os
import tempfile
import subprocess
import json

app = Flask(__name__)

# تخزين مؤقت بسيط (في Render البيانات تروح لو الـ dyno restart)
storage = {}

ideas = [
    "3 أشياء مستحيل تعرفها",
    "سر خطير محد يقولك",
    "وش يصير لو ما نمت يومين؟",
    "أغرب حقيقة في العالم",
    "لماذا نتثاءب؟",
    "سر النجاح في 30 ثانية",
    "أغرب طعام في العالم",
    "هل تعلم؟"
]

scripts = [
    ["هل تعلم أن...", "في شيء غريب...", "تابع للنهاية"],
    ["99% ما يعرفون...", "لكن الحقيقة...", "صدمة"],
    ["هذا الشيء خطير...", "انتبه له...", "لا تسوي كذا"],
    ["واحد...", "اثنين...", "ثلاثة... انتهى!"],
    ["انتبه...", "الحين جاي الصدمة...", "شوف بنفسك"]
]

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    idea = random.choice(ideas)
    script = random.choice(scripts)
    
    # تخزين في الجلسة باستخدام معرف فريد
    session_id = request.headers.get('X-Session-ID', 'default')
    storage[session_id] = {
        "idea": idea,
        "script": script
    }
    
    return jsonify({
        "idea": idea,
        "script": script,
        "session": session_id
    })

@app.route("/video", methods=['POST'])
def video():
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        data = storage.get(session_id, {})
        
        if not data.get("idea"):
            return jsonify({"error": "ولد فكرة أولاً"}), 400

        idea = data["idea"]
        script_lines = data["script"]
        
        # إنشاء ملف SRT للترجمة (التوقيت)
        srt_content = ""
        duration_per_line = 2  # ثانيتين لكل سطر
        for i, line in enumerate([idea] + script_lines):
            start = i * duration_per_line
            end = start + duration_per_line
            srt_content += f"{i+1}\n"
            srt_content += f"00:00:{start:02d},000 --> 00:00:{end:02d},000\n"
            srt_content += f"{line}\n\n"
        
        # حفظ الملفات في /tmp (الوحيد المسموح في Render)
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        srt_path = os.path.join(temp_dir, "subtitles.srt")
        
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        # إنشاء فيديو باستخدام FFmpeg مباشرة (أخف من MoviePy)
        output_path = os.path.join(temp_dir, "output.mp4")
        
        # نص الفيديو الكامل
        full_text = " | ".join([idea] + script_lines)
        
        # استخدام FFmpeg لإنشاء فيديو مع نص
        # نستخدم drawtext مع خط يدعم العربية
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=black:s=720x1280:d={len([idea]+script_lines)*2}",
            "-vf",
            f"drawtext=text='{full_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5,"
            f"format=yuv420p",
            "-c:v", "libx264",
            "-t", str(len([idea]+script_lines)*2),
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ]
        
        # تنفيذ الأمر
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # إذا فشل FFmpeg، نرجع HTML animation كبديل
            return jsonify({
                "status": "html_fallback",
                "message": "تم إنشاء معاينة HTML (FFmpeg غير متوفر)",
                "data": data
            })
        
        # حفظ المسار في التخزين
        storage[session_id + "_video"] = output_path
        
        return jsonify({
            "status": "done",
            "duration": len([idea] + script_lines) * 2
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "انتهى الوقت"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download")
def download():
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        video_path = storage.get(session_id + "_video")
        
        if not video_path or not os.path.exists(video_path):
            # إرجاع فيديو HTML5 كبديل
            return jsonify({
                "error": "الفيديو غير موجود",
                "fallback": "use_html_version"
            }), 404
            
        return send_file(
            video_path,
            as_attachment=True,
            download_name="swiftstore_video.mp4",
            mimetype="video/mp4"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "SwiftStore"})

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SwiftStore - Render</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #fff;
    min-height: 100vh;
    overflow-x: hidden;
}
.container {
    max-width: 1200px;
    margin: auto;
    padding: 40px 20px;
}
h1 {
    text-align: center;
    font-size: clamp(2rem, 5vw, 3.5rem);
    margin-bottom: 40px;
    background: linear-gradient(135deg, #9d50bb, #6e48aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 2s ease-in-out infinite alternate;
}
@keyframes glow {
    from { filter: drop-shadow(0 0 10px rgba(157,80,187,0.5)); }
    to { filter: drop-shadow(0 0 20px rgba(157,80,187,0.8)); }
}
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}
.card {
    background: rgba(31, 28, 61, 0.8);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 0 30px rgba(157,80,187,0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(157,80,187,0.2);
    transition: all 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 40px rgba(157,80,187,0.6);
}
.full {
    grid-column: 1 / -1;
    text-align: center;
}
button {
    padding: 14px 28px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #9d50bb, #6e48aa);
    color: #fff;
    cursor: pointer;
    font-size: 16px;
    margin: 10px 5px;
    transition: all 0.3s;
    font-weight: bold;
    position: relative;
    overflow: hidden;
}
button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s;
}
button:hover::before {
    left: 100%;
}
button:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 20px rgba(157,80,187,0.4);
}
button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
}
.idea {
    font-size: 24px;
    margin-top: 20px;
    padding: 20px;
    background: linear-gradient(135deg, #2a244a, #1f1c3d);
    border-radius: 15px;
    min-height: 60px;
    border-right: 5px solid #9d50bb;
    line-height: 1.6;
}
.script p {
    background: linear-gradient(135deg, #2a244a, #1f1c3d);
    padding: 15px 20px;
    border-radius: 12px;
    margin: 12px 0;
    font-size: 18px;
    border-right: 4px solid #6e48aa;
    animation: slideIn 0.5s ease;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}
.status {
    margin-top: 20px;
    padding: 15px;
    border-radius: 12px;
    display: none;
    font-weight: bold;
    animation: fadeIn 0.3s ease;
}
.status.success { 
    background: linear-gradient(135deg, #4caf50, #45a049);
    display: block;
    color: white;
}
.status.error { 
    background: linear-gradient(135deg, #f44336, #da190b);
    display: block;
    color: white;
}
.status.loading {
    background: linear-gradient(135deg, #2196f3, #1976d2);
    display: block;
    color: white;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,255,255,.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
    margin-left: 10px;
    vertical-align: middle;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
#videoPreview {
    margin-top: 30px;
    display: none;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(157,80,187,0.5);
}
video {
    width: 100%;
    max-width: 400px;
    border-radius: 20px;
}
.html-preview {
    width: 100%;
    max-width: 400px;
    height: 711px;
    background: linear-gradient(135deg, #0f0c29, #302b63);
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 40px;
    margin: 0 auto;
    position: relative;
    overflow: hidden;
}
.html-preview::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(157,80,187,0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}
@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
.preview-text {
    font-size: 32px;
    text-align: center;
    margin: 20px 0;
    z-index: 1;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    opacity: 0;
    animation: textPop 0.5s forwards;
}
@keyframes textPop {
    to { opacity: 1; transform: scale(1); }
}
.preview-line {
    font-size: 24px;
    margin: 10px 0;
    padding: 10px 20px;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    z-index: 1;
    opacity: 0;
}
@media (max-width: 768px) {
    .container { padding: 20px; }
    .card { padding: 20px; }
}
</style>
</head>
<body>
<div class="container">
    <h1>🚀 SwiftStore</h1>
    <div class="grid">
        <div class="card">
            <h3>🎯 الفكرة</h3>
            <button onclick="generate()" id="genBtn">توليد فكرة جديدة</button>
            <div id="idea" class="idea">اضغط "توليد" للحصول على فكرة</div>
        </div>
        <div class="card">
            <h3>📝 السكربت</h3>
            <div id="script" class="script">
                <p style="color: #888; border: none; background: transparent;">السكربت سيظهر هنا...</p>
            </div>
        </div>
        <div class="card full">
            <h3>🎬 إنشاء الفيديو</h3>
            <button onclick="makeVideo()" id="vidBtn" disabled>🎥 إنشاء فيديو</button>
            <button onclick="download()" id="dlBtn" disabled>⬇️ تحميل الفيديو</button>
            <div id="status" class="status"></div>
            <div id="videoPreview"></div>
        </div>
    </div>
</div>

<script>
// توليد معرف فريد للجلسة
const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
let currentData = null;

function showStatus(msg, type='loading') {
    const s = document.getElementById('status');
    s.innerHTML = msg + (type === 'loading' ? '<span class="spinner"></span>' : '');
    s.className = 'status ' + type;
    if (type !== 'loading') {
        setTimeout(() => s.className = 'status', 4000);
    }
}

function generate(){
    const btn = document.getElementById('genBtn');
    btn.disabled = true;
    showStatus('جاري التوليد...');
    
    fetch('/generate', {
        headers: { 'X-Session-ID': sessionId }
    })
    .then(res => res.json())
    .then(data => {
        currentData = data;
        document.getElementById('idea').innerText = data.idea;
        
        const scriptDiv = document.getElementById('script');
        scriptDiv.innerHTML = data.script.map((x, i) => 
            `<p style="animation-delay: ${i * 0.1}s">${x}</p>`
        ).join("");
        
        document.getElementById('vidBtn').disabled = false;
        document.getElementById('dlBtn').disabled = true;
        document.getElementById('videoPreview').style.display = 'none';
        
        showStatus('✅ تم التوليد بنجاح', 'success');
        btn.disabled = false;
    })
    .catch(err => {
        showStatus('❌ خطأ: ' + err.message, 'error');
        btn.disabled = false;
    });
}

function makeVideo(){
    if(!currentData) return;
    
    const btn = document.getElementById('vidBtn');
    btn.disabled = true;
    showStatus('جاري إنشاء الفيديو... قد يستغرق 10-20 ثانية');
    
    fetch('/video', {
        method: 'POST',
        headers: { 
            'X-Session-ID': sessionId,
            'Content-Type': 'application/json'
        }
    })
    .then(r => r.json())
    .then(d => {
        if(d.status === 'done'){
            showStatus('✅ تم إنشاء الفيديو!', 'success');
            document.getElementById('dlBtn').disabled = false;
            showVideoPreview();
        } else if (d.status === 'html_fallback') {
            showStatus('⚠️ ' + d.message, 'success');
            showHTMLPreview(d.data);
            document.getElementById('dlBtn').disabled = false;
        } else {
            showStatus('❌ خطأ: ' + (d.error || 'غير معروف'), 'error');
        }
        btn.disabled = false;
    })
    .catch(err => {
        showStatus('❌ خطأ في الاتصال: ' + err.message, 'error');
        btn.disabled = false;
    });
}

function showVideoPreview() {
    const preview = document.getElementById('videoPreview');
    preview.innerHTML = `
        <video controls autoplay loop muted>
            <source src="/download?session=${sessionId}" type="video/mp4">
            المتصفح لا يدعم الفيديو
        </video>
    `;
    preview.style.display = 'block';
}

function showHTMLPreview(data) {
    const preview = document.getElementById('videoPreview');
    preview.innerHTML = `
        <div class="html-preview">
            <div class="preview-text" style="animation-delay: 0s">${data.idea}</div>
            ${data.script.map((line, i) => 
                `<div class="preview-line" style="animation: textPop 0.5s ${(i+1)*0.5}s forwards">${line}</div>`
            ).join('')}
        </div>
    `;
    preview.style.display = 'block';
    
    // إعادة تشغيل الأنيميشن
    setTimeout(() => {
        const el = preview.querySelector('.html-preview');
        el.style.display = 'none';
        el.offsetHeight; // trigger reflow
        el.style.display = 'flex';
    }, 100);
}

function download(){
    if(document.getElementById('dlBtn').disabled) return;
    
    // فتح في تبويب جديد
    window.open(`/download?session=${sessionId}`, '_blank');
    showStatus('⬇️ جاري التحميل...', 'success');
}

// توليد فكرة تلقائياً عند التحميل
window.onload = () => {
    setTimeout(generate, 500);
};
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
