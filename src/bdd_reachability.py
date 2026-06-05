from src.common_utils import sanitize_variable_name
import pyeda.inter as pye 
from src.petri_model import SafePetriNetSystem
import numpy as np
import functools
import operator
from typing import Tuple

# [FIX] Khoi tao bddone/bddzero an toan tuyet doi
# Thu tu uu tien: 
# 1. Lay tu pye.bddone (Chuan)
# 2. Import tu module con (Backup)
# 3. Tao tu bieu thuc so hoc su dung expr2bdd (Fallback cuoi cung)
try:
    bddone = pye.bddone
    bddzero = pye.bddzero
except AttributeError:
    try:
        from pyeda.boolalg.bdd import bddone, bddzero
    except ImportError:
        # Fallback: Su dung expr2bdd de chuyen doi
        bddone = pye.expr2bdd(pye.expr(1))
        bddzero = pye.expr2bdd(pye.expr(0))

# Gan ham bddvar
bddvar = pye.bddvar

def run_bdd_reachability(net: SafePetriNetSystem) -> Tuple[pye.BinaryDecisionDiagram, int]:
    """
    Task 3: Tinh khong gian trang thai bang phuong phap Ky hieu (Symbolic BDD).
    Su dung BDD de nen va tinh toan tren tap trang thai khong lo.
    """
    print(f"\n>>> [Task 3] Starting Symbolic Reachability (BDD)...")
    
    num_places = len(net.places)
    
    # 1. KHOI TAO BIEN BDD
    X = [] # Bien trang thai hien tai
    Y = [] # Bien trang thai ke tiep
    rename_y_to_x = {} # Map doi ten Y -> X
    
    # Danh sach bien X truy cap theo index
    x_vars_indexed = []

    for pid in net.places:
        safe_name = sanitize_variable_name(pid)
        
        # [FIX] Dung bddvar da duoc gan o tren
        x_var = bddvar(safe_name)           # Vi du: p1
        y_var = bddvar(f"{safe_name}_next") # Vi du: p1_next
        
        X.append(x_var)
        Y.append(y_var)
        x_vars_indexed.append(x_var)
        rename_y_to_x[y_var] = x_var

    # 2. MA HOA TRANG THAI BAN DAU (M0)
    m0_exprs = []
    for i in range(num_places):
        if net.initial_marking[i] == 1:
            m0_exprs.append(x_vars_indexed[i])
        else:
            m0_exprs.append(~x_vars_indexed[i])
            
    if m0_exprs:
        R = functools.reduce(operator.and_, m0_exprs)
    else:
        # [FIX] Dung hang so da tao an toan
        R = bddone

    # 3. XAY DUNG HAM CHUYEN DOI (TRANSITION RELATION - TR)
    tr_components = []
    
    # Gioi han vong lap theo kich thuoc thuc te cua ma tran
    actual_trans_count = min(net.num_transitions, net.pre_matrix.shape[0])

    for t in range(actual_trans_count):
        # A. Dieu kien kich hoat (Enable Condition)
        input_indices = np.where(net.pre_matrix[t] == 1)[0]
        
        # SAFETY CHECK: Output place phai rong
        output_indices = np.where(net.post_matrix[t] == 1)[0]
        pure_outputs = [i for i in output_indices if i not in input_indices]

        conds = []
        for i in input_indices:
            conds.append(x_vars_indexed[int(i)])      # Input = 1
        for i in pure_outputs:
            conds.append(~x_vars_indexed[int(i)])     # Output = 0

        if conds:
            enable_cond = functools.reduce(operator.and_, conds)
        else:
            # [FIX] Dung hang so da tao an toan
            enable_cond = bddone

        # B. Logic trang thai tiep theo (Next State Logic)
        next_state_exprs = []
        for p in range(num_places):
            # Kiem tra bien ma tran
            if t < net.post_matrix.shape[0] and p < net.post_matrix.shape[1]:
                is_in = (net.pre_matrix[t][p] == 1)
                is_out = (net.post_matrix[t][p] == 1)
            else:
                is_in = False
                is_out = False

            x_p = X[p]
            y_p = Y[p]

            if is_out:
                next_state_exprs.append(y_p)        # Sinh token -> Y = 1
            elif is_in and not is_out:
                next_state_exprs.append(~y_p)       # Mat token -> Y = 0
            else:
                # Giu nguyen -> Y = X (XNOR)
                # Dung toan tu ~(x^y) de thay cho Equivalent
                next_state_exprs.append(~(x_p ^ y_p))
        
        # Ket hop: TR_t = Enable AND NextState
        if next_state_exprs:
            next_logic = functools.reduce(operator.and_, next_state_exprs)
            transition_logic = enable_cond & next_logic
        else:
            transition_logic = enable_cond
            
        tr_components.append(transition_logic)

    # TR toan cuc = OR(TR_t1, TR_t2, ...)
    if tr_components:
        global_TR = functools.reduce(operator.or_, tr_components)
    else:
        # [FIX] Dung hang so da tao an toan
        global_TR = bddzero

    # 4. VONG LAP TIM DIEM BAT DONG (FIXED POINT ITERATION)
    steps = 0
    while True:
        steps += 1
        # a. Tinh anh (Image Computation): TIm trang thai tiep theo
        # Formula: exist X . (R(X) AND TR(X, Y))
        rel_prod = R & global_TR
        
        # b. Lam tron (Smoothing): Loai bo bien X
        next_states_y = rel_prod.smoothing(set(X))
        
        # c. Doi ten Y -> X
        next_states_x = next_states_y.compose(rename_y_to_x)
        
        # d. Hop nhat vao tap cu
        new_R = R | next_states_x
        
        # e. Kiem tra dung
        if new_R.equivalent(R):
            break
        R = new_R

    count = int(R.satisfy_count())
    print(f"Finished after {steps} iterations.")
    print(f"Total Reachable Markings (BDD): {count}")
    
    return R, count