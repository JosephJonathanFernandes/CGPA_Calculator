import sys
import pandas as pd
from src.logic import *

def test_qa():
    bugs = []
    
    # 1. CGPA / SGPA logic
    # - all-same-grade subjects
    res = compute_sgpa([8.0, 8.0, 8.0], [4, 4, 4])
    if res["sgpa"] != 8.0 or res["status"] != "cleared":
        bugs.append(f"SGPA all-same-grade failed: {res}")
        
    # - mixed grades
    res = compute_sgpa([10.0, 5.0], [4, 4])
    if res["sgpa"] != 7.5 or res["status"] != "cleared":
        bugs.append(f"SGPA mixed grades failed: {res}")
        
    # - a single subject
    res = compute_sgpa([9.0], [3])
    if res["sgpa"] != 9.0 or res["status"] != "cleared":
        bugs.append(f"SGPA single subject failed: {res}")
        
    # - maximum subject count (e.g. 20)
    res = compute_sgpa([8.0]*20, [3]*20)
    if res["sgpa"] != 8.0 or res["status"] != "cleared":
        bugs.append(f"SGPA max subjects failed: {res}")
        
    # - 0-credit audit course
    res = compute_sgpa([8.0, 0.0], [4, 0])
    if res["sgpa"] != 8.0 or res["status"] != "cleared":
        bugs.append(f"SGPA 0-credit course failed: {res}")
        
    # - Backlog state: F in exactly one subject
    res = compute_sgpa([8.0, 0.0, 8.0], [3, 4, 3])
    if res["status"] != "backlog_pending":
        bugs.append(f"SGPA Backlog 1 F failed: expected backlog_pending, got {res}")
    if res["sgpa"] is not None:
        bugs.append(f"SGPA Backlog 1 F sgpa is not None: {res}")
        
    # CGPA withheld
    cgpa_res = compute_cgpa([8.0, None, 8.0], [20, 20, 20])
    if cgpa_res["status"] != "blocked" or cgpa_res["cgpa"] is not None:
        bugs.append(f"CGPA Backlog withheld failed: {cgpa_res}")

    # - Backlog state: F in more than one semester simultaneously
    cgpa_res = compute_cgpa([None, None, 8.0], [20, 20, 20])
    if cgpa_res["status"] != "blocked" or cgpa_res["blocked_semesters"] != [1, 2]:
        bugs.append(f"CGPA Backlog multiple failed: {cgpa_res}")
        
    # - Backlog state: F as the ONLY subject in a semester
    res = compute_sgpa([0.0], [4])
    if res["status"] != "backlog_pending":
        bugs.append(f"SGPA Backlog only F failed: {res}")
        
    # - Weighted vs Simple Average
    cgpa_res = compute_cgpa([8.0, 9.0], [20, 10], method="simple_average")
    if cgpa_res["cgpa"] != 8.5:
        bugs.append(f"CGPA Simple Average failed: {cgpa_res}")
        
    cgpa_res2 = compute_cgpa([8.0, 9.0], [20, 10], method="weighted")
    expected = (8.0*20 + 9.0*10) / 30
    if abs(cgpa_res2["cgpa"] - expected) > 0.001:
        bugs.append(f"CGPA Weighted Average failed: {cgpa_res2}")

    # Percentage formulas
    mu = cgpa_to_percentage(8.0, "mu")
    if abs(mu - 72.5) > 0.001: bugs.append(f"MU formula wrong: {mu}")
    
    cbse = cgpa_to_percentage(8.0, "cbse")
    if abs(cbse - 76.0) > 0.001: bugs.append(f"CBSE formula wrong: {cbse}")
    
    direct = cgpa_to_percentage(8.0, "direct")
    if abs(direct - 80.0) > 0.001: bugs.append(f"Direct formula wrong: {direct}")

    # Target planner
    req = required_sgpa_for_target(8.0, 80, 8.5, 40)
    if abs(req - 9.5) > 0.001: bugs.append(f"Target Planner basic failed: {req}")
    
    # Target Planner: 0 remaining credits
    req = required_sgpa_for_target(8.0, 80, 8.5, 0)
    if req is not None: bugs.append(f"Target Planner 0 credits failed: {req}")
    
    # Feasibility
    if classify_target_feasibility(0.0) != "Already Achieved":
        bugs.append(f"Target Planner feasibility <=0 failed")
    if classify_target_feasibility(10.0) != "Feasible":
        bugs.append(f"Target Planner feasibility <=10 failed")
    if classify_target_feasibility(10.01) != "Not Feasible":
        bugs.append(f"Target Planner feasibility >10 failed")
        
    for bug in bugs:
        print("BUG FOUND:", bug)
    if not bugs:
        print("All pure logic QA passed.")

if __name__ == '__main__':
    test_qa()
