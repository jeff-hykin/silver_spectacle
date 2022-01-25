# ensure commands folder exists
if ! [[ -d "$FORNIX_COMMANDS_FOLDER" ]]; then
    # remove a potenial file
    rm -f "$FORNIX_COMMANDS_FOLDER"
    # make the folder
    mkdir -p "$FORNIX_COMMANDS_FOLDER"
fi