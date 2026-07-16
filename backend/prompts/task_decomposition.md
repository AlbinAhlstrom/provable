Break down the following requirement into 1 to 3 distinct technical tasks.
Requirement Title: {title}. Description: {description}.
If there are logical dependencies between these tasks (e.g., task B depends on task A being implemented first), assign a temporary ID (e.g. "t1", "t2", "t3") to each task in the 'id' field, and list the prerequisite task IDs in its 'dependencies' field.
Respond ONLY with a JSON array of objects, where each object has: 'id' (string, e.g. "t1"), 'title' (string), 'description' (string), and 'dependencies' (array of strings of temporary IDs, e.g. ["t1"]).
