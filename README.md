# mbox-to-eml Project

This project provides a graphical user interface (GUI) tool for exporting emails from an MBOX file to EML format. It is designed to help users easily convert their email archives into a more accessible format.

## Features

- **Export Emails**: Convert emails from MBOX format to individual EML files.
- **GUI Interface**: User-friendly interface for selecting MBOX files and output directories.
- **Filename Sanitization**: Automatically sanitizes filenames to avoid issues with invalid characters.
- **Progress Tracking**: Displays progress during the export process.

## Requirements

To run this project, you need Python 3.6 or higher. The application uses built-in Python modules (`tkinter`, `email`, `mailbox`, etc.), so no additional packages are required via pip.

- On Windows and macOS, `tkinter` is included with Python.
- On Linux, you may need to install `tkinter` via your package manager (e.g., `sudo apt install python3-tk` on Ubuntu).

## Usage

### Running the Program

You can run the program in two ways:

1. **Using the GUI**: Simply execute the script `src/mbox_to_eml_gui.py` to launch the graphical interface.

2. **Command Line (Headless Mode)**: You can also run the script from the command line by providing the MBOX file and output directory as arguments:

   ```
   python src/mbox_to_eml_gui.py <path_to_mbox_file> <output_directory>
   ```

   This mode is useful for automation or when running in environments without a GUI.

## Docker Usage

The application can be run in a Docker container for easy deployment, especially in headless environments.

### Building the Docker Image

1. Ensure Docker is installed on your system.
2. Navigate to the project root directory.
3. Build the image:

   ```
   docker build -t mbox-to-eml .
   ```

### Running in Docker (Headless Mode)

The Docker version runs in headless mode by default. Mount your local directories containing the MBOX file and output folder:

```
docker run --rm -v /path/to/your/files:/app/data mbox-to-eml /app/data/input.mbox /app/data/output
```

- Replace `/path/to/your/files` with the absolute path to your local directory containing the MBOX file.
- The MBOX file should be named `input.mbox` (or adjust the path accordingly).
- Output EML files will be saved in the `output` subdirectory.

### Running GUI in Docker (Advanced)

If you need the GUI in Docker (e.g., on Linux with X11), ensure X11 forwarding is set up and run:

```
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /path/to/your/files:/app/data mbox-to-eml --gui
```

Note: GUI mode in Docker requires additional setup and may not work on all systems.

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