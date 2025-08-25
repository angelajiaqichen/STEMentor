# STEMentor with Meta Llama 3 Integration 🦙

This guide explains how to set up and use Meta Llama 3 from Hugging Face as the LLM for your STEMentor chatbot.

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip package manager
- At least 8GB RAM (16GB+ recommended for Llama 3 8B)
- GPU with 12GB+ VRAM (optional, but recommended)

### 2. Hugging Face Account
1. Create an account at [Hugging Face](https://huggingface.co/)
2. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Create a new token with "Read" permissions
4. Save this token - you'll need it later

### 3. Request Access to Llama 3 (If Needed)
Some Llama 3 models may require requesting access:
1. Visit [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
2. Click "Request access" if required
3. Wait for approval (usually quick)

### 4. Automated Setup
Run the setup script to install dependencies automatically:

```bash
cd backend
python setup_llama.py
```

This will:
- Check your Python/pip installation
- Install PyTorch and Transformers
- Install all required dependencies
- Create environment configuration file

### 5. Manual Setup (Alternative)
If you prefer manual setup:

```bash
# Install PyTorch (CPU version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or for CUDA support (if you have a compatible GPU)
pip install torch torchvision torchaudio

# Install other dependencies
pip install -r requirements.txt
```

### 6. Configure Environment
Edit the `.env` file and add your Hugging Face token:

```bash
# Copy the example file
cp .env.example .env

# Edit .env file
nano .env
```

Add your token:
```
HUGGINGFACE_TOKEN=your_actual_token_here
LLAMA_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
```

## 🎯 Available Models

You can choose different Llama 3 variants by setting `LLAMA_MODEL` in your `.env` file:

| Model | Size | RAM Required | Description |
|-------|------|--------------|-------------|
| `meta-llama/Meta-Llama-3-8B-Instruct` | 8B | 16GB+ | **Recommended** - Good balance of performance and resource usage |
| `meta-llama/Meta-Llama-3-70B-Instruct` | 70B | 64GB+ | Highest quality, requires significant resources |
| `meta-llama/Llama-2-7b-chat-hf` | 7B | 14GB+ | Alternative if Llama 3 access is unavailable |

## 🏃‍♂️ Running the API

Start the backend with Llama 3 integration:

```bash
cd backend
python simple_main.py
```

The first run will:
1. Download the model (several GB) - this may take 10-30 minutes
2. Load the model into memory
3. Start the API server

You'll see logs like:
```
INFO: Initializing Llama 3 model: meta-llama/Meta-Llama-3-8B-Instruct
INFO: Using device: cuda  # or cpu
INFO: Loading tokenizer...
INFO: Loading model...
INFO: Llama 3 model initialized successfully!
```

## 🧪 Testing the Chatbot

### 1. Test via Frontend
1. Make sure your React frontend is running: `npm start` (in the frontend directory)
2. Go to `http://localhost:3000`
3. Click "Test AI Tutor" button
4. You should see a response from Llama 3

### 2. Test via API
```bash
# Test the AI status endpoint
curl http://localhost:8000/api/v1/ai/status

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain photosynthesis"}'
```

### 3. Test via API Documentation
Visit `http://localhost:8000/docs` to use the interactive API documentation.

## 📊 Performance Considerations

### CPU vs GPU
- **CPU**: Works but slow (30-60 seconds per response)
- **GPU**: Much faster (2-10 seconds per response)
- **Apple Silicon (M1/M2)**: Good performance with MPS backend

### Memory Usage
- **Llama 3 8B**: ~16GB RAM or ~12GB VRAM
- **Llama 3 70B**: ~140GB RAM or ~80GB VRAM
- **Fallback models**: ~4-8GB RAM

### Optimization Options

1. **Use GPU if available**:
   ```python
   # Automatic in the code - GPU will be used if detected
   ```

2. **Reduce precision for less memory**:
   The code automatically uses `float16` on GPU, `float32` on CPU

3. **Use smaller models**:
   ```bash
   # In .env file
   LLAMA_MODEL=microsoft/DialoGPT-medium  # Much smaller fallback
   ```

## 🛠️ Troubleshooting

### Common Issues

**1. "CUDA out of memory"**
- Reduce batch size or use CPU
- Try a smaller model
- Close other GPU applications

**2. "Model access denied"**
- Request access on Hugging Face model page
- Ensure your token has correct permissions
- Check if the model name is correct

**3. "Import error: No module named 'transformers'"**
- Run: `pip install transformers`
- Ensure you're using the correct Python environment

**4. Slow responses**
- This is normal on CPU (30+ seconds)
- Consider using GPU or a smaller model

**5. "Failed to initialize AI service"**
- Check your internet connection (for model download)
- Verify Hugging Face token
- Look at detailed logs for specific error

### Getting Help

The system includes fallback mechanisms:
1. If Llama 3 fails, it tries a smaller model
2. If all models fail, it returns error messages
3. Detailed logging helps identify issues

Check the logs for detailed error information.

## 🔧 Advanced Configuration

### Custom Model Parameters
You can modify generation parameters in `services/ai_service.py`:

```python
self.max_new_tokens = 512      # Maximum response length
self.temperature = 0.7         # Creativity (0.1-1.0)
self.top_p = 0.9              # Nucleus sampling
self.repetition_penalty = 1.1  # Avoid repetition
```

### Custom System Messages
The chatbot uses educational system messages by default, but you can customize them:

```python
# Via API
{
  "message": "Explain calculus",
  "system_message": "You are a math professor. Be very detailed and use examples."
}
```

## 📈 Monitoring

The API provides several monitoring endpoints:

- `/health` - Basic health check
- `/api/v1/ai/status` - AI service status and model info
- Check logs for detailed model performance metrics

## 🎓 Educational Features

The Llama 3 integration is optimized for education:

1. **STEM-focused system prompts**
2. **Document analysis capabilities**
3. **Context-aware responses**
4. **Step-by-step explanations**
5. **Encouraging and patient tone**

The AI tutor can:
- Answer questions about uploaded documents
- Explain complex concepts step-by-step
- Generate practice questions
- Provide learning guidance
- Adapt to different difficulty levels

## 🔄 Updates and Maintenance

To update the model or dependencies:

```bash
# Update Python packages
pip install --upgrade transformers torch

# Clear model cache if needed
rm -rf ~/.cache/huggingface/

# Restart the API to reload everything
```

---

**Note**: The first startup will be slow as it downloads the model. Subsequent starts are much faster as the model is cached locally.
