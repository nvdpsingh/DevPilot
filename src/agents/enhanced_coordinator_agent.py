"""
Enhanced Coordinator Agent - Orchestrates the complete development workflow with GitHub integration.
"""
import asyncio
import time
from typing import Dict, Any, List
from pathlib import Path
import json

from .planner_agent import PlannerAgent
from .react_agent import ReactAgent
from .deployer_agent import DeployerAgent
from .tester_agent import TesterAgent
from ..services.github_service import GitHubService
from ..services.ai_service import ai_service

class EnhancedCoordinatorAgent:
    """Enhanced coordinator that manages the complete development lifecycle."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.react = ReactAgent()
        self.deployer = DeployerAgent()
        self.tester = TesterAgent()
        self.github = GitHubService()
        self.active_projects = {}
    
    async def start_advanced_development(
        self, 
        command: str, 
        project_name: str,
        project_type: str = "web-app",
        tech_stack: str = "react-node"
    ) -> Dict[str, Any]:
        """Start the complete development workflow with GitHub integration."""
        
        start_time = time.time()
        project_id = f"project_{int(time.time())}"
        
        try:
            # Initialize project tracking
            self.active_projects[project_name] = {
                "status": "starting",
                "current_phase": "planning",
                "iteration": 0,
                "start_time": start_time,
                "project_type": project_type,
                "tech_stack": tech_stack,
                "command": command,
                "github_repo": None,
                "pages_url": None,
                "local_url": None
            }
            
            # Phase 1: AI Planning
            print(f"🧠 Phase 1: AI Planning for {project_name}")
            self.active_projects[project_name]["current_phase"] = "planning"
            
            plan_result = await self.planner.create_project_plan(command, project_name)
            if plan_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"Planning failed: {plan_result['message']}"
                }
            
            # Phase 2: Create Functional Application
            print(f"💻 Phase 2: Creating functional application for {project_name}")
            self.active_projects[project_name]["current_phase"] = "coding"
            
            app_result = await self.github.create_functional_app(
                project_name, project_type, tech_stack, command
            )
            
            if app_result["status"] != "success":
                return {
                    "status": "error", 
                    "message": f"App creation failed: {app_result['message']}"
                }
            
            # Phase 3: Create GitHub Repository
            print(f"📦 Phase 3: Creating GitHub repository for {project_name}")
            self.active_projects[project_name]["current_phase"] = "github_setup"
            
            repo_result = await self.github.create_repository(
                project_name,
                f"AI-Generated {project_type.title()}: {command}",
                is_public=True
            )
            
            if repo_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"GitHub repository creation failed: {repo_result['message']}"
                }
            
            self.active_projects[project_name]["github_repo"] = repo_result["repository_url"]
            
            # Phase 4: Push to GitHub
            print(f"🚀 Phase 4: Pushing code to GitHub for {project_name}")
            self.active_projects[project_name]["current_phase"] = "github_push"
            
            project_path = Path("custom_projects") / project_name
            push_result = await self.github.push_to_github(
                project_path, 
                repo_result["clone_url"], 
                project_name
            )
            
            if push_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"GitHub push failed: {push_result['message']}"
                }
            
            # Phase 5: Setup GitHub Pages
            print(f"🌐 Phase 5: Setting up GitHub Pages for {project_name}")
            self.active_projects[project_name]["current_phase"] = "pages_setup"
            
            pages_result = await self.github.setup_github_pages(project_name)
            
            if pages_result["status"] == "success":
                self.active_projects[project_name]["pages_url"] = pages_result["pages_url"]
            
            # Phase 6: Local Deployment
            print(f"🏠 Phase 6: Local deployment for {project_name}")
            self.active_projects[project_name]["current_phase"] = "deployment"
            
            deploy_result = await self.deployer.deploy_project(project_name)
            
            if deploy_result["status"] == "success":
                self.active_projects[project_name]["local_url"] = deploy_result["url"]
                self.active_projects[project_name]["status"] = "deployed"
            else:
                self.active_projects[project_name]["status"] = "deployed_with_issues"
            
            # Phase 7: Testing
            print(f"🧪 Phase 7: Testing {project_name}")
            self.active_projects[project_name]["current_phase"] = "testing"
            
            test_result = await self.tester.test_project(project_name)
            
            # Phase 8: Iterative Improvement
            print(f"🔄 Phase 8: Iterative improvement for {project_name}")
            self.active_projects[project_name]["current_phase"] = "improvement"
            
            max_iterations = 3
            for iteration in range(max_iterations):
                self.active_projects[project_name]["iteration"] = iteration + 1
                
                print(f"🔄 Iteration {iteration + 1} for {project_name}")
                
                # Test the project
                test_result = await self.tester.test_project(project_name)
                
                if test_result["status"] == "success" and test_result.get("all_tests_passed", False):
                    print(f"✅ All tests passed for {project_name}")
                    break
                
                # Fix issues if any
                if test_result.get("issues"):
                    print(f"🔧 Fixing issues in iteration {iteration + 1}")
                    fix_result = await self.react.fix_project_issues(
                        project_name, 
                        test_result["issues"]
                    )
                    
                    if fix_result["status"] == "success":
                        # Push fixes to GitHub
                        push_result = await self.github.push_to_github(
                            project_path,
                            repo_result["clone_url"],
                            project_name
                        )
            
            # Final status update
            self.active_projects[project_name]["status"] = "completed"
            self.active_projects[project_name]["current_phase"] = "completed"
            
            total_time = time.time() - start_time
            
            return {
                "status": "success",
                "message": "Advanced development cycle completed successfully",
                "data": {
                    "project_name": project_name,
                    "project_type": project_type,
                    "tech_stack": tech_stack,
                    "github_repo": repo_result["repository_url"],
                    "pages_url": self.active_projects[project_name].get("pages_url"),
                    "local_url": self.active_projects[project_name].get("local_url"),
                    "status": "completed",
                    "iterations_completed": self.active_projects[project_name]["iteration"],
                    "total_time": total_time,
                    "files_created": app_result.get("files_created", [])
                }
            }
            
        except Exception as e:
            self.active_projects[project_name]["status"] = "error"
            return {
                "status": "error",
                "message": f"Development cycle failed: {str(e)}"
            }
    
    async def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get the current status of a project."""
        
        if project_name not in self.active_projects:
            return {
                "status": "error",
                "message": "Project not found"
            }
        
        project = self.active_projects[project_name]
        
        return {
            "status": "success",
            "data": {
                "project_name": project_name,
                "status": project["status"],
                "current_phase": project["current_phase"],
                "iteration": project["iteration"],
                "github_repo": project.get("github_repo"),
                "pages_url": project.get("pages_url"),
                "local_url": project.get("local_url"),
                "project_type": project.get("project_type"),
                "tech_stack": project.get("tech_stack"),
                "command": project.get("command")
            }
        }
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all active projects."""
        
        projects = []
        for project_name, project_data in self.active_projects.items():
            projects.append({
                "project_name": project_name,
                "status": project_data["status"],
                "current_phase": project_data["current_phase"],
                "iteration": project_data["iteration"],
                "github_repo": project_data.get("github_repo"),
                "pages_url": project_data.get("pages_url"),
                "local_url": project_data.get("local_url"),
                "project_type": project_data.get("project_type"),
                "tech_stack": project_data.get("tech_stack")
            })
        
        return projects
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        
        total_projects = len(self.active_projects)
        active_projects = len([p for p in self.active_projects.values() if p["status"] in ["starting", "deployed", "deployed_with_issues"]])
        completed_projects = len([p for p in self.active_projects.values() if p["status"] == "completed"])
        deployed_projects = len([p for p in self.active_projects.values() if p.get("local_url")])
        
        success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 100
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "deployed_projects": deployed_projects,
            "success_rate": f"{success_rate:.1f}%"
        }
