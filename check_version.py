import subprocess

def check_versions(requirements_file):
    with open(requirements_file, 'r') as file:
        packages = file.readlines()
    
    for package in packages:
        package_name = package.split('==')[0]
        current_version = package.split('==')[1].strip()
        
        # Use pip to get the latest version of the package
        latest_version = subprocess.run(
            ['pip', 'index', 'versions', package_name],
            capture_output=True, text=True
        ).stdout.split('\n')[1].strip().split(' ')[-1]
        
        print(f"{package_name}: current version: {current_version}, latest version: {latest_version}")

check_versions('requirements.txt')
