import numpy as np
import sys
import os
import json

from config import *

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
    
    def offsettuple(self, x, y, offset):
        return max(0, offset), min(x, y + offset)
                
    def calculate_score(self, height, intersect, metric):
        score = 0

        # for i in self.offsetrange(target.shape[0], query.shape[0], offset[0]):
        #     for j in self.offsetrange(target.shape[1], query.shape[1], offset[1]):
        #         score += metric(height - target[i, j] - query[i - offset[0], j - offset[1]])

        arr = height - intersect
        # 1 / (x) ** 2
        score = np.sum(metric(arr))

        # print("score: ", score, "score_opt: ", score_opt, "diff: ", score - score_opt)

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

            # height -= np.min([height - target[i, j] - query[i - offset[0], j - offset[1]] 
            #                 for i in self.offsetrange(target.shape[0], query.shape[0], offset[0]) 
            #                 for j in self.offsetrange(target.shape[1], query.shape[1], offset[1])
            #                 if target[i, j] != -np.inf and query[i - offset[0], j - offset[1]] != -np.inf], initial = np.inf)
            
            tar_r = self.offsettuple(target.shape[0], query.shape[0], offset[0])
            tar_c = self.offsettuple(target.shape[1], query.shape[1], offset[1])
            intersect = target[tar_r[0]:tar_r[1], tar_c[0]:tar_c[1]] + query[tar_r[0]-offset[0]:tar_r[1]-offset[0], tar_c[0]-offset[1]:tar_c[1]-offset[1]]
            height -= np.min(height - intersect)
            
            if np.isnan(height) or np.isinf(height):
                return best_score, best_height, best_offset
            
            score = self.calculate_score(height, intersect, lambda x: 1 / (1 + x) ** 2)
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

        # for target_fibo_id, target_rot_id, query_fibo_id, query_rot_id in np.ndindex((2, 2, 2, 2)):
        for target_fibo_id, target_rot_id, query_fibo_id, query_rot_id in np.ndindex((self.target.shape[0], self.target.shape[1], self.query.shape[0], self.query.shape[1])):
            target = self.target[target_fibo_id, target_rot_id]
            dtarget = self.dtarget[target_fibo_id, target_rot_id]
            query = self.query[query_fibo_id, query_rot_id]
            # print("t_f_id: ", target_fibo_id, "t_r_id: ", target_rot_id, "q_f_id: ", query_fibo_id, "q_r_id: ", query_rot_id)
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


def query_target_matching(query, target_id, step = 1):
    target = np.load(os.path.join(STATES_PATH_PREFIX, MESH_CONF["target"]["state"], f"{target_id}.npy"))

    target = target[0:-1:step, 0:-1:step]

    # print(target.shape)

    solver = GridSolver(target, query)
    result = solver.solve(num_iterations=1, hor_count=2, vert_count=2, epsilon=2)

    print(f"Target: {target_id}, score: {result.score}, height: {result.height}, offset: {result.query_offset}, target_fibo_id: {result.target_fibo_id}, target_rot_id: {result.target_rot_id}, query_fibo_id: {result.query_fibo_id}, query_rot_id: {result.query_rot_id}")

    return (result.score, result.height), result.query_offset, (result.target_fibo_id, result.target_rot_id, result.query_fibo_id, result.query_rot_id)

def query_solver(query_id, step = 1):
    results_sch = []
    results_off = []
    results_rot = []
    query = np.load(os.path.join(STATES_PATH_PREFIX, MESH_CONF["query"]["state"], f"{query_id}.npy"))

    query = np.flip(query[0:-1:step, 0:-1:step], axis=3)

    # print(query.shape)

    # for target_id in range(1):
    for target_id in range(MESH_CONF["target"]["num"]):
        sch, off, rot = query_target_matching(query, target_id, step)
        results_sch.append(sch)
        results_off.append(off)
        results_rot.append(rot)
    return np.array(results_sch), np.array(results_off), np.array(results_rot)

def solver(start_id = 0, end_id = -1, step = 1):
    RESULT_PATH_PREFIX = "/kaggle/working/results"
    if not os.path.exists(RESULT_PATH_PREFIX):
        os.makedirs(RESULT_PATH_PREFIX)

    if end_id == -1:
        end_id = MESH_CONF["query"]["num"]
    for i in range(start_id, end_id):
        print(f"Query {i} (from {start_id} to {end_id})...")
        results_sch, results_off, results_rot = query_solver(i, step)
        with open(os.path.join(RESULT_PATH_PREFIX, f"{i}.npy"), "wb") as fo:
            np.save(fo, results_sch)
            np.save(fo, results_off)
            np.save(fo, results_rot)


# target = np.load("targets_states/0.npy")
# query = np.load("queries_states/0.npy")

# solver = GridSolver(target, query)
# result = solver.solve(num_iterations=1, hor_count=2, vert_count=2, epsilon=2)
# print(f"score: {result.score}, height: {result.height}, offset: {result.query_offset}, target_fibo_id: {result.target_fibo_id}, target_rot_id: {result.target_rot_id}, query_fibo_id: {result.query_fibo_id}, query_rot_id: {result.query_rot_id}")
            
if __name__ == "__main__":
    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])
    print(f"Start id: {start_id}, End id: {end_id}")
    # solver(RANGE_QUERIES[range_id][0], RANGE_QUERIES[range_id][1], step=2)
    solver(start_id, end_id, step=2)

    # query_solver(0, step=2)
    # with open(os.path.join(os.path.join(STATES_PATH_PREFIX, MESH_CONF["query"]["result"]), f"0.npy"), "rb") as fo:
    #     results_sch = np.load(fo)
    #     results_off = np.load(fo)
    #     results_rot = np.load(fo)
    # print(results_sch)
    # print(results_off)
    # print(results_rot)