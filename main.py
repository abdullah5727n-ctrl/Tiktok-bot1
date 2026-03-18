from flask import Flask, render_template_string, jsonify, send_file
import random
from moviepy.editor import TextClip

app = Flask(__name__)

ideas = [
    "3 أشياء مستحيل تعرفها",
    "سر خطير محد يقولك",
    "وش يصير لو ما نمت يومين؟",
    "أغرب حقيقة في العالم"
]

scripts = [
    ["هل تعلم أن...", "في شيء غريب...", "تابع للنهاية"],
    ["99% ما يعرفون...", "لكن الحقيقة...", "صدمة"],
    ["هذا الشيء خطير...", "انتبه له...", "لا تسوي كذا"]
]

current = {"idea": "", "script": []}

@app.route("/generate")
def generate():
    current["idea"] = random.choice(ideas)
    current["script"] = random.choice(scripts)
    return jsonify(current)

@app.route("/video")
def video():
    try:
        text = current["idea"] + "\n" + "\n".join(current["script"])

        clip = TextClip(
            text,
            fontsize=60,
            color='white',
            bg_color='black',
            size=(720, 1280),
            method='caption'
        ).set_duration(6)

        clip.write_videofile("output.mp4", fps=24)

        return jsonify({"status": "done"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/download")
def download():
    return send_file("output.mp4", as_attachment=True)

HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<title>SwiftStore</title>

<style>
body {
    margin:0;
    font-family:sans-serif;
    background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color:#fff;
}

.container {
    max-width:1200px;
    margin:auto;
    padding:40px;
}

h1 {
    text-align:center;
    font-size:50px;
    margin-bottom:40px;
    background:linear-gradient(135deg,#9d50bb,#6e48aa);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:30px;
}

.card {
    background:#1f1c3d;
    padding:30px;
    border-radius:20px;
    box-shadow:0 0 30px rgba(157,80,187,0.4);
}

button {
    padding:14px 25px;
    border:none;
    border-radius:12px;
    background:linear-gradient(135deg,#9d50bb,#6e48aa);
    color:#fff;
    cursor:pointer;
    font-size:16px;
    margin-top:10px;
}

button:hover {
    transform:scale(1.05);
}

.idea {
    font-size:22px;
    margin-top:15px;
}

.script p {
    background:#2a244a;
    padding:12px;
    border-radius:10px;
    margin:8px 0;
}

.full {
    grid-column: span 2;
    text-align:center;
}
</style>

</head>
<body>

<div class="container">

<h1>SwiftStore</h1>

<div class="grid">

<div class="card">
<h3>الفكرة</h3>
<button onclick="generate()">توليد</button>
<div id="idea" class="idea"></div>
</div>

<div class="card">
<h3>السكربت</h3>
<div id="script" class="script"></div>
</div>

<div class="card full">
<h3>الفيديو</h3>
<button onclick="makeVideo()">إنشاء فيديو</button>
<button onclick="download()">تحميل الفيديو</button>
</div>

</div>

</div>

<script>
function generate(){
fetch('/generate')
.then(res=>res.json())
.then(data=>{
document.getElementById('idea').innerText = data.idea
document.getElementById('script').innerHTML =
data.script.map(x=>"<p>"+x+"</p>").join("")
})
}

function makeVideo(){
fetch('/video').then(r=>r.json()).then(d=>{
if(d.status){
alert("تم إنشاء الفيديو")
}else{
alert("خطأ: " + d.error)
}
})
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