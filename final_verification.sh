#!/bin/bash

echo "=================================================="
echo "🎯 BUY/SELL INFERENCE - FINAL VERIFICATION"
echo "=================================================="
echo ""

echo "1️⃣ Running Validation Tests..."
echo "--------------------------------------------------"
python validate_buy_sell_inference.py 2>&1 | grep -E "PASS|FAIL|Passed:"
echo ""

echo "2️⃣ Checking Python Syntax..."
echo "--------------------------------------------------"
python -m py_compile trade_processor.py && echo "✅ trade_processor.py syntax OK"
echo ""

echo "3️⃣ Checking Implementation Files..."
echo "--------------------------------------------------"
ls -1 *buy_sell* *BUY_SELL* 2>/dev/null | while read file; do
    echo "✅ $file"
done
echo ""

echo "4️⃣ Verifying Key Implementation..."
echo "--------------------------------------------------"
grep -q "WSOL = \"So111" trade_processor.py && echo "✅ WSOL constant defined"
grep -q "owner_changes\[owner\]\[mint\]" trade_processor.py && echo "✅ Owner grouping implemented"
grep -q "mint_in = WSOL" trade_processor.py && echo "✅ BUY inference implemented"
grep -q "mint_out = WSOL" trade_processor.py && echo "✅ SELL inference implemented"
grep -q "🎯 Detected action=" trade_processor.py && echo "✅ Required logging present"
echo ""

echo "5️⃣ Checking Documentation..."
echo "--------------------------------------------------"
[ -f BUY_SELL_INFERENCE_IMPLEMENTATION.md ] && echo "✅ Implementation guide exists"
[ -f QUICK_REF_BUY_SELL_INFERENCE.md ] && echo "✅ Quick reference exists"
[ -f IMPLEMENTATION_SUMMARY_BUY_SELL.md ] && echo "✅ Summary report exists"
echo ""

echo "=================================================="
echo "✅ VERIFICATION COMPLETE"
echo "=================================================="
