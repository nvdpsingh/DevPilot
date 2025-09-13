"""
AI Service - Handles AI interactions using Groq API.
"""
import os
from typing import Dict, Any, List
import httpx
from ..config.settings import settings

class AIService:
    """Service for AI interactions using Groq API."""
    
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.ai_model
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Groq API."""
        
        if not self.api_key:
            return "AI service not configured - no API key provided"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"AI API error: {response.status_code} - {response.text}"
                    
        except Exception as e:
            return f"AI service error: {str(e)}"
    
    async def generate_plan(self, command: str, project_name: str) -> Dict[str, Any]:
        """Generate a project plan using AI."""
        
        prompt = f"""
        Create a detailed development plan for the following project:
        
        Project Name: {project_name}
        Command: {command}
        
        Please provide a comprehensive plan including:
        1. Project overview and objectives
        2. Technical architecture and technology stack
        3. File structure and key components
        4. Implementation phases
        5. Testing strategy
        6. Deployment considerations
        
        Format the response as a structured plan that can be used for development.
        """
        
        plan_text = await self.generate_text(prompt, max_tokens=2000)
        
        return {
            "status": "success",
            "plan": plan_text,
            "project_name": project_name,
            "command": command
        }
    
    async def generate_code(self, prompt: str, file_type: str = "python") -> str:
        """Generate code using AI."""
        
        code_prompt = f"""
        Generate {file_type} code for the following requirements:
        
        {prompt}
        
        Please provide clean, well-commented, production-ready code.
        Include proper error handling and best practices.
        """
        
        return await self.generate_text(code_prompt, max_tokens=1500)
    
    async def fix_code(self, code: str, issues: List[str], file_type: str = "python") -> str:
        """Fix code issues using AI."""
        
        issues_text = "\n".join([f"- {issue}" for issue in issues])
        
        fix_prompt = f"""
        Fix the following {file_type} code based on the issues identified:
        
        Issues:
        {issues_text}
        
        Original Code:
        ```{file_type}
        {code}
        ```
        
        Please provide the corrected code with all issues resolved.
        """
        
        return await self.generate_text(fix_prompt, max_tokens=1500)

# Global instance
ai_service = AIService()
