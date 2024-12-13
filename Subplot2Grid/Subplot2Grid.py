import tkinter as tk
from tkinter import messagebox, filedialog
import re
import sys 
import os

from PIL import Image, ImageDraw, ImageFont
import pyperclip


class WhiteboardApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Subplot2Grid Generator!")
        
        

        self.default_width_canvas_size = 400  # Default width of canvas in pixels
        self.default_height_canvas_size = 400  # Default height of canvas in pixels
        self.width_canvas_size = self.default_width_canvas_size
        self.height_canvas_size = self.default_height_canvas_size
        self.cell_size = 5  # Default cell size in pixels

        # Derive row and column grid sizes based on canvas size and cell size
        self.row_grid_size = self.height_canvas_size // self.cell_size
        self.col_grid_size = self.width_canvas_size // self.cell_size

        self.canvas = tk.Canvas(master, width=self.width_canvas_size, height=self.height_canvas_size, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4)
        self.master.iconbitmap(self.resource_path("./s2g.ico"))

        # List to store drawn rectangles
        self.rectangles = []
        self.start_x = None
        self.start_y = None

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_draw)
        self.canvas.bind("<Button-3>", self.remove_rectangle)  # Right-click event

        # Controls for resizing canvas and setting cell size
        self.width_size_label = tk.Label(master, text="Figure Width (px):")
        self.width_size_label.grid(row=1, column=0)
        self.width_size_entry = tk.Entry(master)
        self.width_size_entry.insert(0, str(self.width_canvas_size))
        self.width_size_entry.grid(row=1, column=1)

        self.height_size_label = tk.Label(master, text="Figure Height (px):")
        self.height_size_label.grid(row=2, column=0)
        self.height_size_entry = tk.Entry(master)
        self.height_size_entry.insert(0, str(self.height_canvas_size))
        self.height_size_entry.grid(row=2, column=1)

        self.cell_size_label = tk.Label(master, text="Cell Size (px):")
        self.cell_size_label.grid(row=3, column=0)
        self.cell_size_entry = tk.Entry(master)
        self.cell_size_entry.insert(0, str(self.cell_size))
        self.cell_size_entry.grid(row=3, column=1)

        self.update_btn = tk.Button(master, text="Update Canvas", command=self.update_canvas)
        self.update_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Buttons
        self.generate_btn = tk.Button(master, text="Generate Code", command=self.generate_code)
        self.generate_btn.grid(row=5, column=0, pady=10)

        self.reset_btn = tk.Button(master, text="Reset", command=self.reset_canvas)
        self.reset_btn.grid(row=5, column=1, pady=10)

        self.grid_map_btn = tk.Button(master, text="Generate Grid Map Image", command=self.generate_grid_map_image)
        self.grid_map_btn.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.draw_grid_lines()
        
        
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            # If running as a PyInstaller bundle
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Running in a normal Python environment
            return os.path.join(os.path.dirname(__file__), relative_path)
            
    def draw_grid_lines(self):
        # Draw the grid lines in a faded red color
        faded_red = "#FFAAAA"  # Red color

        # Draw horizontal lines (red, faded)
        for i in range(self.row_grid_size + 1):
            self.canvas.create_line(0, i * self.cell_size, self.width_canvas_size, i * self.cell_size, fill=faded_red)

        # Draw vertical lines (red, faded)
        for i in range(self.col_grid_size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.height_canvas_size, fill=faded_red)

    def start_draw(self, event):
        # Record the starting point of the rectangle
        self.start_x = event.x
        self.start_y = event.y

    def draw_rectangle(self, event):
        # Draw a temporary rectangle as the mouse moves
        self.canvas.delete("temp_rectangle")
        self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="blue", tags="temp_rectangle")

    def finish_draw(self, event):
        # Finalize the rectangle
        self.canvas.delete("temp_rectangle")
        rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="blue", fill="blue", stipple="gray50")
        self.rectangles.append((self.start_x, self.start_y, event.x, event.y))

    def remove_rectangle(self, event):
        # Check if right-click is inside any rectangle
        for idx, rect in enumerate(self.rectangles):
            x0, y0, x1, y1 = rect
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                # Remove the rectangle from the canvas and list
                self.canvas.delete(self.canvas.find_overlapping(x0, y0, x1, y1)[0])
                del self.rectangles[idx]
                break

    def update_canvas(self):
        
        try:
            
            new_width_canvas_size = int(self.width_size_entry.get())
            new_height_canvas_size = int(self.height_size_entry.get())
            new_cell_size = int(self.cell_size_entry.get())
            if new_width_canvas_size <= 0 or new_height_canvas_size <= 0 or new_cell_size <= 0:
                raise ValueError("Values must be positive integers.")

            self.width_canvas_size = new_width_canvas_size
            self.height_canvas_size = new_height_canvas_size
            self.cell_size = new_cell_size

            # Derive row and column grid sizes based on the new dimensions and cell size
            self.row_grid_size = self.height_canvas_size // self.cell_size
            self.col_grid_size = self.width_canvas_size // self.cell_size

            self.canvas.config(width=self.width_canvas_size, height=self.height_canvas_size)
            self.reset_canvas()
            self.draw_grid_lines()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    
    def generate_code(self, show_message=True):
        code_lines = []
        # Add line for creating the figure with dimensions matching the canvas
        code_lines.append(f"fig = plt.figure(figsize=({self.width_canvas_size / 100}, {self.height_canvas_size / 100}))")

        # Store the rectangles with their calculated positions (this will help in reordering)
        rects_with_positions = []

        for idx, rect in enumerate(self.rectangles, start=1):
            x0, y0, x1, y1 = rect
            # Determine grid position and span for the rectangle
            row_start = int(min(y0, y1) / self.cell_size)
            row_span = int(abs(y1 - y0) / self.cell_size)
            col_start = int(min(x0, x1) / self.cell_size)
            col_span = int(abs(x1 - x0) / self.cell_size)

            # Store the rectangle and its calculated position (row, column)
            rects_with_positions.append((rect, row_start, col_start, row_span, col_span))

        # Sort the rectangles by row_start first, and then by col_start (left to right)
        rects_with_positions.sort(key=lambda x: (x[1], x[2]))  # First by row, then by column

        # Create subplot code lines with reordered ax names
        for idx, (rect, row_start, col_start, row_span, col_span) in enumerate(rects_with_positions, start=1):
            code_lines.append(f"ax{idx} = plt.subplot2grid(({self.row_grid_size}, {self.col_grid_size}), "
                              f"({row_start}, {col_start}), rowspan={row_span}, colspan={col_span})")

        if code_lines:
            code_str = "\n".join(code_lines)
            if show_message:
                self.show_code_popup(code_str)
                
             # Ask the user if they want to save the generated code as a .txt file
            save_option = messagebox.askyesno("Save Code", "Would you like to save the generated code to a .txt file?")
            if save_option:
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
                if file_path:
                    try:
                        with open(file_path, 'w') as file:
                            file.write(code_str)
                        messagebox.showinfo("Saved", f"Code saved to {file_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error saving file: {e}")
        
        else:
            messagebox.showwarning("No Rectangles", "No rectangles drawn to generate code.")

        self.code_lines = code_lines



        
    def show_code_popup(self, code_str):
        popup = tk.Toplevel(self.master)
        popup.title("Generated Code")

        text_widget = tk.Text(popup, wrap="word", height=20, width=60)
        text_widget.insert("1.0", code_str)
        text_widget.configure(state="disabled")
        text_widget.pack(pady=10, padx=10)

        copy_button = tk.Button(popup, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(code_str))
        copy_button.pack(pady=5)

        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=5)

    def copy_to_clipboard(self, code_str):
        pyperclip.copy(code_str)
        messagebox.showinfo("Copied", "Code copied to clipboard!")

    def reset_canvas(self):
        self.canvas.delete("all")
        self.rectangles = []
        self.draw_grid_lines()

    def generate_grid_map_image(self):
        import matplotlib.pyplot as plt
        # Execute each line to create the figure and axes dynamically
        self.generate_code(show_message=False)
        
        exec('import matplotlib.pyplot as plt', globals())
        for line in self.code_lines:
            exec(line, globals())
       
        axis_names = re.findall(r'ax\d+', '\n'.join(self.code_lines))

        # Turn off x and y ticks for each axis automatically
        for axis_name in axis_names:
            # Access the axis object dynamically
            axis = globals().get(axis_name)  # Fetch the axis object (e.g., ax1, ax2, etc.)
            
            if axis:  # Make sure the axis object exists
                axis.text(0,0,axis_name, fontsize=6)
                axis.set_xticks([])  # Turn off x-axis ticks
                axis.set_yticks([])  # Turn off y-axis ticks
                
    
        plt.show()
        
        # Save the plot to a file (ask for the filename and format)
        save_option = messagebox.askyesno("Save Image", "Would you like to save the image?")
        if save_option:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            if file_path:
                plt.savefig(file_path)
                messagebox.showinfo("Saved", f"Image saved to {file_path}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WhiteboardApp(root)
    root.mainloop()
