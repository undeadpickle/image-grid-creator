# -*- coding: utf-8 -*-
import os
import math
from PIL import Image, ImageDraw, ImageFont
import sys
import shutil
import re

# --- Configuration ---
DEFAULT_INPUT_FOLDER = "./input_images"
# DEFAULT_PROJECT_NAME removed, will be derived automatically
DEFAULT_OUTPUT_DIR = "."
BACKGROUND_COLOR = "white"

# --- Resizing ---
TARGET_IMAGE_WIDTH = 512

# --- Spacing & Numbering ---
SPACING = 25
NUMBER_AREA_HEIGHT = 35
NUMBER_COLOR = "black"
FONT_SIZE = 24

# --- Copy & Rename ---
COPY_AND_RENAME_FILES = True  # Set to False to disable file copying/renaming
RENAMED_OUTPUT_FOLDER = "./renamed_grid_images"

# --- Font Loading ---
# (Font loading code remains the same)
FONT = None
common_fonts = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
]
for font_path in common_fonts:
    try:
        FONT = ImageFont.truetype(font_path, FONT_SIZE)
        print(f"Font: Using '{font_path}' at size {FONT_SIZE}")
        break
    except IOError:
        continue
if FONT is None:
    try:
        FONT = ImageFont.load_default()
        print(f"Warning: Common fonts not found. Using Pillow's basic default font.")
    except Exception as e:
        print(f"Error: Could not load any font. Details: {e}")
        FONT = None


# --- Helper Function ---
def sanitize_filename(name):
    """Removes potentially problematic characters for filenames."""
    name = name.replace(" ", "-")
    name = re.sub(r"[^\w\-]+", "", name)
    if not name:
        return "script_project"  # Default if name becomes empty
    return name.lower()


# --- Main Function Definition ---
# Added perform_copy_rename parameter
def create_image_grid(input_folder, project_name, output_dir, perform_copy_rename):
    """
    Loads PNG images, optionally resizes them, arranges them in a grid
    with spacing, numbers each image, handles errors, saves the grid with
    a dynamic filename (using provided project_name), and optionally
    copies/renames original files based on perform_copy_rename flag.
    """
    if "PIL" not in sys.modules:
        print("Error: Pillow library not found...")
        return
    if FONT is None and NUMBER_COLOR.lower() != "none":
        print("Error: Font not loaded...")
        return
    if not os.path.isdir(input_folder):
        print(f"Error: Input folder '{input_folder}' not found.")
        return

    print(f"Scanning folder '{input_folder}' for PNG images...")
    valid_images_data = []
    skipped_files = []
    base_img_width, base_img_height = None, None
    canvas_mode = "RGB"
    bg_color_value = BACKGROUND_COLOR

    potential_files = sorted(
        [
            f
            for f in os.listdir(input_folder)
            if os.path.isfile(os.path.join(input_folder, f))
            and f.lower().endswith(".png")
        ]
    )
    if not potential_files:
        print(f"Error: No PNG files found in '{input_folder}'.")
        return
    print(f"Target image width set to: {TARGET_IMAGE_WIDTH or 'Original'} pixels.")

    # --- Image Loading, Validation, and Resizing Loop ---
    # (Loop remains the same)
    for filename in potential_files:
        image_path = os.path.join(input_folder, filename)
        try:
            with Image.open(image_path) as img:
                img.load()
                original_width, original_height = img.size
                current_img_width, current_img_height = original_width, original_height
                if TARGET_IMAGE_WIDTH and original_width > TARGET_IMAGE_WIDTH:
                    aspect_ratio = original_height / original_width
                    new_width = TARGET_IMAGE_WIDTH
                    new_height = int(new_width * aspect_ratio)
                    try:
                        img = img.resize(
                            (new_width, new_height), Image.Resampling.LANCZOS
                        )
                        current_img_width, current_img_height = img.size
                    except Exception as resize_err:
                        print(
                            f"Warning: Failed to resize {filename}. Skipping. Error: {resize_err}"
                        )
                        skipped_files.append(filename + " (resize failed)")
                        continue
                if base_img_width is None:
                    base_img_width = current_img_width
                    base_img_height = current_img_height
                    img_mode = img.mode
                    print(
                        f"Using base grid cell image dimensions: {base_img_width}x{base_img_height} (based on potentially resized '{filename}')"
                    )
                    if "A" in img_mode and BACKGROUND_COLOR != "white":
                        canvas_mode = "RGBA"
                        bg_color_value = BACKGROUND_COLOR
                        print("Using RGBA mode for canvas.")
                    elif BACKGROUND_COLOR == "transparent":
                        canvas_mode = "RGBA"
                        bg_color_value = (0, 0, 0, 0)
                        print("Using RGBA mode for canvas (transparent background).")
                    else:
                        canvas_mode = "RGB"
                        bg_color_value = BACKGROUND_COLOR
                        print("Using RGB mode for canvas.")
                if img.mode != canvas_mode:
                    try:
                        img = img.convert(canvas_mode)
                    except Exception as convert_err:
                        print(
                            f"Warning: Could not convert {filename} mode ({img.mode}) to {canvas_mode}. Skipping file. Error: {convert_err}"
                        )
                        skipped_files.append(filename + " (conversion failed)")
                        continue
                valid_images_data.append((img.copy(), filename))
        except Exception as e:
            print(f"Warning: Skipping file '{filename}'. Reason: {type(e).__name__}")
            skipped_files.append(filename + f" ({type(e).__name__})")
        if base_img_width is None and len(valid_images_data) == 0:
            print("Error: Could not load initial image(s). Aborting.")
            return

    # --- Post-processing Checks ---
    if not valid_images_data:
        print("Error: No valid images could be processed.")
        return
    num_images = len(valid_images_data)
    print(f"\nSuccessfully processed {num_images} valid images.")
    if skipped_files:
        print("Skipped files/operations:")
        [print(f"- {s}") for s in skipped_files]

    # --- Grid Calculation ---
    cols = math.ceil(math.sqrt(num_images))
    rows = math.ceil(num_images / cols)
    print(f"Creating a grid of {rows} rows x {cols} columns.")
    cell_img_width = base_img_width
    cell_img_height = base_img_height
    cell_total_height = cell_img_height + (
        NUMBER_AREA_HEIGHT if NUMBER_COLOR.lower() != "none" else 0
    )
    canvas_width = (cols * cell_img_width) + ((cols + 1) * SPACING)
    canvas_height = (rows * cell_total_height) + ((rows + 1) * SPACING)

    # --- Create Canvas ---
    try:
        canvas = Image.new(
            canvas_mode, (int(canvas_width), int(canvas_height)), bg_color_value
        )
        draw = ImageDraw.Draw(canvas)
        print(f"Created canvas of size: {int(canvas_width)}x{int(canvas_height)}")
    except ValueError as ve:
        print(f"Error creating canvas (too large?). Error: {ve}")
        return
    except Exception as e:
        print(f"Error creating canvas: {e}")
        return

    # --- Place Images and Draw Numbers ---
    # (Loop remains the same)
    numbering_enabled = NUMBER_COLOR.lower() != "none" and FONT is not None
    for i, (img, original_filename) in enumerate(valid_images_data):
        row = i // cols
        col = i % cols
        cell_x_start = SPACING + (col * (cell_img_width + SPACING))
        cell_y_start = SPACING + (row * (cell_total_height + SPACING))
        if numbering_enabled:
            number_text = str(i + 1)
            try:
                try:
                    bbox = draw.textbbox((0, 0), number_text, font=FONT)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    number_x = cell_x_start + (cell_img_width - text_width) / 2
                    number_y = (
                        cell_y_start + (NUMBER_AREA_HEIGHT - text_height) / 2 - bbox[1]
                    )
                except AttributeError:
                    text_width, text_height = draw.textsize(number_text, font=FONT)
                    number_x = cell_x_start + (cell_img_width - text_width) / 2
                    number_y = cell_y_start + (NUMBER_AREA_HEIGHT - text_height) / 2
                draw.text(
                    (int(number_x), int(number_y)),
                    number_text,
                    fill=NUMBER_COLOR,
                    font=FONT,
                )
            except Exception as e:
                print(
                    f"Error drawing number for image {i+1} ({original_filename}): {e}"
                )
        img_paste_x = cell_x_start
        img_paste_y = cell_y_start + (NUMBER_AREA_HEIGHT if numbering_enabled else 0)
        current_paste_width, current_paste_height = img.size
        paste_offset_x = (cell_img_width - current_paste_width) / 2
        paste_offset_y = (cell_img_height - current_paste_height) / 2
        final_paste_x = int(img_paste_x + paste_offset_x)
        final_paste_y = int(img_paste_y + paste_offset_y)
        try:
            canvas.paste(img, (final_paste_x, final_paste_y))
        except Exception as paste_err:
            print(
                f"Error pasting image {i+1} ({original_filename}). Error: {paste_err}"
            )

    # --- Generate Dynamic Filename ---
    sanitized_proj_name = sanitize_filename(project_name)
    dynamic_filename = (
        f"{sanitized_proj_name}_grid_{int(canvas_width)}x{int(canvas_height)}.png"
    )
    output_grid_filepath = os.path.join(output_dir, dynamic_filename)

    # --- Save Final Grid Image ---
    grid_saved_successfully = False
    try:
        os.makedirs(output_dir, exist_ok=True)
        canvas.save(output_grid_filepath, "PNG")
        print(f"\nSuccessfully saved the image grid to '{output_grid_filepath}'")
        grid_saved_successfully = True
    except Exception as e:
        print(f"Error saving the final grid image to '{output_grid_filepath}': {e}")

    # --- Copy and Rename Original Files (if enabled and grid saved) ---
    if grid_saved_successfully and perform_copy_rename:
        print(f"\nCopying and renaming files to folder: '{RENAMED_OUTPUT_FOLDER}'...")
        # (Rest of copy/rename logic is identical to previous version)
        try:
            os.makedirs(RENAMED_OUTPUT_FOLDER, exist_ok=True)
            copied_count = 0
            copy_errors = []
            for i, (img_obj, original_filename) in enumerate(valid_images_data):
                original_path = os.path.join(input_folder, original_filename)
                _, ext = os.path.splitext(original_filename)
                new_filename = f"{i + 1}{ext or '.png'}"
                new_path = os.path.join(RENAMED_OUTPUT_FOLDER, new_filename)
                try:
                    if os.path.exists(original_path):
                        shutil.copy2(original_path, new_path)
                        copied_count += 1
                    else:
                        print(f"  Error: Original file not found '{original_path}'")
                        copy_errors.append(original_filename + " (Not found)")
                except Exception as copy_e:
                    print(
                        f"  Error copying '{original_filename}' to '{new_path}': {copy_e}"
                    )
                    copy_errors.append(original_filename + f" ({copy_e})")
            print(
                f"Finished copying files. Copied: {copied_count}, Errors: {len(copy_errors)}."
            )
            if copy_errors:
                print("Errors occurred during copying:")
                [print(f"- {error}") for error in copy_errors]
        except Exception as dir_e:
            print(f"Error setting up or performing file copy operation: {dir_e}")


# --- Main Execution ---
if __name__ == "__main__":
    print("\nImage Grid Creator")
    print("--------------------")
    input_dir = (
        input(f"Enter folder containing PNG images [{DEFAULT_INPUT_FOLDER}]: ")
        or DEFAULT_INPUT_FOLDER
    )

    # --- Automatically Determine Project Name from Script's Location ---
    try:
        # Get the absolute path to the directory containing this script file
        # __file__ is a special variable holding the path of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Get the name of that directory (the last part of the path)
        auto_project_name = os.path.basename(script_directory)

        # Handle cases where the script might be in the root ('/') which results in an empty basename
        if not auto_project_name:
            print(
                "Warning: Could not determine valid script directory name (maybe running from root?)."
            )
            # Fallback: Use the current working directory name instead
            auto_project_name = os.path.basename(os.getcwd())
            if not auto_project_name:  # Final fallback if CWD name is also empty
                auto_project_name = "script_location_project"  # Assign a fixed default

        print(f"Using project name derived from script's folder: '{auto_project_name}'")

    except NameError:
        # Handle cases where __file__ might not be defined (e.g., running in some interactive modes)
        print(
            "Warning: Could not automatically determine script location (__file__ not defined)."
        )
        print("Falling back to using the input folder name for the project name.")
        abs_input_dir = os.path.abspath(input_dir)
        auto_project_name = os.path.basename(abs_input_dir)
        if not auto_project_name:
            auto_project_name = "input_folder_project"
        print(f"Using project name derived from input folder: '{auto_project_name}'")

    # Sanitize the automatically derived name before using it
    sanitized_auto_project_name = sanitize_filename(auto_project_name)
    # --- End of Project Name Determination ---

    output_dir_prompt = (
        input(f"Enter directory to save grid image [{DEFAULT_OUTPUT_DIR}]: ")
        or DEFAULT_OUTPUT_DIR
    )

    # --- Confirmation for Copy/Rename ---
    # (Section remains the same)
    copy_rename_enabled_for_run = COPY_AND_RENAME_FILES
    if COPY_AND_RENAME_FILES:
        print("\nCOPY & RENAME ENABLED:")
        print(f"Original files from '{input_dir}' will be COPIED to:")
        print(f"'{RENAMED_OUTPUT_FOLDER}' and renamed (e.g., 1.png, 2.png...).")
        print("Your original files will NOT be modified in the input folder.")
        confirm = input("Do you want to proceed? (yes/no) [yes]: ") or "yes"
        if confirm.lower() not in ["yes", "y"]:
            print("Copy & Rename operation cancelled by user.")
            copy_rename_enabled_for_run = False
        else:
            print("Proceeding with Copy & Rename enabled.")
    else:
        copy_rename_enabled_for_run = False

    # --- Call the main function ---
    create_image_grid(
        input_dir,
        sanitized_auto_project_name,
        output_dir_prompt,
        copy_rename_enabled_for_run,
    )
