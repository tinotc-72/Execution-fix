#!/usr/bin/env python3
"""
Execution Pipeline Diagnostic Tool
===================================

Static analysis tool that scans the repository for execution pipeline failures
and produces a structured Markdown report with prioritized remediation suggestions.

This tool performs read-only analysis and does not modify any files.

Usage:
    python tools/diagnose_execution_pipeline.py

Output:
    - Prints summary to stdout
    - Generates docs/PIPELINE_DIAGNOSTIC.md with detailed findings
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Finding:
    """Represents a single diagnostic finding"""
    file_path: str
    line_num: int
    severity: str  # "HIGH", "MEDIUM", "LOW"
    category: str
    description: str
    code_snippet: str
    suggestion: str


@dataclass
class DiagnosticReport:
    """Container for all diagnostic findings"""
    findings: List[Finding] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def add_finding(self, finding: Finding):
        """Add a finding and update statistics"""
        self.findings.append(finding)
        self.stats[finding.severity] += 1
        self.stats[f"category_{finding.category}"] += 1


class ExecutionPipelineDiagnostic:
    """Main diagnostic engine"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.report = DiagnosticReport()
        
    def scan_repository(self):
        """Scan entire repository for execution pipeline issues"""
        print("[DIAGNOSTIC] Scanning repository for execution pipeline issues...")
        
        # Get all Python files
        python_files = list(self.repo_root.glob("**/*.py"))
        
        # Exclude certain directories
        excluded_dirs = {'.git', '__pycache__', '.venv', 'venv', 'OLDER', 'UNSORTED_MISC'}
        python_files = [
            f for f in python_files 
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]
        
        print(f"[DIAGNOSTIC] Found {len(python_files)} Python files to analyze")
        
        for py_file in python_files:
            try:
                self._analyze_file(py_file)
            except Exception as e:
                print(f"[DIAGNOSTIC] Warning: Error analyzing {py_file}: {e}")
        
        print(f"[DIAGNOSTIC] Scan complete. Found {len(self.report.findings)} issues")
        
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        rel_path = file_path.relative_to(self.repo_root)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return  # Skip files that can't be read
        
        # Run all checks
        self._check_ata_placeholder(rel_path, content, lines)
        self._check_ata_exists_param(rel_path, content, lines)
        self._check_create_ata_usage(rel_path, content, lines)
        self._check_none_returns(rel_path, content, lines)
        self._check_buildresult_imports(rel_path, content, lines)
        self._check_message_compile_alts(rel_path, content, lines)
        self._check_missing_build_alts(rel_path, content, lines)
        self._check_compute_budget_placement(rel_path, content, lines)
        self._check_instruction_data_type(rel_path, content, lines)
        self._check_raw_submission_calls(rel_path, content, lines)
        self._check_scaffold_executors(rel_path, content, lines)
        self._check_solana_py_imports(rel_path, content, lines)
        self._check_missing_blockhash(rel_path, content, lines)
        self._check_improper_ata_signer(rel_path, content, lines)
        
    def _check_ata_placeholder(self, rel_path: Path, content: str, lines: List[str]):
        """Check for placeholder ATA PDA derivation"""
        # Check if this is utils/ata.py
        if str(rel_path) == "utils/ata.py" or str(rel_path).endswith("/ata.py"):
            # Look for the placeholder return in associated_token_address
            for i, line in enumerate(lines, 1):
                if "return mint" in line and "# placeholder" in line.lower():
                    self.report.add_finding(Finding(
                        file_path=str(rel_path),
                        line_num=i,
                        severity="HIGH",
                        category="ATA_PLACEHOLDER",
                        description="Placeholder ATA PDA derivation returns mint instead of proper PDA",
                        code_snippet=line.strip(),
                        suggestion="Replace with: seeds = [bytes(owner), bytes(SPL_TOKEN_PROGRAM_ID), bytes(mint)]; ata, _ = Pubkey.find_program_address(seeds, SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID); return ata"
                    ))
                    
    def _check_ata_exists_param(self, rel_path: Path, content: str, lines: List[str]):
        """Check for ensure_ata functions using 'exists' boolean instead of RPC query"""
        # Look for ensure_ata_for or ensure_ata_ixs with exists parameter
        for i, line in enumerate(lines, 1):
            if re.search(r'def\s+ensure_ata_(for|ixs)\s*\([^)]*exists\s*:', line):
                # Found function definition with exists parameter
                self.report.add_finding(Finding(
                    file_path=str(rel_path),
                    line_num=i,
                    severity="HIGH",
                    category="ATA_EXISTS_BOOLEAN",
                    description="ensure_ata function uses 'exists' boolean parameter instead of RPC query",
                    code_snippet=line.strip(),
                    suggestion="Replace 'exists' parameter with actual RPC query: response = await rpc_client.get_token_accounts_by_owner(owner, {'mint': str(mint)}); exists = response.value is not None and len(response.value) > 0"
                ))
                
            # Also check for calls using exists parameter
            if re.search(r'ensure_ata_(for|ixs)\s*\([^)]*exists\s*=', line):
                self.report.add_finding(Finding(
                    file_path=str(rel_path),
                    line_num=i,
                    severity="MEDIUM",
                    category="ATA_EXISTS_USAGE",
                    description="Call to ensure_ata function passes 'exists' boolean instead of querying RPC",
                    code_snippet=line.strip(),
                    suggestion="Remove 'exists' parameter and let the function query RPC directly"
                ))
                
    def _check_create_ata_usage(self, rel_path: Path, content: str, lines: List[str]):
        """Check create_associated_token_account usage and PDA derivation"""
        for i, line in enumerate(lines, 1):
            if "create_associated_token_account" in line:
                # Check if it's using associated_token_address
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 5)
                context = "\n".join(lines[context_start:context_end])
                
                if "associated_token_address" in context:
                    # Check if the placeholder issue exists
                    if str(rel_path) == "utils/ata.py" or "return mint" in context:
                        self.report.add_finding(Finding(
                            file_path=str(rel_path),
                            line_num=i,
                            severity="HIGH",
                            category="ATA_PDA_DERIVATION",
                            description="create_associated_token_account may be using placeholder PDA derivation",
                            code_snippet=line.strip(),
                            suggestion="Ensure associated_token_address() performs proper PDA derivation using Pubkey.find_program_address"
                        ))
                        
    def _check_none_returns(self, rel_path: Path, content: str, lines: List[str]):
        """Check for functions that should return BuildResult but return None"""
        # Look for functions that might be builders (have build/execute/try_ in name)
        # and return None
        in_function = False
        function_name = ""
        function_line = 0
        has_buildresult_return = False
        
        for i, line in enumerate(lines, 1):
            # Check for function definition
            func_match = re.match(r'\s*(?:async\s+)?def\s+((?:build|execute|try_)\w+)\s*\(', line)
            if func_match:
                in_function = True
                function_name = func_match.group(1)
                function_line = i
                has_buildresult_return = False
                
            # Check for return BuildResult in type hint
            if in_function and "-> BuildResult" in line:
                has_buildresult_return = True
                
            # Check for return None
            if in_function and re.match(r'\s*return\s+None\s*$', line):
                if has_buildresult_return:
                    self.report.add_finding(Finding(
                        file_path=str(rel_path),
                        line_num=i,
                        severity="HIGH",
                        category="NONE_RETURN",
                        description=f"Function '{function_name}' declares BuildResult return type but returns None",
                        code_snippet=line.strip(),
                        suggestion="Return BuildResult(ok=False, tx=None, reason='...') instead of None"
                    ))
                    
            # Reset when we exit the function (next def or class)
            if in_function and i > function_line:
                if re.match(r'^(?:class|def|async\s+def)\s+', line):
                    in_function = False
                    
    def _check_buildresult_imports(self, rel_path: Path, content: str, lines: List[str]):
        """Check if builders that return BuildResult have the import"""
        has_buildresult_import = "from models.build_result import BuildResult" in content
        has_buildresult_return = "-> BuildResult" in content
        
        if has_buildresult_return and not has_buildresult_import:
            # Find the line with BuildResult return type
            for i, line in enumerate(lines, 1):
                if "-> BuildResult" in line:
                    self.report.add_finding(Finding(
                        file_path=str(rel_path),
                        line_num=i,
                        severity="HIGH",
                        category="MISSING_BUILDRESULT_IMPORT",
                        description="Function declares BuildResult return type but BuildResult is not imported",
                        code_snippet=line.strip(),
                        suggestion="Add: from models.build_result import BuildResult"
                    ))
                    break
                    
    def _check_message_compile_alts(self, rel_path: Path, content: str, lines: List[str]):
        """Check MessageV0.compile / VersionedTransaction creation for missing ALTs"""
        for i, line in enumerate(lines, 1):
            # Look for MessageV0.compile calls
            if "MessageV0.compile" in line or "Message.new_with_blockhash" in line:
                # Check if address_lookup_tables is passed
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 3)
                context = "\n".join(lines[context_start:context_end])
                
                # Check for addressTableLookups in the broader context
                if "addressTableLookups" in content or "address_table_lookups" in content:
                    # This file deals with ALTs
                    if not ("address_lookup_tables" in context or "lookup_tables" in context):
                        self.report.add_finding(Finding(
                            file_path=str(rel_path),
                            line_num=i,
                            severity="HIGH",
                            category="MISSING_ALTS_COMPILE",
                            description="MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter",
                            code_snippet=line.strip(),
                            suggestion="Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])"
                        ))
                        
    def _check_missing_build_alts(self, rel_path: Path, content: str, lines: List[str]):
        """Check for missing build_alts_from_tables calls when ALTs are present"""
        has_address_table_lookups = "addressTableLookups" in content or "address_table_lookups" in content
        has_build_alts_call = "build_alts_from_tables" in content
        
        if has_address_table_lookups and not has_build_alts_call:
            # Find where addressTableLookups appears
            for i, line in enumerate(lines, 1):
                if "addressTableLookups" in line or "address_table_lookups" in line:
                    self.report.add_finding(Finding(
                        file_path=str(rel_path),
                        line_num=i,
                        severity="MEDIUM",
                        category="MISSING_BUILD_ALTS",
                        description="File references addressTableLookups but doesn't call build_alts_from_tables",
                        code_snippet=line.strip(),
                        suggestion="Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)"
                    ))
                    break
                    
    def _check_compute_budget_placement(self, rel_path: Path, content: str, lines: List[str]):
        """Check if with_compute_budget is used before MessageV0.compile"""
        for i, line in enumerate(lines, 1):
            if "MessageV0.compile" in line:
                # Look backwards for with_compute_budget
                context_start = max(0, i - 20)
                context_lines = lines[context_start:i]
                
                if "with_compute_budget" in "\n".join(context_lines):
                    # Good - compute budget is before compile
                    pass
                elif "with_compute_budget" in content:
                    # with_compute_budget exists but might be in wrong place
                    # Look if it's after compile
                    context_end = min(len(lines), i + 20)
                    after_lines = lines[i:context_end]
                    if "with_compute_budget" in "\n".join(after_lines):
                        self.report.add_finding(Finding(
                            file_path=str(rel_path),
                            line_num=i,
                            severity="HIGH",
                            category="COMPUTE_BUDGET_PLACEMENT",
                            description="with_compute_budget called AFTER MessageV0.compile (should be before)",
                            code_snippet=line.strip(),
                            suggestion="Call with_compute_budget BEFORE MessageV0.compile: ixs = with_compute_budget(ixs, ...); message = MessageV0.compile(...)"
                        ))
                        
    def _check_instruction_data_type(self, rel_path: Path, content: str, lines: List[str]):
        """Check if Instruction.data is constructed as list instead of bytes"""
        for i, line in enumerate(lines, 1):
            # Look for Instruction creation with data parameter
            if "Instruction(" in line:
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 5)
                context = "\n".join(lines[context_start:context_end])
                
                # Check if data is a list (look for [0x.. or [1, 2, 3 patterns)
                if re.search(r'data\s*=\s*\[\s*(?:0x|\d)', context):
                    self.report.add_finding(Finding(
                        file_path=str(rel_path),
                        line_num=i,
                        severity="MEDIUM",
                        category="INSTRUCTION_DATA_TYPE",
                        description="Instruction.data constructed as list instead of bytes",
                        code_snippet=line.strip(),
                        suggestion="Convert to bytes: data=bytes([...]) or data=b'...'"
                    ))
                    
    def _check_raw_submission_calls(self, rel_path: Path, content: str, lines: List[str]):
        """Check for raw submission calls instead of unified send_and_confirm_v0_tx"""
        raw_patterns = [
            r'\.sendTransaction\s*\(',
            r'\.sendRawTransaction\s*\(',
            r'requests\.post\s*\([^)]*swap',
            r'httpx\.post\s*\([^)]*swap',
            r'client\.send_transaction\s*\(',
            r'rpc_client\.send_transaction\s*\(',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in raw_patterns:
                if re.search(pattern, line):
                    # Check if send_and_confirm_v0_tx is used elsewhere in file
                    if "send_and_confirm_v0_tx" not in content:
                        self.report.add_finding(Finding(
                            file_path=str(rel_path),
                            line_num=i,
                            severity="HIGH",
                            category="RAW_SUBMISSION",
                            description="Using raw submission call instead of unified send_and_confirm_v0_tx",
                            code_snippet=line.strip(),
                            suggestion="Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)"
                        ))
                        break
                        
    def _check_scaffold_executors(self, rel_path: Path, content: str, lines: List[str]):
        """Check for scaffold/nonfunctional executors not gated behind config"""
        # Check for mev_raydium_executor.py and similar scaffold files
        scaffold_markers = [
            "minimal scaffold",
            "not functional yet",
            "TODO: Implement",
            "currently non-functional",
            "scaffold for",
        ]
        
        if any(marker.lower() in content.lower() for marker in scaffold_markers):
            # This looks like a scaffold file
            # Check if it has config gating
            has_config_gate = any([
                "if os.getenv" in content,
                "if config.get" in content,
                "if ENABLE_" in content,
            ])
            
            if not has_config_gate and str(rel_path).endswith("_executor.py"):
                # Find the class or function definition
                for i, line in enumerate(lines, 1):
                    if "class " in line or "def try_" in line:
                        self.report.add_finding(Finding(
                            file_path=str(rel_path),
                            line_num=i,
                            severity="MEDIUM",
                            category="SCAFFOLD_EXECUTOR",
                            description="Scaffold/nonfunctional executor not gated behind config flag",
                            code_snippet=line.strip(),
                            suggestion="Add config gating: if not os.getenv('ENABLE_SCAFFOLD_EXECUTORS'): return BuildResult(ok=False, reason='Executor disabled')"
                        ))
                        break
                        
    def _check_solana_py_imports(self, rel_path: Path, content: str, lines: List[str]):
        """Check for any usage of solana-py imports"""
        for i, line in enumerate(lines, 1):
            if re.match(r'\s*(?:from|import)\s+solana\.', line):
                self.report.add_finding(Finding(
                    file_path=str(rel_path),
                    line_num=i,
                    severity="LOW",
                    category="SOLANA_PY_IMPORT",
                    description="Using solana-py import (should use solders)",
                    code_snippet=line.strip(),
                    suggestion="Replace with solders equivalent: from solders.* import ..."
                ))
                
    def _check_missing_blockhash(self, rel_path: Path, content: str, lines: List[str]):
        """Check for missing get_recent_blockhash usage"""
        # Look for MessageV0.compile or transaction building
        has_message_compile = "MessageV0.compile" in content or "Message.new_with_blockhash" in content
        has_blockhash_fetch = "get_recent_blockhash" in content or "get_latest_blockhash" in content
        
        if has_message_compile and not has_blockhash_fetch:
            # This might be missing blockhash fetch
            for i, line in enumerate(lines, 1):
                if "MessageV0.compile" in line or "Message.new_with_blockhash" in line:
                    # Check if blockhash is a parameter or variable
                    context_start = max(0, i - 10)
                    context = "\n".join(lines[context_start:i])
                    
                    if "blockhash" not in context:
                        self.report.add_finding(Finding(
                            file_path=str(rel_path),
                            line_num=i,
                            severity="MEDIUM",
                            category="MISSING_BLOCKHASH",
                            description="MessageV0.compile without apparent blockhash fetch",
                            code_snippet=line.strip(),
                            suggestion="Fetch blockhash: from utils.alt_fetch import get_recent_blockhash; blockhash = await get_recent_blockhash(rpc_url)"
                        ))
                    break
                    
    def _check_improper_ata_signer(self, rel_path: Path, content: str, lines: List[str]):
        """Check for improper signer/owner in create_associated_token_account"""
        for i, line in enumerate(lines, 1):
            if "create_associated_token_account" in line:
                # Get some context
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 2)
                context = "\n".join(lines[context_start:context_end])
                
                # Look for suspicious patterns like payer != owner
                # This is a heuristic check
                if "create_associated_token_account(payer, owner" in context:
                    # This is correct pattern, skip
                    pass
                elif re.search(r'create_associated_token_account\([^,]+,\s*[^,]+,\s*[^)]+\)', line):
                    # Has 3 params, check if owner/payer seem right
                    # This is a basic check - may need refinement
                    pass
                    
    def generate_report(self, output_path: str):
        """Generate Markdown report"""
        print(f"[DIAGNOSTIC] Generating report to {output_path}...")
        
        # Sort findings by severity and file
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_findings = sorted(
            self.report.findings,
            key=lambda f: (severity_order.get(f.severity, 3), f.file_path, f.line_num)
        )
        
        with open(output_path, 'w') as f:
            f.write("# Execution Pipeline Diagnostic Report\n\n")
            f.write(f"**Generated:** {self._get_timestamp()}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"**Total Issues Found:** {len(self.report.findings)}\n\n")
            f.write(f"- 🔴 HIGH severity: {self.report.stats['HIGH']}\n")
            f.write(f"- 🟡 MEDIUM severity: {self.report.stats['MEDIUM']}\n")
            f.write(f"- 🔵 LOW severity: {self.report.stats['LOW']}\n\n")
            
            # Category Breakdown
            f.write("## Issues by Category\n\n")
            categories = {}
            for finding in sorted_findings:
                categories[finding.category] = categories.get(finding.category, 0) + 1
            
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{category}:** {count} issues\n")
            f.write("\n")
            
            # Prioritized Remediation List
            f.write("## Prioritized Remediation List\n\n")
            
            # Group by severity
            for severity in ["HIGH", "MEDIUM", "LOW"]:
                severity_findings = [f for f in sorted_findings if f.severity == severity]
                if severity_findings:
                    icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}[severity]
                    f.write(f"### {icon} {severity} Priority\n\n")
                    
                    for finding in severity_findings:
                        f.write(f"#### {finding.category}: {finding.file_path}:{finding.line_num}\n\n")
                        f.write(f"**Description:** {finding.description}\n\n")
                        f.write(f"**Code:**\n```python\n{finding.code_snippet}\n```\n\n")
                        f.write(f"**Suggested Fix:**\n```python\n{finding.suggestion}\n```\n\n")
                        f.write("---\n\n")
            
            # Detailed Findings by File
            f.write("## Detailed Findings by File\n\n")
            
            findings_by_file = defaultdict(list)
            for finding in sorted_findings:
                findings_by_file[finding.file_path].append(finding)
            
            for file_path in sorted(findings_by_file.keys()):
                file_findings = findings_by_file[file_path]
                f.write(f"### {file_path}\n\n")
                f.write(f"**Issues:** {len(file_findings)}\n\n")
                
                for finding in file_findings:
                    icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}[finding.severity]
                    f.write(f"- **Line {finding.line_num}** {icon} [{finding.category}] {finding.description}\n")
                    f.write(f"  - Code: `{finding.code_snippet}`\n")
                    f.write(f"  - Fix: {finding.suggestion}\n\n")
            
            # Recommendations
            f.write("## General Recommendations\n\n")
            f.write("1. **Address HIGH priority issues first** - These directly impact execution reliability\n")
            f.write("2. **Fix ATA-related issues** - Proper PDA derivation and RPC queries are critical\n")
            f.write("3. **Standardize on send_and_confirm_v0_tx** - Replace all raw submission calls\n")
            f.write("4. **Gate scaffold executors** - Prevent incomplete code from running in production\n")
            f.write("5. **Complete BuildResult migration** - Ensure all builders return BuildResult properly\n")
            f.write("6. **Fix ALT handling** - Proper address lookup table usage prevents transaction failures\n")
            f.write("7. **Migrate from solana-py to solders** - Use solders exclusively for consistency\n\n")
            
        print(f"[DIAGNOSTIC] Report written to {output_path}")
        
    def print_summary(self):
        """Print summary to stdout"""
        print("\n" + "="*80)
        print("EXECUTION PIPELINE DIAGNOSTIC SUMMARY")
        print("="*80)
        print(f"\nTotal Issues Found: {len(self.report.findings)}")
        print(f"  - HIGH severity:   {self.report.stats['HIGH']}")
        print(f"  - MEDIUM severity: {self.report.stats['MEDIUM']}")
        print(f"  - LOW severity:    {self.report.stats['LOW']}")
        
        print("\nTop Issues by Category:")
        categories = {}
        for finding in self.report.findings:
            categories[finding.category] = categories.get(finding.category, 0) + 1
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {category}: {count}")
        
        print("\nHigh Priority Files:")
        high_priority_files = defaultdict(int)
        for finding in self.report.findings:
            if finding.severity == "HIGH":
                high_priority_files[finding.file_path] += 1
        
        for file_path, count in sorted(high_priority_files.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {file_path}: {count} HIGH issues")
        
        print("\n" + "="*80)
        print("Full report generated: docs/PIPELINE_DIAGNOSTIC.md")
        print("="*80 + "\n")
        
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    # Get repository root (parent of tools directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print(f"[DIAGNOSTIC] Repository root: {repo_root}")
    
    # Create diagnostic instance
    diagnostic = ExecutionPipelineDiagnostic(str(repo_root))
    
    # Scan repository
    diagnostic.scan_repository()
    
    # Generate report
    report_path = repo_root / "docs" / "PIPELINE_DIAGNOSTIC.md"
    report_path.parent.mkdir(exist_ok=True)
    diagnostic.generate_report(str(report_path))
    
    # Print summary
    diagnostic.print_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
