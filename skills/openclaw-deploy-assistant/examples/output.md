Execution summary:
- Platform routed: macOS
- Baseline check: node >=22, npm available
- Flow executed: setup -> start -> check
- Acceptance check: doctor/status/dashboard executed

Result:
- Deployment status: passed
- Service state: running
- Dashboard: reachable

If failed:
- First error line captured
- doctor/status rerun completed
- Binary path/version diagnostics captured
- Next fix action listed from troubleshooting docs
