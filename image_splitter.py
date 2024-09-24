# Written with Chat GPT


import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import math

class ImageTilerApp:
    def __init__(self, master):
        self.master = master
        master.title("Image Tiler")

        # Variables
        self.canvas_width = tk.DoubleVar()
        self.canvas_height = tk.DoubleVar()
        self.tile_width = tk.DoubleVar()
        self.tile_height = tk.DoubleVar()
        self.overlap = tk.DoubleVar(value=1.0)  # Default overlap of 1 cm
        self.dpi = tk.IntVar(value=300)  # Default DPI of 300
        self.padding = tk.DoubleVar(value=1.0)  # Default padding of 1%
        self.image_path = ""
        self.image = None

        # UI elements
        tk.Label(master, text="Canvas Width (cm):").grid(row=0, column=0, sticky='e')
        tk.Entry(master, textvariable=self.canvas_width).grid(row=0, column=1)

        tk.Label(master, text="Canvas Height (cm):").grid(row=1, column=0, sticky='e')
        tk.Entry(master, textvariable=self.canvas_height).grid(row=1, column=1)

        tk.Label(master, text="Tile Width (cm):").grid(row=2, column=0, sticky='e')
        tk.Entry(master, textvariable=self.tile_width).grid(row=2, column=1)

        tk.Label(master, text="Tile Height (cm):").grid(row=3, column=0, sticky='e')
        tk.Entry(master, textvariable=self.tile_height).grid(row=3, column=1)

        tk.Label(master, text="Overlap (cm):").grid(row=4, column=0, sticky='e')
        tk.Entry(master, textvariable=self.overlap).grid(row=4, column=1)

        tk.Label(master, text="DPI:").grid(row=5, column=0, sticky='e')
        tk.Entry(master, textvariable=self.dpi).grid(row=5, column=1)

        tk.Label(master, text="Max Padding (%):").grid(row=6, column=0, sticky='e')
        tk.Entry(master, textvariable=self.padding).grid(row=6, column=1)

        tk.Button(master, text="Load Image", command=self.load_image).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(master, text="Process Image", command=self.process_image).grid(row=8, column=0, columnspan=2)

    def load_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Open Image File", filetypes=filetypes)
        if filepath:
            self.image_path = filepath
            try:
                self.image = Image.open(self.image_path)
                messagebox.showinfo("Image Loaded", "Image loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{e}")
                self.image = None

    def process_image(self):
        if not self.image:
            messagebox.showerror("Error", "No image loaded!")
            return

        try:
            canvas_w_cm = self.canvas_width.get()
            canvas_h_cm = self.canvas_height.get()
            tile_w_cm = self.tile_width.get()
            tile_h_cm = self.tile_height.get()
            overlap_cm = self.overlap.get()
            dpi = self.dpi.get()
            padding_percent = self.padding.get()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numeric values.")
            return

        if (canvas_w_cm <= 0 or canvas_h_cm <= 0 or tile_w_cm <= 0 or tile_h_cm <= 0 or
            overlap_cm < 0 or dpi <= 0 or padding_percent < 0 or padding_percent >= 50):
            messagebox.showerror("Error", "Dimensions, DPI, and padding must be positive numbers. Padding must be less than 50%.")
            return

        # Pixels per centimeter
        px_per_cm = dpi / 2.54  # 1 inch = 2.54 cm

        # Allowed padding in centimeters
        allowed_padding_w_cm = (padding_percent / 100.0) * canvas_w_cm
        allowed_padding_h_cm = (padding_percent / 100.0) * canvas_h_cm

        # Original image dimensions in pixels
        image_w_px, image_h_px = self.image.size
        image_w_cm = image_w_px / px_per_cm
        image_h_cm = image_h_px / px_per_cm

        # Option 1: Scale to fit width
        scaled_image_w_cm_1 = canvas_w_cm - 2 * allowed_padding_w_cm
        s_1 = scaled_image_w_cm_1 / image_w_cm  # Scaling factor
        scaled_image_h_cm_1 = image_h_cm * s_1

        # Check if scaled image height fits in canvas
        option1_valid = scaled_image_h_cm_1 <= canvas_h_cm

        # Option 2: Scale to fit height
        scaled_image_h_cm_2 = canvas_h_cm - 2 * allowed_padding_h_cm
        s_2 = scaled_image_h_cm_2 / image_h_cm  # Scaling factor
        scaled_image_w_cm_2 = image_w_cm * s_2

        # Check if scaled image width fits in canvas
        option2_valid = scaled_image_w_cm_2 <= canvas_w_cm

        # Choose the option with the largest scaling factor s
        if option1_valid and option2_valid:
            if s_1 > s_2:
                s = s_1
                scaled_image_w_cm = scaled_image_w_cm_1
                scaled_image_h_cm = scaled_image_h_cm_1
            else:
                s = s_2
                scaled_image_w_cm = scaled_image_w_cm_2
                scaled_image_h_cm = scaled_image_h_cm_2
        elif option1_valid:
            s = s_1
            scaled_image_w_cm = scaled_image_w_cm_1
            scaled_image_h_cm = scaled_image_h_cm_1
        elif option2_valid:
            s = s_2
            scaled_image_w_cm = scaled_image_w_cm_2
            scaled_image_h_cm = scaled_image_h_cm_2
        else:
            messagebox.showerror("Error", "Unable to fit the image within the specified padding constraints.")
            return

        # Compute the scaled image size in pixels
        scaled_image_w_px = int(scaled_image_w_cm * px_per_cm)
        scaled_image_h_px = int(scaled_image_h_cm * px_per_cm)

        # Create the resized image
        resized_image = self.image.resize((scaled_image_w_px, scaled_image_h_px), Image.LANCZOS)

        # Compute the canvas size in pixels
        canvas_px_w = int(canvas_w_cm * px_per_cm)
        canvas_px_h = int(canvas_h_cm * px_per_cm)

        # Create the canvas image
        canvas_image = Image.new(self.image.mode, (canvas_px_w, canvas_px_h), (255, 255, 255))

        # Compute the paste positions
        paste_x = (canvas_px_w - scaled_image_w_px) // 2
        paste_y = (canvas_px_h - scaled_image_h_px) // 2

        canvas_image.paste(resized_image, (paste_x, paste_y))

        # Convert tile and overlap dimensions to pixels
        tile_px_w = int(tile_w_cm * px_per_cm)
        tile_px_h = int(tile_h_cm * px_per_cm)
        overlap_px = int(overlap_cm * px_per_cm)

        # Calculate number of tiles, accounting for overlap
        num_tiles_w = math.ceil((canvas_px_w - overlap_px) / (tile_px_w - overlap_px))
        num_tiles_h = math.ceil((canvas_px_h - overlap_px) / (tile_px_h - overlap_px))

        # Create output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            messagebox.showinfo("Cancelled", "No output directory selected.")
            return

        # Split the image into tiles with overlap
        tile_count = 0
        for i in range(num_tiles_h):
            for j in range(num_tiles_w):
                left = int(j * (tile_px_w - overlap_px))
                upper = int(i * (tile_px_h - overlap_px))
                right = left + tile_px_w
                lower = upper + tile_px_h

                # Adjust boundaries if they exceed the canvas size
                if right > canvas_px_w:
                    right = canvas_px_w
                    left = right - tile_px_w
                if lower > canvas_px_h:
                    lower = canvas_px_h
                    upper = lower - tile_px_h
                if left < 0:
                    left = 0
                    right = tile_px_w
                if upper < 0:
                    upper = 0
                    lower = tile_px_h

                box = (left, upper, right, lower)
                tile = canvas_image.crop(box)
                tile_filename = os.path.join(output_dir, f"tile_{i+1}_{j+1}.png")
                tile.save(tile_filename, dpi=(dpi, dpi))
                tile_count += 1

        messagebox.showinfo("Success", f"Image has been divided into {tile_count} tiles with {overlap_cm} cm overlap and maximum {padding_percent}% padding.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageTilerApp(root)
    root.mainloop()
