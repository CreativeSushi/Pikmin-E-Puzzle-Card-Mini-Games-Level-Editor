import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

# --- Config ---
DEFAULT_GAMETYPE = "Plucking Pikmin"
DEFAULT_WIDTH = 11
DEFAULT_HEIGHT = 8
rows, cols = 8, 11
cell_size = 48
TAB_NAMES = ["Level 1", "Level 2", "Level 3"]
GT_OPTIONS = ["Plucking Pikmin", "Marching Pikmin", "Connecting Pikmin"]
current_tab_index = 0

image_folder = "tiles"
image_cache = {}

main_grid_refs = [[None for _ in range(cols)] for _ in range(rows)]
overlay_grid_refs = [[None for _ in range(cols)] for _ in range(rows)]

TILE_PATHS = [f"tiles\\0{c}.png" for c in range(7)]
PIKMIN_PATHS = [f"tiles\\Pik0{c+1}.png" for c in range(6)]

sequences = {
    "SEQ1": bytes.fromhex("50 49 4B 4D 49 4E 50 55 5A 5A 4C 45 30 31"),
    "SEQ2": bytes.fromhex("50 49 4B 4D 49 4E 50 55 5A 5A 4C 45 30 32"),
    "SEQ3": bytes.fromhex("50 49 4B 4D 49 4E 50 55 5A 5A 4C 45 30 33")
}

# --- Functions ---
def show_tab(tab_index: int):
    """Hide all frames, then show the selected one."""
    for frame in frames:
        frame.pack_forget()
    frames[tab_index].pack(fill="both", expand=True)
    current_tab_index = tab_index

def game_control(tab_index: int):
    """Handle updates when game type or coordinates change."""
    gt = gt_vars[tab_index].get()
    try:
        width = int(width_vars[tab_index].get())
        height = int(height_vars[tab_index].get())
    except ValueError:
        return  # Ignore invalid input

    width = max(1, min(width, 11))
    height = max(1, min(height, 9))

    # Placeholder for actual update logic
    print(f"[Tab {tab_index}] Game: {gt}, X={width}, Y={height}")


def load_footer_images(parent: tk.Frame, paths: list[str], row: int):
    """Load a row of images into a footer frame."""
    parent.images = getattr(parent, "images", [])
    for c, path in enumerate(paths):
        img = Image.open(path).resize((36, 36), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        parent.images.append(photo)
        tk.Label(parent, image=photo, bg="#ccc").grid(row=row, column=c, padx=1, pady=1)

def load_bin_file():
    """Prompt user to select a BIN file, search for sequence, load PNGs."""
    file_path = filedialog.askopenfilename(
        title="Select BIN File",
        filetypes=[("BIN files", "*.bin"), ("All files", "*.*")]
    )
    if not file_path:
        return
    
    occurrences = []
    
    with open(file_path, "rb") as f:
        data = f.read()
        
    for seq_name, seq_bytes in sequences.items():
        start = 0
        while True:
            idx = data.find(seq_bytes, start)
            if idx == -1:
                break
            occurrences.append((idx, seq_name, seq_bytes))
            start = idx + 1
        
    #Change occurrences[:1] to occurrences[:3] when ready to develop more levels per card
    for pos, seq_name, seq_bytes in occurrences[:1]:
        print(seq_name)
        if seq_name == "SEQ1":
            loadgametype_1(data[pos+21:pos+197])
                
def loadgametype_1(block):
    #print(pos)
    #start = pos + 14
    #game1 = data[start:start + 183]
    

    if len(block) < ((rows * cols) *2):
        print("Not enough image bytes in the block!")
        return

    # Split into two sets
    bottom_bytes = block[0:rows*cols]
    overlay_bytes = block[rows*cols:(rows*cols)*2]

    # Draw main grid
    for r in range(rows):
        for c in range(cols):
            byte_val = bottom_bytes[r*cols + c]
            filename = f"{byte_val:02X}.png"
            img = get_image(filename)
            if img:
                if main_grid_refs[r][c]:
                    img_frame.delete(main_grid_refs[r][c])
                main_grid_refs[r][c] = img_frame.create_image(
                    c*cell_size, r*cell_size,
                    anchor="nw",
                    image=img
                )

    # Draw overlay grid (offset upward by 9 pixels)
    for r in range(rows):
        for c in range(cols):
            byte_val = overlay_bytes[r*cols + c]
            filename = "pik"+f"{byte_val:02X}.png"
            img = get_image(filename)
            if img:
                if overlay_grid_refs[r][c]:
                    img_frame.delete(overlay_grid_refs[r][c])
                overlay_grid_refs[r][c] = img_frame.create_image(
                    c*cell_size, r*cell_size - 14,  # shifted up
                    anchor="nw",
                    image=img
                )    
    
def game2(position,byteStart):
    print("test game 2")
    
def game3(position,byteStart):
    print("test game 3")
    
def get_image(filename):
    """Load and cache an image."""
    full_path = os.path.join(image_folder, filename)
    if not os.path.exists(full_path):
        print(f"Image not found: {full_path}")
        return None
    if filename not in image_cache:
        img = Image.open(full_path).resize((cell_size, cell_size), Image.Resampling.LANCZOS)
        image_cache[filename] = ImageTk.PhotoImage(img)
    return image_cache[filename]


# --- Main UI ---
root = tk.Tk()
root.title("Pikmin E+ Level Editor")
root.geometry("700x520")

# --- Top button bar ---
top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x")

tk.Button(
    top_frame, text="Import card data", command=load_bin_file, bg="#d9ead3"
).pack(side="left", padx=5, pady=5)

for i, name in enumerate(TAB_NAMES):
    tk.Button(top_frame, text=name, command=lambda i=i: show_tab(i)).pack(
        side="left", padx=5, pady=5
    )

# --- Content frames ---
frames, images = [], [None] * len(TAB_NAMES)
gt_vars, width_vars, height_vars = [], [], []

for tab_index in range(len(TAB_NAMES)):
    frame = tk.Frame(root, bg="white")

    # Left control panel
    control_panel = tk.Frame(frame, width=150, bg="#eeeeee")
    control_panel.pack(side="left", fill="y", padx=5, pady=5)

    # Dropdown
    tk.Label(control_panel, text="Game Type:").pack(pady=(10, 0))
    gt_var = tk.StringVar(value=DEFAULT_GAMETYPE)
    gt_vars.append(gt_var)
    gt_select = ttk.Combobox(
        control_panel, textvariable=gt_var, values=GT_OPTIONS, state="readonly"
    )
    gt_select.pack(pady=5, fill="x")
    gt_select.bind("<<ComboboxSelected>>", lambda e, i=tab_index: game_control(i))

    # Width/Height
    tk.Label(control_panel, text="Camera Coordinates").pack(pady=(2, 0))
    size_frame = tk.Frame(control_panel, bg="#eeeeee")
    size_frame.pack(pady=10)

    width_var = tk.StringVar(value=str(DEFAULT_WIDTH))
    width_vars.append(width_var)
    tk.Label(size_frame, text="X").pack(side="left")
    width_spin = tk.Spinbox(size_frame, from_=1, to=11, textvariable=width_var, width=3)
    width_spin.pack(side="left", padx=2)
    width_spin.config(command=lambda i=tab_index: game_control(i))
    width_var.trace_add("write", lambda *_, i=tab_index: game_control(i))

    height_var = tk.StringVar(value=str(DEFAULT_HEIGHT))
    height_vars.append(height_var)
    tk.Label(size_frame, text="Y").pack(side="left")
    height_spin = tk.Spinbox(size_frame, from_=1, to=9, textvariable=height_var, width=3)
    height_spin.pack(side="left", padx=2)
    height_spin.config(command=lambda i=tab_index: game_control(i))
    height_var.trace_add("write", lambda *_, i=tab_index: game_control(i))

    # Main image area
    #img_frame = tk.Frame(frame, bg="white")
    #img_frame.pack(side="left", fill="both", expand=True)
    
    img_frame = tk.Canvas(frame, bg="white", highlightthickness=0)
    img_frame.pack(side="left", fill="both", expand=True)

    # Footer
    footer_frame = tk.Frame(img_frame, bg="#ddd", height=100)
    footer_frame.pack(side="bottom", fill="x")
    load_footer_images(footer_frame, TILE_PATHS, row=0)
    load_footer_images(footer_frame, PIKMIN_PATHS, row=1)

    frames.append(frame)

# Show first tab
show_tab(0)
root.mainloop()
