import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import random
import io
from collections import deque


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Paint App")
        self.root.geometry("1000x650")

        self.current_color = "black"
        self.tool = "pen"
        self.dark_mode = False

        self.undo_stack = []
        self.preview_shape = None

        self.image_to_insert = None
        self.waiting_for_placement = False

        # Track dynamic canvas size
        self.canvas_width = 1000
        self.canvas_height = 650

        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.tk_image = None

        self.setup_ui()

    # ===============================
    # UI SETUP
    # ===============================
    def setup_ui(self):
        self.toolbar = tk.Frame(self.root, bg="lightgray")
        self.toolbar.pack(fill=tk.X)

        colors = ["black", "red", "green", "blue",
                  "purple", "yellow", "pink",
                  "gray", "orange", "brown"]

        for color in colors:
            tk.Button(self.toolbar, bg=color, width=3,
                      command=lambda c=color: self.set_color(c)).pack(side=tk.LEFT, padx=2)

        self.color_label = tk.Label(self.toolbar, text="Color: Black")
        self.color_label.pack(side=tk.LEFT, padx=10)

        self.width_slider = tk.Scale(self.toolbar, from_=1, to=25,
                                     orient=tk.HORIZONTAL, label="Width")
        self.width_slider.set(3)
        self.width_slider.pack(side=tk.LEFT)

        tools = ["pen", "eraser", "rectangle", "oval", "triangle", "spray", "fill"]
        for t in tools:
            tk.Button(self.toolbar, text=t.capitalize(),
                      command=lambda tool=t: self.set_tool(tool)).pack(side=tk.LEFT)

        tk.Button(self.toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Load", command=self.load_image).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Insert Image", command=self.insert_image).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Dark Mode", command=self.toggle_dark_mode).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Resize binding
        self.canvas.bind("<Configure>", self.on_resize)

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        self.start_x = None
        self.start_y = None

    # ===============================
    # RESIZE HANDLING
    # ===============================
    def on_resize(self, event):
        if event.width < 10 or event.height < 10:
            return

        # Resize PIL image to match canvas
        new_image = self.image.resize((event.width, event.height))
        self.image = new_image
        self.draw = ImageDraw.Draw(self.image)

        self.canvas_width = event.width
        self.canvas_height = event.height

        self.redraw_canvas()

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
        # Image placement
        if self.waiting_for_placement and self.image_to_insert:
            x, y = event.x, event.y
            self.tk_image = ImageTk.PhotoImage(self.image_to_insert)
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)
            self.image.paste(self.image_to_insert, (x, y))
            self.waiting_for_placement = False
            self.image_to_insert = None
            return

        self.start_x, self.start_y = event.x, event.y
        self.save_undo_state()

        # Fill tool (NOW WORKS AFTER RESIZE)
        if self.tool == "fill":
            try:
                target_color = self.image.getpixel((event.x, event.y))
                replacement_color = Image.new("RGB", (1, 1), self.current_color).getpixel((0, 0))
                self.flood_fill(event.x, event.y, target_color, replacement_color)
                self.redraw_canvas()
            except:
                pass
            return

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

    def end_draw(self, event):
        pass  # Shapes unchanged for brevity

    # ===============================
    # FLOOD FILL
    # ===============================
    def flood_fill(self, x, y, target_color, replacement_color):
        width, height = self.image.size
        pixels = self.image.load()

        if target_color == replacement_color:
            return

        queue = deque([(x, y)])

        while queue:
            px, py = queue.popleft()

            if px < 0 or py < 0 or px >= width or py >= height:
                continue

            if pixels[px, py] != target_color:
                continue

            pixels[px, py] = replacement_color

            queue.append((px+1, py))
            queue.append((px-1, py))
            queue.append((px, py+1))
            queue.append((px, py-1))

    # ===============================
    # IMAGE INSERT
    # ===============================
    def insert_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return

        img = Image.open(path)
        img = img.resize((300, 300))

        self.image_to_insert = img
        self.waiting_for_placement = True

    # ===============================
    # CONTROLS
    # ===============================
    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

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

    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            self.image.save(path)

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image = Image.open(path).resize((self.canvas_width, self.canvas_height))
            self.draw = ImageDraw.Draw(self.image)
            self.redraw_canvas()


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()