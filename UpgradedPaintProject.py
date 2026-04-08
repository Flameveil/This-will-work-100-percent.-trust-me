import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import random
import io


class PaintApp:
    def __init__(self, root):
        """Initialize application and state."""
        self.root = root
        self.root.title("Advanced Paint App")
        self.root.geometry("1000x650")

        # ===== Drawing State =====
        self.current_color = "black"
        self.tool = "pen"
        self.dark_mode = False

        # Undo system (stores last 5 states)
        self.undo_stack = []

        # Preview shape
        self.preview_shape = None

        # Image buffer
        self.image = Image.new("RGB", (1000, 650), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.tk_image = None  # for displaying images

        self.setup_ui()

    # ===============================
    # UI SETUP
    # ===============================
    def setup_ui(self):
        self.toolbar = tk.Frame(self.root, bg="lightgray")
        self.toolbar.pack(fill=tk.X)

        # ===== Colors (expanded) =====
        colors = [
            "black", "red", "green", "blue",
            "purple", "yellow", "pink",
            "gray", "orange", "brown"
        ]

        for color in colors:
            tk.Button(self.toolbar, bg=color, width=3,
                      command=lambda c=color: self.set_color(c)).pack(side=tk.LEFT, padx=2)

        self.color_label = tk.Label(self.toolbar, text="Color: Black")
        self.color_label.pack(side=tk.LEFT, padx=10)

        # ===== Pen Width =====
        self.width_slider = tk.Scale(self.toolbar, from_=1, to=25,
                                     orient=tk.HORIZONTAL, label="Width")
        self.width_slider.set(3)
        self.width_slider.pack(side=tk.LEFT)

        # ===== Tools =====
        tools = ["pen", "eraser", "rectangle", "oval", "triangle", "spray"]
        for t in tools:
            tk.Button(self.toolbar, text=t.capitalize(),
                      command=lambda tool=t: self.set_tool(tool)).pack(side=tk.LEFT)

        # ===== Actions =====
        tk.Button(self.toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Load", command=self.load_image).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Insert Image", command=self.insert_image).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Dark Mode", command=self.toggle_dark_mode).pack(side=tk.LEFT)

        # ===== Canvas =====
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        self.start_x = None
        self.start_y = None

    # ===============================
    # STATE MANAGEMENT
    # ===============================
    def set_color(self, color):
        self.current_color = color
        self.color_label.config(text=f"Color: {color.capitalize()}")

    def set_tool(self, tool):
        self.tool = tool

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#2b2b2b" if self.dark_mode else "lightgray"
        fg = "white" if self.dark_mode else "black"

        self.toolbar.config(bg=bg)
        self.color_label.config(bg=bg, fg=fg)

    # ===============================
    # DRAWING
    # ===============================
    def start_draw(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.save_undo_state()

        if self.preview_shape:
            self.canvas.delete(self.preview_shape)
            self.preview_shape = None

    def draw_motion(self, event):
        width = self.width_slider.get()

        if self.tool == "pen":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.current_color, width=width, smooth=True)
            self.draw.line([self.start_x, self.start_y, event.x, event.y],
                           fill=self.current_color, width=width)
            self.start_x, self.start_y = event.x, event.y

        elif self.tool == "eraser":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill="white", width=width)
            self.draw.line([self.start_x, self.start_y, event.x, event.y],
                           fill="white", width=width)
            self.start_x, self.start_y = event.x, event.y

        elif self.tool == "spray":
            for _ in range(20):
                x = event.x + random.randint(-10, 10)
                y = event.y + random.randint(-10, 10)
                self.canvas.create_oval(x, y, x+1, y+1, fill=self.current_color)
                self.draw.point((x, y), fill=self.current_color)

        else:
            if self.preview_shape:
                self.canvas.delete(self.preview_shape)

            if self.tool == "rectangle":
                self.preview_shape = self.canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    outline=self.current_color, width=width
                )

            elif self.tool == "oval":
                self.preview_shape = self.canvas.create_oval(
                    self.start_x, self.start_y, event.x, event.y,
                    outline=self.current_color, width=width
                )

            elif self.tool == "triangle":
                points = [
                    self.start_x, event.y,
                    (self.start_x + event.x) // 2, self.start_y,
                    event.x, event.y
                ]
                self.preview_shape = self.canvas.create_polygon(
                    points, outline=self.current_color, fill="", width=width
                )

    def end_draw(self, event):
        width = self.width_slider.get()

        if self.preview_shape:
            self.canvas.delete(self.preview_shape)
            self.preview_shape = None

        if self.tool == "rectangle":
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                         outline=self.current_color, width=width)
            self.draw.rectangle([self.start_x, self.start_y, event.x, event.y],
                                outline=self.current_color, width=width)

        elif self.tool == "oval":
            self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                    outline=self.current_color, width=width)
            self.draw.ellipse([self.start_x, self.start_y, event.x, event.y],
                              outline=self.current_color, width=width)

        elif self.tool == "triangle":
            points = [
                (self.start_x, event.y),
                ((self.start_x + event.x) // 2, self.start_y),
                (event.x, event.y)
            ]
            self.canvas.create_polygon(points, outline=self.current_color,
                                       fill="", width=width)
            self.draw.polygon(points, outline=self.current_color)

    # ===============================
    # IMAGE INSERT FEATURE
    # ===============================
    def insert_image(self):
        """Insert an image onto the canvas and into the drawing buffer."""
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not path:
            return

        img = Image.open(path)
        img = img.resize((300, 300))  # resize for convenience

        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(50, 50, anchor=tk.NW, image=self.tk_image)

        # Paste into drawing buffer so it saves
        self.image.paste(img, (50, 50))

    # ===============================
    # CANVAS CONTROLS
    # ===============================
    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (1000, 650), "white")
        self.draw = ImageDraw.Draw(self.image)

    # ===============================
    # UNDO SYSTEM
    # ===============================
    def save_undo_state(self):
        if len(self.undo_stack) >= 5:
            self.undo_stack.pop(0)

        buffer = io.BytesIO()
        self.image.save(buffer, format="PNG")
        self.undo_stack.append(buffer.getvalue())

    def undo(self):
        if not self.undo_stack:
            return

        data = self.undo_stack.pop()
        self.image = Image.open(io.BytesIO(data))
        self.draw = ImageDraw.Draw(self.image)
        self.redraw_canvas()

    def redraw_canvas(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    # ===============================
    # SAVE / LOAD
    # ===============================
    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            self.image.save(path)

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image = Image.open(path)
            self.draw = ImageDraw.Draw(self.image)
            self.redraw_canvas()


# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()