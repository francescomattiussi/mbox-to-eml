# mbox-to-eml Project

This project provides a graphical user interface (GUI) tool for exporting emails from an MBOX file to EML format. It is designed to help users easily convert their email archives into a more accessible format.

## Features

- **Export Emails**: Convert emails from MBOX format to individual EML files.
- **GUI Interface**: User-friendly interface for selecting MBOX files and output directories.
- **Filename Sanitization**: Automatically sanitizes filenames to avoid issues with invalid characters.
- **Progress Tracking**: Displays progress during the export process.

## Requirements

To run this project, you need to have the following Python packages installed:

- `tkinter`
- `email`
- `mailbox`

You can install the required packages using the following command:

```
pip install -r requirements.txt
```

## Usage

### Running the Program

You can run the program in two ways:

1. **Using the GUI**: Simply execute the script `src/mbox_to_eml_gui.py` to launch the graphical interface.

2. **Command Line**: You can also run the script from the command line by providing the MBOX file and output directory as arguments:

   ```
   python src/mbox_to_eml_gui.py <path_to_mbox_file> <output_directory>
   ```

### Building the Executable

To create an executable file for distribution, you can use the provided build scripts:

- For Unix-based systems, run:

  ```
  ./build.sh
  ```

- For Windows, run:

  ```
  build.bat
  ```

This will generate an executable that you can share with your colleagues.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.