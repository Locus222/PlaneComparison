"""Spustí testy a zapíše výsledek."""
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/test_crew_summary.py", "-v", "--tb=short", "--no-header"],
    capture_output=True, text=True,
    cwd=os.path.dirname(os.path.abspath(__file__)),
    timeout=120
)
output = result.stdout + "\n--- STDERR ---\n" + result.stderr
with open("_test_result.txt", "w", encoding="utf-8") as f:
    f.write(output)
print("RC=", result.returncode)
print(output)
