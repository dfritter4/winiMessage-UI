import os

def count_lines_of_code(directory, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = set()
    total_lines = 0

    for root, dirs, files in os.walk(directory):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Count non-empty, non-comment lines
                        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
                        total_lines += code_lines
                        print(f"{file_path}: {code_lines} lines")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    print(f"Total lines of code: {total_lines}")

if __name__ == "__main__":
    folder = input("Enter the folder path: ").strip()
    if os.path.isdir(folder):
        count_lines_of_code(folder, exclude_dirs={'venv'})
    else:
        print(f"Invalid folder path: {folder}")
