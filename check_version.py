import subprocess

def check_versions(requirements_file):
    with open(requirements_file, 'r') as file:
        packages = file.readlines()
    
    for package in packages:
        if '==' in package:
            package_name = package.split('==')[0]
            current_version = package.split('==')[1].strip()
        else:
            package_name = package.strip()
            current_version = "N/A"

        try:
            result = subprocess.run(
                ['pip', 'index', 'versions', package_name],
                capture_output=True, text=True
            ).stdout.split('\n')
            
            # Find the line that contains "LATEST"
            latest_version_line = next(line for line in result if "LATEST" in line)
            latest_version = latest_version_line.split()[-1]
            
            print(f"{package_name}: current version: {current_version}, latest version: {latest_version}")
        
        except StopIteration:
            print(f"Could not determine latest version for {package_name}")

check_versions('requirements.txt')
