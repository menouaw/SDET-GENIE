from browser_use import Agent, Controller, ActionResult
from browser_use.browser.context import BrowserContext
from typing import Optional
import json
from pydantic import BaseModel

class elment_on_page(BaseModel):

    index: int
    xpath: Optional[str] = None

class Post(BaseModel):
    XPATH: str

class Posts(BaseModel):
    posts: list[Post]

controller = Controller(output_model=Posts)

@controller.action("Get XPath of element using index", param_model=elment_on_page)
async def get_xpath_of_element(params: elment_on_page, browser: BrowserContext):
    session = await browser.get_session()
    state = session.cached_state

    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    element_node = state.selector_map[params.index]
    absolute_xpath = element_node.xpath
    if absolute_xpath is None:
        return ActionResult(error="Element not found, try another index")
    relative_xpath = '/' + absolute_xpath if absolute_xpath.startswith('/') else absolute_xpath

    try:
        if hasattr(element_node, 'attributes') and element_node.attributes:
            attrs = element_node.attributes
            tag_name = element_node.tag_name if hasattr(element_node, 'tag_name') else None

            if tag_name:
                # Use double quotes consistently in XPath expressions
                if 'id' in attrs and attrs['id']:
                    relative_xpath = f"//{tag_name}[@id=\"{attrs['id']}\"]"
                elif 'class' in attrs and attrs['class']:
                    relative_xpath = f"//{tag_name}[contains(@class, \"{attrs['class']}\")]"
                elif 'name' in attrs and attrs['name']:
                    relative_xpath = f"//{tag_name}[@name=\"{attrs['name']}\"]"
    except Exception as e:
        print(f"Error generating relative xpath: {e}")
        # Fall back to absolute xpath if there's an error

    # Create the Posts object
    posts = Posts(posts=[Post(XPATH=relative_xpath)])

    # Use custom JSON encoding to avoid escaping issues
    custom_json = json.dumps(posts.model_dump(), ensure_ascii=False)
    return ActionResult(
        extracted_content=f"The relative xpath of the element is {relative_xpath}",
        include_in_memory=True,
        # Use raw string to bypass controller's JSON serialization
        raw_output=custom_json
    )