import os
import subprocess
import re

def format_code_block(language, code):
    # Temporary file to hold code before formatting
    temp_file = "temp_code_file"
    
    with open(temp_file, "w") as f:
        f.write(code)
    
    if language == "cpp":
        subprocess.run(["clang-format", "-i", temp_file])
    elif language == "rust":
        subprocess.run(["rustfmt", temp_file])
    
    # Read back the formatted code
    with open(temp_file, "r") as f:
        formatted_code = f.read()
    
    os.remove(temp_file)
    
    return formatted_code

def process_markdown_file(filepath):
    with open(filepath, "r") as file:
        content = file.read()
    
    # Regular expression to find code blocks with specific language
    pattern = re.compile(r"```(\w+)\n(.*?)\n```", re.DOTALL)
    
    def replace_code_block(match):
        language = match.group(1)
        code = match.group(2)
        formatted_code = format_code_block(language, code)
        return f"```{language}\n{formatted_code}\n```"
    
    new_content = pattern.sub(replace_code_block, content)
    
    with open(filepath, "w") as file:
        file.write(new_content)

def format_markdown_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                process_markdown_file(filepath)

if __name__ == "__main__":
    format_markdown_files(f"{os.path.dirname(os.path.realpath(__file__))}/../_posts")
