import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import pyperclip

# pyautogui safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

class AutoTyperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typer GUI (File & Text Auto-Typing)")
        self.root.geometry("620x580")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.is_running = False
        self.stop_requested = False

        self.setup_ui()

    def setup_ui(self):
        # Header Title
        title_label = tk.Label(
            self.root, 
            text="⚡ Auto Typer Automation Utility", 
            font=("Segoe UI", 16, "bold"), 
            bg="#1e1e2e", 
            fg="#cdd6f4"
        )
        title_label.pack(pady=(15, 5))

        subtitle = tk.Label(
            self.root,
            text="फाइल चुनें या नीचे टेक्स्ट लिखें, 'Start' दबाएं और जहाँ टाइप कराना है वहाँ क्लिक करें।",
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#a6adc8"
        )
        subtitle.pack(pady=(0, 10))

        # File Chooser Frame
        file_frame = tk.Frame(self.root, bg="#1e1e2e")
        file_frame.pack(fill="x", padx=20, pady=5)

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(
            file_frame, 
            textvariable=self.file_path_var, 
            font=("Consolas", 10),
            bg="#313244", 
            fg="#cdd6f4", 
            insertbackground="#cdd6f4",
            bd=1,
            relief=tk.FLAT
        )
        file_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))

        choose_btn = tk.Button(
            file_frame, 
            text="📁 Browse File (.txt)", 
            command=self.browse_file,
            font=("Segoe UI", 9, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            cursor="hand2",
            bd=0,
            padx=12,
            pady=4
        )
        choose_btn.pack(side="right")

        # Text Area Preview / Direct Input
        text_label = tk.Label(
            self.root, 
            text="Content / Text to Type (File का डाटा यहाँ दिखेगा या आप सीधे भी लिख सकते हैं):", 
            font=("Segoe UI", 9, "bold"), 
            bg="#1e1e2e", 
            fg="#cdd6f4"
        )
        text_label.pack(anchor="w", padx=20, pady=(10, 3))

        self.text_area = tk.Text(
            self.root, 
            height=9, 
            font=("Consolas", 10), 
            bg="#313244", 
            fg="#cdd6f4", 
            insertbackground="#cdd6f4",
            bd=1,
            relief=tk.FLAT,
            wrap="word"
        )
        self.text_area.pack(fill="x", padx=20, pady=5)

        # Settings Frame (Delay & Speed)
        settings_frame = tk.Frame(self.root, bg="#1e1e2e")
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Countdown delay
        tk.Label(settings_frame, text="Start Delay (Seconds):", font=("Segoe UI", 9), bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        self.delay_spin = tk.Spinbox(settings_frame, from_=1, to=30, width=6, font=("Segoe UI", 10), bg="#313244", fg="#cdd6f4", bd=1)
        self.delay_spin.delete(0, "end")
        self.delay_spin.insert(0, "5")
        self.delay_spin.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=2)

        # Typing Speed / interval
        tk.Label(settings_frame, text="Typing Speed (Sec/char):", font=("Segoe UI", 9), bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=2, sticky="w", padx=(0, 5), pady=2)
        self.speed_spin = tk.Spinbox(settings_frame, from_=0.001, to=1.0, increment=0.01, width=6, font=("Segoe UI", 10), bg="#313244", fg="#cdd6f4", bd=1)
        self.speed_spin.delete(0, "end")
        self.speed_spin.insert(0, "0.03")
        self.speed_spin.grid(row=0, column=3, sticky="w", pady=2)

        # Status Label
        self.status_var = tk.StringVar(value="Status: Ready")
        status_label = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            font=("Segoe UI", 10, "italic"), 
            bg="#181825", 
            fg="#fab387",
            pady=6
        )
        status_label.pack(fill="x", padx=20, pady=10)

        # Control Buttons Frame
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=20, pady=5)

        self.start_btn = tk.Button(
            btn_frame, 
            text="▶ Start Auto-Typing", 
            command=self.start_typing_thread,
            font=("Segoe UI", 11, "bold"),
            bg="#a6e3a1", 
            fg="#11111b",
            activebackground="#94e2d5",
            cursor="hand2",
            bd=0,
            pady=8
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.stop_btn = tk.Button(
            btn_frame, 
            text="⏹ Stop", 
            command=self.stop_typing,
            font=("Segoe UI", 11, "bold"),
            bg="#f38ba8", 
            fg="#11111b",
            activebackground="#eba0ac",
            cursor="hand2",
            bd=0,
            pady=8,
            state="disabled"
        )
        self.stop_btn.pack(side="right", fill="x", expand=True)

        # Warning / Safety Tip
        tip_label = tk.Label(
            self.root,
            text="Emergency Stop: माउस कर्सर को स्क्रीन के बिल्कुल कोने (Top-Left) में ले जाएं।",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#6c7086"
        )
        tip_label.pack(side="bottom", pady=10)

    def browse_file(self):
        file_selected = filedialog.askopenfilename(
            title="टेक्स्ट फाइल चुनें",
            filetypes=[("Text Files (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")]
        )
        if file_selected:
            self.file_path_var.set(file_selected)
            try:
                with open(file_selected, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"फाइल पढ़ने में समस्या: {e}")

    def start_typing_thread(self):
        content = self.text_area.get("1.0", tk.END).rstrip("\n")
        if not content.strip():
            messagebox.showwarning("Empty Content", "कृपया पहले कोई फाइल लोड करें या टेक्स्ट बॉक्स में कुछ लिखें!")
            return

        try:
            delay = int(self.delay_spin.get())
            speed = float(self.speed_spin.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Start Delay और Speed सही संख्या में दें!")
            return

        self.is_running = True
        self.stop_requested = False
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        threading.Thread(target=self.run_auto_type, args=(content, delay, speed), daemon=True).start()

    def stop_typing(self):
        self.stop_requested = True
        self.status_var.set("Status: Stopping typing...")

    def run_auto_type(self, content, delay, speed):
        # Countdown
        for i in range(delay, 0, -1):
            if self.stop_requested:
                break
            self.status_var.set(f"⏳ Typing शुरू होगी {i} सेकंड में... (उस जगह क्लिक करें जहाँ टाइप करना है)")
            time.sleep(1)

        if not self.stop_requested:
            self.status_var.set("⚡ Auto-Typing चल रही है...")
            for char in content:
                if self.stop_requested:
                    break
                try:
                    # Hindi / Unicode characters typing via clipboard if needed
                    if ord(char) > 127:
                        pyperclip.copy(char)
                        pyautogui.hotkey('ctrl', 'v')
                    else:
                        pyautogui.write(char)
                    time.sleep(speed)
                except Exception:
                    pass

        if self.stop_requested:
            self.status_var.set("⏹ Typing रोक दी गई!")
        else:
            self.status_var.set("✅ Typing सफलतापूर्वक पूरी हो गई!")

        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperGUI(root)
    root.mainloop()
