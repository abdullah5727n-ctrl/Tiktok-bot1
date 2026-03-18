services:
  - type: web
    name: tiktok-bot
    runtime: python
    buildCommand: |
      apt-get update && apt-get install -y ffmpeg imagemagick
      pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
