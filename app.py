import os
import json
from flask import Flask, request, redirect, render_template_string
import hashlib, time
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# ---- Google Indexing API setup (Env Variable থেকে Credentials পড়বে) ----
google_creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if not google_creds_json:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")

# JSON string থেকে dictionary, তারপর credentials object
info = json.loads(google_creds_json)
credentials = service_account.Credentials.from_service_account_info(
    info,
    scopes=['https://www.googleapis.com/auth/indexing']
)
indexing_service = build('indexing', 'v3', credentials=credentials)

# ---- বাকি অংশ আগের মতোই ----
redirect_map = {}

@app.route('/')
def home():
    return render_template_string('''
        <h1>ইনস্টা ইনডেক্সার</h1>
        <form action="/submit" method="post">
            <input type="text" name="insta_url" placeholder="ইনস্টাগ্রাম পোস্ট লিংক দিন" required style="width:400px">
            <button type="submit">Index Now</button>
        </form>
        <p>{{ message }}</p>
    ''', message=request.args.get('message',''))

@app.route('/submit', methods=['POST'])
def submit():
    insta_url = request.form['insta_url'].strip()
    if not insta_url.startswith('https://www.instagram.com/p/'):
        return "শুধুমাত্র Instagram পোস্ট URL দিন।", 400

    unique = hashlib.md5((insta_url + str(time.time())).encode()).hexdigest()[:8]
    short_path = f"go/{unique}"

    # আপনার ডোমেইন (trevomo.com) – এটি আর বদলাতে হবে না
    my_redirect_url = f"https://trevomo.com/{short_path}"

    redirect_map[short_path] = insta_url

    body = {'url': my_redirect_url, 'type': 'URL_UPDATED'}
    try:
        indexing_service.urlNotifications().publish(body=body).execute()
        msg = f"✅ গুগলে জমা হয়েছে: {my_redirect_url}"
    except Exception as e:
        msg = f"⚠️ API এরর: {str(e)}<br>তবুও রিডাইরেক্ট তৈরি: <a href='{my_redirect_url}'>{my_redirect_url}</a>"

    return render_template_string('''
        <h1>ইনস্টা ইনডেক্সার</h1>
        <p>{{ message|safe }}</p>
        <a href="/">আরেকটি লিংক দিন</a>
    ''', message=msg)

@app.route('/go/<code>')
def handle_redirect(code):
    key = f"go/{code}"
    target = redirect_map.get(key)
    if target:
        resp = redirect(target, code=301)
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    return "পাওয়া যায়নি", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)