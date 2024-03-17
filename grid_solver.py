import numpy as np
import sys

class GridSolverResult:
    def __init__(self, score, height, query_offset, target_fibo_id, target_rot_id, query_fibo_id, query_rot_id):
        self.score = score
        self.height = height
        self.query_offset = query_offset
        self.target_fibo_id = target_fibo_id
        self.target_rot_id = target_rot_id
        self.query_fibo_id = query_fibo_id
        self.query_rot_id = query_rot_id

class GridSolver:
    def __init__(self, target, query, dtarget=None): # dtarget is the gradient/derivative of the target
        self.target = target
        self.query = query
        if dtarget is None:
            self.dtarget = np.zeros((target.shape[0], target.shape[1], 2, target.shape[2], target.shape[3]))

            for i, j in np.ndindex(target.shape[:2]):
                self.dtarget[i, j] = np.gradient(target[i, j])
        else:
            self.dtarget = dtarget

    def fix_holes(self, grids):
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

    def offsetrange(self, x, y, offset):
        return range(max(0, offset), min(x, y + offset))
                
    def calculate_score(self, height, target, query, offset, metric):
        score = 0
        
        for i in self.offsetrange(target.shape[0], query.shape[0], offset[0]):
            for j in self.offsetrange(target.shape[1], query.shape[1], offset[1]):
                score += metric(height - target[i, j] - query[i - offset[0], j - offset[1]])

        return score
    
    def calculate(self, target, query, dtarget, initial_offset, num_iterations, epsilon=1e-6):
        offset = initial_offset
        height = np.max(target) + np.max(query) + 1

        best_score = -np.inf
        best_height = np.inf
        best_offset = (-np.inf, -np.inf)

        for iteration in range(num_iterations):
            if offset[0] < 0 or offset[1] < 0 or offset[0] >= target.shape[0] or offset[1] >= target.shape[1]:
                return best_score, best_height, best_offset
            
            height -= np.min([height - target[i, j] - query[i - offset[0], j - offset[1]] 
                            for i in self.offsetrange(target.shape[0], query.shape[0], offset[0]) 
                            for j in self.offsetrange(target.shape[1], query.shape[1], offset[1])
                            if target[i, j] != -np.inf and query[i - offset[0], j - offset[1]] != -np.inf], initial = np.inf)
            
            if np.isnan(height) or np.isinf(height):
                return best_score, best_height, best_offset
            
            score = self.calculate_score(height, target, query, offset, lambda x: 1 / (1 + x) ** 2)
            if score > best_score:
                best_score  = score
                best_height = height
                best_offset = offset

            if iteration == num_iterations - 1:
                break

            dx = np.mean([dtarget[0, i, j]
                          for i in self.offsetrange(target.shape[0], query.shape[0], offset[0])
                          for j in self.offsetrange(target.shape[1], query.shape[1], offset[1])
                          if not np.isnan(dtarget[0, i, j]) and not np.isinf(dtarget[0, i, j])
                          and height - target[i, j] - query[i - offset[0], j - offset[1]] < epsilon])
            dy = np.mean([dtarget[1, i, j]
                          for i in self.offsetrange(target.shape[0], query.shape[0], offset[0])
                          for j in self.offsetrange(target.shape[1], query.shape[1], offset[1])
                          if not np.isnan(dtarget[1, i, j]) and not np.isinf(dtarget[1, i, j])
                          and height - target[i, j] - query[i - offset[0], j - offset[1]] < epsilon])
            
            if np.isnan(dx) or np.isinf(dx):
                dx = 0
            if np.isnan(dy) or np.isinf(dy):
                dy = 0
            
            offset = (offset[0] + int(round(dx)), offset[1] + int(round(dy)))
            
        return best_score, best_height, best_offset

    def solve(self, num_iterations=10, hor_count = 5, vert_count = 5, epsilon=1e-6):
        assert hor_count <= self.target.shape[0] and vert_count <= self.target.shape[1]
        
        self.fix_holes(self.target)
        self.fix_holes(self.query)

        best_score = -np.inf
        best_height = np.inf
        best_offset = (-np.inf, -np.inf)
        best_target_fibo_id = -1
        best_target_rot_id = -1
        best_query_fibo_id = -1
        best_query_rot_id = -1

        for target_fibo_id, target_rot_id, query_fibo_id, query_rot_id in np.ndindex((self.target.shape[0], self.target.shape[1], self.query.shape[0], self.query.shape[1])):
            target = self.target[target_fibo_id, target_rot_id]
            dtarget = self.dtarget[target_fibo_id, target_rot_id]
            query = self.query[query_fibo_id, query_rot_id]
            print("t_f_id: ", target_fibo_id, "t_r_id: ", target_rot_id, "q_f_id: ", query_fibo_id, "q_r_id: ", query_rot_id)
            for i in np.linspace(0, query.shape[0], hor_count + 1, dtype=int)[:-1]:
                for j in np.linspace(0, query.shape[1], vert_count + 1, dtype=int)[:-1]:
                    score, height, offset = self.calculate(target, query, dtarget, (i, j), num_iterations, epsilon)
                    if score > best_score:
                        best_score          = score
                        best_height         = height
                        best_offset         = offset
                        best_target_fibo_id = target_fibo_id
                        best_target_rot_id  = target_rot_id
                        best_query_fibo_id  = query_fibo_id
                        best_query_rot_id   = query_rot_id

        return GridSolverResult(best_score, best_height, best_offset, best_target_fibo_id, best_target_rot_id, best_query_fibo_id, best_query_rot_id)

target = np.load("targets_states/0.npy")
query = np.load("queries_states/0.npy")

solver = GridSolver(target, query)
result = solver.solve(num_iterations=1, hor_count=2, vert_count=2, epsilon=2)
print(f"score: {result.score}, height: {result.height}, offset: {result.query_offset}, target_fibo_id: {result.target_fibo_id}, target_rot_id: {result.target_rot_id}, query_fibo_id: {result.query_fibo_id}, query_rot_id: {result.query_rot_id}")