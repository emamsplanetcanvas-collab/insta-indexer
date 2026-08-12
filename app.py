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
@app.route('/flights')
def flights():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
        <meta name="description" content="Independent Travel Assistance Desk - Flight Bookings, Rescheduling, Date Changes & Cancellations Support. Speak with a travel specialist now.">
        <meta name="robots" content="index, follow">
        <title>Trevomo Travel Desk | Independent Flight Booking & Support</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            :root {
                --navy-deep: #0F172A;
                --royal-blue: #1E40AF;
                --royal-blue-hover: #1a3696;
                --accent-orange: #F97316;
                --accent-orange-hover: #ea580c;
                --accent-green: #10B981;
                --accent-green-light: #d1fae5;
                --white: #FFFFFF;
                --slate-50: #F8FAFC;
                --slate-100: #F1F5F9;
                --slate-200: #E2E8F0;
                --slate-300: #CBD5E1;
                --slate-500: #64748B;
                --slate-600: #475569;
                --slate-700: #334155;
                --slate-800: #1E293B;
                --slate-900: #0F172A;
                --yellow-50: #FFFBEB;
                --yellow-200: #FDE68A;
                --yellow-700: #A16207;
                --yellow-800: #854D0E;
                --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
                --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                --topbar-height: 48px;
                --header-height: 56px;
            }

            *,
            *::before,
            *::after {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            html {
                scroll-behavior: smooth;
                -webkit-text-size-adjust: 100%;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                overflow-x: hidden;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                line-height: 1.6;
                color: var(--slate-800);
                background-color: var(--slate-50);
                min-height: 100vh;
                padding-top: var(--topbar-height);
                -webkit-tap-highlight-color: transparent;
                overflow-x: hidden;
                max-width: 100vw;
            }

            /* ==================== TOP STICKY BAR ==================== */
            .top-bar {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
                background: var(--navy-deep);
                color: var(--white);
                padding: 6px 10px;
                text-align: center;
                font-weight: 500;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                flex-wrap: nowrap;
                box-shadow: var(--shadow-md);
                height: var(--topbar-height);
                overflow: hidden;
                white-space: nowrap;
                letter-spacing: 0.01em;
            }

            .top-bar__live-dot {
                width: 8px;
                height: 8px;
                min-width: 8px;
                border-radius: 50%;
                background: var(--accent-green);
                animation: live-pulse 1.8s ease-in-out infinite;
                display: inline-block;
                flex-shrink: 0;
            }

            @keyframes live-pulse {
                0%,
                100% {
                    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
                }
                50% {
                    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
                }
            }

            .top-bar__live-text {
                font-size: 0.6rem;
                font-weight: 700;
                color: var(--accent-green);
                letter-spacing: 0.04em;
                flex-shrink: 0;
                text-transform: uppercase;
            }

            .top-bar__divider {
                width: 1px;
                height: 14px;
                background: rgba(255, 255, 255, 0.25);
                flex-shrink: 0;
                margin: 0 2px;
            }

            .top-bar__label {
                font-size: 0.6rem;
                font-weight: 400;
                color: #cbd5e1;
                flex-shrink: 1;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .top-bar__phone {
                color: var(--white);
                font-weight: 700;
                text-decoration: none;
                flex-shrink: 0;
                font-size: 0.75rem;
                letter-spacing: 0.02em;
                transition: color 150ms ease;
                padding: 4px 8px;
                border-radius: 4px;
                min-height: 44px;
                display: inline-flex;
                align-items: center;
            }
            .top-bar__phone:hover,
            .top-bar__phone:active {
                color: var(--accent-orange);
            }

            .top-bar__phone-icon {
                margin-right: 4px;
                flex-shrink: 0;
            }

            /* ==================== HEADER ==================== */
            .header {
                background: var(--white);
                border-bottom: 1px solid var(--slate-200);
                padding: 8px 12px;
                position: sticky;
                top: var(--topbar-height);
                z-index: 999;
                box-shadow: var(--shadow-sm);
                height: var(--header-height);
                display: flex;
                align-items: center;
            }

            .header__inner {
                max-width: 1200px;
                margin: 0 auto;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
            }

            .header__brand {
                display: flex;
                align-items: center;
                gap: 8px;
                text-decoration: none;
                flex-shrink: 1;
                min-width: 0;
            }

            .header__brand-icon {
                width: 34px;
                height: 34px;
                min-width: 34px;
                background: var(--royal-blue);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                box-shadow: var(--shadow-md);
            }

            .header__brand-icon svg {
                width: 18px;
                height: 18px;
                fill: white;
            }

            .header__brand-text {
                min-width: 0;
                overflow: hidden;
            }

            .header__brand-name {
                font-size: 0.9rem;
                font-weight: 800;
                color: var(--navy-deep);
                letter-spacing: -0.02em;
                line-height: 1.2;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                display: block;
            }
            .header__brand-tagline {
                font-size: 0.55rem;
                color: var(--slate-500);
                font-weight: 500;
                letter-spacing: 0.03em;
                text-transform: uppercase;
                display: block;
                white-space: nowrap;
            }

            .header__cta {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                background: var(--accent-orange);
                color: var(--white);
                font-weight: 700;
                font-size: 0.7rem;
                padding: 10px 14px;
                border-radius: 50px;
                text-decoration: none;
                white-space: nowrap;
                transition: all 150ms ease;
                box-shadow: 0 2px 8px rgba(249, 115, 22, 0.35);
                letter-spacing: 0.01em;
                flex-shrink: 0;
                min-height: 44px;
                min-width: 44px;
                justify-content: center;
            }
            .header__cta:active {
                background: var(--accent-orange-hover);
                transform: scale(0.95);
                box-shadow: 0 1px 4px rgba(249, 115, 22, 0.3);
            }

            .header__cta-icon {
                width: 14px;
                height: 14px;
                flex-shrink: 0;
            }

            /* ==================== HERO SECTION ==================== */
            .hero {
                background: linear-gradient(170deg, #f8fafc 0%, #eef2ff 30%, #e0e7ff 60%, #f1f5f9 100%);
                padding: 24px 12px 32px;
                position: relative;
                overflow: hidden;
            }

            .hero__bg-pattern {
                position: absolute;
                inset: 0;
                pointer-events: none;
                opacity: 0.03;
                background-image: radial-gradient(circle at 30% 60%, #1E40AF 1px, transparent 1px),
                    radial-gradient(circle at 70% 40%, #1E40AF 1px, transparent 1px),
                    radial-gradient(circle at 50% 80%, #0F172A 1.5px, transparent 1.5px);
                background-size: 35px 35px, 50px 50px, 45px 45px;
            }

            .hero__inner {
                max-width: 700px;
                margin: 0 auto;
                text-align: center;
                position: relative;
                z-index: 1;
            }

            .hero__independent-badge {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                background: var(--white);
                border: 1.5px solid var(--slate-200);
                padding: 5px 10px;
                border-radius: 50px;
                font-size: 0.6rem;
                font-weight: 600;
                color: var(--slate-600);
                letter-spacing: 0.03em;
                text-transform: uppercase;
                margin-bottom: 16px;
                box-shadow: var(--shadow-sm);
                flex-wrap: wrap;
                justify-content: center;
            }

            .hero__independent-badge-icon {
                width: 12px;
                height: 12px;
                color: var(--royal-blue);
                flex-shrink: 0;
            }

            .hero__headline {
                font-size: clamp(1.4rem, 4vw, 2.8rem);
                font-weight: 900;
                color: var(--navy-deep);
                line-height: 1.15;
                letter-spacing: -0.03em;
                margin-bottom: 8px;
                padding: 0 4px;
            }

            .hero__subheadline {
                font-size: clamp(0.8rem, 2vw, 1.1rem);
                color: var(--slate-600);
                font-weight: 400;
                margin-bottom: 20px;
                line-height: 1.5;
                max-width: 500px;
                margin-left: auto;
                margin-right: auto;
                padding: 0 4px;
            }

            /* Hero Call Box */
            .hero__call-box {
                background: var(--white);
                border: 2px solid var(--slate-200);
                border-radius: 16px;
                padding: 18px 14px 22px;
                box-shadow: var(--shadow-xl);
                transition: all 250ms ease;
                position: relative;
                max-width: 420px;
                margin: 0 auto;
            }

            .hero__call-icon-wrapper {
                position: relative;
                display: inline-block;
                margin-bottom: 10px;
            }

            .hero__call-icon-circle {
                width: 52px;
                height: 52px;
                background: var(--accent-green);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.2), 0 0 0 14px rgba(16, 185, 129, 0.08);
                animation: phone-pulse-ring 2.2s ease-in-out infinite;
                position: relative;
                z-index: 1;
            }

            @keyframes phone-pulse-ring {
                0%,
                100% {
                    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.35), 0 0 0 10px rgba(16, 185, 129, 0.12);
                    transform: scale(1);
                }
                30% {
                    box-shadow: 0 0 0 12px rgba(16, 185, 129, 0), 0 0 0 24px rgba(16, 185, 129, 0);
                    transform: scale(1.05);
                }
                50% {
                    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0), 0 0 0 0 rgba(16, 185, 129, 0);
                    transform: scale(1);
                }
                70% {
                    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.18), 0 0 0 16px rgba(16, 185, 129, 0.05);
                    transform: scale(1.02);
                }
            }

            .hero__call-icon-circle svg {
                width: 24px;
                height: 24px;
                fill: white;
            }

            .hero__call-number {
                display: block;
                font-size: clamp(1.5rem, 5vw, 2.6rem);
                font-weight: 900;
                color: var(--navy-deep);
                text-decoration: none;
                letter-spacing: -0.02em;
                line-height: 1.1;
                margin-bottom: 4px;
                transition: color 150ms ease;
                word-break: break-all;
                overflow-wrap: anywhere;
                padding: 6px 4px;
                min-height: 44px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .hero__call-number:active {
                color: var(--royal-blue);
            }

            .hero__call-cta-text {
                display: block;
                font-size: 0.7rem;
                font-weight: 600;
                color: var(--accent-orange);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            }

            .hero__wait-time {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                background: var(--accent-green-light);
                color: #065f46;
                font-weight: 600;
                font-size: 0.7rem;
                padding: 5px 12px;
                border-radius: 50px;
                letter-spacing: 0.02em;
                flex-wrap: wrap;
                justify-content: center;
            }

            .hero__wait-time-dot {
                width: 7px;
                height: 7px;
                min-width: 7px;
                border-radius: 50%;
                background: var(--accent-green);
                animation: live-pulse 1.8s ease-in-out infinite;
            }

            .hero__independent-note {
                font-size: 0.6rem;
                color: var(--slate-500);
                margin-top: 10px;
                font-weight: 400;
                letter-spacing: 0.02em;
                line-height: 1.4;
                padding: 0 2px;
            }

            /* ==================== SERVICES GRID ==================== */
            .services {
                max-width: 1100px;
                margin: 0 auto;
                padding: 28px 10px;
                overflow: hidden;
            }

            .services__heading {
                text-align: center;
                font-size: clamp(1.1rem, 3vw, 1.6rem);
                font-weight: 800;
                color: var(--navy-deep);
                margin-bottom: 4px;
                letter-spacing: -0.02em;
                padding: 0 8px;
            }
            .services__subheading {
                text-align: center;
                font-size: 0.7rem;
                color: var(--slate-500);
                margin-bottom: 22px;
                font-weight: 400;
                padding: 0 8px;
            }

            .services__grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }

            @media (min-width: 480px) {
                .services__grid {
                    gap: 10px;
                }
            }

            @media (min-width: 768px) {
                .services__grid {
                    grid-template-columns: repeat(4, 1fr);
                    gap: 14px;
                }
            }

            .service-card {
                background: var(--white);
                border: 1.5px solid var(--slate-200);
                border-radius: 12px;
                padding: 14px 8px;
                text-align: center;
                transition: all 200ms ease;
                cursor: default;
                box-shadow: var(--shadow-sm);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 6px;
                min-height: 0;
            }
            .service-card:active {
                border-color: var(--royal-blue);
                box-shadow: var(--shadow-lg);
                transform: scale(0.97);
            }

            .service-card__icon {
                width: 38px;
                height: 38px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
            .service-card__icon--blue {
                background: #eff6ff;
                color: #2563eb;
            }
            .service-card__icon--amber {
                background: #fffbeb;
                color: #d97706;
            }
            .service-card__icon--red {
                background: #fef2f2;
                color: #dc2626;
            }
            .service-card__icon--purple {
                background: #faf5ff;
                color: #7c3aed;
            }

            .service-card__icon svg {
                width: 20px;
                height: 20px;
            }

            .service-card__title {
                font-size: 0.7rem;
                font-weight: 700;
                color: var(--slate-800);
                letter-spacing: -0.01em;
                line-height: 1.3;
            }
            .service-card__desc {
                font-size: 0.6rem;
                color: var(--slate-500);
                font-weight: 400;
                line-height: 1.4;
                display: none;
            }

            @media (min-width: 480px) {
                .service-card__desc {
                    display: block;
                }
                .service-card {
                    padding: 16px 10px;
                    gap: 8px;
                }
                .service-card__icon {
                    width: 44px;
                    height: 44px;
                }
                .service-card__icon svg {
                    width: 22px;
                    height: 22px;
                }
                .service-card__title {
                    font-size: 0.78rem;
                }
            }

            /* ==================== CARRIERS SECTION ==================== */
            .carriers {
                max-width: 1100px;
                margin: 0 auto;
                padding: 0 10px 28px;
                text-align: center;
                overflow: hidden;
            }

            .carriers__heading {
                font-size: clamp(1rem, 2.5vw, 1.2rem);
                font-weight: 700;
                color: var(--navy-deep);
                margin-bottom: 4px;
                letter-spacing: -0.01em;
                padding: 0 8px;
            }
            .carriers__note {
                font-size: 0.65rem;
                color: var(--slate-500);
                margin-bottom: 14px;
                font-weight: 400;
                padding: 0 8px;
            }

            .carriers__badges {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 6px;
            }

            .carrier-badge {
                display: inline-block;
                background: var(--white);
                border: 1.5px solid var(--slate-200);
                padding: 7px 11px;
                border-radius: 50px;
                font-size: 0.65rem;
                font-weight: 600;
                color: var(--slate-700);
                letter-spacing: 0.01em;
                transition: all 150ms ease;
                white-space: nowrap;
                box-shadow: var(--shadow-sm);
                min-height: 36px;
                display: inline-flex;
                align-items: center;
            }
            .carrier-badge:active {
                border-color: var(--royal-blue);
                color: var(--royal-blue);
                box-shadow: var(--shadow-md);
            }

            /* ==================== WHY CALL US ==================== */
            .why-call {
                background: var(--navy-deep);
                padding: 36px 12px;
                color: var(--white);
                text-align: center;
            }

            .why-call__inner {
                max-width: 1000px;
                margin: 0 auto;
            }

            .why-call__heading {
                font-size: clamp(1.1rem, 3vw, 1.6rem);
                font-weight: 800;
                margin-bottom: 4px;
                letter-spacing: -0.02em;
                padding: 0 4px;
            }
            .why-call__subheading {
                font-size: 0.7rem;
                color: #94a3b8;
                margin-bottom: 24px;
                font-weight: 400;
                padding: 0 4px;
            }

            .why-call__grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 14px;
            }

            @media (min-width: 480px) {
                .why-call__grid {
                    grid-template-columns: repeat(3, 1fr);
                    gap: 16px;
                }
            }

            .why-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 18px 14px;
                text-align: center;
                transition: all 200ms ease;
            }
            .why-card:active {
                background: rgba(255, 255, 255, 0.09);
                border-color: rgba(255, 255, 255, 0.25);
                transform: scale(0.97);
            }

            .why-card__icon {
                width: 40px;
                height: 40px;
                margin: 0 auto 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .why-card__icon svg {
                width: 20px;
                height: 20px;
                fill: var(--accent-orange);
            }
            .why-card__title {
                font-size: 0.85rem;
                font-weight: 700;
                margin-bottom: 4px;
                letter-spacing: -0.01em;
            }
            .why-card__desc {
                font-size: 0.7rem;
                color: #cbd5e1;
                font-weight: 400;
                line-height: 1.5;
            }

            /* ==================== FTC DISCLAIMER BOX ==================== */
            .ftc-disclaimer {
                max-width: 1100px;
                margin: 22px auto;
                padding: 0 10px;
            }

            .ftc-disclaimer__box {
                background: var(--yellow-50);
                border: 2px solid var(--yellow-200);
                border-radius: 12px;
                padding: 16px 12px;
                box-shadow: var(--shadow-md);
            }

            .ftc-disclaimer__heading {
                font-size: 0.7rem;
                font-weight: 700;
                color: var(--yellow-800);
                margin-bottom: 6px;
                letter-spacing: 0.02em;
                text-transform: uppercase;
                display: flex;
                align-items: center;
                gap: 6px;
                flex-wrap: wrap;
            }

            .ftc-disclaimer__heading-icon {
                width: 16px;
                height: 16px;
                min-width: 16px;
                color: var(--yellow-700);
            }

            .ftc-disclaimer__text {
                font-size: 0.65rem;
                color: #78350f;
                line-height: 1.6;
                font-weight: 400;
                margin: 0;
            }
            .ftc-disclaimer__text strong {
                color: #5c2d0a;
            }

            /* ==================== FOOTER ==================== */
            .footer {
                background: var(--navy-deep);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding: 22px 12px 18px;
                color: #94a3b8;
                text-align: center;
            }

            .footer__inner {
                max-width: 1100px;
                margin: 0 auto;
            }

            .footer__brand {
                font-size: 0.9rem;
                font-weight: 700;
                color: var(--white);
                margin-bottom: 2px;
                letter-spacing: -0.01em;
            }
            .footer__tagline {
                font-size: 0.6rem;
                color: #64748b;
                margin-bottom: 14px;
                letter-spacing: 0.02em;
            }

            .footer__links {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 8px 12px;
                margin-bottom: 12px;
            }

            .footer__link {
                color: #94a3b8;
                text-decoration: underline;
                font-size: 0.7rem;
                font-weight: 500;
                cursor: pointer;
                transition: color 150ms ease;
                background: none;
                border: none;
                font-family: inherit;
                letter-spacing: 0.01em;
                padding: 8px 6px;
                min-height: 44px;
                min-width: 44px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
            }
            .footer__link:active {
                color: var(--white);
            }

            .footer__copyright {
                font-size: 0.6rem;
                color: #64748b;
                line-height: 1.5;
                padding: 0 4px;
            }

            /* ==================== MODALS ==================== */
            .modal-overlay {
                display: none;
                position: fixed;
                inset: 0;
                z-index: 2000;
                background: rgba(15, 23, 42, 0.8);
                align-items: center;
                justify-content: center;
                padding: 12px;
                backdrop-filter: blur(2px);
                -webkit-backdrop-filter: blur(2px);
            }
            .modal-overlay.active {
                display: flex;
            }

            .modal {
                background: var(--white);
                border-radius: 14px;
                padding: 22px 16px;
                max-width: 580px;
                width: 100%;
                max-height: 82vh;
                overflow-y: auto;
                box-shadow: var(--shadow-2xl);
                position: relative;
                -webkit-overflow-scrolling: touch;
            }

            .modal__close {
                position: sticky;
                top: 0;
                float: right;
                width: 40px;
                height: 40px;
                min-width: 40px;
                border-radius: 50%;
                border: 1.5px solid var(--slate-200);
                background: var(--white);
                cursor: pointer;
                font-size: 1.3rem;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--slate-600);
                transition: all 150ms ease;
                z-index: 5;
                line-height: 1;
                margin-left: 8px;
                margin-bottom: 8px;
            }
            .modal__close:active {
                background: var(--slate-100);
                border-color: var(--slate-300);
                color: var(--slate-900);
            }

            .modal__title {
                font-size: clamp(1rem, 3vw, 1.3rem);
                font-weight: 800;
                color: var(--navy-deep);
                margin-bottom: 12px;
                letter-spacing: -0.02em;
                padding-right: 8px;
            }

            .modal__body {
                font-size: 0.75rem;
                color: var(--slate-700);
                line-height: 1.7;
                clear: both;
            }
            .modal__body p {
                margin-bottom: 8px;
            }
            .modal__body h4 {
                font-size: 0.85rem;
                font-weight: 700;
                color: var(--navy-deep);
                margin: 14px 0 4px;
            }

            /* ==================== LARGER SCREENS ==================== */
            @media (min-width: 480px) {
                :root {
                    --topbar-height: 44px;
                    --header-height: 52px;
                }
                .top-bar {
                    padding: 6px 14px;
                    gap: 8px;
                }
                .top-bar__live-text {
                    font-size: 0.68rem;
                }
                .top-bar__label {
                    font-size: 0.7rem;
                }
                .top-bar__phone {
                    font-size: 0.82rem;
                }
                .top-bar__divider {
                    margin: 0 4px;
                }
                .header {
                    padding: 8px 16px;
                }
                .header__brand-name {
                    font-size: 1rem;
                }
                .header__brand-tagline {
                    font-size: 0.6rem;
                }
                .header__cta {
                    font-size: 0.78rem;
                    padding: 10px 16px;
                }
                .header__brand-icon {
                    width: 38px;
                    height: 38px;
                    min-width: 38px;
                }
                .header__brand-icon svg {
                    width: 20px;
                    height: 20px;
                }
                .hero {
                    padding: 32px 16px 40px;
                }
                .hero__call-box {
                    padding: 22px 18px 26px;
                    border-radius: 18px;
                }
                .hero__call-icon-circle {
                    width: 60px;
                    height: 60px;
                }
                .hero__call-icon-circle svg {
                    width: 28px;
                    height: 28px;
                }
                .hero__call-cta-text {
                    font-size: 0.75rem;
                }
                .hero__wait-time {
                    font-size: 0.75rem;
                    padding: 6px 14px;
                }
                .hero__independent-note {
                    font-size: 0.65rem;
                }
                .services {
                    padding: 36px 16px;
                }
                .services__heading {
                    font-size: clamp(1.2rem, 3vw, 1.7rem);
                }
                .services__subheading {
                    font-size: 0.78rem;
                    margin-bottom: 26px;
                }
                .carriers {
                    padding: 0 16px 36px;
                }
                .carrier-badge {
                    font-size: 0.7rem;
                    padding: 8px 13px;
                }
                .why-call {
                    padding: 44px 16px;
                }
                .ftc-disclaimer {
                    padding: 0 16px;
                    margin: 28px auto;
                }
                .ftc-disclaimer__box {
                    padding: 18px 16px;
                }
                .ftc-disclaimer__heading {
                    font-size: 0.75rem;
                }
                .ftc-disclaimer__text {
                    font-size: 0.7rem;
                }
                .footer {
                    padding: 28px 16px 20px;
                }
                .footer__brand {
                    font-size: 1rem;
                }
                .footer__tagline {
                    font-size: 0.65rem;
                }
                .footer__link {
                    font-size: 0.75rem;
                }
                .footer__copyright {
                    font-size: 0.65rem;
                }
                .modal {
                    padding: 26px 20px;
                    border-radius: 18px;
                }
                .modal__body {
                    font-size: 0.8rem;
                }
            }

            @media (min-width: 768px) {
                :root {
                    --topbar-height: 42px;
                    --header-height: 56px;
                }
                body {
                    padding-top: var(--topbar-height);
                }
                .top-bar {
                    padding: 7px 18px;
                    gap: 10px;
                    justify-content: center;
                }
                .top-bar__live-text {
                    font-size: 0.72rem;
                }
                .top-bar__label {
                    font-size: 0.75rem;
                }
                .top-bar__phone {
                    font-size: 0.88rem;
                }
                .header {
                    padding: 10px 20px;
                }
                .header__brand-name {
                    font-size: 1.1rem;
                }
                .header__cta {
                    font-size: 0.85rem;
                    padding: 11px 20px;
                }
                .hero {
                    padding: 44px 20px 52px;
                }
                .hero__headline {
                    font-size: clamp(1.8rem, 4.5vw, 3rem);
                }
                .hero__subheadline {
                    font-size: clamp(0.9rem, 2vw, 1.15rem);
                }
                .hero__call-box {
                    padding: 28px 24px 32px;
                    border-radius: 20px;
                }
                .hero__call-icon-circle {
                    width: 68px;
                    height: 68px;
                }
                .hero__call-icon-circle svg {
                    width: 32px;
                    height: 32px;
                }
                .hero__call-number {
                    font-size: clamp(1.8rem, 5vw, 3rem);
                }
                .services {
                    padding: 48px 20px;
                }
                .services__grid {
                    grid-template-columns: repeat(4, 1fr);
                    gap: 14px;
                }
                .service-card {
                    padding: 20px 12px;
                    gap: 10px;
                }
                .service-card__icon {
                    width: 48px;
                    height: 48px;
                }
                .service-card__icon svg {
                    width: 24px;
                    height: 24px;
                }
                .service-card__title {
                    font-size: 0.82rem;
                }
                .service-card__desc {
                    font-size: 0.68rem;
                    display: block;
                }
                .carriers {
                    padding: 0 20px 44px;
                }
                .carrier-badge {
                    font-size: 0.75rem;
                    padding: 9px 15px;
                }
                .why-call {
                    padding: 52px 20px;
                }
                .why-call__grid {
                    gap: 20px;
                }
                .why-card {
                    padding: 22px 16px;
                }
                .why-card__icon {
                    width: 44px;
                    height: 44px;
                }
                .why-card__icon svg {
                    width: 22px;
                    height: 22px;
                }
                .ftc-disclaimer {
                    padding: 0 20px;
                    margin: 32px auto;
                }
                .ftc-disclaimer__box {
                    padding: 20px 18px;
                }
                .footer {
                    padding: 32px 20px 22px;
                }
                .hero__independent-badge {
                    font-size: 0.68rem;
                    padding: 6px 12px;
                }
            }

            @media (min-width: 1024px) {
                .hero__inner {
                    max-width: 750px;
                }
                .hero__call-box {
                    max-width: 480px;
                    padding: 32px 28px 36px;
                }
                .services__grid {
                    gap: 18px;
                }
                .service-card {
                    padding: 24px 16px;
                    border-radius: 14px;
                }
                .service-card:hover {
                    border-color: var(--royal-blue);
                    box-shadow: var(--shadow-lg);
                    transform: translateY(-3px);
                }
                .carrier-badge:hover {
                    border-color: var(--royal-blue);
                    color: var(--royal-blue);
                    box-shadow: var(--shadow-md);
                    transform: translateY(-1px);
                }
                .why-card:hover {
                    background: rgba(255, 255, 255, 0.09);
                    border-color: rgba(255, 255, 255, 0.25);
                    transform: translateY(-2px);
                }
                .header__cta:hover {
                    background: var(--accent-orange-hover);
                    box-shadow: 0 4px 16px rgba(249, 115, 22, 0.5);
                    transform: translateY(-1px);
                }
                .footer__link:hover {
                    color: var(--white);
                }
                .modal__close:hover {
                    background: var(--slate-100);
                    border-color: var(--slate-300);
                    color: var(--slate-900);
                }
                .hero__call-number:hover {
                    color: var(--royal-blue);
                }
                .top-bar__phone:hover {
                    color: var(--accent-orange);
                }
            }

            /* ==================== VERY SMALL SCREENS (320px) ==================== */
            @media (max-width: 359px) {
                :root {
                    --topbar-height: 50px;
                    --header-height: 50px;
                }
                .top-bar {
                    padding: 4px 6px;
                    gap: 3px;
                }
                .top-bar__live-text {
                    font-size: 0.5rem;
                }
                .top-bar__live-dot {
                    width: 6px;
                    height: 6px;
                    min-width: 6px;
                }
                .top-bar__divider {
                    height: 10px;
                    margin: 0 1px;
                }
                .top-bar__label {
                    font-size: 0.5rem;
                }
                .top-bar__phone {
                    font-size: 0.65rem;
                    padding: 4px 4px;
                }
                .top-bar__phone-icon {
                    margin-right: 2px;
                }
                .header {
                    padding: 4px 8px;
                }
                .header__brand-icon {
                    width: 28px;
                    height: 28px;
                    min-width: 28px;
                    border-radius: 6px;
                }
                .header__brand-icon svg {
                    width: 15px;
                    height: 15px;
                }
                .header__brand-name {
                    font-size: 0.72rem;
                }
                .header__brand-tagline {
                    font-size: 0.48rem;
                }
                .header__cta {
                    font-size: 0.6rem;
                    padding: 8px 10px;
                    gap: 3px;
                    min-height: 38px;
                    min-width: 38px;
                }
                .header__cta-icon {
                    width: 11px;
                    height: 11px;
                }
                .hero {
                    padding: 16px 8px 22px;
                }
                .hero__headline {
                    font-size: 1.15rem;
                }
                .hero__subheadline {
                    font-size: 0.68rem;
                    margin-bottom: 14px;
                }
                .hero__call-box {
                    padding: 14px 10px 16px;
                    border-radius: 12px;
                    border-width: 1.5px;
                }
                .hero__call-icon-circle {
                    width: 42px;
                    height: 42px;
                }
                .hero__call-icon-circle svg {
                    width: 20px;
                    height: 20px;
                }
                .hero__call-number {
                    font-size: 1.2rem;
                }
                .hero__call-cta-text {
                    font-size: 0.6rem;
                }
                .hero__wait-time {
                    font-size: 0.6rem;
                    padding: 4px 8px;
                    gap: 3px;
                }
                .hero__independent-badge {
                    font-size: 0.5rem;
                    padding: 4px 7px;
                    gap: 3px;
                }
                .services__grid {
                    grid-template-columns: 1fr 1fr;
                    gap: 5px;
                }
                .service-card {
                    padding: 10px 5px;
                    border-radius: 8px;
                    gap: 3px;
                }
                .service-card__icon {
                    width: 30px;
                    height: 30px;
                    border-radius: 6px;
                }
                .service-card__icon svg {
                    width: 16px;
                    height: 16px;
                }
                .service-card__title {
                    font-size: 0.6rem;
                }
                .service-card__desc {
                    font-size: 0.5rem;
                    display: none;
                }
                .carriers__badges {
                    gap: 4px;
                }
                .carrier-badge {
                    font-size: 0.55rem;
                    padding: 5px 8px;
                    min-height: 30px;
                }
                .why-call {
                    padding: 24px 8px;
                }
                .why-call__grid {
                    gap: 8px;
                }
                .why-card {
                    padding: 12px 10px;
                    border-radius: 10px;
                }
                .why-card__icon {
                    width: 32px;
                    height: 32px;
                }
                .why-card__icon svg {
                    width: 16px;
                    height: 16px;
                }
                .why-card__title {
                    font-size: 0.7rem;
                }
                .why-card__desc {
                    font-size: 0.6rem;
                }
                .ftc-disclaimer__box {
                    padding: 12px 8px;
                }
                .ftc-disclaimer__heading {
                    font-size: 0.6rem;
                }
                .ftc-disclaimer__text {
                    font-size: 0.55rem;
                }
                .footer {
                    padding: 16px 8px 12px;
                }
                .footer__link {
                    font-size: 0.6rem;
                    padding: 6px 4px;
                    min-height: 36px;
                    min-width: 36px;
                }
                .footer__copyright {
                    font-size: 0.5rem;
                }
            }

            /* ==================== ACCESSIBILITY & FOCUS ==================== */
            a:focus-visible,
            button:focus-visible {
                outline: 2.5px solid var(--royal-blue);
                outline-offset: 3px;
                border-radius: 4px;
            }

            @media (prefers-reduced-motion: reduce) {
                *,
                *::before,
                *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }

            .skip-link {
                position: absolute;
                top: -100px;
                left: 10px;
                background: var(--royal-blue);
                color: white;
                padding: 8px 14px;
                border-radius: 0 0 6px 6px;
                z-index: 3000;
                font-weight: 600;
                text-decoration: none;
                transition: top 150ms ease;
                font-size: 0.7rem;
            }
            .skip-link:focus {
                top: 0;
            }
        </style>
    </head>
    <body>

        <a href="#main-content" class="skip-link">Skip to Main Content</a>

        <!-- ==================== TOP STICKY BAR ==================== -->
        <div class="top-bar" role="banner" aria-label="Independent Travel Desk - 24/7 Support">
            <span class="top-bar__live-dot" aria-hidden="true"></span>
            <span class="top-bar__live-text">LIVE</span>
            <span class="top-bar__divider" aria-hidden="true"></span>
            <span class="top-bar__label">Independent Travel Desk</span>
            <span class="top-bar__divider" aria-hidden="true"></span>
            <a href="tel:+18332420904" class="top-bar__phone" aria-label="Call Travel Desk at 1 8 3 3 2 4 2 0 9 0 4">
                <span class="top-bar__phone-icon">📞</span> +1 (833) 242-0904
            </a>
        </div>

        <!-- ==================== HEADER ==================== -->
        <header class="header" role="banner">
            <div class="header__inner">
                <a href="/" class="header__brand" aria-label="Trevomo Travel Desk - Home">
                    <div class="header__brand-icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                        </svg>
                    </div>
                    <span class="header__brand-text">
                        <span class="header__brand-name">Trevomo Travel Desk</span>
                        <span class="header__brand-tagline">Independent Travel Assistance</span>
                    </span>
                </a>
                <a href="tel:+18332420904" class="header__cta" aria-label="Call Flight Specialist Now">
                    <svg class="header__cta-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                        <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                    </svg>
                    Call Specialist
                </a>
            </div>
        </header>

        <!-- ==================== MAIN CONTENT ==================== -->
        <main id="main-content">

            <!-- HERO SECTION -->
            <section class="hero" aria-labelledby="hero-headline">
                <div class="hero__bg-pattern" aria-hidden="true"></div>
                <div class="hero__inner">
                    <div class="hero__independent-badge">
                        <svg class="hero__independent-badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M9 12l2 2 4-4"/>
                        </svg>
                        Independent Travel Assistance Desk
                    </div>
                    <h1 id="hero-headline" class="hero__headline">
                        Fast Flight Bookings, Rescheduling &amp; Cancellations
                    </h1>
                    <p class="hero__subheadline">
                        Speak directly with an expert travel agent for instant flight assistance. <strong>Trevomo Travel Desk</strong> is an independent service — not affiliated with any single airline.
                    </p>

                    <div class="hero__call-box">
                        <div class="hero__call-icon-wrapper">
                            <div class="hero__call-icon-circle" aria-hidden="true">
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                                </svg>
                            </div>
                        </div>
                        <a href="tel:+18332420904" class="hero__call-number" aria-label="Call Trevomo Travel Desk at 1 8 3 3 2 4 2 0 9 0 4">
                            +1 (833) 242-0904
                        </a>
                        <span class="hero__call-cta-text">Tap to Call Now — Instant Connection</span>
                        <span class="hero__wait-time">
                            <span class="hero__wait-time-dot" aria-hidden="true"></span>
                            Average Wait Time: Under 30 Seconds
                        </span>
                        <p class="hero__independent-note">
                            ⓘ Trevomo Travel Desk is an <strong>independent travel assistance desk</strong>. We are not directly affiliated with or endorsed by any airline.
                        </p>
                    </div>
                </div>
            </section>

            <!-- SERVICES GRID -->
            <section class="services" aria-labelledby="services-heading">
                <h2 id="services-heading" class="services__heading">How Our Travel Specialists Help You</h2>
                <p class="services__subheading">Expert assistance for all your flight needs — one call away.</p>
                <div class="services__grid">
                    <div class="service-card">
                        <div class="service-card__icon service-card__icon--blue" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                            </svg>
                        </div>
                        <h3 class="service-card__title">✈️ New Flight Reservations</h3>
                        <p class="service-card__desc">Book new flights across all major US carriers with expert guidance.</p>
                    </div>
                    <div class="service-card">
                        <div class="service-card__icon service-card__icon--amber" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M9 16l2 2 4-4"/>
                            </svg>
                        </div>
                        <h3 class="service-card__title">🔄 Flight Rescheduling &amp; Date Changes</h3>
                        <p class="service-card__desc">Need to change your travel dates? We handle rescheduling quickly.</p>
                    </div>
                    <div class="service-card">
                        <div class="service-card__icon service-card__icon--red" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                            </svg>
                        </div>
                        <h3 class="service-card__title">❌ Flight Cancellations &amp; Refund Guidance</h3>
                        <p class="service-card__desc">Cancel your booking and understand refund options with our specialists.</p>
                    </div>
                    <div class="service-card">
                        <div class="service-card__icon service-card__icon--purple" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="2" y="6" width="20" height="14" rx="2"/><path d="M12 12v4"/><circle cx="12" cy="9" r="1"/>
                            </svg>
                        </div>
                        <h3 class="service-card__title">🧳 Seat Upgrades &amp; Baggage Assistance</h3>
                        <p class="service-card__desc">Get help with seat selection, upgrades, and baggage-related inquiries.</p>
                    </div>
                </div>
            </section>

            <!-- SUPPORTED CARRIERS -->
            <section class="carriers" aria-labelledby="carriers-heading">
                <h2 id="carriers-heading" class="carriers__heading">We Assist With All Major US Carriers</h2>
                <p class="carriers__note">Our independent travel desk supports bookings across these and other airlines. No official affiliation implied.</p>
                <div class="carriers__badges">
                    <span class="carrier-badge">Delta Air Lines</span>
                    <span class="carrier-badge">United Airlines</span>
                    <span class="carrier-badge">American Airlines</span>
                    <span class="carrier-badge">Southwest Airlines</span>
                    <span class="carrier-badge">Alaska Airlines</span>
                    <span class="carrier-badge">JetBlue Airways</span>
                    <span class="carrier-badge">Spirit Airlines</span>
                    <span class="carrier-badge">Frontier Airlines</span>
                    <span class="carrier-badge">Hawaiian Airlines</span>
                </div>
            </section>

            <!-- WHY CALL US -->
            <section class="why-call" aria-labelledby="why-call-heading">
                <div class="why-call__inner">
                    <h2 id="why-call-heading" class="why-call__heading">Why Call Trevomo Travel Desk?</h2>
                    <p class="why-call__subheading">We make flight assistance simple, fast, and hassle-free.</p>
                    <div class="why-call__grid">
                        <div class="why-card">
                            <div class="why-card__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                                </svg>
                            </div>
                            <h3 class="why-card__title">Instant Support</h3>
                            <p class="why-card__desc">Connect with a live travel specialist in under 30 seconds. No bots, no endless menus.</p>
                        </div>
                        <div class="why-card">
                            <div class="why-card__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                                </svg>
                            </div>
                            <h3 class="why-card__title">No Long Hold Times</h3>
                            <p class="why-card__desc">We prioritize quick connections. Most callers speak with a specialist within seconds.</p>
                        </div>
                        <div class="why-card">
                            <div class="why-card__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                                </svg>
                            </div>
                            <h3 class="why-card__title">Expert Booking Assistance</h3>
                            <p class="why-card__desc">Our knowledgeable travel specialists help you find the best routes, rates, and options available.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- FTC COMPLIANCE DISCLAIMER BOX -->
            <section class="ftc-disclaimer" aria-labelledby="ftc-heading">
                <div class="ftc-disclaimer__box">
                    <h2 id="ftc-heading" class="ftc-disclaimer__heading">
                        <svg class="ftc-disclaimer__heading-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                        </svg>
                        FTC Compliance &amp; Transparency Disclaimer
                    </h2>
                    <p class="ftc-disclaimer__text">
                        <strong>Trevomo Travel Desk is an independent travel assistance desk</strong> and is <strong>not directly affiliated with, endorsed by, sponsored by, or representing any specific airline</strong>, including but not limited to Delta Air Lines, United Airlines, American Airlines, Southwest Airlines, Alaska Airlines, JetBlue Airways, Spirit Airlines, Frontier Airlines, or Hawaiian Airlines. We provide third-party travel booking assistance, rescheduling support, cancellation guidance, and related travel information services. All airline names, trademarks, service marks, and logos referenced on this site are the exclusive property of their respective owners and are used here for descriptive purposes only. This website is operated by an independent third-party travel assistance provider. Calls placed to the number listed on this site may be routed to qualified travel specialists who can assist with bookings across multiple carriers. <strong>By placing a call, you acknowledge and agree to our Terms of Service and Privacy Policy.</strong> This site complies with all applicable US Federal Trade Commission (FTC) regulations regarding transparent advertising and consumer disclosures.
                    </p>
                </div>
            </section>

        </main>

        <!-- ==================== FOOTER ==================== -->
        <footer class="footer" role="contentinfo">
            <div class="footer__inner">
                <p class="footer__brand">Trevomo Travel Desk</p>
                <p class="footer__tagline">Independent Travel Assistance Desk — Not affiliated with any airline.</p>
                <div class="footer__links">
                    <button class="footer__link" onclick="openModal('privacy-modal')" aria-label="View Privacy Policy">Privacy Policy</button>
                    <button class="footer__link" onclick="openModal('terms-modal')" aria-label="View Terms of Service">Terms of Service</button>
                    <button class="footer__link" onclick="openModal('disclaimer-modal')" aria-label="View Full Disclaimer">Disclaimer</button>
                    <button class="footer__link" onclick="openModal('contact-modal')" aria-label="Contact Us">Contact Us</button>
                </div>
                <p class="footer__copyright">
                    &copy; <span id="copyright-year">2026</span> Trevomo Travel Desk. All rights reserved.<br>
                    Marketcall Offer ID: 6711 — Flight Booking Bundle.<br>
                    Trevomo Travel Desk is an <strong>independent travel assistance desk</strong>. Not an airline representative.
                </p>
            </div>
        </footer>

        <!-- ==================== MODALS ==================== -->
        <div class="modal-overlay" id="privacy-modal" role="dialog" aria-modal="true" aria-labelledby="privacy-modal-title">
            <div class="modal">
                <button class="modal__close" onclick="closeModal('privacy-modal')" aria-label="Close Privacy Policy modal">&times;</button>
                <h3 class="modal__title" id="privacy-modal-title">Privacy Policy</h3>
                <div class="modal__body">
                    <p><strong>Effective Date:</strong> January 1, 2026</p>
                    <p>Trevomo Travel Desk ("we," "us," or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your personal information when you interact with our independent travel assistance services.</p>
                    <h4>Information We Collect</h4>
                    <p>When you call our travel desk, we may collect information such as your name, phone number, travel preferences, and booking details to assist you effectively. We do not sell your personal information to third parties.</p>
                    <h4>How We Use Your Information</h4>
                    <p>Your information is used solely to provide travel assistance, process bookings, communicate with you about your travel needs, and improve our services. Calls may be recorded for quality assurance purposes with your consent where required by law.</p>
                    <h4>Third-Party Sharing</h4>
                    <p>We may share your information with trusted travel service partners solely to fulfill your booking requests. We do not share data for unrelated marketing purposes.</p>
                    <h4>Contact</h4>
                    <p>For privacy-related inquiries, please contact us through the information provided on our Contact Us page.</p>
                </div>
            </div>
        </div>

        <div class="modal-overlay" id="terms-modal" role="dialog" aria-modal="true" aria-labelledby="terms-modal-title">
            <div class="modal">
                <button class="modal__close" onclick="closeModal('terms-modal')" aria-label="Close Terms of Service modal">&times;</button>
                <h3 class="modal__title" id="terms-modal-title">Terms of Service</h3>
                <div class="modal__body">
                    <p><strong>Effective Date:</strong> January 1, 2026</p>
                    <p>By using the services provided by Trevomo Travel Desk, you agree to the following terms and conditions. Please read them carefully.</p>
                    <h4>Service Description</h4>
                    <p>Trevomo Travel Desk operates as an <strong>independent travel assistance desk</strong>. We are not an airline, nor are we directly affiliated with or endorsed by any specific airline. Our services include flight booking assistance, rescheduling support, cancellation guidance, and related travel information.</p>
                    <h4>User Responsibilities</h4>
                    <p>You agree to provide accurate information when requesting our services. You acknowledge that final booking terms, fares, and policies are determined by the respective airlines and travel providers.</p>
                    <h4>Limitation of Liability</h4>
                    <p>Trevomo Travel Desk strives to provide accurate assistance but is not liable for changes in airline policies, fare fluctuations, or actions taken by third-party carriers.</p>
                    <h4>Governing Law</h4>
                    <p>These terms are governed by the laws of the United States. Any disputes shall be resolved through binding arbitration in accordance with applicable US regulations.</p>
                </div>
            </div>
        </div>

        <div class="modal-overlay" id="disclaimer-modal" role="dialog" aria-modal="true" aria-labelledby="disclaimer-modal-title">
            <div class="modal">
                <button class="modal__close" onclick="closeModal('disclaimer-modal')" aria-label="Close Disclaimer modal">&times;</button>
                <h3 class="modal__title" id="disclaimer-modal-title">Full Disclaimer</h3>
                <div class="modal__body">
                    <p><strong>Trevomo Travel Desk</strong> is an <strong>independent travel assistance desk</strong> operating as a third-party service provider. We are <strong>NOT</strong> an official representative, agent, or customer service department of any airline, including but not limited to Delta Air Lines, United Airlines, American Airlines, Southwest Airlines, Alaska Airlines, JetBlue Airways, Spirit Airlines, Frontier Airlines, or Hawaiian Airlines.</p>
                    <p>All trademarks, service marks, trade names, and logos referenced on this website are the property of their respective owners. Any reference to airline brands is for informational and descriptive purposes only and does not imply endorsement, sponsorship, or affiliation.</p>
                    <p>The phone number provided on this site connects callers to independent travel specialists who can assist with bookings across multiple carriers. This is a paid affiliate marketing service operating in compliance with US Federal Trade Commission (FTC) guidelines.</p>
                    <p>Marketcall Offer ID: 6711 (Flight Booking Bundle).</p>
                </div>
            </div>
        </div>

        <div class="modal-overlay" id="contact-modal" role="dialog" aria-modal="true" aria-labelledby="contact-modal-title">
            <div class="modal">
                <button class="modal__close" onclick="closeModal('contact-modal')" aria-label="Close Contact Us modal">&times;</button>
                <h3 class="modal__title" id="contact-modal-title">Contact Us</h3>
                <div class="modal__body">
                    <p>For immediate flight booking assistance, rescheduling, or cancellations, please call our independent travel desk directly:</p>
                    <p style="font-size:clamp(1rem,4vw,1.4rem);font-weight:800;color:#0F172A;text-align:center;margin:14px 0;word-break:break-all;">
                        <a href="tel:+18332420904" style="color:#0F172A;text-decoration:none;padding:8px 4px;display:inline-block;min-height:44px;">+1 (833) 242-0904</a>
                    </p>
                    <p>Our travel specialists are available 24 hours a day, 7 days a week to assist you.</p>
                    <p><strong>Trevomo Travel Desk</strong> — Independent Travel Assistance</p>
                    <p style="font-size:0.7rem;color:#64748b;">Marketcall Offer ID: 6711 | Flight Booking Bundle</p>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('copyright-year').textContent = new Date().getFullYear();

            function openModal(modalId) {
                const modal = document.getElementById(modalId);
                if (modal) {
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                    const closeBtn = modal.querySelector('.modal__close');
                    if (closeBtn) {
                        setTimeout(() => closeBtn.focus(), 100);
                    }
                    modal.setAttribute('aria-hidden', 'false');
                }
            }

            function closeModal(modalId) {
                const modal = document.getElementById(modalId);
                if (modal) {
                    modal.classList.remove('active');
                    document.body.style.overflow = '';
                    modal.setAttribute('aria-hidden', 'true');
                    const trigger = document.querySelector(`[onclick*="${modalId}"]`);
                    if (trigger) {
                        setTimeout(() => trigger.focus(), 100);
                    }
                }
            }

            document.querySelectorAll('.modal-overlay').forEach(overlay => {
                overlay.addEventListener('click', function(e) {
                    if (e.target === this) {
                        closeModal(this.id);
                    }
                });
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    const activeModal = document.querySelector('.modal-overlay.active');
                    if (activeModal) {
                        closeModal(activeModal.id);
                    }
                }
            });

            document.querySelectorAll('.modal-overlay').forEach(modal => {
                modal.setAttribute('aria-hidden', 'true');
            });

            console.log('%cTrevomo Travel Desk %c| Independent Travel Assistance Desk',
                'font-weight:bold;color:#0F172A;font-size:14px;', 'color:#64748B;font-size:11px;');
            console.log('%cMarketcall Offer ID: 6711 %c| Flight Booking Bundle',
                'font-weight:bold;color:#1E40AF;', 'color:#64748B;');
            console.log('%c📞 Call: +1 (833) 242-0904 %c| Available 24/7',
                'font-weight:bold;color:#F97316;font-size:13px;', 'color:#10B981;');
            console.log('%cFTC Compliant ✅ | Independent Desk | Not Airline-Affiliated',
                'color:#64748B;font-size:9px;');
        </script>

    </body>
    </html>
    ''')
    if __name__ == '__main__':
    app.run(debug=True, port=5000)
