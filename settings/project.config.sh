# 
# NOTE: I wouldn't recommend adding new variables (or anything) here
# 
# (but the existing vars can be changed)


# TODO: in the future have a mechanism for walking up the current path to find the nearest parent project structure
# (instead of using PWD)
export FORNIX_FOLDER="$PWD"
export FORNIX_HOME="$FORNIX_FOLDER/settings/home/"
export FORNIX_COMMANDS_FOLDER="$FORNIX_FOLDER/commands/"

# 
# run all the setups
# 
# this loop is so stupidly complicated because of many inherent-to-shell reasons, for example: https://stackoverflow.com/questions/13726764/while-loop-subshell-dilemma-in-bash
for_each_item_in="$FORNIX_FOLDER/settings/"; [ -z "$__NESTED_WHILE_COUNTER" ] && __NESTED_WHILE_COUNTER=0;__NESTED_WHILE_COUNTER="$((__NESTED_WHILE_COUNTER + 1))"; trap 'rm -rf "$__temp_var__temp_folder"' EXIT; __temp_var__temp_folder="$(mktemp -d)"; mkfifo "$__temp_var__temp_folder/pipe_for_while_$__NESTED_WHILE_COUNTER"; (find "$for_each_item_in" -maxdepth 1 ! -path . -print0 2>/dev/null | sort -z > "$__temp_var__temp_folder/pipe_for_while_$__NESTED_WHILE_COUNTER" &); while read -d $'\0' each
do
    # check if file exists
    if [ -f "$each/#initialize.sh" ]
    then
        source "$each/#initialize.sh"
    fi
done < "$__temp_var__temp_folder/pipe_for_while_$__NESTED_WHILE_COUNTER";__NESTED_WHILE_COUNTER="$((__NESTED_WHILE_COUNTER - 1))"