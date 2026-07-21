# Nemotron GPT Wrapper — Vercel Deployment

A secure ChatGPT-style web wrapper for the NVIDIA Nemotron model.
The **API key** and **hidden system prompt** live only on the server (Vercel
serverless function) and are never exposed to the browser.

## 📁 File Structure

```
nemotron-wrapper/
├── api/
│   └── chat.py          # Backend serverless function (hidden prompt + API key)
├── public/
│   └── index.html       # Frontend chat UI
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md
```

## 🚀 Deploy to Vercel

### Option A — GitHub (recommended)

1. Create a new GitHub repository and push these files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```
2. Go to https://vercel.com → **Add New… → Project** → import your repo.
3. In **Settings → Environment Variables**, add:
   ```
   NVIDIA_API_KEY = your-nvidia-key-here
   ```
4. Click **Deploy**. You'll get a URL like `https://your-ai.vercel.app`.

### Option B — Vercel CLI

```bash
npm i -g vercel
vercel            # follow prompts
vercel env add NVIDIA_API_KEY   # paste your key
vercel --prod
```

## 🔒 Security Notes

- ✅ The API key is read from `os.environ["NVIDIA_API_KEY"]` — set it in Vercel, never in code.
- ✅ The system prompt lives in `api/chat.py` (server-side only).
- ❌ Never put the key or prompt in `index.html` or any client-side JavaScript.

## ✏️ Customize

- **System prompt:** edit `SYSTEM_PROMPT` in `api/chat.py`.
- **Model settings:** change `temperature`, `top_p`, `max_tokens` in `api/chat.py`.
- **UI:** edit colors/text in `public/index.html`.
