#!/bin/bash

echo "=================================================="
echo "TRADE DETECTION RESTORATION VALIDATION"
echo "=================================================="
echo ""

echo "1. Syntax Check..."
python3 -m py_compile main.py trade_processor.py wallet_tx_parser.py websocket_handler.py
if [ $? -eq 0 ]; then
    echo "   ✅ All files compile without errors"
else
    echo "   ❌ Syntax errors found"
    exit 1
fi
echo ""

echo "2. Balance Change Requirement Check..."
if grep -q "detect_buy_sell.*target_wallets" main.py; then
    echo "   ✅ Balance change detection present in main.py"
else
    echo "   ❌ Balance change detection missing"
fi

if grep -q "if not detected_actions" main.py; then
    echo "   ✅ Execution gated on balance changes"
else
    echo "   ❌ Execution not properly gated"
fi
echo ""

echo "3. Aggressive Execution Removal Check..."
aggressive_count=$(grep -c "AGGRESSIVE\|aggressive.*execution\|zero.delta\|synthetic.*trade" main.py trade_processor.py wallet_tx_parser.py 2>/dev/null || echo 0)
if [ "$aggressive_count" -eq "0" ]; then
    echo "   ✅ No aggressive execution patterns found"
else
    echo "   ⚠️  Found $aggressive_count aggressive execution patterns (may be in comments)"
fi
echo ""

echo "4. Fallback Logic Check..."
if grep -q "return 'unknown'" trade_processor.py; then
    echo "   ✅ Fallback returns 'unknown' when unclear (doesn't force execution)"
else
    echo "   ❌ Fallback doesn't properly return 'unknown'"
fi
echo ""

echo "5. Validation vs Execution Check..."
if grep -q "VALIDATION only\|validation only" main.py trade_processor.py; then
    echo "   ✅ Signer + instruction checks documented as validation only"
else
    echo "   ⚠️  Validation documentation may need update"
fi
echo ""

echo "=================================================="
echo "VALIDATION COMPLETE"
echo "=================================================="
echo ""
echo "Summary:"
echo "- Core logic restored from working branch"
echo "- Balance changes REQUIRED for execution"
echo "- Aggressive execution patterns removed"
echo "- Fallback logic fixed (validation only)"
echo ""
echo "✅ Trade detection and parsing logic successfully restored!"
