"""
MIT License

Copyright (c) 2025 ItsRene

See LICENSE file for the complete license text.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors


class PyramidChart:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyramid Chart")
        
        # Ensure required directories exist
        self.setup_directories()
        
        try:
            # Dictionary to store positions and entries
            self.positions = {}
            self.position_frames = {}
            
            # Dictionary to store available names and their images
            self.name_database = {}  # Format: {'name': 'image_path'}
            
            # Load saved name database if it exists
            self.load_name_database()
            
            # Get number of people
            self.get_people_count()
            
            print(f"People count: {self.people_count}")  # Debug print
            
            # Calculate pyramid structure
            self.pyramid_structure = self.calculate_pyramid_structure(self.people_count)
            print(f"Pyramid structure: {self.pyramid_structure}")  # Debug print
            
            # Setup the GUI
            self.setup_gui()
            
            # Save name database when closing
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Error starting application: {str(e)}")

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs('images', exist_ok=True)

    def load_name_database(self):
        """Load the saved name database from a JSON file"""
        try:
            db_path = 'name_database.json'
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    self.name_database = json.load(f)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load name database: {str(e)}")
            self.name_database = {}

    def save_name_database(self):
        """Save the name database to a JSON file"""
        try:
            with open('name_database.json', 'w') as f:
                json.dump(self.name_database, f, indent=4)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not save name database: {str(e)}")

    def on_closing(self):
        """Handle window closing"""
        self.save_name_database()
        self.root.destroy()

    def get_people_count(self):
        """Ask user for the number of people in the pyramid"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pyramid Size")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Enter number of people in pyramid:", 
                 padding="20").pack()
        
        var = tk.StringVar(value="10")  # Default value
        entry = ttk.Entry(dialog, textvariable=var)
        entry.pack(pady=10)
        
        def validate_and_set():
            try:
                count = int(var.get())
                if count > 0:
                    self.people_count = count
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Please enter a positive number")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        ttk.Button(dialog, text="OK", command=validate_and_set).pack(pady=10)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # If people_count wasn't set, use default
        if not hasattr(self, 'people_count'):
            self.people_count = 10

    def manage_names(self):
        dialog = NameManagerDialog(self.root, self.name_database)
        if dialog.result:
            self.name_database = dialog.result

    def add_person(self):
        try:
            if not self.name_database:
                if messagebox.askyesno("No Names", 
                    "No names in database. Would you like to add names now?"):
                    self.manage_names()
                return

            dialog = PersonDialog(self.root, 
                                list(range(1, self.people_count + 1)),
                                self.name_database)
            if dialog.result:
                name, position = dialog.result
                image_path = self.name_database[name]
                self.add_to_position(name, position, image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding person: {str(e)}")

    def setup_gui(self):
        print("Setting up GUI...")  # Debug print
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create a canvas with scrollbar for the pyramid - further increased height
        self.canvas = tk.Canvas(self.main_frame, width=1200, height=2000, bg='lightgray')
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        
        # Pack layout for canvas and scrollbar
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create pyramid frame inside canvas - increased size
        self.pyramid_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.pyramid_frame, anchor="nw", 
                                                     width=1200, height=2000)
        
        # Bind frame configuration to update scroll region
        self.pyramid_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Colors for each level (top to bottom) - extended for more levels
        self.level_colors = ['#90C979', '#F4D03F', '#E67E22', '#3498DB', '#8E44AD'] * 3  # Repeat colors for more levels
        
        # Calculate pyramid structure based on total positions
        self.pyramid_structure = self.calculate_pyramid_structure(self.people_count)
        
        # Create boxes
        self.create_pyramid_boxes()
        
        # Control buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(side=tk.BOTTOM, pady=20, padx=20)  # Added padx for more horizontal space
        
        # Create two rows of buttons for better layout
        top_row = ttk.Frame(button_frame)
        bottom_row = ttk.Frame(button_frame)
        top_row.pack(pady=(0, 5))  # Add space between rows
        bottom_row.pack()
        
        # Top row buttons
        ttk.Button(top_row, text="Manage Names", 
                  command=self.manage_names).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_row, text="Add Person", 
                  command=self.add_person).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_row, text="Print Chart", 
                  command=self.print_chart).pack(side=tk.LEFT, padx=5)
        
        # Bottom row buttons
        ttk.Button(bottom_row, text="Save Assignments", 
                  command=self.save_assignments).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_row, text="Load Assignments", 
                  command=self.load_assignments).pack(side=tk.LEFT, padx=5)
        
        print("GUI setup complete")  # Debug print

    def calculate_pyramid_structure(self, total_positions):
        """Calculate how many boxes should be in each row of the pyramid"""
        structure = []
        remaining = total_positions
        current_row = 1
        
        while remaining > 0:
            # Add current row size to structure
            if remaining >= current_row:
                structure.append(current_row)
                remaining -= current_row
                current_row += 1
            else:
                # If there are remaining positions, add them as the last row
                if remaining > 0:
                    structure.append(remaining)
                break
        
        return structure

    def add_to_position(self, name, position, image_path, update=False):
        try:
            # Check if position already occupied and we're not updating
            if position in self.positions and not update:
                messagebox.showerror("Error", f"Position {position} is already occupied")
                return
            
            # Get the frame
            frame = self.position_frames[position]
            
            # Clear existing content
            for widget in frame.winfo_children():
                widget.destroy()
            
            # Get frame dimensions
            frame.update_idletasks()  # Ensure dimensions are updated
            box_width = frame.winfo_width()
            box_height = frame.winfo_height()
            
            # Calculate image size - use 70% of box height for image, leaving space for name
            image_height = int(box_height * 0.7)
            image_width = box_width - 10  # Leave 5px padding on each side
            
            # Load and resize image
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    # Calculate dimensions maintaining aspect ratio
                    img_width, img_height = image.size
                    aspect_ratio = img_width / img_height
                    
                    # Calculate new dimensions maintaining aspect ratio
                    new_height = image_height
                    new_width = int(new_height * aspect_ratio)
                    
                    # If width is too large, scale based on width instead
                    if new_width > image_width:
                        new_width = image_width
                        new_height = int(new_width / aspect_ratio)
                    
                    image = image.resize((new_width, new_height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Create image label with padding
                    img_label = ttk.Label(frame, image=photo)
                    img_label.image = photo  # Keep reference
                    img_label.pack(expand=True, pady=(5, 0))
                
                except Exception as e:
                    print(f"Error loading image: {str(e)}")
            
            # Add name label with smaller font and padding
            name_label = ttk.Label(frame, 
                                 text=name,
                                 font=('Arial', 9),  # Smaller font
                                 anchor='center',
                                 wraplength=box_width-10)  # Allow text to wrap
            name_label.pack(expand=False, pady=(2, 5))
            
            # Store position data
            self.positions[position] = {
                'name': name,
                'image_path': image_path
            }
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding to position: {str(e)}")
            
    def draw_lines(self):
        # Remove any existing canvas
        for widget in self.pyramid_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
                
        # Create a canvas for lines
        canvas = tk.Canvas(self.pyramid_frame, width=800, height=600)
        canvas.place(x=0, y=0)
        canvas.lower()  # Put canvas behind other widgets
        
        # Define pyramid structure (boxes per row, bottom to top)
        pyramid_structure = [5, 4, 3, 2, 1]  # Bottom to top
        
        # Draw lines between positions
        position_number = 1
        for row in range(len(pyramid_structure)-1):
            boxes_in_current_row = pyramid_structure[-(row+1)]  # Current row (from bottom)
            boxes_in_next_row = pyramid_structure[-(row+2)]     # Row above
            
            for box in range(boxes_in_current_row):
                current_frame = self.position_frames[position_number]
                
                # Get coordinates of current box's top center
                x1 = current_frame.winfo_rootx() - self.pyramid_frame.winfo_rootx()
                y1 = current_frame.winfo_rooty() - self.pyramid_frame.winfo_rooty()
                x1 += current_frame.winfo_width() // 2
                
                # Connect to boxes in the row above
                if box < boxes_in_current_row - 1:
                    # Connect to box above and to the right
                    next_frame = self.position_frames[position_number + boxes_in_current_row]
                    x2 = next_frame.winfo_rootx() - self.pyramid_frame.winfo_rootx()
                    y2 = next_frame.winfo_rooty() - self.pyramid_frame.winfo_rooty()
                    x2 += next_frame.winfo_width() // 2
                    y2 += next_frame.winfo_height()
                    canvas.create_line(x1, y1, x2, y2, width=2, fill='#666666')
                
                if box > 0:
                    # Connect to box above and to the left
                    prev_frame = self.position_frames[position_number + boxes_in_current_row - 1]
                    x2 = prev_frame.winfo_rootx() - self.pyramid_frame.winfo_rootx()
                    y2 = prev_frame.winfo_rooty() - self.pyramid_frame.winfo_rooty()
                    x2 += prev_frame.winfo_width() // 2
                    y2 += prev_frame.winfo_height()
                    canvas.create_line(x1, y1, x2, y2, width=2, fill='#666666')
                
                position_number += 1
        
    def print_chart(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if not filename:
                return

            # Create PDF
            c = canvas.Canvas(filename, pagesize=landscape(A4))
            width, height = landscape(A4)
            
            # Calculate dimensions with minimal margins
            margin = 10  # Further reduced margin
            usable_height = height - (2 * margin)
            usable_width = width - (2 * margin)
            
            total_rows = len(self.pyramid_structure)
            max_boxes_in_row = max(self.pyramid_structure)
            
            # Calculate box dimensions - further increased sizes
            h_spacing = 8  # Further reduced horizontal spacing
            v_spacing = 12  # Further reduced vertical spacing
            
            # Increase maximum box dimensions even more
            box_width = min(
                300,  # Further increased max box width
                (usable_width - (max_boxes_in_row - 1) * h_spacing) / max_boxes_in_row
            )
            box_height = min(
                250,  # Further increased max box height
                (usable_height - (total_rows - 1) * v_spacing) / total_rows
            )

            # Start position for the pyramid
            start_y = height - margin
            
            # Draw boxes row by row
            current_pos = 1
            for row_idx, num_boxes in enumerate(self.pyramid_structure):
                row_width = (num_boxes * box_width) + ((num_boxes - 1) * h_spacing)
                start_x = (width - row_width) / 2
                
                for col in range(num_boxes):
                    x = start_x + (col * (box_width + h_spacing))
                    y = start_y - (row_idx * (box_height + v_spacing))
                    
                    # Draw box outline
                    c.rect(x, y - box_height, box_width, box_height)
                    
                    pos_info = self.positions.get(current_pos, {})
                    name = pos_info.get('name', 'Empty')
                    
                    if pos_info.get('image_path') and os.path.exists(pos_info['image_path']):
                        try:
                            # Load image
                            img = Image.open(pos_info['image_path'])
                            
                            # Reserve minimal space for name to maximize image size
                            name_height = 20  # Slightly increased for bold text
                            image_area_height = box_height - name_height

                            # Draw image to fill the entire box width and available height
                            c.drawImage(
                                pos_info['image_path'],
                                x,  # Left align with box
                                y - box_height + name_height,  # Bottom align with name area
                                width=box_width,  # Fill full width
                                height=image_area_height,  # Fill available height
                                preserveAspectRatio=True  # Keep aspect ratio while filling
                            )

                            # Draw name with white background at bottom
                            c.setFillColor(colors.white)
                            c.rect(x, y - box_height, box_width, name_height, fill=True, stroke=False)
                            c.setFillColor(colors.black)
                            # Use Helvetica-Bold for names
                            c.setFont("Helvetica-Bold", 12)  # Increased font size and bold
                            c.drawCentredString(x + box_width/2, y - box_height + 7, name)

                        except Exception as e:
                            print(f"Error processing image for position {current_pos}: {str(e)}")
                            c.setFont("Helvetica-Bold", 12)
                            c.drawCentredString(x + box_width/2, y - box_height/2, name)
                    else:
                        # If no image, just draw the name centered in the box
                        c.setFont("Helvetica-Bold", 12)
                        c.drawCentredString(x + box_width/2, y - box_height/2, name)
                    
                    current_pos += 1
            
            c.save()
            messagebox.showinfo("Success", "Chart saved as PDF successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating PDF: {str(e)}")

    def save_assignments(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                data = {str(pos): {
                    'name': info['name'],
                    'image_path': info['image_path']
                } for pos, info in self.positions.items()}
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", "Assignments saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving assignments: {str(e)}")
            
    def load_assignments(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                # Clear existing assignments
                for frame in self.position_frames.values():
                    for widget in frame.winfo_children():
                        widget.destroy()
                
                self.positions.clear()
                
                # Load saved assignments
                for pos, info in data.items():
                    if os.path.exists(info['image_path']):
                        self.add_to_position(info['name'], int(pos), info['image_path'])
                    else:
                        messagebox.showwarning("Warning", 
                            f"Image not found for {info['name']}: {info['image_path']}")
                        
                messagebox.showinfo("Success", "Assignments loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading assignments: {str(e)}")

    def create_pyramid_boxes(self):
        print("Creating pyramid boxes...")  # Debug print
        
        # Clear existing boxes
        for widget in self.pyramid_frame.winfo_children():
            widget.destroy()
        
        # Reset position frames dictionary
        self.position_frames = {}
        
        # Set fixed box dimensions
        box_width = 150
        box_height = 100
        h_spacing = 30
        v_spacing = 60
        
        # Find the widest row in the pyramid structure
        max_boxes_in_row = max(self.pyramid_structure)
        
        # Calculate total width needed based on widest row
        total_width = (max_boxes_in_row * box_width) + ((max_boxes_in_row - 1) * h_spacing)
        
        # Start position counter
        current_pos = 1
        
        # Create boxes row by row, starting from the top
        for row_idx, num_boxes in enumerate(self.pyramid_structure):
            # Calculate row width and starting position to center the row
            row_width = (num_boxes * box_width) + ((num_boxes - 1) * h_spacing)
            start_x = (total_width - row_width) // 2
            
            # Create boxes for this row
            for col in range(num_boxes):
                # Create the box frame with border
                frame = ttk.Frame(
                    self.pyramid_frame,
                    style=f'Level{row_idx+1}.TFrame'
                )
                
                # Position the box
                x_pos = start_x + (col * (box_width + h_spacing))
                y_pos = row_idx * (box_height + v_spacing) + 50
                
                frame.place(
                    x=x_pos,
                    y=y_pos,
                    width=box_width,
                    height=box_height
                )
                
                # Add border to the frame
                border_frame = ttk.Frame(
                    frame,
                    style='Border.TFrame'
                )
                border_frame.place(x=0, y=0, relwidth=1, relheight=1)
                
                # Store the frame and position
                position = current_pos
                self.position_frames[position] = frame
                
                # Add click binding to both frames
                def make_click_handler(pos):
                    return lambda e: self.box_clicked(pos)
                
                click_handler = make_click_handler(position)
                frame.bind('<Button-1>', click_handler)
                border_frame.bind('<Button-1>', click_handler)
                
                # If position is empty, add "Empty" label
                if position not in self.positions:
                    empty_label = ttk.Label(frame, 
                                          text="Empty",
                                          anchor='center')
                    empty_label.pack(expand=True)
                    # Bind click to empty label as well
                    empty_label.bind('<Button-1>', click_handler)
                
                # Increment position counter
                current_pos += 1
        
        # Configure styles for each level and border
        style = ttk.Style()
        level_colors = ['#90C979', '#F4D03F', '#E67E22', '#3498DB', '#8E44AD'] * 4
        for i, color in enumerate(level_colors[:len(self.pyramid_structure)]):
            style.configure(f'Level{i+1}.TFrame', background=color)
        
        # Configure border style
        style.configure('Border.TFrame', borderwidth=1, relief='solid')
        
        print(f"Created {current_pos - 1} boxes")  # Debug print
        
        # Update scroll region
        self.pyramid_frame.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

    def box_clicked(self, position):
        """Handle click on a pyramid box"""
        try:
            if not self.name_database:
                if messagebox.askyesno("No Names", 
                    "No names in database. Would you like to add names now?"):
                    self.manage_names()
                return

            # Show name selection dialog
            dialog = NameSelectionDialog(self.root, self.name_database)
            if dialog.result:
                name = dialog.result
                image_path = self.name_database[name]
                self.add_to_position(name, position, image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding person: {str(e)}")

    def on_window_resize(self, event):
        # Only handle main window resize events
        if event.widget == self.root:
            # Add a small delay to prevent too frequent updates
            if hasattr(self, '_resize_job'):
                self.root.after_cancel(self._resize_job)
            self._resize_job = self.root.after(100, self.update_pyramid_layout)

    def update_pyramid_layout(self):
        # Store current positions
        current_positions = self.positions.copy()
        
        # Recreate pyramid with current window dimensions
        self.create_pyramid_boxes(self.level_colors)
        
        # Restore positions
        for position, data in current_positions.items():
            self.add_to_position(data['name'], position, data['image_path'])

    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame to match"""
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)

class NameManagerDialog:
    def __init__(self, parent, existing_database=None):
        self.result = None
        self.database = existing_database.copy() if existing_database else {}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manage Names")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        dialog_width = 500
        dialog_height = 400
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Names listbox
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.names_listbox = tk.Listbox(list_frame, width=40, height=10)
        self.names_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                command=self.names_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.names_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate listbox
        self.update_listbox()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Add Name", 
                  command=self.add_name).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected", 
                  command=self.remove_name).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Done", 
                  command=self.done).pack(side=tk.LEFT, padx=5)
        
        self.dialog.wait_window()
    
    def update_listbox(self):
        self.names_listbox.delete(0, tk.END)
        for name in sorted(self.database.keys()):
            self.names_listbox.insert(tk.END, name)
    
    def add_name(self):
        name_dialog = AddNameDialog(self.dialog)
        if name_dialog.result:
            name, image_path = name_dialog.result
            self.database[name] = image_path
            self.update_listbox()
    
    def remove_name(self):
        selection = self.names_listbox.curselection()
        if selection:
            name = self.names_listbox.get(selection[0])
            del self.database[name]
            self.update_listbox()
    
    def done(self):
        self.result = self.database
        self.dialog.destroy()

class AddNameDialog:
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Name")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack()
        
        # Name entry
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var).grid(row=0, column=1, pady=5)
        
        # Image selection
        ttk.Label(main_frame, text="Photo:").grid(row=1, column=0, pady=5)
        self.image_path = None
        self.image_label = ttk.Label(main_frame, text="No image selected")
        self.image_label.grid(row=1, column=1, pady=5)
        
        ttk.Button(main_frame, text="Browse...", 
                  command=self.select_image).grid(row=1, column=2, pady=5)
        
        # OK/Cancel buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="OK", 
                  command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.dialog.wait_window()
    
    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if self.image_path:
            self.image_label.config(text=os.path.basename(self.image_path))
    
    def ok_clicked(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name")
            return
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image")
            return
        
        self.result = (name, self.image_path)
        self.dialog.destroy()

class PersonDialog:
    def __init__(self, parent, positions, name_database):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Person to Position")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack()
        
        # Name selection
        ttk.Label(main_frame, text="Select Name:").grid(row=0, column=0, pady=5)
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(main_frame, 
                                     textvariable=self.name_var,
                                     values=sorted(name_database.keys()),
                                     state="readonly")
        self.name_combo.grid(row=0, column=1, pady=5)
        
        # Position selection
        ttk.Label(main_frame, text="Position:").grid(row=1, column=0, pady=5)
        self.position_var = tk.StringVar(value=str(positions[0]))
        ttk.Combobox(main_frame, 
                    textvariable=self.position_var,
                    values=positions,
                    state="readonly").grid(row=1, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", 
                  command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_var.get()
        if not name:
            messagebox.showerror("Error", "Please select a name")
            return
        
        self.result = (name, int(self.position_var.get()))
        self.dialog.destroy()

class NameSelectionDialog:
    def __init__(self, parent, name_database):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Name")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set dialog size and position
        dialog_width = 400
        dialog_height = 250
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name selection with better spacing
        ttk.Label(main_frame, text="Select a name to add:", 
                 font=('TkDefaultFont', 12)).pack(pady=(0,10))
        
        # Combobox for name selection
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(main_frame, 
                                     textvariable=self.name_var,
                                     values=sorted(name_database.keys()),
                                     state="readonly",
                                     width=40)
        self.name_combo.pack(pady=(0,20))
        
        # Buttons with better styling
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20,0))
        
        # Style buttons
        ttk.Button(button_frame, text="Add", 
                  command=self.ok_clicked,
                  style='Accent.TButton',
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy,
                  width=15).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog on screen
        self.dialog.update_idletasks()
        self.dialog.geometry(f"+{x}+{y}")
        
        # Make dialog modal
        self.dialog.focus_set()
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_var.get()
        if not name:
            messagebox.showerror("Error", "Please select a name")
            return
        
        self.result = name
        self.dialog.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.geometry("800x600")  # Initial size
        root.minsize(600, 400)    # Minimum size
        app = PyramidChart(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {str(e)}")















