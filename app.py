import os
import yt_dlp
import requests
import urllib.parse
from flask import Flask, render_template_string, request, Response, stream_with_context

app = Flask(__name__)

# ==========================================
# 🎨 1. COMMON NAVBAR (JavaScript & Dark Mode)
# ==========================================
NAVBAR = """
<style>
    body.light-mode { background-color: #f8fafc !important; color: #0f172a !important; }
    body.light-mode nav, body.light-mode #mobileMenu, body.light-mode .glass { background-color: #ffffff !important; border-color: #e2e8f0 !important; }
    body.light-mode .text-white { color: #0f172a !important; }
    body.light-mode .text-zinc-400 { color: #475569 !important; }
    body.light-mode .bg-\\[\\#18181b\\] { background-color: #ffffff !important; }
    body.light-mode .bg-zinc-900 { background-color: #f1f5f9 !important; color: #0f172a !important; border-color: #cbd5e1 !important; }
    body.light-mode .bg-\\[\\#09090b\\] { background-color: #f8fafc !important; }
    body.light-mode .bg-\\[\\#0f0f13\\] { background-color: #ffffff !important; }
</style>

<nav class="w-full bg-[#0f0f13] border-b border-zinc-800 p-4 sticky top-0 z-40 shadow-xl flex justify-between items-center transition-colors duration-300">
    <a href="/" class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500 flex items-center gap-2">🐼 WahabPanda</a>
    <button onclick="toggleMenu()" class="text-zinc-400 hover:text-emerald-400 focus:outline-none">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
    </button>
</nav>

<div id="mobileMenu" class="fixed inset-0 bg-[#09090b] z-50 hidden flex-col transition-all duration-300 shadow-2xl overflow-y-auto">
    <div class="flex justify-between items-center p-4 border-b border-zinc-800 bg-[#0f0f13]">
        <a href="/" class="text-2xl font-black text-emerald-400">🐼 WahabPanda</a>
        <button onclick="toggleMenu()" class="bg-zinc-800 text-emerald-400 p-2 rounded-lg hover:bg-zinc-700 transition"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
    </div>

    <div class="flex flex-col p-6">
        <a href="/tool/sora" class="text-zinc-300 font-bold hover:text-emerald-400 py-4 border-b border-zinc-800/50">✨ Sora AI</a>
        <a href="/tool/tiktok" class="text-zinc-300 font-bold hover:text-pink-400 py-4 border-b border-zinc-800/50">🎵 TikTok</a>
        <a href="/tool/youtube" class="text-zinc-300 font-bold hover:text-red-500 py-4 border-b border-zinc-800/50">▶️ YouTube</a>
        <a href="/tool/instagram" class="text-zinc-300 font-bold hover:text-purple-400 py-4 border-b border-zinc-800/50">📸 Instagram</a>
        <a href="/tool/facebook" class="text-zinc-300 font-bold hover:text-blue-500 py-4 border-b border-zinc-800/50">📘 Facebook</a>
        <a href="/tool/twitter" class="text-zinc-300 font-bold hover:text-gray-300 py-4 border-b border-zinc-800/50">𝕏 Twitter (X)</a>
        <a href="/tool/pinterest" class="text-zinc-300 font-bold hover:text-red-600 py-4 border-b border-zinc-800/50">📌 Pinterest</a>
        <a href="/tool/reddit" class="text-zinc-300 font-bold hover:text-orange-500 py-4 border-b border-zinc-800/50">👽 Reddit</a>
        <a href="/tool/snapchat" class="text-zinc-300 font-bold hover:text-yellow-400 py-4 border-b border-zinc-800/50">👻 Snapchat</a>
        
        <div class="mt-8 mb-4">
            <button onclick="toggleTheme(); toggleMenu();" class="flex items-center text-emerald-400 font-bold py-2 w-full text-left">
                <span id="theme-icon" class="mr-3 text-xl">☀️</span> <span id="theme-text" data-i18n="m-light">Light Mode</span>
            </button>
        </div>

        <div class="mt-6 mb-10">
            <p class="text-zinc-500 text-sm mb-4 font-bold tracking-widest flex items-center"><span class="mr-2">🌐</span> LANGUAGE</p>
            <div class="grid grid-cols-2 gap-4">
                <button onclick="setLang('en'); toggleMenu();" id="lang-en" class="lang-btn text-zinc-400 hover:text-white text-sm text-left transition">🇺🇸 English</button>
                <button onclick="setLang('ur'); toggleMenu();" id="lang-ur" class="lang-btn text-zinc-400 hover:text-white text-sm text-left transition">🇵🇰 اردو</button>
            </div>
        </div>
    </div>
</div>

<script>
    const i18n = {
        'en': { 'm-light': 'Light Mode', 'm-dark': 'Dark Mode', 'h-t1': 'Download Videos', 'h-t2': 'From Anywhere.', 'h-desc': 'Fast, free video downloads. Support Single & Bulk Links.', 'btn-ext': 'Extract All Videos', 'wait': 'Extracting Videos... Please wait ⏳', 'p-link': 'Paste links here (one link per line)...', 'btn-dl': 'Download MP4' },
        'ur': { 'm-light': 'لائٹ موڈ', 'm-dark': 'ڈارک موڈ', 'h-t1': 'ویڈیوز ڈاؤنلوڈ کریں', 'h-t2': 'کہیں سے بھی۔', 'h-desc': 'اب ایک ساتھ کئی ویڈیوز بھی ڈاؤنلوڈ کی جا سکتی ہیں۔', 'btn-ext': 'تمام ویڈیوز نکالیں', 'wait': 'ویڈیوز نکالی جا رہی ہیں... ⏳', 'p-link': 'یہاں لنکس پیسٹ کریں (ہر لائن میں ایک لنک)...', 'btn-dl': 'ڈاؤنلوڈ کریں' }
    };
    function toggleMenu() { const m = document.getElementById('mobileMenu'); m.classList.toggle('hidden'); m.classList.toggle('flex'); }
    function toggleTheme() { document.body.classList.toggle('light-mode'); const isLight = document.body.classList.contains('light-mode'); localStorage.setItem('theme', isLight ? 'light' : 'dark'); updateThemeUI(isLight); }
    function updateThemeUI(isLight) { const lang = localStorage.getItem('lang') || 'en'; document.getElementById('theme-icon').innerText = isLight ? '🌙' : '☀️'; document.getElementById('theme-text').innerText = isLight ? i18n[lang]['m-dark'] : i18n[lang]['m-light']; }
    function setLang(lang) {
        localStorage.setItem('lang', lang);
        document.querySelectorAll('[data-i18n]').forEach(el => { const key = el.getAttribute('data-i18n'); if(i18n[lang][key]) el.innerText = i18n[lang][key]; });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { const key = el.getAttribute('data-i18n-placeholder'); if(i18n[lang][key]) el.placeholder = i18n[lang][key]; });
        document.querySelectorAll('.lang-btn').forEach(btn => { btn.classList.remove('bg-emerald-900/20', 'text-emerald-400', 'border-emerald-500/30'); btn.classList.add('text-zinc-400'); btn.classList.remove('border'); });
        const activeBtn = document.getElementById('lang-' + lang);
        if(activeBtn) { activeBtn.classList.add('bg-emerald-900/20', 'text-emerald-400', 'border', 'border-emerald-500/30'); activeBtn.classList.remove('text-zinc-400'); }
        updateThemeUI(document.body.classList.contains('light-mode')); 
    }
    window.onload = () => { if(localStorage.getItem('theme') === 'light') { document.body.classList.add('light-mode'); updateThemeUI(true); } const savedLang = localStorage.getItem('lang') || 'en'; setLang(savedLang); };
</script>
"""

# ==========================================
# 🏠 2. HOME PAGE (With Mega SEO Engine)
# ==========================================
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>WahabPanda | Universal Video Downloader - TikTok, YouTube, Sora & More</title>
    <meta name="title" content="WahabPanda | Universal Video Downloader - Free & Fast">
    <meta name="description" content="Download HD videos from TikTok (No Watermark), YouTube, Sora AI, Instagram, Facebook, Twitter, and more. 100% Free, Fast, and secure multi-video downloader.">
    <meta name="keywords" content="video downloader, tiktok video download no watermark, youtube downloader, sora video download, facebook video download, instagram reels download, free video saver, wahabpanda, savepanda alternative">
    <meta name="robots" content="index, follow">
    <meta name="author" content="Wahab Creators">

    <meta property="og:type" content="website">
    <meta property="og:title" content="WahabPanda | Universal Video Downloader">
    <meta property="og:description" content="Download HD videos from 1000+ websites for free. No watermark, fast and secure.">
    <meta property="og:image" content="https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg"> <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="WahabPanda | The Ultimate Video Downloader">
    <meta property="twitter:description" content="Download your favorite videos instantly in HD.">

    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "WahabPanda Downloader",
      "url": "https://wahabpanda.com",
      "description": "A free, universal video downloader supporting TikTok, YouTube, Instagram, and more.",
      "applicationCategory": "MultimediaApplication",
      "operatingSystem": "All",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      }
    }
    </script>

    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background-color: #09090b; color: #f4f4f5; font-family: 'Inter', sans-serif; transition: background-color 0.3s, color 0.3s; }</style>
</head>
<body class="flex flex-col items-center min-h-screen">
    {{ navbar|safe }}
    <div class="text-center mt-12 mb-10 px-4 transition-all">
        <h1 class="text-5xl md:text-7xl font-black mb-4 tracking-tighter text-white">
            <span data-i18n="h-t1">Download Videos</span> <br><span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500" data-i18n="h-t2">From Anywhere.</span>
        </h1>
        <p class="text-zinc-400 text-lg max-w-2xl mx-auto" data-i18n="h-desc">Fast, free video downloads. Support Single & Bulk Links.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl w-full px-4 mb-20">
        <a href="/tool/tiktok" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-pink-500 transition shadow-lg"><div class="text-3xl mb-3">🎵</div><h2 class="text-xl font-bold text-pink-400">TikTok</h2></a>
        <a href="/tool/youtube" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-red-500 transition shadow-lg"><div class="text-3xl mb-3">▶️</div><h2 class="text-xl font-bold text-red-500">YouTube</h2></a>
        <a href="/tool/sora" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-emerald-500 transition shadow-lg"><div class="text-3xl mb-3">✨</div><h2 class="text-xl font-bold text-emerald-400">Sora AI</h2></a>
        <a href="/tool/instagram" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-purple-500 transition shadow-lg"><div class="text-3xl mb-3">📸</div><h2 class="text-xl font-bold text-purple-400">Instagram</h2></a>
        <a href="/tool/facebook" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-blue-600 transition shadow-lg"><div class="text-3xl mb-3">📘</div><h2 class="text-xl font-bold text-blue-500">Facebook</h2></a>
        <a href="/tool/twitter" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-gray-400 transition shadow-lg"><div class="text-3xl mb-3">𝕏</div><h2 class="text-xl font-bold text-gray-400">Twitter (X)</h2></a>
        <a href="/tool/pinterest" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-red-600 transition shadow-lg"><div class="text-3xl mb-3">📌</div><h2 class="text-xl font-bold text-red-600">Pinterest</h2></a>
        <a href="/tool/reddit" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-orange-500 transition shadow-lg"><div class="text-3xl mb-3">👽</div><h2 class="text-xl font-bold text-orange-500">Reddit</h2></a>
        <a href="/tool/snapchat" class="bg-[#18181b] border border-zinc-800 p-6 rounded-2xl hover:border-yellow-500 transition shadow-lg"><div class="text-3xl mb-3">👻</div><h2 class="text-xl font-bold text-yellow-500">Snapchat</h2></a>
    </div>
</body>
</html>
"""

# ==========================================
# 🛠️ 3. TOOL PAGE (With Dynamic SEO)
# ==========================================
TOOL_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>{{ seo_title }} | WahabPanda</title>
    <meta name="title" content="{{ seo_title }} - WahabPanda">
    <meta name="description" content="{{ seo_desc }}">
    <meta name="keywords" content="{{ seo_keywords }}">
    <meta name="robots" content="index, follow">
    
    <meta property="og:title" content="{{ seo_title }}">
    <meta property="og:description" content="{{ seo_desc }}">
    <meta property="og:type" content="website">

    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background-color: #09090b; color: #f4f4f5; font-family: 'Inter', sans-serif; } .glass { background: #18181b; border: 1px solid #27272a; transition: background-color 0.3s; }</style>
</head>
<body class="flex flex-col items-center min-h-screen">
    {{ navbar|safe }}
    <div class="w-full max-w-3xl glass rounded-2xl p-6 md:p-8 mt-8 mx-4 shadow-2xl border-t-4 mb-20" style="border-top-color: {{ theme_color }};">
        <h1 class="text-3xl md:text-4xl font-black mb-2 text-center" style="color: {{ theme_color }};">{{ tool_name }} Video Downloader</h1>
        <p class="text-zinc-400 text-center mb-6 text-sm">Download HD {{ tool_name }} videos instantly. Paste one or multiple links.</p>
        
        <form method="POST" onsubmit="document.getElementById('loading').style.display='block';">
            <div class="flex flex-col gap-4">
                <textarea name="urls" rows="4" data-i18n-placeholder="p-link" placeholder="Paste links here (one link per line)..." class="w-full p-4 rounded-xl bg-zinc-900 text-white border border-zinc-700 focus:outline-none resize-none" style="focus:border-color: {{ theme_color }};" required></textarea>
                <button type="submit" class="w-full font-bold py-4 rounded-xl transition text-white text-lg shadow-lg hover:scale-[1.02] transform" style="background-color: {{ theme_color }};">
                    🚀 <span data-i18n="btn-ext">Extract All Videos</span>
                </button>
            </div>
        </form>

        <div id="loading" class="hidden text-center mt-8">
            <p class="font-bold animate-pulse text-lg" style="color: {{ theme_color }};" data-i18n="wait">Extracting Videos... Please wait ⏳</p>
        </div>

        {% if error %} <div class="mt-6 p-4 bg-red-900/30 border border-red-800 text-red-400 rounded-xl text-center font-bold">❌ {{ error }}</div> {% endif %}
        {% if info %} <div class="mt-6 p-4 bg-yellow-900/30 border border-yellow-800 text-yellow-400 rounded-xl text-center font-bold">⚠️ {{ info }}</div> {% endif %}
        
        {% if videos %}
            <div class="mt-8 space-y-6">
            {% for video in videos %}
            <div class="p-6 bg-zinc-900 rounded-xl border border-zinc-700 flex flex-col md:flex-row gap-6 items-center shadow-inner">
                <img src="{{ video.cover }}" class="w-full md:w-1/3 rounded-xl shadow-lg border border-zinc-800">
                <div class="w-full md:w-2/3 flex flex-col justify-center items-center md:items-start text-center md:text-left">
                    <span class="text-xs font-black px-4 py-1 rounded-full w-max mb-3 uppercase tracking-widest shadow-md" style="background-color: {{ theme_color }}; color: #000;">✅ {{ video.platform }}</span>
                    <h2 class="text-lg font-bold text-white mb-4 line-clamp-2 px-2 md:px-0">{{ video.title }}</h2>
                    
                    {% if video.formats %}
                    <div class="w-full mb-4">
                        <select onchange="this.nextElementSibling.href = this.value" class="w-full p-3 rounded-xl bg-zinc-800 text-white border border-zinc-600 focus:outline-none font-bold" style="border-left: 4px solid {{ theme_color }};">
                            {% for f in video.formats %}
                                <option value="{{ f.url }}">{{ f.res }} (HD Audio + Video)</option>
                            {% endfor %}
                        </select>
                        <a href="{% if video.formats %}{{ video.formats[0].url }}{% else %}{{ video.download_link }}{% endif %}" target="_blank" class="mt-4 block w-full text-center text-white font-black py-4 rounded-xl transition shadow-xl text-lg hover:scale-[1.02] transform" style="background-color: {{ theme_color }};">
                            📥 <span data-i18n="btn-dl">Download MP4</span>
                        </a>
                    </div>
                    {% else %}
                        <a href="{{ video.download_link }}" target="_blank" class="w-full text-center text-white font-black py-4 rounded-xl transition shadow-xl text-lg hover:scale-[1.02] transform" style="background-color: {{ theme_color }};">
                            📥 <span data-i18n="btn-dl">Download MP4</span>
                        </a>
                    {% endif %}
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
# 🧠 BACKEND ROUTES (With SEO Injector)
# ==========================================
@app.route('/')
def home():
    return render_template_string(HOME_PAGE, navbar=NAVBAR)

@app.route('/tool/<platform>', methods=['GET', 'POST'])
def tool_page(platform):
    configs = {
        'tiktok': {'name': 'TikTok', 'color': '#ec4899', 'kw': 'tiktok downloader, tiktok video download, no watermark'},
        'instagram': {'name': 'Instagram', 'color': '#a855f7', 'kw': 'instagram reels download, ig video saver, insta downloader'},
        'facebook': {'name': 'Facebook', 'color': '#3b82f6', 'kw': 'facebook video download, fb watch downloader, fb reels save'},
        'youtube': {'name': 'YouTube', 'color': '#ef4444', 'kw': 'youtube video downloader, yt shorts download, free yt saver'},
        'twitter': {'name': 'X (Twitter)', 'color': '#9ca3af', 'kw': 'twitter video download, x video saver, download from x'},
        'sora': {'name': 'Sora AI', 'color': '#10b981', 'kw': 'sora video downloader, openai sora download, sora ai saver'},
        'pinterest': {'name': 'Pinterest', 'color': '#dc2626', 'kw': 'pinterest video download, pin saver, pinterest downloader'}, 
        'reddit': {'name': 'Reddit', 'color': '#f97316', 'kw': 'reddit video download, save reddit video, reddit downloader'},    
        'snapchat': {'name': 'Snapchat', 'color': '#eab308', 'kw': 'snapchat video download, snap story saver, snap downloader'}  
    }
    
    if platform not in configs: return "Tool not found!", 404
    config = configs[platform]
    
    # 🚀 DYNAMIC SEO INJECTION
    seo_title = f"{config['name']} Video Downloader"
    seo_desc = f"Use WahabPanda to download {config['name']} videos for free in HD quality. No watermark, fast, and 100% secure."
    seo_keywords = f"{config['kw']}, wahabpanda, free video downloader"
    
    videos_data = []
    error_msgs = []
    info_msg = None

    if request.method == 'POST':
        raw_urls = request.form.get('urls', '').strip().split('\n')
        urls = [u.strip() for u in raw_urls if u.strip()]
        
        if len(urls) > 5:
            info_msg = "We have processed the first 5 links to prevent server overload."
            urls = urls[:5]

        for url in urls:
            url_lower = url.lower()
            if platform in ['sora', 'twitter'] or 'x.com' in url_lower or 'twitter.com' in url_lower:
                if 'sora.chatgpt.com' in url_lower or 'openai.com' in url_lower:
                    error_msgs.append("Sora direct links protected. Use X/TikTok links.")
                else:
                    api_url = url_lower.replace("twitter.com", "api.vxtwitter.com").replace("x.com", "api.vxtwitter.com")
                    try:
                        res = requests.get(api_url).json()
                        if 'mediaURLs' in res and len(res['mediaURLs']) > 0:
                            videos_data.append({'platform': '𝕏 Twitter / X', 'title': res.get('text', 'Video')[:60], 'cover': 'https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg', 'download_link': f"/proxy_download?video_url={urllib.parse.quote(res['mediaURLs'][0])}", 'formats': None})
                        else: error_msgs.append(f"No video found: {url[:30]}...")
                    except Exception: error_msgs.append(f"Security blocked: {url[:30]}...")
            else:
                try:
                    # 🔥 بس یہ ہے وہ نئی جادوئی سیٹنگ جس نے آپ کے پچھلے کوڈ کو بالکل نہیں چھیڑا
                    ydl_opts = {
                        'quiet': True, 
                        'no_warnings': True, 
                        'format': 'best',
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                        },
                        'extractor_args': {'youtube': ['player_client=ios,android']},
                        'extractor_retries': 3,
                        'socket_timeout': 15,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        final_formats = None
                        if platform == 'youtube':
                            formats_list = []
                            seen_res = set()
                            for f in info.get('formats', []):
                                res = f.get('height')
                                if res and f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                                    res_str = f"{res}p"
                                    if res_str not in seen_res:
                                        proxy_url = f"/proxy_download?video_url={urllib.parse.quote(f.get('url'))}"
                                        formats_list.append({'res': res_str, 'url': proxy_url, 'val': res})
                                        seen_res.add(res_str)
                            formats_list = sorted(formats_list, key=lambda x: x['val'], reverse=True)
                            final_formats = formats_list

                        raw_url = info.get('url')
                        force_download_link = f"/proxy_download?video_url={urllib.parse.quote(raw_url)}" if raw_url else ""
                        videos_data.append({'platform': info.get('extractor_key', platform).capitalize(), 'title': info.get('title', 'Video')[:60], 'cover': info.get('thumbnail', 'https://via.placeholder.com/500'), 'download_link': force_download_link, 'formats': final_formats if final_formats and len(final_formats) > 0 else None})
                except Exception as e: 
                    error_msgs.append(f"Download failed for {url[:30]}... Error: {str(e)}")

    final_error = " | ".join(error_msgs) if error_msgs else None
    return render_template_string(TOOL_PAGE, navbar=NAVBAR, tool_name=config['name'], theme_color=config['color'], videos=videos_data, error=final_error, info=info_msg, seo_title=seo_title, seo_desc=seo_desc, seo_keywords=seo_keywords)

@app.route('/proxy_download')
def proxy_download():
    video_url = urllib.parse.unquote(request.args.get('video_url'))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        req = requests.get(video_url, headers=headers, stream=True)
        return Response(stream_with_context(req.iter_content(chunk_size=1024*1024)), content_type='application/octet-stream', headers={'Content-Disposition': 'attachment; filename="WahabPanda_Video.mp4"'})
    except Exception as e:
        return f"Download Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
