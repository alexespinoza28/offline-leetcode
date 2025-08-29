#!/usr/bin/env python3
"""
Language template manager for switching between programming languages.

This module handles the creation and management of language-specific
template files for coding problems.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class LanguageTemplateManager:
    """
    Manager for language template operations.
    
    Handles switching between programming languages for problems,
    creating template files, and managing language-specific configurations.
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """Initialize the template manager."""
        self.templates_dir = Path(templates_dir)
        self.language_configs = self._load_language_configs()
    
    def _load_language_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load language-specific configurations."""
        return {
            "python": {
                "extension": ".py",
                "template": "def solution():\\n    pass\\n\\nif __name__ == '__main__':\\n    # Test code here\\n    pass",
                "comment_style": "#",
                "main_function": "solution"
            },
            "cpp": {
                "extension": ".cpp",
                "template": "#include <iostream>\\n#include <vector>\\nusing namespace std;\\n\\nclass Solution {\\npublic:\\n    // Your solution here\\n};\\n\\nint main() {\\n    // Test code here\\n    return 0;\\n}",
                "comment_style": "//",
                "main_function": "Solution"
            },
            "java": {
                "extension": ".java",
                "template": "public class Solution {\\n    public void solution() {\\n        // Your solution here\\n    }\\n    \\n    public static void main(String[] args) {\\n        // Test code here\\n    }\\n}",
                "comment_style": "//",
                "main_function": "solution"
            },
            "javascript": {
                "extension": ".js",
                "template": "function solution() {\\n    // Your solution here\\n}\\n\\n// Test code\\nif (require.main === module) {\\n    // Test code here\\n}",
                "comment_style": "//",
                "main_function": "solution"
            }
        }
    
    def switch_language(self, problem_slug: str, from_lang: str, to_lang: str, 
                       preserve_logic: bool = True) -> Dict[str, Any]:
        """
        Switch a problem from one language to another.
        
        Args:
            problem_slug: The problem identifier
            from_lang: Source language
            to_lang: Target language
            preserve_logic: Whether to attempt to preserve existing logic
            
        Returns:
            Dictionary with switch operation results
        """
        try:
            # Validate languages
            if from_lang not in self.language_configs:
                raise ValueError(f"Unsupported source language: {from_lang}")
            if to_lang not in self.language_configs:
                raise ValueError(f"Unsupported target language: {to_lang}")
            
            # Get language configurations
            from_config = self.language_configs[from_lang]
            to_config = self.language_configs[to_lang]
            
            # Create template for target language
            template_content = self._generate_template(problem_slug, to_lang, to_config)
            
            # If preserve_logic is True, attempt to extract and convert logic
            if preserve_logic:
                existing_code = self._read_existing_code(problem_slug, from_lang)
                if existing_code:
                    converted_code = self._convert_logic(existing_code, from_lang, to_lang)
                    template_content = converted_code
            
            # Write new template file
            success = self._write_template_file(problem_slug, to_lang, template_content)
            
            return {
                "problem": problem_slug,
                "from_lang": from_lang,
                "to_lang": to_lang,
                "template_updated": success,
                "template_path": str(self._get_template_path(problem_slug, to_lang)),
                "preserved_logic": preserve_logic and existing_code is not None
            }
            
        except Exception as e:
            return {
                "problem": problem_slug,
                "from_lang": from_lang,
                "to_lang": to_lang,
                "template_updated": False,
                "error": str(e)
            }
    
    def _generate_template(self, problem_slug: str, language: str, config: Dict[str, Any]) -> str:
        """Generate template content for a specific language."""
        template = config["template"]
        comment_style = config["comment_style"]
        
        # Add problem-specific comments
        header = f"{comment_style} Problem: {problem_slug}\\n{comment_style} Language: {language}\\n\\n"
        
        return header + template
    
    def _read_existing_code(self, problem_slug: str, language: str) -> Optional[str]:
        """Read existing code file if it exists."""
        try:
            file_path = self._get_template_path(problem_slug, language)
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
        except Exception:
            pass
        return None
    
    def _convert_logic(self, code: str, from_lang: str, to_lang: str) -> str:
        """Attempt to convert logic between languages (basic implementation)."""
        # This is a simplified conversion - in practice, this would be much more sophisticated
        to_config = self.language_configs[to_lang]
        
        # Start with the target language template
        converted = self._generate_template("", to_lang, to_config)
        
        # Add a comment about the conversion
        comment_style = to_config["comment_style"]
        conversion_note = f"\\n{comment_style} Converted from {from_lang}\\n{comment_style} Original logic preserved below:\\n\\n"
        
        # For now, just add the original code as comments
        original_as_comments = "\\n".join([f"{comment_style} {line}" for line in code.split("\\n")])
        
        return converted + conversion_note + original_as_comments
    
    def _write_template_file(self, problem_slug: str, language: str, content: str) -> bool:
        """Write template file to disk."""
        try:
            file_path = self._get_template_path(problem_slug, language)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception:
            return False
    
    def _get_template_path(self, problem_slug: str, language: str) -> Path:
        """Get the file path for a template."""
        config = self.language_configs[language]
        extension = config["extension"]
        return self.templates_dir / problem_slug / f"solution{extension}"
    
    def get_supported_languages(self) -> list:
        """Get list of supported programming languages."""
        return list(self.language_configs.keys())
    
    def create_problem_templates(self, problem_slug: str, languages: list = None) -> Dict[str, bool]:
        """Create template files for a problem in multiple languages."""
        if languages is None:
            languages = self.get_supported_languages()
        
        results = {}
        for language in languages:
            if language in self.language_configs:
                config = self.language_configs[language]
                content = self._generate_template(problem_slug, language, config)
                success = self._write_template_file(problem_slug, language, content)
                results[language] = success
            else:
                results[language] = False
        
        return results
    
    def get_template_info(self, problem_slug: str, language: str) -> Dict[str, Any]:
        """Get information about a template file."""
        try:
            file_path = self._get_template_path(problem_slug, language)
            config = self.language_configs.get(language, {})
            
            return {
                "problem": problem_slug,
                "language": language,
                "file_path": str(file_path),
                "exists": file_path.exists(),
                "extension": config.get("extension", ""),
                "main_function": config.get("main_function", ""),
                "comment_style": config.get("comment_style", "")
            }
        except Exception as e:
            return {
                "problem": problem_slug,
                "language": language,
                "error": str(e)
            }