def generate_browser_task(scenario: str) -> str:
    """Generate the browser task prompt for executing Gherkin scenarios"""
    return f"""
    Execute the following Gherkin scenario with comprehensive logging and detailed actions.
    For each interactive element you encounter, use the "Get XPath of element using index" action 
    to capture its XPath. Get the XPath BEFORE performing any actions on the element.
    Capture element selectors, properties, and states during execution.
    
    {scenario}
    """