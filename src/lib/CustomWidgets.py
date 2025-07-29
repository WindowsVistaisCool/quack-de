import customtkinter as ctk
import math
import time
from CTkColorPicker import CTkColorPicker

class TouchScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)

        self.bind("<Button-1>", self.start_touch)
        self.bind("<B1-Motion>", self.on_touch_move)
        self.bind("<ButtonRelease-1>", self.end_touch)

        self.last_touch_y = 0
        self.last_touch_time = 0
        self.velocity = 0
        self.is_touching = False
        self.momentum_after_id = None

        self.sensitivity = 8.0
        self.friction = 0.9
        self.momentumThreshold = 50  # Minimum velocity to start momentum scrolling
        self.updateRate = 16  # Update rate for momentum scrolling in milliseconds

    def start_touch(self, event):
        self.is_touching = True
        self.last_touch_y = event.y_root
        self.last_touch_time = time.time()
        # Cancel any existing momentum
        if self.momentum_after_id:
            self.after_cancel(self.momentum_after_id)
            self.momentum_after_id = None

    def on_touch_move(self, event):
        if not self.is_touching:
            return
            
        current_time = time.time()
        current_y = event.y_root
        
        # Calculate time difference (avoid division by zero)
        time_diff = current_time - self.last_touch_time
        if time_diff < 0.001:  # Less than 1ms, too fast to be meaningful
            return
        
        # Calculate velocity (pixels per second)
        y_diff = current_y - self.last_touch_y
        self.velocity = y_diff / time_diff

        # Apply immediate scrolling based on movement
        if abs(y_diff) > 0:
            canvas = self._parent_canvas
            # Convert pixel movement to scroll units
            scroll_delta = -y_diff / self.sensitivity
            current_view = canvas.yview()[0]
            new_view = max(0.0, min(1.0, current_view + scroll_delta / 100.0))
            canvas.yview_moveto(new_view)
        
        self.last_touch_y = current_y
        self.last_touch_time = current_time
    
    def end_touch(self, _):
        self.is_touching = False

        # Start momentum scrolling if velocity is significant
        if abs(self.velocity) > self.momentumThreshold:  # Minimum velocity threshold
            self.apply_momentum()

    def apply_momentum(self):
        if abs(self.velocity) < 10:  # Stop when velocity is too small
            self.momentum_after_id = None
            return
        
        # Apply momentum scroll
        canvas = self._parent_canvas
        scroll_delta = self.velocity / 1000.0  # Convert to scroll units
        current_view = canvas.yview()[0]
        new_view = max(0.0, min(1.0, current_view - scroll_delta / 100.0))
        canvas.yview_moveto(new_view)
        
        # Decay velocity
        self.velocity *= self.friction
        # Schedule next momentum update
        self.momentum_after_id = self.after(self.updateRate, self.apply_momentum)  # ~60fps

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
