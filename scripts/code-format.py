import os
import subprocess
import re

def format_code_block(language, code):
    
    # extend this with other formatters
    if language == "cpp" or language == "c":
        formatted_code = format_cxx_snippet(code,language)
    elif language == "rust":
        formatted_code = format_rust_snippet(code)
    elif language == "shell":
        formatted_code = code
    else:
        raise Exception(f"unknown language '{language}'")

    return formatted_code

def format_cxx_snippet(code, language='cpp'):
    # Define a temporary file name
    temp_file = f"temp_code_file.{language}"
    
    # Wrap the snippet in a minimal C/C++ main function
    wrapped_code = f"int main() {{\n{code}\n}}"

    # Write the wrapped code to the temporary file
    with open(temp_file, "w") as f:
        f.write(wrapped_code)
    
    # Run clang-format on the temporary file
    subprocess.run(["clang-format-18", "-i", temp_file])

    # Read back the formatted code
    with open(temp_file, "r") as f:
        formatted_code = f.read()

    # Extract the formatted snippet (removing the wrapping)
    formatted_snippet = extract_cpp_snippet(formatted_code)

    # Clean up the temporary file
    os.remove(temp_file)
    
    return formatted_snippet

def extract_cpp_snippet(formatted_code):
    # Regex pattern to extract code inside main function
    pattern = r"int\s+main\s*\(\)\s*\{\s*([\s\S]*?)\s*\}"
    match = re.search(pattern, formatted_code)
    if match:
        return match.group(1).strip()  # Return the code inside the main function
    else:
        raise Exception("this should not happen, cxx snippet not wrapped in main")


def format_rust_snippet(code):
    # Define a temporary file name
    temp_file = "temp_code_file.rs"
    
    # Wrap the snippet in a minimal Rust main function
    wrapped_code = f"fn main() {{\n{code}\n}}"

    # Write the wrapped code to the temporary file
    with open(temp_file, "w") as f:
        f.write(wrapped_code)
    
    # Run rustfmt on the temporary file
    result = subprocess.run(["rustfmt", temp_file])
    if result.returncode != 0:
        raise Exception("Formatter returned with errors")

    # Read back the formatted code
    with open(temp_file, "r") as f:
        formatted_code = f.read()

    # Remove the wrapping (extract the original snippet back)
    # This assumes that the snippet was correctly placed within the main function
    formatted_snippet = extract_rust_snippet(formatted_code)

    # Clean up the temporary file
    os.remove(temp_file)
    
    return formatted_snippet
   
def extract_rust_snippet(formatted_code):
    # Regex pattern to extract code inside main function
    pattern = r"fn\s+main\s*\(\)\s*\{\s*([\s\S]*?)\s*\}"
    match = re.search(pattern, formatted_code)
    if match:
        return match.group(1).strip()  # Return the code inside the main function
    else:
        raise Exception("this should not happen, rust snippet not wrapped in main")

def process_markdown_file(filepath):
    print(f"processing '{filepath}'")
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
