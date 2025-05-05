import os
import colorsys
from tkinter import Tk, Button, Label, Entry, filedialog, messagebox, Canvas, Toplevel, colorchooser, Frame
from colorthief import ColorThief
from collections import Counter
from PIL import Image, ImageDraw

colors_per_image = 9
preview_size = 20
undo_stack = []
generated_colors = []
last_output_file = ""

def rgb_to_hsb(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def show_preview(colors):
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

    canvas.bind("<Button-1>", on_click)
    preview.bind("<Control-z>", undo)
    draw_palette()

def export_act():
    if not generated_colors:
        messagebox.showerror("Nothing to save", "No palette generated yet.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".act", filetypes=[("Photoshop ACT", "*.act")])
    if file:
        with open(file, "wb") as f:
            for color in generated_colors:
                f.write(bytes(color))
            # Pad to 256 colors if needed
            while len(generated_colors) < 256:
                f.write(bytes((0, 0, 0)))
        messagebox.showinfo("Saved", f"ACT file saved:\n{file}")

def export_png():
    if not generated_colors:
        messagebox.showerror("Nothing to export", "No palette generated yet.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
    if not file:
        return
    img = Image.new("RGB", (16 * preview_size, 16 * preview_size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i, color in enumerate(generated_colors):
        x = (i % 16) * preview_size
        y = (i // 16) * preview_size
        draw.rectangle([x, y, x + preview_size, y + preview_size], fill=color, outline=(0, 0, 0))
    img.save(file)
    messagebox.showinfo("Saved", f"Palette image saved:\n{file}")

def generate_palette(image_folder, colors_per_image_value):
    global generated_colors
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

    generated_colors = unique_colors
    show_preview(generated_colors)

# === GUI Setup ===
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_label.config(text=folder)
        folder_label.folder = folder

def run_generation():
    folder = getattr(folder_label, 'folder', None)
    try:
        colors_value = int(color_entry.get())
        if colors_value < 1 or colors_value > 256:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a number between 1 and 256 for colors per image.")
        return
    if not folder:
        messagebox.showerror("Missing info", "Please select an image folder.")
        return
    generate_palette(folder, colors_value)

# === Main Window ===
# === Main Window ===
root = Tk()
root.title("PNG to .ACT Palette Generator")
root.geometry("640x360")

top_frame = Frame(root)
top_frame.pack(pady=10)

# Folder frame (aligned top)
folder_frame = Frame(top_frame)
folder_frame.pack(side="left", anchor="n", padx=20)
Label(folder_frame, text="1. Select image folder:").pack(anchor="w")
Button(folder_frame, text="Browse Folder", command=select_folder).pack(anchor="w")
folder_label = Label(folder_frame, text="No folder selected", wraplength=250, justify="left")
folder_label.pack(anchor="w")

# Color per image frame (aligned top)
color_frame = Frame(top_frame)
color_frame.pack(side="left", anchor="n", padx=20)
Label(color_frame, text="2. Colors per image (1–256):").pack(anchor="w")
color_entry = Entry(color_frame, width=5)
color_entry.insert(0, "9")
color_entry.pack(anchor="w", pady=(0, 10))

# Generate button
Button(root, text="🎨 Generate & Preview", command=run_generation, bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=10)

# Export options
export_frame = Frame(root)
export_frame.pack(pady=10)
Button(export_frame, text="💾 Save .ACT File", command=export_act, bg="#2196F3", fg="white", padx=10).pack(side="left", padx=10)
Button(export_frame, text="🖼️ Export as PNG", command=export_png, bg="#9C27B0", fg="white", padx=10).pack(side="left", padx=10)

root.mainloop()

