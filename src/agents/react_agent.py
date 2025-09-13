"""
React Agent - Reads plans and creates real files, can iterate and fix based on feedback.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from groq import Groq

class ReactAgent:
    """Agent responsible for reading plans and creating/updating real project files."""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.projects_dir = Path("custom_projects")
        self.projects_dir.mkdir(exist_ok=True)
        self.plans_dir = Path("project_plans")
    
    async def create_project_from_plan(self, plan_id: str) -> Dict[str, Any]:
        """Create a real project from a plan."""
        
        print(f"🔧 React Agent: Creating project from plan {plan_id}")
        
        # Load the plan
        plan = await self._load_plan(plan_id)
        if not plan:
            return {"status": "error", "message": f"Plan {plan_id} not found"}
        
        project_name = plan["project_name"]
        project_path = self.projects_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        # Create files based on plan
        files_created = await self._create_project_files(plan, project_path)
        
        return {
            "status": "success",
            "project_name": project_name,
            "project_path": str(project_path),
            "files_created": files_created,
            "plan_id": plan_id
        }
    
    async def _load_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Load a plan from the plans directory."""
        for plan_file in self.plans_dir.glob("*.json"):
            with open(plan_file, 'r') as f:
                plan = json.load(f)
                if plan.get("plan_id") == plan_id:
                    return plan
        return None
    
    async def _create_project_files(self, plan: Dict[str, Any], project_path: Path) -> List[Dict[str, Any]]:
        """Create all project files based on the plan."""
        
        files_created = []
        file_structure = plan.get("file_structure", {})
        
        # Create backend files
        backend_files = await self._create_backend_files(plan, project_path)
        files_created.extend(backend_files)
        
        # Create frontend files
        frontend_files = await self._create_frontend_files(plan, project_path)
        files_created.extend(frontend_files)
        
        # Create test files
        test_files = await self._create_test_files(plan, project_path)
        files_created.extend(test_files)
        
        # Create deployment files
        deployment_files = await self._create_deployment_files(plan, project_path)
        files_created.extend(deployment_files)
        
        return files_created
    
    async def _create_backend_files(self, plan: Dict[str, Any], project_path: Path) -> List[Dict[str, Any]]:
        """Create backend Python files."""
        files = []
        
        # Create main.py
        main_py = project_path / "main.py"
        main_content = await self._generate_main_py(plan)
        main_py.write_text(main_content)
        files.append({
            "name": "main.py",
            "type": "Python",
            "path": str(main_py),
            "size": len(main_content)
        })
        
        # Create requirements.txt
        requirements = project_path / "requirements.txt"
        req_content = await self._generate_requirements_txt(plan)
        requirements.write_text(req_content)
        files.append({
            "name": "requirements.txt",
            "type": "Config",
            "path": str(requirements),
            "size": len(req_content)
        })
        
        # Create API directory and files
        api_dir = project_path / "api"
        api_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        init_py = api_dir / "__init__.py"
        init_py.write_text("# API package")
        files.append({
            "name": "api/__init__.py",
            "type": "Python",
            "path": str(init_py),
            "size": 15
        })
        
        # Create routes.py
        routes_py = api_dir / "routes.py"
        routes_content = await self._generate_routes_py(plan)
        routes_py.write_text(routes_content)
        files.append({
            "name": "api/routes.py",
            "type": "Python",
            "path": str(routes_py),
            "size": len(routes_content)
        })
        
        # Create models directory
        models_dir = project_path / "models"
        models_dir.mkdir(exist_ok=True)
        
        models_init = models_dir / "__init__.py"
        models_init.write_text("# Models package")
        files.append({
            "name": "models/__init__.py",
            "type": "Python",
            "path": str(models_init),
            "size": 18
        })
        
        models_data = models_dir / "data.py"
        models_content = await self._generate_models_py(plan)
        models_data.write_text(models_content)
        files.append({
            "name": "models/data.py",
            "type": "Python",
            "path": str(models_data),
            "size": len(models_content)
        })
        
        return files
    
    async def _create_frontend_files(self, plan: Dict[str, Any], project_path: Path) -> List[Dict[str, Any]]:
        """Create frontend HTML/CSS/JS files."""
        files = []
        
        # Create index.html
        index_html = project_path / "index.html"
        html_content = await self._generate_index_html(plan)
        index_html.write_text(html_content)
        files.append({
            "name": "index.html",
            "type": "HTML",
            "path": str(index_html),
            "size": len(html_content)
        })
        
        # Create style.css
        style_css = project_path / "style.css"
        css_content = await self._generate_style_css(plan)
        style_css.write_text(css_content)
        files.append({
            "name": "style.css",
            "type": "CSS",
            "path": str(style_css),
            "size": len(css_content)
        })
        
        # Create script.js
        script_js = project_path / "script.js"
        js_content = await self._generate_script_js(plan)
        script_js.write_text(js_content)
        files.append({
            "name": "script.js",
            "type": "JavaScript",
            "path": str(script_js),
            "size": len(js_content)
        })
        
        return files
    
    async def _create_test_files(self, plan: Dict[str, Any], project_path: Path) -> List[Dict[str, Any]]:
        """Create test files."""
        files = []
        
        tests_dir = project_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Create test_main.py
        test_main = tests_dir / "test_main.py"
        test_content = await self._generate_test_main(plan)
        test_main.write_text(test_content)
        files.append({
            "name": "tests/test_main.py",
            "type": "Python Test",
            "path": str(test_main),
            "size": len(test_content)
        })
        
        return files
    
    async def _create_deployment_files(self, plan: Dict[str, Any], project_path: Path) -> List[Dict[str, Any]]:
        """Create deployment files."""
        files = []
        
        # Create Dockerfile
        dockerfile = project_path / "Dockerfile"
        docker_content = await self._generate_dockerfile(plan)
        dockerfile.write_text(docker_content)
        files.append({
            "name": "Dockerfile",
            "type": "Docker",
            "path": str(dockerfile),
            "size": len(docker_content)
        })
        
        # Create README.md
        readme = project_path / "README.md"
        readme_content = await self._generate_readme(plan)
        readme.write_text(readme_content)
        files.append({
            "name": "README.md",
            "type": "Markdown",
            "path": str(readme),
            "size": len(readme_content)
        })
        
        return files
    
    async def _generate_main_py(self, plan: Dict[str, Any]) -> str:
        """Generate main.py content using AI."""
        try:
            prompt = f"""
            Create a FastAPI main.py file for this project:
            Project: {plan['project_name']}
            Command: {plan['command']}
            
            Include:
            - FastAPI app setup
            - CORS middleware
            - Static file serving
            - Basic routes
            - Health check endpoint
            - Error handling
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except:
            # Fallback content
            return f'''"""
{plan['project_name']} - Generated by React Agent
Command: {plan['command']}
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(
    title="{plan['project_name']}",
    description="Generated by Multi-Agent System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.exists("."):
    app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """Root endpoint - serves the main application."""
    if os.path.exists("index.html"):
        return HTMLResponse(open("index.html").read())
    return {{"message": "{plan['project_name']}", "status": "running"}}

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy", "message": "Application is running"}}

@app.get("/api/info")
async def info():
    """Get project information."""
    return {{
        "project_name": "{plan['project_name']}",
        "command": "{plan['command']}",
        "status": "active"
    }}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''
    
    async def _generate_requirements_txt(self, plan: Dict[str, Any]) -> str:
        """Generate requirements.txt content."""
        dependencies = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0", 
            "pydantic==2.5.0",
            "python-multipart==0.0.6",
            "pytest==7.4.0",
            "httpx==0.25.2"
        ]
        return "\n".join(dependencies) + "\n"
    
    async def _generate_routes_py(self, plan: Dict[str, Any]) -> str:
        """Generate API routes."""
        return f'''"""
API Routes for {plan['project_name']}
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def api_root():
    return {{"message": "API is running", "project": "{plan['project_name']}"}}

@router.get("/command")
async def get_command():
    return {{"original_command": "{plan['command']}", "status": "processed"}}
'''
    
    async def _generate_models_py(self, plan: Dict[str, Any]) -> str:
        """Generate data models."""
        return f'''"""
Data models for {plan['project_name']}
"""
from pydantic import BaseModel
from typing import Optional

class ProjectInfo(BaseModel):
    name: str
    command: str
    status: str

class HealthResponse(BaseModel):
    status: str
    message: str
'''
    
    async def _generate_index_html(self, plan: Dict[str, Any]) -> str:
        """Generate HTML content."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan['project_name']}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{plan['project_name']}</h1>
            <p>Generated by Multi-Agent System</p>
        </header>
        
        <main>
            <div class="info-card">
                <h2>Project Information</h2>
                <p><strong>Command:</strong> {plan['command']}</p>
                <p><strong>Status:</strong> <span id="status">Loading...</span></p>
            </div>
            
            <div class="actions">
                <button onclick="checkHealth()">Check Health</button>
                <button onclick="getInfo()">Get Info</button>
            </div>
            
            <div id="output" class="output"></div>
        </main>
    </div>
    
    <script src="script.js"></script>
</body>
</html>'''
    
    async def _generate_style_css(self, plan: Dict[str, Any]) -> str:
        """Generate CSS content."""
        return '''body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: white;
}

.container {
    max-width: 800px;
    margin: 0 auto;
}

header {
    text-align: center;
    margin-bottom: 40px;
}

header h1 {
    font-size: 2.5rem;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.info-card {
    background: rgba(255, 255, 255, 0.1);
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    backdrop-filter: blur(10px);
}

.actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-bottom: 30px;
}

button {
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s;
}

button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.output {
    background: rgba(0, 0, 0, 0.2);
    padding: 20px;
    border-radius: 10px;
    min-height: 100px;
    font-family: monospace;
    white-space: pre-wrap;
}'''
    
    async def _generate_script_js(self, plan: Dict[str, Any]) -> str:
        """Generate JavaScript content."""
        return '''async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        document.getElementById('output').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById('output').textContent = 'Error: ' + error.message;
    }
}

async function getInfo() {
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        document.getElementById('output').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById('output').textContent = 'Error: ' + error.message;
    }
}

// Auto-check health on load
window.onload = function() {
    checkHealth();
    setInterval(checkHealth, 30000); // Check every 30 seconds
};'''
    
    async def _generate_test_main(self, plan: Dict[str, Any]) -> str:
        """Generate test file."""
        return f'''"""
Test cases for {plan['project_name']}
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_info_endpoint():
    """Test info endpoint."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "project_name" in data
    assert "command" in data
'''
    
    async def _generate_dockerfile(self, plan: Dict[str, Any]) -> str:
        """Generate Dockerfile."""
        return f'''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "main.py"]'''
    
    async def _generate_readme(self, plan: Dict[str, Any]) -> str:
        """Generate README.md."""
        return f'''# {plan['project_name']}

Generated by Multi-Agent Development System

## Command
{plan['command']}

## Quick Start

### Local Development
```bash
pip install -r requirements.txt
python main.py
```

### Docker
```bash
docker build -t {plan['project_name']} .
docker run -p 8001:8001 {plan['project_name']}
```

## API Endpoints
- GET / - Main application
- GET /api/health - Health check
- GET /api/info - Project information

## Testing
```bash
pytest tests/
```

## Generated by Multi-Agent System
This project was automatically generated by the Multi-Agent Development System.'''
    
    async def fix_file_based_on_feedback(self, project_name: str, file_path: str, feedback: str) -> Dict[str, Any]:
        """Fix a file based on test feedback using AI."""
        
        print(f"🔧 React Agent: Fixing {file_path} based on feedback")
        
        # Read the current file
        project_path = self.projects_dir / project_name
        full_file_path = project_path / file_path
        
        if not full_file_path.exists():
            return {"status": "error", "message": f"File {file_path} not found"}
        
        current_content = full_file_path.read_text()
        
        try:
            # Use AI to fix the file
            prompt = f"""
            Fix this code based on the feedback:
            
            File: {file_path}
            Current code:
            {current_content}
            
            Feedback: {feedback}
            
            Please provide the corrected code that addresses the feedback.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            fixed_content = response.choices[0].message.content
            
            # Write the fixed content back
            full_file_path.write_text(fixed_content)
            
            return {
                "status": "success",
                "file_path": file_path,
                "message": "File fixed based on feedback"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file_path": file_path,
                "message": f"Failed to fix file: {str(e)}"
            }
