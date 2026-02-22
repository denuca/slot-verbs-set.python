# 🎰 Slot Machine -- Production-Ready Flask + Redis + Vercel Setup

## Overview

This project is a serverless-compatible Flask slot game using:

-   Flask (Python backend)
-   Redis (Free Tier)
-   Vercel Blob (Private storage, streamed securely)
-   Vercel Analytics
-   Vanilla JavaScript frontend

Designed to run on: - Vercel Free Tier - Redis Free Tier - Vercel Blob
Free Tier

------------------------------------------------------------------------

# 🧑‍💻 Local Development

## 1. Clone Repository

git clone `<your-repo>`{=html} cd slot-machine

## 2. Create Virtual Environment

python -m venv .venv\
source .venv/bin/activate\
pip install -r requirements.txt

## 3. Run Redis Locally (Docker)

docker run -p 6379:6379 redis

## 4. Add Test Data

redis-cli

SADD slot:index slot:A-A-A\
SET slot:A-A-A
'\[\["abc","abc","abc","1","1","0"\],\["def","def","def","1","1","0"\]\]'

## 5. Create .env

REDIS_URL=redis://localhost:6379/0\
SECRET_KEY=dev_secret\
MEDIA_STORAGE_PATH=./private_media\
MEDIA_TOKEN_SECRET=local_media_secret

## 6. Run Flask

flask run

Open http://127.0.0.1:5000

------------------------------------------------------------------------

# 🗂 Media Architecture (Private & Secure)

## 🎯 Goal

-   Media files must NOT be publicly downloadable
-   Media must NOT live in `/static`
-   Media must work locally AND on Vercel Free Tier
-   Must remain compatible with Redis Free Tier

## 📁 Where Media Files Go

### ✅ Local Development

Place files in:

private_media/ images/A.webp images/B.webp audio/A.mp3 audio/B.mp3

Files are NOT exposed publicly.

They are streamed through Flask via:

/media/`<signed-token>`{=html}

### ✅ On Vercel (Production)

1.  Create Private Blob Storage
2.  Upload files using same structure: images/A.png audio/A.mp3
3.  Store Blob credentials in Vercel Environment Variables

The backend fetches and streams media securely.

------------------------------------------------------------------------

# 🔐 How Secure Streaming Works

1.  Backend generates short-lived signed token
2.  Frontend receives secure media URL
3.  Browser requests `/media/<token>`
4.  Backend validates token
5.  Backend streams file from:
    -   Local disk (dev)
    -   Vercel Blob (prod)
6.  File never publicly exposed

Optional: Enable token expiration timestamps for stronger protection.

------------------------------------------------------------------------

# 🧠 Game Logic

## Spin Flow

1.  Random slot selected from Redis
2.  Symbols parsed from key (slot:A-A-A → A-A-A)
3.  Secure media URLs generated
4.  Session reset
5.  JSON returned to frontend

## Guess Flow

1.  Input normalized
2.  Full combo match checked
3.  Session tracks:
    -   attempts_used
    -   found_combos
4.  Game ends when:
    -   All combos found OR
    -   MAX_ATTEMPTS reached

------------------------------------------------------------------------

# 🎵 Recommended Media Formats (Free Tier Optimized)

## Images

Currently uses PNG but should use: WebP
- Smaller size than PNG/JPEG
- Excellent compression
- Fully supported in modern browsers
- Ideal for Vercel bandwidth limits

## Audio

Use: MP3 (128kbps mono)
- Small file size
- Universal support
- Best tradeoff for free tier bandwidth

Avoid:
- WAV (too large)
- Uncompressed formats

------------------------------------------------------------------------

# 🚀 Deploy to Vercel

## 1. Install CLI

npm i -g vercel

## 2. Login

vercel login

## 3. Initialize

vercel

## 4. Add Environment Variables (Dashboard → Settings)

REDIS_URL
SECRET_KEY
MEDIA_TOKEN_SECRET
BLOB_READ_WRITE_TOKEN (if using Blob)

## 5. Deploy

vercel --prod

------------------------------------------------------------------------

# 🔁 Updating Deployment

Push to GitHub OR run:

vercel --prod

------------------------------------------------------------------------

# 📊 Analytics

Add to index.html before
```{=html}
</body>
```
:

```{=html}
<script defer src="/_vercel/insights/script.js"></script>
```
View analytics in Vercel Dashboard → Analytics.

------------------------------------------------------------------------

# 🐛 Debugging

## Check Redis Keys

redis-cli SMEMBERS slot:index

## Check Slot Data

redis-cli GET slot:A-A-A

## JSON Validation

Ensure stored JSON is valid.

------------------------------------------------------------------------

# 🎯 Architecture Principles

-   Stateless backend
-   Redis session tracking
-   Private media streaming
-   Signed token protection
-   Free-tier optimized
-   Modular structure
