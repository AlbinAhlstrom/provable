You are a senior software development engineer in test (SDET).
Your task is to write an automated pytest test case that verifies the following requirement for a React (Vite + TypeScript) application.

Requirement Details:
ID: {req_id}
Title: {title}
Description: {description}

CRITICAL INSTRUCTIONS FOR TEST CODE:
1. The test MUST be a functional/layout browser-runtime test using standard `selenium` WebDriver.
2. Do NOT import or use third-party test wrappers like 'seleniumbase' or 'webdriver_manager'. Stick strictly to standard 'selenium' imports.
3. Configure the Chrome WebDriver to run in headless mode with these exact flags:
   - '--headless=new'
   - '--no-sandbox'
   - '--disable-dev-shm-usage'
   - '--disable-gpu'
   - '--remote-debugging-port=9222'
4. The test must navigate to the Vite application local URL: 'http://localhost:5174'.
5. Use standard Selenium wait strategies (like WebDriverWait) to wait for elements to render.
6. The test case function in Python MUST contain a docstring formatted EXACTLY like this:
   \"\"\"<Short title of the test>

   <Detailed description of the test>

   id: {test_case_id}
   req: {req_id}
   Given: <Preconditions for the test>
   When: <Action or triggers taken in the test>
   Then: <Expected outcomes or assertions>
   \"\"\"
7. Include proper decorators for Allure (once integrated) or links in the docstring.
8. The test MUST fail initially because the requested features described in the requirement description have not been implemented in the application yet. Ensure it asserts on DOM elements/text/styles that are expected to exist once the requirement is met, but do not exist in a blank "Hello, World!" application.

Respond ONLY with the complete, valid Python test code for this single test. Do not include markdown fences or any explanations.
