import time
import numpy as np
from collections import deque
from typing import Set, Tuple
from src.petri_model import SafePetriNetSystem

def run_bfs_explicit(net: SafePetriNetSystem) -> Set[Tuple[int, ...]]:
    """
    Task 2: Duyet khong gian trang thai tuong minh (Explicit Reachability).
    Su dung thuat toan Breadth-First Search (BFS).
    """
    print(f"\n>>> [Task 2] Starting Explicit Reachability (BFS)...")
    start_time = time.time()
    
    visited_states = set()
    queue = deque()

    # Kiem tra M0
    if len(net.initial_marking) > 0:
        # Chuyen numpy array sang tuple de luu vao set
        # [FIX] Convert sang kieu int thuan cua Python ngay tu dau de in cho dep
        m0_tuple = tuple(map(int, net.initial_marking))
        visited_states.add(m0_tuple)
        queue.append(net.initial_marking)
    else:
        return set()

    # Vong lap duyet
    step_count = 0
    while queue:
        current_m = queue.popleft()
        step_count += 1

        # Thu tat ca cac transition
        for t_idx in range(net.num_transitions):
            
            # 1. Kiem tra dieu kien ban (Enabled)
            if np.all(current_m >= net.pre_matrix[t_idx]):
                
                # 2. Tinh trang thai moi: M' = M - Pre + Post
                next_m = current_m - net.pre_matrix[t_idx] + net.post_matrix[t_idx]
                
                # 1-SAFE CHECK
                # Neu trang thai moi co > 1 token o bat ky dau, bo qua.
                if np.any(next_m > 1):
                    continue
                
                # [FIX] Convert sang int thuan truoc khi luu
                next_m_tuple = tuple(map(int, next_m))

                # 3. Neu la trang thai moi -> Luu lai
                if next_m_tuple not in visited_states:
                    visited_states.add(next_m_tuple)
                    queue.append(next_m)

    duration = time.time() - start_time
    print(f"Done. Processed {step_count} steps.")
    print(f"Total Reachable Markings found: {len(visited_states)}")
    print(f"Execution time: {duration:.4f} seconds")

    # In ra cac trang thai neu so luong it (< 50)
    if len(visited_states) < 50:
        print("\n[List of Reachable Markings (Explicit)]")
        # Sap xep de in theo thu tu dep mat
        sorted_states = sorted(list(visited_states))
        for idx, s in enumerate(sorted_states):
            print(f"M{idx}: {s}")
    
    return visited_states