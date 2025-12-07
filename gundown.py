import tkinter as tk
from tkinter import messagebox
import random
import datetime
import os

class GunDownGame:
    def __init__(self, root):
        self.root = root
        self.root.title("GunDown Game")
        self.root.geometry("500x600")
        
        # Game State
        self.rows = 0
        self.cols = 0
        self.hidden_count = 0
        self.hidden_locs = []
        self.found_locs = []
        self.guesses_made = []
        self.buttons = {} # Map grid numbers to button widgets
        self.cheat_mode = False

        # Create the UI Screens
        self.setup_frame = tk.Frame(root, padx=20, pady=20)
        self.game_frame = tk.Frame(root, padx=20, pady=20)
        
        # Initialize the Setup Screen
        self.build_setup_screen()
        self.setup_frame.pack()

    def build_setup_screen(self):
        """Builds the initial input form."""
        tk.Label(self.setup_frame, text="GunDown Setup", font=("Arial", 20, "bold")).pack(pady=10)

        # Grid Dimensions
        tk.Label(self.setup_frame, text="Grid Size (e.g., 3x3, 5x5):").pack()
        self.entry_grid = tk.Entry(self.setup_frame)
        self.entry_grid.insert(0, "3x3")
        self.entry_grid.pack(pady=5)

        # Hidden Count
        tk.Label(self.setup_frame, text="Hidden Objects Count:").pack()
        self.entry_hidden = tk.Entry(self.setup_frame)
        self.entry_hidden.insert(0, "3")
        self.entry_hidden.pack(pady=5)

        # Cheat Mode Checkbox
        self.var_cheat = tk.BooleanVar()
        tk.Checkbutton(self.setup_frame, text="Cheat Mode (Show Hidden)", variable=self.var_cheat).pack(pady=10)

        # Start Button
        tk.Button(self.setup_frame, text="Start Game", command=self.validate_and_start, 
                  bg="green", fg="white", font=("Arial", 12)).pack(pady=15)

    def validate_and_start(self):
        """Validates inputs similar to the original validate_args function."""
        grid_str = self.entry_grid.get().lower()
        
        try:
            if 'x' not in grid_str:
                raise ValueError("Format must be RxC (e.g. 3x3)")
            
            r_str, c_str = grid_str.split('x')
            self.rows = int(r_str)
            self.cols = int(c_str)
            self.hidden_count = int(self.entry_hidden.get())
            self.cheat_mode = self.var_cheat.get()

            # Logic Validation (Min 3x3, Max 5x5)
            if not (3 <= self.rows <= 5 and 3 <= self.cols <= 5):
                messagebox.showerror("Error", "Grid size must be between 3x3 and 5x5.")
                return

            # Hidden Count Validation
            max_hidden = (self.rows * self.cols) // 2
            if self.hidden_count < 2 or self.hidden_count > max_hidden:
                messagebox.showerror("Error", f"Hidden objects must be between 2 and {max_hidden}.")
                return

            # If valid, switch screens
            self.setup_game_logic()
            self.setup_frame.pack_forget()
            self.build_game_screen()
            self.game_frame.pack()

        except ValueError:
            messagebox.showerror("Error", "Invalid Input. Please check your numbers.")

    def setup_game_logic(self):
        """Generates random locations."""
        total_cells = self.rows * self.cols
        grid_nums = list(range(1, total_cells + 1))
        self.hidden_locs = random.sample(grid_nums, self.hidden_count)
        self.guesses_made = []
        self.found_locs = []

    def build_game_screen(self):
        """Builds the grid of buttons."""
        # Clear previous game widgets if any
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # Status Label
        self.lbl_status = tk.Label(self.game_frame, 
                                   text=f"Find {self.hidden_count} objects! Click to guess.", 
                                   font=("Arial", 12))
        self.lbl_status.grid(row=0, column=0, columnspan=self.cols, pady=10)

        # Create Grid Buttons
        self.buttons = {}
        counter = 1
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.game_frame, text=str(counter), 
                                width=6, height=3, font=("Arial", 10, "bold"),
                                command=lambda n=counter: self.handle_guess(n))
                
                # Cheat Mode Visualization (Optional hint)
                if self.cheat_mode and counter in self.hidden_locs:
                    btn.config(bg="#e0e0e0") # Slightly darker grey for cheat

                btn.grid(row=r+1, column=c, padx=2, pady=2)
                self.buttons[counter] = btn
                counter += 1

    def handle_guess(self, num):
        """Handles the logic when a button is clicked."""
        if num in self.guesses_made:
            return # Already guessed

        self.guesses_made.append(num)
        btn = self.buttons[num]

        # Check if hit
        if num in self.hidden_locs:
            self.found_locs.append(num)
            btn.config(bg="#90EE90", text="X") # Light Green for Found
        else:
            btn.config(bg="#FFB6C1", state="disabled") # Light Red for Miss

        # Update Status
        remaining = self.hidden_count - len(self.guesses_made)
        
        # In this UI version, we give them exactly 'hidden_count' guesses
        # to match the loop: "for i in range(hidden_count)"
        
        if len(self.guesses_made) >= self.hidden_count:
            self.finish_game()
        else:
            guesses_left = self.hidden_count - len(self.guesses_made)
            self.lbl_status.config(text=f"Guesses left: {guesses_left}")

    def finish_game(self):
        """Calculates score, shows results, saves file."""
        # Reveal all cells
        for num, btn in self.buttons.items():
            btn.config(state="disabled") # Lock grid
            if num in self.hidden_locs and num not in self.found_locs:
                btn.config(bg="#FFD700", text="H") # Gold for Missed Hidden

        # Calc Stats
        found_count = len(self.found_locs)
        percentage = int((found_count / self.hidden_count) * 100)
        
        self.lbl_status.config(text=f"Game Over! Score: {percentage}%")
        
        # Save Result
        filename = self.save_result_to_file(percentage)
        
        # Show Message
        msg = f"You found {found_count} out of {self.hidden_count}.\nSaved to {filename}"
        messagebox.showinfo("Game Over", msg)
        
        # Play Again Button
        tk.Button(self.game_frame, text="Play Again", command=self.reset_game, bg="skyblue").grid(row=self.rows+2, column=0, columnspan=self.cols, pady=20)

    def save_result_to_file(self, score_pct):
        """Reusing your specific file saving format."""
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        file_ts = now.strftime("%Y%m%d %H%M")
        rand_code = random.randint(1000, 9999)
        
        filename = f"{file_ts} {rand_code}"
        if self.cheat_mode:
            filename += "C"
        filename += ".txt"

        try:
            with open(filename, "w") as f:
                f.write(f"Date: {date_str}\n")
                f.write(f"Time: {time_str}\n")
                hidden_str = ",".join(map(str, sorted(self.hidden_locs)))
                found_str = ",".join(map(str, sorted(self.found_locs)))
                f.write(f"Hidden locations: {hidden_str}\n")
                f.write(f"Found locations: {found_str}\n")
                f.write(f"{len(self.found_locs)} out of {len(self.hidden_locs)} found ({score_pct}%)\n")
            return filename
        except IOError:
            return "Error saving file"

    def reset_game(self):
        """Resets to setup screen."""
        self.game_frame.pack_forget()
        self.setup_frame.pack()

# --- Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GunDownGame(root)
    root.mainloop()