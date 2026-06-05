import sys
import os
import argparse
import numpy as np
import time

from src.pnml_parser import PNMLReader
from src.bfs_explicit import run_bfs_explicit
from src.bdd_reachability import run_bdd_reachability
from src.deadlock import find_deadlock
from src.optimization import find_optimal_marking

def print_header(title):
    print("\n" + "="*60)
    print(f"   {title}")
    print("="*60)

def main():
    # Thiet lap tham so dong lenh de chon file test de dang
    parser = argparse.ArgumentParser(description='Petri Net Analysis Tool')
    parser.add_argument('--input', type=str, default='tests/test_small.pnml', help='Path to PNML input file')
    args = parser.parse_args()

    input_file = args.input

    # --- Kiem tra file dau vao ---
    if not os.path.exists(input_file):
        print(f"\n[ERROR] Input file '{input_file}' not found.")
        print("Please provide a valid PNML file path using --input argument.")
        return

    # ==============================================================================
    # TASK 1: PARSING & MODEL INFO
    # ==============================================================================
    print_header("TASK 1: READ PNML & MODEL DETAILS")
    try:
        start_t = time.time()
        net = PNMLReader.read_file(input_file)
        load_time = time.time() - start_t
        
        print(f"File loaded: {input_file}")
        print(f"Parse time:  {load_time:.4f}s")
        net.print_details()
        
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return

    # ==============================================================================
    # TASK 2: EXPLICIT REACHABILITY (BFS)
    # ==============================================================================
    print_header("TASK 2: REACHABILITY GRAPH (BFS)")
    explicit_states = run_bfs_explicit(net)
    # BFS function in src already prints details, so we just store the result

    # ==============================================================================
    # TASK 3: SYMBOLIC REACHABILITY (BDD)
    # ==============================================================================
    print_header("TASK 3: SYMBOLIC REACHABILITY (BDD)")
    reachable_bdd, bdd_count = run_bdd_reachability(net)

    # --- VERIFICATION: COMPARE BFS vs BDD ---
    print("\n>>> [VERIFICATION] Comparing Task 2 and Task 3 results:")
    if len(explicit_states) == bdd_count:
        print(f"   [PASS] MATCHED! Total Reachable States: {bdd_count}")
    else:
        print(f"   [FAIL] MISMATCH! BFS found {len(explicit_states)}, but BDD found {bdd_count}")
        print("   (Note: If the state space is huge, BFS might have been cut off or memory limit reached)")

    # ==============================================================================
    # TASK 4: DEADLOCK DETECTION (ILP + BDD)
    # ==============================================================================
    print_header("TASK 4: DEADLOCK DETECTION")
    # Luu y: Ham find_deadlock cua ban da tich hop goi ILP truoc, sau do moi fallback ve BDD
    deadlock_marking = find_deadlock(net, reachable_bdd)

    if deadlock_marking:
        print(f"\n   => CONCLUSION: The system has a DEADLOCK.")
    else:
        print(f"\n   => CONCLUSION: The system is DEADLOCK-FREE.")

    # ==============================================================================
    # TASK 5: OPTIMIZATION
    # ==============================================================================
    print_header("TASK 5: OPTIMIZATION (Weighted Sum)")
    
    # Tao trong so mau (Gia su trong so = ID cua Place + 1 hoac random)
    # De don gian va de kiem tra, ta gan tat ca trong so = 1
    weights = np.ones(net.num_places, dtype=int)
    print(f"Weight Vector w: {weights}")
    
    best_m, max_val = find_optimal_marking(net, reachable_bdd, weights)
    
    print("\n   => SUMMARY:")
    print(f"   Max Objective Value: {max_val}")
    print(f"   Optimal Marking:     {best_m}")

    print("\n" + "="*60)
    print("   ANALYSIS COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()