You are a developer working on a React (Vite + TypeScript) application.

Here are the current source files in the project:
{current_workspace_context}

Please implement the following ticket:
{task_desc}
{feedback_note_attempt}

You MUST implement the requested changes in the codebase AND write a corresponding automated pytest test file under `tests/test_example.py` to verify the functionality.{bug_test_instruction}
The pytest tests should run in a Python environment using Selenium WebDriver in headless mode to verify that the app behaves correctly at runtime.
Your test file `tests/test_example.py` should define test functions that setup a headless Selenium webdriver, navigate to 'http://localhost:5174' (where the workspace application runs), and perform functional/layout checks.

CRITICAL INSTRUCTIONS FOR BROWSER RUNTIME TESTS:
1. Always run Chrome in headless mode with parameters '--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', and '--remote-debugging-port=9222'.
2. Do NOT import or use 'webdriver_manager' or 'ChromeDriverManager'. Use standard 'webdriver.Chrome(options=chrome_options)' directly (Selenium 4 handles driver binaries automatically).
3. Use standard Selenium wait strategies (like WebDriverWait) to ensure components are loaded.
4. Assert on runtime properties (like element position, dimensions, computed visibility, or text content in the browser DOM) instead of reading source files as plain text.
5. CRITICAL RESPONSIVENESS REQUIREMENT: The application MUST be fully responsive and display correctly on both desktop (e.g. 1280px width) and mobile (e.g. 375px width) viewports. Ensure that your styling (CSS) accommodates different screen widths without content overlapping, getting truncated, or causing horizontal scrollbars on mobile. If you write automated Selenium tests, verify that layout and elements align correctly at both viewport sizes.
6. NO THIRD-PARTY LIBRARIES: Do NOT import or use third-party test wrappers such as 'seleniumbase'. Stick strictly to standard 'selenium' imports (e.g. `from selenium import webdriver`).
7. SCROLLBAR TOLERANCE: When comparing computed element widths against the viewport width in tests, do NOT assume they match exactly down to the pixel. Vertical scrollbars consume about 15-20px of space. Instead, assert that they match `document.documentElement.clientWidth` (which excludes scrollbar width) or allow a tolerance of at least 20px (e.g. `abs(header_width - viewport_width) <= 20`).
8. CLEAN UP OVERRIDDEN STYLES: When updating or moving layouts (e.g., changing header positioning), ensure you clean up and remove any old properties (such as relative centering offsets like `left: 50%` or `transform: translateX(-50%)`) rather than leaving them to conflict with the new styles.

CRITICAL REQUIREMENT FOR TEST CASES:
Each test case function in `tests/test_example.py` MUST contain a docstring formatted EXACTLY like this:
\"\"\"<Short title of the test>

<Detailed description of the test>

id: TST-<unique 4-digit number>
req: {parent_id}
Given: <Preconditions for the test>
When: <Action or triggers taken in the test>
Then: <Expected outcomes or assertions>
\"\"\"

Example:
\"\"\"Test home page header layout.

Verify that the app homepage header is fixed at the top and the main content does not overlap it.

id: TST-1001
req: {parent_id}
Given: The Vite app is running
When: Opening the page in headless Chrome and checking element positions
Then: The header bounding box y is 0, and the content container y is greater than or equal to the header height
\"\"\"

Modify the necessary files to implement the requested changes. Only output files that need to be changed or created.

IMPORTANT: Respond ONLY with file blocks in this exact format (no markdown fences):
=== FILE: src/App.tsx ===
<full file content here>
=== END FILE ===
=== FILE: tests/test_example.py ===
<full pytest test content here>
=== END FILE ===

You may output multiple file blocks. Each block must contain the COMPLETE file content (not a diff). Do NOT include any other text outside the file blocks.
