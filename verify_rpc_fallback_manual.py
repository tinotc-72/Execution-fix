#!/usr/bin/env python3
"""
Simplified manual verification of the RPC fallback implementation.
This script validates the code structure without requiring all dependencies.
"""

import re


def verify_implementation():
    """Verify the implementation matches problem statement requirements"""
    print("\n" + "=" * 80)
    print("MANUAL VERIFICATION: RPC Fallback Implementation")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    print("\n1️⃣  Verifying _submit_via_rpc method")
    print("-" * 80)
    
    # Extract _submit_via_rpc method
    submit_rpc_match = re.search(
        r'async def _submit_via_rpc\(self, vtx\) -> str \| None:(.*?)(?=\n    async def |\n    def |\Z)',
        content,
        re.DOTALL
    )
    
    if submit_rpc_match:
        method = submit_rpc_match.group(0)
        print("✅ Method exists with correct signature")
        
        # Check for key implementation details
        checks = [
            ('raw = bytes(vtx)', 'Converts transaction to bytes'),
            ('"jsonrpc": "2.0"', 'Uses JSON-RPC 2.0 format'),
            ('"method": "sendTransaction"', 'Calls sendTransaction method'),
            ('base64.b64encode(raw).decode()', 'Encodes as base64'),
            ('httpx.AsyncClient(timeout=15.0)', 'Uses httpx with 15s timeout'),
            ('self._rpc_url', 'Posts to RPC URL'),
            ('sig = (data or {}).get("result")', 'Parses signature from result field'),
            ('[SUBMIT_RPC] sig=', 'Logs signature on success'),
            ('[SUBMIT_RPC] no result:', 'Logs error when no result'),
            ('[SUBMIT_RPC] error:', 'Logs exception on failure'),
        ]
        
        for pattern, description in checks:
            if pattern in method:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
    else:
        print("❌ Method not found!")
        return False
    
    print("\n2️⃣  Verifying send_and_confirm method")
    print("-" * 80)
    
    # Extract send_and_confirm method - simpler approach
    if 'async def send_and_confirm(self, vtx' in content:
        print("✅ Method exists")
        
        # Find the method content
        start_idx = content.find('async def send_and_confirm(self, vtx')
        # Find next method or end of class
        next_method_idx = content.find('\n    async def ', start_idx + 10)
        if next_method_idx == -1:
            next_method_idx = content.find('\n    def ', start_idx + 10)
        if next_method_idx == -1:
            next_method_idx = len(content)
        
        method = content[start_idx:next_method_idx]
        
        # Verify the execution order
        jito_pos = method.find('await self._submit_via_jito(vtx)')
        rpc_pos = method.find('await self._submit_via_rpc(vtx)')
        
        if jito_pos > 0 and rpc_pos > jito_pos:
            print("  ✅ Jito is tried before RPC (correct order)")
        else:
            print("  ❌ Execution order incorrect")
        
        # Check for key implementation details
        checks = [
            ('sig = await self._submit_via_jito(vtx)', 'Calls Jito first'),
            ('[EXECUTOR] Falling back to RPC submission', 'Logs RPC fallback warning'),
            ('sig = await self._submit_via_rpc(vtx)', 'Falls back to RPC'),
            ('[EXECUTOR] submission failed (Jito and RPC)', 'Logs total failure'),
            ('await self._confirm_with_retries(sig)', 'Confirms transaction'),
            ('[CONFIRM][FINAL] sig=', 'Logs final confirmation'),
        ]
        
        for pattern, description in checks:
            if pattern in method:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
    else:
        print("❌ Method not found!")
        return False
    
    print("\n3️⃣  Verifying submit_transaction uses new method")
    print("-" * 80)
    
    # Check submit_transaction
    submit_tx_match = re.search(
        r'async def submit_transaction\(self, vtx.*?\):(.*?)(?=\n    async def |\n    def |\Z)',
        content,
        re.DOTALL
    )
    
    if submit_tx_match:
        method = submit_tx_match.group(0)
        if '_submit_via_rpc' in method:
            print("  ✅ Uses _submit_via_rpc (not old _submit_to_rpc)")
        else:
            print("  ❌ Still using old method name")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    
    return True


def show_code_snippets():
    """Show the actual implementation snippets"""
    print("\n" + "=" * 80)
    print("CODE SNIPPETS: Implementation Details")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        lines = f.readlines()
    
    # Find and display _submit_via_rpc
    print("\n📝 _submit_via_rpc method:")
    print("-" * 80)
    in_method = False
    indent_count = 0
    for i, line in enumerate(lines, 1):
        if 'async def _submit_via_rpc' in line:
            in_method = True
            indent_count = len(line) - len(line.lstrip())
        
        if in_method:
            print(f"{i:3d}  {line.rstrip()}")
            
            # Stop at next method definition at same indentation level
            if i > lines.index([l for l in lines if 'async def _submit_via_rpc' in l][0]) + 1:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_count and 'def ' in line:
                    break
    
    # Find and display send_and_confirm
    print("\n📝 send_and_confirm method:")
    print("-" * 80)
    in_method = False
    indent_count = 0
    for i, line in enumerate(lines, 1):
        if 'async def send_and_confirm' in line:
            in_method = True
            indent_count = len(line) - len(line.lstrip())
        
        if in_method:
            print(f"{i:3d}  {line.rstrip()}")
            
            # Stop at end of file or next method
            if i > lines.index([l for l in lines if 'async def send_and_confirm' in l][0]) + 1:
                if line.strip() and not line.strip().startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_count and line.strip():
                        break


def main():
    """Run verification"""
    verify_implementation()
    show_code_snippets()
    
    print("\n" + "=" * 80)
    print("✅ MANUAL VERIFICATION COMPLETE")
    print("=" * 80)
    print("\nSummary of changes:")
    print("1. Renamed _submit_to_rpc → _submit_via_rpc")
    print("2. _submit_via_rpc now uses httpx (not aiohttp session)")
    print("3. _submit_via_rpc parses signature from JSON-RPC 'result' field")
    print("4. send_and_confirm logs '[EXECUTOR] Falling back to RPC submission'")
    print("5. send_and_confirm logs '[EXECUTOR] submission failed (Jito and RPC)'")
    print("6. All error cases have robust logging with [SUBMIT_RPC] prefix")
    print("7. Maintains Jito → RPC execution order")
    print()


if __name__ == "__main__":
    main()
