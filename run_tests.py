#!/usr/bin/env python3

import subprocess
import sys
import os
import time  # NEW

def run_test(test_num, expected):
    test_file = f"test_input_{test_num}.txt"

    if not os.path.exists(test_file):
        print(f"Test {test_num}: ❌ FILE NOT FOUND - {test_file}")
        return False

    try:
        with open(test_file, "r") as f:
            start = time.perf_counter()  # NEW
            result = subprocess.run(
                ["python3", "zoo_solution.py"],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=5
            )
            elapsed_ms = (time.perf_counter() - start) * 1000  # NEW

        output = result.stdout.strip()

        if output == expected:
            print(f"Test {test_num}: ✅ PASS | {elapsed_ms:9.2f} ms | Output: {output:15} | Expected: {expected}")
            return True
        else:
            print(f"Test {test_num}: ❌ FAIL | {elapsed_ms:9.2f} ms | Output: {output:15} | Expected: {expected}")
            return False

    except subprocess.TimeoutExpired:
        print(f"Test {test_num}: ⏱️ TIMEOUT (5s)")
        return False
    except Exception as e:
        print(f"Test {test_num}: ❌ ERROR - {e}")
        return False

def main():
    tests = [
        (1, "possible"),
        (2, "impossible"),
        (3, "possible"),
        (4, "impossible"),
    ]

    print("\n" + "="*80)
    print(" "*15 + "Zoo Management (ICPC 2023 World Finals - Problem R)")
    print("="*80 + "\n")

    suite_start = time.perf_counter()   # NEW

    passed = 0
    for test_num, expected in tests:
        if run_test(test_num, expected):
            passed += 1

    suite_ms = (time.perf_counter() - suite_start) * 1000  # NEW

    print("\n" + "="*80)
    total = len(tests)
    percentage = (100 * passed) // total if total > 0 else 0
    print(f"Results: {passed}/{total} tests passed ({percentage}%)")
    print(f"Total runtime: {suite_ms:.2f} ms")  # NEW
    print("="*80 + "\n")

    if passed == total:
        print("✅ All tests passed! Ready for LMS submission.\n")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

