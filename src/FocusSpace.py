import customtkinter as ctk
import markdown
from tkinter import messagebox, filedialog, font
import os
import json

class FocusSpace(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Get system fonts
        self.available_fonts = sorted(font.families())
        
        # Configure window
        self.title("Empty Focus Space")
        self.geometry("800x600")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        # Set appearance mode and theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Set background color
        self.configure(fg_color=self.settings["appearance"]["background_color"])
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color=self.settings["appearance"]["background_color"])
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create menu frame (initially hidden)
        self.menu_frame = ctk.CTkFrame(
            self.main_container, 
            height=self.settings["layout"]["menu_height"],
            fg_color=self.settings["appearance"]["background_color"]
        )
        self.menu_frame.place(x=0, y=0, relwidth=1.0)  # Place at the top
        
        # Add file menu buttons
        self.open_button = ctk.CTkButton(
            self.menu_frame,
            text="Open (Ctrl+O)",
            command=self.open_file,
            width=100,
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            fg_color=self.settings["appearance"]["background_color"],
            text_color=self.settings["appearance"]["text_color"],
            hover_color=self.settings["appearance"]["button_hover_color"]
        )
        self.open_button.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.save_button = ctk.CTkButton(
            self.menu_frame,
            text="Save (Ctrl+S)",
            command=self.save_file,
            width=100,
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            fg_color=self.settings["appearance"]["background_color"],
            text_color=self.settings["appearance"]["text_color"],
            hover_color=self.settings["appearance"]["button_hover_color"]
        )
        self.save_button.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        # Font selection combobox
        self.font_label = ctk.CTkLabel(
            self.menu_frame,
            text="Font:",
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            text_color=self.settings["appearance"]["text_color"]
        )
        self.font_label.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.font_combobox = ctk.CTkComboBox(
            self.menu_frame,
            values=self.available_fonts,
            command=self.change_font,
            width=150,
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            dropdown_font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            fg_color=self.settings["appearance"]["background_color"],
            text_color=self.settings["appearance"]["text_color"],
            button_color=self.settings["appearance"]["background_color"],
            button_hover_color=self.settings["appearance"]["button_hover_color"]
        )
        # Set default font if it exists in system fonts, otherwise use the first available font
        if self.settings["text"]["default_font"] in self.available_fonts:
            self.font_combobox.set(self.settings["text"]["default_font"])
        else:
            self.font_combobox.set(self.available_fonts[0])
        self.font_combobox.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        # Font size controls in the same row
        self.font_size = self.settings["text"]["default_font_size"]
        self.font_size_label = ctk.CTkLabel(
            self.menu_frame, 
            text=f"Font Size: {self.font_size}",
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            text_color=self.settings["appearance"]["text_color"]
        )
        self.font_size_label.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.decrease_font = ctk.CTkButton(
            self.menu_frame,
            text="-",
            width=30,
            command=self.decrease_font_size,
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            fg_color=self.settings["appearance"]["background_color"],
            text_color=self.settings["appearance"]["text_color"],
            hover_color=self.settings["appearance"]["button_hover_color"]
        )
        self.decrease_font.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.increase_font = ctk.CTkButton(
            self.menu_frame,
            text="+",
            width=30,
            command=self.increase_font_size,
            font=(self.settings["text"]["default_font"], self.settings["text"]["button_font_size"]),
            fg_color=self.settings["appearance"]["background_color"],
            text_color=self.settings["appearance"]["text_color"],
            hover_color=self.settings["appearance"]["button_hover_color"]
        )
        self.increase_font.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        # Add margin control buttons
        self.top_margin_label = ctk.CTkLabel(
            self.menu_frame,
            text=f"Top Margin: {self.settings['layout']['top_margin']}px",
            width=120
        )
        self.top_margin_label.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.increase_top_margin_btn = ctk.CTkButton(
            self.menu_frame,
            text="+",
            width=30,
            command=self.increase_top_margin_func
        )
        self.increase_top_margin_btn.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.decrease_top_margin_btn = ctk.CTkButton(
            self.menu_frame,
            text="-",
            width=30,
            command=self.decrease_top_margin_func
        )
        self.decrease_top_margin_btn.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.left_margin_label = ctk.CTkLabel(
            self.menu_frame,
            text=f"Left Margin: {self.settings['layout']['left_margin']}px",
            width=120
        )
        self.left_margin_label.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.increase_left_margin_btn = ctk.CTkButton(
            self.menu_frame,
            text="+",
            width=30,
            command=self.increase_left_margin_func
        )
        self.increase_left_margin_btn.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        self.decrease_left_margin_btn = ctk.CTkButton(
            self.menu_frame,
            text="-",
            width=30,
            command=self.decrease_left_margin_func
        )
        self.decrease_left_margin_btn.pack(side="left", padx=self.settings["layout"]["menu_padding"])
        
        # Create text widget with margins
        self.text_widget = ctk.CTkTextbox(
            self.main_container,
            wrap="word",
            font=(self.settings["text"]["default_font"], self.settings["text"]["default_font_size"]),
            fg_color=self.settings["appearance"]["background_color"],
            text_color=self.settings["appearance"]["text_color"]
        )
        self.text_widget.pack(fill="both", expand=True, padx=self.settings["layout"]["left_margin"], pady=self.settings["layout"]["top_margin"])
        
        # Configure cursor color and blink rate using the underlying Tkinter text widget
        self.text_widget._textbox.configure(
            insertbackground=self.settings["appearance"]["cursor_color"],
            insertontime=self.settings["appearance"]["cursor_blink_on_time"],
            insertofftime=self.settings["appearance"]["cursor_blink_off_time"]
        )
        
        # Current file path
        self.current_file = None
        
        # Bind keyboard shortcuts
        self.bind(self.settings["shortcuts"]["open_file"], lambda e: self.open_file())
        self.bind(self.settings["shortcuts"]["save_file"], lambda e: self.save_file())
        self.bind(self.settings["shortcuts"]["toggle_fullscreen"], self.toggle_fullscreen)
        self.bind(self.settings["shortcuts"]["increase_font"], lambda e: self.increase_font_size())
        self.bind(self.settings["shortcuts"]["decrease_font"], lambda e: self.decrease_font_size())
        self.bind(self.settings["shortcuts"]["increase_top_margin"], lambda e: self.increase_top_margin_func())
        self.bind(self.settings["shortcuts"]["decrease_top_margin"], lambda e: self.decrease_top_margin_func())
        self.bind(self.settings["shortcuts"]["increase_left_margin"], lambda e: self.increase_left_margin_func())
        self.bind(self.settings["shortcuts"]["decrease_left_margin"], lambda e: self.decrease_left_margin_func())
        
        # Bind mouse events for showing/hiding controls
        self.bind("<Motion>", self.handle_mouse_motion)
        self.text_widget.bind("<Motion>", self.handle_mouse_motion)
        
        # Initially hide the controls
        self.menu_frame.place_forget()
        
        # Start in fullscreen mode
        self.attributes("-fullscreen", True)
        
    def load_settings(self):
        """Load settings from settings.json file."""
        try:
            with open(os.path.join(os.path.dirname(__file__), "settings.json"), "r") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load settings: {str(e)}")
            return {}
            
    def handle_mouse_motion(self, event):
        """Show/hide controls based on mouse position."""
        if event.y < 50:  # If mouse is near the top
            self.menu_frame.place(x=0, y=0, relwidth=1.0)
        else:
            self.menu_frame.place_forget()
        
    def open_file(self):
        """Open a markdown file and display its contents."""
        file_path = filedialog.askopenfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_widget.delete('1.0', 'end')
                    self.text_widget.insert('1.0', content)
                    self.current_file = file_path
                    self.title(f"Empty Focus Space - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save the current content as a markdown file."""
        if not self.current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            content = self.text_widget.get('1.0', 'end-1c')
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            self.title(f"Empty Focus Space - {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            
    def change_font(self, choice):
        """Change the font of the text widget."""
        self.text_widget.configure(font=(choice, self.font_size))
            
    def decrease_font_size(self):
        """Decrease the font size of the text widget."""
        if self.font_size > self.settings["text"]["min_font_size"]:
            self.font_size -= self.settings["text"]["font_size_step"]
            self.update_font_size()
            
    def increase_font_size(self):
        """Increase the font size of the text widget."""
        if self.font_size < self.settings["text"]["max_font_size"]:
            self.font_size += self.settings["text"]["font_size_step"]
            self.update_font_size()
            
    def update_font_size(self):
        """Update the font size of the text widget and the label."""
        current_font = self.font_combobox.get()
        self.text_widget.configure(font=(current_font, self.font_size))
        self.font_size_label.configure(text=f"Font Size: {self.font_size}")
        
    def increase_top_margin_func(self):
        """Increase the top margin"""
        self.settings["layout"]["top_margin"] += 10
        self.update_margins()
        
    def decrease_top_margin_func(self):
        """Decrease the top margin"""
        if self.settings["layout"]["top_margin"] > 10:
            self.settings["layout"]["top_margin"] -= 10
            self.update_margins()
            
    def increase_left_margin_func(self):
        """Increase the left margin"""
        self.settings["layout"]["left_margin"] += 10
        self.update_margins()
        
    def decrease_left_margin_func(self):
        """Decrease the left margin"""
        if self.settings["layout"]["left_margin"] > 10:
            self.settings["layout"]["left_margin"] -= 10
            self.update_margins()
            
    def update_margins(self):
        """Update the text widget margins and labels"""
        self.text_widget.pack_configure(
            padx=self.settings["layout"]["left_margin"],
            pady=self.settings["layout"]["top_margin"]
        )
        self.top_margin_label.configure(text=f"Top Margin: {self.settings['layout']['top_margin']}px")
        self.left_margin_label.configure(text=f"Left Margin: {self.settings['layout']['left_margin']}px")
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.attributes("-fullscreen", not self.attributes("-fullscreen")) 