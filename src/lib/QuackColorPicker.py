import math
from CTkColorPicker import CTkColorPicker

class QuackColorPicker(CTkColorPicker):
    def __init__(self, master=None, orientation="vertical", **kwargs):
        super().__init__(master=master, orientation=orientation, **kwargs)
        self.configure(fg_color=master._fg_color)

        self.label.destroy()
        self.canvas.pack_forget()
        self.slider.pack_forget()    
        self.pack_forget()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)

        self.canvas.configure(bg=master._fg_color)

        self.slider.configure(width=40)

        if orientation == "vertical":
            self.canvas.grid(row=0, column=0, padx=20, pady=15, sticky="")
            self.slider.grid(row=0, column=1, padx=20, pady=15, sticky="nsw")
        else:
            self.canvas.grid(row=0, column=0, padx=15, pady=15, sticky="")
            self.slider.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="sew")

    def configure(self, **kwargs):
        if "command" in kwargs:
            self.command = kwargs["command"]
            del kwargs["command"]

        super().configure(**kwargs)

    def on_mouse_drag(self, event):
        x = event.x
        y = event.y
        self.canvas.delete("all")
        self.canvas.create_image(self.image_dimension/2, self.image_dimension/2, image=self.wheel, anchor="center")
        
        d_from_center = math.sqrt(((self.image_dimension/2)-x)**2 + ((self.image_dimension/2)-y)**2)
        
        if d_from_center < self.image_dimension/2:
            self.target_x, self.target_y = x, y
        else:
            self.target_x, self.target_y = self.projection_on_circle(x, y, self.image_dimension/2, self.image_dimension/2, self.image_dimension/2 -1)

        self.canvas.create_image(self.target_x, self.target_y, image=self.target, anchor="center")
        
        self.get_target_color()
        self.update_colors()

    def update_colors(self):
        brightness = self.brightness_slider_value.get()

        self.get_target_color()

        r = int(self.rgb_color[0] * (brightness/255))
        g = int(self.rgb_color[1] * (brightness/255))
        b = int(self.rgb_color[2] * (brightness/255))
        
        self.rgb_color = [r, g, b]

        self.default_hex_color = "#{:02x}{:02x}{:02x}".format(*self.rgb_color)
        
        self.slider.configure(progress_color=self.default_hex_color)

        if self.command:
            self.command(self.rgb_color)
