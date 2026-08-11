import os
import json
import re
from flask import Flask, request, redirect, render_template_string
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Google credentials from environment variable
google_creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if not google_creds_json:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")
info = json.loads(google_creds_json)
credentials = service_account.Credentials.from_service_account_info(
    info,
    scopes=['https://www.googleapis.com/auth/indexing']
)
indexing_service = build('indexing', 'v3', credentials=credentials)

def extract_post_id(url):
    """ইনস্টাগ্রাম পোস্ট URL থেকে শর্টকোড (যেমন CxYzAbCd) বের করে"""
    match = re.search(r'instagram\.com/p/([A-Za-z0-9_-]+)/?', url)
    return match.group(1) if match else None

# Google Search Console verification route
@app.route('/google9050b88856403157.html')
def google_verify():
    return 'google-site-verification: google9050b88856403157.html'

@app.route('/')
def home():
    return render_template_string('''
        <h1>ইনস্টা ইনডেক্সার</h1>
        <form action="/submit" method="post">
            <input type="text" name="insta_url" placeholder="ইনস্টাগ্রাম পোস্ট লিংক দিন" required style="width:400px">
            <button type="submit">Index Now</button>
        </form>
        <p>{{ message }}</p>
        <p><a href="/bulk">একসাথে অনেক লিংক জমা দিতে চান? (বাল্ক সাবমিশন)</a></p>
    ''', message=request.args.get('message',''))

@app.route('/submit', methods=['POST'])
def submit():
    insta_url = request.form['insta_url'].strip()
    post_id = extract_post_id(insta_url)
    if not post_id:
        return "ইনস্টাগ্রাম পোস্ট URL সঠিক নয়।", 400

    # সরাসরি পোস্টের ID দিয়ে আমাদের URL
    my_redirect_url = f"https://www.trevomo.com/go/{post_id}"

    body = {'url': my_redirect_url, 'type': 'URL_UPDATED'}
    try:
        indexing_service.urlNotifications().publish(body=body).execute()
        msg = f"✅ গুগলে জমা হয়েছে: {my_redirect_url}"
    except Exception as e:
        msg = f"⚠️ API এরর: {str(e)}<br>তবে রিডাইরেক্ট তৈরি: <a href='{my_redirect_url}'>{my_redirect_url}</a>"

    return render_template_string('''
        <h1>ইনস্টা ইনডেক্সার</h1>
        <p>{{ message|safe }}</p>
        <a href="/">আরেকটি লিংক দিন</a>
    ''', message=msg)

@app.route('/go/<code>')
def handle_redirect(code):
    """সরাসরি ইনস্টাগ্রামের পোস্ট URL-এ 301 রিডাইরেক্ট"""
    target_url = f"https://www.instagram.com/p/{code}/"
    resp = redirect(target_url, code=301)
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

# বাল্ক সাবমিশন পেইজ
@app.route('/bulk')
def bulk_form():
    return render_template_string('''
        <h1>বাল্ক ইনস্টাগ্রাম লিংক জমা দিন</h1>
        <p>প্রতি লাইনে একটি করে ইনস্টাগ্রাম পোস্ট URL পেস্ট করুন (সর্বোচ্চ ২০০টি)</p>
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
