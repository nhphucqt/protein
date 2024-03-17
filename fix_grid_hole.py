import numpy as np

def fix_holes(grids):
    def is_hole(grid, i, j):
        if grid[i,j] != -np.inf:
            return False
        for di in [-1, 1]:
            for dj in [-1, 1]:
                if grid[i+di, j+dj] == -np.inf:
                    return False
        return True
    
    def fix_hole(grid):
        for i in range(grid.shape[0])[1:-1]:
            for j in range(grid.shape[1])[1:-1]:
                if is_hole(grid, i, j):
                    grid[i, j] = (grid[i-1, j] + grid[i+1, j] + grid[i, j-1] + grid[i, j+1]) / 4

    for i in range(grids.shape[0]):
        for j in range(grids.shape[1]):
            fix_hole(grids[i,j])