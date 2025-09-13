# 🤖 Multi-Agent Development System

An AI-powered development system with iterative testing and fixing capabilities. The system uses multiple specialized agents that work together to plan, develop, deploy, and continuously improve projects.

## 🏗️ Architecture

### Agents

1. **Planner Agent** 🧠
   - Creates detailed project plans using AI
   - Saves plans to JSON documents for iteration
   - Analyzes requirements and generates technical specifications

2. **React Agent** 🔧
   - Reads plans and creates real project files
   - Can fix files based on test feedback
   - Generates Python, HTML, CSS, and JavaScript code

3. **Deployer Agent** 🚀
   - Handles local deployment of projects
   - Manages process lifecycle (start, stop, restart)
   - Monitors project health and status

4. **Tester Agent** 🧪
   - Integrates with TestSprite for automated testing
   - Runs local pytest tests
   - Provides feedback for code improvements

5. **Coordinator Agent** 🎯
   - Orchestrates the entire development process
   - Manages the iterative loop: Plan → Code → Deploy → Test → Fix → Repeat
   - Tracks project status and history

## 🔄 Development Cycle

1. **Planning Phase**: Planner Agent creates a detailed project plan
2. **Development Phase**: React Agent creates real project files
3. **Deployment Phase**: Deployer Agent starts the project locally
4. **Testing Phase**: Tester Agent runs tests using TestSprite
5. **Iteration Phase**: If tests fail, React Agent fixes issues and the cycle repeats
6. **Completion**: Project is ready when all tests pass

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Start the Server

```bash
python main.py server
```

### 4. Open the Web UI

Visit http://localhost:8000 to access the web interface.

## 🎯 Usage

### Web Interface

1. Enter a project command (e.g., "Build a task management app")
2. Optionally specify a project name
3. Click "Start Development Cycle"
4. Watch the agents work through the development process
5. Access your deployed project when ready

### Command Line

```bash
# Start the server
python main.py server

# Run a demo
python main.py demo
```

### API Endpoints

- `POST /api/start-development` - Start a new development cycle
- `GET /api/projects` - List all active projects
- `GET /api/projects/{name}` - Get project status
- `POST /api/projects/{name}/stop` - Stop a project
- `POST /api/projects/{name}/restart` - Restart a project
- `POST /api/projects/{name}/test` - Run tests on a project
- `GET /api/system-status` - Get system status

## 📁 Project Structure

```
custom_projects/          # Generated projects
├── project_name/
│   ├── main.py          # FastAPI application
│   ├── requirements.txt # Dependencies
│   ├── index.html       # Frontend
│   ├── style.css        # Styles
│   ├── script.js        # JavaScript
│   ├── tests/           # Test files
│   └── README.md        # Documentation

project_plans/           # Project plans
├── project_name_plan.json

test_results/            # Test results
├── project_name_test_timestamp.json
```

## 🔧 Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key for AI functionality
- `TESTSPRITE_API_KEY`: Your TestSprite API key
- `TESTSPRITE_MCP_URL`: TestSprite MCP server URL (default: http://localhost:3000)
- `PROJECTS_DIR`: Directory for generated projects (default: custom_projects)
- `PLANS_DIR`: Directory for project plans (default: project_plans)

### TestSprite Integration

The system integrates with TestSprite for automated testing:

1. Start TestSprite MCP server
2. Configure `TESTSPRITE_API_KEY` and `TESTSPRITE_MCP_URL`
3. The Tester Agent will automatically use TestSprite for testing

## 🎨 Features

- **Real File Creation**: Creates actual project files, not simulations
- **Iterative Development**: Continuously tests and fixes code
- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Web Interface**: Easy-to-use web UI for project management
- **TestSprite Integration**: Automated testing with feedback
- **Local Deployment**: Deploy and test projects locally
- **Project Tracking**: Monitor project status and history

## 🔍 How It Works

1. **User Input**: User provides a project command
2. **Planning**: Planner Agent creates a detailed plan using AI
3. **File Creation**: React Agent generates real project files
4. **Deployment**: Deployer Agent starts the project locally
5. **Testing**: Tester Agent runs tests using TestSprite
6. **Feedback Loop**: If tests fail, React Agent fixes issues and the cycle repeats
7. **Completion**: Project is ready when all tests pass

## 🛠️ Development

### Adding New Agents

1. Create a new agent class in `src/agents/`
2. Implement the required methods
3. Add the agent to the Coordinator Agent
4. Update the API endpoints if needed

### Customizing the Development Cycle

Modify the `CoordinatorAgent` class to customize the development process:

- Change the number of iterations
- Add new phases
- Modify the testing strategy
- Customize the feedback loop

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support, please open an issue on GitHub or contact the development team.
