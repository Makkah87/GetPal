import os
import colorsys
from tkinter import Tk, Button, Label, Entry, filedialog, messagebox, Canvas, Toplevel, colorchooser, Frame
from colorthief import ColorThief
from collections import Counter
from PIL import Image, ImageDraw

colors_per_image = 9  # Default value
preview_size = 20
undo_stack = []

def rgb_to_hsb(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def show_preview(colors, output_file):
    preview = Toplevel()
    preview.title("Palette Preview (click to edit, Ctrl+Z to undo)")

    canvas_width = preview_size * 16
    canvas_height = preview_size * 16
    canvas = Canvas(preview, width=canvas_width, height=canvas_height)
    canvas.pack(padx=10, pady=10)

    def draw_palette():
        canvas.delete("all")
        for i, color in enumerate(colors):
            x = (i % 16) * preview_size
            y = (i // 16) * preview_size
            hex_color = '#%02x%02x%02x' % color
            canvas.create_rectangle(x, y, x + preview_size, y + preview_size, fill=hex_color, outline="black")

    def on_click(event):
        x, y = event.x // preview_size, event.y // preview_size
        index = y * 16 + x
        if 0 <= index < len(colors):
            current = colors[index]
            rgb, hex_code = colorchooser.askcolor(color=current)
            if rgb:
                undo_stack.append((index, colors[index]))
                r, g, b = [int(v) for v in rgb]
                colors[index] = (r, g, b)
                draw_palette()

    def undo(event=None):
        if undo_stack:
            index, previous_color = undo_stack.pop()
            colors[index] = previous_color
            draw_palette()

    def confirm_and_save():
        with open(output_file, "wb") as f:
            for color in colors:
                f.write(bytes(color))
        messagebox.showinfo("Success", f"Saved .ACT file:\n{output_file}")
        preview.destroy()

    def export_png():
        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if not file:
            return
        img = Image.new("RGB", (16 * preview_size, 16 * preview_size), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        for i, color in enumerate(colors):
            x = (i % 16) * preview_size
            y = (i // 16) * preview_size
            draw.rectangle([x, y, x + preview_size, y + preview_size], fill=color, outline=(0, 0, 0))
        img.save(file)
        messagebox.showinfo("Saved", f"Palette image saved:\n{file}")

    canvas.bind("<Button-1>", on_click)
    preview.bind("<Control-z>", undo)
    draw_palette()

    Button(preview, text="💾 Save .ACT File", command=confirm_and_save, bg="#4CAF50", fg="white").pack(pady=(10, 5))
    Button(preview, text="🖼️ Export as PNG", command=export_png, bg="#2196F3", fg="white").pack(pady=(0, 10))

def generate_palette(image_folder, output_file, colors_per_image_value):
    all_colors = []

    for filename in os.listdir(image_folder):
        if filename.lower().endswith('.png'):
            try:
                ct = ColorThief(os.path.join(image_folder, filename))
                palette = ct.get_palette(color_count=colors_per_image_value)
                all_colors.extend(palette)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if not all_colors:
        messagebox.showerror("No colors", "No colors were extracted. Check the folder.")
        return

    color_counts = Counter(all_colors)
    unique_colors = [color for color, _ in color_counts.most_common(256)]
    unique_colors = sorted(unique_colors, key=rgb_to_hsb)

    while len(unique_colors) < 256:
        unique_colors.append((0, 0, 0))

    show_preview(unique_colors, output_file)

# === GUI Setup ===
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_label.config(text=folder)
        folder_label.folder = folder

def select_output():
    file = filedialog.asksaveasfilename(defaultextension=".act", filetypes=[("Photoshop ACT", "*.act")])
    if file:
        output_label.config(text=file)
        output_label.output = file

def run_generation():
    folder = getattr(folder_label, 'folder', None)
    output = getattr(output_label, 'output', None)
    try:
        colors_value = int(color_entry.get())
        if colors_value < 1 or colors_value > 256:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a number between 1 and 256 for colors per image.")
        return
    if not folder or not output:
        messagebox.showerror("Missing info", "Please select both a folder and an output file.")
        return
    generate_palette(folder, output, colors_value)

# === Main Window ===
root = Tk()
root.title("PNG to .ACT Palette Generator")
root.geometry("600x300")  # Nice wide window

# Top frame to arrange folder + output side by side
top_frame = Frame(root)
top_frame.pack(pady=10)

# Folder frame
folder_frame = Frame(top_frame)
folder_frame.pack(side="left", padx=10)
Label(folder_frame, text="1. Select image folder:").pack(pady=5)
Button(folder_frame, text="Browse Folder", command=select_folder).pack()
folder_label = Label(folder_frame, text="No folder selected", wraplength=250)
folder_label.pack()

# Output frame
output_frame = Frame(top_frame)
output_frame.pack(side="left", padx=10)
Label(output_frame, text="2. Select output .ACT file:").pack(pady=5)
Button(output_frame, text="Choose Save Location", command=select_output).pack()
output_label = Label(output_frame, text="No output selected", wraplength=250)
output_label.pack()

# Colors per image (bottom)
Label(root, text="3. Colors per image (1-256):").pack(pady=10)
color_entry = Entry(root)
color_entry.insert(0, "9")
color_entry.pack()

Button(root, text="Generate & Preview", command=run_generation, bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=20)

root.mainloop()
