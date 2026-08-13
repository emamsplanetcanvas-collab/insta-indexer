import os
import json
import re
from flask import Flask, request, redirect, render_template_string
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Google credentials from Render environment variable
google_creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if not google_creds_json:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")
info = json.loads(google_creds_json)
credentials = service_account.Credentials.from_service_account_info(
    info, scopes=['https://www.googleapis.com/auth/indexing']
)
indexing_service = build('indexing', 'v3', credentials=credentials)

def extract_post_id(url):
    """ইনস্টাগ্রাম পোস্ট URL থেকে শর্টকোড (যেমন CxYzAbCd) বের করে"""
    match = re.search(r'instagram\.com/p/([A-Za-z0-9_-]+)/?', url)
    return match.group(1) if match else None

# Google Search Console verification route (unchanged)
@app.route('/google9050b88856403157.html')
def google_verify():
    return 'google-site-verification: google9050b88856403157.html'

# Home with form
@app.route('/')
def home():
    return render_template_string('''
        <h1>ইনস্টা ইনডেক্সার (ক্যানোনিকাল)</h1>
        <form action="/submit" method="post">
            <input type="text" name="insta_url" placeholder="ইনস্টাগ্রাম পোস্ট URL দিন" required style="width:400px">
            <button type="submit">Index Now</button>
        </form>
        <p>{{ message }}</p>
        <p><a href="/bulk">বাল্ক সাবমিশন</a></p>
    ''', message=request.args.get('message',''))

# Submit handler
@app.route('/submit', methods=['POST'])
def submit():
    insta_url = request.form['insta_url'].strip()
    post_id = extract_post_id(insta_url)
    if not post_id:
        return "ইনস্টাগ্রাম পোস্ট URL সঠিক নয়।", 400

    # ক্যানোনিকাল পেজের URL (আপনার ডোমেইনে)
    page_url = f"https://www.trevomo.com/c/{post_id}"

    # Indexing API-তে জমা
    body = {'url': page_url, 'type': 'URL_UPDATED'}
    try:
        indexing_service.urlNotifications().publish(body=body).execute()
        msg = f"✅ গুগলে জমা হয়েছে: {page_url}"
    except Exception as e:
        msg = f"⚠️ API এরর: {str(e)}"

    return render_template_string('''
        <h1>জমা হয়েছে</h1>
        <p>{{ message|safe }}</p>
        <a href="/">আরেকটি দিন</a>
    ''', message=msg)

# ক্যানোনিকাল পেজ (দেখাবে না কাউকে, শুধু গুগলের জন্য)
@app.route('/c/<slug>')
def canonical_page(slug):
    insta_url = f"https://www.instagram.com/p/{slug}/"
    # পেজটি অত্যন্ত সরল, কোনো কন্টেন্ট নয়, শুধু ক্যানোনিকাল ট্যাগ ও মেটা রিফ্রেশ
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link rel="canonical" href="{{ target }}" />
            <meta http-equiv="refresh" content="0; url={{ target }}" />
            <title>Instagram Post</title>
        </head>
        <body style="text-align:center; padding:50px; font-family:Arial;">
            <p>Redirecting to Instagram... <a href="{{ target }}">Click here</a> if not redirected.</p>
        </body>
        </html>
    ''', target=insta_url)

# বাল্ক সাবমিশন পেজ (আগের মতোই)
@app.route('/bulk')
def bulk_form():
    return render_template_string('''
        <h1>বাল্ক ইনস্টাগ্রাম লিংক জমা দিন</h1>
        <p>প্রতি লাইনে একটি করে পোস্ট URL পেস্ট করুন (সর্বোচ্চ ২০০টি)</p>
        <textarea id="links" rows="15" cols="80" placeholder="https://www.instagram.com/p/CODE1/
https://www.instagram.com/p/CODE2/"></textarea><br><br>
        <button onclick="startBulk()">সবগুলো জমা করো</button>
        <div id="status"></div>
        <script>
            async function startBulk() {
                const links = document.getElementById('links').value.trim().split('\\n').filter(l => l.trim() !== '');
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = `মোট ${links.length} টি লিংক পাওয়া গেছে। জমা দেওয়া শুরু...<br>`;
                for (let i = 0; i < links.length; i++) {
                    const link = links[i].trim();
                    try {
                        const formData = new FormData();
                        formData.append('insta_url', link);
                        const response = await fetch('/submit', { method: 'POST', body: formData });
                        const text = await response.text();
                        statusDiv.innerHTML += `${i+1}. ${link} → ✅ জমা হয়েছে<br>`;
                    } catch (err) {
                        statusDiv.innerHTML += `${i+1}. ${link} → ❌ ভুল: ${err.message}<br>`;
                    }
                    await new Promise(r => setTimeout(r, 500));
                }
                statusDiv.innerHTML += `<br><b>সব শেষ! মোট ${links.length} টি লিংক জমা দেওয়া হয়েছে।</b>`;
            }
        </script>
    ''')
@app.route('/flights')
def flights():
    return render_template_string('''
        <html>
        <head>
            <title>Flights - Trevomo</title>
        </head>
        <body style="font-family:Arial; text-align:center; padding:50px;">
            <h1>Welcome to Trevomo Flights</h1>
            <p>Find the best flight deals here.</p>
            <p>Contact: support@trevomo.com</p>
        </body>
        </html>
    ''')
    @app.route('/robots.txt')
def robots_txt():
    return "User-agent: *\nAllow: /", 200, {'Content-Type': 'text/plain'}
if __name__ == '__main__':
    app.run(debug=True, port=5000)
