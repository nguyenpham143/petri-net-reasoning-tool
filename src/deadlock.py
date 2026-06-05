import time
from src.common_utils import sanitize_variable_name
import pyeda.inter as pye 
import pulp as lp
from src.petri_model import SafePetriNetSystem
import numpy as np
import functools
import operator
from typing import List, Optional

# [FIX] Khoi tao bddone/bddzero an toan
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

bddvar = pye.bddvar

def find_deadlock(net: SafePetriNetSystem, reachable_bdd: pye.BinaryDecisionDiagram) -> Optional[List[int]]:
    start_time = time.time()
    """
    Task 4: Phat hien trang thai Deadlock (Tac nghen).
    
    Ly thuyet:
    - Deadlock la trang thai ma tai do he thong dung hoat dong vi KHONG CO bat ky 
      transition nao thoa man dieu kien ban (Enabled).
    - Cong thuc BDD: Deadlock = Reachable_Set AND (NOT (Enable_T1 OR Enable_T2 ...))
    """
    print(f"\n>>> [Task 4] DEADLOCK ANALYSIS")

    """
    Su dung phuong phap ILP de giai truoc (nhanh hon ve thoi gian), nhung ILP 
    co the cho ra unreachable marking neu Petri Net co it nhat 1 truong hop P <==> T
    (hoac mot so dieu kien khac tui chua tim ra) nen phai kiem tra ket qua co reachable
    hay khong. Neu khong thi chay theo bdd.
    """

    result = ILP_deadlock_detection(net)
    
    # Neu ILP tra ve None tuc la khong co deadlock
    if result is None:
        time_taken = time.time() - start_time
        print("\n[RESULT] System is SAFE. No deadlock state found (ILP Check).")
        print(f"Execution time for deadlock detection: {time_taken:.4f}")
        return None
    
    # [FIX] Verfiy ket qua ILP co reachable khong
    reachable_check = is_reachable(net, reachable_bdd, result)
    
    if reachable_check:
        time_taken = time.time() - start_time
        print(f"\n[WARNING] DEADLOCK DETECTED!")
        print(f"-> Deadlock Marking: {result}")
        print(f"Execution time for deadlock detection: {time_taken:.4f}")
        return result
    
    # input("ILP method failed since marking found was not reachable.\n")

    # 1. Tai tao bien BDD (Can khop ten bien voi Task 3 de tinh toan chung)
    X_vars = []
    x_vars_indexed = [] # Dung de truy cap theo index ma tran
    
    for pid in net.places:
        vname = sanitize_variable_name(pid)
        # [FIX] Dung bddvar an toan
        var = bddvar(vname) # Bien trang thai hien tai (x)
        X_vars.append(var)
        x_vars_indexed.append(var)

    # 2. Xay dung dieu kien "Co it nhat 1 transition ban duoc" (Any Enabled)
    enabled_exprs = []
    
    # Lay so luong transition thuc te (de phong ma tran thieu dong)
    actual_trans_count = min(net.num_transitions, net.pre_matrix.shape[0])

    for t in range(actual_trans_count):
        # Lay danh sach Place dau vao va dau ra tu Ma tran cau truc
        input_indices = np.where(net.pre_matrix[t] == 1)[0]
        output_indices = np.where(net.post_matrix[t] == 1)[0]
        
        # Logic Safety (1-safe): Transition chi ban duoc neu Output Place dang rong
        # (tru khi place do vua la Input vua la Output)
        pure_outputs = [i for i in output_indices if i not in input_indices]

        conds = []
        # Dieu kien 1: Input places phai co token (=1)
        for i in input_indices:
            conds.append(x_vars_indexed[int(i)])
            
        # Dieu kien 2: Output places phai rong (=0)
        for i in pure_outputs:
            conds.append(~x_vars_indexed[int(i)])

        # Hop nhat cac dieu kien bang AND
        if conds:
            t_enabled = functools.reduce(operator.and_, conds)
        else:
            t_enabled = bddone # [FIX] bddone

        enabled_exprs.append(t_enabled)

    # Hop nhat tat ca transition bang OR -> "Co bat ky cai nao ban duoc khong?"
    if enabled_exprs:
        any_trans_enabled = functools.reduce(operator.or_, enabled_exprs)
    else:
        any_trans_enabled = bddzero # [FIX] bddzero

    # 3. Dieu kien Deadlock: Phu dinh cua "Co transition ban duoc"
    is_dead = ~any_trans_enabled

    # 4. Giao voi tap Reachable de tim Deadlock thuc su
    # (Vi co the co trang thai dead nhung khong bao gio voi toi duoc tu M0)
    deadlock_states = reachable_bdd & is_dead

    # 5. Trich xuat ket qua (Lay 1 nghiem mau de bao cao)
    solution = deadlock_states.satisfy_one()
    
    if solution is None:
        print("\n[RESULT] System is SAFE. No deadlock state found.")
        return None

    # Chuyen doi tu dict {Bien BDD: Gia Tri} sang List[int]
    result = []
    for var in X_vars:
        # Neu bien khong xuat hien trong nghiem (Don't care), mac dinh la 0
        val = solution.get(var, 0) 
        result.append(int(val))

    time_taken = time.time() - start_time
    print(f"\n[WARNING] DEADLOCK DETECTED!")
    print(f"-> Deadlock Marking: {result}")
    print(f"Execution time for deadlock detection: {time_taken:.4f}")
    return result


def ILP_deadlock_detection(
    pn: SafePetriNetSystem,
) -> Optional[List[int]]:
    # Create coincidence matrix
    n_places = pn.num_places
    n_transitions = min(pn.num_transitions, pn.pre_matrix.shape[0])
    Coincidence = pn.post_matrix - pn.pre_matrix                                    # C[t][p] = Post[t][p] - Pre[t][p]

    LPmodel = lp.LpProblem("ILP_deadlock_detection", lp.LpMaximize)
    
    # [FIX] Dung range(n_places) lam key
    M = lp.LpVariable.dicts("Num_of_tokens_in_each_place", range(n_places), cat = "Binary")     # Constraint 1: 0 <= M <= 1
    x = lp.LpVariable.dicts("Num_of_fires_for_each_transition", range(n_transitions), cat = "Integer", lowBound=0)
    
    for p_in in range(n_places):
        # [FIX] Tinh dot product thu cong
        dot_product = lp.lpSum([Coincidence[t_idx][p_in] * x[t_idx] for t_idx in range(n_transitions)])
        LPmodel += M[p_in] == pn.initial_marking[p_in] + dot_product     # Constraint 2: M[p] = M0[p] + C[p]*x

    for t_in in range(n_transitions):
        I_places_in = np.where(pn.pre_matrix[t_in] == 1)[0]
        
        # Chi them constraint neu co input places
        if len(I_places_in) > 0:
            M_I_places = [M[p_in] for p_in in I_places_in]                 # Number of tokens in each of those places
            n_inputs = len(I_places_in)
            LPmodel += lp.lpSum(M_I_places) <= n_inputs - 1                # Constraint 3: Sum(input_places) <= Count(input_places) - 1, for every transition
    
    LPmodel.solve(lp.PULP_CBC_CMD(msg=0)) # Tat log solver
    status = lp.LpStatus[LPmodel.status]

    if status == "Infeasible":
        return None
    else:
        # [FIX] Lay ket qua tu bien M theo index
        result_marking = []
        for p_in in range(n_places):
            result_marking.append(int(M[p_in].varValue))
        return result_marking

# Ham verify moi
def is_reachable(net, reachable_bdd, marking_list):
    bdd_vars = [bddvar(sanitize_variable_name(p)) for p in net.place_labels]
    exprs = []
    for i, val in enumerate(marking_list):
        if val == 1: exprs.append(bdd_vars[i])
        else: exprs.append(~bdd_vars[i])
    marking_bdd = functools.reduce(operator.and_, exprs)
    return not (reachable_bdd & marking_bdd).is_zero()