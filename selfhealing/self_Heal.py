import asyncio
import pandas as pd
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_actions import controller, Posts, Post
from report_generator import generate_html_report, save_report
import uuid
from datetime import datetime, timedelta
from browser_use import Agent, Controller, ActionResult
from browser_use.browser.context import BrowserContext
 
async def update_xpaths(input_file="input.csv"):

    start_time = datetime.now()
    run_id = str(uuid.uuid4())
    df = pd.read_csv(input_file)
    updates = []
    errors = []
    unchanged_elements = []
    xpath_map = {}  # Store original XPaths for unchanged elements
    for index, row in df.iterrows():
        prompt = row['Prompt']
        variable_name = row['Variable_Name']
        existing_xpath = row['Locator_Value']
        xpath_map[variable_name] = existing_xpath # Store XPath
        print(f"\nProcessing {variable_name}...")
        try:
            model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key="AIzaSyDkP68ZaeHeZZi105o9NSg--sgGZv2TPBE", temp=0)
            agent = Agent(task=prompt, llm=model, controller=controller)
            history = await agent.run()
            result = history.final_result()
            if result:
                try:
                    # First try to parse as regular JSON
                    try:
                        parsed: Posts = Posts.model_validate_json(result)
                        detected_xpath = parsed.posts[0].XPATH if parsed.posts else None
                    except Exception as json_error:
                        print(f"Standard JSON parsing failed: {json_error}")
                        # Fallback: manual extraction of XPATH from the result
                        try:
                            import re
                            xpath_match = re.search(r'"XPATH"\s*:\s*"([^"]+)"', result)
                            detected_xpath = xpath_match.group(1) if xpath_match else None
                            print(f"Manually extracted XPath: {detected_xpath}")
                        except Exception as manual_error:
                            print(f"Manual extraction failed: {manual_error}")
                            detected_xpath = None

                    if detected_xpath and existing_xpath != detected_xpath:
                        print(f"XPath MISMATCH for {variable_name}!")
                        print(f"Old: {existing_xpath}")
                        print(f"New: {detected_xpath}")
                        updates.append({
                            'Variable_Name': variable_name,
                            'Old_XPath': existing_xpath,
                            'New_XPath': detected_xpath
                        })
                        df.at[index, 'Locator_Value'] = detected_xpath
                    elif detected_xpath:
                        print(f"XPath MATCH for {variable_name} - No update needed")
                        unchanged_elements.append(variable_name) # Add to unchanged list
                    else:
                        print(f"No XPath detected for {variable_name}. Existing value retained.")
                        print(f"Raw result: {result}")
                        unchanged_elements.append(variable_name) # Add to unchanged list
                except Exception as e:
                    print(f"Error parsing result for {variable_name}: {e}")
                    print(f"Raw result: {result}")
                    errors.append({'Variable_Name': variable_name, 'Error': str(e), 'XPath': existing_xpath})
            else:
                print(f'No result for {variable_name}')
                errors.append({'Variable_Name': variable_name, 'Error': "No result from agent", 'XPath': existing_xpath})
        except Exception as e: # Catch agent errors
            print(f"Agent error for {variable_name}: {e}")
            errors.append({'Variable_Name': variable_name, 'Error': str(e), 'XPath': existing_xpath})
    end_time = datetime.now()
    duration = end_time - start_time

    report_data = {
        'run_id': run_id,
        'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
        'duration': str(duration),  # Keep as string for report
        'total_elements': len(df),
        'updated_elements': len(updates),
        'error_elements': len(errors),
        'updates': updates,
        'errors': errors,
        'unchanged_elements': unchanged_elements,
        'xpath_map': xpath_map, # Include XPath mapping
    }
    html_report = generate_html_report(report_data)
    report_filename = f"selfheal_report_{start_time.strftime('%Y%m%d_%H%M%S')}.html"
    report_path = save_report(html_report, report_filename)

    if updates:
        print("\nUpdates made:")
        for update in updates:
            print(f"- {update['Variable_Name']}: '{update['Old_XPath']}' → '{update['New_XPath']}'")
        df.to_csv(input_file, index=False)
        print(f"\nUpdated CSV file saved to {input_file}")
    else:
        print("\nNo XPath updates needed - all locators are current")
    print(f"\nReport generated: {report_path}")

async def main():
    await update_xpaths()

if __name__ == '__main__':
    asyncio.run(main())