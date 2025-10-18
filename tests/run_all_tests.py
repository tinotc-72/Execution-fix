#!/usr/bin/env python3
"""
Test runner for all DEX minimal tests

This script runs all DEX tests in simulate mode to verify they work correctly.

Usage:
    python tests/run_all_tests.py
"""

import subprocess
import sys
from pathlib import Path

# Configure colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_test(test_name, script_path):
    """Run a single test script in simulate mode."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}Running: {test_name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")
    
    try:
        # Run the test in simulate mode
        result = subprocess.run(
            [sys.executable, str(script_path), "--simulate"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Check exit code
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {test_name} passed{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.RED}❌ {test_name} failed with exit code {result.returncode}{Colors.ENDC}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}❌ {test_name} timed out{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ {test_name} raised exception: {e}{Colors.ENDC}")
        return False


def main():
    """Run all tests."""
    print(f"{Colors.BOLD}Minimal per-DEX Test Suite{Colors.ENDC}")
    print(f"Running all tests in simulate mode...\n")
    
    tests_dir = Path(__file__).parent
    
    tests = [
        ("Jupiter DEX Test", tests_dir / "test_jupiter.py"),
        ("Pump.fun DEX Test", tests_dir / "test_pumpfun.py"),
        ("Raydium CPMM DEX Test", tests_dir / "test_raydium_cpmm.py"),
        ("Meteora DEX Test", tests_dir / "test_meteora.py"),
    ]
    
    results = []
    for test_name, script_path in tests:
        passed = run_test(test_name, script_path)
        results.append((test_name, passed))
    
    # Print summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}Test Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}PASSED{Colors.ENDC}" if passed else f"{Colors.RED}FAILED{Colors.ENDC}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed_count}/{total_count} tests passed{Colors.ENDC}")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}✅ All tests passed!{Colors.ENDC}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  Some tests failed or require implementation{Colors.ENDC}\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
