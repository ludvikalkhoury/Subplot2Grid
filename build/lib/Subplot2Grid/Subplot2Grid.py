import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel
import re
import sys 
import os

from PIL import Image, ImageDraw, ImageFont
import pyperclip


class Subplot2Grid:
	version = "0.0.1"
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
		
		self.canvas.bind("<Button-2>", self.start_move)  # Middle-click event
		self.canvas.bind("<B2-Motion>", self.move_rectangle)  # Middle-click drag

		self.canvas.focus_set()  # To catch key events like pressing 'm'


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

		

		# Buttons
		self.update_btn = tk.Button(master, text="Update Canvas", command=self.update_canvas)
		self.update_btn.grid(row=4, column=0, columnspan=1, pady=10)
		
		self.grid_map_btn = tk.Button(master, text="Generate Grid Map Image", command=self.generate_grid_map_image)
		self.grid_map_btn.grid(row=4, column=1, columnspan=1, pady=10)
		
		
		self.generate_btn = tk.Button(master, text="Generate Code", command=self.generate_code)
		self.generate_btn.grid(row=4, column=2, pady=10)
		
		self.help_btn = tk.Button(master, text="help", command=self.display_help_message)
		self.help_btn.grid(row=4, column=3, pady=10)
		
		#self.reset_btn = tk.Button(master, text="Reset", command=self.reset_canvas)
		#self.reset_btn.grid(row=5, column=1, pady=10)

		
		
		self.draw_grid_lines()
		
	
	def display_help_message(self):
		# Create a new top-level window
		help_window = Toplevel(self.master)
		help_window.title("Help")
		
		self.help_text = (
			"Subplot2Grid is a tool that helps you design subplot layouts and generate corresponding code.\n\n"
			"Instructions:\n"
			"- Use the left mouse button to draw a rectangle on the canvas.\n"
			"- Use the right mouse button to delete a rectangle.\n"
			"- Use the middle mouse button to move and adjust the rectangle's placement.\n\n"
			"Features:\n"
			"- Generate and save the Python code for your layout.\n"
			"- Export a template image of the grid to remember labels and subplots."
			)	
		
		# Add a label with the help message
		help_message = tk.Label(help_window, text=self.help_text, wraplength=400, justify="left")
		help_message.pack(padx=20, pady=20)

		# Add a close button
		close_button = tk.Button(help_window, text="Close", command=help_window.destroy)
		close_button.pack(pady=10)
		
		
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
		self.start_x = (event.x // self.cell_size) * self.cell_size
		self.start_y = (event.y // self.cell_size) * self.cell_size



	def create_rectangle(self, x0, y0, x1, y1):
		"""Create a rectangle and store its ID."""
		rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="blue")
		self.rectangles.append(rect_id)
		print(f"Rectangle created with ID: {rect_id}")
	
	
	def draw_rectangle(self, event):
		# Draw a temporary rectangle as the mouse moves
		current_x = (event.x // self.cell_size) * self.cell_size
		current_y = (event.y // self.cell_size) * self.cell_size

		# Draw a temporary rectangle
		self.canvas.delete("temp_rectangle")
		self.canvas.create_rectangle(
			self.start_x, self.start_y, current_x, current_y,
			outline="blue", tags="temp_rectangle"
		)
		
		
		
	def finish_draw(self, event):
		# Snap the final mouse position to the nearest grid corner
		end_x = (event.x // self.cell_size) * self.cell_size
		end_y = (event.y // self.cell_size) * self.cell_size

		# Calculate the width and height of the rectangle
		width = abs(end_x - self.start_x)
		height = abs(end_y - self.start_y)

		# Only finalize the rectangle if the width is greater than or equal to one cell size
		if width >= self.cell_size and height >= self.cell_size:
			# Finalize the rectangle and create the rectangle on the canvas
			self.canvas.delete("temp_rectangle")
			rect_id = self.canvas.create_rectangle(
				self.start_x, self.start_y, end_x, end_y,
				outline="blue", fill="blue", stipple="gray50"
			)
			# Append the rectangle details to the list with the rect_id
			self.rectangles.append((rect_id, self.start_x, self.start_y, end_x, end_y))
		else:
			# Show a message or simply ignore if the rectangle is too thin
			print("Rectangle too thin, not added.")



	def remove_rectangle(self, event):
		"""Remove the rectangle under the mouse pointer on right-click."""
		for idx, (rect_id, x0, y0, x1, y1) in enumerate(self.rectangles):
			# Check if the event position is inside the rectangle
			if x0 <= event.x <= x1 and y0 <= event.y <= y1:
				# Delete the rectangle from the canvas
				self.canvas.delete(rect_id)
				# Remove the rectangle from the list
				del self.rectangles[idx]
				print(f"Rectangle with ID {rect_id} removed.")
				break
		else:
			print("No rectangle found at the click position.")


	def start_move(self, event):
		# Start moving a rectangle with middle-click
		for idx, (rect_id, x0, y0, x1, y1) in enumerate(self.rectangles):
			if x0 <= event.x <= x1 and y0 <= event.y <= y1:
				self.selected_rect = (rect_id, x0, y0, x1, y1)
				self.offset_x = event.x - x0
				self.offset_y = event.y - y0
				break
	
	def move_rectangle(self, event):
		# Move the selected rectangle with middle-click dragging
		if self.selected_rect:
			rect_id, x0, y0, x1, y1 = self.selected_rect
			
			dx = event.x - self.offset_x - x0
			dy = event.y - self.offset_y - y0
			
			# Snap the mouse position to the grid (cell size)
			snap_x = (event.x // self.cell_size) * self.cell_size
			snap_y = (event.y // self.cell_size) * self.cell_size
			
			# Find the closest corner to snap the rectangle to
			corners = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
			closest_corner = min(corners, key=lambda corner: (corner[0] - snap_x) ** 2 + (corner[1] - snap_y) ** 2)

			# Calculate the new position for the rectangle based on the closest corner
			snap_dx = closest_corner[0] - x0
			snap_dy = closest_corner[1] - y0

			# Apply snapping adjustments to the rectangle's coordinates
			new_x0 = snap_x
			new_y0 = snap_y
			new_x1 = new_x0 + (x1 - x0)
			new_y1 = new_y0 + (y1 - y0)
		
			self.canvas.coords(rect_id, new_x0, new_y0, new_x1, new_y1)
			
			# Update the position in the rectangles list
			for i, rect in enumerate(self.rectangles):
				if rect[0] == rect_id:
					self.rectangles[i] = (rect_id, new_x0, new_y0, new_x1, new_y1)
					break  # Found and updated the matching rectangle
			
			# Update the offset values for the next movement
			self.offset_x = event.x - new_x0
			self.offset_y = event.y - new_y0



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
			_, x0, y0, x1, y1 = rect
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

		if len(code_lines) > 1:
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
			messagebox.showwarning("No Rectangles", "No rectangles drawn to generate code or grid map image.")

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


		if len(self.code_lines) > 1:
			
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
	app = Subplot2Grid(root)
	root.mainloop()
