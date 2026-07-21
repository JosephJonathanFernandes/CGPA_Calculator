import pytest
import pandas as pd
from src.logic import *

def test_sgpa_all_same_grade():
    res = compute_sgpa([8.0, 8.0, 8.0], [4, 4, 4])
    assert res["sgpa"] == 8.0
    assert res["status"] == "cleared"

def test_sgpa_mixed_grades():
    res = compute_sgpa([10.0, 5.0], [4, 4])
    assert res["sgpa"] == 7.5
    assert res["status"] == "cleared"

def test_sgpa_single_subject():
    res = compute_sgpa([9.0], [3])
    assert res["sgpa"] == 9.0
    assert res["status"] == "cleared"

def test_sgpa_max_subjects():
    res = compute_sgpa([8.0] * 20, [3] * 20)
    assert res["sgpa"] == 8.0
    assert res["status"] == "cleared"

def test_sgpa_audit_course():
    res = compute_sgpa([8.0, 0.0], [4, 0])
    assert res["sgpa"] == 8.0
    assert res["status"] == "cleared"

def test_backlog_one_f_one_semester():
    res = compute_sgpa([8.0, 0.0, 8.0], [3, 4, 3])
    assert res["status"] == "backlog_pending"
    assert res["sgpa"] is None

def test_cgpa_withheld_from_sgpa():
    res = compute_cgpa([8.0, None, 8.0], [20, 20, 20])
    assert res["status"] == "blocked"
    assert res["cgpa"] is None
    assert res["blocked_semesters"] == [2]

def test_cgpa_withheld_multiple_semesters():
    res = compute_cgpa([None, None, 8.0], [20, 20, 20])
    assert res["status"] == "blocked"
    assert res["blocked_semesters"] == [1, 2]

def test_backlog_only_f():
    res = compute_sgpa([0.0], [4])
    assert res["status"] == "backlog_pending"

def test_cgpa_average_modes():
    cgpa_res1 = compute_cgpa([8.0, 9.0], [20, 10], method="simple_average")
    assert cgpa_res1["cgpa"] == 8.5
    
    cgpa_res2 = compute_cgpa([8.0, 9.0], [20, 10], method="weighted")
    expected = (8.0*20 + 9.0*10) / 30
    assert abs(cgpa_res2["cgpa"] - expected) < 0.001

def test_percentage_formulas():
    assert abs(cgpa_to_percentage(8.0, "mu") - 72.5) < 0.001
    assert abs(cgpa_to_percentage(8.0, "cbse") - 76.0) < 0.001
    assert abs(cgpa_to_percentage(8.0, "direct") - 80.0) < 0.001

def test_target_planner():
    # Feasible
    req = required_sgpa_for_target(8.0, 80, 8.5, 40)
    assert abs(req - 9.5) < 0.001
    assert classify_target_feasibility(req) == "Feasible"

    # Already achieved (req <= 0)
    req = required_sgpa_for_target(9.0, 80, 5.0, 40)
    assert classify_target_feasibility(req) == "Already Achieved"

    # Not feasible
    req = required_sgpa_for_target(6.0, 80, 9.5, 20)
    assert classify_target_feasibility(req) == "Not Feasible"

    # 0 remaining credits
    req = required_sgpa_for_target(8.0, 80, 8.5, 0)
    assert req is None
