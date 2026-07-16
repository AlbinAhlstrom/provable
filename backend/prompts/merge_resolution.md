You are a senior software engineer resolving a git merge conflict in the file '{fname}'.
         
Here is the content of the file containing merge conflict markers:
{content}

Please resolve all the conflict markers ('<<<<<<< HEAD', '=======', '>>>>>>>') in this file and combine the changes from both sides logically and cleanly.

CRITICAL REQUIREMENTS:
1. Do NOT include any git conflict markers ('<<<<<<< HEAD', '=======', '>>>>>>>') in your output.
2. If you are resolving conflicts in CSS files (especially 'src/index.css'), you MUST ensure that the 'body {{ ... }}' style block is placed BEFORE the 'html, body {{ ... }}' style block (or similar) to prevent regex/index matching errors in the test suite.
3. Output the COMPLETE resolved file contents and absolutely NOTHING else. No markdown block formatting, no explanation, just the plain text of the resolved file.
4. Keep modifications minimal and preserve the exact styling rules and declarations of unaffected lines. Do not merge body block properties (like font-size) into the global html, body block.
