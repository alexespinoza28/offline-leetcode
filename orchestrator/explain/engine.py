#!/usr/bin/env python3
"""
Explanation engine for generating solution explanations.

This module provides functionality to generate detailed explanations
for coding solutions, including algorithm analysis, complexity analysis,
and step-by-step breakdowns using template-based rendering.
"""

import json
import re
import ast
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from .template_loader import TemplateLoader

logger = logging.getLogger(__name__)


class ExplanationEngine:
    """
    Engine for generating solution explanations.
    
    Provides detailed explanations of coding solutions including:
    - Template-based explanation generation
    - Algorithm pattern recognition
    - Code analysis and complexity estimation
    - Variable substitution in templates
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the explanation engine.
        
        Args:
            templates_dir: Directory containing explanation templates
        """
        self.template_loader = TemplateLoader(templates_dir) if templates_dir else TemplateLoader()
        self.code_analyzer = CodeAnalyzer()
    

    
    def generate_explanation(self, problem_slug: str, language: str, code: str = None, 
                           tags: List[str] = None, difficulty: str = None) -> str:
        """
        Generate a detailed explanation for a solution using templates.
        
        Args:
            problem_slug: The problem identifier
            language: Programming language of the solution
            code: Optional source code to analyze
            tags: Problem tags for template selection
            difficulty: Problem difficulty level
            
        Returns:
            Detailed explanation string
        """
        try:
            # Find the best matching template
            template_name = self.template_loader.find_template(
                problem_slug, tags, difficulty
            )
            
            if not template_name:
                logger.warning(f"No template found for problem: {problem_slug}")
                return self._generate_fallback_explanation(problem_slug, language, code)
            
            # Analyze code if provided
            code_analysis = {}
            if code:
                code_analysis = self.code_analyzer.analyze_code(code, language)
            
            # Prepare template variables
            variables = self._prepare_template_variables(
                problem_slug, language, code, code_analysis, tags, difficulty
            )
            
            # Render template with variables
            explanation = self.template_loader.render_template(template_name, variables)
            
            # Add code-specific insights if available
            if code_analysis:
                explanation += self._add_code_insights(code_analysis, language)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation for {problem_slug}: {e}")
            return self._generate_fallback_explanation(problem_slug, language, code)
    
    def _prepare_template_variables(self, problem_slug: str, language: str, 
                                  code: str, code_analysis: Dict[str, Any],
                                  tags: List[str] = None, difficulty: str = None) -> Dict[str, Any]:
        """
        Prepare variables for template substitution.
        
        Args:
            problem_slug: Problem identifier
            language: Programming language
            code: Source code
            code_analysis: Results from code analysis
            tags: Problem tags
            difficulty: Problem difficulty
            
        Returns:
            Dictionary of template variables
        """
        variables = {
            'problem_slug': problem_slug,
            'language': language,
            'difficulty': difficulty or 'medium',
            'tags': ', '.join(tags) if tags else 'general',
        }
        
        # Add code analysis results
        if code_analysis:
            variables.update({
                'time_complexity': code_analysis.get('time_complexity', 'O(n)'),
                'space_complexity': code_analysis.get('space_complexity', 'O(1)'),
                'algorithm_type': code_analysis.get('algorithm_type', 'iterative'),
                'data_structures': ', '.join(code_analysis.get('data_structures', [])),
                'patterns': ', '.join(code_analysis.get('patterns', [])),
                'key_operations': code_analysis.get('key_operations', []),
            })
        
        return variables
    
    def _generate_fallback_explanation(self, problem_slug: str, language: str, code: str = None) -> str:
        """Generate a basic explanation when no template is found."""
        explanation = f"# Solution Explanation for {problem_slug}\\n\\n"
        explanation += f"## Language: {language}\\n\\n"
        
        if code:
            code_analysis = self.code_analyzer.analyze_code(code, language)
            explanation += f"## Algorithm Analysis\\n"
            explanation += f"- **Time Complexity**: {code_analysis.get('time_complexity', 'O(n)')}\\n"
            explanation += f"- **Space Complexity**: {code_analysis.get('space_complexity', 'O(1)')}\\n"
            explanation += f"- **Algorithm Type**: {code_analysis.get('algorithm_type', 'iterative')}\\n\\n"
            
            if code_analysis.get('patterns'):
                explanation += f"## Detected Patterns\\n"
                for pattern in code_analysis['patterns']:
                    explanation += f"- {pattern}\\n"
                explanation += "\\n"
        
        explanation += "## General Approach\\n"
        explanation += "This solution implements a systematic approach to solve the problem "
        explanation += "using appropriate data structures and algorithms.\\n\\n"
        
        return explanation
    
    def _add_code_insights(self, code_analysis: Dict[str, Any], language: str) -> str:
        """Add code-specific insights to the explanation."""
        insights = "\\n## Code Analysis Insights\\n\\n"
        
        # Data structures used
        if code_analysis.get('data_structures'):
            insights += "### Data Structures Used\\n"
            for ds in code_analysis['data_structures']:
                insights += f"- **{ds}**: Provides efficient operations for this problem type\\n"
            insights += "\\n"
        
        # Algorithm patterns
        if code_analysis.get('patterns'):
            insights += "### Algorithm Patterns\\n"
            for pattern in code_analysis['patterns']:
                insights += f"- {pattern}\\n"
            insights += "\\n"
        
        # Language-specific optimizations
        if language == 'python':
            insights += "### Python-Specific Features\\n"
            insights += "- Uses Python's built-in data structures for optimal performance\\n"
            insights += "- Leverages list comprehensions and built-in functions where appropriate\\n"
        elif language == 'cpp':
            insights += "### C++ Specific Features\\n"
            insights += "- Uses STL containers and algorithms for efficiency\\n"
            insights += "- Optimized for performance with minimal overhead\\n"
        
        return insights
    
    def explain_with_examples(self, problem_slug: str, language: str, 
                            code: str = None, examples: list = None) -> str:
        """Generate explanation with example walkthroughs."""
        base_explanation = self.generate_explanation(problem_slug, language, code)
        
        if examples:
            example_section = "\\n## Example Walkthroughs\\n"
            for i, example in enumerate(examples, 1):
                example_section += f"\\n### Example {i}\\n"
                example_section += f"Input: {example.get('input', 'N/A')}\\n"
                example_section += f"Output: {example.get('output', 'N/A')}\\n"
                example_section += f"Explanation: {example.get('explanation', 'Step-by-step execution of the algorithm')}\\n"
            
            return base_explanation + example_section
        
        return base_explanation
    
    def get_hints(self, problem_slug: str, difficulty_level: str = "medium") -> list:
        """Generate progressive hints for a problem."""
        # Basic hint system
        hints = [
            "Think about the most efficient data structure for this problem",
            "Consider the time complexity requirements",
            "Look for patterns in the input/output examples",
            "Think about edge cases and how to handle them"
        ]
        
        problem_type = self._analyze_problem_type(problem_slug)
        
        # Add problem-type specific hints
        type_hints = {
            "array": ["Consider using two pointers or sliding window", "Hash maps can provide O(1) lookups"],
            "string": ["Think about character frequency or pattern matching", "Consider string manipulation techniques"],
            "tree": ["Think about tree traversal methods (DFS/BFS)", "Consider recursive vs iterative approaches"],
            "graph": ["Consider graph traversal algorithms", "Think about visited node tracking"],
            "dynamic_programming": ["Look for overlapping subproblems", "Consider memoization or tabulation"],
            "binary_search": ["Think about the search space and how to eliminate half", "Consider the invariant conditions"]
        }
        
        if problem_type in type_hints:
            hints.extend(type_hints[problem_type])
        
        return hints[:4]  # Return first 4 hints
cla
ss CodeAnalyzer:
    """
    Analyzes source code to extract algorithmic patterns and complexity information.
    """
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.pattern_matchers = {
            'python': self._analyze_python_code,
            'cpp': self._analyze_cpp_code,
            'java': self._analyze_java_code,
            'javascript': self._analyze_javascript_code,
        }
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code to extract patterns, complexity, and data structures.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Get language-specific analyzer
            analyzer = self.pattern_matchers.get(language.lower(), self._analyze_generic_code)
            
            # Perform analysis
            analysis = analyzer(code)
            
            # Add general analysis
            analysis.update(self._analyze_general_patterns(code))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return self._get_default_analysis()
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python-specific code patterns."""
        analysis = {
            'language': 'python',
            'data_structures': [],
            'patterns': [],
            'algorithm_type': 'iterative',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)'
        }
        
        # Detect data structures
        if 'dict(' in code or '{' in code and ':' in code:
            analysis['data_structures'].append('dictionary')
        if 'set(' in code or 'set()' in code:
            analysis['data_structures'].append('set')
        if 'list(' in code or '[' in code:
            analysis['data_structures'].append('list')
        if 'deque' in code:
            analysis['data_structures'].append('deque')
        if 'heapq' in code:
            analysis['data_structures'].append('heap')
        
        # Detect patterns
        if 'left' in code and 'right' in code:
            analysis['patterns'].append('Two Pointers')
        if 'dp[' in code or 'memo' in code:
            analysis['patterns'].append('Dynamic Programming')
        if 'queue' in code and 'append' in code and 'popleft' in code:
            analysis['patterns'].append('BFS')
        if 'stack' in code or ('append' in code and 'pop()' in code):
            analysis['patterns'].append('DFS/Stack')
        if 'sliding' in code or ('window' in code):
            analysis['patterns'].append('Sliding Window')
        
        # Detect recursion
        if 'def ' in code and code.count('def ') > 1:
            # Check if function calls itself
            func_names = re.findall(r'def (\w+)', code)
            for func_name in func_names:
                if func_name in code.split('def ' + func_name)[1:]:
                    analysis['algorithm_type'] = 'recursive'
                    break
        
        # Estimate complexity
        nested_loops = code.count('for ') + code.count('while ')
        if nested_loops > 1:
            analysis['time_complexity'] = 'O(n²)'
        elif 'sort' in code:
            analysis['time_complexity'] = 'O(n log n)'
        elif 'binary' in code or 'bisect' in code:
            analysis['time_complexity'] = 'O(log n)'
        
        # Space complexity
        if analysis['data_structures'] or 'dp[' in code:
            analysis['space_complexity'] = 'O(n)'
        elif analysis['algorithm_type'] == 'recursive':
            analysis['space_complexity'] = 'O(h)'  # height of recursion
        
        return analysis
    
    def _analyze_cpp_code(self, code: str) -> Dict[str, Any]:
        """Analyze C++-specific code patterns."""
        analysis = {
            'language': 'cpp',
            'data_structures': [],
            'patterns': [],
            'algorithm_type': 'iterative',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)'
        }
        
        # Detect STL containers
        if 'vector' in code:
            analysis['data_structures'].append('vector')
        if 'unordered_map' in code or 'map' in code:
            analysis['data_structures'].append('hash_map')
        if 'unordered_set' in code or 'set' in code:
            analysis['data_structures'].append('set')
        if 'queue' in code:
            analysis['data_structures'].append('queue')
        if 'stack' in code:
            analysis['data_structures'].append('stack')
        if 'priority_queue' in code:
            analysis['data_structures'].append('heap')
        
        # Detect patterns
        if 'left' in code and 'right' in code:
            analysis['patterns'].append('Two Pointers')
        if 'dp[' in code:
            analysis['patterns'].append('Dynamic Programming')
        if 'queue' in code and 'push' in code and 'pop' in code:
            analysis['patterns'].append('BFS')
        if 'stack' in code:
            analysis['patterns'].append('DFS/Stack')
        
        # Detect recursion
        if code.count('return ') > 1 and ('left' in code or 'right' in code):
            analysis['algorithm_type'] = 'recursive'
        
        # Estimate complexity
        nested_loops = code.count('for(') + code.count('for (') + code.count('while(') + code.count('while (')
        if nested_loops > 1:
            analysis['time_complexity'] = 'O(n²)'
        elif 'sort' in code:
            analysis['time_complexity'] = 'O(n log n)'
        elif 'binary_search' in code:
            analysis['time_complexity'] = 'O(log n)'
        
        # Space complexity
        if analysis['data_structures'] or 'dp[' in code:
            analysis['space_complexity'] = 'O(n)'
        elif analysis['algorithm_type'] == 'recursive':
            analysis['space_complexity'] = 'O(h)'
        
        return analysis
    
    def _analyze_java_code(self, code: str) -> Dict[str, Any]:
        """Analyze Java-specific code patterns."""
        analysis = {
            'language': 'java',
            'data_structures': [],
            'patterns': [],
            'algorithm_type': 'iterative',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)'
        }
        
        # Detect Java collections
        if 'ArrayList' in code or 'List' in code:
            analysis['data_structures'].append('list')
        if 'HashMap' in code or 'Map' in code:
            analysis['data_structures'].append('hash_map')
        if 'HashSet' in code or 'Set' in code:
            analysis['data_structures'].append('set')
        if 'Queue' in code:
            analysis['data_structures'].append('queue')
        if 'Stack' in code:
            analysis['data_structures'].append('stack')
        if 'PriorityQueue' in code:
            analysis['data_structures'].append('heap')
        
        # Similar pattern detection as other languages
        if 'left' in code and 'right' in code:
            analysis['patterns'].append('Two Pointers')
        if 'dp[' in code:
            analysis['patterns'].append('Dynamic Programming')
        
        return analysis
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript-specific code patterns."""
        analysis = {
            'language': 'javascript',
            'data_structures': [],
            'patterns': [],
            'algorithm_type': 'iterative',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)'
        }
        
        # Detect JavaScript data structures
        if 'Array' in code or '[' in code:
            analysis['data_structures'].append('array')
        if 'Map' in code or 'new Map' in code:
            analysis['data_structures'].append('map')
        if 'Set' in code or 'new Set' in code:
            analysis['data_structures'].append('set')
        if '{}' in code:
            analysis['data_structures'].append('object')
        
        # Pattern detection
        if 'left' in code and 'right' in code:
            analysis['patterns'].append('Two Pointers')
        if 'dp[' in code:
            analysis['patterns'].append('Dynamic Programming')
        
        return analysis
    
    def _analyze_generic_code(self, code: str) -> Dict[str, Any]:
        """Generic code analysis for unsupported languages."""
        return {
            'language': 'generic',
            'data_structures': [],
            'patterns': [],
            'algorithm_type': 'iterative',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)'
        }
    
    def _analyze_general_patterns(self, code: str) -> Dict[str, Any]:
        """Analyze general algorithmic patterns regardless of language."""
        patterns = []
        
        # Loop patterns
        loop_count = len(re.findall(r'\b(for|while)\b', code, re.IGNORECASE))
        if loop_count > 1:
            patterns.append('Nested Iteration')
        elif loop_count == 1:
            patterns.append('Single Loop')
        
        # Conditional patterns
        if_count = len(re.findall(r'\bif\b', code, re.IGNORECASE))
        if if_count > 3:
            patterns.append('Complex Conditional Logic')
        
        # Mathematical operations
        if any(op in code for op in ['+', '-', '*', '/', '%', '**', 'pow']):
            patterns.append('Mathematical Operations')
        
        # String operations
        if any(op in code for op in ['substring', 'substr', 'slice', 'split', 'join']):
            patterns.append('String Manipulation')
        
        return {'general_patterns': patterns}
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when code analysis fails."""
        return {
            'language': 'unknown',
            'data_structures': [],
            'patterns': [],
            'algorithm_type': 'iterative',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'general_patterns': []
        }