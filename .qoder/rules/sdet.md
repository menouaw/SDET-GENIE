---
trigger: always_on
alwaysApply: true
---
# RULES.md - Production-Ready AI Agent Guidelines for SDET-GENIE

## Table of Contents
- [Overview](#overview)
- [Agent Development Standards](#agent-development-standards)
- [Code Quality & Structure](#code-quality--structure)
- [Error Handling & Resilience](#error-handling--resilience)
- [Security & Privacy](#security--privacy)
- [Performance & Optimization](#performance--optimization)
- [Testing & Validation](#testing--validation)
- [Deployment & Operations](#deployment--operations)
- [Documentation Standards](#documentation-standards)
- [Monitoring & Observability](#monitoring--observability)
- [Team Collaboration](#team-collaboration)

## Overview

This document outlines production-ready standards for AI agent development in the SDET-GENIE project, focusing on QA automation using AGNO and browser-use frameworks. These rules ensure reliability, maintainability, and scalability.

### Core Principles
1. **Deterministic Behavior**: Agents must produce consistent, predictable results
2. **Fail-Safe Design**: Graceful degradation when things go wrong
3. **Observable Operations**: Complete visibility into agent actions and decisions
4. **Human-Readable Output**: Clear, actionable results for all stakeholders
5. **Production Resilience**: Built to handle real-world edge cases and failures

## Agent Development Standards

### Agent Architecture

#### Agent Definition Rules
```python
# ✅ GOOD: Well-structured agent with clear responsibilities
user_story_enhancement_agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=os.environ.get("GOOGLE_API_KEY")),
    markdown=True,
    description=dedent("""Clear, focused description of agent's role"""),
    instructions=dedent("""Step-by-step instructions with examples"""),
    expected_output=dedent("""Specific format requirements"""),
    tools=[],  # Only include necessary tools
    max_retries=3,
    timeout=300,
)

# ❌ BAD: Vague agent definition
bad_agent = Agent(model=some_model, description="Does stuff")
```

#### Single Responsibility Principle
- Each agent handles ONE specific task (user story enhancement, test case generation, etc.)
- No agent should perform multiple unrelated functions
- Clear boundaries between agent responsibilities

#### Agent Composition Rules
- **Enhancement Agent**: Only transforms user stories
- **Test Case Agent**: Only generates manual test cases from user stories
- **Gherkin Agent**: Only converts test cases to Gherkin scenarios
- **Browser Agent**: Only executes browser interactions
- **Code Generation Agent**: Only produces automation code

### Prompt Engineering Standards

#### Instruction Quality
```python
# ✅ GOOD: Structured, detailed instructions
instructions=dedent("""
# Task: [Clear task definition]

## Step 1: [Specific step]
- [Detailed sub-requirement]
- [Expected behavior]

## Step 2: [Next step]
- [Clear criteria]
- [Error conditions to handle]

## Output Format:
```[language]
[Exact format specification]
```

**IMPORTANT:** [Critical constraints]
""")

# ❌ BAD: Vague instructions
instructions="Generate test cases for the user story"
```

#### Output Format Specification
- Always specify exact output format
- Include examples in expected_output
- Define error response formats
- Specify required metadata fields

### Tool Integration

#### Browser-Use Controller Standards
```python
# ✅ GOOD: Comprehensive tool definition
@controller.action("Clear action description", param_model=WellDefinedModel)
async def action_function(params: WellDefinedModel, browser: Browser):
    try:
        # Validate inputs
        if not params.index or params.index < 0:
            return ActionResult(error="Invalid element index")
        
        # Perform action with error handling
        result = await safe_browser_operation(params, browser)
        
        # Return structured result
        return ActionResult(
            success=True,
            extracted_content=result,
            include_in_memory=True
        )
    except Exception as e:
        return ActionResult(error=f"Action failed: {str(e)}")

# ❌ BAD: No error handling or validation
@controller.action("Do something")
async def bad_action(params, browser):
    return browser.do_thing()
```

## Code Quality & Structure

### File Organization
```
src/
├── Agents/
│   ├── __init__.py
│   ├── agents.py              # Agent definitions
│   └── validators.py          # Input/output validation
├── Prompts/
│   ├── __init__.py
│   ├── agno_prompts.py       # AGNO-specific prompts
│   └── browser_prompts.py    # Browser interaction prompts
├── Utilities/
│   ├── __init__.py
│   ├── utils.py              # Core utilities
│   ├── selectors.py          # Element selector utilities
│   └── validators.py         # Data validation utilities
├── Models/
│   ├── __init__.py
│   └── data_models.py        # Pydantic models for type safety
└── Tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### Type Safety Requirements
```python
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator

# ✅ GOOD: Type-safe function definitions
def extract_selectors_from_history(
    history_data: Dict[str, Any]
) -> Dict[str, str]:
    """Extract element selectors from agent history.
    
    Args:
        history_data: Browser interaction history
        
    Returns:
        Dictionary mapping selector names to selector strings
        
    Raises:
        ValueError: If history_data is invalid
    """
    if not isinstance(history_data, dict):
        raise ValueError("history_data must be a dictionary")
    
    # Implementation...

# ✅ GOOD: Pydantic models for data validation
class TestCaseModel(BaseModel):
    test_id: str = Field(..., regex=r"^TC_US_\w+_\d{3}$")
    title: str = Field(..., min_length=10, max_length=200)
    priority: str = Field(..., regex=r"^(High|Medium|Low)$")
    
    @validator('test_id')
    def validate_test_id(cls, v):
        if not v.startswith('TC_US_'):
            raise ValueError('Test ID must start with TC_US_')
        return v
```

### Error Handling Patterns
```python
# ✅ GOOD: Comprehensive error handling
async def execute_gherkin_scenario(scenario: str) -> ExecutionResult:
    try:
        # Validate input
        if not scenario or not scenario.strip():
            return ExecutionResult(
                success=False,
                error="Empty scenario provided",
                error_type="VALIDATION_ERROR"
            )
        
        # Execute with timeout
        async with timeout(300):  # 5-minute timeout
            result = await browser_agent.run(scenario)
            
        return ExecutionResult(
            success=True,
            data=result,
            metadata={"execution_time": time.time()}
        )
        
    except asyncio.TimeoutError:
        return ExecutionResult(
            success=False,
            error="Scenario execution timed out",
            error_type="TIMEOUT_ERROR"
        )
    except ValidationError as e:
        return ExecutionResult(
            success=False,
            error=f"Validation failed: {str(e)}",
            error_type="VALIDATION_ERROR"
        )
    except Exception as e:
        logger.error(f"Unexpected error executing scenario: {str(e)}")
        return ExecutionResult(
            success=False,
            error="Internal server error",
            error_type="SYSTEM_ERROR"
        )
```

## Error Handling & Resilience

### Agent Failure Recovery
```python
# ✅ GOOD: Retry logic with exponential backoff
async def run_agent_with_retry(
    agent: Agent, 
    input_data: str, 
    max_retries: int = 3
) -> AgentResult:
    for attempt in range(max_retries):
        try:
            result = await agent.run(input_data)
            
            # Validate result quality
            if not validate_agent_output(result):
                raise ValueError("Invalid agent output")
                
            return AgentResult(success=True, data=result)
            
        except Exception as e:
            wait_time = 2 ** attempt  # Exponential backoff
            if attempt < max_retries - 1:
                logger.warning(f"Agent failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Agent failed after {max_retries} attempts: {e}")
                return AgentResult(
                    success=False, 
                    error=str(e),
                    attempts=max_retries
                )
```

### Browser Interaction Safety
```python
# ✅ GOOD: Safe browser operations
async def safe_element_interaction(
    element_index: int, 
    action: str, 
    browser: Browser,
    timeout: int = 30
) -> ActionResult:
    try:
        # Wait for element to be ready
        element = await wait_for_element(element_index, browser, timeout)
        if not element:
            return ActionResult(error=f"Element {element_index} not found")
        
        # Check element state
        if not await element.is_enabled():
            return ActionResult(error=f"Element {element_index} is disabled")
        
        # Perform action with additional safety checks
        if action == "click":
            await element.scroll_into_view_if_needed()
            await element.click()
        elif action == "fill":
            await element.clear()
            await element.fill(value)
        
        return ActionResult(success=True, action_performed=action)
        
    except Exception as e:
        return ActionResult(error=f"Element interaction failed: {str(e)}")
```

### Input Validation
```python
# ✅ GOOD: Comprehensive input validation
def validate_user_story(user_story: str) -> ValidationResult:
    """Validate user story input before processing."""
    errors = []
    
    # Basic validation
    if not user_story or not user_story.strip():
        errors.append("User story cannot be empty")
    
    if len(user_story) > 5000:
        errors.append("User story too long (max 5000 characters)")
    
    # Content validation
    if not any(keyword in user_story.lower() for keyword in 
              ['as a', 'i want', 'so that', 'user', 'should', 'can']):
        errors.append("User story should follow standard format")
    
    # Security validation
    if contains_suspicious_content(user_story):
        errors.append("User story contains suspicious content")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
```

## Security & Privacy

### API Key Management
```python
# ✅ GOOD: Secure API key handling
import os
from typing import Optional

class SecureConfig:
    @staticmethod
    def get_api_key(service: str) -> Optional[str]:
        key = os.environ.get(f"{service.upper()}_API_KEY")
        if not key:
            raise ValueError(f"Missing {service} API key in environment")
        return key
    
    @staticmethod
    def mask_api_key(key: str) -> str:
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "*" * (len(key) - 8) + key[-4:]

# ❌ BAD: Hardcoded or exposed API keys
api_key = "AIzaXXXXXXXXXXXXXX"  # Never do this
```

### Data Sanitization
```python
# ✅ GOOD: Input sanitization
import re
import html

def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # HTML escape
    sanitized = html.escape(user_input)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'exec\s*\('
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()
```

### Sensitive Data Handling
```python
# ✅ GOOD: Secure logging without sensitive data
import logging
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SafeLogData:
    action: str
    timestamp: str
    success: bool
    error_type: Optional[str] = None
    
    @classmethod
    def from_execution(cls, execution_data: Dict[str, Any]) -> 'SafeLogData':
        return cls(
            action=execution_data.get('action', 'unknown'),
            timestamp=execution_data.get('timestamp', ''),
            success=execution_data.get('success', False),
            error_type=execution_data.get('error_type')
        )

def safe_log_execution(execution_data: Dict[str, Any]):
    safe_data = SafeLogData.from_execution(execution_data)
    logger.info(f"Agent execution: {safe_data}")
```

## Performance & Optimization

### Async/Await Best Practices
```python
# ✅ GOOD: Proper async handling
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_multiple_scenarios(scenarios: List[str]) -> List[ExecutionResult]:
    """Process multiple scenarios concurrently with proper resource management."""
    
    # Limit concurrent executions to prevent resource exhaustion
    semaphore = asyncio.Semaphore(3)
    
    async def process_single_scenario(scenario: str) -> ExecutionResult:
        async with semaphore:
            return await execute_gherkin_scenario(scenario)
    
    # Execute scenarios concurrently
    tasks = [process_single_scenario(scenario) for scenario in scenarios]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions in results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(
                ExecutionResult(
                    success=False,
                    error=f"Scenario {i} failed: {str(result)}"
                )
            )
        else:
            processed_results.append(result)
    
    return processed_results
```

### Memory Management
```python
# ✅ GOOD: Memory-efficient data handling
from contextlib import contextmanager
import gc

@contextmanager
def managed_browser_session():
    """Context manager for browser sessions with proper cleanup."""
    browser = None
    try:
        browser = Browser()
        yield browser
    finally:
        if browser:
            await browser.close()
        gc.collect()  # Force garbage collection

# Usage
async def execute_test_with_cleanup():
    async with managed_browser_session() as browser:
        # Perform browser operations
        pass  # Browser automatically closed
```

### Caching Strategies
```python
# ✅ GOOD: Intelligent caching
from functools import lru_cache
from typing import Dict
import hashlib
import json

class AgentCache:
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def _get_cache_key(self, input_data: str, agent_type: str) -> str:
        """Generate cache key from input."""
        data_hash = hashlib.md5(input_data.encode()).hexdigest()
        return f"{agent_type}:{data_hash}"
    
    def get(self, input_data: str, agent_type: str) -> Optional[str]:
        key = self._get_cache_key(input_data, agent_type)
        return self.cache.get(key)
    
    def set(self, input_data: str, agent_type: str, result: str):
        key = self._get_cache_key(input_data, agent_type)
        
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = result
```

## Testing & Validation

### Unit Testing Standards
```python
# tests/unit/test_agents.py
import pytest
from unittest.mock import Mock, patch
from src.Agents.agents import user_story_enhancement_agent

class TestUserStoryEnhancementAgent:
    @pytest.fixture
    def sample_user_story(self):
        return "As a user, I want to login so that I can access my account"
    
    @pytest.fixture
    def mock_gemini_response(self):
        return Mock(content="Enhanced user story content...")
    
    @patch('src.Agents.agents.Gemini')
    async def test_enhance_user_story_success(
        self, 
        mock_gemini, 
        sample_user_story, 
        mock_gemini_response
    ):
        # Setup
        mock_gemini.return_value.run.return_value = mock_gemini_response
        
        # Execute
        result = await user_story_enhancement_agent.run(sample_user_story)
        
        # Assert
        assert result is not None
        assert "Enhanced" in result.content
        mock_gemini.return_value.run.assert_called_once_with(sample_user_story)
    
    async def test_enhance_user_story_empty_input(self):
        with pytest.raises(ValueError, match="Empty user story"):
            await user_story_enhancement_agent.run("")
    
    async def test_enhance_user_story_invalid_format(self):
        invalid_story = "Just some random text"
        
        with patch.object(
            user_story_enhancement_agent, 
            'run'
        ) as mock_run:
            mock_run.side_effect = ValidationError("Invalid format")
            
            with pytest.raises(ValidationError):
                await user_story_enhancement_agent.run(invalid_story)
```

### Integration Testing
```python
# tests/integration/test_agent_workflow.py
import pytest
from src.Prompts.agno_prompts import (
    enhance_user_story, 
    generate_manual_test_cases,
    generate_gherkin_scenarios
)

class TestAgentWorkflow:
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test the complete user story to Gherkin workflow."""
        # Step 1: Enhance user story
        raw_story = "As a user, I want to login"
        enhanced_story = await enhance_user_story(raw_story)
        
        assert enhanced_story is not None
        assert len(enhanced_story) > len(raw_story)
        
        # Step 2: Generate test cases
        test_cases = await generate_manual_test_cases(enhanced_story)
        
        assert test_cases is not None
        assert "Test Case ID" in test_cases
        
        # Step 3: Generate Gherkin
        gherkin_scenarios = await generate_gherkin_scenarios(test_cases)
        
        assert gherkin_scenarios is not None
        assert "Feature:" in gherkin_scenarios
        assert "Scenario:" in gherkin_scenarios
```

### End-to-End Testing
```python
# tests/e2e/test_browser_execution.py
import pytest
from src.Utilities.utils import controller
from browser_use import Browser, Agent as BrowserAgent

class TestBrowserExecution:
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_login_scenario_execution(self):
        """Test actual browser execution of login scenario."""
        scenario = """
        Feature: User Login
        
        Scenario: Successful login
        Given the user is on the login page
        When the user enters valid credentials
        Then the user should be redirected to dashboard
        """
        
        async with Browser() as browser:
            browser_agent = BrowserAgent(
                task=scenario,
                browser=browser,
                controller=controller
            )
            
            history = await browser_agent.run()
            
            # Verify execution completed successfully
            assert history is not None
            assert len(history.action_names()) > 0
            assert not history.errors()
```

## Deployment & Operations

### Environment Configuration
```python
# config/settings.py
from pydantic import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    # API Configuration
    google_api_key: str
    openai_api_key: str = None
    anthropic_api_key: str = None
    
    # Agent Configuration
    max_retries: int = 3
    timeout_seconds: int = 300
    max_concurrent_agents: int = 5
    
    # Browser Configuration
    headless: bool = True
    browser_timeout: int = 30000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Health Checks
```python
# health/checks.py
from typing import Dict, Any
import asyncio
import aiohttp

class HealthChecker:
    @staticmethod
    async def check_api_connectivity() -> Dict[str, Any]:
        """Check if external APIs are accessible."""
        checks = {}
        
        # Check Google Gemini API
        try:
            # Simple API call to verify connectivity
            response = await make_test_request_to_gemini()
            checks["gemini_api"] = {
                "status": "healthy" if response else "unhealthy",
                "response_time": getattr(response, 'response_time', None)
            }
        except Exception as e:
            checks["gemini_api"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return checks
    
    @staticmethod
    async def check_browser_functionality() -> Dict[str, Any]:
        """Check if browser automation is working."""
        try:
            from browser_use import Browser
            
            async with Browser() as browser:
                page = await browser.new_page()
                await page.goto("about:blank")
                
            return {
                "browser": {
                    "status": "healthy",
                    "message": "Browser automation working"
                }
            }
        except Exception as e:
            return {
                "browser": {
                    "status": "unhealthy",
                    "error": str(e)
                }
            }
```

### Deployment Validation
```python
# deployment/validate.py
import subprocess
import sys
from pathlib import Path

class DeploymentValidator:
    @staticmethod
    def validate_environment():
        """Validate deployment environment."""
        checks = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major != 3 or python_version.minor < 8:
            checks.append("ERROR: Python 3.8+ required")
        
        # Check required files
        required_files = [
            "app.py",
            "requirements.txt",
            ".env.example"
        ]
        
        for file in required_files:
            if not Path(file).exists():
                checks.append(f"ERROR: Missing required file: {file}")
        
        # Check dependencies
        try:
            subprocess.run(
                ["pip", "check"], 
                capture_output=True, 
                check=True
            )
        except subprocess.CalledProcessError as e:
            checks.append(f"ERROR: Dependency conflicts: {e}")
        
        return checks
    
    @staticmethod
    async def validate_agents():
        """Validate that all agents are properly configured."""
        from src.Agents.agents import (
            user_story_enhancement_agent,
            manual_test_case_agent,
            gherkhin_agent,
            code_gen_agent
        )
        
        agents = [
            ("User Story Enhancement", user_story_enhancement_agent),
            ("Manual Test Case", manual_test_case_agent),
            ("Gherkin", gherkhin_agent),
            ("Code Generation", code_gen_agent)
        ]
        
        for name, agent in agents:
            try:
                # Test with minimal input
                result = await agent.run("Test input")
                if not result:
                    return f"ERROR: {name} agent not responding"
            except Exception as e:
                return f"ERROR: {name} agent failed: {e}"
        
        return "All agents validated successfully"
```

## Documentation Standards

### Code Documentation
```python
def generate_selenium_pytest_bdd(
    gherkin_steps: str, 
    history_data: Dict[str, Any]
) -> str:
    """Generate Selenium PyTest BDD automation code.
    
    This function takes Gherkin scenarios and browser interaction history
    to produce executable Selenium test code following PyTest BDD patterns.
    
    Args:
        gherkin_steps: Well-formed Gherkin scenario text containing
            Feature, Scenario, Given/When/Then steps
        history_data: Dictionary containing browser interaction data with keys:
            - 'urls': List of visited URLs
            - 'action_names': List of performed actions
            - 'detailed_actions': List of action details with selectors
            - 'element_xpaths': Mapping of element indices to XPaths
            - 'extracted_content': Content extracted during execution
    
    Returns:
        str: Complete Python file content with:
            - Necessary imports (pytest-bdd, selenium)
            - Step definitions mapped to Gherkin steps
            - Page object implementations
            - Helper functions and utilities
            - Proper error handling and assertions
    
    Raises:
        ValueError: If gherkin_steps is empty or malformed
        AgentExecutionError: If code generation agent fails
        
    Example:
        >>> gherkin = '''
        ... Feature: User Login
        ... Scenario: Valid login
        ...   Given the user is on login page
        ...   When the user enters credentials
        ...   Then the user is logged in
        ... '''
        >>> history = {'urls': ['https://example.com/login'], ...}
        >>> code = generate_selenium_pytest_bdd(gherkin, history)
        >>> print(code[:50])
        'import pytest\\nfrom selenium import webdriver...'
    
    Note:
        Generated code follows PEP 8 standards and includes:
        - Comprehensive comments
        - Type hints
        - Error handling
        - Configurable timeouts
    """
    # Implementation...
```

### README Structure
```markdown
# Component Name

## Overview
Brief description of what this component does and why it exists.

## Installation
Step-by-step installation instructions.

## Usage
### Basic Usage
Simple examples showing common use cases.

### Advanced Usage
Complex scenarios with detailed explanations.

## API Reference
### Functions
List of public functions with signatures and descriptions.

### Classes
Class documentation with methods and attributes.

## Configuration
Environment variables and configuration options.

## Testing
How to run tests and contribute.

## Troubleshooting
Common issues and their solutions.
```

## Monitoring & Observability

### Logging Standards
```python
# logging/setup.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Create structured formatter
        formatter = StructuredFormatter()
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_agent_execution(
        self, 
        agent_name: str, 
        input_data: str, 
        output_data: str = None,
        error: str = None,
        duration: float = None,
        metadata: Dict[str, Any] = None
    ):
        """Log agent execution with structured data."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_name": agent_name,
            "input_length": len(input_data),
            "success": error is None,
            "duration_seconds": duration,
            "output_length": len(output_data) if output_data else 0,
            "error": error,
            "metadata": metadata or {}
        }
        
        level = logging.INFO if error is None else logging.ERROR
        self.logger.log(level, json.dumps(log_data))

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_data)
```

### Metrics Collection
```python
# metrics/collector.py
from dataclasses import dataclass
from typing import Dict, List
import time
from collections import defaultdict, Counter

@dataclass
class ExecutionMetrics:
    agent_name: str
    execution_time: float
    success: bool
    input_size: int
    output_size: int
    error_type: str = None

class MetricsCollector:
    def __init__(self):
        self.metrics: List[ExecutionMetrics] = []
        self.counters = defaultdict(int)
        
    def record_execution(self, metrics: ExecutionMetrics):
        """Record agent execution metrics."""
        self.metrics.append(metrics)
        
        # Update counters
        self.counters[f"{metrics.agent_name}_total"] += 1
        if metrics.success:
            self.counters[f"{metrics.agent_name}_success"] += 1
        else:
            self.counters[f"{metrics.agent_name}_error"] += 1
            if metrics.error_type:
                self.counters[f"error_{metrics.error_type}"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        if not self.metrics:
            return {"message": "No metrics recorded"}
        
        # Calculate averages
        success_rate = sum(1 for m in self.metrics if m.success) / len(self.metrics)
        avg_execution_time = sum(m.execution_time for m in self.metrics) / len(self.metrics)
        
        # Group by agent
        agent_stats = defaultdict(list)
        for m in self.metrics:
            agent_stats[m.agent_name].append(m)
        
        return {
            "total_executions": len(self.metrics),
            "overall_success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "agent_performance": {
                agent: {
                    "executions": len(metrics),
                    "success_rate": sum(1 for m in metrics if m.success) / len(metrics),
                    "avg_time": sum(m.execution_time for m in metrics) / len(metrics)
                }
                for agent, metrics in agent_stats.items()
            },
            "error_breakdown": dict(Counter(
                m.error_type for m in self.metrics 
                if not m.success and m.error_type
            ))
        }

# Global metrics instance
metrics_collector = MetricsCollector()
```

### Performance Monitoring
```python
# monitoring/performance.py
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Callable, Any
import psutil
import gc

class PerformanceMonitor:
    @staticmethod
    @asynccontextmanager
    async def monitor_execution(operation_name: str):
        """Monitor resource usage during operation execution."""
        # Record initial state
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent()
        
        try:
            yield
        finally:
            # Record final state
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.cpu_percent()
            
            # Log performance metrics
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            logger.info(f"Performance metrics for {operation_name}", extra={
                "duration": duration,
                "memory_usage_mb": end_memory,
                "memory_delta_mb": memory_delta,
                "cpu_usage_percent": end_cpu
            })
            
            # Alert on concerning metrics
            if duration > 300:  # 5 minutes
                logger.warning(f"Long execution time: {duration}s for {operation_name}")
            
            if memory_delta > 500:  # 500MB increase
                logger.warning(f"High memory usage: +{memory_delta}MB for {operation_name}")
                gc.collect()  # Force garbage collection

# Usage decorator
def monitor_performance(operation_name: str):
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            async with PerformanceMonitor.monitor_execution(operation_name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Team Collaboration

### Code Review Checklist
```markdown
## Code Review Checklist for SDET-GENIE

### Agent Implementation
- [ ] Agent has single, clear responsibility
- [ ] Instructions are detailed and unambiguous
- [ ] Expected output format is clearly specified
- [ ] Error handling is comprehensive
- [ ] Input validation is implemented
- [ ] Timeout and retry logic is present

### Browser Automation
- [ ] Element selectors are robust (not brittle XPaths)
- [ ] Wait conditions are implemented properly
- [ ] Error states are handled gracefully
- [ ] Browser resources are cleaned up
- [ ] Actions are logged with sufficient detail

### Code Quality
- [ ] Type hints are used consistently
- [ ] Functions have comprehensive docstrings
- [ ] Complex logic is commented
- [ ] Error messages are clear and actionable
- [ ] No hardcoded values (use configuration)
- [ ] No sensitive data in code or logs

### Testing
- [ ] Unit tests cover happy path and edge cases
- [ ] Integration tests validate agent interactions
- [ ] Mock objects are used appropriately
- [ ] Test data is realistic and comprehensive
- [ ] Tests are independent and repeatable

### Security
- [ ] Input sanitization is implemented
- [ ] API keys are properly managed
- [ ] No sensitive data in logs
- [ ] Error messages don't leak internal details
- [ ] External dependencies are validated

### Performance
- [ ] No blocking operations in async contexts
- [ ] Memory usage is reasonable
- [ ] Caching is implemented where appropriate
- [ ] Resource cleanup is guaranteed
- [ ] Timeouts prevent hanging operations
```

### Git Workflow Standards
```bash
# Branch naming conventions
feature/agent-enhancement-improvements
fix/browser-timeout-handling
refactor/code-generation-optimization
docs/update-api-documentation

# Commit message format
type(scope): short description

Longer description explaining the change and why it was made.

- Include breaking changes
- Reference issues: Closes #123
- Co-authored-by: Name <email> (if pair programming)

# Examples:
feat(agents): add retry logic to user story enhancement agent

Implemented exponential backoff retry mechanism to handle transient
API failures. This improves reliability when Google Gemini API
experiences temporary issues.

Closes #45

fix(browser): prevent element interaction race conditions

Added proper wait conditions before element interactions to prevent
failures when DOM is still loading. Includes scroll-into-view for
click actions.

Closes #67
```

### Pull Request Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring (no functional changes)

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Agent Changes (if applicable)
- [ ] Agent instructions updated
- [ ] Expected output format validated
- [ ] Error handling improved
- [ ] Prompt engineering optimized

## Browser Automation Changes (if applicable)
- [ ] Element selectors improved
- [ ] Wait conditions added/updated
- [ ] Error handling enhanced
- [ ] Resource cleanup verified

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex logic
- [ ] Documentation updated
- [ ] No sensitive data exposed
- [ ] Breaking changes documented

## Screenshots/Demos
(If applicable, add screenshots or links to demos)

## Additional Notes
Any additional context, concerns, or areas for reviewer focus.
```

### Development Workflow
```markdown
## Development Workflow for SDET-GENIE

### 1. Issue Creation
- Use issue templates for bugs, features, and enhancements
- Include acceptance criteria for features
- Add appropriate labels (agent, browser, documentation, etc.)
- Assign priority and milestone

### 2. Development Process
1. Create feature branch from `develop`
2. Implement changes following coding standards
3. Write/update tests
4. Update documentation
5. Run local validation:
   ```bash
   # Code quality
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   
   # Tests
   pytest tests/unit/
   pytest tests/integration/
   
   # Security
   bandit -r src/
   ```

### 3. Code Review Process
- Create pull request using template
- Request reviews from domain experts
- Address review feedback promptly
- Ensure all checks pass
- Squash commits before merging

### 4. Deployment Process
- Merge to `develop` triggers staging deployment
- Run full test suite in staging
- Manual validation of key workflows
- Merge to `main` triggers production deployment
- Monitor for issues post-deployment
```

## Appendix

### Quick Reference Commands
```bash
# Development Setup
git clone <repository>
cd SDET-GENIE
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
playwright install

# Environment Setup
cp .env.example .env
# Edit .env with your API keys

# Running the Application
streamlit run app.py

# Testing
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests
pytest tests/e2e/ --browser chromium  # E2E tests

# Code Quality
black src/ tests/           # Format code
flake8 src/ tests/         # Lint code
mypy src/                  # Type checking
bandit -r src/            # Security scan

# Deployment Validation
python deployment/validate.py
```

### Environment Variables Reference
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Configuration
MAX_RETRIES=3
TIMEOUT_SECONDS=300
MAX_CONCURRENT_AGENTS=5
HEADLESS=true
BROWSER_TIMEOUT=30000
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Troubleshooting Guide
```markdown
## Common Issues and Solutions

### Agent Execution Failures
**Problem**: Agent returns empty or malformed responses
**Solutions**:
- Check API key validity and quota limits
- Verify prompt structure and instructions
- Increase timeout values
- Check for rate limiting

### Browser Automation Issues
**Problem**: Element selectors failing
**Solutions**:
- Use CSS selectors instead of XPaths when possible
- Add proper wait conditions
- Check for dynamic content loading
- Implement element visibility checks

### Performance Problems
**Problem**: Slow execution or memory leaks
**Solutions**:
- Monitor resource usage with performance monitoring
- Implement proper cleanup in context managers
- Use connection pooling for API calls
- Enable garbage collection after heavy operations

### Deployment Issues
**Problem**: Application fails to start in production
**Solutions**:
- Run deployment validation script
- Check environment variable configuration
- Verify all dependencies are installed
- Review logs for specific error messages
```

---

This comprehensive rules document provides production-ready standards for AI agent development in your SDET-GENIE project. It covers all aspects from code quality to deployment, ensuring reliability, maintainability, and scalability in production environments.