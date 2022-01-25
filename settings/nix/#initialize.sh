export __FORNIX_NIX_SETTINGS_PATH="$FORNIX_FOLDER/settings/nix/settings.toml"
export __FORNIX_NIX_MAIN_CODE_PATH="$FORNIX_FOLDER/settings/nix/parse_dependencies.nix"
export __FORNIX_NIX_PACKAGES_FILE_PATH="$FORNIX_FOLDER/settings/requirements/nix.toml"
export __FORNIX_NIX_PATH_EXPORT_FILE="$FORNIX_FOLDER/settings/.cache/dependency_paths.dont-sync.json"
export __FORNIX_NIX_COMMANDS="$FORNIX_FOLDER/settings/nix/commands"


# 
# connect shell.nix
# 
# unlink existing
rm -f "$FORNIX_FOLDER/settings/requirements/shell.nix" 2>/dev/null
rm -rf "$FORNIX_FOLDER/settings/requirements/shell.nix" 2>/dev/null
# syslink local tools
ln -s "../nix/shell.nix" "$FORNIX_FOLDER/settings/requirements/shell.nix"

# 
# connect nix.toml
# 
# unlink existing
rm -f "$FORNIX_FOLDER/settings/requirements/nix.toml" 2>/dev/null
rm -rf "$FORNIX_FOLDER/settings/requirements/nix.toml" 2>/dev/null
# syslink local tools
ln -s "../nix/nix.toml" "$FORNIX_FOLDER/settings/requirements/nix.toml"

# 
# connect commands
# 
# unlink existing
rm -f "$FORNIX_FOLDER/commands/tools/nix" 2>/dev/null
rm -rf "$FORNIX_FOLDER/commands/tools/nix" 2>/dev/null
# syslink local tools
ln -s "../../settings/nix/commands" "$FORNIX_FOLDER/commands/tools/nix"