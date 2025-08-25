import os
import logging
from typing import Optional, Dict, Any, List
import httpx
import json
import asyncio

logger = logging.getLogger(__name__)

class LlamaAIService:
    """AI Service using Meta Llama 3 via Hugging Face Inference API"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the Llama 3 AI service
        
        Args:
            model_name: The Hugging Face model name for Llama 3
        """
        # Use environment variable or default to Llama 3 8B
        self.model_name = model_name or os.getenv("LLAMA_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.is_initialized = False
        
        # Model configuration
        self.max_new_tokens = 512
        self.temperature = 0.7
        self.top_p = 0.9
        self.repetition_penalty = 1.1
        
        # HTTP client for API calls
        self.client = None
        
    async def initialize(self):
        """Initialize the API client and test connection"""
        try:
            logger.info(f"Initializing Llama 3 API service: {self.model_name}")
            logger.info("Using Hugging Face Inference API (no local model needed)")
            
            # Check if we have a Hugging Face token
            if not self.hf_token:
                logger.error("HUGGINGFACE_TOKEN not found. This is required for the Inference API.")
                return False
            
            # Create HTTP client
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.hf_token}",
                    "Content-Type": "application/json"
                },
                timeout=httpx.Timeout(120.0)  # 2 minutes timeout for API calls
            )
            
            # Test the API connection
            logger.info("Testing API connection...")
            test_response = await self._make_api_call(
                "Hello, can you respond with a simple greeting?",
                max_new_tokens=50
            )
            
            if test_response:
                self.is_initialized = True
                logger.info("✅ Llama 3 API service initialized successfully!")
                logger.info(f"Test response: {test_response[:100]}...")
                return True
            else:
                logger.error("❌ Failed to get response from API")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Llama 3 API service: {str(e)}")
            return False
    
    async def _make_api_call(self, prompt: str, **parameters) -> Optional[str]:
        """Make a call to the Hugging Face Inference API"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": parameters.get("max_new_tokens", self.max_new_tokens),
                    "temperature": parameters.get("temperature", self.temperature),
                    "top_p": parameters.get("top_p", self.top_p),
                    "repetition_penalty": parameters.get("repetition_penalty", self.repetition_penalty),
                    "do_sample": True,
                    "return_full_text": False  # Only return new generated text
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            logger.info(f"Making API call to: {self.api_url}")
            response = await self.client.post(self.api_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    # Standard response format
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    # Alternative response format
                    generated_text = result.get("generated_text", "")
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return None
                
                # Clean up the response
                generated_text = generated_text.strip()
                generated_text = generated_text.replace('<|eot_id|>', '').replace('<|end_of_text|>', '')
                
                return generated_text.strip()
                
            elif response.status_code == 503:
                # Model is loading, wait and retry
                logger.info("Model is loading, waiting 10 seconds before retry...")
                await asyncio.sleep(10)
                return await self._make_api_call(prompt, **parameters)
                
            else:
                logger.error(f"API call failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making API call: {str(e)}")
            return None
    
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
            
            prompt += f"{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
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
        Generate a response using Llama 3 via Hugging Face API
        
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
            
            # Generate response via API
            logger.info(f"Generating response for: {user_message[:100]}...")
            response = await self._make_api_call(
                prompt,
                max_new_tokens=kwargs.get("max_new_tokens", self.max_new_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty)
            )
            
            if response:
                logger.info("Response generated successfully via API")
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
            f"Document content:\n{document_content[:1500]}..."  # Limit content length for API
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
            "api_url": self.api_url,
            "initialized": self.is_initialized,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "deployment_type": "huggingface_inference_api"
        }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.client:
            await self.client.aclose()
            logger.info("HTTP client closed")

# Global AI service instance
ai_service = LlamaAIService()
