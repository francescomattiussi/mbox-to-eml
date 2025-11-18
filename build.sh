#!/bin/bash

# Navigate to the src directory
cd src

# Use PyInstaller to create the executable
pyinstaller --onefile --windowed mbox_to_eml_gui.py

# Move the generated executable to the root directory
mv dist/mbox_to_eml_gui ../

# Clean up the build files
cd ..
rm -rf build dist mbox_to_eml_gui.spec

echo "Build completed. The executable is located in the root directory."