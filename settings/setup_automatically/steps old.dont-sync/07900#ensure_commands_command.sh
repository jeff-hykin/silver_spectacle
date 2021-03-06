# create the "commands" command if it doesnt exist
if ! [[ -f "$FORNIX_COMMANDS_FOLDER/project/commands" ]]; then
    mkdir -p "$FORNIX_COMMANDS_FOLDER/project"
    echo '#!/usr/bin/env bash
    echo "project commands:"
    tree "$FORNIX_COMMANDS_FOLDER/project" -C --dirsfirst -A -F --noreport | sed '"'"'s/^/    /'"'"' | sed "1d"
    echo 
    echo "examples:"
    echo "    project clean"
    echo "    _ clean"
    ' > "$FORNIX_COMMANDS_FOLDER/project/commands"
fi

commands () {
    question="are you sure you want to show all commands? [y/n]";answer=''
    while true; do
        echo "$question"; read response
        case "$response" in
            [Yy]* ) answer='yes'; break;;
            [Nn]* ) answer='no'; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done

    if [[ "$answer" = 'yes' ]]; then
        # if tput exists
        if [ -n "$(command -v "tput")" ]
        then
            export COLOR_BLUE="$(tput setaf 4)"
            export COLOR_RED="$(tput setaf 1)"
            export COLOR_RESET="$(tput sgr0)"
        fi
            
        
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_BLUE"
        echo "#"
        echo "# built-ins"
        echo "#"
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_RESET"
        compgen -b | sed 's/^/    /'  # will list all the built-ins you could run.
        
        
        
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_BLUE"
        echo "#"
        echo "# keywords"
        echo "#"
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_RESET"
        compgen -k | sed 's/^/    /' # will list all the keywords you could run.
        
        
        
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_BLUE"
        echo "#"
        echo "# functions"
        echo "#"
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_RESET"
        compgen -A function | sed 's/^/    /'
        
        
        
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_BLUE"
        echo "#"
        echo "# aliases"
        echo "#"
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_RESET"
        compgen -a | sed 's/^/    /' # will list all the aliases you could run.
        
        
        
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_BLUE"
        echo "#"
        echo "# executables"
        echo "#"
        [ -n "$COLOR_BLUE" ] && echo "$COLOR_RESET"
        compgen -c | sed 's/^/    /'
        
    else
        echo "okay"
    fi
}
