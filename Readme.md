# SDET-GENIE: AI-AGENTS in QA Automation --> @AGNO ^ @ Browser-use

![image](https://github.com/user-attachments/assets/87ecb2a9-0638-4dee-b630-74aed4e95326)

## 🚀 Project Overview

SDET-GENIE is a cutting-edge, AI-powered Quality Assurance (QA) automation framework that revolutionizes the software testing process. Leveraging advanced AI agents, SDET - GENIE transforms user stories directly into comprehensive, executable test automation code.

## 🌟 Key Features

### 1. AI-Powered QA Agent

- Converts user stories into detailed Gherkin scenarios
- Generates both positive and negative test cases
- Covers various user flows and edge conditions

### 2. Intelligent Browser Agent

- Automated browser interaction and test execution
- Dynamic element identification and mapping
- Comprehensive DOM detail capture
- Robust element selector generation

### 3. Code Generation Agent

- Produces production-ready automation code
- Supports multiple testing frameworks
- Adaptive to different application architectures

## 🔧 Technology Stack

- Python
- AI Models (Google Gemini 2.0 Flash)
- Selenium/Playwright
- Gherkin/Cucumber
- Browser Automation Technologies

## 📦 Installation - Quick start

install playwright:

```shell
playwright install
```

```bash

git clone https://github.com/WaiGenie/SDET-GENIE.git

cd SDET-GENIE

python -m venv .venv

.venv\Scripts\activate

pip install-requirements.txt

Create .env file
Place your GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXX

streamlit run app.py

```

## 🖥️ Quick Start

1. Prepare your user story
2. Run the AI agents
3. Generate and execute automated tests

## 🤝 Contributing

We're excited to welcome contributors to SDET-GENIE! Whether you're fixing bugs, improving documentation, or adding new features, your contributions are highly valued.

### 💡 Why Contribute?

- Gain experience with cutting-edge AI and test automation technologies
- Join a growing community of QA automation enthusiasts
- Help shape the future of AI-powered testing
- Get your name featured in our contributors list
- Learn best practices in test automation

### 🚀 Getting Started with Contributions

```
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests
5. Commit your changes
6. Push to your fork
7. Open a Pull Request
```

## 🔍 Areas for Contribution

- Bug fixes
- Documentation improvements
- New test automation framework support
- Performance optimizations
- Cloud browser provider integrations
- UI/UX improvements
- Test coverage enhancements

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0)

### License Highlights

✔️ Personal and educational use allowed

✔️ Code modification permitted

✔️ Copyright and license notices must be preserved

✔️ Source code must be disclosed when distributing

✔️ Changes must be released under the same license

❌ No commercial use without explicit permission

❌ No warranty provided

For full license details, see the [LICENSE](LICENSE) file or visit [GNU AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.en.html)

## 🤔 Questions or Need Help?

- Open a GitHub Discussion
- Check existing issues
- Join our community Discord - https://discord.gg/QqF68r39

## 📚 Blog Post

Read our in-depth article: [From User Stories to Automated Tests: The Future of QA Automation using AI Agents](https://medium.com/@honeyricky1m3/from-user-stories-to-automated-tests-the-future-of-qa-automation-using-ai-agents-cfe7fe878954)

Demo - https://youtu.be/z0fSNoUZTzw?si=xrfbDsGWlnTJzcYK

## 🌈 Acknowledgments

- Inspired by the challenges in modern software quality assurance
- Powered by cutting-edge AI technologies

## How it works:

```
1 - Entrypoint: User story about what to do in the website.
2 - prompt = generate_gherkin_scenarios(user_story)

3 - With browser context.


4 - Parse Gherkin scenarios.

5 - Execute each Gherkin scenario:
    - Start Browser with custom actions registered:
        Custom actions registered:
        -> "Get XPath of element using index"
        -> "Get element property"
        -> "Perform element action"

    # Execute and collect results
    history = await browser_agent.run()

6 - From browser history:
    -> Collect XPaths.
    -> Collect actions.
    -> Collect extracted content.

    # Combined history:
    # Save combined history to session state
    st.session_state.history = {
        "urls": history.urls(),
        "action_names": history.action_names(),
        "detailed_actions": all_actions,
        "element_xpaths": element_xpath_map,
        "extracted_content": all_extracted_content,
        "errors": history.errors(),
        "model_actions": history.model_actions(),
        "execution_date": st.session_state.get("execution_date", "Unknown")
    }

7 - Code generation:
    automation_code = generator_function(
        generated_steps,  # Generated Gherkin scenarios.
        history
    )
```
## 📝 Changelog
### Version 1.1.0 (19-03-2025) New Features:
- Editable Gherkin Scenarios : Users can now edit the AI-generated Gherkin scenarios directly in the application
- Save Changes Button : Added functionality to save edited scenarios with visual confirmation
- Persistent Scenarios : Saved scenarios remain visible in the UI until explicitly changed
- Execution Flow Improvement : Users must save changes before executing steps (with warning if unsaved changes exist)
- Code Generation Enhancement : Generated code now uses the edited scenarios instead of the original AI-generated ones
- UI Improvements : Simplified color scheme with sky blue theme for better readability Workflow Changes:
    1. Generate Gherkin scenarios from user story
    2. Edit scenarios if needed
    3. Click "Save Changes" button (required even if no edits were made)
    4. Click "Execute Steps" to run the saved scenarios
    5. Generate code based on the executed scenarios and browser history

**Made with ❤️ by the WaiGenie Team**
