import os
import json
import shutil
import platform
import sys
import subprocess
import pkg_resources

def access_resource(relative_path='templates'):
    return pkg_resources.resource_filename('nuisco', relative_path)

def load_template_configs(templates_dir='templates'):
    configs = {}
    templates_dir = access_resource(templates_dir)
    for template_name in os.listdir(templates_dir):
        template_dir = os.path.join(templates_dir, template_name)
        if os.path.isdir(template_dir):
            config_file = os.path.join(template_dir, f"{template_name}-config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    configs[template_name] = json.load(file)
    return configs

def execute_placeholder_code(code):
    print(f"Executing Python code: {code}")
    confirmation = input("Do you want to execute this code? (yes/no): ")
    if confirmation.lower() == 'yes':
        try:
            return str(eval(code))
        except Exception as e:
            return f"Error executing code: {e}"
    else:
        return "Execution cancelled by user"

def get_file_path_content(dest_file_path):
    try:
        with open(dest_file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        try:
            return ""
            with open(dest_file_path, 'rb') as file:
                content = file.read()
            return content#bytes(placeholder, 'utf-8') in content
        except Exception as e:
            print(f"Error processing {dest_file_path}: {e}")
            return ""

def create_template(project_name, template_name, templates_dir='templates', pyversion=None, github=False, install_requirements=False):
    configs = load_template_configs(templates_dir)
    templates_dir = access_resource(templates_dir)
    config = configs.get(template_name)
    if not config:
        raise ValueError(f"Template {template_name} configuration not found")

    target_path = os.path.join(os.getcwd(), project_name)
    if os.path.exists(target_path):
        raise ValueError(f"Project {project_name} already exists")

    pyversion = pyversion or f"{sys.version_info.major}.{sys.version_info.minor}"
    template_args = {'project_name': project_name, 'pyversion': pyversion, 'github': github}

    template_path = os.path.join(templates_dir, template_name)
    files_to_include = config.get('files', [])
    files_to_include += config.get('os_specific', {}).get(platform.system(), [])
    if github:
        files_to_include += config.get('github_files', [])

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    # Handle dependencies
    dependencies_config = config.get('dependencies', {})
    requirements_files = dependencies_config.get('requirements_files')
    direct_dependencies = dependencies_config.get('direct_dependencies', [])
    force_install = dependencies_config.get('force_install_direct_dependencies', False)

    unique_dependencies = set(direct_dependencies)
    for requirements_file in requirements_files:
        requirements_path = os.path.join(template_path, requirements_file or 'requirements.txt')
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                for line in f:
                    unique_dependencies.add(line.strip())

    # Create requirements.txt in the new project
    requirements_file_path = os.path.join(target_path, 'requirements.txt')
    with open(requirements_file_path, 'w') as req_file:
        for dependency in unique_dependencies:
            req_file.write(dependency + '\n')

    # Install direct dependencies immediately if required
    if force_install:
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + direct_dependencies)

    for file_name in files_to_include:
        print(f"Creating {template_path}{file_name}")
        src_file_path = os.path.join(template_path, file_name)
        dest_file_path = os.path.join(target_path, file_name)

        # Create the directories for the destination file if they do not exist
        dest_directory = os.path.dirname(dest_file_path)
        if not os.path.exists(dest_directory):
            os.makedirs(dest_directory)

        if not os.path.exists(src_file_path):
            print(f"Warning: Source file {src_file_path} does not exist. Skipping.")
            continue

        shutil.copy(src_file_path, dest_file_path)

        content = get_file_path_content(dest_file_path)#find_placeholders_in_file()

        for placeholder, value in config.get('placeholders', {}).items():
            if value.startswith('exec:'):
                code = value.split('exec:', 1)[1]
                content = content.replace(f"{{{{{placeholder}}}}}", execute_placeholder_code(code))
            else:
                content = content.replace(f"{{{{{placeholder}}}}}", template_args.get(placeholder, ''))

        with open(dest_file_path, 'w') as file:
            file.write(content)
            
    # Install all requirements at the end if required
    if install_requirements:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file_path])

# Usage
if __name__ == "__main__":
    create_template('my_new_project', 'ppt', pyversion=None, github=True, install_requirements=True)
