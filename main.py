\import tkinter as tk
import numpy as np

# Define grid dimensions
width, height = 600, 400
cell_size = 10
n_cells_x, n_cells_y = width // cell_size, height // cell_size

# Initialize Tkinter
root = tk.Tk()
root.title("Conway's Game of Life")
canvas = tk.Canvas(root, width=width, height=height, bg='black')
canvas.pack()

# Create initial grid state (randomly)
grid = np.random.randint(2, size=(n_cells_x, n_cells_y))

def update_grid(grid):
  new_grid = grid.copy()
  # ... (same logic as Pygame example)
  return new_grid

def draw_grid(grid):
  canvas.delete('all')
  for i in range(n_cells_x):
    for j in range(n_cells_y):
      if grid[i, j]:
        canvas.create_rectangle(i*cell_size, j*cell_size, 
                               (i+1)*cell_size, (j+1)*cell_size, 
                               fill='white', outline='white')

# Update and draw grid repeatedly
def game_loop():
  global grid
  grid = update_grid(grid)
  draw_grid(grid)
  root.after(100, game_loop) # Adjust delay for speed

game_loop()
root.mainloop()
