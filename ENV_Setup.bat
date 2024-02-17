set "repo_url=https://github.com/janjir1/build_settitngs.git"

set "destination_dir=%~dp0build_settitngs"

git clone %repo_url% %destination_dir%

set "repo_url=https://github.com/janjir1/components.git"

set "destination_dir=%~dp0components"

git clone %repo_url% %destination_dir%

setx ESP_UWB_ROOT_DIR %~dp0
echo %ESP_UWB_ROOT_DIR%

pause
