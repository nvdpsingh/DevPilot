"""
FastAPI server for the Multi-Agent Development System.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import logging

from ..agents.coordinator_agent import CoordinatorAgent

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Development System",
    description="AI-powered development with iterative testing and fixing",
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

# Initialize coordinator
coordinator = CoordinatorAgent()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class ProjectRequest(BaseModel):
    command: str
    project_name: Optional[str] = None

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-Agent Development System</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 3rem;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 40px;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .card h2 {
                margin-top: 0;
                color: #fff;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
            }
            .form-group input, .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 16px;
            }
            .form-group input::placeholder, .form-group textarea::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
            .btn {
                background: linear-gradient(45deg, #3b82f6, #8b5cf6);
                border: none;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s;
                width: 100%;
            }
            .btn:hover {
                background: linear-gradient(45deg, #2563eb, #7c3aed);
                transform: translateY(-2px);
            }
            .btn:disabled {
                background: #6b7280;
                cursor: not-allowed;
                transform: none;
            }
            .status {
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                font-family: monospace;
                white-space: pre-wrap;
                min-height: 100px;
            }
            .projects-list {
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
            }
            .project-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .project-name {
                font-weight: 600;
            }
            .project-status {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
            .status-running { background: #10b981; color: white; }
            .status-stopped { background: #6b7280; color: white; }
            .status-error { background: #ef4444; color: white; }
            .status-completed { background: #3b82f6; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Multi-Agent Development System</h1>
                <p>AI-powered development with iterative testing and fixing</p>
            </div>
            
            <div class="main-content">
                <div class="card">
                    <h2>🚀 Start New Project</h2>
                    <form id="projectForm">
                        <div class="form-group">
                            <label for="command">Project Command</label>
                            <textarea id="command" placeholder="e.g., Build a task management app with user authentication" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="projectName">Project Name (optional)</label>
                            <input type="text" id="projectName" placeholder="Leave empty for auto-generated name">
                        </div>
                        <button type="submit" class="btn" id="startBtn">Start Development Cycle</button>
                    </form>
                    <div class="status" id="status">Ready to start development...</div>
                </div>
                
                <div class="card">
                    <h2>📊 Active Projects</h2>
                    <button class="btn" onclick="loadProjects()" style="margin-bottom: 20px;">Refresh Projects</button>
                    <div class="projects-list" id="projectsList">
                        Loading projects...
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let currentProject = null;
            
            document.getElementById('projectForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const command = document.getElementById('command').value.trim();
                if (!command) {
                    alert('Please enter a project command');
                    return;
                }
                
                const projectName = document.getElementById('projectName').value.trim();
                const startBtn = document.getElementById('startBtn');
                const status = document.getElementById('status');
                
                startBtn.disabled = true;
                startBtn.textContent = '🔄 Starting Development...';
                status.textContent = 'Initializing development cycle...';
                
                try {
                    const response = await fetch('/api/start-development', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            command: command,
                            project_name: projectName || undefined
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        currentProject = data.data;
                        status.textContent = `✅ Project created successfully!\\n\\nProject: ${data.data.project_name}\\nURL: ${data.data.url}\\nStatus: ${data.data.final_status}\\nIterations: ${data.data.iterations_completed}\\nTotal Time: ${data.data.total_time.toFixed(2)}s`;
                        
                        // Clear form
                        document.getElementById('command').value = '';
                        document.getElementById('projectName').value = '';
                        
                        // Refresh projects list
                        loadProjects();
                    } else {
                        status.textContent = `❌ Error: ${data.message}`;
                    }
                } catch (error) {
                    status.textContent = `❌ Error: ${error.message}`;
                } finally {
                    startBtn.disabled = false;
                    startBtn.textContent = 'Start Development Cycle';
                }
            });
            
            async function loadProjects() {
                try {
                    const response = await fetch('/api/projects');
                    const data = await response.json();
                    
                    const projectsList = document.getElementById('projectsList');
                    
                    if (data.length === 0) {
                        projectsList.innerHTML = 'No active projects';
                        return;
                    }
                    
                    projectsList.innerHTML = data.map(project => `
                        <div class="project-item">
                            <div>
                                <div class="project-name">${project.project_name}</div>
                                <div style="font-size: 12px; opacity: 0.8;">
                                    Phase: ${project.current_phase} | Iteration: ${project.iteration}
                                </div>
                            </div>
                            <div>
                                <span class="project-status status-${project.status}">${project.status}</span>
                                ${project.url ? `<a href="${project.url}" target="_blank" style="color: #60a5fa; margin-left: 10px;">Open</a>` : ''}
                            </div>
                        </div>
                    `).join('');
                } catch (error) {
                    document.getElementById('projectsList').innerHTML = `Error loading projects: ${error.message}`;
                }
            }
            
            // Load projects on page load
            window.onload = function() {
                loadProjects();
            };
        </script>
    </body>
    </html>
    """

@app.post("/api/start-development", response_model=APIResponse)
async def start_development(request: ProjectRequest):
    """Start a new development cycle."""
    try:
        result = await coordinator.start_development_cycle(
            request.command, 
            request.project_name
        )
        return APIResponse(
            status=result["status"],
            message=result.get("message", "Development cycle completed"),
            data=result
        )
    except Exception as e:
        logger.exception("Failed to start development cycle")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects", response_model=List[Dict[str, Any]])
async def list_projects():
    """List all active projects."""
    try:
        projects = await coordinator.list_active_projects()
        return projects
    except Exception as e:
        logger.exception("Failed to list projects")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_name}", response_model=APIResponse)
async def get_project_status(project_name: str):
    """Get status of a specific project."""
    try:
        status = await coordinator.get_project_status(project_name)
        return APIResponse(
            status="success",
            message="Project status retrieved",
            data=status
        )
    except Exception as e:
        logger.exception(f"Failed to get project status for {project_name}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_name}/stop", response_model=APIResponse)
async def stop_project(project_name: str):
    """Stop a project."""
    try:
        result = await coordinator.stop_project(project_name)
        return APIResponse(
            status=result["status"],
            message=result["message"],
            data=result
        )
    except Exception as e:
        logger.exception(f"Failed to stop project {project_name}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_name}/restart", response_model=APIResponse)
async def restart_project(project_name: str):
    """Restart a project."""
    try:
        result = await coordinator.restart_project(project_name)
        return APIResponse(
            status=result["status"],
            message=result["message"],
            data=result
        )
    except Exception as e:
        logger.exception(f"Failed to restart project {project_name}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_name}/test", response_model=APIResponse)
async def run_tests(project_name: str):
    """Run tests on a project."""
    try:
        result = await coordinator.run_additional_tests(project_name)
        return APIResponse(
            status="success",
            message="Tests completed",
            data=result
        )
    except Exception as e:
        logger.exception(f"Failed to run tests for {project_name}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-status", response_model=APIResponse)
async def get_system_status():
    """Get overall system status."""
    try:
        status = await coordinator.get_system_status()
        return APIResponse(
            status="success",
            message="System status retrieved",
            data=status
        )
    except Exception as e:
        logger.exception("Failed to get system status")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cleanup", response_model=APIResponse)
async def cleanup_all():
    """Clean up all projects."""
    try:
        result = await coordinator.cleanup_all()
        return APIResponse(
            status=result["status"],
            message=result["message"],
            data=result
        )
    except Exception as e:
        logger.exception("Failed to cleanup projects")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)