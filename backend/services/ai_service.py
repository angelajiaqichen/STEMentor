import os
import logging
from typing import Optional, Dict, Any, List
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from pathlib import Path

logger = logging.getLogger(__name__)

class LlamaAIService:
    """AI Service using Meta Llama 3 from Hugging Face"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the Llama 3 AI service
        
        Args:
            model_name: The Hugging Face model name for Llama 3
        """
        # Use environment variable or default to Llama 3 8B
        self.model_name = model_name or os.getenv("LLAMA_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.is_initialized = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Model configuration
        self.max_length = 2048
        self.max_new_tokens = 512
        self.temperature = 0.7
        self.top_p = 0.9
        self.repetition_penalty = 1.1
        
    async def initialize(self):
        """Initialize the model and tokenizer"""
        try:
            logger.info(f"Initializing Llama 3 model: {self.model_name}")
            logger.info(f"Using device: {self.device}")
            
            # Check if we have a Hugging Face token
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if not hf_token:
                logger.warning("HUGGINGFACE_TOKEN not found. You may need this for some models.")
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=hf_token,
                trust_remote_code=True
            )
            
            # Add pad token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate configuration
            logger.info("Loading model...")
            model_kwargs = {
                "token": hf_token,
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None,
            }
            
            # For CPU or limited GPU memory, use smaller precision
            if self.device == "cpu":
                model_kwargs["torch_dtype"] = torch.float32
                model_kwargs.pop("device_map", None)
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            self.is_initialized = True
            logger.info("Llama 3 model initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Llama 3 model: {str(e)}")
            # Fallback to a smaller model or mock responses
            await self._initialize_fallback()
    
    async def _initialize_fallback(self):
        """Initialize with a smaller model or mock responses if main model fails"""
        try:
            logger.info("Attempting to load smaller model as fallback...")
            # Try a smaller model like CodeLlama or fall back to mock
            fallback_model = "microsoft/DialoGPT-medium"  # Much smaller alternative
            
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForCausalLM.from_pretrained(
                fallback_model,
                torch_dtype=torch.float32
            )
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  # Force CPU
            )
            
            self.is_initialized = True
            self.model_name = fallback_model
            logger.info(f"Fallback model {fallback_model} initialized successfully!")
            
        except Exception as e:
            logger.error(f"Fallback initialization also failed: {str(e)}")
            self.is_initialized = False
    
    def _create_prompt(self, user_message: str, context: Optional[str] = None, system_message: Optional[str] = None) -> str:
        """Create a properly formatted prompt for Llama 3"""
        
        # Default system message for educational context
        if system_message is None:
            system_message = (
                "You are an intelligent AI tutor specializing in STEM education. "
                "You help students learn by providing clear explanations, breaking down complex concepts, "
                "and offering step-by-step guidance. Always be encouraging, patient, and educational in your responses."
            )
        
        # Format the prompt using Llama 3's chat format
        if "Meta-Llama-3" in self.model_name:
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

"""
            
            if context:
                prompt += f"Context: {context}\n\n"
            
            prompt += f"{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"
        else:
            # Generic format for other models
            prompt = f"System: {system_message}\n\n"
            if context:
                prompt += f"Context: {context}\n\n"
            prompt += f"User: {user_message}\n\nAssistant:"
        
        return prompt
    
    async def generate_response(
        self, 
        user_message: str, 
        context: Optional[str] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response using Llama 3
        
        Args:
            user_message: The user's question or message
            context: Optional context from documents or previous conversation
            system_message: Optional custom system message
            **kwargs: Additional generation parameters
        
        Returns:
            Generated response string
        """
        
        if not self.is_initialized:
            return "I'm sorry, but the AI service is not properly initialized. Please try again later."
        
        try:
            # Create the prompt
            prompt = self._create_prompt(user_message, context, system_message)
            
            # Generation parameters
            generation_params = {
                "max_new_tokens": kwargs.get("max_new_tokens", self.max_new_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "repetition_penalty": kwargs.get("repetition_penalty", self.repetition_penalty),
                "do_sample": True,
                "eos_token_id": self.tokenizer.eos_token_id,
                "pad_token_id": self.tokenizer.pad_token_id,
            }
            
            # Generate response
            logger.info("Generating response with Llama 3...")
            outputs = self.pipeline(
                prompt,
                **generation_params,
                return_full_text=False  # Only return the new generated text
            )
            
            if outputs and len(outputs) > 0:
                response = outputs[0]['generated_text'].strip()
                
                # Clean up the response (remove any remaining special tokens)
                response = response.replace('<|eot_id|>', '').replace('<|end_of_text|>', '').strip()
                
                logger.info("Response generated successfully")
                return response
            else:
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I encountered an error while processing your request. Please try again."
    
    async def analyze_document(self, document_content: str, subject: str) -> Dict[str, Any]:
        """
        Analyze uploaded document content
        
        Args:
            document_content: The text content of the document
            subject: The subject category
        
        Returns:
            Analysis results including key topics, difficulty level, etc.
        """
        
        analysis_prompt = (
            f"Analyze this {subject} document and provide:\n"
            f"1. Key topics covered\n"
            f"2. Difficulty level (beginner/intermediate/advanced)\n"
            f"3. Main concepts that students should understand\n"
            f"4. Potential quiz questions\n\n"
            f"Document content:\n{document_content[:2000]}..."  # Limit content length
        )
        
        try:
            response = await self.generate_response(
                analysis_prompt,
                system_message="You are an expert educational content analyzer. Provide structured analysis of academic documents."
            )
            
            return {
                "analysis": response,
                "subject": subject,
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                "analysis": "Document analysis failed. Please try again.",
                "subject": subject,
                "status": "failed"
            }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "initialized": self.is_initialized,
            "max_length": self.max_length,
            "max_new_tokens": self.max_new_tokens
        }

# Global AI service instance
ai_service = LlamaAIService()
