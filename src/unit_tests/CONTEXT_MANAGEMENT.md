# Context Management in SDET-GENIE Browser Automation

## Overview
This document explains how SDET-GENIE maintains context between Gherkin scenarios during browser automation execution to ensure seamless navigation and state preservation.

## Problem Statement
When executing multiple Gherkin scenarios separately, each scenario runs in its own browser agent instance, causing loss of:
- Current URL context
- Browser state (cookies, localStorage, sessionStorage)
- Navigation history
- Element interaction context

This leads to scenarios failing because they can't find the expected page state or URL.

## Solution Approach

### 1. Single Browser Session
Instead of creating separate browser agents for each scenario, we use a single browser session that maintains state across all scenarios:

```python
# Create one browser agent for all scenarios
browser_agent = TrackingBrowserAgent(
    task="",  # Task updated for each scenario
    llm=browser_use_llm,
    use_vision=True,
    generate_gif=True,
)

# Execute all scenarios in the same session
for scenario in scenarios:
    browser_agent.task = generate_browser_task(scenario, execution_context)
    scenario_history = await browser_agent.run()
```

### 2. Context-Aware Task Generation
The task generation includes execution context to help the AI agent understand the current state:

```python
def generate_browser_task(scenario: str, context: dict = None) -> str:
    # Include context information in the prompt
    context_section = ""
    if context:
        context_section = "\n**Execution Context:**\n"
        if "current_url" in context:
            context_section += f"- Current URL: {context['current_url']}\n"
        if "visited_urls" in context:
            context_section += f"- Previously visited URLs: {', '.join(context['visited_urls'])}\n"
```

### 3. Lifecycle Hooks for State Tracking
We use browser agent lifecycle hooks to capture and maintain state between steps:

```python
async def on_step_end(agent):
    """Hook to capture context after each step"""
    try:
        # Capture current URL
        current_url = await agent.browser_session.get_current_page_url()
        if current_url and current_url not in execution_context["visited_urls"]:
            execution_context["visited_urls"].append(current_url)
    except Exception as e:
        # Silently handle errors in hooks
        pass

# Execute with hooks
scenario_history = await browser_agent.run(on_step_end=on_step_end)
```

### 4. Element Context Tracking
The element tracker now includes execution context with each element interaction:

```python
details = {
    "element_index": node.element_index,
    "tag_name": node.node_name.lower() if node.node_name else "",
    # ... other element details
    "execution_context": self.execution_context.copy()  # Add context to element details
}
```

## Benefits

### 1. Seamless Navigation
- Scenarios can continue from where the previous scenario left off
- No need to re-navigate to base URLs in each scenario
- State is preserved between scenario executions

### 2. Improved Reliability
- Reduced failures due to missing context
- Better handling of dynamic content
- More accurate element identification

### 3. Enhanced Debugging
- Complete execution history with context
- Better error reporting with state information
- Easier troubleshooting of scenario failures

## Implementation Details

### Browser Executor Changes
1. Single browser session creation for all scenarios
2. Context-aware task generation
3. Lifecycle hooks for state tracking
4. History merging for comprehensive reporting

### Element Tracker Enhancements
1. Execution context storage
2. Context inclusion in element details
3. Context update methods

### Prompt Engineering Improvements
1. Context section in browser task prompts
2. URL and navigation history awareness
3. Session state information in prompts

## Usage Examples

### Before (Context Lost)
```gherkin
Scenario: User logs in
  Given the user is on the login page
  When the user enters credentials
  And clicks login
  Then the user is on the dashboard

Scenario: User adds item to cart
  Given the user is on the dashboard  # ❌ Fails - not on dashboard
  When the user clicks "Add to Cart"
  Then the item is added to cart
```

### After (Context Maintained)
```gherkin
Scenario: User logs in
  Given the user is on the login page
  When the user enters credentials
  And clicks login
  Then the user is on the dashboard

Scenario: User adds item to cart
  Given the user is on the dashboard  # ✅ Works - context maintained
  When the user clicks "Add to Cart"
  Then the item is added to cart
```

## Future Enhancements

### 1. Advanced State Management
- Cookie and localStorage persistence
- Session state serialization
- Cross-browser state sharing

### 2. Intelligent Context Inference
- AI-powered context prediction
- Automatic scenario dependency detection
- Smart state restoration

### 3. Enhanced Debugging Tools
- Visual context timeline
- State diff analysis
- Context-aware error suggestions

This context management approach significantly improves the reliability and user experience of SDET-GENIE's browser automation capabilities.