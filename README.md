# Image Grid Creator Script

## Description

This Python script automates the process of creating a contact sheet or proof sheet from a folder of PNG images. It arranges the images in a grid, adds sequential numbers above each image, provides spacing, optionally resizes images for smaller output, and saves the final composite grid as a single PNG file.

The script **automatically determines a project name** based on the name of the folder containing the script (`make_grid.py`) and includes this name, along with the grid dimensions, in the output filename.

It also includes an optional feature to copy the original images into a separate folder, renaming them according to their grid number.

This is useful for presenting multiple design options, photos, or assets to clients or team members, allowing them to easily reference specific items by number.

## Features

- Loads all `.png` images from a specified input folder.
- Automatically calculates grid dimensions (rows/columns) to be roughly square.
- Optionally resizes images to a target width (maintaining aspect ratio) to control output file size.
- Adds configurable spacing between images in the grid.
- Numbers each image sequentially, displaying the number in the space above it.
- Customizable font size and color for numbers.
- Customizable background color for the grid canvas (including transparent).
- Handles image loading errors gracefully, skipping problematic files and reporting them.
- **Generates a dynamic output filename** including a project name (derived from the script's parent folder) and the final grid dimensions (e.g., `project-folder-name_grid_2048x1600.png`).
- **Optional:** Copies original images to a separate output folder, renaming them sequentially (e.g., `1.png`, `2.png`, ...) based on their grid position, leaving original files untouched.

## Requirements

- **Python 3:** The script is written for Python 3.
- **Pillow Library:** The Python Imaging Library (Pillow fork) is required for image manipulation.

### Installation

1.  **Python 3:** Ensure you have Python 3 installed on your system. You can download it from [python.org](https://www.python.org/).
2.  **Pillow:** Install the Pillow library using pip. It's highly recommended to use a Python virtual environment to avoid conflicts with system packages (especially on macOS and Linux distributions implementing PEP 668).

    ```bash
    # Optional: Create and activate a virtual environment in your project folder
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`

    # Install Pillow
    pip install Pillow
    ```

## Usage

1.  **Prepare Images:** Place all the PNG images you want to include in the grid into a single folder (e.g., `input_images`).
2.  **Save Script:** Place the `make_grid.py` script file inside your main project folder. The name of this folder will be used as the project name in the output filename.
3.  **Run Script:** Open your terminal or command prompt, navigate to the directory where you saved the script (`make_grid.py`), and run it using Python 3:

    ```bash
    # Activate virtual environment if you created one
    # source venv/bin/activate

    python make_grid.py
    ```

4.  **Follow Prompts:** The script will ask for:

    - **Input Folder:** The path to the folder containing your PNG images. Press Enter to use the default (`./input_images`). The script will confirm the project name derived from its containing folder.
    - **Output Directory:** Where to save the final grid image. Press Enter for the current directory (`.`).
    - **(Optional) Copy & Rename Confirmation:** If the `COPY_AND_RENAME_FILES` flag is enabled in the script, it will ask for confirmation before copying/renaming files.

5.  **Output:**
    - **Grid Image:** A single PNG file will be created in the specified output directory. The filename will be dynamically generated based on the script's parent folder name and the grid dimensions (e.g., `your-project-folder_grid_3000x2500.png`).
    - **(Optional) Renamed Images Folder:** If the copy/rename feature was enabled and confirmed, a new folder (default: `./renamed_grid_images`) will be created containing copies of your original input images, renamed sequentially (`1.png`, `2.png`, etc.).

## Configuration

You can easily customize the script's behavior by modifying the variables in the **Configuration** section near the top of the `make_grid.py` file:

- `DEFAULT_INPUT_FOLDER`: Default path for the image source folder.
- `DEFAULT_OUTPUT_DIR`: Default directory where the final grid image is saved.
- `BACKGROUND_COLOR`: Background color of the grid canvas (e.g., `'white'`, `'black'`, `'grey'`, `'transparent'`). Transparency requires RGBA mode.
- `TARGET_IMAGE_WIDTH`: Set to a pixel value (e.g., `512`) to resize wider images down. Set to `None` or `0` to disable resizing.
- `SPACING`: Gap in pixels between images in the grid.
- `NUMBER_AREA_HEIGHT`: Height in pixels of the space above each image reserved for the number.
- `NUMBER_COLOR`: Color name or hex code for the numbers (e.g., `'black'`, `'red'`, `'#FF0000'`). Set to `'none'` to disable numbering.
- `FONT_SIZE`: Font size for the numbers. Adjust for legibility based on `TARGET_IMAGE_WIDTH` and `NUMBER_AREA_HEIGHT`.
- `COPY_AND_RENAME_FILES`: Set to `True` to enable the feature that copies original files to a new folder with numbered names. Set to `False` to disable.
- `RENAMED_OUTPUT_FOLDER`: The name of the folder where copied/renamed files will be stored if the feature is enabled.

### Font Note

The script tries to find common system fonts (like Arial or DejaVuSans). If it fails, it uses a basic default font from Pillow, which might be small or low quality. For best results, you might need to:

1.  Install a common font like Arial or DejaVu Sans.
2.  Modify the `common_fonts` list in the script to include the full, correct path to a `.ttf` font file on your specific system.

## License

This script is released under the MIT License. (You may want to add a `LICENSE` file with the actual MIT license text).
