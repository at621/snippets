import os

def write_readme(folder_path, content):
    with open(f"{folder_path}/Readme.md", "w") as f:
        f.write(content)

def create_project_structure(project_name, product_name=None):
    # Create root directory
    root_dir = f"{product_name}/{project_name}" if product_name else project_name
   
    # List of folder names to be created under the project
    folders = ["src", "tests", "models", "data", "pipeline", "docs"]
   
    # Descriptions for each folder
    descriptions = {
        "src": "The folder that consists of the source code related to data gathering, data preparation, feature extraction, etc.",
        "tests": "The folder that consists of the code representing unit tests for code maintained within the src folder.",
        "models": "The folder that consists of files representing trained/retrained models.",
        "data": "The folder consists of data used for model training/retraining.",
        "pipeline": "The folder consists of code that's used for retraining and testing the model in an automated manner.",
        "docs": "The folder that consists of code related to the product requirement specifications (PRS), technical design specifications (TDS), etc."
    }
   
    # Create the project root folder
    os.makedirs(root_dir, exist_ok=True)
   
    # Create Readme.md inside the project root folder
    write_readme(root_dir, "# Project Readme\nThis is the root directory of the project.")
   
    # Create sub-folders inside the project root folder
    for folder in folders:
        folder_path = f"{root_dir}/{folder}"
        os.makedirs(folder_path, exist_ok=True)
       
        # Create Readme.md for each sub-folder
        write_readme(folder_path, f"# {folder.capitalize()} Folder\n{descriptions[folder]}")

# Create single project structure
create_project_structure("project_name")

# Create multiple project structures under different product lines
create_project_structure("project_name_1", "product_name_1")
create_project_structure("project_name_2", "product_name_1")
create_project_structure("project_name_1", "product_name_2")
