from flask import Flask, render_template_string, jsonify, send_file
import random, os
from moviepy.editor import *
from gtts import gTTS

app = Flask(__name__)

ideas = [
    "3 أشياء مستحيل تعرفها 😳",
    "سر خطير محد يقولك 🔥",
    "وش يصير لو ما نمت يومين؟ 😨",
    "أغرب حقيقة في العالم 🤯"
]

scripts = [
    ["هل تعلم أن...", "في شيء غريب...", "تابع للنهاية 😳"],
    ["99% ما يعرفون...", "لكن الحقيقة...", "صدمة 🔥"],
    ["هذا الشيء خطير...", "انتبه له...", "لا تسوي كذا 😨"]
]

current = {"idea":"", "script":[]}

@app.route("/generate")
def generate():
    current["idea"] = random.choice(ideas)
    current["script"] = random.choice(scripts)
    return jsonify(current)

@app.route("/video")
def video():
    text = current["idea"] + ". " + " ".join(current["script"])

    # 🔊 صوت
    tts = gTTS(text=text, lang='ar')
    tts.save("voice.mp3")
    audio = AudioFileClip("voice.mp3")

    # 🎥 خلفية
    bg = VideoFileClip("bg.mp4").subclip(0,10).resize((720,1280))

    # ✨ تأثير Zoom
    bg = bg.fx(vfx.resize, lambda t: 1 + 0.05*t)

    # 📝 نص
    txt = TextClip(text, fontsize=55, color='white',
                   method='caption', size=(650,1000))\
                   .set_position("center").set_duration(10)

    # 🎵 موسيقى خفيفة (اختياري)
    final = CompositeVideoClip([bg, txt])
    final = final.set_audio(audio)

    final.write_videofile("output.mp4", fps=24)

    return jsonify({"status":"done"})

@app.route("/download")
def download():
    return send_file("output.mp4", as_attachment=True)

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<title>God Mode AI</title>

<style>
body {
    margin:0;
    font-family:sans-serif;
    background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color:#fff;
}
.container {
    max-width:1100px;
    margin:auto;
    padding:30px;
}
h1 {
    text-align:center;
    font-size:45px;
    background:linear-gradient(135deg,#9d50bb,#6e48aa);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
}
.card {
    background:#1f1c3d;
    padding:20px;
    border-radius:15px;
    box-shadow:0 0 25px rgba(157,80,187,0.4);
}
button {
    padding:12px 20px;
    border:none;
    border-radius:10px;
    background:linear-gradient(135deg,#9d50bb,#6e48aa);
    color:#fff;
    cursor:pointer;
    margin-top:10px;
}
.script p {
    background:#2a244a;
    padding:10px;
    border-radius:8px;
    margin:5px 0;
}
</style>

</head>
<body>

<div class="container">
<h1>😈 GOD MODE AI</h1>

<div class="grid">

<div class="card">
<h3>🎯 الفكرة</h3>
<button onclick="gen()">توليد</button>
<div id="idea"></div>
</div>

<div class="card">
<h3>📜 السكربت</h3>
<div id="script" class="script"></div>
</div>

<div class="card">
<h3>🎬 الفيديو</h3>
<button onclick="make()">إنشاء فيديو</button>
<button onclick="download()">تحميل</button>
</div>

</div>
</div>

<script>
function gen(){
fetch('/generate')
.then(r=>r.json())
.then(d=>{
document.getElementById('idea').innerText=d.idea
document.getElementById('script').innerHTML=
d.script.map(x=>"<p>"+x+"</p>").join("")
})
}

function make(){
fetch('/video').then(()=>alert("🔥 تم إنشاء الفيديو"))
}

function download(){
window.location='/download'
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)