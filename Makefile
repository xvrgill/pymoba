#save_requirements_script := scripts/save_requirements.sh
save_requirements_script := scripts/save_requirements.py

# Ensure that pip is up to date.
update_pip:
	pip3 install --upgrade pip

# Install Python package requirements.
save_requirements: update_pip
	python3 $(save_requirements_script)

install_editable: update_pip
	pip3 install -e .
