import os, re

frontend_dir = r'c:\Users\Win-11\PersonalProjects\Stick2It\frontend\src'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    # Replace 'http://localhost:8000...' with `${import.meta.env.VITE_API_URL}...`
    # Case 1: Double quotes
    content = re.sub(r'\"http://localhost:8000([^\"]*)\"', r'`${import.meta.env.VITE_API_URL}\1`', content)
    # Case 2: Single quotes
    content = re.sub(r'\'http://localhost:8000([^\']*)\'', r'`${import.meta.env.VITE_API_URL}\1`', content)
    # Case 3: Backticks
    content = re.sub(r'`http://localhost:8000([^`]*)`', r'`${import.meta.env.VITE_API_URL}\1`', content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
            process_file(os.path.join(root, file))

print('Done replacing.')
