"""
Tester Agent - Handles testing using TestSprite and provides feedback.
"""
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx

class TesterAgent:
    """Agent responsible for testing projects using TestSprite."""
    
    def __init__(self):
        self.projects_dir = Path("custom_projects")
        self.testsprite_url = "http://localhost:3000"  # TestSprite MCP URL
        self.test_results_dir = Path("test_results")
        self.test_results_dir.mkdir(exist_ok=True)
    
    async def test_project(self, project_name: str) -> Dict[str, Any]:
        """Test a project using TestSprite."""
        
        print(f"🧪 Tester Agent: Testing {project_name}")
        
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            return {
                "status": "error",
                "message": f"Project {project_name} not found"
            }
        
        # Check if project is running
        health_check = await self._check_project_health(project_name)
        if not health_check["healthy"]:
            return {
                "status": "error",
                "message": f"Project {project_name} is not running or unhealthy"
            }
        
        # Run local tests first
        local_test_result = await self._run_local_tests(project_path)
        
        # Run TestSprite tests
        testsprite_result = await self._run_testsprite_tests(project_name, project_path)
        
        # Combine results
        combined_result = {
            "status": "success",
            "project_name": project_name,
            "local_tests": local_test_result,
            "testsprite_tests": testsprite_result,
            "overall_status": self._determine_overall_status(local_test_result, testsprite_result),
            "feedback": self._generate_feedback(local_test_result, testsprite_result)
        }
        
        # Save test results
        await self._save_test_results(project_name, combined_result)
        
        return combined_result
    
    async def _check_project_health(self, project_name: str) -> Dict[str, Any]:
        """Check if the project is running and healthy."""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8001/api/health", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "healthy": True,
                        "response": data
                    }
                else:
                    return {
                        "healthy": False,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _run_local_tests(self, project_path: Path) -> Dict[str, Any]:
        """Run local pytest tests."""
        
        print(f"🔍 Running local tests for {project_path.name}")
        
        tests_dir = project_path / "tests"
        if not tests_dir.exists():
            return {
                "status": "skipped",
                "message": "No tests directory found"
            }
        
        try:
            # Run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "status": "completed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "Tests timed out"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _run_testsprite_tests(self, project_name: str, project_path: Path) -> Dict[str, Any]:
        """Run tests using TestSprite MCP server."""
        
        print(f"🎯 Running TestSprite tests for {project_name}")
        
        try:
            # Check if TestSprite MCP is available
            async with httpx.AsyncClient() as client:
                # Test connection
                try:
                    response = await client.get(f"{self.testsprite_url}/health", timeout=5)
                    if response.status_code != 200:
                        return {
                            "status": "unavailable",
                            "message": "TestSprite MCP server not responding"
                        }
                except:
                    return {
                        "status": "unavailable",
                        "message": "TestSprite MCP server not available"
                    }
                
                # Generate test cases using TestSprite
                test_generation = await self._generate_test_cases(project_name, project_path)
                
                # Run the generated tests
                test_execution = await self._execute_test_cases(project_name, test_generation)
                
                return {
                    "status": "completed",
                    "test_generation": test_generation,
                    "test_execution": test_execution,
                    "success": test_execution.get("success", False)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"TestSprite testing failed: {str(e)}"
            }
    
    async def _generate_test_cases(self, project_name: str, project_path: Path) -> Dict[str, Any]:
        """Generate test cases using TestSprite."""
        
        try:
            # Read project files to understand the structure
            main_py = project_path / "main.py"
            if main_py.exists():
                main_content = main_py.read_text()
            else:
                main_content = ""
            
            # Create test generation request
            test_request = {
                "project_name": project_name,
                "project_type": "fastapi",
                "main_file_content": main_content,
                "test_requirements": [
                    "Test all API endpoints",
                    "Test error handling",
                    "Test response formats",
                    "Test health checks"
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.testsprite_url}/generate-tests",
                    json=test_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "test_cases": response.json(),
                        "message": "Test cases generated successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Test generation failed: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"Test generation failed: {str(e)}"
            }
    
    async def _execute_test_cases(self, project_name: str, test_generation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generated test cases."""
        
        try:
            if test_generation.get("status") != "success":
                return {
                    "status": "skipped",
                    "message": "No test cases to execute"
                }
            
            # Create a test execution request
            execution_request = {
                "project_name": project_name,
                "test_cases": test_generation.get("test_cases", []),
                "target_url": "http://localhost:8001"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.testsprite_url}/execute-tests",
                    json=execution_request,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "results": result,
                        "success": result.get("passed", 0) > 0,
                        "message": f"Tests executed: {result.get('passed', 0)} passed, {result.get('failed', 0)} failed"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Test execution failed: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"Test execution failed: {str(e)}"
            }
    
    def _determine_overall_status(self, local_tests: Dict[str, Any], testsprite_tests: Dict[str, Any]) -> str:
        """Determine the overall test status."""
        
        local_success = local_tests.get("success", False)
        testsprite_success = testsprite_tests.get("success", False)
        
        if local_success and testsprite_success:
            return "all_passed"
        elif local_success or testsprite_success:
            return "partial_pass"
        else:
            return "failed"
    
    def _generate_feedback(self, local_tests: Dict[str, Any], testsprite_tests: Dict[str, Any]) -> List[str]:
        """Generate feedback for the React Agent."""
        
        feedback = []
        
        # Local test feedback
        if local_tests.get("status") == "completed":
            if local_tests.get("success"):
                feedback.append("✅ Local tests passed successfully")
            else:
                feedback.append("❌ Local tests failed - check test output for details")
                if local_tests.get("stderr"):
                    feedback.append(f"Error details: {local_tests['stderr'][:200]}...")
        elif local_tests.get("status") == "skipped":
            feedback.append("⚠️ No local tests found - consider adding test files")
        
        # TestSprite feedback
        if testsprite_tests.get("status") == "completed":
            if testsprite_tests.get("success"):
                feedback.append("✅ TestSprite tests passed successfully")
            else:
                feedback.append("❌ TestSprite tests failed - check API implementation")
        elif testsprite_tests.get("status") == "unavailable":
            feedback.append("⚠️ TestSprite not available - using local tests only")
        
        # Overall feedback
        overall_status = self._determine_overall_status(local_tests, testsprite_tests)
        if overall_status == "all_passed":
            feedback.append("🎉 All tests passed! Project is ready for production.")
        elif overall_status == "partial_pass":
            feedback.append("⚠️ Some tests passed, but improvements needed.")
        else:
            feedback.append("🚨 Tests failed - code needs fixes before deployment.")
        
        return feedback
    
    async def _save_test_results(self, project_name: str, results: Dict[str, Any]) -> None:
        """Save test results to a file."""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.test_results_dir / f"{project_name}_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Test results saved to: {results_file}")
    
    async def get_test_history(self, project_name: str) -> List[Dict[str, Any]]:
        """Get test history for a project."""
        
        history = []
        pattern = f"{project_name}_test_*.json"
        
        for results_file in self.test_results_dir.glob(pattern):
            with open(results_file, 'r') as f:
                result = json.load(f)
                history.append({
                    "timestamp": results_file.stem.split("_test_")[1],
                    "overall_status": result.get("overall_status"),
                    "local_tests": result.get("local_tests", {}).get("success"),
                    "testsprite_tests": result.get("testsprite_tests", {}).get("success")
                })
        
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)
    
    async def get_feedback_for_react_agent(self, project_name: str) -> List[str]:
        """Get specific feedback for the React Agent to fix issues."""
        
        # Get the latest test results
        history = await self.get_test_history(project_name)
        if not history:
            return ["No test history available"]
        
        latest_result = history[0]
        
        feedback = []
        
        if latest_result["overall_status"] == "failed":
            feedback.append("Code has critical issues that need immediate fixing")
            feedback.append("Check API endpoints and error handling")
            feedback.append("Verify all imports and dependencies are correct")
        elif latest_result["overall_status"] == "partial_pass":
            feedback.append("Some functionality works but needs improvement")
            feedback.append("Review failed test cases and fix accordingly")
        else:
            feedback.append("Code is working well, consider adding more features")
        
        return feedback
