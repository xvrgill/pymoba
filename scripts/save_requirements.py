import yaml
import subprocess
from pathlib import Path
import pexpect

with open('../config.yaml', 'r') as config:
    config_data = yaml.safe_load(config)

project_settings = config_data['project']
make_settings = project_settings['make_settings']
save_reqs_with = make_settings['save_requirements_with']
script_path = Path(project_settings['script_path'])

# Validate requirement options
valid_save_reqs_with_options = [
    'pipreqs',
    'pip'
]

if save_reqs_with not in valid_save_reqs_with_options:
    __msg__ = 'Invalid option for saving project requirements. Valid options: '
    f'{", ".join(valid_save_reqs_with_options)}. Selected option: {save_reqs_with}'
    raise ValueError(__msg__)

# Define output path specification depending on config
if save_reqs_with == 'pipreqs':
    output_path = '/'.join(['.', '..'])
    check_file_path = '/'.join([output_path, 'requirements.txt'])
elif save_reqs_with == 'pip':
    output_path = script_path / '..' / 'requirements.txt'
    check_file_path = output_path
else:
    __msg__ = 'No output path set for saving project requirements'
    raise ValueError(__msg__)

# Construct bash script
bash_script = Path('./save_requirements.sh')
print(f'Script path: {bash_script}')
bash_command = [str(bash_script.absolute()), save_reqs_with, str(output_path), str(check_file_path)]

# Run bash script
child = pexpect.spawn(bash_command[0], bash_command[1:])
try:
    child.expect("take input")
    answer = input(f"The {check_file_path} file does not exist. Would you like to create one? [y/n]: ")
    child.sendline(answer)
    child_output = child.read().decode()
    print(child_output)
except pexpect.EOF:
    child_output = child.before.decode()
    print(child_output)

child.close()

# with subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                       stdin=subprocess.PIPE, universal_newlines=True) as process:
#     try:
#         stdout, stderr = process.communicate(timeout=60)  # Set a timeout (in seconds)
#         print("STDOUT:", stdout)
#         print("STDERR:", stderr)
#     except subprocess.TimeoutExpired:
#         print("Subprocess timed out.")
#         process.kill()  # Terminate the subprocess if it times out

