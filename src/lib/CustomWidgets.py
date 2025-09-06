import customtkinter as ctk
import math
import time

from CTkColorPicker import CTkColorPicker


class QuackExtendedButton(ctk.CTkButton):
    def __init__(
        self, master=None, longpress_callback=None, longpress_threshold=550, **kwargs
    ):
        super().__init__(master=master, **kwargs)

        # Long press configuration
        self.longpress_callback = longpress_callback
        self.longpress_threshold = longpress_threshold

        # Long press state variables
        self.press_start_time = None
        self.is_long_press = False
        self.longpress_timer_id = None
        self.normal_command = None

        # Scroll detection variables
        self.parent_is_scrolling = False

        # Store the original command and replace it with our handler
        if "command" in kwargs:
            self.normal_command = kwargs["command"]

        # Override the command to disable default behavior
        super().configure(command=lambda: None)

        # Bind our event handlers
        self.bind("<Button-1>", self._on_button_press)
        self.bind("<ButtonRelease-1>", self._on_button_release)

    def configure(self, **kwargs):
        """Override configure to handle command parameter"""
        if "command" in kwargs:
            self.normal_command = kwargs["command"]
            del kwargs["command"]  # Remove it so parent doesn't get it

        if "longpress_callback" in kwargs:
            self.longpress_callback = kwargs["longpress_callback"]
            del kwargs["longpress_callback"]

        if "longpress_threshold" in kwargs:
            self.longpress_threshold = kwargs["longpress_threshold"]
            del kwargs["longpress_threshold"]

        super().configure(**kwargs)

    def _trigger_long_press(self):
        """Triggered automatically when long press threshold is reached"""
        if not self.parent_is_scrolling:  # Only trigger if not scrolling
            self.is_long_press = True
            if self.longpress_callback:
                self.longpress_callback()

    def _handle_parent_scroll_start(self):
        """Called by parent TouchScrollableFrame when scrolling starts"""
        self.parent_is_scrolling = True
        # Cancel the long press timer since scrolling started
        if self.longpress_timer_id is not None:
            self.after_cancel(self.longpress_timer_id)
            self.longpress_timer_id = None

    def _on_button_press(self, event):
        """Handle button press start"""
        self.press_start_time = time.time()
        self.is_long_press = False
        self.parent_is_scrolling = False

        # Schedule long press trigger
        if self.longpress_callback:
            self.longpress_timer_id = self.after(
                int(self.longpress_threshold), self._trigger_long_press
            )

    def _on_button_release(self, event):
        """Handle button release"""
        if self.press_start_time is None:
            return

        # Cancel the long press timer if it hasn't triggered yet
        if self.longpress_timer_id is not None:
            self.after_cancel(self.longpress_timer_id)
            self.longpress_timer_id = None

        # Only execute normal command if it wasn't a long press and parent wasn't scrolling
        if (
            not self.is_long_press
            and not self.parent_is_scrolling
            and self.normal_command
        ):
            self.normal_command()

        # Reset state
        self.press_start_time = None
        self.parent_is_scrolling = False

    def set_long_press_callback(self, callback):
        """Set the long press callback function"""
        self.longpress_callback = callback

    def set_normal_command(self, command):
        """Set the normal (short press) command function"""
        self.normal_command = command


class ToggleButton(ctk.CTkButton):
    def __init__(
        self,
        # variable: ctk.BooleanVar = None,
        toggled_color="#d33c34",
        hover_toggled=None,
        toggled_text=None,
        *args,
        **kwargs
    ):
        if toggled_text is None:
            toggled_text = kwargs.get("text", "")
        if hover_toggled is None:
            hover_toggled = toggled_color

        # self._variable = variable
        self._hover_toggled = hover_toggled
        self._toggled_color = toggled_color
        self._toggled_text = toggled_text
        self._untoggled_text = kwargs.get("text", "")

        super().__init__(*args, **kwargs)

        self._untoggled_color = self.cget("fg_color")
        self._hover_untoggled = self.cget("hover_color")
        self._toggled = False

    def _cmd_pre(self):
        self._toggled = not self._toggled
        if self._toggled:
            self.configure(
                fg_color=self._toggled_color,
                text=self._toggled_text,
                hover_color=self._hover_toggled,
            )
        else:
            self.configure(
                fg_color=self._untoggled_color,
                text=self._untoggled_text,
                hover_color=self._hover_untoggled,
            )

    def configure(self, **kwargs):
        """Override configure to handle command parameter"""
        if "command" in kwargs:

            cmd = kwargs["command"]
            kwargs["command"] = lambda: (self._cmd_pre(), cmd(self._toggled))
        super().configure(**kwargs)

    def toggle(self, state=None):
        if state is not None:
            self._toggled = not state # will be updated in `self._cmd_pre`
        self._command()


class TouchScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)

        # Bind to all widgets in the frame, including children
        self.bind_all("<Button-1>", self.start_touch_all)
        self.bind_all("<B1-Motion>", self.on_touch_move_all)
        self.bind_all("<ButtonRelease-1>", self.end_touch_all)

        self.last_touch_y = 0
        self.last_touch_time = 0
        self.velocity = 0
        self.is_touching = False
        self.momentum_after_id = None
        self.scroll_active = False

        self.sensitivity = 8.0
        self.friction = 0.9
        self.momentumThreshold = 50  # Minimum velocity to start momentum scrolling
        self.updateRate = 16  # Update rate for momentum scrolling in milliseconds

    def _is_event_in_frame(self, event):
        """Check if the event originated within this scrollable frame"""
        widget = event.widget
        # Walk up the widget hierarchy to see if we're inside this frame
        while widget:
            if widget == self:
                return True
            try:
                widget = widget.master
            except AttributeError:
                widget = None
        return False

    def start_touch_all(self, event):
        if not self._is_event_in_frame(event):
            return

        self.is_touching = True
        self.scroll_active = False
        self.last_touch_y = event.y_root
        self.last_touch_time = time.time()
        # Cancel any existing momentum
        if self.momentum_after_id:
            self.after_cancel(self.momentum_after_id)
            self.momentum_after_id = None

    def on_touch_move_all(self, event):
        if not self._is_event_in_frame(event) or not self.is_touching:
            return

        current_time = time.time()
        current_y = event.y_root

        # Calculate movement
        y_diff = current_y - self.last_touch_y

        # If we detect significant movement, activate scrolling
        if abs(y_diff) > 5 and not self.scroll_active:
            self.scroll_active = True
            # Notify any QuackExtendedButtons that scrolling has started
            self._notify_buttons_scrolling_started(event)

        if self.scroll_active:
            # Calculate time difference (avoid division by zero)
            time_diff = current_time - self.last_touch_time
            if time_diff < 0.001:  # Less than 1ms, too fast to be meaningful
                return

            # Calculate velocity (pixels per second)
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

    def _notify_buttons_scrolling_started(self, event):
        """Find any QuackExtendedButtons and notify them that scrolling has started"""

        def find_buttons(widget):
            buttons = []
            if isinstance(widget, QuackExtendedButton):
                buttons.append(widget)
            for child in widget.winfo_children():
                buttons.extend(find_buttons(child))
            return buttons

        buttons = find_buttons(self)
        for button in buttons:
            button._handle_parent_scroll_start()

    def end_touch_all(self, event):
        if not self._is_event_in_frame(event):
            return

        self.is_touching = False

        # Start momentum scrolling if velocity is significant and we were actively scrolling
        if self.scroll_active and abs(self.velocity) > self.momentumThreshold:
            self.apply_momentum()

        self.scroll_active = False

    # Keep the old methods for backward compatibility
    def start_touch(self, event):
        self.start_touch_all(event)

    def on_touch_move(self, event):
        self.on_touch_move_all(event)

    def end_touch(self, event):
        self.end_touch_all(event)

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
        self.momentum_after_id = self.after(
            self.updateRate, self.apply_momentum
        )  # ~60fps


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
        self.canvas.create_image(
            self.image_dimension / 2,
            self.image_dimension / 2,
            image=self.wheel,
            anchor="center",
        )

        d_from_center = math.sqrt(
            ((self.image_dimension / 2) - x) ** 2
            + ((self.image_dimension / 2) - y) ** 2
        )

        if d_from_center < self.image_dimension / 2:
            self.target_x, self.target_y = x, y
        else:
            self.target_x, self.target_y = self.projection_on_circle(
                x,
                y,
                self.image_dimension / 2,
                self.image_dimension / 2,
                self.image_dimension / 2 - 1,
            )

        self.canvas.create_image(
            self.target_x, self.target_y, image=self.target, anchor="center"
        )

        self.get_target_color()
        self.update_colors()

    def update_colors(self):
        brightness = self.brightness_slider_value.get()

        self.get_target_color()

        r = int(self.rgb_color[0] * (brightness / 255))
        g = int(self.rgb_color[1] * (brightness / 255))
        b = int(self.rgb_color[2] * (brightness / 255))

        self.rgb_color = [r, g, b]

        self.default_hex_color = "#{:02x}{:02x}{:02x}".format(*self.rgb_color)

        self.slider.configure(progress_color=self.default_hex_color)

        if self.command:
            self.command(self.rgb_color)
