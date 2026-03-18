from flask import Flask, render_template_string, jsonify, send_file
import random
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from gtts import gTTS

app = Flask(__name__)

# ===============================
# IDEAS
# ===============================
ideas = [
    "3 أشياء مستحيل تعرفها 😳",
    "سر خطير محد يقولك 🔥",
    "وش يصير لو ما نمت 48 ساعة؟ 😨",
    "أغرب شيء ممكن تشوفه 🤯"
]

scripts = [
    ["هل تعلم أن...", "في شيء مرعب...", "تابع للنهاية 😳"],
    ["99% ما يعرفون...", "لكن الحقيقة...", "صدمة 🔥"],
    ["هذا الشيء خطير...", "انتبه له...", "لا تسوي كذا 😨"]
]

current = {"idea":"", "script":[]}

# ===============================
# GENERATE
# ===============================
@app.route("/generate")
def generate():
    current["idea"] = random.choice(ideas)
    current["script"] = random.choice(scripts)
    return jsonify(current)

# ===============================
# VIDEO LEGENDARY
# ===============================
@app.route("/video")
def video():
    text = current["idea"] + ". " + " ".join(current["script"])

    # صوت
    tts = gTTS(text=text, lang='ar')
    tts.save("voice.mp3")

    audio = AudioFileClip("voice.mp3")

    # خلفية فيديو
    bg = VideoFileClip("bg.mp4").subclip(0, 10).resize((720,1280))

    # نص
    txt = TextClip(text, fontsize=60, color='white', method='caption', size=(650,1000))
    txt = txt.set_position("center").set_duration(10)

    # دمج
    final = CompositeVideoClip([bg, txt])
    final = final.set_audio(audio)

    final.write_videofile("output.mp4", fps=24)

    return jsonify({"status":"done"})

# ===============================
# DOWNLOAD
# ===============================
@app.route("/download")
def download():
    return send_file("output.mp4", as_attachment=True)

# ===============================
# UI
# ===============================
HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<title>Legendary AI</title>
<style>
body {background:#0f0c29;color:#fff;font-family:sans-serif;text-align:center}
h1 {color:#9d50bb;font-size:40px}
button {padding:15px;margin:10px;border:none;border-radius:10px;
background:linear-gradient(135deg,#9d50bb,#6e48aa);color:#fff;font-size:16px;cursor:pointer}
.box {background:#1f1c3d;padding:20px;border-radius:15px;margin:20px}
</style>
</head>
<body>

<h1>😈 Legendary TikTok AI</h1>

<div class="box">
<button onclick="gen()">🎯 Generate</button>
<p id="idea"></p>
<div id="script"></div>
</div>

<div class="box">
<button onclick="make()">🎬 Create Video</button>
<button onclick="download()">📥 Download</button>
</div>

<script>
function gen(){
fetch('/generate').then(r=>r.json()).then(d=>{
document.getElementById('idea').innerText=d.idea
document.getElementById('script').innerHTML=d.script.map(x=>"<p>"+x+"</p>").join("")
})
}
function make(){fetch('/video').then(()=>alert("🔥 تم إنشاء الفيديو"))}
function download(){window.location='/download'}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)