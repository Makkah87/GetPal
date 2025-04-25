import os
from colorthief import ColorThief
from collections import Counter
import colorsys
import tkinter as tk
from tkinter import filedialog, messagebox


# Convert RGB to HSB for sorting
def rgb_to_hsb(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h, s, v)


# Function to process images and generate palette
def generate_palette():
    image_folder = folder_entry.get()
    output_file = output_entry.get()
    try:
        colors_per_image = int(colors_per_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number for colors per image.")
        return

    if not os.path.exists(image_folder):
        messagebox.showerror("Invalid folder", "Please select a valid folder with images.")
        return

    all_colors = []

    # Extract colors from images
    for filename in os.listdir(image_folder):
        if filename.lower().endswith('.png'):
            img_path = os.path.join(image_folder, filename)
            try:
                color_thief = ColorThief(img_path)
                palette = color_thief.get_palette(color_count=colors_per_image)
                all_colors.extend(palette)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Deduplicate and sort colors
    color_counts = Counter(all_colors)
    unique_colors = [color for color, _ in color_counts.most_common(256)]

    # Sort colors by Hue, then Saturation, then Brightness
    unique_colors = sorted(unique_colors, key=rgb_to_hsb)

    # Pad to 256 colors if needed
    while len(unique_colors) < 256:
        unique_colors.append((0, 0, 0))  # black

    # Save the palette to .ACT file
    try:
        with open(output_file, "wb") as f:
            for color in unique_colors:
                f.write(bytes(color))  # Each color is 3 bytes: R, G, B
        messagebox.showinfo("Success", f"Palette saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving palette: {e}")


# Function to browse for the folder containing images
def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)


# Function to browse for output file location
def browse_output_file():
    output_path = filedialog.asksaveasfilename(defaultextension=".act", filetypes=[("ACT files", "*.act")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_path)


# Creating main GUI window
root = tk.Tk()
root.title("Palette Generator")

# Create and place widgets
folder_label = tk.Label(root, text="Image Folder:")
folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

folder_entry = tk.Entry(root, width=40)
folder_entry.grid(row=0, column=1, padx=10, pady=5)

browse_folder_button = tk.Button(root, text="Browse", command=browse_folder)
browse_folder_button.grid(row=0, column=2, padx=10, pady=5)

output_label = tk.Label(root, text="Output File (.act):")
output_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

output_entry = tk.Entry(root, width=40)
output_entry.grid(row=1, column=1, padx=10, pady=5)

browse_output_button = tk.Button(root, text="Browse", command=browse_output_file)
browse_output_button.grid(row=1, column=2, padx=10, pady=5)

colors_per_label = tk.Label(root, text="Colors Per Image:")
colors_per_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

colors_per_entry = tk.Entry(root, width=10)
colors_per_entry.insert(0, "9")  # Default to 9 colors per image
colors_per_entry.grid(row=2, column=1, padx=10, pady=5)

generate_button = tk.Button(root, text="Generate Palette", command=generate_palette)
generate_button.grid(row=3, column=0, columnspan=3, pady=10)

# Start the GUI event loop
root.mainloop()
