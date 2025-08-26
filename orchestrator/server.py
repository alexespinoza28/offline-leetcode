"""
HTTP server for the orchestrator.

This module provides a FastAPI-based HTTP server that exposes the orchestrator
functionality via REST API endpoints for the frontend to consume.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Interview Coding Platform API",
    description="Backend API for the coding interview practice platform",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (built frontend)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")


# Request/Response Models
class RunRequest(BaseModel):
    action: str  # "run", "explain", "gen-tests"
    problem: str
    lang: str
    code: str
    tests: Optional[str] = "sample"  # "sample", "unit", "all"


class TestCase(BaseModel):
    id: str
    status: str  # "OK", "WA", "TLE", etc.
    time_ms: Optional[int] = None
    memory_mb: Optional[int] = None
    input: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    diff: Optional[str] = None


class TestSummary(BaseModel):
    passed: int
    failed: int
    total: int
    time_ms: int
    memory_mb: int


class RunResponse(BaseModel):
    status: str  # "OK", "COMPILE_ERROR", "RUNTIME_ERROR", etc.
    summary: Optional[TestSummary] = None
    cases: Optional[List[TestCase]] = None
    logs: Optional[Dict[str, str]] = None
    explanation: Optional[str] = None


class Problem(BaseModel):
    slug: str
    title: str
    difficulty: str
    tags: List[str]
    statement_md: str
    examples: List[Dict[str, str]]
    constraints: List[Dict[str, Any]]


# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "orchestrator"}


@app.get("/api/problems", response_model=List[Problem])
async def get_problems():
    """Get list of all available problems."""
    try:
        problems_dir = Path(__file__).parent.parent / "problems"
        problems = []
        
        if not problems_dir.exists():
            return problems
        
        for problem_dir in problems_dir.iterdir():
            if problem_dir.is_dir():
                problem_json = problem_dir / "problem.json"
                if problem_json.exists():
                    try:
                        with open(problem_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        problems.append(Problem(
                            slug=data.get("slug", problem_dir.name),
                            title=data.get("title", ""),
                            difficulty=data.get("difficulty", "Medium"),
                            tags=data.get("tags", []),
                            statement_md=data.get("statement_md", ""),
                            examples=data.get("examples", []),
                            constraints=data.get("constraints", [])
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to load problem {problem_dir.name}: {e}")
        
        # Sort by difficulty and title
        difficulty_order = {"Easy": 0, "Medium": 1, "Hard": 2}
        problems.sort(key=lambda p: (difficulty_order.get(p.difficulty, 1), p.title))
        
        return problems
    
    except Exception as e:
        logger.error(f"Error loading problems: {e}")
        raise HTTPException(status_code=500, detail="Failed to load problems")


@app.get("/api/problems/{slug}", response_model=Problem)
async def get_problem(slug: str):
    """Get a specific problem by slug."""
    try:
        problem_dir = Path(__file__).parent.parent / "problems" / slug
        problem_json = problem_dir / "problem.json"
        
        if not problem_json.exists():
            raise HTTPException(status_code=404, detail="Problem not found")
        
        with open(problem_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Problem(
            slug=data.get("slug", slug),
            title=data.get("title", ""),
            difficulty=data.get("difficulty", "Medium"),
            tags=data.get("tags", []),
            statement_md=data.get("statement_md", ""),
            examples=data.get("examples", []),
            constraints=data.get("constraints", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading problem {slug}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load problem")


@app.get("/api/problems/{slug}/solution/{lang}")
async def get_solution(slug: str, lang: str):
    """Get the current solution code for a problem in a specific language."""
    try:
        problem_dir = Path(__file__).parent.parent / "problems" / slug
        solution_dir = problem_dir / "solutions" / lang
        
        # Map language to entry file
        entry_files = {
            "c": "main.c",
            "cpp": "main.cpp", 
            "py": "main.py",
            "js": "main.js",
            "java": "Main.java"
        }
        
        entry_file = entry_files.get(lang)
        if not entry_file:
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        solution_file = solution_dir / entry_file
        
        if solution_file.exists():
            with open(solution_file, 'r', encoding='utf-8') as f:
                code = f.read()
        else:
            # Return template code if solution doesn't exist
            template_dir = Path(__file__).parent.parent / "templates" / lang
            template_file = template_dir / entry_file
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    code = f.read()
            else:
                code = f"// Template for {lang} not found"
        
        return {"code": code}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading solution {slug}/{lang}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load solution")


@app.post("/api/run", response_model=RunResponse)
async def run_code(request: RunRequest):
    """Execute code and return test results."""
    try:
        # TODO: Implement actual orchestrator integration
        # For now, return a mock response
        
        logger.info(f"Running {request.problem} in {request.lang}")
        
        # Mock response for development
        return RunResponse(
            status="OK",
            summary=TestSummary(
                passed=2,
                failed=0,
                total=2,
                time_ms=45,
                memory_mb=12
            ),
            cases=[
                TestCase(
                    id="sample_1",
                    status="OK",
                    time_ms=23,
                    memory_mb=8,
                    input="[2,7,11,15]\n9",
                    expected="[0,1]",
                    actual="[0,1]"
                ),
                TestCase(
                    id="sample_2", 
                    status="OK",
                    time_ms=22,
                    memory_mb=4,
                    input="[3,2,4]\n6",
                    expected="[1,2]",
                    actual="[1,2]"
                )
            ],
            logs={
                "compile": "Compilation successful",
                "stderr": ""
            }
        )
    
    except Exception as e:
        logger.error(f"Error running code: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute code")


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )