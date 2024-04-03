1. run ENV_setup.bat - downloads the arduino library and vscode setup to this folder, sets the local dir variable
2. build using esp idf v5.1.2
 2.1 cmake should copy the arduino component and .vscode into the build project
 2.2 builder should get more data

The git settings were changed so that projects 1 and 2 cannot be built this way. They need the original DW1000 library from makerfabs.