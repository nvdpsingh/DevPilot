"""
Main entry point for the Multi-Agent Development System.
"""
import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

app = typer.Typer()

@app.command()
def server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False
):
    """Start the development server."""
    console.print(Panel.fit(
        Text("Multi-Agent Development System", style="bold blue"),
        title="🚀 Starting Server",
        border_style="blue"
    ))
    
    console.print(f"🌐 Server starting on {host}:{port}")
    console.print(f"🔄 Reload: {'Enabled' if reload else 'Disabled'}")
    console.print(f"📱 Open: http://{host}:{port}")
    
    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=reload
    )

@app.command()
def demo():
    """Run a demo development cycle."""
    import asyncio
    from src.agents.coordinator_agent import CoordinatorAgent
    
    async def run_demo():
        console.print(Panel.fit(
            Text("Running Demo Development Cycle", style="bold green"),
            title="🎯 Demo",
            border_style="green"
        ))
        
        coordinator = CoordinatorAgent()
        
        # Demo command
        command = "Build a simple todo app with add, edit, delete functionality"
        project_name = "demo_todo_app"
        
        console.print(f"📋 Command: {command}")
        console.print(f"🏗️ Project: {project_name}")
        console.print("🔄 Starting development cycle...")
        
        result = await coordinator.start_development_cycle(command, project_name)
        
        if result["status"] == "success":
            console.print(Panel.fit(
                Text(f"✅ Demo completed successfully!\\n\\nProject: {result['project_name']}\\nURL: {result['url']}\\nIterations: {result['iterations_completed']}\\nTime: {result['total_time']:.2f}s", style="green"),
                title="🎉 Success",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                Text(f"❌ Demo failed: {result.get('message', 'Unknown error')}", style="red"),
                title="💥 Error",
                border_style="red"
            ))
    
    asyncio.run(run_demo())

if __name__ == "__main__":
    app()
