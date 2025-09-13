"""
Deployer Agent - Handles local deployment of projects.
"""
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import psutil

class DeployerAgent:
    """Agent responsible for deploying projects locally."""
    
    def __init__(self):
        self.projects_dir = Path("custom_projects")
        self.running_processes = {}  # Track running processes
    
    async def deploy_project(self, project_name: str) -> Dict[str, Any]:
        """Deploy a project locally."""
        
        print(f"🚀 Deployer Agent: Deploying {project_name}")
        
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            return {
                "status": "error",
                "message": f"Project {project_name} not found"
            }
        
        # Stop existing process if running
        await self.stop_project(project_name)
        
        # Install dependencies
        install_result = await self._install_dependencies(project_path)
        if not install_result["success"]:
            return {
                "status": "error",
                "message": f"Failed to install dependencies: {install_result['error']}"
            }
        
        # Start the application
        start_result = await self._start_application(project_path, project_name)
        
        return {
            "status": "success" if start_result["success"] else "error",
            "project_name": project_name,
            "url": f"http://localhost:8001",
            "pid": start_result.get("pid"),
            "message": start_result["message"]
        }
    
    async def _install_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Install project dependencies."""
        
        print(f"📦 Installing dependencies for {project_path.name}")
        
        try:
            # Check if requirements.txt exists
            requirements_file = project_path / "requirements.txt"
            if not requirements_file.exists():
                return {
                    "success": True,
                    "message": "No requirements.txt found, skipping installation"
                }
            
            # Install dependencies
            result = subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Dependencies installed successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_application(self, project_path: Path, project_name: str) -> Dict[str, Any]:
        """Start the application process."""
        
        print(f"▶️ Starting application {project_name}")
        
        try:
            # Start the application in background
            process = subprocess.Popen(
                ["python", "main.py"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for startup
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                # Store process info
                self.running_processes[project_name] = {
                    "process": process,
                    "pid": process.pid,
                    "start_time": time.time(),
                    "project_path": str(project_path)
                }
                
                return {
                    "success": True,
                    "pid": process.pid,
                    "message": f"Application started successfully on port 8001"
                }
            else:
                # Process exited, get error
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "message": f"Application failed to start: {stderr}",
                    "stdout": stdout,
                    "stderr": stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start application: {str(e)}"
            }
    
    async def stop_project(self, project_name: str) -> Dict[str, Any]:
        """Stop a running project."""
        
        print(f"⏹️ Stopping project {project_name}")
        
        if project_name in self.running_processes:
            process_info = self.running_processes[project_name]
            process = process_info["process"]
            
            try:
                # Terminate the process
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop
                    process.kill()
                    process.wait()
                
                # Remove from tracking
                del self.running_processes[project_name]
                
                return {
                    "status": "success",
                    "message": f"Project {project_name} stopped successfully"
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to stop project: {str(e)}"
                }
        else:
            return {
                "status": "success",
                "message": f"Project {project_name} was not running"
            }
    
    async def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get the status of a project."""
        
        if project_name in self.running_processes:
            process_info = self.running_processes[project_name]
            process = process_info["process"]
            
            if process.poll() is None:
                # Process is running
                return {
                    "status": "running",
                    "pid": process_info["pid"],
                    "url": "http://localhost:8001",
                    "start_time": process_info["start_time"],
                    "uptime": time.time() - process_info["start_time"]
                }
            else:
                # Process has stopped
                del self.running_processes[project_name]
                return {
                    "status": "stopped",
                    "message": "Process has stopped"
                }
        else:
            return {
                "status": "not_running",
                "message": "Project is not running"
            }
    
    async def list_running_projects(self) -> List[Dict[str, Any]]:
        """List all running projects."""
        
        running_projects = []
        
        for project_name, process_info in self.running_processes.items():
            process = process_info["process"]
            
            if process.poll() is None:
                running_projects.append({
                    "project_name": project_name,
                    "pid": process_info["pid"],
                    "url": "http://localhost:8001",
                    "start_time": process_info["start_time"],
                    "uptime": time.time() - process_info["start_time"]
                })
            else:
                # Clean up stopped processes
                del self.running_processes[project_name]
        
        return running_projects
    
    async def restart_project(self, project_name: str) -> Dict[str, Any]:
        """Restart a project."""
        
        print(f"🔄 Restarting project {project_name}")
        
        # Stop the project
        stop_result = await self.stop_project(project_name)
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Start the project
        project_path = self.projects_dir / project_name
        start_result = await self._start_application(project_path, project_name)
        
        return {
            "status": "success" if start_result["success"] else "error",
            "project_name": project_name,
            "restart_successful": start_result["success"],
            "message": start_result["message"]
        }
    
    async def check_health(self, project_name: str) -> Dict[str, Any]:
        """Check the health of a running project."""
        
        if project_name not in self.running_processes:
            return {
                "status": "error",
                "message": "Project is not running"
            }
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8001/api/health", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "healthy",
                        "response": data,
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "message": "Health check failed"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {str(e)}"
            }
    
    async def cleanup_all(self):
        """Stop all running projects."""
        
        print("🧹 Cleaning up all running projects")
        
        for project_name in list(self.running_processes.keys()):
            await self.stop_project(project_name)
        
        return {
            "status": "success",
            "message": "All projects stopped"
        }

# Import asyncio at the top level
import asyncio
