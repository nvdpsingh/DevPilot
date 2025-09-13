"""
Planner Agent - Creates and manages project plans in documents.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from groq import Groq

class PlannerAgent:
    """Agent responsible for planning projects and saving plans to documents."""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.plans_dir = Path("project_plans")
        self.plans_dir.mkdir(exist_ok=True)
    
    async def create_project_plan(self, command: str, project_name: str) -> Dict[str, Any]:
        """Create a comprehensive project plan and save it to a document."""
        
        print(f"🧠 Planner Agent: Creating plan for '{command}'")
        
        # Generate AI-powered plan
        plan = await self._generate_ai_plan(command, project_name)
        
        # Save plan to document
        plan_doc = await self._save_plan_to_document(plan, project_name)
        
        return {
            "status": "success",
            "plan_id": plan["plan_id"],
            "plan_document": str(plan_doc),
            "plan": plan
        }
    
    async def _generate_ai_plan(self, command: str, project_name: str) -> Dict[str, Any]:
        """Generate a detailed project plan using AI."""
        
        try:
            # Create AI prompt for planning
            prompt = f"""
            Create a detailed development plan for: {command}
            Project Name: {project_name}
            
            Please provide:
            1. Project overview and goals
            2. Technical architecture
            3. File structure (detailed)
            4. Implementation phases
            5. Testing strategy
            6. Deployment requirements
            7. Dependencies and requirements
            
            Format as a structured JSON plan.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            ai_plan = response.choices[0].message.content
            
            # Parse and structure the plan
            plan = {
                "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "project_name": project_name,
                "command": command,
                "created_at": datetime.now().isoformat(),
                "ai_plan": ai_plan,
                "phases": self._extract_phases(ai_plan),
                "file_structure": self._extract_file_structure(ai_plan),
                "dependencies": self._extract_dependencies(ai_plan),
                "status": "created"
            }
            
        except Exception as e:
            print(f"⚠️ AI planning failed: {e}")
            # Fallback plan
            plan = self._create_fallback_plan(command, project_name)
        
        return plan
    
    def _extract_phases(self, ai_plan: str) -> List[Dict[str, str]]:
        """Extract implementation phases from AI plan."""
        phases = [
            {"phase": 1, "name": "Setup", "description": "Initialize project structure and dependencies"},
            {"phase": 2, "name": "Core Files", "description": "Create main application files"},
            {"phase": 3, "name": "API Development", "description": "Build API endpoints and routes"},
            {"phase": 4, "name": "Frontend", "description": "Create user interface"},
            {"phase": 5, "name": "Testing", "description": "Implement and run tests"},
            {"phase": 6, "name": "Deployment", "description": "Deploy application locally"},
            {"phase": 7, "name": "Iteration", "description": "Test, fix, and improve based on feedback"}
        ]
        return phases
    
    def _extract_file_structure(self, ai_plan: str) -> Dict[str, List[str]]:
        """Extract file structure from AI plan."""
        return {
            "backend": [
                "main.py",
                "requirements.txt",
                "api/__init__.py",
                "api/routes.py",
                "models/__init__.py",
                "models/data.py",
                "utils/__init__.py",
                "utils/helpers.py"
            ],
            "frontend": [
                "index.html",
                "style.css",
                "script.js",
                "components/",
                "assets/"
            ],
            "tests": [
                "test_main.py",
                "test_api.py",
                "test_models.py"
            ],
            "deployment": [
                "Dockerfile",
                "docker-compose.yml",
                "README.md"
            ]
        }
    
    def _extract_dependencies(self, ai_plan: str) -> List[str]:
        """Extract dependencies from AI plan."""
        return [
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "pydantic==2.5.0",
            "python-multipart==0.0.6",
            "pytest==7.4.0",
            "httpx==0.25.2"
        ]
    
    def _create_fallback_plan(self, command: str, project_name: str) -> Dict[str, Any]:
        """Create a fallback plan when AI fails."""
        return {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "project_name": project_name,
            "command": command,
            "created_at": datetime.now().isoformat(),
            "ai_plan": f"Fallback plan for: {command}",
            "phases": self._extract_phases(""),
            "file_structure": self._extract_file_structure(""),
            "dependencies": self._extract_dependencies(""),
            "status": "created"
        }
    
    async def _save_plan_to_document(self, plan: Dict[str, Any], project_name: str) -> Path:
        """Save the plan to a JSON document."""
        
        plan_file = self.plans_dir / f"{project_name}_plan.json"
        
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"📄 Plan saved to: {plan_file}")
        return plan_file
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a plan by ID."""
        for plan_file in self.plans_dir.glob("*.json"):
            with open(plan_file, 'r') as f:
                plan = json.load(f)
                if plan.get("plan_id") == plan_id:
                    return plan
        return None
    
    async def update_plan_status(self, plan_id: str, status: str, notes: str = ""):
        """Update the status of a plan."""
        plan = await self.get_plan(plan_id)
        if plan:
            plan["status"] = status
            plan["updated_at"] = datetime.now().isoformat()
            if notes:
                plan["notes"] = notes
            
            plan_file = self.plans_dir / f"{plan['project_name']}_plan.json"
            with open(plan_file, 'w') as f:
                json.dump(plan, f, indent=2)
            
            print(f"📝 Plan {plan_id} updated: {status}")
    
    async def list_plans(self) -> List[Dict[str, Any]]:
        """List all available plans."""
        plans = []
        for plan_file in self.plans_dir.glob("*.json"):
            with open(plan_file, 'r') as f:
                plan = json.load(f)
                plans.append({
                    "plan_id": plan.get("plan_id"),
                    "project_name": plan.get("project_name"),
                    "status": plan.get("status"),
                    "created_at": plan.get("created_at")
                })
        return plans
