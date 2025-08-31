# Interview Coding Platform

An offline-first, dockerized, multi-language interview coding platform with VS Code integration.

## Features

- **Offline-First**: Complete functionality without internet connectivity
- **Multi-Language Support**: C, C++, Python 3, Node.js, Java
- **VS Code Integration**: Custom extension with problems tree and result panels
- **Automated Testing**: Sample, unit, and hidden test execution with multiple comparison modes
- **Resource Limits**: Time, memory, and process limits for secure code execution
- **Progress Tracking**: SQLite-based analytics and performance metrics
- **Git Integration**: Pre-commit validation and GitHub Actions CI
- **Community Problem Packs**: Installable problem sets with proper versioning
- **Explanation Engine**: Template-based and community-contributed explanations

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd interview-coding-platform

# Start the platform
docker-compose -f docker/docker-compose.yml up

# Access VS Code in your browser
open http://localhost:8080
```

### Local Development

```bash
# Install dependencies
cd orchestrator && pip install -r requirements.txt
cd ../vscode-extension && npm install

# Build the extension
npm run compile
```

### Starting the Backend

If you are developing locally and not using Docker, you can start the backend server using the provided script:

```bash
./start_backend.sh
```

This script will start the backend server in the background. You will see the Process ID (PID) of the server, which you can use to stop it later with `kill <PID>`. The backend server will be accessible at `http://0.0.0.0:8000`.

## Project Structure

```
interview-coding-platform/
├── docker/                     # Docker configuration
├── vscode-extension/           # VS Code extension source
├── orchestrator/               # Python backend services
│   ├── language_adapters/      # Language-specific compilation/execution
│   ├── testing/               # Test engine and comparators
│   ├── explain/               # Explanation generation
│   ├── db/                    # Progress tracking database
│   └── utils/                 # Utility functions
├── problems/                   # Problem definitions and solutions
├── templates/                  # Language starter templates
├── tools/                     # CLI utilities
└── .github/                   # CI/CD workflows
```

## Usage

1. **Browse Problems**: Use the Problems tree view in VS Code sidebar
2. **Select Language**: Right-click problem → Switch Language
3. **Write Solution**: Edit the solution file in your chosen language
4. **Run Tests**: Right-click problem → Run Tests
5. **Get Explanations**: Right-click problem → Explain Solution
6. **Track Progress**: View results in the integrated panel

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding problems and contributing to the platform.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
