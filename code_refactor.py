#!/usr/bin/env python3
"""
Advanced Code Refactoring Tool using Gemini API
Refactors messy code into clean, maintainable, well-structured code
"""

import os
import ast
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai
from datetime import datetime

class CodeRefactorer:
    def __init__(self, api_key: str):
        """Initialize the code refactorer with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.output_dir = Path("refactored_code")
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_code_structure(self, code: str, language: str) -> Dict:
        """Analyze code structure to provide context for refactoring"""
        analysis = {
            "language": language,
            "lines_of_code": len(code.split('\n')),
            "complexity_indicators": [],
            "imports": [],
            "functions": [],
            "classes": []
        }
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            analysis["imports"].append(f"{node.module}.{', '.join([alias.name for alias in node.names])}")
                    elif isinstance(node, ast.FunctionDef):
                        analysis["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        analysis["classes"].append(node.name)
            except SyntaxError:
                analysis["complexity_indicators"].append("Syntax errors present")
        
        # General complexity indicators
        if analysis["lines_of_code"] > 500:
            analysis["complexity_indicators"].append("Large file (>500 lines)")
        if len(analysis["functions"]) > 20:
            analysis["complexity_indicators"].append("Many functions (>20)")
        if len(analysis["classes"]) > 10:
            analysis["complexity_indicators"].append("Many classes (>10)")
        
        # Check for code smells
        if "TODO" in code or "FIXME" in code:
            analysis["complexity_indicators"].append("Contains TODO/FIXME comments")
        if code.count("except:") > 0:
            analysis["complexity_indicators"].append("Bare except clauses found")
        if len(re.findall(r'def \w+\(.*\):(?:\s*\n)*(?:\s{4,}.*\n){20,}', code)) > 0:
            analysis["complexity_indicators"].append("Very long functions detected")
            
        return analysis
    
    def get_refactoring_system_prompt(self, language: str, analysis: Dict) -> str:
        """Generate contextual system prompt based on code analysis"""
        base_prompt = f"""You are an expert {language} code refactoring specialist with deep knowledge of software engineering best practices.

ANALYSIS OF CURRENT CODE:
- Language: {analysis['language']}
- Lines of code: {analysis['lines_of_code']}
- Functions: {len(analysis['functions'])}
- Classes: {len(analysis['classes'])}
- Complexity indicators: {', '.join(analysis['complexity_indicators']) if analysis['complexity_indicators'] else 'None detected'}
- Imports detected: {', '.join(analysis['imports'][:10])}{'...' if len(analysis['imports']) > 10 else ''}

REFACTORING OBJECTIVES:
1. **Structure & Organization**: Break down large functions/classes into smaller, focused units
2. **Code Quality**: Eliminate code smells, improve readability, add proper error handling
3. **Maintainability**: Apply SOLID principles, design patterns, and clean architecture
4. **Documentation**: Add comprehensive docstrings, type hints, and meaningful comments
5. **Performance**: Optimize where possible without sacrificing readability
6. **Testing**: Make code more testable through dependency injection and modular design

SPECIFIC REFACTORING RULES:
✅ DO:
- Preserve ALL existing functionality and behavior
- Keep all real imports and dependencies intact
- Split large files into logical modules when beneficial
- Extract reusable components and utilities
- Implement proper exception handling and logging
- Add type hints and comprehensive documentation
- Follow {language} conventions and best practices
- Create configuration files for constants and settings
- Use dependency injection for better testability

❌ DON'T:
- Create mock classes or placeholder implementations
- Remove or change existing functionality
- Add external dependencies not already present
- Break backward compatibility
- Create overly complex abstractions

FILE ORGANIZATION:
If splitting into multiple files, use this format:
=== FILENAME: main_module.{('py' if language == 'python' else 'ts')} ===
[main code]

=== FILENAME: config.{('py' if language == 'python' else 'ts')} ===
[configuration constants]

=== FILENAME: utils.{('py' if language == 'python' else 'ts')} ===
[utility functions]

=== FILENAME: models.{('py' if language == 'python' else 'ts')} ===
[data models/classes]

RESPONSE FORMAT:
1. Brief explanation of refactoring approach and key improvements
2. Refactored code (single file or multiple files with clear separators)
3. Summary of changes made and benefits achieved
"""
        return base_prompt
    
    def refactor_code(self, code: str, language: str = "python", 
                     filename: str = None) -> Dict:
        """Refactor the given code"""
        try:
            # Analyze code structure first
            analysis = self.analyze_code_structure(code, language)
            
            # Generate contextual system prompt
            system_prompt = self.get_refactoring_system_prompt(language, analysis)
            
            # Create the refactoring request
            user_prompt = f"""Please refactor the following {language} code:

FILENAME: {filename or f'code.{("py" if language == "python" else "ts")}'}

```{language}
{code}
```

Focus on the complexity indicators identified: {', '.join(analysis['complexity_indicators']) if analysis['complexity_indicators'] else 'General code improvement'}

Please provide clean, production-ready refactored code that maintains all existing functionality."""
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate refactored code
            response = self.model.generate_content(full_prompt)
            
            # Parse the response
            files = self.parse_refactored_response(response.text, language)
            
            return {
                "success": True,
                "original_analysis": analysis,
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
    
    def parse_refactored_response(self, response: str, language: str) -> List[Dict]:
        """Parse refactored code response that may contain multiple files"""
        files = []
        
        # Check for file separators
        file_pattern = r"=== FILENAME: (.+?) ==="
        file_matches = re.findall(file_pattern, response)
        
        if file_matches:
            # Multiple files
            parts = re.split(file_pattern, response)
            
            # First part contains explanation
            if parts[0].strip():
                explanation = self.extract_explanation(parts[0])
                if explanation:
                    files.append({
                        "filename": "REFACTORING_NOTES.md",
                        "content": explanation,
                        "type": "documentation"
                    })
            
            # Process file pairs
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    filename = parts[i].strip()
                    content = parts[i + 1].strip()
                    
                    # Clean and validate code
                    content = self.clean_and_validate_code(content, language)
                    
                    files.append({
                        "filename": filename,
                        "content": content,
                        "type": "code"
                    })
        else:
            # Single file with embedded explanation
            explanation, code = self.separate_explanation_and_code(response)
            
            if explanation:
                files.append({
                    "filename": "REFACTORING_NOTES.md",
                    "content": explanation,
                    "type": "documentation"
                })
            
            if code:
                extension = "py" if language == "python" else "ts"
                files.append({
                    "filename": f"refactored_code.{extension}",
                    "content": self.clean_and_validate_code(code, language),
                    "type": "code"
                })
        
        return files
    
    def extract_explanation(self, text: str) -> str:
        """Extract explanation text from response"""
        # Remove code blocks and clean up explanation
        explanation = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        explanation = explanation.strip()
        
        if len(explanation) > 50:  # Only return substantial explanations
            return f"# Refactoring Notes\n\n{explanation}"
        return ""
    
    def separate_explanation_and_code(self, response: str) -> Tuple[str, str]:
        """Separate explanation from code in a single response"""
        code_blocks = re.findall(r'```\w*\n(.*?)```', response, re.DOTALL)
        
        if code_blocks:
            # Largest code block is likely the main code
            code = max(code_blocks, key=len).strip()
            
            # Everything else is explanation
            explanation = re.sub(r'```.*?```', '', response, flags=re.DOTALL).strip()
            
            return explanation, code
        
        # If no code blocks, treat entire response as code
        return "", response.strip()
    
    def clean_and_validate_code(self, code: str, language: str) -> str:
        """Clean and validate refactored code"""
        # Remove markdown code block markers
        code = re.sub(r'```\w*\n?', '', code)
        code = re.sub(r'```', '', code)
        
        # Remove excessive blank lines
        lines = code.split('\n')
        cleaned_lines = []
        blank_count = 0
        
        for line in lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:  # Allow max 2 consecutive blank lines
                    cleaned_lines.append('')
            else:
                blank_count = 0
                cleaned_lines.append(line.rstrip())
        
        # Remove trailing blank lines
        while cleaned_lines and cleaned_lines[-1] == '':
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def refactor_file(self, file_path: str, language: str = None) -> Dict:
        """Refactor code from a file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Auto-detect language if not provided
        if not language:
            if file_path.suffix == '.py':
                language = 'python'
            elif file_path.suffix in ['.ts', '.js']:
                language = 'typescript'
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_path.suffix}"
                }
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {e}"
            }
        
        # Refactor the code
        return self.refactor_code(code, language, file_path.name)
    
    def save_refactored_files(self, files: List[Dict], project_name: str = None) -> List[str]:
        """Save refactored files to disk"""
        if not project_name:
            project_name = f"refactored_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
    
    def refactor_and_save(self, code: str, language: str = "python", 
                         filename: str = None, project_name: str = None) -> Dict:
        """Refactor code and save results in one operation"""
        result = self.refactor_code(code, language, filename)
        
        if result["success"]:
            saved_files = self.save_refactored_files(result["files"], project_name)
            result["saved_files"] = saved_files
            
            # Print summary
            print(f"\n=== Refactoring Summary ===")
            print(f"Original complexity indicators: {', '.join(result['original_analysis']['complexity_indicators'])}")
            print(f"Generated {len(result['files'])} files")
            print(f"Reduced from {result['original_analysis']['lines_of_code']} lines to multiple organized modules")
        
        return result

# Example usage
def main():
    """Example usage of the CodeRefactorer"""
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    refactorer = CodeRefactorer(API_KEY)
    
    # Example: Refactor a messy Python script (simulating a complex test automation script)
    messy_code = '''
import os,sys,json,time,requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

def run_tests():
    driver = webdriver.Chrome()
    results = []
    try:
        # Login test
        driver.get("https://example.com/login")
        driver.find_element(By.ID, "username").send_keys("test@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(2)
        if "dashboard" in driver.current_url:
            results.append({"test": "login", "status": "pass", "time": time.time()})
        else:
            results.append({"test": "login", "status": "fail", "time": time.time()})
        
        # Search test
        driver.get("https://example.com/search")
        driver.find_element(By.ID, "search-input").send_keys("test query")
        driver.find_element(By.ID, "search-btn").click()
        time.sleep(3)
        search_results = driver.find_elements(By.CLASS_NAME, "search-result")
        if len(search_results) > 0:
            results.append({"test": "search", "status": "pass", "time": time.time()})
        else:
            results.append({"test": "search", "status": "fail", "time": time.time()})
        
        # Checkout test
        driver.get("https://example.com/product/123")
        driver.find_element(By.ID, "add-to-cart").click()
        time.sleep(1)
        driver.get("https://example.com/cart")
        driver.find_element(By.ID, "checkout-btn").click()
        time.sleep(2)
        driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
        driver.find_element(By.ID, "expiry").send_keys("12/25")
        driver.find_element(By.ID, "cvv").send_keys("123")
        driver.find_element(By.ID, "submit-payment").click()
        time.sleep(5)
        if "order-confirmation" in driver.current_url:
            results.append({"test": "checkout", "status": "pass", "time": time.time()})
        else:
            results.append({"test": "checkout", "status": "fail", "time": time.time()})
            
    except Exception as e:
        print(f"Error: {e}")
        results.append({"test": "error", "status": "fail", "error": str(e), "time": time.time()})
    finally:
        driver.quit()
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv("test_results.csv", index=False)
    
    # Generate report
    passed = len([r for r in results if r.get("status") == "pass"])
    failed = len([r for r in results if r.get("status") == "fail"])
    
    report = f"""
    Test Execution Report
    ====================
    Total Tests: {len(results)}
    Passed: {passed}
    Failed: {failed}
    Success Rate: {(passed/len(results)*100):.2f}%
    
    Details:
    """
    
    for result in results:
        report += f"- {result['test']}: {result['status']}\n"
    
    with open("test_report.txt", "w") as f:
        f.write(report)
    
    print("Tests completed. Results saved to test_results.csv and test_report.txt")

if __name__ == "__main__":
    run_tests()
'''
    
    print("Refactoring messy test automation script...")
    result = refactorer.refactor_and_save(
        messy_code,
        language="python",
        filename="messy_test_script.py",
        project_name="clean_test_automation"
    )
    
    if result["success"]:
        print("\n✅ Refactoring completed successfully!")
        for file_path in result["saved_files"]:
            print(f"  - {file_path}")
    else:
        print(f"❌ Refactoring failed: {result['error']}")

if __name__ == "__main__":
    main()
