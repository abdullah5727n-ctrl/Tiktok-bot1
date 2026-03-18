from flask import Flask, render_template_string, jsonify
import random

app = Flask(__name__)

# ===============================
# IDEAS
# ===============================
ideas = [
    "3 أشياء مستحيل تعرفها 😳",
    "سر خطير محد يقولك 🔥",
    "وش يصير لو ما نمت يومين؟ 😨",
    "أغرب حقيقة في العالم 🤯",
    "معلومة راح تغير حياتك 🔥"
]

scripts = [
    ["هل تعلم أن...", "في شيء غريب...", "تابع للنهاية 😳"],
    ["99% ما يعرفون...", "لكن الحقيقة...", "صدمة 🔥"],
    ["هذا الشيء خطير...", "انتبه له...", "لا تسوي كذا 😨"]
]

current = {"idea": "", "script": []}

# ===============================
# GENERATE
# ===============================
@app.route("/generate")
def generate():
    current["idea"] = random.choice(ideas)
    current["script"] = random.choice(scripts)
    return jsonify(current)

# ===============================
# UI (Legendary Purple)
# ===============================
HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Legendary Dashboard</title>
<style>
body {
    margin:0;
    font-family:sans-serif;
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color:#fff;
    text-align:center;
}
h1 {
    font-size:40px;
    background:linear-gradient(135deg,#9d50bb,#6e48aa);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.container {
    padding:30px;
}
.card {
    background:#1f1c3d;
    padding:20px;
    margin:20px auto;
    border-radius:15px;
    max-width:500px;
    box-shadow:0 0 20px rgba(157,80,187,0.4);
}
button {
    padding:15px 25px;
    margin:10px;
    border:none;
    border-radius:10px;
    background:linear-gradient(135deg,#9d50bb,#6e48aa);
    color:#fff;
    font-size:16px;
    cursor:pointer;
}
button:hover {
    transform:scale(1.05);
}
p {
    font-size:18px;
}
</style>
</head>
<body>

<div class="container">
<h1>🔥 Legendary AI Dashboard</h1>

<div class="card">
<button onclick="generate()">🎯 توليد فكرة</button>
<p id="idea"></p>
<div id="script"></div>
</div>

</div>

<script>
function generate(){
fetch('/generate')
.then(res=>res.json())
.then(data=>{
document.getElementById('idea').innerText = data.idea;
document.getElementById('script').innerHTML =
data.script.map(x=>"<p>"+x+"</p>").join("");
});
}
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
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)