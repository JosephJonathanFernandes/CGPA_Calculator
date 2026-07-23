import json
import sys
sys.path.append('.')
from src.logic import *

results = {}

# 1. Edge cases for SGPA
results['sgpa_0_credits'] = compute_sgpa([8.0], [0]) # Expect {"sgpa": None, "status": "error"}
results['sgpa_max_credits'] = compute_sgpa([8.0], [35]) # Expect ok
results['sgpa_f_grade'] = compute_sgpa([0.0, 9.0], [4, 4]) # Expect {"sgpa": None, "status": "backlog_pending"}
results['sgpa_o_grade'] = compute_sgpa([10.0, 10.0], [4, 4]) # Expect 10.0

# 2. Edge cases for CGPA
results['cgpa_backlog_sem'] = compute_cgpa([8.0, 0.0], [20, 20]) # This tests if a semester with 0.0 SGPA (backlog) crashes it
results['cgpa_all_backlogs'] = compute_cgpa([0.0, 0.0], [20, 20])
results['cgpa_1_sem'] = compute_cgpa([8.0], [20])
results['cgpa_12_sem'] = compute_cgpa([8.0]*12, [20]*12)

# 3. Percentages
results['pct_mu_8'] = cgpa_to_percentage(8.0, 'mu')
results['pct_cbse_8'] = cgpa_to_percentage(8.0, 'cbse')
results['pct_direct_8'] = cgpa_to_percentage(8.0, 'direct')
results['pct_mu_0'] = cgpa_to_percentage(0.0, 'mu')
results['pct_mu_10'] = cgpa_to_percentage(10.0, 'mu')
results['pct_cbse_10'] = cgpa_to_percentage(10.0, 'cbse')
results['pct_direct_10'] = cgpa_to_percentage(10.0, 'direct')

# 4. Target Feasibility
results['req_sgpa_normal'] = required_sgpa_for_target(8.0, 40, 8.5, 20)
results['req_sgpa_0_rem'] = required_sgpa_for_target(8.0, 40, 8.5, 0)
results['req_sgpa_invalid_target'] = required_sgpa_for_target(8.0, 40, 11.0, 20)

for k, v in results.items():
    print(f"{k}: {v}")
