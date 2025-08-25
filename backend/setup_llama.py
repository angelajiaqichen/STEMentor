#!/usr/bin/env python3
"""
Setup script for STEMentor with Llama 3 integration
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_requirements():
    """Check if Python and pip are available"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if pip is available
    try:
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
        print("✅ pip is available")
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False
    
    return True

def setup_environment():
    """Set up the environment file"""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to actual env file
        with open(env_example) as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your HUGGINGFACE_TOKEN")
        print("   You can get a token from: https://huggingface.co/settings/tokens")
    else:
        print("✅ Environment file already exists")

def install_dependencies():
    """Install Python dependencies"""
    print("\n🔧 Installing Python dependencies...")
    
    # Install torch first (may need specific version for your system)
    torch_result = run_command(
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "Installing PyTorch (CPU version)"
    )
    
    if torch_result is None:
        print("⚠️  PyTorch installation may have failed, trying with CUDA support...")
        run_command(
            "pip install torch torchvision torchaudio",
            "Installing PyTorch (with CUDA if available)"
        )
    
    # Install other dependencies
    result = run_command(
        "pip install -r requirements.txt",
        "Installing other dependencies"
    )
    
    if result is None:
        print("❌ Failed to install dependencies")
        return False
    
    return True

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} installed")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__} installed")
        
        from services.ai_service import LlamaAIService
        print("✅ AI service can be imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🎓 STEMentor with Llama 3 Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install Python 3.8+ and pip")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your HUGGINGFACE_TOKEN")
    print("2. Run: python simple_main.py")
    print("3. The API will start and begin loading the Llama 3 model")
    print("\nNote: The first run may take several minutes to download the model.")

if __name__ == "__main__":
    main()
