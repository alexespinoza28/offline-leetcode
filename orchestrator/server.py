"""
HTTP server for the orchestrator.

This module provides a FastAPI-based HTTP server that exposes the orchestrator
functionality via REST API endpoints for the frontend to consume.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from .execution.service import execution_service
from .db.progress import ProgressDB
from .utils.limits import ResourceLimits

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
async def run_code(request: RunRequest, background_tasks: BackgroundTasks):
    """Execute code and return test results."""
    try:
        logger.info(f"Running {request.problem} in {request.lang}")
        
        # Execute code using the execution service
        result = await execution_service.execute_solution(
            code=request.code,
            language=request.lang,
            problem_id=request.problem,
            user_id=None,  # TODO: Add user authentication
            session_id=None  # TODO: Add session management
        )
        
        if result["status"] == "error":
            return RunResponse(
                status="INTERNAL_ERROR",
                logs={"error": result["message"]}
            )
        
        # Convert execution service result to API response format
        test_cases = []
        for test_result in result.get("test_results", []):
            test_cases.append(TestCase(
                id=test_result["test_id"],
                status=test_result["status"],
                time_ms=int(test_result["time_ms"]),
                memory_mb=int(test_result.get("memory_mb", 0)),
                input=test_result["input"],
                expected=test_result["expected_output"],
                actual=test_result["actual_output"],
                diff=test_result.get("diff")
            ))
        
        # Create summary
        passed = result.get("passed_tests", 0)
        total = result.get("total_tests", 0)
        failed = total - passed
        
        summary = TestSummary(
            passed=passed,
            failed=failed,
            total=total,
            time_ms=int(result.get("total_time_ms", 0)),
            memory_mb=int(max((tc.get("memory_mb", 0) for tc in result.get("test_results", [])), default=0))
        )
        
        # Map execution status to API status
        status_mapping = {
            "accepted": "OK",
            "wrong_answer": "WA", 
            "compilation_error": "COMPILE_ERROR",
            "runtime_error": "RUNTIME_ERROR",
            "time_limit_exceeded": "TIME_LIMIT_EXCEEDED",
            "memory_limit_exceeded": "MEMORY_LIMIT_EXCEEDED",
            "internal_error": "INTERNAL_ERROR"
        }
        
        api_status = status_mapping.get(result.get("status", "internal_error"), "INTERNAL_ERROR")
        
        return RunResponse(
            status=api_status,
            summary=summary,
            cases=test_cases,
            logs=result.get("logs", {}),
            explanation=result.get("message")
        )
    
    except Exception as e:
        logger.error(f"Error running code: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute code")


@app.post("/api/validate")
async def validate_syntax(request: dict):
    """Validate code syntax without execution."""
    try:
        code = request.get("code", "")
        language = request.get("lang", "py")
        
        result = await execution_service.validate_syntax(code, language)
        
        return {
            "valid": result["valid"],
            "message": result["message"],
            "language": result["language"]
        }
    
    except Exception as e:
        logger.error(f"Error validating syntax: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate syntax")


@app.get("/api/stats")
async def get_execution_stats():
    """Get execution statistics and system status."""
    try:
        stats = await execution_service.get_execution_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.post("/api/explain")
async def explain_code(request: dict):
    """Generate explanation for code solution."""
    try:
        code = request.get("code", "")
        language = request.get("lang", "py")
        problem = request.get("problem", "")
        
        # TODO: Implement AI-powered code explanation
        # For now, return a basic analysis
        
        explanation = f"""
## Code Analysis

**Language:** {language.upper()}
**Problem:** {problem}

### Algorithm Overview
This solution implements a standard approach to solve the problem.

### Time Complexity
- **Time:** O(n) - Linear time complexity
- **Space:** O(1) - Constant space complexity

### Key Points
1. The solution follows a straightforward approach
2. Edge cases are handled appropriately
3. The implementation is clean and readable

### Suggestions
- Consider adding more comments for clarity
- Test with edge cases to ensure robustness
        """
        
        return {
            "explanation": explanation.strip(),
            "complexity": {
                "time": "O(n)",
                "space": "O(1)"
            },
            "suggestions": [
                "Add more comments for clarity",
                "Test with edge cases",
                "Consider alternative approaches"
            ]
        }
    
    except Exception as e:
        logger.error(f"Error explaining code: {e}")
        raise HTTPException(status_code=500, detail="Failed to explain code")


@app.post("/api/debug")
async def debug_code(request: dict):
    """Debug code and provide suggestions."""
    try:
        code = request.get("code", "")
        language = request.get("lang", "py")
        problem = request.get("problem", "")
        error = request.get("error", "")
        
        # TODO: Implement AI-powered debugging
        # For now, return basic debugging suggestions
        
        suggestions = []
        
        if "syntax" in error.lower() or "compilation" in error.lower():
            suggestions.extend([
                "Check for missing semicolons or brackets",
                "Verify variable declarations",
                "Ensure proper indentation"
            ])
        elif "runtime" in error.lower():
            suggestions.extend([
                "Check for null pointer access",
                "Verify array bounds",
                "Handle edge cases properly"
            ])
        elif "timeout" in error.lower() or "tle" in error.lower():
            suggestions.extend([
                "Optimize algorithm complexity",
                "Avoid nested loops if possible",
                "Use more efficient data structures"
            ])
        else:
            suggestions.extend([
                "Review the problem requirements",
                "Test with sample inputs",
                "Check variable types and ranges"
            ])
        
        return {
            "suggestions": suggestions,
            "common_issues": [
                "Off-by-one errors in loops",
                "Incorrect handling of edge cases",
                "Wrong data type usage"
            ],
            "debugging_tips": [
                "Add print statements to trace execution",
                "Test with minimal examples first",
                "Verify input/output format"
            ]
        }
    
    except Exception as e:
        logger.error(f"Error debugging code: {e}")
        raise HTTPException(status_code=500, detail="Failed to debug code")


@app.get("/api/analytics/problems/{problem_id}")
async def get_problem_analytics(problem_id: str):
    """Get analytics for a specific problem."""
    try:
        analytics = await execution_service.get_problem_analytics(problem_id)
        return analytics
    
    except Exception as e:
        logger.error(f"Error getting problem analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get problem analytics")


@app.get("/api/analytics/languages/{language}")
async def get_language_analytics(language: str):
    """Get analytics for a specific language."""
    try:
        analytics = await execution_service.get_language_analytics(language)
        return analytics
    
    except Exception as e:
        logger.error(f"Error getting language analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get language analytics")


@app.get("/api/results/{execution_id}")
async def get_detailed_results(execution_id: str):
    """Get detailed results for a specific execution."""
    try:
        results = await execution_service.get_detailed_results(execution_id)
        
        if results is None:
            raise HTTPException(status_code=404, detail="Execution results not found")
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detailed results: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detailed results")


@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get overall analytics and insights."""
    try:
        stats = await execution_service.get_execution_stats()
        
        # Add additional insights
        insights = {
            "performance_insights": [],
            "improvement_suggestions": [],
            "trending_problems": [],
            "language_recommendations": []
        }
        
        # Generate insights based on stats
        if "overall_success_rate" in stats:
            success_rate = stats["overall_success_rate"]
            if success_rate < 0.5:
                insights["improvement_suggestions"].append(
                    "Focus on understanding problem requirements before coding"
                )
            elif success_rate > 0.8:
                insights["improvement_suggestions"].append(
                    "Great job! Consider tackling harder problems"
                )
        
        if "average_execution_time" in stats:
            avg_time = stats["average_execution_time"]
            if avg_time > 500:
                insights["performance_insights"].append(
                    "Consider optimizing algorithms for better performance"
                )
            elif avg_time < 100:
                insights["performance_insights"].append(
                    "Excellent performance! Your solutions are efficient"
                )
        
        return {
            "statistics": stats,
            "insights": insights,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics overview")


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )