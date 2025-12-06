import sys
import random
import datetime

def validate_args():
    """
    Validates command line arguments.
    Returns: rows, cols, hidden_count, cheat_mode
    """
    args = sys.argv
    
    # --- HELP MENU (Added for Assignment Requirement) ---
    if len(args) > 1 and args[1].lower() == "help":
        print("\n--- GunDown Help ---")
        print("Goal: Find hidden objects on the grid.")
        print("Rules: Guess locations based on the grid numbers.")
        print("Usage: python gundown.py [GridSize] [HiddenCount]")
        print("Example: python gundown.py 3x3 3")
        sys.exit()
    # ----------------------------------------------------

    # Check minimum arguments
    if len(args) < 3:
        print("Error: Missing arguments.")
        print("Usage: python gundown.py [Grid] [Hidden] (show)")
        print("Try 'python gundown.py help' for more info.")
        sys.exit()

    # Parse Grid Size (e.g., "3x3")
    grid_str = args[1].lower()
    if 'x' not in grid_str:
        print("Error: Grid format must be like 3x3.")
        sys.exit()
    
    try:
        r_str, c_str = grid_str.split('x')
        rows = int(r_str)
        cols = int(c_str)
        hidden_count = int(args[2])
    except ValueError:
        print("Error: Dimensions and hidden count must be integers.")
        sys.exit()

    # Validate Grid Rules (Min 3x3, Max 5x5) [cite: 70]
    if not (3 <= rows <= 5 and 3 <= cols <= 5):
        print("Error: Grid size must be between 3x3 and 5x5.")
        sys.exit()

    # Validate Hidden Count Rules (Min 2, Max half of cells) [cite: 71]
    max_hidden = (rows * cols) // 2
    if hidden_count < 2 or hidden_count > max_hidden:
        print(f"Error: For a {rows}x{cols} grid, hidden objects must be between 2 and {max_hidden}.")
        sys.exit()

    # Check for Cheat Mode [cite: 171]
    cheat_mode = False
    if len(args) > 3 and args[3].lower() == "show":
        cheat_mode = True

    return rows, cols, hidden_count, cheat_mode

def save_result(hidden_locs, found_locs, score_pct, cheat_mode):
    """
    Saves game details to a text file with a random ID name.
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # Generate filename: YYYYMMDD HHMM RRRR.txt [cite: 160]
    file_ts = now.strftime("%Y%m%d %H%M")
    rand_code = random.randint(1000, 9999)
    filename = f"{file_ts} {rand_code}"
    
    if cheat_mode:
        filename += "C"  # [cite: 174]
    filename += ".txt"

    # Write content
    try:
        with open(filename, "w") as f:
            f.write(f"Date: {date_str}\n")
            f.write(f"Time: {time_str}\n")
            
            # Convert lists to comma-separated strings
            hidden_str = ",".join(map(str, sorted(hidden_locs)))
            found_str = ",".join(map(str, sorted(found_locs)))
            
            f.write(f"Hidden locations: {hidden_str}\n")
            f.write(f"Found locations: {found_str}\n")
            
            found_count = len(found_locs)
            total_hidden = len(hidden_locs)
            f.write(f"{found_count} out of {total_hidden} found ({score_pct}%)\n")
            
        print(f"Game saved to {filename}")
    except IOError:
        print("Error writing to file.")

def play_game():
    rows, cols, hidden_count, cheat_mode = validate_args()
    total_cells = rows * cols
    
    # Generate grid numbers [1, 2, 3...]
    grid_nums = list(range(1, total_cells + 1))
    
    # Select hidden locations
    hidden_locs = random.sample(grid_nums, hidden_count)
    
    # --- Display Initial Grid ---
    print(f"\nGrid Size: {rows}x{cols} | Hidden Objects: {hidden_count}")
    for r in range(rows):
        row_display = []
        for c in range(cols):
            num = grid_nums[r * cols + c]
            # Cheat mode: Show empty space if hidden [cite: 173]
            if cheat_mode and num in hidden_locs:
                row_display.append(" ") 
            else:
                row_display.append(str(num))
        print("\t".join(row_display))
    print("-" * 20)

    # --- User Guessing Loop ---
    guesses = []
    found_locs = []
    
    for i in range(hidden_count):
        while True:
            try:
                # Prompt user [cite: 108]
                g = int(input(f"Guess hidden object location {i+1} of {hidden_count}: "))
                if 1 <= g <= total_cells:
                    guesses.append(g)
                    if g in hidden_locs:
                        found_locs.append(g)
                    break
                else:
                    print(f"Please enter a number between 1 and {total_cells}.")
            except ValueError:
                print("Invalid input. Enter a number.")

    # --- Calculate Results ---
    final_grid_display = []
    for num in grid_nums:
        if num in found_locs:
            final_grid_display.append("X") # Hit [cite: 120]
        elif num in hidden_locs:
            final_grid_display.append("H") # Missed Hidden [cite: 117]
        else:
            final_grid_display.append(str(num)) # Empty

    # --- Display Final Grid ---
    print("\n--- Game Over ---")
    for r in range(rows):
        start = r * cols
        end = start + cols
        print("\t".join(final_grid_display[start:end]))
        
    # --- Display Stats ---
    found_count = len(found_locs)
    percentage = int((found_count / hidden_count) * 100)
    
    print("\nFinal Result")
    print(f"Hidden locations: {','.join(map(str, sorted(hidden_locs)))}")
    print(f"Found locations : {','.join(map(str, sorted(found_locs)))}")
    print(f"{found_count} out of {hidden_count} found ({percentage}%)")

    # --- Save to File ---
    save_result(hidden_locs, found_locs, percentage, cheat_mode)

if __name__ == "__main__":
    play_game()