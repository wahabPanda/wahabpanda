import yt_dlp
import requests
import urllib.parse
import os
from flask import Flask, render_template_string, request, Response, stream_with_context

app = Flask(__name__)

# ==========================================
# 🎨 1. COMMON NAVBAR
# ==========================================
NAVBAR = """
<style>
    body.light-mode { background-color: #f8fafc !important; color: #0f172a !important; }
    body.light-mode nav, body.light-mode #mobileMenu, body.light-mode .glass { background-color: #ffffff !important; border-color: #e2e8f0 !important; }
    body.light-mode .text-white { color: #0f172a !important; }
    body.light-mode .text-zinc-400 { color: #475569 !important; }
    body.light-mode .bg-\\[\\#18181b\\] { background-color: #ffffff !important; }
    body.light-mode .bg-zinc-900 { background-color: #f1f5f9 !important; color: #0f172a !important; border-color: #cbd5e1 !important; }
</style>

<nav class="w-full bg-[#0f0f13] border-b border-zinc-800 p-4 sticky top-0 z-40 shadow-xl flex justify-between items-center">
    <a href="/" class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">🐼 WahabPanda</a>
    <button onclick="toggleMenu()" class="text-zinc-400 hover:text-emerald-400 focus:outline-none">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
    </button>
</nav>

<div id="mobileMenu" class="fixed inset-0 bg-[#09090b] z-50 hidden flex-col transition-all duration-300 shadow-2xl overflow-y-auto">
    <div class="flex justify-between items-center p-4 border-b border-zinc-800 bg-[#0f0f13]">
        <a href="/" class="text-2xl font-black text-emerald-400">🐼 WahabPanda</a>
        <button onclick="toggleMenu()" class="bg-zinc-800 text-emerald-400 p-2 rounded-lg hover:bg-zinc-700 transition"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
    </div>
    <div class="flex flex-col p-6 font-bold text-zinc-300">
        <a href="/tool/tiktok" class="py-4 border-b border-zinc-800/50">🎵 TikTok</a>
        <a href="/tool/youtube" class="py-4 border-b border-zinc-800/50">▶️ YouTube</a>
        <a href="/tool/instagram" class="py-4 border-b border-zinc-800/50">📸 Instagram</a>
        <a href="/tool/facebook" class="py-4 border-b border-zinc-800/50">📘 Facebook</a>
        <a href="/tool/twitter" class="py-4 border-b border-zinc-800/50">𝕏 Twitter (X)</a>
        <a href="/tool/pinterest" class="py-4 border-b border-zinc-800/50">📌 Pinterest</a>
        <a href="/tool/snapchat" class="py-4 border-b border-zinc-800/50">👻 Snapchat</a>
    </div>
</div>

<script>
    function toggleMenu() { const m = document.getElementById('mobileMenu'); m.classList.toggle('hidden'); m.classList.toggle('flex'); }
</script>
"""

# ==========================================
# 🏠 2. HOME PAGE
# ==========================================
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WahabPanda | Best Video Downloader</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background-color: #09090b; color: #f4f4f5; font-family: 'Inter', sans-serif; }</style>
</head>
<body class="flex flex-col items-center min-h-screen">
    {{ navbar|safe }}
    <div class="text-center mt-12 mb-10 px-4">
        <h1 class="text-5xl md:text-7xl font-black mb-4 tracking-tighter text-white">
            Download Videos <br><span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">From Anywhere.</span>
        </h1>
        <p class="text-zinc-400 text-lg max-w-2xl mx-auto">Fast, free, and no watermarks. Support for YouTube, TikTok, Pinterest & more.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl w-full px-4 mb-20">
        <a href="/tool/tiktok" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-pink-500 transition shadow-lg text-xl font-bold text-pink-400">🎵 TikTok</a>
        <a href="/tool/youtube" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-red-500 transition shadow-lg text-xl font-bold text-red-500">▶️ YouTube</a>
        <a href="/tool/instagram" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-purple-500 transition shadow-lg text-xl font-bold text-purple-400">📸 Instagram</a>
        <a href="/tool/facebook" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-blue-600 transition shadow-lg text-xl font-bold text-blue-500">📘 Facebook</a>
        <a href="/tool/pinterest" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-red-600 transition shadow-lg text-xl font-bold text-red-600">📌 Pinterest</a>
        <a href="/tool/snapchat" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-yellow-500 transition shadow-lg text-xl font-bold text-yellow-500">👻 Snapchat</a>
    </div>
</body>
</html>
"""

# ==========================================
# 🛠️ 3. TOOL PAGE
# ==========================================
TOOL_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ tool_name }} Downloader | WahabPanda</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background-color: #09090b; color: #f4f4f5; font-family: 'Inter', sans-serif; } .glass { background: #18181b; border: 1px solid #27272a; }</style>
</head>
<body class="flex flex-col items-center min-h-screen">
    {{ navbar|safe }}
    <div class="w-full max-w-3xl glass rounded-2xl p-6 md:p-8 mt-8 mx-4 shadow-2xl border-t-4 mb-20" style="border-top-color: {{ theme_color }};">
        <h1 class="text-3xl md:text-4xl font-black mb-6 text-center uppercase" style="color: {{ theme_color }};">{{ tool_name }} Downloader</h1>
        
        <form method="POST" onsubmit="document.getElementById('loading').style.display='block';">
            <div class="flex flex-col gap-4">
                <textarea name="urls" rows="3" placeholder="Paste link here..." class="w-full p-4 rounded-xl bg-zinc-900 text-white border border-zinc-700 focus:outline-none" required></textarea>
                <button type="submit" class="w-full font-bold py-4 rounded-xl transition text-white text-lg shadow-lg hover:scale-[1.02] transform" style="background-color: {{ theme_color }};">
                    🚀 Start Extraction
                </button>
            </div>
        </form>

        <div id="loading" class="hidden text-center mt-8 font-bold animate-pulse" style="color: {{ theme_color }};">
            Fetching video... Please wait ⏳
        </div>

        {% if error %} <div class="mt-6 p-4 bg-red-900/30 border border-red-800 text-red-400 rounded-xl text-center font-bold">❌ {{ error }}</div> {% endif %}
        
        {% if videos %}
            <div class="mt-8 space-y-6">
            {% for video in videos %}
            <div class="p-6 bg-zinc-900 rounded-xl border border-zinc-700 flex flex-col md:flex-row gap-6 items-center">
                <img src="{{ video.cover }}" class="w-full md:w-1/3 rounded-xl shadow-lg border border-zinc-800">
                <div class="w-full md:w-2/3 flex flex-col items-center md:items-start">
                    <span class="text-xs font-black px-4 py-1 rounded-full mb-3 uppercase tracking-widest" style="background-color: {{ theme_color }}; color: #000;">✅ {{ video.platform }}</span>
                    <h2 class="text-lg font-bold text-white mb-4 text-center md:text-left">{{ video.title }}</h2>
                    <a href="{{ video.download_link }}" target="_blank" class="w-full text-center text-white font-black py-4 rounded-xl transition shadow-xl text-lg hover:scale-[1.02] transform" style="background-color: {{ theme_color }};">
                        📥 Download MP4
                    </a>
                </div>
            </div>
            {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# ==========================================
# 🧠 BACKEND LOGIC
# ==========================================
@app.route('/')
def home():
    return render_template_string(HOME_PAGE, navbar=NAVBAR)

@app.route('/tool/<platform>', methods=['GET', 'POST'])
def tool_page(platform):
    configs = {
        'tiktok': {'name': 'TikTok', 'color': '#ec4899'},
        'instagram': {'name': 'Instagram', 'color': '#a855f7'},
        'facebook': {'name': 'Facebook', 'color': '#3b82f6'},
        'youtube': {'name': 'YouTube', 'color': '#ef4444'},
        'twitter': {'name': 'Twitter', 'color': '#9ca3af'},
        'pinterest': {'name': 'Pinterest', 'color': '#dc2626'}, 
        'snapchat': {'name': 'Snapchat', 'color': '#eab308'}  
    }
    
    if platform not in configs: return "Tool not found!", 404
    config = configs[platform]
    
    videos_data = []
    error_msg = None

    if request.method == 'POST':
        urls = [u.strip() for u in request.form.get('urls', '').split('\n') if u.strip()]
        
        for url in urls[:3]:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    }
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    raw_url = info.get('url')
                    if raw_url:
                        proxy_url = f"/proxy_download?video_url={urllib.parse.quote(raw_url)}"
                        videos_data.append({
                            'platform': info.get('extractor_key', platform).capitalize(),
                            'title': info.get('title', 'Video')[:60],
                            'cover': info.get('thumbnail', 'https://via.placeholder.com/500'),
                            'download_link': proxy_url
                        })
            except Exception as e:
                error_msg = "Could not fetch video. Please check the link."

    return render_template_string(TOOL_PAGE, navbar=NAVBAR, tool_name=config['name'], theme_color=config['color'], videos=videos_data, error=error_msg)

@app.route('/proxy_download')
def proxy_download():
    video_url = urllib.parse.unquote(request.args.get('video_url'))
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = requests.get(video_url, headers=headers, stream=True)
        return Response(stream_with_context(req.iter_content(chunk_size=1024*1024)), 
                        content_type='application/octet-stream', 
                        headers={'Content-Disposition': 'attachment; filename="WahabPanda_Video.mp4"'})
    except Exception as e:
        return f"Error: {str(e)}"

# 🚀 Gunicorn کے لیے فائنل لائن
if __name__ == "__main__":
    app.run()
