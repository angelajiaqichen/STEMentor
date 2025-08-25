# STEMentor with Llama 3 via Hugging Face API 🦙📡

**Simple, lightweight setup using Hugging Face Inference API - no local model download required!**

## 🚀 Quick Setup (5 minutes)

### 1. Get Hugging Face Token
1. Create account at [huggingface.co](https://huggingface.co/)
2. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Create new token with "Read" permissions
4. Copy the token

### 2. Request Llama 3 Access (if needed)
1. Visit [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
2. Click "Request access" if required (usually approved quickly)

### 3. Setup the API
```bash
cd backend
python setup_llama.py
```

### 4. Configure Environment
Edit `.env` file:
```
HUGGINGFACE_TOKEN=your_actual_token_here
LLAMA_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
```

### 5. Run the API
```bash
python simple_main.py
```

**That's it!** 🎉 No model downloads, no GPU needed!

## 🧪 Test Your Chatbot

### Via Frontend
1. Start React frontend: `npm start` (in frontend directory)  
2. Go to `http://localhost:3000`
3. Click "💬 Test AI Tutor"
4. Get real Llama 3 responses!

### Via API
```bash
# Test status
curl http://localhost:8000/api/v1/ai/status

# Chat with Llama 3
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain photosynthesis in simple terms"}'
```

## 📊 Advantages of API Approach

✅ **No model downloads** - Models run on HF servers  
✅ **Lightweight** - Only ~50MB of dependencies vs 15GB+  
✅ **No GPU required** - Runs perfectly on any machine  
✅ **Always up-to-date** - Latest model versions automatically  
✅ **Fast setup** - Ready in minutes, not hours  
✅ **Scalable** - HF handles the infrastructure  

## 💰 Costs

- **Hugging Face Inference API** is free for moderate usage
- Rate limits apply (check HF documentation for current limits)
- For high-volume usage, consider HF Pro subscription

## 🛠️ Configuration

### Available Models
Edit `LLAMA_MODEL` in `.env`:
- `meta-llama/Meta-Llama-3-8B-Instruct` (recommended)
- `meta-llama/Meta-Llama-3-70B-Instruct` (more powerful)

### Generation Parameters
In `services/ai_service.py`:
```python
self.max_new_tokens = 512    # Response length
self.temperature = 0.7       # Creativity (0.1-1.0) 
self.top_p = 0.9            # Nucleus sampling
```

## 🔍 Monitoring

- **Logs**: Check console output for API calls
- **Status**: `GET /api/v1/ai/status`
- **Health**: `GET /health`

## 🐛 Troubleshooting

**"Invalid token"** → Check your HUGGINGFACE_TOKEN in `.env`

**"Model access denied"** → Request access on the HF model page

**"Model loading"** → First call takes 10-30s, then it's fast

**Slow responses** → Normal for first few calls, then ~2-5 seconds

## 🎓 Educational Features

The AI tutor is optimized for STEM education:
- Explains complex concepts step-by-step
- Analyzes uploaded documents
- Provides encouraging, patient responses
- Offers practice questions and examples

## 🔄 Updates

To update:
```bash
pip install --upgrade httpx fastapi
git pull origin main
```

---

**🎯 Perfect for**: Development, testing, moderate usage, educational use  
**⚡ Response time**: ~2-5 seconds after initial warmup  
**💾 Storage**: No local model storage needed  
**🖥️ Requirements**: Any computer with internet connection
