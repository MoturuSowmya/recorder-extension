#!/usr/bin/env python3
"""
Complete Usage Example: GenAI Script Generator and Code Refactorer
Demonstrates practical usage of both tools with automation testing features
"""

import os
from pathlib import Path
from script_generator import ScriptGenerator
from code_refactorer import CodeRefactorer

def demonstrate_script_generation():
    """Demonstrate script generation with automation testing features"""
    print("🚀 Starting Script Generation Demo...")
    
    # Initialize generator
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    generator = ScriptGenerator(api_key)
    
    # Example 1: Generate Test Prioritization System (from your requirements)
    print("\n📋 Generating Automated Test Prioritization System...")
    
    prioritization_prompt = """
    Create a Python system for Automated Test Prioritization that optimizes test execution order in CI/CD pipelines.
    
    REQUIREMENTS:
    - Analyze test execution histories and failure patterns
    - Rank tests by importance (coverage impact, failure history, business criticality)
    - Consider code changes from Git to identify affected tests
    - Implement multiple prioritization algorithms (risk-based, coverage-based, time-based)
    - Provide natural language explanations for prioritization decisions
    - Generate execution plans with time estimates
    - Support integration with Jenkins, GitHub Actions, GitLab CI
    - Include real-time re-prioritization based on running test results
    - Create detailed reports and dashboards
    - Support parallel execution planning
    
    TECHNICAL SPECIFICATIONS:
    - Use Git integration for change analysis
    - Implement machine learning for failure prediction
    - Create modular architecture with plugin system
    - Include comprehensive configuration management
    - Add progress tracking and cancellation support
    - Support multiple test frameworks (pytest, unittest, nose)
    - Include CLI and web interface options
    - Add extensive logging and monitoring
    
    The system should speed up CI/CD feedback by running high-risk tests first.
    """
    
    result = generator.generate_and_save(
        prioritization_prompt,
        language="python",
        project_name="test_prioritization_system"
    )
    
    if result["success"]:
        print(f"✅ Generated {len(result['files'])} files for Test Prioritization System")
        for file_path in result["saved_files"]:
            print(f"   📄 {file_path}")
    else:
        print(f"❌ Generation failed: {result['error']}")
    
    # Example 2: Generate Environment Issue Predictor (TypeScript)
    print("\n🌍 Generating Environment Issue Predictor...")
    
    environment_prompt = """
    Create a TypeScript application for Environment Issue Prediction in automation testing.
    
    REQUIREMENTS:
    - Monitor test environments (browser versions, OS, network conditions)
    - Analyze environment-related test failures from logs and metrics
    - Predict potential environment issues before they cause failures
    - Provide automated fixes and suggestions (browser updates, configuration changes)
    - Track environment stability trends and patterns
    - Generate alerts for environment degradation
    - Support multiple environment types (local, staging, production-like)
    - Include integration with monitoring tools (Prometheus, Grafana, DataDog)
    - Create real-time dashboards for environment health
    - Support automated environment provisioning recommendations
    
    TECHNICAL SPECIFICATIONS:
    - Use TypeScript with strict typing and modern Node.js
    - Implement real-time data streaming and processing
    - Create microservices architecture with Docker support
    - Include comprehensive API with OpenAPI documentation
    - Add WebSocket support for real-time updates
    - Implement caching and performance optimization
    - Include extensive unit and integration tests
    - Support configuration via environment variables and config files
    - Add comprehensive error handling and logging
    
    Focus on preventing environment-related test failures proactively.
    """
    
    result = generator.generate_and_save(
        environment_prompt,
        language="typescript",
        project_name="environment_issue_predictor"
    )
    
    if result["success"]:
        print(f"✅ Generated {len(result['files'])} files for Environment Issue Predictor")
        for file_path in result["saved_files"]:
            print(f"   📄 {file_path}")
    else:
        print(f"❌ Generation failed: {result['error']}")

def demonstrate_code_refactoring():
    """Demonstrate code refactoring with a complex legacy script"""
    print("\n🔧 Starting Code Refactoring Demo...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    refactorer = CodeRefactorer(api_key)
    
    # Example: Legacy test report analyzer (complex, messy code)
    print("\n📊 Refactoring Legacy Test Report Analyzer...")
    
    legacy_code = '''
import os, sys, json, csv, xml.etree.ElementTree as ET, re, datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

def analyze_reports():
    results = []
    test_data = {}
    failures = {}
    trends = {}
    
    # Process different report formats
    for file in os.listdir("reports"):
        if file.endswith(".json"):
            try:
                with open(f"reports/{file}") as f:
                    data = json.load(f)
                    for test in data.get("tests", []):
                        test_name = test["name"]
                        status = test["status"]
                        duration = test.get("duration", 0)
                        timestamp = test.get("timestamp", "")
                        
                        if test_name not in test_data:
                            test_data[test_name] = []
                        test_data[test_name].append({
                            "status": status,
                            "duration": duration,
                            "timestamp": timestamp,
                            "file": file
                        })
                        
                        if status == "failed":
                            error_msg = test.get("error", "")
                            if test_name not in failures:
                                failures[test_name] = []
                            failures[test_name].append({
                                "error": error_msg,
                                "timestamp": timestamp,
                                "file": file
                            })
            except Exception as e:
                print(f"Error processing {file}: {e}")
                
        elif file.endswith(".xml"):
            try:
                tree = ET.parse(f"reports/{file}")
                root = tree.getroot()
                for testcase in root.findall(".//testcase"):
                    test_name = testcase.get("name", "") + "." + testcase.get("classname", "")
                    time_val = float(testcase.get("time", 0))
                    
                    failure = testcase.find("failure")
                    error = testcase.find("error")
                    
                    status = "passed"
                    error_msg = ""
                    if failure is not None:
                        status = "failed"
                        error_msg = failure.text or ""
                    elif error is not None:
                        status = "error"
                        error_msg = error.text or ""
                    
                    if test_name not in test_data:
                        test_data[test_name] = []
                    test_data[test_name].append({
                        "status": status,
                        "duration": time_val,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "file": file
                    })
                    
                    if status in ["failed", "error"]:
                        if test_name not in failures:
                            failures[test_name] = []
                        failures[test_name].append({
                            "error": error_msg,
                            "timestamp": datetime.datetime.now().isoformat(),
                            "file": file
                        })
            except Exception as e:
                print(f"Error processing XML {file}: {e}")
        
        elif file.endswith(".csv"):
            try:
                df = pd.read_csv(f"reports/{file}")
                for _, row in df.iterrows():
                    test_name = row.get("test_name", "")
                    status = row.get("status", "")
                    duration = row.get("duration", 0)
                    timestamp = row.get("timestamp", "")
                    
                    if test_name not in test_data:
                        test_data[test_name] = []
                    test_data[test_name].append({
                        "status": status,
                        "duration": float(duration) if duration else 0,
                        "timestamp": timestamp,
                        "file": file
                    })
                    
                    if status == "failed":
                        error_msg = row.get("error_message", "")
                        if test_name not in failures:
                            failures[test_name] = []
                        failures[test_name].append({
                            "error": error_msg,
                            "timestamp": timestamp,
                            "file": file
                        })
            except Exception as e:
                print(f"Error processing CSV {file}: {e}")
    
    # Calculate flakiness for each test
    flaky_tests = {}
    for test_name, executions in test_data.items():
        if len(executions) > 1:
            total = len(executions)
            passed = len([e for e in executions if e["status"] == "passed"])
            failed = len([e for e in executions if e["status"] == "failed"])
            
            if passed > 0 and failed > 0:
                flakiness = (failed / total) * 100
                if flakiness > 10:  # More than 10% failure rate
                    flaky_tests[test_name] = {
                        "flakiness_percentage": flakiness,
                        "total_runs": total,
                        "passed": passed,
                        "failed": failed,
                        "executions": executions
                    }
    
    # Generate trend analysis
    for test_name, executions in test_data.items():
        sorted_executions = sorted(executions, key=lambda x: x["timestamp"])
        recent_executions = sorted_executions[-10:]  # Last 10 runs
        
        if len(recent_executions) >= 5:
            recent_failures = len([e for e in recent_executions if e["status"] == "failed"])
            if recent_failures >= 3:
                trends[test_name] = {
                    "trend": "degrading",
                    "recent_failure_rate": (recent_failures / len(recent_executions)) * 100,
                    "recent_executions": recent_executions
                }
    
    # Generate summary report
    total_tests = len(test_data)
    total_executions = sum(len(executions) for executions in test_data.values())
    total_flaky = len(flaky_tests)
    total_trending_down = len(trends)
    
    print(f"=== Test Analysis Summary ===")
    print(f"Total Tests: {total_tests}")
    print(f"Total Executions: {total_executions}")
    print(f"Flaky Tests: {total_flaky}")
    print(f"Tests Trending Down: {total_trending_down}")
    
    # Save detailed results
    with open("analysis_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "total_executions": total_executions,
                "flaky_tests_count": total_flaky,
                "trending_down_count": total_trending_down
            },
            "flaky_tests": flaky_tests,
            "trends": trends,
            "all_test_data": test_data
        }, f, indent=2)
    
    # Generate visualizations
    if flaky_tests:
        test_names = list(flaky_tests.keys())[:10]  # Top 10 flaky tests
        flakiness_percentages = [flaky_tests[name]["flakiness_percentage"] for name in test_names]
        
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(test_names)), flakiness_percentages)
        plt.xlabel("Tests")
        plt.ylabel("Flakiness Percentage")
        plt.title("Top 10 Flaky Tests")
        plt.xticks(range(len(test_names)), [name[:30] + "..." if len(name) > 30 else name for name in test_names], rotation=45)
        plt.tight_layout()
        plt.savefig("flaky_tests_chart.png")
        plt.close()
    
    print("Analysis complete. Results saved to analysis_results.json")
    if flaky_tests:
        print("Flaky tests chart saved to flaky_tests_chart.png")

if __name__ == "__main__":
    analyze_reports()
'''
    
    result = refactorer.refactor_and_save(
        legacy_code,
        language="python",
        filename="legacy_test_analyzer.py",
        project_name="clean_test_analyzer"
    )
    
    if result["success"]:
        print(f"✅ Refactoring completed successfully!")
        print(f"📈 Complexity reduced from {result['original_analysis']['lines_of_code']} lines to organized modules")
        print("📁 Generated files:")
        for file_path in result["saved_files"]:
            print(f"   📄 {file_path}")
    else:
        print(f"❌ Refactoring failed: {result['error']}")

def demonstrate_file_refactoring():
    """Demonstrate refactoring from an existing file"""
    print("\n📁 Demonstrating File-based Refactoring...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    refactorer = CodeRefactorer(api_key)
    
    # Create a sample messy file to refactor
    sample_file = Path("sample_messy_code.py")
    messy_content = '''
import requests, json, time, os
from selenium import webdriver

def do_everything():
    # Login and run tests
    driver = webdriver.Chrome()
    driver.get("https://example.com")
    driver.find_element_by_id("username").send_keys("test")
    driver.find_element_by_id("password").send_keys("pass")
    driver.find_element_by_id("login").click()
    time.sleep(2)
    
    # Check multiple pages
    pages = ["dashboard", "profile", "settings", "reports"]
    for page in pages:
        driver.get(f"https://example.com/{page}")
        time.sleep(1)
        if "error" in driver.page_source.lower():
            print(f"Error on {page}")
        else:
            print(f"{page} is OK")
    
    # API tests
    api_results = []
    endpoints = ["/api/users", "/api/products", "/api/orders"]
    for endpoint in endpoints:
        try:
            response = requests.get(f"https://api.example.com{endpoint}")
            if response.status_code == 200:
                api_results.append({"endpoint": endpoint, "status": "pass"})
            else:
                api_results.append({"endpoint": endpoint, "status": "fail"})
        except:
            api_results.append({"endpoint": endpoint, "status": "error"})
    
    # Save results
    with open("results.json", "w") as f:
        json.dump(api_results, f)
    
    driver.quit()
    print("All tests completed")

do_everything()
'''
    
    # Write sample file
    with open(sample_file, 'w') as f:
        f.write(messy_content)
    
    print(f"📝 Created sample file: {sample_file}")
    
    # Refactor the file
    result = refactorer.refactor_file(
        str(sample_file),
        language="python"
    )
    
    if result["success"]:
        saved_files = refactorer.save_refactored_files(
            result["files"], 
            "refactored_from_file"
        )
        print(f"✅ File refactoring completed!")
        print("📁 Generated files:")
        for file_path in saved_files:
            print(f"   📄 {file_path}")
    else:
        print(f"❌ File refactoring failed: {result['error']}")
    
    # Clean up sample file
    sample_file.unlink()
    print(f"🗑️  Cleaned up sample file")

def main():
    """Main demonstration function"""
    print("🎯 GenAI Automation Testing Tools Demo")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY environment variable not set!")
        print("Please set it with: export GEMINI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Demonstrate script generation
        demonstrate_script_generation()
        
        print("\n" + "=" * 50)
        
        # Demonstrate code refactoring
        demonstrate_code_refactoring()
        
        print("\n" + "=" * 50)
        
        # Demonstrate file-based refactoring
        demonstrate_file_refactoring()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📋 Summary:")
        print("✅ Generated multiple automation testing tools")
        print("✅ Refactored legacy code into clean modules")
        print("✅ Demonstrated file-based refactoring")
        print("\n💡 Next steps:")
        print("1. Review generated code in the output directories")
        print("2. Customize prompts for your specific needs")
        print("3. Integrate with your existing CI/CD pipelines")
        print("4. Use the refactored code as templates for future projects")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Please check your API key and network connection")

if __name__ == "__main__":
    main()
