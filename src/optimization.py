import time
from src.common_utils import sanitize_variable_name
from pyeda.inter import *
from src.petri_model import SafePetriNetSystem
import numpy as np
from typing import List, Optional, Tuple

def find_optimal_marking(
    net: SafePetriNetSystem, 
    reachable_bdd: BinaryDecisionDiagram, 
    weights: np.ndarray
) -> Tuple[Optional[List[int]], Optional[int]]:
    start_time = time.time()
    """
    Task 5: Toi uu hoa tren tap trang thai dat duoc.
    Muc tieu: Tim trang thai M sao cho ham muc tieu f(M) = c^T * M la lon nhat.
    
    Ky thuat:
    - Duyet qua cac khoi nghiem (Cube) cua BDD.
    - Xu ly bien "Don't Care": Neu bien khong bi rang buoc trong BDD, 
      ta chon gia tri (0 hoac 1) dua tren trong so de toi da hoa tong.
    """
    print(f"\n>>> [Task 5] OPTIMIZATION (MAXIMIZE OBJECTIVE)")
    
    # Kiem tra tap rong
    if reachable_bdd.is_zero():
        print("[ERROR] Reachable set is empty. Cannot optimize.")
        return None, None

    # Tai tao bien BDD de tra cuu
    bdd_vars = []
    for pid in net.places:
        vname = sanitize_variable_name(pid)
        bdd_vars.append(bddvar(vname))

    max_val = -float('inf')
    best_marking = None

    # Duyet qua tat ca cac khoi nghiem thoa man (Satisfying Cubes)
    count_cubes = 0
    for point in reachable_bdd.satisfy_all():
        count_cubes += 1
        current_marking = []
        current_val = 0
        
        for i, var in enumerate(bdd_vars):
            # Lay gia tri cua bien trong khoi nghiem hien tai
            val = point.get(var)
            
            if val is not None:
                # Truong hop 1: Bien Bi Rang Buoc (Fixed)
                # Bat buoc phai theo gia tri cua nghiem (0 hoac 1)
                bit = int(val)
            else:
                # Truong hop 2: Bien Tu Do (Don't Care)
                # Bien nay nhan gia tri nao cung thuoc tap Reachable.
                # Chien thuat Greedy: Chon gia tri co loi nhat cho ham muc tieu.
                # - Neu trong so duong -> chon 1 (de cong them vao tong)
                # - Neu trong so am/bang 0 -> chon 0 (de tranh bi tru)
                if i < len(weights) and weights[i] > 0:
                    bit = 1
                else:
                    bit = 0
            
            current_marking.append(bit)
            
            # Tinh tong tich vo huong: val += bit * weight
            if i < len(weights):
                current_val += bit * weights[i]
        
        # Cap nhat gia tri tot nhat
        if current_val > max_val:
            max_val = current_val
            best_marking = current_marking

    time_taken = time.time() - start_time
    print(f"Scanned {count_cubes} solution cubes in BDD.")
    print(f"\n[OPTIMIZATION RESULT]")
    print(f"Max Objective Value: {max_val}")
    print(f"Optimal Marking: {best_marking}")
    print(f"Execution time for optimization: {time_taken:.4f}")
    
    return best_marking, int(max_val)