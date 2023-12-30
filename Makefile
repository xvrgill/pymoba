save_requirements_script := scripts/save_requirements.sh

# Ensure that pip is up to date.
update_pip:
	pip3 install --upgrade pip

# Install Python package requirements.
save_requirements: update_pip
	$(save_requirements_script)

install_editable: update_pip
	pip3 install -e .
