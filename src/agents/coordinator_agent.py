"""
Coordinator Agent - Orchestrates the entire multi-agent development process.
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from .planner_agent import PlannerAgent
from .react_agent import ReactAgent
from .deployer_agent import DeployerAgent
from .tester_agent import TesterAgent

class CoordinatorAgent:
    """Main coordinator that orchestrates all agents in the development process."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.react = ReactAgent()
        self.deployer = DeployerAgent()
        self.tester = TesterAgent()
        
        self.active_projects = {}  # Track active projects
        self.max_iterations = 5  # Maximum iterations for the loop
    
    async def start_development_cycle(self, command: str, project_name: str = None) -> Dict[str, Any]:
        """Start the complete development cycle."""
        
        if not project_name:
            project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🎯 Coordinator: Starting development cycle for '{command}'")
        
        # Initialize project tracking
        self.active_projects[project_name] = {
            "command": command,
            "status": "starting",
            "current_phase": "planning",
            "iteration": 0,
            "start_time": time.time(),
            "history": []
        }
        
        try:
            # Phase 1: Planning
            print(f"📋 Phase 1: Planning project {project_name}")
            plan_result = await self.planner.create_project_plan(command, project_name)
            
            if plan_result["status"] != "success":
                return await self._handle_error(project_name, "Planning failed", plan_result)
            
            self.active_projects[project_name]["current_phase"] = "planning_complete"
            self.active_projects[project_name]["plan_id"] = plan_result["plan_id"]
            
            # Phase 2: Initial Development
            print(f"🔧 Phase 2: Creating project {project_name}")
            dev_result = await self.react.create_project_from_plan(plan_result["plan_id"])
            
            if dev_result["status"] != "success":
                return await self._handle_error(project_name, "Development failed", dev_result)
            
            self.active_projects[project_name]["current_phase"] = "development_complete"
            
            # Phase 3: Initial Deployment
            print(f"🚀 Phase 3: Deploying project {project_name}")
            deploy_result = await self.deployer.deploy_project(project_name)
            
            if deploy_result["status"] != "success":
                return await self._handle_error(project_name, "Deployment failed", deploy_result)
            
            self.active_projects[project_name]["current_phase"] = "deployed"
            self.active_projects[project_name]["url"] = deploy_result["url"]
            
            # Phase 4: Iterative Testing and Fixing
            print(f"🔄 Phase 4: Starting iterative testing and fixing for {project_name}")
            iteration_result = await self._run_iterative_cycle(project_name)
            
            # Final status
            self.active_projects[project_name]["status"] = "completed"
            self.active_projects[project_name]["end_time"] = time.time()
            
            return {
                "status": "success",
                "project_name": project_name,
                "url": deploy_result["url"],
                "plan_id": plan_result["plan_id"],
                "iterations_completed": iteration_result["iterations"],
                "final_status": iteration_result["final_status"],
                "total_time": time.time() - self.active_projects[project_name]["start_time"],
                "message": "Development cycle completed successfully"
            }
            
        except Exception as e:
            return await self._handle_error(project_name, f"Unexpected error: {str(e)}", {})
    
    async def _run_iterative_cycle(self, project_name: str) -> Dict[str, Any]:
        """Run the iterative testing and fixing cycle."""
        
        iteration = 0
        max_iterations = self.max_iterations
        all_tests_passed = False
        
        while iteration < max_iterations and not all_tests_passed:
            iteration += 1
            print(f"🔄 Iteration {iteration} for {project_name}")
            
            # Test the project
            test_result = await self.tester.test_project(project_name)
            
            # Record iteration
            self.active_projects[project_name]["history"].append({
                "iteration": iteration,
                "test_result": test_result,
                "timestamp": time.time()
            })
            
            # Check if all tests passed
            if test_result.get("overall_status") == "all_passed":
                all_tests_passed = True
                print(f"✅ All tests passed in iteration {iteration}")
                break
            
            # Get feedback for fixing
            feedback = await self.tester.get_feedback_for_react_agent(project_name)
            
            # Fix issues based on feedback
            if test_result.get("overall_status") in ["failed", "partial_pass"]:
                print(f"🔧 Fixing issues in iteration {iteration}")
                
                # Get the main file to fix
                main_file = "main.py"
                feedback_text = "\\n".join(feedback)
                
                fix_result = await self.react.fix_file_based_on_feedback(
                    project_name, main_file, feedback_text
                )
                
                if fix_result["status"] == "success":
                    # Restart the project with fixes
                    restart_result = await self.deployer.restart_project(project_name)
                    if restart_result["status"] != "success":
                        print(f"⚠️ Failed to restart project: {restart_result['message']}")
                else:
                    print(f"⚠️ Failed to fix file: {fix_result['message']}")
            
            # Wait a moment before next iteration
            await asyncio.sleep(2)
        
        return {
            "iterations": iteration,
            "final_status": "all_passed" if all_tests_passed else "max_iterations_reached",
            "all_tests_passed": all_tests_passed
        }
    
    async def _handle_error(self, project_name: str, error_message: str, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors in the development process."""
        
        self.active_projects[project_name]["status"] = "error"
        self.active_projects[project_name]["error"] = error_message
        self.active_projects[project_name]["error_details"] = error_details
        self.active_projects[project_name]["end_time"] = time.time()
        
        print(f"❌ Error in {project_name}: {error_message}")
        
        return {
            "status": "error",
            "project_name": project_name,
            "error": error_message,
            "error_details": error_details,
            "message": "Development cycle failed"
        }
    
    async def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get the current status of a project."""
        
        if project_name not in self.active_projects:
            return {
                "status": "not_found",
                "message": f"Project {project_name} not found"
            }
        
        project_info = self.active_projects[project_name]
        
        # Get deployment status
        deploy_status = await self.deployer.get_project_status(project_name)
        
        return {
            "project_name": project_name,
            "status": project_info["status"],
            "current_phase": project_info["current_phase"],
            "iteration": project_info["iteration"],
            "deployment_status": deploy_status,
            "start_time": project_info["start_time"],
            "history": project_info["history"]
        }
    
    async def list_active_projects(self) -> List[Dict[str, Any]]:
        """List all active projects."""
        
        projects = []
        for project_name, project_info in self.active_projects.items():
            deploy_status = await self.deployer.get_project_status(project_name)
            projects.append({
                "project_name": project_name,
                "status": project_info["status"],
                "current_phase": project_info["current_phase"],
                "iteration": project_info["iteration"],
                "deployment_status": deploy_status["status"],
                "url": deploy_status.get("url"),
                "start_time": project_info["start_time"]
            })
        
        return projects
    
    async def stop_project(self, project_name: str) -> Dict[str, Any]:
        """Stop a project and clean up."""
        
        if project_name not in self.active_projects:
            return {
                "status": "error",
                "message": f"Project {project_name} not found"
            }
        
        # Stop deployment
        deploy_result = await self.deployer.stop_project(project_name)
        
        # Update project status
        self.active_projects[project_name]["status"] = "stopped"
        self.active_projects[project_name]["end_time"] = time.time()
        
        return {
            "status": "success",
            "project_name": project_name,
            "deploy_result": deploy_result,
            "message": "Project stopped successfully"
        }
    
    async def restart_project(self, project_name: str) -> Dict[str, Any]:
        """Restart a project."""
        
        if project_name not in self.active_projects:
            return {
                "status": "error",
                "message": f"Project {project_name} not found"
            }
        
        # Restart deployment
        restart_result = await self.deployer.restart_project(project_name)
        
        if restart_result["status"] == "success":
            self.active_projects[project_name]["status"] = "running"
            self.active_projects[project_name]["current_phase"] = "deployed"
        
        return restart_result
    
    async def run_additional_tests(self, project_name: str) -> Dict[str, Any]:
        """Run additional tests on a project."""
        
        if project_name not in self.active_projects:
            return {
                "status": "error",
                "message": f"Project {project_name} not found"
            }
        
        # Run tests
        test_result = await self.tester.test_project(project_name)
        
        # Record the test
        self.active_projects[project_name]["history"].append({
            "iteration": "additional",
            "test_result": test_result,
            "timestamp": time.time()
        })
        
        return test_result
    
    async def cleanup_all(self) -> Dict[str, Any]:
        """Clean up all projects."""
        
        print("🧹 Coordinator: Cleaning up all projects")
        
        # Stop all deployments
        deploy_result = await self.deployer.cleanup_all()
        
        # Clear active projects
        self.active_projects.clear()
        
        return {
            "status": "success",
            "message": "All projects cleaned up",
            "deploy_result": deploy_result
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the overall system status."""
        
        active_count = len(self.active_projects)
        running_count = 0
        
        for project_name in self.active_projects:
            deploy_status = await self.deployer.get_project_status(project_name)
            if deploy_status["status"] == "running":
                running_count += 1
        
        return {
            "active_projects": active_count,
            "running_projects": running_count,
            "max_iterations": self.max_iterations,
            "agents": {
                "planner": "active",
                "react": "active", 
                "deployer": "active",
                "tester": "active"
            }
        }
