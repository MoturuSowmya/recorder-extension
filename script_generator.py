=#!/usr/bin/env python3
"""
Advanced Script Generator using Gemini API
Generates clean, well-structured scripts based on prompts and saves to files
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai
from datetime import datetime

class ScriptGenerator:
    def __init__(self, api_key: str):
        """Initialize the script generator with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.output_dir = Path("generated_scripts")
        self.output_dir.mkdir(exist_ok=True)
        
    def get_script_generation_prompt(self, language: str) -> str:
        """Get the system prompt for script generation"""
        return f"""You are an expert {language} developer specializing in automation testing and development tools.

Your task is to generate clean, well-structured, production-ready code based on user requirements.

GUIDELINES:
1. Write clean, readable, and maintainable code
2. Include proper error handling and logging
3. Add comprehensive docstrings and comments
4. Follow {language} best practices and conventions
5. Include type hints (Python) or proper typing (TypeScript)
6. Structure code with proper separation of concerns
7. Include import statements for all dependencies
8. Add example usage when appropriate
9. Consider edge cases and validation

OUTPUT FORMAT:
- Provide complete, runnable code
- If multiple files are needed, clearly separate them with "=== FILENAME: <name> ==="
- Include setup/installation instructions if needed
- Add brief explanation of the solution approach

Focus on creating production-ready code that can be used immediately without placeholder implementations."""

    def get_refactoring_prompt(self, language: str) -> str:
        """Get the system prompt for code refactoring"""
        return f"""You are an expert {language} code refactoring specialist.

Your task is to refactor messy, poorly structured code into clean, maintainable, professional-quality code.

REFACTORING PRINCIPLES:
1. Improve code readability and structure
2. Extract reusable functions/classes
3. Apply SOLID principles and design patterns
4. Eliminate code duplication
5. Improve error handling and logging
6. Add proper type hints and documentation
7. Split large files into logical modules when beneficial
8. Preserve all existing functionality
9. Keep all real imports and dependencies (NO mock/placeholder implementations)

STRUCTURAL IMPROVEMENTS:
- Extract configuration into separate files
- Separate business logic from presentation
- Create proper class hierarchies
- Implement proper exception handling
- Add comprehensive logging
- Use dependency injection where appropriate

OUTPUT FORMAT:
- If splitting into multiple files, use "=== FILENAME: <name> ==="
- Provide import/export statements for file relationships
- Include brief explanation of refactoring decisions
- Maintain backward compatibility where possible

IMPORTANT: Never create mock classes or placeholder implementations. Keep all real functionality intact."""

    def generate_script(self, prompt: str, language: str = "python", 
                       task_type: str = "script") -> Dict:
        """Generate a script based on the given prompt"""
        try:
            # Select appropriate system prompt
            if task_type == "refactor":
                system_prompt = self.get_refactoring_prompt(language)
            else:
                system_prompt = self.get_script_generation_prompt(language)
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\nUSER REQUEST:\n{prompt}"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Parse the response to extract files
            files = self.parse_multi_file_response(response.text, language)
            
            return {
                "success": True,
                "files": files,
                "raw_response": response.text,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def parse_multi_file_response(self, response: str, language: str) -> List[Dict]:
        """Parse response that may contain multiple files"""
        files = []
        
        # Check if response contains file separators
        file_pattern = r"=== FILENAME: (.+?) ==="
        file_matches = re.findall(file_pattern, response)
        
        if file_matches:
            # Split response by file separators
            parts = re.split(file_pattern, response)
            
            # First part might contain general explanation
            if parts[0].strip():
                files.append({
                    "filename": "README.md",
                    "content": parts[0].strip(),
                    "type": "documentation"
                })
            
            # Process file pairs (filename, content)
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    filename = parts[i].strip()
                    content = parts[i + 1].strip()
                    
                    # Clean up code blocks
                    content = self.clean_code_content(content)
                    
                    files.append({
                        "filename": filename,
                        "content": content,
                        "type": "code"
                    })
        else:
            # Single file response
            content = self.clean_code_content(response)
            extension = "py" if language == "python" else "ts"
            
            files.append({
                "filename": f"generated_script.{extension}",
                "content": content,
                "type": "code"
            })
        
        return files
    
    def clean_code_content(self, content: str) -> str:
        """Clean up code content by removing markdown formatting"""
        # Remove code block markers
        content = re.sub(r'```\w*\n', '', content)
        content = re.sub(r'```', '', content)
        
        # Remove excessive whitespace
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_lines.append(line.rstrip())
        
        return '\n'.join(cleaned_lines).strip()
    
    def save_files(self, files: List[Dict], project_name: str = None) -> List[str]:
        """Save generated files to disk"""
        if not project_name:
            project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_dir = self.output_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        saved_files = []
        
        for file_info in files:
            file_path = project_dir / file_info["filename"]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info["content"])
            
            saved_files.append(str(file_path))
            print(f"Saved: {file_path}")
        
        return saved_files
    
    def generate_and_save(self, prompt: str, language: str = "python", 
                         task_type: str = "script", project_name: str = None) -> Dict:
        """Generate script and save to files in one operation"""
        result = self.generate_script(prompt, language, task_type)
        
        if result["success"]:
            saved_files = self.save_files(result["files"], project_name)
            result["saved_files"] = saved_files
        
        return result

# Example usage and test cases
def main():
    """Example usage of the ScriptGenerator"""
    # Initialize with your Gemini API key
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    generator = ScriptGenerator(API_KEY)
    
    # Example 1: Generate a flaky test detector (from your automation testing features)
    flaky_test_prompt = """
    Create a Python script that implements a Flaky Test Detector for automation testing.
    
    Requirements:
    - Analyze test execution histories from JSON files
    - Identify tests with inconsistent pass/fail patterns
    - Calculate flakiness percentage for each test
    - Provide natural language explanations for flakiness causes
    - Generate reports with suggested fixes
    - Support configurable flakiness thresholds
    - Include visualization of flaky test trends
    
    The script should be modular, well-documented, and include example usage.
    """
    
    print("Generating Flaky Test Detector...")
    result = generator.generate_and_save(
        flaky_test_prompt, 
        language="python",
        project_name="flaky_test_detector"
    )
    
    if result["success"]:
        print(f"Generated {len(result['files'])} files")
        for file_path in result["saved_files"]:
            print(f"  - {file_path}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Generate test coverage gap analyzer
    coverage_prompt = """
    Create a TypeScript script that implements a Test Coverage Gap Analyzer.
    
    Requirements:
    - Read coverage reports (JSON format)
    - Analyze application source code
    - Identify untested code paths and functions
    - Generate natural language suggestions for new tests
    - Prioritize gaps by risk level (critical, high, medium, low)
    - Export findings to JSON and markdown reports
    - Support integration with popular coverage tools
    
    Use modern TypeScript with proper typing and error handling.
    """
    
    print("\nGenerating Test Coverage Gap Analyzer...")
    result = generator.generate_and_save(
        coverage_prompt,
        language="typescript", 
        project_name="coverage_gap_analyzer"
    )
    
    if result["success"]:
        print(f"Generated {len(result['files'])} files")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
