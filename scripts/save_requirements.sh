#! /bin/bash

save_reqs_with="$1"
output_path="$2"
check_file_path="$3"

# Get the current directory (i.e. where this file exists).
#script_dirname="$(dirname "$0")"

# Activate the virtual environment if you're using one.
 source "./../venv/bin/activate"

# Global vars to control file creation and prompting conditional logic.
create_file=false
prompt_flag=true

# Display target path for requirements file
# echo "Out path: $output_path"

# Function used to generate prompt. Will regenerate on invalid input.
prompt_user () {
#  read -rp "The $check_file_path file does not exist. Would you like to create one? [y/n]: " res
  read -rp "take input" res
}

# If the requirements file doesn't exist, ask if user wants to generate one
if ! [ -f "$check_file_path" ]
then
  while [ $prompt_flag = true ];
  do
    prompt_user

    if ! [[ $res == 'y' ]] || [[ $res == 'n' ]]
    then
      echo "Invalid response. Please select either 'y' or 'n'"
    elif [[ $res == 'y' ]]
    then
      prompt_flag=false
      create_file=true
    else
      prompt_flag=false
      create_file=false
    fi
  done
else
  echo "Requirements file found. Freezing requirements..."
  if [[ $save_reqs_with == 'pipreqs' ]]
  then
    pipreqs --force "$output_path"
  elif [[ $save_reqs_with == 'pip' ]]
  then
    pip3 freeze > "$output_path"
  else
    echo "Invalid option $save_reqs_with passed" 1>&2
    exit 1
  fi
fi

# Create the file based on the flag.
if [ $create_file ]
then
  # Display resulting flags and output path
  # echo "create_file = $create_file"
  # echo "prompt_flag = $prompt_flag"
  # echo "Creating requirements file in $out_path"

  # Make sure Python is aliased properly when not using path to binary.
  # pip3 freeze --exclude-editable > "$out_path"

  if [[ $save_reqs_with == 'pipreqs' ]]
  then
    pipreqs --force "$output_path"
  elif [[ $save_reqs_with == 'pip' ]]
  then
    pip3 freeze > "$output_path"
  else
    echo "Invalid option $save_reqs_with passed" 1>&2
    exit 1
  fi
fi

# Deactivate virtual environment if used.
 deactivate
