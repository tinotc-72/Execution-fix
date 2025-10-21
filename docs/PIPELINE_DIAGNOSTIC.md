# Execution Pipeline Diagnostic Report

**Generated:** 2025-10-21 04:53:31

## Executive Summary

**Total Issues Found:** 402

- 🔴 HIGH severity: 108
- 🟡 MEDIUM severity: 26
- 🔵 LOW severity: 268

## Issues by Category

- **SOLANA_PY_IMPORT:** 268 issues
- **RAW_SUBMISSION:** 57 issues
- **NONE_RETURN:** 37 issues
- **MISSING_BUILD_ALTS:** 22 issues
- **MISSING_ALTS_COMPILE:** 12 issues
- **SCAFFOLD_EXECUTOR:** 2 issues
- **ATA_EXISTS_USAGE:** 2 issues
- **ATA_PLACEHOLDER:** 1 issues
- **ATA_EXISTS_BOOLEAN:** 1 issues

## Prioritized Remediation List

### 🔴 HIGH Priority

#### RAW_SUBMISSION: 1_Jupiter.py:78

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
sig = await self.client.send_transaction(tx, opts=TxOpts(skip_preflight=True, max_retries=1))
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:157

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:307

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:471

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:844

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
signature = await self.client.send_transaction(transaction, opts=opts)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:940

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
buy_sig = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:983

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
sell_sig = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: 1_Pump.fun.py:1229

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: CRITICAL_ATA_FIX.py:186

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: EMERGENCY_ATA_PATCH.py:194

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: base_solana_executor.py:174

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: clmm_copy_executor.py:137

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: clmm_execute_trade.py:319

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_execute_trade.py:471

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_execute_trade.py:651

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_execute_trade.py:697

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_execute_trade.py:761

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_hybrid_copy_executor.py:207

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_jupiter_hybrid.py:173

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_jupiter_hybrid.py:270

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_jupiter_hybrid.py:356

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: clmm_jupiter_trader.py:144

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: cpmm_copy_executor.py:288

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: cpmm_copy_executor.py:327

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: create_observation.py:91

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: create_observation_final.py:136

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: create_observation_official.py:130

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### MISSING_ALTS_COMPILE: demo_alt_fetch.py:200

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
print("    new_message = Message.new_with_blockhash(")
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### RAW_SUBMISSION: direct_pumpfun.py:80

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.rpc_client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: direct_pumpfun.py:148

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.rpc_client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: generic_executor.py:85

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
send_result = await self.rpc_client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: hybrid_clmm_trader.py:155

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: hybrid_clmm_trader.py:254

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: hybrid_clmm_trader.py:332

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: hybrid_trader.py:215

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: hybrid_trader.py:334

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: initialize_observation.py:116

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: jupiter_copy_bot.py:374

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: jupiter_copy_bot.py:506

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(tx, opts=opts)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: jupiter_copy_executor.py:250

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:253

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:283

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:286

**Description:** Function 'execute_copy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:345

**Description:** Function 'execute_buy_copy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:351

**Description:** Function 'execute_buy_copy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:360

**Description:** Function 'execute_buy_copy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_copy_executor.py:363

**Description:** Function 'execute_buy_copy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: jupiter_trade_executor.py:403

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
sig = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: jupiter_trade_executor.py:472

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
sig = await self.client.send_transaction(tx, opts=opts)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: jupiter_trader.py:375

**Description:** Function 'execute_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_trader.py:379

**Description:** Function 'execute_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_trader.py:394

**Description:** Function 'execute_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_trader.py:415

**Description:** Function 'execute_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: jupiter_trader.py:419

**Description:** Function 'execute_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: meteora_copy_executor.py:553

**Description:** Function 'build_and_submit_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: meteora_copy_executor.py:564

**Description:** Function 'build_and_submit_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: meteora_copy_executor.py:575

**Description:** Function 'build_and_submit_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: meteora_copy_executor.py:586

**Description:** Function 'build_and_submit_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: meteora_copy_executor.py:592

**Description:** Function 'build_and_submit_sell' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: mev_pumpfun_executor.py:290

**Description:** Function 'execute_sell_all' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: mev_pumpfun_executor.py:300

**Description:** Function 'execute_sell_all' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: orca_manual_trader.py:183

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: phoenix_manual_trader.py:180

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(tx)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: pump_router_executor.py:204

**Description:** Function 'execute_router_buy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: pump_router_executor.py:208

**Description:** Function 'execute_router_buy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: pump_router_executor.py:267

**Description:** Function 'execute_router_buy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: pumpfun_copy_executor_old.py:190

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(tx, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_copy_executor_old.py:369

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_copy_executor_old.py:650

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_copy_executor_old.py:963

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_executor.py:129

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_executor.py:371

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_executor.py:533

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_trade_executor.py:159

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: pumpfun_trade_executor.py:427

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: raydium_clmm_copy_executor.py:407

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: raydium_clmm_trade_executor.py:156

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await self.client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: raydium_copy_executor.py:888

**Description:** Function 'try_raydium_buy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_copy_executor.py:891

**Description:** Function 'try_raydium_buy' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: raydium_official_structure.py:86

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
result = await client.send_transaction(tx, opts=TxOpts(skip_preflight=True))
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### NONE_RETURN: raydium_trade_executor.py:275

**Description:** Function 'execute_buy_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:378

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:398

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:453

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:465

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:469

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:517

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:556

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### NONE_RETURN: raydium_trade_executor.py:560

**Description:** Function 'execute_sell_trade' declares BuildResult return type but returns None

**Code:**
```python
return None
```

**Suggested Fix:**
```python
Return BuildResult(ok=False, tx=None, reason='...') instead of None
```

---

#### RAW_SUBMISSION: raydium_v4_amm_trader.py:392

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: real_clmm_executor.py:165

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = await self.client.send_transaction(transaction)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: send_mev_router_example.py:52

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
response = client.send_transaction(transaction, sender)
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: test_integration_submit_methods.py:74

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
'JitoClient call': 'await self.jito_client.send_transaction(signed_tx_bytes)' in method_content,
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: test_submit_methods.py:27

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
"await self.jito_client.send_transaction(signed_tx_bytes)",
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### RAW_SUBMISSION: test_submit_methods.py:213

**Description:** Using raw submission call instead of unified send_and_confirm_v0_tx

**Code:**
```python
"result = await self.jito_client.send_transaction(signed_tx_bytes)",
```

**Suggested Fix:**
```python
Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:240

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
"""Check MessageV0.compile / VersionedTransaction creation for missing ALTs"""
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:284

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
"""Check if with_compute_budget is used before MessageV0.compile"""
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:286

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
if "MessageV0.compile" in line:
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:305

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
description="with_compute_budget called AFTER MessageV0.compile (should be before)",
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:307

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
suggestion="Call with_compute_budget BEFORE MessageV0.compile: ixs = with_compute_budget(ixs, ...); message = MessageV0.compile(...)"
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:409

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
# Look for MessageV0.compile or transaction building
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:410

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
has_message_compile = "MessageV0.compile" in content or "Message.new_with_blockhash" in content
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:416

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
if "MessageV0.compile" in line or "Message.new_with_blockhash" in line:
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: tools/diagnose_execution_pipeline.py:427

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
description="MessageV0.compile without apparent blockhash fetch",
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: transaction_cloner.py:333

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
new_message = Message.new_with_blockhash(
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### MISSING_ALTS_COMPILE: transaction_cloner.py:384

**Description:** MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter

**Code:**
```python
new_message = Message.new_with_blockhash(
```

**Suggested Fix:**
```python
Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])
```

---

#### ATA_PLACEHOLDER: utils/ata.py:42

**Description:** Placeholder ATA PDA derivation returns mint instead of proper PDA

**Code:**
```python
return mint  # placeholder!
```

**Suggested Fix:**
```python
Replace with: seeds = [bytes(owner), bytes(SPL_TOKEN_PROGRAM_ID), bytes(mint)]; ata, _ = Pubkey.find_program_address(seeds, SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID); return ata
```

---

#### ATA_EXISTS_BOOLEAN: utils/ata.py:70

**Description:** ensure_ata function uses 'exists' boolean parameter instead of RPC query

**Code:**
```python
def ensure_ata_for(owner: Pubkey, mint: Pubkey, payer: Pubkey, exists: bool) -> List[Instruction]:
```

**Suggested Fix:**
```python
Replace 'exists' parameter with actual RPC query: response = await rpc_client.get_token_accounts_by_owner(owner, {'mint': str(mint)}); exists = response.value is not None and len(response.value) > 0
```

---

### 🟡 MEDIUM Priority

#### MISSING_BUILD_ALTS: execution_coordinator.py:631

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
kwargs['addressTableLookups'] = required_accounts.get('lookup_tables', [])
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: full_output.py:3

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-06 18:55:55,427 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': '41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 55, 427124, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 393367, 'costUnits': 403892, 'err': None, 'fee': 310654, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [2, 16, 1], 'data': '3awy1w6vdVeX', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [39, 23, 24, 25, 15, 16, 41, 44], 'data': 'J9A6eM58XaLWXKsmqBa2NbWp', 'programIdIndex': 43, 'stackHeight': 2}, {'accounts': [16, 25, 39], 'data': '3JpGTWoUyaDu', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [24, 15, 23], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42], 'data': '59p8WydnSZtV29EZJ5EPHbUYgwcyEPuwe7SXrhmNB83k1QhfcFC71rtXHa', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [15, 17, 39], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [19, 3, 21], 'data': '3Z6sYHBgK6Ky', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35], 'data': '59p8WydnSZtSYqyRFuqQPv9H538j1vw22B54xWsoUsCA53MawYHzdhGF2x', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [16, 14, 39], 'data': '3JvGaqeJM4Hd', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [12, 3, 13], 'data': '3YMxHtDwKwzF', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28], 'data': 'wZRp7wZ3czsp8TiBYg9eUvG8CbxCoDYm42UzZBycSgh5Z3PVpMQRnwuz', 'programIdIndex': 46, 'stackHeight': 2}, {'accounts': [16, 27, 39], 'data': '3QJJ2xEUe3q1', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [32, 3, 26], 'data': '3FDG456PfyrP', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [37], 'data': '4KbP49BdVApjtHuXZdNzDMRzUrFad32msbNDnEYAYPQjzkC9HQWsZg1bqYcV42HqWmzj35W86LMLAaDsXdQGXr8ABcyjSB2Yy87SyzmryVoMFg2uka2ui24a42mTckbKcFwx3Y2Eb9shgn5HevkmfzSeLBWjMYtYsaPqPgxPAghFzqsn88EC9wz8HdnuK9FYZjzy5wnjFY3g8pXfG8cLUUWa3V2U2YjRfFBCC35KxSZrwp7j7rSBAvVyRuoyaMG4xEpfdd2jLcJMMwcipiYk9YxfgYAgNgogzLaApf2JjMX59N2GBCHAQFQDYCQYMEvao1PwTBGz9hAZC562sXP9oJLAkrmUQz4Y3JNyL1A28SLxuPuK8tnf5yKx4mwe8rWLKv1S1DfEUbQrq4xP9vmgFEJJZ5i4QX5kyyJbcikf8Q7Bz4jKf4X8HDWNc6YigxvzPMBhT8X82kqsNojDZ', 'programIdIndex': 8, 'stackHeight': 2}, {'accounts': [2, 16, 1], 'data': '3avKVPuic5LT', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [3, 5, 39], 'data': '3uktGuL5uriK', 'programIdIndex': 41, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'GrzzQpVYkCoDnXGVpANW9iDGJk9EbcJJRj9FgY3GeVNm', 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'jitodontfront11111111111JustUseJupiterU1tra', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'FovDWEsftJv4X1EfapqVwG2VDcEDG2vsa7vaje3qAo56', 'SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe', 'Sysvar1nstructions1111111111111111111111111', 'A1BBtTYJd4i3xU8D6Tc2FzU6ZN4oXZWXKZnCxwbHXr8x', 'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK'], 'writable': ['4ZEwCEENfgAqzbyKLBDLZxSeixbKpZknirkWLFVcaLBw', '7yUHJWhvRnspqZKezhVHxJmsLLcfNyDn4dhYTCNNPTxe', '8z95LBWmSRKkQv1XPczvN6s2Fc3Rk5X6oi1ueW3nndBV', 'Bc1Ki733Cv9Fu2qGwar3n6EjQBofTpwrVAg2uSo5uLUV', 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'Efe7p9ZEbd99dCoGU3mbYbRRxU9tJuSmHX6jYDtbKC4x', '2p29nqD7DN1PczBMmgrFdtYKTfv6rJ7H3yMut4eu7nYT', '5SPztfEn1VAaWDBAXjQKwVrGbr6e8g3F6JJnUc9eCuSe', '2rJJP6RAyfo5HaoR9T6SDjWU885RkQBH3PyRpnoFrkDU', '3aSDFqAyFJPniaZpJf7Vn9PxZqT6dcuxzg9HXwWkbpVP', 'E83CnZbE1cz2ww5rqYuvWmAdMwWh3ZkJJcrbo49TaaGU', 'E9TL1PrwPxpdvMGjSXJQidJSmdBG4LYJJWoHDF5gSVv2', 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'H1j2gqzW61MrdjJsu6s5gamLq9wcKkinw1a7GWyjdd6k', 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'CTaDZW2LhvHPRnA9JWcZF8R5y2mpkV2RcHAXyEoKLbzp', 'JHVJLsPsbzNW8JP8cPYmrwfzD2M9aHXdFHSjeeCDERu', '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', '4LCiADXLEBW2JepG5iue3iTB3ozXb3YLGqheQNEWTSAY', '666Sz6bUgQwS2vgGDkPSwfqSsxtmBUh7Zvya6p2nkTJF', '7B5dskPoP5r2vXPDJgzvwCNTtuYwXVgV6KEeaWn8o2Ph', 'C86icgvRMBRHZWnTFjHnLh4o3BVroZYx5CHueZzAqByo', 'DnrPPNMp3ZqcCcrF8LEPLiXBiwMDPwELKFAy8ToHwUsD', 'FSGuR2PvoUqZvuQNxQVgyUeP4Mcsa89JxeqvAFWqSJdo', 'GwXt2aQ8gT39XT7HhcSdiDyTdxNgLY3pyJQm56mcbzWE']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121763506924, 9204256, 2039280, 2039280, 20152947666, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8769954653, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599752863345, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2430379783', 'decimals': 6, 'uiAmount': 2430.379783, 'uiAmountString': '2430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1290180175863', 'decimals': 6, 'uiAmount': 1290180.175863, 'uiAmountString': '1290180.175863'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3329485185848465', 'decimals': 6, 'uiAmount': 3329485185.848465, 'uiAmountString': '3329485185.848465'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '519465211363', 'decimals': 6, 'uiAmount': 519465.211363, 'uiAmountString': '519465.211363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4059641614', 'decimals': 6, 'uiAmount': 4059.641614, 'uiAmountString': '4059.641614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8767915373', 'decimals': 9, 'uiAmount': 8.767915373, 'uiAmountString': '8.767915373'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4072118737060', 'decimals': 6, 'uiAmount': 4072118.73706, 'uiAmountString': '4072118.73706'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599731804056', 'decimals': 9, 'uiAmount': 7599.731804056, 'uiAmountString': '7599.731804056'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713647633243', 'decimals': 6, 'uiAmount': 1713647.633243, 'uiAmountString': '1713647.633243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '751162111', 'decimals': 6, 'uiAmount': 751.162111, 'uiAmountString': '751.162111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3625092093786', 'decimals': 6, 'uiAmount': 3625092.093786, 'uiAmountString': '3625092.093786'}}], 'preBalances': [121763893741, 9204256, 2039280, 2039280, 20152871503, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8559129552, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599963688446, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3430379783', 'decimals': 6, 'uiAmount': 3430.379783, 'uiAmountString': '3430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18533267719', 'decimals': 6, 'uiAmount': 18533.267719, 'uiAmountString': '18533.267719'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3330667810953218', 'decimals': 6, 'uiAmount': 3330667810.953218, 'uiAmountString': '3330667810.953218'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '518536327363', 'decimals': 6, 'uiAmount': 518536.327363, 'uiAmountString': '518536.327363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4058441614', 'decimals': 6, 'uiAmount': 4058.441614, 'uiAmountString': '4058.441614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8557090272', 'decimals': 9, 'uiAmount': 8.557090272, 'uiAmountString': '8.557090272'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4135662209305', 'decimals': 6, 'uiAmount': 4135662.209305, 'uiAmountString': '4135662.209305'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599942629157', 'decimals': 9, 'uiAmount': 7599.942629157, 'uiAmountString': '7599.942629157'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713597693243', 'decimals': 6, 'uiAmount': 1713597.693243, 'uiAmountString': '1713597.693243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '731186111', 'decimals': 6, 'uiAmount': 731.186111, 'uiAmountString': '731.186111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3650570424932', 'decimals': 6, 'uiAmount': 3650570.424932, 'uiAmountString': '3650570.424932'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', '5ht281axHQXoQ2PWD6vrxxnHEa8TmsLuzs7XTDnmTdCt', '7QRKuCbdjxRjno55LE1GGFVKqxeFUWeNtUaLQ4a9Gz9X', '9fBpwxcudpLyJskhiiKmU8wPszeUuCB8sSjhPi44QuFb', 'B95oUgde4SfoekubbV1hbFanLBRV7UL26zXqcZZhHdrx', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'], 'addressTableLookups': [{'accountKey': '2z84tgaUYNWMwotQjmSpRygdH96m5M5VpUqZQH1L24UF', 'readonlyIndexes': [70, 68, 12], 'writableIndexes': [67, 64, 65, 66, 58, 63]}, {'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 40, 11, 1, 20], 'writableIndexes': [32, 49]}, {'accountKey': 'DWSgR97yTc3WENhkddFBkoBsute6mKpaJ5Kkfix8KWXb', 'readonlyIndexes': [225], 'writableIndexes': [219, 229, 188, 227, 222, 223]}, {'accountKey': 'EE8XintbVcFLm3CR3rNLfW5WcBKDtsniQwLKsWz3enYi', 'readonlyIndexes': [168, 173], 'writableIndexes': [169, 170, 171]}, {'accountKey': 'JBMZHmsCUZEfXpNPm4N1XQ2seJbDo3CFSfmQjK4mShDh', 'readonlyIndexes': [34, 40], 'writableIndexes': [37, 29, 38, 35, 33, 41, 39, 31]}], 'header': {'numReadonlySignedAccounts': 1, 'numReadonlyUnsignedAccounts': 3, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'KGAnEb', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [], 'data': '3QZwSzAJHXSo', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [39, 1, 2, 16, 3, 5, 38, 34, 41, 41, 37, 8, 16, 43, 39, 23, 24, 25, 15, 16, 41, 44, 36, 41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42, 36, 41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35, 46, 39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28, 8, 40], 'data': '2uadBoC4kUfkSytM1gJGnMJKGK8Uu9K455iqA8iRquZaLonKccX4BABoNf9v5VVL7q1N21BztbkGU7cw', 'programIdIndex': 8, 'stackHeight': 1}, {'accounts': [0, 4], 'data': '3Bxs4No5VVsho7hh', 'programIdIndex': 6, 'stackHeight': 1}], 'recentBlockhash': 'EZUJNZw94LezE4g9mf2Ku8FJ1dkMqyRQ4ieEUxBWnhMj'}, 'signatures': ['41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', '3pXHMYvd5xKeyxUMUNNPEWK2Meu6Kwnb3HYkFdNW4dbpY1dN72nL1e75H1oX8BrWfoNgRXz6gbpcW1RLttDavnGt']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: full_output_I.py:93

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-07 17:14:40,238 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': '2WdPgL6BQMDtYkmZnVKPCUpdxV8NnQcvvJ7KCwcdDcmYDX749LmA5z26ThVNchy6RPvusn9pXh7Gz5n8Jiahgv89', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 193054 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: 2xZ84zrhN1YTP9LmrgIw+WTDZUb11jWFmyBjlf69q5XGIxwAAAAAABSUKRYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 138328 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 132262 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 54935 of 181109 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 114425 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 108608 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/uW6GCBOJyhzLYupFgDTqgrWfMy3sZsErvz0sUXMNh+8m0O00xeDnPr+KH1bD1V2cVrqHHbJe7iXRF+vmW3fGN5Ucd2/T74cJwEbZ9oaJ31u0Nm/LcdKppcJDcAAeFSusgjDGSoLLvptLbVdn3hF3e9HVYSX54eAxcJmWVvl+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9GcYyX54eAxcDwTSPl+0ZYzm8cCt0LXR76s7xbZxcUGQajN1aDW/WV4PgxQuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 39154 of 123133 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]', 'Program log: ray_log: A2+2ET0AAAAAAAAAAAAAAAACAAAAAAAAAGhChbwAAAAAqHhQaykAAACsdy882KIAADyV+CHuAAAA', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66410 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 59205 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 26733 of 80600 compute units', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 52094 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 50191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 43488 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 159138 of 197850 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 PJX4Ie4AAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 7, 16, 14, 40, 237716, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 159588, 'costUnits': 167043, 'err': None, 'fee': 475325, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [3, 2, 1], 'data': '3mMeLYZHv31q', 'programIdIndex': 31, 'stackHeight': 2}, {'accounts': [28, 21, 32, 11, 19, 20, 2, 18, 33, 29, 31, 31, 25], 'data': 'KdeEDKHxrmWGNkvCP6n5cEh5', 'programIdIndex': 34, 'stackHeight': 2}, {'accounts': [2, 19, 28], 'data': '3mMeLYZHv31q', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [20, 18, 21], 'data': '3dm7JxVbCvTH', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [14, 16, 15, 12, 13, 18, 17, 28, 31, 25], 'data': '4acasGboxW9ycmr5GDkkPdR', 'programIdIndex': 26, 'stackHeight': 2}, {'accounts': [18, 15, 28], 'data': '3dm7JxVbCvTH', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [13, 17, 13], 'data': '3Y9JSGqCfGmD', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [31, 24, 35, 24, 23, 22, 24, 24, 24, 24, 24, 24, 24, 24, 17, 5, 28], 'data': '69JXzprawbsnmbefSGhpw9Z', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [17, 23, 28], 'data': '3Y9JSGqCfGmD', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [22, 5, 35], 'data': '3PbKaghc6T5y', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [27], 'data': '2C3FxF4wtCk1WPKYcjNvfKxBQp63XmmB7XbdK96PrfUPSGPAGM3Y2JsW2y2rYDAKkUArJC9qEWv2VrfDPx3yPdtwdE2BYpVEhnNZpE1iXZQxVMbXXmB39j2FDqHNnSou7GnJVKpNFqwtyyKhuZitXdw1fsYGtcFNUTxAWP4sboxrfRbiAKLXvXBUVuPncUUse3HzK1dh6kf8FX94UMsJSYQgFh3WXLHRsMgRWGA5SgKDccryGpdG82w5vfQ62Sv5BRYh5zi9ZJLH7BhwgiHeuzz6FWJog2pvB9U3DAc3sK1poBp1UbbWjtEGaaSMzwwdSuSZJDpCs9cKwHuU11BbWPstezw1mLczCw3D', 'programIdIndex': 10, 'stackHeight': 2}, {'accounts': [3, 2, 1], 'data': '3W1GURjhLEgX', 'programIdIndex': 31, 'stackHeight': 2}, {'accounts': [5, 6, 28], 'data': '3PbKaghc6T5y', 'programIdIndex': 31, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['Sysvar1nstructions1111111111111111111111111', 'ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'CyCUgmaCYUZxbux3J2svDzxSryVFMtZNPrnMKS41nc4G', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8'], 'writable': ['8943FQrCirbp2kNk8cVKS5P7vjNzhas3L9fDoqpnv8mw', 'CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU', 'f2FsCiguf172T9achZzJcTjJuM9BLf5nmf18WKaaWUZ', 'fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1', 'GC2yqyD6ZYnAXc8DNy4d7uiYnQ9TBhZBA4WMPbsMKUxK', 'EUvpCGh4qiMtq9wKgp28f9Bjv5Xz2WJqrM83XmYAqkEq', 'FbruxBVHi463Agw2B3Vy27cBkGnEN5g1f4NcHe3REXfe', '5bHD9xdEzJdkVuhs54mGPC9BZgUshqgMg4tqmTwhWggc', 'ARWaajRJyF6PKQryJ4HLzLBfTWM2qmVQUQVtBjk6PgPc', 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', '39fBZjAdwAxwTvrTW5RLDM7zTTRupYE7UJJvuuCJrnfg', 'Dqsmrr3x4JkffT7J9rpi8D3CupVyLCyHvLEbkHGpPBwB', 'DrgGbUa6SMEDeY2YbwgfoKKNx5rLRG5kNkNgunxzp4G3']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 193054 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: 2xZ84zrhN1YTP9LmrgIw+WTDZUb11jWFmyBjlf69q5XGIxwAAAAAABSUKRYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 138328 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 132262 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 54935 of 181109 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 114425 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 108608 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/uW6GCBOJyhzLYupFgDTqgrWfMy3sZsErvz0sUXMNh+8m0O00xeDnPr+KH1bD1V2cVrqHHbJe7iXRF+vmW3fGN5Ucd2/T74cJwEbZ9oaJ31u0Nm/LcdKppcJDcAAeFSusgjDGSoLLvptLbVdn3hF3e9HVYSX54eAxcJmWVvl+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9GcYyX54eAxcDwTSPl+0ZYzm8cCt0LXR76s7xbZxcUGQajN1aDW/WV4PgxQuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 39154 of 123133 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]', 'Program log: ray_log: A2+2ET0AAAAAAAAAAAAAAAACAAAAAAAAAGhChbwAAAAAqHhQaykAAACsdy882KIAADyV+CHuAAAA', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66410 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 59205 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 26733 of 80600 compute units', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 52094 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 50191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 43488 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 159138 of 197850 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 PJX4Ie4AAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [64909369989, 9395859, 2039680, 2039280, 19719074822, 2039280, 2039280, 1, 8995008256, 1, 2729681025, 7298979842, 8352000, 2020397051241, 52784640, 2079311, 8352000, 2140321390, 2039381, 2039280, 2039280, 12917764, 2039280, 178920705287, 14124800, 0, 1141440, 3596047, 156269933, 418700053208, 1000004, 5065007155, 2060160, 141900721504, 1141441, 32327908436, 2500659979], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '239208668', 'decimals': 6, 'uiAmount': 239.208668, 'uiAmountString': '239.208668'}}, {'accountIndex': 3, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 5, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '19114626117', 'decimals': 6, 'uiAmount': 19114.626117, 'uiAmountString': '19114.626117'}}, {'accountIndex': 6, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1022772155708', 'decimals': 6, 'uiAmount': 1022772.155708, 'uiAmountString': '1022772.155708'}}, {'accountIndex': 13, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2020394905405', 'decimals': 9, 'uiAmount': 2020.394905405, 'uiAmountString': '2020.394905405'}}, {'accountIndex': 15, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '228619882592', 'decimals': 6, 'uiAmount': 228619.882592, 'uiAmountString': '228619.882592'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2138278905', 'decimals': 9, 'uiAmount': 2.138278905, 'uiAmountString': '2.138278905'}}, {'accountIndex': 18, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '433400576', 'decimals': 6, 'uiAmount': 433.400576, 'uiAmountString': '433.400576'}}, {'accountIndex': 19, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '408027626684', 'decimals': 6, 'uiAmount': 408027.626684, 'uiAmountString': '408027.626684'}}, {'accountIndex': 20, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '403455858852', 'decimals': 6, 'uiAmount': 403455.858852, 'uiAmountString': '403455.858852'}}, {'accountIndex': 22, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '178026834223728', 'decimals': 6, 'uiAmount': 178026834.223728, 'uiAmountString': '178026834.223728'}}, {'accountIndex': 23, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '178918666007', 'decimals': 9, 'uiAmount': 178.918666007, 'uiAmountString': '178.918666007'}}], 'preBalances': [64909962645, 9395859, 2039680, 2039280, 19718957491, 2039280, 2039280, 1, 8995008256, 1, 2729681025, 7298979842, 8352000, 2021421622232, 52784640, 2079311, 8352000, 2140321390, 2039381, 2039280, 2039280, 12917764, 2039280, 177896134296, 14124800, 0, 1141440, 3596047, 156269933, 418700053208, 1000004, 5065007155, 2060160, 141900721504, 1141441, 32327908436, 2500659979], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '238820218', 'decimals': 6, 'uiAmount': 238.820218, 'uiAmountString': '238.820218'}}, {'accountIndex': 3, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '228500000', 'decimals': 6, 'uiAmount': 228.5, 'uiAmountString': '228.5'}}, {'accountIndex': 5, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '19114626117', 'decimals': 6, 'uiAmount': 19114.626117, 'uiAmountString': '19114.626117'}}, {'accountIndex': 6, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 13, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2021419476396', 'decimals': 9, 'uiAmount': 2021.419476396, 'uiAmountString': '2021.419476396'}}, {'accountIndex': 15, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '228391601359', 'decimals': 6, 'uiAmount': 228391.601359, 'uiAmountString': '228391.601359'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2138278905', 'decimals': 9, 'uiAmount': 2.138278905, 'uiAmountString': '2.138278905'}}, {'accountIndex': 18, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '433400576', 'decimals': 6, 'uiAmount': 433.400576, 'uiAmountString': '433.400576'}}, {'accountIndex': 19, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '407799515134', 'decimals': 6, 'uiAmount': 407799.515134, 'uiAmountString': '407799.515134'}}, {'accountIndex': 20, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '403684140085', 'decimals': 6, 'uiAmount': 403684.140085, 'uiAmountString': '403684.140085'}}, {'accountIndex': 22, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '179049606379436', 'decimals': 6, 'uiAmount': 179049606.379436, 'uiAmountString': '179049606.379436'}}, {'accountIndex': 23, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '177894095016', 'decimals': 9, 'uiAmount': 177.894095016, 'uiAmountString': '177.894095016'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', '4jVFS4iFYaYL4G94Be9eKejW3aNVmsK73DgyDxeF1zeb', '8TGRD1ZSLGGpWnB6A218DZAZdDWJJQz3cT8qnfePRSiK', 'AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw', 'Dp8YMGEG9k9mFy56QtbEBQoKG2fFjrcYmchFag14LK2c', 'G46QTpwZMjBCemM739xa61h7tfKym88omEE4bcetMHRM', '11111111111111111111111111111111', '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ'], 'addressTableLookups': [{'accountKey': '2iUJxrahG52bPemKUWw8CSceESan6K75M6XwfuRmtjcS', 'readonlyIndexes': [42, 44], 'writableIndexes': [43, 40, 45, 38, 41]}, {'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 12, 40, 1, 20], 'writableIndexes': [33, 50]}, {'accountKey': 'Cebe9n1UmhceqQMWpZpkLHTGUZSks33XTzM62n984s8Z', 'readonlyIndexes': [146, 149, 147], 'writableIndexes': [153, 145, 150]}, {'accountKey': 'HQEo1L5u8hDiqFYmHgUwz3WLa1h1t5mAwgB54FZEB38g', 'readonlyIndexes': [9, 4], 'writableIndexes': [159, 160, 156]}], 'header': {'numReadonlySignedAccounts': 1, 'numReadonlyUnsignedAccounts': 5, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'EEzc6T', 'programIdIndex': 9, 'stackHeight': 1}, {'accounts': [], 'data': '3NxujFR17Tbu', 'programIdIndex': 9, 'stackHeight': 1}, {'accounts': [28, 1, 3, 2, 5, 6, 33, 8, 31, 31, 27, 10, 2, 34, 28, 21, 32, 11, 19, 20, 2, 18, 33, 29, 31, 31, 25, 26, 14, 16, 15, 12, 13, 18, 17, 28, 31, 25, 36, 31, 24, 35, 24, 23, 22, 24, 24, 24, 24, 24, 24, 24, 24, 17, 5, 28, 30], 'data': 'CQ7Z1iuQV9mhfcuNXTLayQHmFDFwAH9L8WzN2mrgXgbuW7dmCJcV1uEioaubey277fLsuU', 'programIdIndex': 10, 'stackHeight': 1}, {'accounts': [0, 4], 'data': '3Bxs4EsX5CFe8UZD', 'programIdIndex': 7, 'stackHeight': 1}], 'recentBlockhash': 'B7n7K3ZPUi8toxgCH14jZx5r91jPt9mPWE12atTCS8wV'}, 'signatures': ['2WdPgL6BQMDtYkmZnVKPCUpdxV8NnQcvvJ7KCwcdDcmYDX749LmA5z26ThVNchy6RPvusn9pXh7Gz5n8Jiahgv89', 'dqJgwbh2tHS7WUPEW4UaaFscV7SqYUUJoXEW85k5RBACu2FF786vFes833fsKoiWS1i4SuAfmzme8tRMT2QBaw7']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: full_output_II.py:3

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-06 18:55:20,053 - execution_coordinator - ERROR -    Input params: token_mint=7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk, source_wallet=suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK, trade_info={'signature': 'kGo2toyarf9z8UX2ajqcG3vU8JEcjXhfQYLeGceY9GjGmbtThC8gStH6MeBu1YAwuweWT1j6ohdWHeMT1HRqjYT', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 258345 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 261903 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]', 'Program log: Instruction: SellExactIn', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [3]', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 2039 of 216326 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program data: vdt/007mYe4v729nUnxNTIPERAhplCfJfDf9y6UhzLaf2npUDDGGIwB4xftR0QIAY3EOPunPAwDbGfgGAQAAAJyTbxmx+AAA1uHtWQAAAAA2E3sOOPcAALpIN1kAAAAAZoD0CnkBAABsObQAAAAAAN50AAAAAAAAc9MBAAAAAABfFwAAAAAAAAAAAAAAAAAAAQAB', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 210792 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 201525 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 186515 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 177191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 78407 of 247148 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh7lNA0AAAAAAPl7JhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 121358 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 115292 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 52182 of 161347 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp invoke [2]', 'Program log: 🦐', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 83284 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 77384 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: uzk28I9BxQZ484fWSzqZ3uRB544IUuDeeH1C4MV62fQcrneXpYLIS/F1G4rvWKU8C5OQGVO7h+OudgDex33l1UUKp5Q6jO/Vv5UvDS6eN94wSzulVKGgC/xW3GTCeByOgWtRMH78x2t9mKcEx0+H2l804ruYvH+6HFAqZ4NXRe6wKmcoKoYNVkN7vUR2RfKpWktR95FdWO+Y8MZnn1dZ7wHb14bvP17vnvDAZ5lXX++d8MNnmldc75zwwmebV13v9aDQ1LxWUu/dQhrzHVdT73AGN2WWV1DvuLJ6Z5dXUe+aFmDdCVZW737zyGeRV1fvlfDLZ5JXVO+V8Mpnk1dV7w==', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp consumed 34268 of 106189 compute units', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 70153 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4735 of 68079 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 192640 of 255163 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 L4PGAgAAAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 62523 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 19, 753362, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 202745, 'costUnits': 210206, 'err': None, 'fee': 814009, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [0, 2], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 15, 'stackHeight': 2}, {'accounts': [2, 27], 'data': '6QR9nxorLs8pns5qcUs55CVfrLWHMQf92wS29j4F7zpMp', 'programIdIndex': 14, 'stackHeight': 2}]}, {'index': 3, 'instructions': [{'accounts': [1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 15, 8, 9], 'data': 'B3F1THDgKfWQNoqGkJRTMRi3faUjyQLsQoWRt9HLviQF', 'programIdIndex': 29, 'stackHeight': 2}, {'accounts': [31], 'data': 'EwDfpErTWwQhCAycT1hw3kgHYnu5XfSffnwsXbjvzoi62MCw8U9cB97RyMStDmh9HVqRzgbgjG1bcXcbRvTNifx9K118nrFjmhwTxUKbx2Z5UZbUHGJGDbbX9d6VnDAzcySaj2SWmkXaqewAFqq8EvVxczotqjKhjWSyhHT6a1Qonwmbg1oTp7VfYj3mFbGVUcySmbzxRFKRi1tKpzhN', 'programIdIndex': 29, 'stackHeight': 3}, {'accounts': [3, 16, 6, 1], 'data': 'hQd6eFvBGU7RP', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 5, 30], 'data': 'hUr6YwLadcviq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 8, 30], 'data': 'haTUQVQeEbAtu', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 9, 30], 'data': 'hK9e7r43JdfeV', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34], 'data': 'JrgsXFj1RYPjW8Y8GT2wMrgf', 'programIdIndex': 38, 'stackHeight': 2}, {'accounts': [5, 25, 1], 'data': '3XZV5DYw7S8w', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [26, 10, 24], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 21, 22, 23, 2, 10, 36, 14, 34], 'data': 'EYwtd5cZ2x46GzRdaBV4ncpS7NWF7QPXVE', 'programIdIndex': 35, 'stackHeight': 2}, {'accounts': [22, 2, 21], 'data': '3sFhmXiKHtcf', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [10, 23, 1], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [28], 'data': '2C3FxF4wtCk1WPKYcjNvfKxBQp63Ne2UoU49PzYeeFYQPkQSyK8deGyJeNb3TzpxdREMvnBqqD1SJvxUVZ8VUowXtsZTWuGaMTA39aXtwzCT1vie5JSSK7o7CpHrSSqmMx3B9fbxBn2VwKxb6w9Xek6Qf5oSjCnNVvGqzTQ3coLN7E56GBXemtNt52rNX5azya1jAXc9qXaRQNLhXQDqfAPGntqw8jTp6Cfwrmk61trP1mHs7Dq4rbQiqfgfemviKiPUutgukwoJUgA6ejiLo3NUf3TgyLMAiCPWULy8wuLzy3W8iUVUGFauGCeZSScjWrQ15G6nfribhqmh8u7hDwhKkboTxJXP791H', 'programIdIndex': 13, 'stackHeight': 2}, {'accounts': [2, 20, 1], 'data': '3jJkXKqVVD8T', 'programIdIndex': 14, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['So11111111111111111111111111111111111111112', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj', 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', '2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'Sysvar1nstructions1111111111111111111111111', '9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp', 'SysvarC1ock11111111111111111111111111111111', 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', 'By9zHEbZJvYrBws27SqPXggfSAH3fjnJcdxKgdogyXUm'], 'writable': ['qqdJ4z1yu4sTbAitwXZsGNDoGZFgL2HfVKSVwAXWCfq', 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'ECEPWwZJ1U1Vjsj1X5sUbZYETKMSCjYHuoTMVitCn64t', 'FBWtVVvzsRuAAzVX8ua1hden9KmgPrC2rFijuwEn1ngJ', '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'CRF6Tegjtv3k9tuvKKbXroq4UmKXh9ZP92tn17sjjsFY', 'CT8B2qJAqy93GAU5Qor9s5xGGQEoiEwSSNRPAaDFYrgL']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 258345 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 261903 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]', 'Program log: Instruction: SellExactIn', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [3]', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 2039 of 216326 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program data: vdt/007mYe4v729nUnxNTIPERAhplCfJfDf9y6UhzLaf2npUDDGGIwB4xftR0QIAY3EOPunPAwDbGfgGAQAAAJyTbxmx+AAA1uHtWQAAAAA2E3sOOPcAALpIN1kAAAAAZoD0CnkBAABsObQAAAAAAN50AAAAAAAAc9MBAAAAAABfFwAAAAAAAAAAAAAAAAAAAQAB', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 210792 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 201525 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 186515 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 177191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 78407 of 247148 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh7lNA0AAAAAAPl7JhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 121358 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 115292 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 52182 of 161347 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp invoke [2]', 'Program log: 🦐', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 83284 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 77384 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: uzk28I9BxQZ484fWSzqZ3uRB544IUuDeeH1C4MV62fQcrneXpYLIS/F1G4rvWKU8C5OQGVO7h+OudgDex33l1UUKp5Q6jO/Vv5UvDS6eN94wSzulVKGgC/xW3GTCeByOgWtRMH78x2t9mKcEx0+H2l804ruYvH+6HFAqZ4NXRe6wKmcoKoYNVkN7vUR2RfKpWktR95FdWO+Y8MZnn1dZ7wHb14bvP17vnvDAZ5lXX++d8MNnmldc75zwwmebV13v9aDQ1LxWUu/dQhrzHVdT73AGN2WWV1DvuLJ6Z5dXUe+aFmDdCVZW737zyGeRV1fvlfDLZ5JXVO+V8Mpnk1dV7w==', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp consumed 34268 of 106189 compute units', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 70153 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4735 of 68079 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 192640 of 255163 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 L4PGAgAAAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 62523 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121815835862, 54559143, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338271045, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18393311302, 13018008, 1274267537134, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'postTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '728179866823882', 'decimals': 6, 'uiAmount': 728179866.823882, 'uiAmountString': '728179866.823882'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1610430361', 'decimals': 6, 'uiAmount': 1610.430361, 'uiAmountString': '1610.430361'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11898116474', 'decimals': 6, 'uiAmount': 11898.116474, 'uiAmountString': '11898.116474'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22726813', 'decimals': 6, 'uiAmount': 22.726813, 'uiAmountString': '22.726813'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18391272020', 'decimals': 9, 'uiAmount': 18.39127202, 'uiAmountString': '18.39127202'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274265491845', 'decimals': 9, 'uiAmount': 1274.265491845, 'uiAmountString': '1274.265491845'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586624463991', 'decimals': 6, 'uiAmount': 586624.463991, 'uiAmountString': '586624.463991'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176684933430', 'decimals': 6, 'uiAmount': 176684.93343, 'uiAmountString': '176684.93343'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32339272204', 'decimals': 6, 'uiAmount': 32339.272204, 'uiAmountString': '32339.272204'}}], 'preBalances': [121818891153, 5955720, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338069043, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18390004884, 13018008, 1274317407695, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'preTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1619386466406', 'decimals': 6, 'uiAmount': 1619386.466406, 'uiAmountString': '1619386.466406'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '726560480357476', 'decimals': 6, 'uiAmount': 726560480.357476, 'uiAmountString': '726560480.357476'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1622367191', 'decimals': 6, 'uiAmount': 1622.367191, 'uiAmountString': '1622.367191'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11897996807', 'decimals': 6, 'uiAmount': 11897.996807, 'uiAmountString': '11897.996807'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22720830', 'decimals': 6, 'uiAmount': 22.72083, 'uiAmountString': '22.72083'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18387965602', 'decimals': 9, 'uiAmount': 18.387965602, 'uiAmountString': '18.387965602'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274315362406', 'decimals': 9, 'uiAmount': 1274.315362406, 'uiAmountString': '1274.315362406'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586612650575', 'decimals': 6, 'uiAmount': 586612.650575, 'uiAmountString': '586612.650575'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176673122250', 'decimals': 6, 'uiAmount': 176673.12225, 'uiAmountString': '176673.12225'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32351085620', 'decimals': 6, 'uiAmount': 32351.08562, 'uiAmountString': '32351.08562'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'instructions': [{'accounts': [], 'data': 'FbXwDZ', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [], 'data': '3w56bdfNkcwH', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [2, 1, 27, 14, 15, 0], 'data': '2tDqDdUmhLW1t', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [1, 3, 2, 16, 27, 14, 14, 13, 28, 13, 20, 29, 1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 0, 15, 8, 9, 13, 38, 1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34, 35, 1, 21, 22, 23, 2, 10, 36, 14, 34, 33], 'data': '6ZARjK8Vuzcec2q5gZSKfeFAiRPD2NBawoAqfMk75i1qiqXn4W8jQobUuaD4Nx2eV9Lvh3jEtBpajvJjJ3cG1o6qq4Zx', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [2, 1, 1], 'data': 'A', 'programIdIndex': 14, 'stackHeight': 1}, {'accounts': [0, 11], 'data': '3Bxs43t5YK1vh4TZ', 'programIdIndex': 15, 'stackHeight': 1}], 'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', '8JrWPvg2ZiB2xaBKhRZiwXQzwhwbcii8ySYboGWnCnAB', '3rRjPpCB14e3eXLgE1BueVaHxUekBFfHMCDmTuD6ApbH', '4E7vL7FnDsdrUpqpJqb8C5q8JEoQAoaEKRS5pD6mjBWz', 'BehsFyHbsdea9ixfXx5dPL5DgukyD9ripZXCa6AXi3VW', '5Yt4ff98wjmy2xgRBc4u7MkuLDBzxrHNL3fKdTujvBPo', 'EAxfzwbMfxYJdLeHKpg3SWqajk88aycxSCqfixtdC1Xx', '67pirGqYiCT6j56DdQmAivWZSuZEtYbzSqMTWUNcHZAL', 'EzFT73bzdGAY52VuNKL2rfq8GPkSxBTK6Wd8zSGjJD1N', '5L1uEnJ96z4kgQ4zY9Rg1VWC1RmbtVrfutyMSiJQpVFg', 'E8iYKQbhTywHbncCagNBbZ58JY6cX1SiYk5ZDPJeWFFq', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', '11111111111111111111111111111111', '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'EPiZbnrThjyLnoQ6QQzkxeFqyL5uyg9RzNHHAudUPxBz', 'FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1', 'QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}, 'transaction_full': {'blockTime': 1759773320, 'meta': {'computeUnitsConsumed': 202745, 'costUnits': 210206, 'err': None, 'fee': 814009, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [0, 2], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 15, 'stackHeight': 2}, {'accounts': [2, 27], 'data': '6QR9nxorLs8pns5qcUs55CVfrLWHMQf92wS29j4F7zpMp', 'programIdIndex': 14, 'stackHeight': 2}]}, {'index': 3, 'instructions': [{'accounts': [1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 15, 8, 9], 'data': 'B3F1THDgKfWQNoqGkJRTMRi3faUjyQLsQoWRt9HLviQF', 'programIdIndex': 29, 'stackHeight': 2}, {'accounts': [31], 'data': 'EwDfpErTWwQhCAycT1hw3kgHYnu5XfSffnwsXbjvzoi62MCw8U9cB97RyMStDmh9HVqRzgbgjG1bcXcbRvTNifx9K118nrFjmhwTxUKbx2Z5UZbUHGJGDbbX9d6VnDAzcySaj2SWmkXaqewAFqq8EvVxczotqjKhjWSyhHT6a1Qonwmbg1oTp7VfYj3mFbGVUcySmbzxRFKRi1tKpzhN', 'programIdIndex': 29, 'stackHeight': 3}, {'accounts': [3, 16, 6, 1], 'data': 'hQd6eFvBGU7RP', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 5, 30], 'data': 'hUr6YwLadcviq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 8, 30], 'data': 'haTUQVQeEbAtu', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 9, 30], 'data': 'hK9e7r43JdfeV', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34], 'data': 'JrgsXFj1RYPjW8Y8GT2wMrgf', 'programIdIndex': 38, 'stackHeight': 2}, {'accounts': [5, 25, 1], 'data': '3XZV5DYw7S8w', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [26, 10, 24], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 21, 22, 23, 2, 10, 36, 14, 34], 'data': 'EYwtd5cZ2x46GzRdaBV4ncpS7NWF7QPXVE', 'programIdIndex': 35, 'stackHeight': 2}, {'accounts': [22, 2, 21], 'data': '3sFhmXiKHtcf', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [10, 23, 1], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [28], 'data': '2C3FxF4wtCk1WPKYcjNvfKxBQp63Ne2UoU49PzYeeFYQPkQSyK8deGyJeNb3TzpxdREMvnBqqD1SJvxUVZ8VUowXtsZTWuGaMTA39aXtwzCT1vie5JSSK7o7CpHrSSqmMx3B9fbxBn2VwKxb6w9Xek6Qf5oSjCnNVvGqzTQ3coLN7E56GBXemtNt52rNX5azya1jAXc9qXaRQNLhXQDqfAPGntqw8jTp6Cfwrmk61trP1mHs7Dq4rbQiqfgfemviKiPUutgukwoJUgA6ejiLo3NUf3TgyLMAiCPWULy8wuLzy3W8iUVUGFauGCeZSScjWrQ15G6nfribhqmh8u7hDwhKkboTxJXP791H', 'programIdIndex': 13, 'stackHeight': 2}, {'accounts': [2, 20, 1], 'data': '3jJkXKqVVD8T', 'programIdIndex': 14, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['So11111111111111111111111111111111111111112', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj', 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', '2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'Sysvar1nstructions1111111111111111111111111', '9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp', 'SysvarC1ock11111111111111111111111111111111', 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', 'By9zHEbZJvYrBws27SqPXggfSAH3fjnJcdxKgdogyXUm'], 'writable': ['qqdJ4z1yu4sTbAitwXZsGNDoGZFgL2HfVKSVwAXWCfq', 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'ECEPWwZJ1U1Vjsj1X5sUbZYETKMSCjYHuoTMVitCn64t', 'FBWtVVvzsRuAAzVX8ua1hden9KmgPrC2rFijuwEn1ngJ', '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'CRF6Tegjtv3k9tuvKKbXroq4UmKXh9ZP92tn17sjjsFY', 'CT8B2qJAqy93GAU5Qor9s5xGGQEoiEwSSNRPAaDFYrgL']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 258345 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 261903 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]', 'Program log: Instruction: SellExactIn', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [3]', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 2039 of 216326 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program data: vdt/007mYe4v729nUnxNTIPERAhplCfJfDf9y6UhzLaf2npUDDGGIwB4xftR0QIAY3EOPunPAwDbGfgGAQAAAJyTbxmx+AAA1uHtWQAAAAA2E3sOOPcAALpIN1kAAAAAZoD0CnkBAABsObQAAAAAAN50AAAAAAAAc9MBAAAAAABfFwAAAAAAAAAAAAAAAAAAAQAB', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 210792 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 201525 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 186515 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 177191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 78407 of 247148 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh7lNA0AAAAAAPl7JhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 121358 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 115292 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 52182 of 161347 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp invoke [2]', 'Program log: 🦐', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 83284 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 77384 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: uzk28I9BxQZ484fWSzqZ3uRB544IUuDeeH1C4MV62fQcrneXpYLIS/F1G4rvWKU8C5OQGVO7h+OudgDex33l1UUKp5Q6jO/Vv5UvDS6eN94wSzulVKGgC/xW3GTCeByOgWtRMH78x2t9mKcEx0+H2l804ruYvH+6HFAqZ4NXRe6wKmcoKoYNVkN7vUR2RfKpWktR95FdWO+Y8MZnn1dZ7wHb14bvP17vnvDAZ5lXX++d8MNnmldc75zwwmebV13v9aDQ1LxWUu/dQhrzHVdT73AGN2WWV1DvuLJ6Z5dXUe+aFmDdCVZW737zyGeRV1fvlfDLZ5JXVO+V8Mpnk1dV7w==', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp consumed 34268 of 106189 compute units', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 70153 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4735 of 68079 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 192640 of 255163 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 L4PGAgAAAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 62523 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121815835862, 54559143, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338271045, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18393311302, 13018008, 1274267537134, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'postTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '728179866823882', 'decimals': 6, 'uiAmount': 728179866.823882, 'uiAmountString': '728179866.823882'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1610430361', 'decimals': 6, 'uiAmount': 1610.430361, 'uiAmountString': '1610.430361'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11898116474', 'decimals': 6, 'uiAmount': 11898.116474, 'uiAmountString': '11898.116474'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22726813', 'decimals': 6, 'uiAmount': 22.726813, 'uiAmountString': '22.726813'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18391272020', 'decimals': 9, 'uiAmount': 18.39127202, 'uiAmountString': '18.39127202'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274265491845', 'decimals': 9, 'uiAmount': 1274.265491845, 'uiAmountString': '1274.265491845'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586624463991', 'decimals': 6, 'uiAmount': 586624.463991, 'uiAmountString': '586624.463991'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176684933430', 'decimals': 6, 'uiAmount': 176684.93343, 'uiAmountString': '176684.93343'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32339272204', 'decimals': 6, 'uiAmount': 32339.272204, 'uiAmountString': '32339.272204'}}], 'preBalances': [121818891153, 5955720, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338069043, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18390004884, 13018008, 1274317407695, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'preTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1619386466406', 'decimals': 6, 'uiAmount': 1619386.466406, 'uiAmountString': '1619386.466406'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '726560480357476', 'decimals': 6, 'uiAmount': 726560480.357476, 'uiAmountString': '726560480.357476'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1622367191', 'decimals': 6, 'uiAmount': 1622.367191, 'uiAmountString': '1622.367191'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11897996807', 'decimals': 6, 'uiAmount': 11897.996807, 'uiAmountString': '11897.996807'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22720830', 'decimals': 6, 'uiAmount': 22.72083, 'uiAmountString': '22.72083'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18387965602', 'decimals': 9, 'uiAmount': 18.387965602, 'uiAmountString': '18.387965602'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274315362406', 'decimals': 9, 'uiAmount': 1274.315362406, 'uiAmountString': '1274.315362406'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586612650575', 'decimals': 6, 'uiAmount': 586612.650575, 'uiAmountString': '586612.650575'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176673122250', 'decimals': 6, 'uiAmount': 176673.12225, 'uiAmountString': '176673.12225'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32351085620', 'decimals': 6, 'uiAmount': 32351.08562, 'uiAmountString': '32351.08562'}}], 'rewards': [], 'status': {'Ok': None}}, 'slot': 371620859, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', '8JrWPvg2ZiB2xaBKhRZiwXQzwhwbcii8ySYboGWnCnAB', '3rRjPpCB14e3eXLgE1BueVaHxUekBFfHMCDmTuD6ApbH', '4E7vL7FnDsdrUpqpJqb8C5q8JEoQAoaEKRS5pD6mjBWz', 'BehsFyHbsdea9ixfXx5dPL5DgukyD9ripZXCa6AXi3VW', '5Yt4ff98wjmy2xgRBc4u7MkuLDBzxrHNL3fKdTujvBPo', 'EAxfzwbMfxYJdLeHKpg3SWqajk88aycxSCqfixtdC1Xx', '67pirGqYiCT6j56DdQmAivWZSuZEtYbzSqMTWUNcHZAL', 'EzFT73bzdGAY52VuNKL2rfq8GPkSxBTK6Wd8zSGjJD1N', '5L1uEnJ96z4kgQ4zY9Rg1VWC1RmbtVrfutyMSiJQpVFg', 'E8iYKQbhTywHbncCagNBbZ58JY6cX1SiYk5ZDPJeWFFq', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', '11111111111111111111111111111111', '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'EPiZbnrThjyLnoQ6QQzkxeFqyL5uyg9RzNHHAudUPxBz', 'FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1', 'QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ'], 'addressTableLookups': [{'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [23, 0, 91, 92, 93, 40, 1], 'writableIndexes': [34]}, {'accountKey': '6JjsmWMgQtjUrBmA1obh4NZpc2CPqLcQ9cRPd2C5WBoM', 'readonlyIndexes': [126, 124, 128], 'writableIndexes': [129, 127, 125]}, {'accountKey': 'DMQiFwkdPjts3db8RiYpeiSu4R4CyBjUVhX2v7y8HUWF', 'readonlyIndexes': [58, 55, 52], 'writableIndexes': [51, 53, 59]}], 'header': {'numReadonlySignedAccounts': 0, 'numReadonlyUnsignedAccounts': 8, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'FbXwDZ', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [], 'data': '3w56bdfNkcwH', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [2, 1, 27, 14, 15, 0], 'data': '2tDqDdUmhLW1t', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [1, 3, 2, 16, 27, 14, 14, 13, 28, 13, 20, 29, 1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 0, 15, 8, 9, 13, 38, 1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34, 35, 1, 21, 22, 23, 2, 10, 36, 14, 34, 33], 'data': '6ZARjK8Vuzcec2q5gZSKfeFAiRPD2NBawoAqfMk75i1qiqXn4W8jQobUuaD4Nx2eV9Lvh3jEtBpajvJjJ3cG1o6qq4Zx', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [2, 1, 1], 'data': 'A', 'programIdIndex': 14, 'stackHeight': 1}, {'accounts': [0, 11], 'data': '3Bxs43t5YK1vh4TZ', 'programIdIndex': 15, 'stackHeight': 1}], 'recentBlockhash': 'KoYoGnVuPgzZCSdWKBT2ajwkqKvTj2GtnG5bnMw1QN9'}, 'signatures': ['kGo2toyarf9z8UX2ajqcG3vU8JEcjXhfQYLeGceY9GjGmbtThC8gStH6MeBu1YAwuweWT1j6ohdWHeMT1HRqjYT', 'JZeajkzGMhpPdKBmsfaXW5qYZraekpAUeyXaApK6rPWeubWTEFxHM5qxciGNuD2BzfgHMmXDPvZNuNXNPqgXFTH']}, 'version': 0}, 'extracted_info': {'output_mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'token_mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'source': 'sophisticated_extraction', 'confidence': 'high'}, 'router_program_id': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'dex_type': 'jupiter', 'action': 'sell'}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: full_output_III.py:3

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-06 18:55:33,700 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': 'Df8EmUzNvbLT7FZvZHdrZr7Vq1kwpSB67hW43XrX3xZTYrXrFzXMPvPnvRsv1tGQF5JMqRvtWrb1piVnSwPPwYM', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]', 'Program log: CreateIdempotent', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: GetAccountDataSize', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 338794 compute units', 'Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program log: Initialize the associated token account', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeImmutableOwner', 'Program log: Please upgrade to SPL Token 2022 for immutable owner support', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 332207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 328325 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20442 of 344275 compute units', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 320275 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 323833 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 297844 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 292027 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU31rwC+8NeoW5ahnmHWb9iCYrT3cfO79wpk92QvqJ9W3ELwcfs2SZeoT6jUitWveLrWf7NXKuei1OfEzE3UX7jr9gTJTy+DnPr8V3nWq612cVgUiVfuqM9nRF+vmW3fGN5X5SW7T74cJwEbZ9oaJ31u0y5A0jtKppcKHj//h6NRTfWEZLYzLvptL8pZEty93e9FsZiX54eAxcFlQR/l+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FZnNoG4eAxcCYWSPl+0ZYzKcYCt0LXR76U6xbZxcUGQaDMC6XW/WV4N+Rfuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 46763 of 309830 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 227225 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 219520 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJaJ8GZhEw5RuMaegm7Kp2J14F+MzacEwMQH5MU0KK306AAmfg0LX6DKyx4AAAAAAAAAL8SNqLvhQ88eAAAAAAAAAPB3MlQ+AAAA5P3OEAAAAAAAAAAAAAAAAAAAAAAAAAAA0+HwBgAAAADYggkBAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 48542 of 259809 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 198974 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 193140 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19683 of 208058 compute units', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [2]', 'Program log: Instruction: Buy', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ invoke [3]', 'Program log: Instruction: GetFees', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ consumed 4655 of 128795 compute units', 'Program return: pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ AgAAAAAAAABdAAAAAAAAAB4AAAAAAAAA', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 120025 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 111078 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 102056 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 93031 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Z/RSHyz1d3eWAuRoAAAAANQ2JJlUBQAA8PO6GAAAAAAAAAAAAAAAAPDzuhgAAAAAa6E3VavpAQA5TveqCAAAAOLQaxgAAAAAAgAAAAAAAAAYQAEAAAAAAF0AAAAAAAAAUyQ6AAAAAAD6EG0YAAAAALP2uRgAAAAAE2qrvCNj2IGSTJgIQW4lMDytD7YR7arIohmaVZ+qT9In23x60LKtrZbdNGyuGyj0ADl01fYU0EHbq2rZ6ng8yZeo75gq2QDn0AMZwNBnejFqXNlNYIlQ1kDmU4MBS5bgbG+mNnUhLe1gc/XMF7vvYC7/Zono+DGtS5riV7jnU1lgjMwd/OlhtDt3nBkVBabi079F1aTbRhitdsgtYXVFNV0OMm1Matf/fY9TP8MJCFS9H+8ykQhAD19V155Lh4BRiyUYBwQiLWWBvRgv+FbkGcAeqnLxzVwgEEPSplv+/VoeAAAAAAAAAGbBEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [3]', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 2027 of 79902 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 102460 of 175611 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 71322 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 69501 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 253054 of 317093 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 1DYkmVQFAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 64039 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 33, 700370, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 283601, 'costUnits': 293836, 'err': None, 'fee': 1610000, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [50], 'data': '84eT', 'programIdIndex': 16, 'stackHeight': 2}, {'accounts': [0, 6], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 11, 'stackHeight': 2}, {'accounts': [6], 'data': 'P', 'programIdIndex': 16, 'stackHeight': 2}, {'accounts': [6, 50], 'data': '6PpHgoYBYjXp1psXZyvNVUGrzNw4ndQDEbsKAfPRkZDJG', 'programIdIndex': 16, 'stackHeight': 2}]}, {'index': 3, 'instructions': [{'accounts': [0, 4], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 11, 'stackHeight': 2}, {'accounts': [4, 39], 'data': '6PpHgoYBYjXp1psXZyvNVUGrzNw4ndQDEbsKAfPRkZDJG', 'programIdIndex': 16, 'stackHeight': 2}]}, {'index': 4, 'instructions': [{'accounts': [21, 18, 19, 20, 22, 2, 5, 1, 16, 40], 'data': '4gTFnZ4t8u23XWnxLZnM8kP', 'programIdIndex': 42, 'stackHeight': 2}, {'accounts': [2, 19, 1], 'data': '3mfrCyRWtp1V', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [22, 5, 22], 'data': '3ugP2GsRwXnf', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [16, 1, 32, 4, 33, 5, 34, 10, 9, 7, 51], 'data': '59p8WydnSZtXFLDenLKcwdBR6qjZAp36uw1FMSkCNDfjLmRWHMNV8q6TpB', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [5, 34, 1], 'data': '3ugP2GsRwXnf', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [33, 4, 32], 'data': '3sm4p3kSk6KH', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [1, 23, 4, 2, 25, 24, 14, 40, 16], 'data': '2d6dWj1mbWkTsAvaXudkTbtJM5r', 'programIdIndex': 45, 'stackHeight': 2}, {'accounts': [2, 24, 1], 'data': '3DWFNscvX9cK', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [25, 4, 23], 'data': '3FdLP6sMt8Uo', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [27, 1, 44, 50, 39, 6, 4, 31, 26, 43, 29, 16, 16, 11, 12, 46, 47, 28, 49, 30, 8, 48, 38], 'data': 'AJTQ2h9DXrC5M2wm3yq8UFHCVvePMuJ8f', 'programIdIndex': 47, 'stackHeight': 2}, {'accounts': [48, 47], 'data': '2BfZXS1GQrCLYxNyN28stskDGyVX2YQ3nqcFzKDzWJsLqu', 'programIdIndex': 38, 'stackHeight': 3}, {'accounts': [31, 50, 6, 27], 'data': 'iociATzmWB4x5', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [4, 39, 26, 1], 'data': 'jHZY3pXyxwy6g', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [4, 39, 29, 1], 'data': 'hAL2BgMEGim9J', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [4, 39, 28, 1], 'data': 'hQopfA1UXFBKW', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [46], 'data': 'CTu2YvT3DVurkJGfs6YDcKYxjZ6CZLKYgEgTy4MAgTsvecJPQzwXw7bUBWRgMEUVRnQok1qKxMazsqzd3Ds4XoiirZEkL28Xc5CCY2g4SWsFtpPKeM2bvihFa7ASgZVXo6jZKNsfasnCXHUCbhr9AfpNaDa63Q8K3RyjpWfCtdhb2EDqmmQ42S1Yz2q4HqkzktZzSUizgz46SdmDUUnDAHG96VqQDZg8xBqSv5j8RFfM9tS9xVqhbXbXMoBuK2XS1YoZ6Eu5So9qWAYjCf5bFCDMPnS9FNbLi7hgY27L2y9FhbkUjNFfAxfXuJai53JxDRwfZjDCtgwm48VzJjQ4pavBCwZ3RY6Aeg6uFTnPczKUFjvPFZNuSDpDtptTkzLNAzVNP2jYyV7tQtR82AoWcih45favJT95LubRdWi1K5WfMRNefUvWwMezVUqwt5XU3vFKydj8t4kw7WtZ3QaLxLkdAuz2NS83zo8FpigiN5P8kPpn1xkFLLnmAcw9ByQ7a7JZjjNswsmHzo9jP4uDrbNe1MfGYkXCRzj9', 'programIdIndex': 47, 'stackHeight': 3}, {'accounts': [35], 'data': '4KbP49BdVApjtHuXZdNzDMRzUrFad32msbNDnEYAYPQjzkC9HQWsZg1bqYcV42HqWmzj35WAJByTR9p2U8k9R5rpJKUkh33noRHpWHZ8mhGVdXbozcmg4EboPYACZrKoU9UmgybDRMSXT1zTmUHrKa5kbPtygTDa784hdqtA9Qjr92s85QrNwZzUAHwfKvjTuXcH79M23AVC7AodKhbH3F2eU8ku6KWxFaqiFPaMJTkkuzF3VaKtv3vbBaBk77GRkgAd1qm3WFWk3YsZDMtWrXnM5dHonKbTShGDiYaPAN2s761jbzfX8BjgCgZ1PEZ47xGXU4q1n6GsFW5wEsCMmuub5bKCeS68BpJv8mzfUpE8nNREkPEGvGghoVjfDTSg5AFqefGTVRiJA11je4fynrwN6yhaUXHiddenQM2b8jkzegEjxDLe8pbw1fWyaDHqAuaqxH4dwjGq9ZcbZ', 'programIdIndex': 15, 'stackHeight': 2}, {'accounts': [2, 17, 1], 'data': '3QAg3utWGhiF', 'programIdIndex': 16, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ', 'So11111111111111111111111111111111111111112', 'Sysvar1nstructions1111111111111111111111111', 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY', '7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ', 'ADyA8hdefvWN2dbGGWFotbzWxrAvLW83WG6QCVXvJKqw', 'goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j', 'GS4CU59F31iL7aR2Q8zVS8DRrcRnXX1yjQ66TqNVQnaR', 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA', '5PHirr8joyTMp9JMm6nW7hNDVyEYdkzDqazxPD7RaTjx', 'DRdByGXTqxpVr72bZFXJ27Y2UQ2gfjtbr5tFDeEb8RG3', 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', '7T9uvDmpdKVzxsWkEQvpnZKnEsaK6LQ7tnDpd6pNJfZH'], 'writable': ['DY6pE7aiDafuk35REZF9p9av3vbV2VQrvdZ4YyB1pZ4C', '4Un9yaV18EBHApYRkEEpYWY3NsBPaABofWLNC21LapVE', 'Ai4kU7H79HHtK6pRTX13kqAgihH41afgLqnDAuPkekMC', 'CTUhs66Gph5q4BcdWKmRAYqWDvwkrU1xFukivEh2GXm2', 'EciLGydSE5RvGLQ3YutztkAzgcA48kNMrbASVigVKCZg', 'H75FJTVxzKcXsyxMsp2R1TSDP85m6LXiDFW5cFU4gL4W', '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'Gsy5Zr7Vxn5KckAbduPHHGR1qzPJ4w3GSYmcinWAkhrC', 'pKiUC9hDXv52xqU1p3BKypV9AQjAMgfZUGRnoBsdkKm', '2DjchPNarSqGJNNPCpXJCCagFv7Cn3wAhLd3nJCMpsE8', '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', '4Rvyik5jWSxXSapXrAJsnDdUrgU5cFRzNcvHygVpYQRH', '7GFUN3bWzJMKMRZ34JLsvcqdssDbXnp589SiE33KVwcC', 'C2aFPdENg4A2HQsmrd5rTw5TaYBX5Ku887cWjbFKtZpw', 'E8NKrYjZPstjbBXPPJp3qkEGjdw9BeVGvHMQpWGM9GQ3', 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'ATUMydDvNcELzNk9GP1Ky7i2Mgx2t2ej5aNPMhA6F2VH', 'ChcWkmUbWDbBspDjPX6ZXi7Hb9kZ7VTbNUf6nMtWF1YH']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]', 'Program log: CreateIdempotent', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: GetAccountDataSize', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 338794 compute units', 'Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program log: Initialize the associated token account', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeImmutableOwner', 'Program log: Please upgrade to SPL Token 2022 for immutable owner support', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 332207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 328325 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20442 of 344275 compute units', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 320275 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 323833 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 297844 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 292027 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU31rwC+8NeoW5ahnmHWb9iCYrT3cfO79wpk92QvqJ9W3ELwcfs2SZeoT6jUitWveLrWf7NXKuei1OfEzE3UX7jr9gTJTy+DnPr8V3nWq612cVgUiVfuqM9nRF+vmW3fGN5X5SW7T74cJwEbZ9oaJ31u0y5A0jtKppcKHj//h6NRTfWEZLYzLvptL8pZEty93e9FsZiX54eAxcFlQR/l+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FZnNoG4eAxcCYWSPl+0ZYzKcYCt0LXR76U6xbZxcUGQaDMC6XW/WV4N+Rfuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 46763 of 309830 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 227225 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 219520 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJaJ8GZhEw5RuMaegm7Kp2J14F+MzacEwMQH5MU0KK306AAmfg0LX6DKyx4AAAAAAAAAL8SNqLvhQ88eAAAAAAAAAPB3MlQ+AAAA5P3OEAAAAAAAAAAAAAAAAAAAAAAAAAAA0+HwBgAAAADYggkBAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 48542 of 259809 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 198974 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 193140 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19683 of 208058 compute units', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [2]', 'Program log: Instruction: Buy', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ invoke [3]', 'Program log: Instruction: GetFees', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ consumed 4655 of 128795 compute units', 'Program return: pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ AgAAAAAAAABdAAAAAAAAAB4AAAAAAAAA', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 120025 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 111078 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 102056 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 93031 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Z/RSHyz1d3eWAuRoAAAAANQ2JJlUBQAA8PO6GAAAAAAAAAAAAAAAAPDzuhgAAAAAa6E3VavpAQA5TveqCAAAAOLQaxgAAAAAAgAAAAAAAAAYQAEAAAAAAF0AAAAAAAAAUyQ6AAAAAAD6EG0YAAAAALP2uRgAAAAAE2qrvCNj2IGSTJgIQW4lMDytD7YR7arIohmaVZ+qT9In23x60LKtrZbdNGyuGyj0ADl01fYU0EHbq2rZ6ng8yZeo75gq2QDn0AMZwNBnejFqXNlNYIlQ1kDmU4MBS5bgbG+mNnUhLe1gc/XMF7vvYC7/Zono+DGtS5riV7jnU1lgjMwd/OlhtDt3nBkVBabi079F1aTbRhitdsgtYXVFNV0OMm1Matf/fY9TP8MJCFS9H+8ykQhAD19V155Lh4BRiyUYBwQiLWWBvRgv+FbkGcAeqnLxzVwgEEPSplv+/VoeAAAAAAAAAGbBEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [3]', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 2027 of 79902 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 102460 of 175611 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 71322 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 69501 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 253054 of 317093 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 1DYkmVQFAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 64039 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121796250128, 9912007, 2039280, 18938098122, 0, 2039280, 2039280, 70407360, 1844400, 70407360, 70407360, 1, 789146954, 1, 0, 2729681025, 5065007155, 2039380, 8352000, 2039283, 8352000, 52784640, 2039281, 6849541, 2039280, 2538088049828, 37639912739, 2978880, 97567361710, 53577114376, 25068895, 2039280, 5532941, 56513762977, 2039280, 3596047, 418677002208, 1000004, 1141472, 1158072388620, 0, 1161444, 1141440, 6551763765953, 4457500, 1142440, 1002022, 109153247, 18374406, 0, 1461600, 0], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '74463650', 'decimals': 6, 'uiAmount': 74.46365, 'uiAmountString': '74.46365'}}, {'accountIndex': 5, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 9, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '5860904679124', 'decimals': 6, 'uiAmount': 5860904.679124, 'uiAmountString': '5860904.679124'}}, {'accountIndex': 17, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HU23r7UoZbqTUuh3vA7emAGztFtqwTeVips789vqxxBw', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '6045215880', 'decimals': 6, 'uiAmount': 6045.21588, 'uiAmountString': '6045.21588'}}, {'accountIndex': 19, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'Ai4kU7H79HHtK6pRTX13kqAgihH41afgLqnDAuPkekMC', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '115303496137', 'decimals': 6, 'uiAmount': 115303.496137, 'uiAmountString': '115303.496137'}}, {'accountIndex': 22, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'H75FJTVxzKcXsyxMsp2R1TSDP85m6LXiDFW5cFU4gL4W', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '350235198190070', 'decimals': 9, 'uiAmount': 350235.19819007, 'uiAmountString': '350235.19819007'}}, {'accountIndex': 24, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '374025903438', 'decimals': 6, 'uiAmount': 374025.903438, 'uiAmountString': '374025.903438'}}, {'accountIndex': 25, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2538086010544', 'decimals': 9, 'uiAmount': 2538.086010544, 'uiAmountString': '2538.086010544'}}, {'accountIndex': 26, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '37637873459', 'decimals': 9, 'uiAmount': 37.637873459, 'uiAmountString': '37.637873459'}}, {'accountIndex': 28, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DRdByGXTqxpVr72bZFXJ27Y2UQ2gfjtbr5tFDeEb8RG3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '97565322430', 'decimals': 9, 'uiAmount': 97.56532243, 'uiAmountString': '97.56532243'}}, {'accountIndex': 29, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '53575075096', 'decimals': 9, 'uiAmount': 53.575075096, 'uiAmountString': '53.575075096'}}, {'accountIndex': 31, 'mint': 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '532536150420119', 'decimals': 6, 'uiAmount': 532536150.420119, 'uiAmountString': '532536150.420119'}}, {'accountIndex': 33, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '56511703659', 'decimals': 9, 'uiAmount': 56.511703659, 'uiAmountString': '56.511703659'}}, {'accountIndex': 34, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '480163480699117', 'decimals': 9, 'uiAmount': 480163.480699117, 'uiAmountString': '480163.480699117'}}], 'preBalances': [121802339687, 7807898, 2039280, 18937697123, 0, 2039280, 0, 70407360, 1844400, 70407360, 70407360, 1, 789146954, 1, 0, 2729681025, 5065007155, 2039380, 8352000, 2039283, 8352000, 52784640, 2039281, 6849541, 2039280, 2538220954288, 37230111785, 2978880, 97566132552, 53573303989, 25068895, 2039280, 5532941, 56795763845, 2039280, 3596047, 418677002208, 1000004, 1141472, 1158072388620, 0, 1161444, 1141440, 6551763765953, 4457500, 1142440, 1002022, 109153247, 18374406, 0, 1461600, 0], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '174463650', 'decimals': 6, 'uiAmount': 174.46365, 'uiAmountString': '174.46365'}}, {'accountIndex': 5, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 9, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 17, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HU23r7UoZbqTUuh3vA7emAGztFtqwTeVips789vqxxBw', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '6043575880', 'decimals': 6, 'uiAmount': 6043.57588, 'uiAmountString': '6043.57588'}}, {'accountIndex': 19, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'Ai4kU7H79HHtK6pRTX13kqAgihH41afgLqnDAuPkekMC', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '115236611337', 'decimals': 6, 'uiAmount': 115236.611337, 'uiAmountString': '115236.611337'}}, {'accountIndex': 22, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'H75FJTVxzKcXsyxMsp2R1TSDP85m6LXiDFW5cFU4gL4W', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '350502898756070', 'decimals': 9, 'uiAmount': 350502.89875607, 'uiAmountString': '350502.89875607'}}, {'accountIndex': 24, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '373994428238', 'decimals': 6, 'uiAmount': 373994.428238, 'uiAmountString': '373994.428238'}}, {'accountIndex': 25, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2538218915004', 'decimals': 9, 'uiAmount': 2538.218915004, 'uiAmountString': '2538.218915004'}}, {'accountIndex': 26, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '37228072505', 'decimals': 9, 'uiAmount': 37.228072505, 'uiAmountString': '37.228072505'}}, {'accountIndex': 28, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DRdByGXTqxpVr72bZFXJ27Y2UQ2gfjtbr5tFDeEb8RG3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '97564093272', 'decimals': 9, 'uiAmount': 97.564093272, 'uiAmountString': '97.564093272'}}, {'accountIndex': 29, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '53571264709', 'decimals': 9, 'uiAmount': 53.571264709, 'uiAmountString': '53.571264709'}}, {'accountIndex': 31, 'mint': 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '538397055099243', 'decimals': 6, 'uiAmount': 538397055.099243, 'uiAmountString': '538397055.099243'}}, {'accountIndex': 33, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '56793704527', 'decimals': 9, 'uiAmount': 56.793704527, 'uiAmountString': '56.793704527'}}, {'accountIndex': 34, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '479895780133117', 'decimals': 9, 'uiAmount': 479895.780133117, 'uiAmountString': '479895.780133117'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', '76U6Ds3W2g9SY284AKQ5usDTv8B6TvJnupbM889a9EFA', '77N86XfcBSAvcGNPYMAVjjyf2feUJwmUoiJ96HzPtySd', '8JHmvYWTvgMCM4XZn3WpngwZRWWWgd9jxPB2c8rdnQ9e', 'AXNMeXbbEsK7LDMmFPgiEt9Msok3MBWetaZLWvaNtpx6', 'BD1yGZNeyTR6i2yaPCYR8zfXoEyXS8DFWx21g3WG25zo', 'CGYWxf8vWAeBVV2WSeu4hZGe8sjWc7ZPJZnFW7s3PCKy', 'DsVNyEhcD1F9apxPxeCb5Xdcia54uaZrcmjmLzk7qkAs', 'DWe8o233ok6muipK3qcnnuD1b5N1voao2GvReiy3bYzD', 'GBm5LJcFuJmhqsMi9Un1ooAeUdLkrUZGgGPFoWFLS5FB', '11111111111111111111111111111111', 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL', 'ComputeBudget111111111111111111111111111111', 'CTCAsP51f2jfXZUBxwgixoZmJ3EAM595N61Fq1gVm7Ni', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'], 'addressTableLookups': [{'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 40, 1, 86, 23], 'writableIndexes': [52]}, {'accountKey': 'AFfzVh7qC5MdvYj1fmfeyL6tvRDqLrxdwhooATZaST47', 'readonlyIndexes': [146, 14, 144], 'writableIndexes': [147, 148, 143, 142, 145]}, {'accountKey': 'D4QBMf27hQbL2JkaM1xy5gvQavLpPyXqf4SMcEsWwg43', 'readonlyIndexes': [148, 38, 206, 36, 22], 'writableIndexes': [203, 207, 204]}, {'accountKey': 'DxDSaPr5vw9g5kBFHjuNLgKXvXEaEAZJe4uVirn94haR', 'readonlyIndexes': [16, 141, 109], 'writableIndexes': [142, 138, 137, 136, 11, 106]}, {'accountKey': 'HpZkwQHLVJZE864sq7eR2hDtpJ9LZH65ZqrYUBzuQVsT', 'readonlyIndexes': [221], 'writableIndexes': [220, 229, 54]}], 'header': {'numReadonlySignedAccounts': 0, 'numReadonlyUnsignedAccounts': 6, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'LcVLq5', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [], 'data': '3ReKnJZaqz8P', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [0, 6, 1, 50, 11, 16], 'data': '2', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [4, 1, 39, 16, 11, 0], 'data': '2tDqDdUmhLW1t', 'programIdIndex': 15, 'stackHeight': 1}, {'accounts': [1, 2, 6, 36, 50, 16, 16, 15, 35, 15, 17, 42, 21, 18, 19, 20, 22, 2, 5, 1, 16, 40, 41, 16, 1, 32, 4, 33, 5, 34, 10, 9, 7, 51, 45, 1, 23, 4, 2, 25, 24, 14, 40, 16, 47, 27, 1, 44, 50, 39, 6, 4, 31, 26, 43, 29, 16, 16, 11, 12, 46, 47, 28, 49, 30, 8, 48, 38, 0, 37], 'data': 'PQB5t7vv4wRsESuAKYpvJqqrSdcR8oDZM7qKmD4s8zhhDPVKFwW78HSLenTTATdo2vMKSVcJATEoLw', 'programIdIndex': 15, 'stackHeight': 1}, {'accounts': [4, 1, 1], 'data': 'A', 'programIdIndex': 16, 'stackHeight': 1}, {'accounts': [0, 3], 'data': '3Bxs4J72XK7NHUAT', 'programIdIndex': 11, 'stackHeight': 1}], 'recentBlockhash': 'r9L2MGdbiRtVLH2gvQoZVs6rN667RrbWFRczMVE1U2n'}, 'signatures': ['Df8EmUzNvbLT7FZvZHdrZr7Vq1kwpSB67hW43XrX3xZTYrXrFzXMPvPnvRsv1tGQF5JMqRvtWrb1piVnSwPPwYM', '2Tsya2ZNFTYhnhe2nZ16nfrefa2MK8c2HLCqxnSzuBDT8FtLcr1QTmCuvYD7XozryM3PinwnH3scvN8syZwB8GQy']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: full_output_IV.py:2

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-06 18:55:42,747 - __main__ - ERROR - Uncertain action or token mint detected in main: action=unknown, token_mint=UNKNOWN, trade_info={'signature': '62GzueLZRbm4sfURKdnL13AasTJJhHCAogTosdR2BoffZMUDp1fvBmkcc2qetfKfCft731ZL1wqdqhkG24UsS5hy', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 42, 618259, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 300, 'costUnits': 1632, 'err': None, 'fee': 5000, 'innerInstructions': [], 'loadedAddresses': {'readonly': [], 'writable': []}, 'logMessages': ['Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success'], 'postBalances': [19258274510, 121776879239, 1, 1], 'postTokenBalances': [], 'preBalances': [19258280510, 121776878239, 1, 1], 'preTokenBalances': [], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'instructions': [{'accounts': [0, 1], 'data': '3Bxs4ffTu9T19DNF', 'programIdIndex': 2, 'stackHeight': 1}, {'accounts': [], 'data': 'FDJTAf', 'programIdIndex': 3, 'stackHeight': 1}], 'accountKeys': ['AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw', 'gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}, 'transaction_full': {'blockTime': 1759773343, 'meta': {'computeUnitsConsumed': 300, 'costUnits': 1632, 'err': None, 'fee': 5000, 'innerInstructions': [], 'loadedAddresses': {'readonly': [], 'writable': []}, 'logMessages': ['Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success'], 'postBalances': [19258274510, 121776879239, 1, 1], 'postTokenBalances': [], 'preBalances': [19258280510, 121776878239, 1, 1], 'preTokenBalances': [], 'rewards': [], 'status': {'Ok': None}}, 'slot': 371620916, 'transaction': {'message': {'accountKeys': ['AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw', 'gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111'], 'addressTableLookups': [], 'header': {'numReadonlySignedAccounts': 0, 'numReadonlyUnsignedAccounts': 2, 'numRequiredSignatures': 1}, 'instructions': [{'accounts': [0, 1], 'data': '3Bxs4ffTu9T19DNF', 'programIdIndex': 2, 'stackHeight': 1}, {'accounts': [], 'data': 'FDJTAf', 'programIdIndex': 3, 'stackHeight': 1}], 'recentBlockhash': 'JAsKK2HTaDjzXwiVh48uodAAhT6StqRazcPGk2GXXe6H'}, 'signatures': ['62GzueLZRbm4sfURKdnL13AasTJJhHCAogTosdR2BoffZMUDp1fvBmkcc2qetfKfCft731ZL1wqdqhkG24UsS5hy']}, 'version': 0}, 'router_program_id': None, 'dex_type': 'unknown'}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: full_output_V.py:3

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-06 18:55:55,427 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': '41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 55, 427124, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 393367, 'costUnits': 403892, 'err': None, 'fee': 310654, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [2, 16, 1], 'data': '3awy1w6vdVeX', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [39, 23, 24, 25, 15, 16, 41, 44], 'data': 'J9A6eM58XaLWXKsmqBa2NbWp', 'programIdIndex': 43, 'stackHeight': 2}, {'accounts': [16, 25, 39], 'data': '3JpGTWoUyaDu', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [24, 15, 23], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42], 'data': '59p8WydnSZtV29EZJ5EPHbUYgwcyEPuwe7SXrhmNB83k1QhfcFC71rtXHa', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [15, 17, 39], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [19, 3, 21], 'data': '3Z6sYHBgK6Ky', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35], 'data': '59p8WydnSZtSYqyRFuqQPv9H538j1vw22B54xWsoUsCA53MawYHzdhGF2x', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [16, 14, 39], 'data': '3JvGaqeJM4Hd', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [12, 3, 13], 'data': '3YMxHtDwKwzF', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28], 'data': 'wZRp7wZ3czsp8TiBYg9eUvG8CbxCoDYm42UzZBycSgh5Z3PVpMQRnwuz', 'programIdIndex': 46, 'stackHeight': 2}, {'accounts': [16, 27, 39], 'data': '3QJJ2xEUe3q1', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [32, 3, 26], 'data': '3FDG456PfyrP', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [37], 'data': '4KbP49BdVApjtHuXZdNzDMRzUrFad32msbNDnEYAYPQjzkC9HQWsZg1bqYcV42HqWmzj35W86LMLAaDsXdQGXr8ABcyjSB2Yy87SyzmryVoMFg2uka2ui24a42mTckbKcFwx3Y2Eb9shgn5HevkmfzSeLBWjMYtYsaPqPgxPAghFzqsn88EC9wz8HdnuK9FYZjzy5wnjFY3g8pXfG8cLUUWa3V2U2YjRfFBCC35KxSZrwp7j7rSBAvVyRuoyaMG4xEpfdd2jLcJMMwcipiYk9YxfgYAgNgogzLaApf2JjMX59N2GBCHAQFQDYCQYMEvao1PwTBGz9hAZC562sXP9oJLAkrmUQz4Y3JNyL1A28SLxuPuK8tnf5yKx4mwe8rWLKv1S1DfEUbQrq4xP9vmgFEJJZ5i4QX5kyyJbcikf8Q7Bz4jKf4X8HDWNc6YigxvzPMBhT8X82kqsNojDZ', 'programIdIndex': 8, 'stackHeight': 2}, {'accounts': [2, 16, 1], 'data': '3avKVPuic5LT', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [3, 5, 39], 'data': '3uktGuL5uriK', 'programIdIndex': 41, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'GrzzQpVYkCoDnXGVpANW9iDGJk9EbcJJRj9FgY3GeVNm', 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'jitodontfront11111111111JustUseJupiterU1tra', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'FovDWEsftJv4X1EfapqVwG2VDcEDG2vsa7vaje3qAo56', 'SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe', 'Sysvar1nstructions1111111111111111111111111', 'A1BBtTYJd4i3xU8D6Tc2FzU6ZN4oXZWXKZnCxwbHXr8x', 'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK'], 'writable': ['4ZEwCEENfgAqzbyKLBDLZxSeixbKpZknirkWLFVcaLBw', '7yUHJWhvRnspqZKezhVHxJmsLLcfNyDn4dhYTCNNPTxe', '8z95LBWmSRKkQv1XPczvN6s2Fc3Rk5X6oi1ueW3nndBV', 'Bc1Ki733Cv9Fu2qGwar3n6EjQBofTpwrVAg2uSo5uLUV', 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'Efe7p9ZEbd99dCoGU3mbYbRRxU9tJuSmHX6jYDtbKC4x', '2p29nqD7DN1PczBMmgrFdtYKTfv6rJ7H3yMut4eu7nYT', '5SPztfEn1VAaWDBAXjQKwVrGbr6e8g3F6JJnUc9eCuSe', '2rJJP6RAyfo5HaoR9T6SDjWU885RkQBH3PyRpnoFrkDU', '3aSDFqAyFJPniaZpJf7Vn9PxZqT6dcuxzg9HXwWkbpVP', 'E83CnZbE1cz2ww5rqYuvWmAdMwWh3ZkJJcrbo49TaaGU', 'E9TL1PrwPxpdvMGjSXJQidJSmdBG4LYJJWoHDF5gSVv2', 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'H1j2gqzW61MrdjJsu6s5gamLq9wcKkinw1a7GWyjdd6k', 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'CTaDZW2LhvHPRnA9JWcZF8R5y2mpkV2RcHAXyEoKLbzp', 'JHVJLsPsbzNW8JP8cPYmrwfzD2M9aHXdFHSjeeCDERu', '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', '4LCiADXLEBW2JepG5iue3iTB3ozXb3YLGqheQNEWTSAY', '666Sz6bUgQwS2vgGDkPSwfqSsxtmBUh7Zvya6p2nkTJF', '7B5dskPoP5r2vXPDJgzvwCNTtuYwXVgV6KEeaWn8o2Ph', 'C86icgvRMBRHZWnTFjHnLh4o3BVroZYx5CHueZzAqByo', 'DnrPPNMp3ZqcCcrF8LEPLiXBiwMDPwELKFAy8ToHwUsD', 'FSGuR2PvoUqZvuQNxQVgyUeP4Mcsa89JxeqvAFWqSJdo', 'GwXt2aQ8gT39XT7HhcSdiDyTdxNgLY3pyJQm56mcbzWE']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121763506924, 9204256, 2039280, 2039280, 20152947666, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8769954653, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599752863345, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2430379783', 'decimals': 6, 'uiAmount': 2430.379783, 'uiAmountString': '2430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1290180175863', 'decimals': 6, 'uiAmount': 1290180.175863, 'uiAmountString': '1290180.175863'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3329485185848465', 'decimals': 6, 'uiAmount': 3329485185.848465, 'uiAmountString': '3329485185.848465'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '519465211363', 'decimals': 6, 'uiAmount': 519465.211363, 'uiAmountString': '519465.211363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4059641614', 'decimals': 6, 'uiAmount': 4059.641614, 'uiAmountString': '4059.641614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8767915373', 'decimals': 9, 'uiAmount': 8.767915373, 'uiAmountString': '8.767915373'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4072118737060', 'decimals': 6, 'uiAmount': 4072118.73706, 'uiAmountString': '4072118.73706'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599731804056', 'decimals': 9, 'uiAmount': 7599.731804056, 'uiAmountString': '7599.731804056'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713647633243', 'decimals': 6, 'uiAmount': 1713647.633243, 'uiAmountString': '1713647.633243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '751162111', 'decimals': 6, 'uiAmount': 751.162111, 'uiAmountString': '751.162111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3625092093786', 'decimals': 6, 'uiAmount': 3625092.093786, 'uiAmountString': '3625092.093786'}}], 'preBalances': [121763893741, 9204256, 2039280, 2039280, 20152871503, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8559129552, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599963688446, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3430379783', 'decimals': 6, 'uiAmount': 3430.379783, 'uiAmountString': '3430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18533267719', 'decimals': 6, 'uiAmount': 18533.267719, 'uiAmountString': '18533.267719'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3330667810953218', 'decimals': 6, 'uiAmount': 3330667810.953218, 'uiAmountString': '3330667810.953218'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '518536327363', 'decimals': 6, 'uiAmount': 518536.327363, 'uiAmountString': '518536.327363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4058441614', 'decimals': 6, 'uiAmount': 4058.441614, 'uiAmountString': '4058.441614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8557090272', 'decimals': 9, 'uiAmount': 8.557090272, 'uiAmountString': '8.557090272'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4135662209305', 'decimals': 6, 'uiAmount': 4135662.209305, 'uiAmountString': '4135662.209305'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599942629157', 'decimals': 9, 'uiAmount': 7599.942629157, 'uiAmountString': '7599.942629157'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713597693243', 'decimals': 6, 'uiAmount': 1713597.693243, 'uiAmountString': '1713597.693243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '731186111', 'decimals': 6, 'uiAmount': 731.186111, 'uiAmountString': '731.186111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3650570424932', 'decimals': 6, 'uiAmount': 3650570.424932, 'uiAmountString': '3650570.424932'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', '5ht281axHQXoQ2PWD6vrxxnHEa8TmsLuzs7XTDnmTdCt', '7QRKuCbdjxRjno55LE1GGFVKqxeFUWeNtUaLQ4a9Gz9X', '9fBpwxcudpLyJskhiiKmU8wPszeUuCB8sSjhPi44QuFb', 'B95oUgde4SfoekubbV1hbFanLBRV7UL26zXqcZZhHdrx', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'], 'addressTableLookups': [{'accountKey': '2z84tgaUYNWMwotQjmSpRygdH96m5M5VpUqZQH1L24UF', 'readonlyIndexes': [70, 68, 12], 'writableIndexes': [67, 64, 65, 66, 58, 63]}, {'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 40, 11, 1, 20], 'writableIndexes': [32, 49]}, {'accountKey': 'DWSgR97yTc3WENhkddFBkoBsute6mKpaJ5Kkfix8KWXb', 'readonlyIndexes': [225], 'writableIndexes': [219, 229, 188, 227, 222, 223]}, {'accountKey': 'EE8XintbVcFLm3CR3rNLfW5WcBKDtsniQwLKsWz3enYi', 'readonlyIndexes': [168, 173], 'writableIndexes': [169, 170, 171]}, {'accountKey': 'JBMZHmsCUZEfXpNPm4N1XQ2seJbDo3CFSfmQjK4mShDh', 'readonlyIndexes': [34, 40], 'writableIndexes': [37, 29, 38, 35, 33, 41, 39, 31]}], 'header': {'numReadonlySignedAccounts': 1, 'numReadonlyUnsignedAccounts': 3, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'KGAnEb', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [], 'data': '3QZwSzAJHXSo', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [39, 1, 2, 16, 3, 5, 38, 34, 41, 41, 37, 8, 16, 43, 39, 23, 24, 25, 15, 16, 41, 44, 36, 41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42, 36, 41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35, 46, 39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28, 8, 40], 'data': '2uadBoC4kUfkSytM1gJGnMJKGK8Uu9K455iqA8iRquZaLonKccX4BABoNf9v5VVL7q1N21BztbkGU7cw', 'programIdIndex': 8, 'stackHeight': 1}, {'accounts': [0, 4], 'data': '3Bxs4No5VVsho7hh', 'programIdIndex': 6, 'stackHeight': 1}], 'recentBlockhash': 'EZUJNZw94LezE4g9mf2Ku8FJ1dkMqyRQ4ieEUxBWnhMj'}, 'signatures': ['41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', '3pXHMYvd5xKeyxUMUNNPEWK2Meu6Kwnb3HYkFdNW4dbpY1dN72nL1e75H1oX8BrWfoNgRXz6gbpcW1RLttDavnGt']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: live_test.py:144

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-12 19:52:43,676 - __main__ - DEBUG - [DEBUG] Received trade_info: {"signature": "5qbjjcFhxCvrTHGekucWQZ1vQkg1Ymv7779yFJ748VkKsi6iu8rP1Z21LYKbtBrrDLMPwCWTjZ4BSUDhCByAhTCG", "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 248857 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C invoke [2]", "Program log: Instruction: SwapBaseInput", "Program data: QMbN6CYIceJI4udx59A3ofmMlP1m9B+Pj46toZZSB/5r+9rwnJg3BZlv5SAKAAAAtlc+b/E5AAAMmVgVAAAAACIxqNt3AAAAAAAAAAAAAAAAAAAAAAAAAAEHBy8FSrSNmH2k5ZaeYyzd843WQUE0naQbC2lbkdFcOgFKMZOdXl4qu+33PLDiIfHZfFZQAESzDEeFcAC2PkEXX6U2AAAAAAB4uwIAAAAAAAE=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 217120 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 207784 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C consumed 40848 of 240875 compute units", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]", "Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh5Hlw8AAAAAAKGPOhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 148467 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 142401 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 56610 of 192614 compute units", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123744 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 117910 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19743 of 132888 compute units", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 83032 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 74271 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 65162 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 46765 of 108843 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 60219 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 58316 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 51614 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 207568 of 254407 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 Pq5fS3oAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "timestamp": "2025-10-12 18:52:43.676305+00:00", "detection_method": "websocket_logs", "meta": {"computeUnitsConsumed": 208018, "costUnits": 217583, "err": null, "fee": 1327265, "innerInstructions": [{"index": 2, "instructions": [{"accounts": [6, 3, 1], "data": "3o6gTY92PWS3", "programIdIndex": 39, "stackHeight": 2}, {"accounts": [19, 42, 46, 28, 3, 5, 31, 30, 39, 39, 47, 32, 29], "data": "E73fXHPWvSR26xdrkcn61Mfy9PBXZeF11", "programIdIndex": 40, "stackHeight": 2}, {"accounts": [3, 47, 31, 19], "data": "gGFSQLtFifcMK", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [30, 32, 5, 42], "data": "gYC7zK6KnzT65", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [19, 25, 44, 11, 26, 27, 3, 20, 47, 36, 39, 39, 43], "data": "KcznxBaB6yLt1qxnuAtjGA3q", "programIdIndex": 45, "stackHeight": 2}, {"accounts": [3, 26, 19], "data": "3mAA1WCjWQ39", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [27, 20, 25], "data": "3axGPDMLwZFu", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [19, 22, 21, 20, 24, 23, 8, 43, 39], "data": "2d6h89NAF1vPVgxDFFpt5ctHNXr", "programIdIndex": 41, "stackHeight": 2}, {"accounts": [20, 23, 19], "data": "3axGPDMLwZFu", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [24, 21, 22], "data": "3NuWBSfJDtT1", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [17, 34, 14, 16, 21, 5, 32, 38, 15, 34, 19, 39, 39, 33, 34, 18, 13, 12], "data": "PgQWtn8oziwwmBJTsh8GDDrdH3tAuFKtT", "programIdIndex": 34, "stackHeight": 2}, {"accounts": [21, 38, 16, 19], "data": "gpeTSRCfp74UY", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [14, 32, 5, 17], "data": "gTyviGyM6hC53", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [33], "data": "yCGxBopjnVNQkNP5usq1Pp1LotWgFqhshb2FwZvZaweHPpnc6jtd3TYTRQKLLqwJB3B3AvrSdvAaw1d3JCvZJyhaZft26fdbqfh6CTFkcvxYo64ekV4ikyVVmGwScaJaML7PaE4ShmAfMADuCyTh85PQmuUoeGBAZLJYpPSjnc7QMtXdmwni9DCLD6h7XDLYrZLkr3", "programIdIndex": 34, "stackHeight": 3}, {"accounts": [35], "data": "4KbP49BdVApjtHuXZdNzDMRzUrFZqdN9HrSffmYR1ngUfG8AxF9yxqkSPQhzo1FH8DcWEYzgW7gThnehHfaYLLHcUPBMFT4hunDc4scFAugqeVeh4A1NaVfFniBRPfDXbAKjPFRe5nnDjmwuSQ8rV5A8DMGwiePWaH1kZeB2t8gdzosXTx3nQmJ7tNKHSoTTbpwd88k3S1mP9ARCNT5CdcAyC9Lh7ZuQNUuScM45UxcpdN5vuFDVzdXuDPLrSKXjQVvF5zYSufRDnsJyiMbVNUqGymvjZWsVoxj7Y5jQBr9LskESY8F91LCr5KTvyTiNPdjLp95p7erPpYpiUZqB5goFZU68NY31bHEgJPb8TXBQ3AdpGqL1Xi3tjAYcXMt1emenAhrTicnPL3DviwMycqEeUnxHgZ5JYijHh6V4Gx9xxbRix41FF4TqQwwrg51VpUAMQM42pCoxSL1qy", "programIdIndex": 10, "stackHeight": 2}, {"accounts": [6, 3, 1], "data": "3EkbcbviRwzF", "programIdIndex": 39, "stackHeight": 2}, {"accounts": [5, 4, 19], "data": "3PweZcmXEcz3", "programIdIndex": 39, "stackHeight": 2}]}], "loadedAddresses": {"readonly": ["632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "D1ZN9Wj1fRSUQfCjhvnu1hqDMT7hzjzBBpi12nVniYD6", "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo", "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "jitodontfront11111111111JustUseJupiterU1tra", "So11111111111111111111111111111111111111112", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C", "goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j", "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "Sysvar1nstructions1111111111111111111111111", "By9zHEbZJvYrBws27SqPXggfSAH3fjnJcdxKgdogyXUm", "SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF", "G95xxie3XbkCqtE39GgQ9Ggc7xBC8Uceve7HFDEFApkc", "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB"], "writable": ["4LzG4fCcbxMYDYzPcmfRzAQeVSkkB2qeaZnHDVK4zrkp", "5oQuwHERHx3E5TptB8HpeUWfbUs7EzjboFZiFyAkiFes", "9PBsqbBF1zEDck2YbkeAFNmAFMH75ZUWW7BA2Wv2Z7SY", "Ax3hzMZDuJjRoHuj86MkF9p5Vq8bWFKC7GZBs5mgfntq", "C4Y3AhocJzHZFK3gjjanjCxoFxBjZsBpo8BdU8dEbx2L", "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "FamNAW9SyTjDivRAPAaZfzSqgDgbAHNVb7oxYSpipoSS", "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "E6LAwCLSHLkDCoMXZPtnDtpcvCYWcs3ZZLHLreiFwjUi", "qqdJ4z1yu4sTbAitwXZsGNDoGZFgL2HfVKSVwAXWCfq", "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "Gsy5Zr7Vxn5KckAbduPHHGR1qzPJ4w3GSYmcinWAkhrC", "pKiUC9hDXv52xqU1p3BKypV9AQjAMgfZUGRnoBsdkKm", "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "CRF6Tegjtv3k9tuvKKbXroq4UmKXh9ZP92tn17sjjsFY", "CT8B2qJAqy93GAU5Qor9s5xGGQEoiEwSSNRPAaDFYrgL", "5uX2hmJJMUwXynsisoiCbQfD9mkos3uCkqhDgQWPRDSk", "C45FMw2N3n5ZE5A74jkvL6LNAjSLxiL6bn2oESu29rFh", "Ekt1x1kLzMxiq9XU2oPHU1GDHZg7SKKZTqjpEkD6WMoH", "HpHh4LdNtcfGrJAjuABcdWUP1fAADr3USvpkX81rnrki"]}, "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 248857 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C invoke [2]", "Program log: Instruction: SwapBaseInput", "Program data: QMbN6CYIceJI4udx59A3ofmMlP1m9B+Pj46toZZSB/5r+9rwnJg3BZlv5SAKAAAAtlc+b/E5AAAMmVgVAAAAACIxqNt3AAAAAAAAAAAAAAAAAAAAAAAAAAEHBy8FSrSNmH2k5ZaeYyzd843WQUE0naQbC2lbkdFcOgFKMZOdXl4qu+33PLDiIfHZfFZQAESzDEeFcAC2PkEXX6U2AAAAAAB4uwIAAAAAAAE=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 217120 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 207784 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C consumed 40848 of 240875 compute units", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]", "Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh5Hlw8AAAAAAKGPOhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 148467 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 142401 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 56610 of 192614 compute units", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123744 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 117910 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19743 of 132888 compute units", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 83032 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 74271 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 65162 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 46765 of 108843 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 60219 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 58316 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 51614 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 207568 of 254407 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 Pq5fS3oAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "postBalances": [121435305597, 9760911, 21545145300, 2039280, 2039280, 2039280, 2039280, 1, 0, 1, 2729681025, 7298979842, 71437440, 71437440, 2039280, 23385600, 67490882898, 7182720, 71437440, 171551098, 2039280, 2415112199, 6849547, 2039281, 2776792400852, 12917769, 2039280, 2039280, 5324400, 29252880, 2039280, 2039280, 1461600, 4000419, 32941452, 3596047, 418938902554, 1000004, 1171250707549, 5289313643, 45791780, 1142441, 1221496159635, 0, 2060160, 1141441, 2533440, 98390921], "postTokenBalances": [{"accountIndex": 3, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "6360473", "decimals": 6, "uiAmount": 6.360473, "uiAmountString": "6.360473"}}, {"accountIndex": 4, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "525250571838", "decimals": 6, "uiAmount": 525250.571838, "uiAmountString": "525250.571838"}}, {"accountIndex": 5, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "7677766270", "decimals": 6, "uiAmount": 7677.76627, "uiAmountString": "7677.76627"}}, {"accountIndex": 6, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "366205648", "decimals": 6, "uiAmount": 366.205648, "uiAmountString": "366.205648"}}, {"accountIndex": 14, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "26626085502162", "decimals": 6, "uiAmount": 26626085.502162, "uiAmountString": "26626085.502162"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "67488843618", "decimals": 9, "uiAmount": 67.488843618, "uiAmountString": "67.488843618"}}, {"accountIndex": 20, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2685286213", "decimals": 6, "uiAmount": 2685.286213, "uiAmountString": "2685.286213"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2413072917", "decimals": 9, "uiAmount": 2.413072917, "uiAmountString": "2.413072917"}}, {"accountIndex": 23, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "371709943212", "decimals": 6, "uiAmount": 371709.943212, "uiAmountString": "371709.943212"}}, {"accountIndex": 24, "mint": "So11111111111111111111111111111111111111112", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2776790361568", "decimals": 9, "uiAmount": 2776.790361568, "uiAmountString": "2776.790361568"}}, {"accountIndex": 26, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "145137051061", "decimals": 6, "uiAmount": 145137.051061, "uiAmountString": "145137.051061"}}, {"accountIndex": 27, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "64414390274", "decimals": 6, "uiAmount": 64414.390274, "uiAmountString": "64414.390274"}}, {"accountIndex": 30, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "63202802214455", "decimals": 6, "uiAmount": 63202802.214455, "uiAmountString": "63202802.214455"}}, {"accountIndex": 31, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "48032353295", "decimals": 6, "uiAmount": 48032.353295, "uiAmountString": "48032.353295"}}], "preBalances": [121436963178, 9760911, 21544814984, 2039280, 2039280, 2039280, 2039280, 1, 0, 1, 2729681025, 7298979842, 71437440, 71437440, 2039280, 23385600, 67452971546, 7182720, 71437440, 171551098, 2039280, 2415112199, 6849547, 2039281, 2776830312204, 12917769, 2039280, 2039280, 5324400, 29252880, 2039280, 2039280, 1461600, 4000419, 32941452, 3596047, 418938902554, 1000004, 1171250707549, 5289313643, 45791780, 1142441, 1221496159635, 0, 2060160, 1141441, 2533440, 98390921], "preTokenBalances": [{"accountIndex": 3, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "5591442", "decimals": 6, "uiAmount": 5.591442, "uiAmountString": "5.591442"}}, {"accountIndex": 4, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "0", "decimals": 6, "uiAmount": null, "uiAmountString": "0"}}, {"accountIndex": 5, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "7677766270", "decimals": 6, "uiAmount": 7677.76627, "uiAmountString": "7677.76627"}}, {"accountIndex": 6, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "732411296", "decimals": 6, "uiAmount": 732.411296, "uiAmountString": "732.411296"}}, {"accountIndex": 14, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "26636549732846", "decimals": 6, "uiAmount": 26636549.732846, "uiAmountString": "26636549.732846"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "67450932266", "decimals": 9, "uiAmount": 67.450932266, "uiAmountString": "67.450932266"}}, {"accountIndex": 20, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2685286213", "decimals": 6, "uiAmount": 2685.286213, "uiAmountString": "2685.286213"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2413072917", "decimals": 9, "uiAmount": 2.413072917, "uiAmountString": "2.413072917"}}, {"accountIndex": 23, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "371702635308", "decimals": 6, "uiAmount": 371702.635308, "uiAmountString": "371702.635308"}}, {"accountIndex": 24, "mint": "So11111111111111111111111111111111111111112", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2776828272920", "decimals": 9, "uiAmount": 2776.82827292, "uiAmountString": "2776.82827292"}}, {"accountIndex": 26, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "145129742328", "decimals": 6, "uiAmount": 145129.742328, "uiAmountString": "145129.742328"}}, {"accountIndex": 27, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "64421698178", "decimals": 6, "uiAmount": 64421.698178, "uiAmountString": "64421.698178"}}, {"accountIndex": 30, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "63717588555609", "decimals": 6, "uiAmount": 63717588.555609, "uiAmountString": "63717588.555609"}}, {"accountIndex": 31, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "47674225411", "decimals": 6, "uiAmount": 47674.225411, "uiAmountString": "47674.225411"}}], "rewards": [], "status": {"Ok": null}}, "transaction": {"message": {"accountKeys": ["gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB", "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "77N86XfcBSAvcGNPYMAVjjyf2feUJwmUoiJ96HzPtySd", "8cHRSqBtNw4sbzq1aSGZYaMPsfG7CsksZLik9AWF29z", "9itSauTyTV1TqepGGSFE1Xqpr8QrwU896ejDqoCsc41Y", "FswGbE4Drue6KiDYzXWfhoSWdtnhJLHarc4xqeDZU2Xq", "FX2cJi3TQ7fehdNEo9P4y5Ye2FR1bt6cSKmYJ9Md95eN", "11111111111111111111111111111111", "9FcdAZrMX1zxd3mBDAzCqfoYCw3ubRrG3Ch9ZnTRmq8g", "ComputeBudget111111111111111111111111111111", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", "QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ"], "addressTableLookups": [{"accountKey": "2MU934HtM4i8wzemrCcx1TfSHer5ryGPt9UKL81VgNJ6", "readonlyIndexes": [29, 30, 62], "writableIndexes": [65, 24, 27, 25, 28, 64, 31]}, {"accountKey": "3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW", "readonlyIndexes": [0, 40, 1, 23, 20], "writableIndexes": [13, 51, 34]}, {"accountKey": "D4QBMf27hQbL2JkaM1xy5gvQavLpPyXqf4SMcEsWwg43", "readonlyIndexes": [6, 206, 0, 201], "writableIndexes": [203, 207, 204]}, {"accountKey": "DMQiFwkdPjts3db8RiYpeiSu4R4CyBjUVhX2v7y8HUWF", "readonlyIndexes": [52, 55], "writableIndexes": [51, 53, 59]}, {"accountKey": "ESb1zo7dy5VvQ7yfuWqmkpw6Fm3bVi5PEcqPrRUB1jeu", "readonlyIndexes": [251, 244], "writableIndexes": [245, 250, 249, 246]}], "header": {"numReadonlySignedAccounts": 1, "numReadonlyUnsignedAccounts": 5, "numRequiredSignatures": 2}, "instructions": [{"accounts": [], "data": "LKdZq1", "programIdIndex": 9, "stackHeight": 1}, {"accounts": [], "data": "3skHkfbuoXPV", "programIdIndex": 9, "stackHeight": 1}, {"accounts": [19, 1, 6, 3, 5, 4, 47, 32, 39, 39, 35, 10, 3, 40, 19, 42, 46, 28, 3, 5, 31, 30, 39, 39, 47, 32, 29, 45, 19, 25, 44, 11, 26, 27, 3, 20, 47, 36, 39, 39, 43, 41, 19, 22, 21, 20, 24, 23, 8, 43, 39, 34, 17, 34, 14, 16, 21, 5, 32, 38, 15, 34, 19, 39, 39, 33, 34, 18, 13, 12, 10, 37], "data": "2uadBoC4kUfkUzUFsLsCUVVvSkycFZqiQaEFzCJ4hkQLvh6N3egyDzFA2nr5xBAoBJrSYjNvcX7KDBXH", "programIdIndex": 10, "stackHeight": 1}, {"accounts": [0, 2], "data": "3Bxs4DaLPq2VNELw", "programIdIndex": 7, "stackHeight": 1}], "recentBlockhash": "3AxLkueqDtPJz3T3JALraJpfye5S3FQs4UQJWZZwQxRE"}, "signatures": ["5qbjjcFhxCvrTHGekucWQZ1vQkg1Ymv7779yFJ748VkKsi6iu8rP1Z21LYKbtBrrDLMPwCWTjZ4BSUDhCByAhTCG", "5mpH1hSbF9BXgSu7sYmoeoZh4G46DpQAn2ntyia96MaUAwRPrh8pLMJaAYzaA2oAGtZSr5xcqqLnek8GAm9bEbW8"]}, "parsed_tx": {"dex": "unknown", "action": "unknown", "mint": null, "amount": null, "signature": null, "source_wallet": null, "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "unknown", "confidence": 0}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: live_test_II.py:50

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-12 18:55:28,558 - __main__ - DEBUG - [DEBUG] Received trade_info: {"signature": "3v9GsuiHTeGmJNJbRNzJGj9ZQ5RhGGgKwZrvvZZvYy7KKhiaRbUqLa3okH8TtumqY4ZU74E2FcWgJExjYFTEJpyC", "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 112754 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]", "Program log: ray_log: AyIM2xIUAAAAAAAAAAAAAAABAAAAAAAAAA2WUGoUAAAAJ8lResUCAABJbbku8ykAADw6BFIBAAAA", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 91974 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 84860 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 25831 of 105380 compute units", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]", "Program log: Instruction: swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66442 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 60534 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/ufnQT/ggSLdQ/BT3+/o5a1Dxa89BYqFP/RkXA2L0UEcBfZyrmuHnPr9+QuC/1V2cVtYRScnWsSHRF+vmW3fGN5XioGHT74cJwEbZ9oaJ31u0Nm/LcdOppcK9j//h69RTfaAuMhjLvptLWB32/hF3e9ERYSX54eAxcJmWVvl+0ZYzm8cCt0LXR75HfzZjxcUGQd46hztP/GV4Np15rP2WBjTBIrHI4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FinNoG4eAxcF4TSPl+0ZYzm8cCt0LXR76s7xbZxcUGQc3wMcbW/WV4xvVDuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 40513 of 76513 compute units", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 34275 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 32023 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 25587 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 95625 of 116436 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 f26VQQAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "timestamp": "2025-10-12 17:55:28.557756+00:00", "detection_method": "websocket_logs", "meta": {"computeUnitsConsumed": 96075, "costUnits": 102072, "err": null, "fee": 88330, "innerInstructions": [{"index": 2, "instructions": [{"accounts": [3, 4, 1], "data": "3K9tj26pg5EP", "programIdIndex": 25, "stackHeight": 2}, {"accounts": [25, 17, 26, 16, 18, 4, 14, 23], "data": "9nznFBXsXGEtbXLdbbuBQdD", "programIdIndex": 27, "stackHeight": 2}, {"accounts": [4, 18, 23], "data": "3K9tj26pg5EP", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [16, 14, 26], "data": "3PXqUYe8heWj", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [11, 9, 10, 13, 12, 14, 15, 23, 25, 19], "data": "4Q7KEgP54q45GpgmEPEvVcB", "programIdIndex": 20, "stackHeight": 2}, {"accounts": [14, 10, 23], "data": "3PXqUYe8heWj", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [12, 15, 12], "data": "3fYBp4GtthRh", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [21], "data": "RkQoknrFGESHWQ2WBEU8ZchvjAkGNA8o8CneJpdndrKUUiBtSBbrEFTk5Dv3oybgNqNh8j6VMgCrnNyvQ8sxHcyjboDEHiUS1so6f28yxrcPMYaRfMeV6ZZX2FgyTn7YXosmTBE8ZiujQgN8Cui5SZjirChSgYfJyjYCDADaDsYH1pbUcpBsKP2Jm8LE1MW591H8DKGYaPprJ4D2P1BhvtSsaTHdxwQAnTHt2zsuT6jxQyDkVxWDqy", "programIdIndex": 8, "stackHeight": 2}, {"accounts": [15, 15, 23], "data": "3JDwL7DuHRdy", "programIdIndex": 25, "stackHeight": 2}, {"accounts": [15, 2, 23], "data": "3amp5dzsRGFy", "programIdIndex": 25, "stackHeight": 2}]}], "loadedAddresses": {"readonly": ["Sysvar1nstructions1111111111111111111111111", "ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY", "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "jitodontfront11111111111JustUseJupiterU1tra", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump"], "writable": ["8943FQrCirbp2kNk8cVKS5P7vjNzhas3L9fDoqpnv8mw", "CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU", "f2FsCiguf172T9achZzJcTjJuM9BLf5nmf18WKaaWUZ", "fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1", "GC2yqyD6ZYnAXc8DNy4d7uiYnQ9TBhZBA4WMPbsMKUxK", "2p29nqD7DN1PczBMmgrFdtYKTfv6rJ7H3yMut4eu7nYT", "5SPztfEn1VAaWDBAXjQKwVrGbr6e8g3F6JJnUc9eCuSe", "4YAgjfFQYjqezqco9y6ZtHN2idDgazFC6ivPLmsMSEQU", "AemYRZmJryzAQ9Z4RLfUBLnPRUY5ecooc94EJvemfti4", "EqmuG7mdMjLfdGxXDEasm3gc16RGhZ3dAgcVfPmkAJSC"]}, "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 112754 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]", "Program log: ray_log: AyIM2xIUAAAAAAAAAAAAAAABAAAAAAAAAA2WUGoUAAAAJ8lResUCAABJbbku8ykAADw6BFIBAAAA", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 91974 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 84860 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 25831 of 105380 compute units", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]", "Program log: Instruction: swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66442 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 60534 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/ufnQT/ggSLdQ/BT3+/o5a1Dxa89BYqFP/RkXA2L0UEcBfZyrmuHnPr9+QuC/1V2cVtYRScnWsSHRF+vmW3fGN5XioGHT74cJwEbZ9oaJ31u0Nm/LcdOppcK9j//h69RTfaAuMhjLvptLWB32/hF3e9ERYSX54eAxcJmWVvl+0ZYzm8cCt0LXR75HfzZjxcUGQd46hztP/GV4Np15rP2WBjTBIrHI4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FinNoG4eAxcF4TSPl+0ZYzm8cCt0LXR76s7xbZxcUGQc3wMcbW/WV4xvVDuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 40513 of 76513 compute units", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 34275 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 32023 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 25587 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 95625 of 116436 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 f26VQQAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "postBalances": [123721736473, 9160838, 2039280, 2039280, 2039280, 22519994331, 1, 1, 2729681025, 8352000, 2786822252190, 52784640, 2079311, 8352000, 995823284, 2039380, 3041515066351, 70421476, 2039281, 0, 1141441, 3596047, 418938902554, 214648494, 1000004, 5289313643, 32335376897, 2817789979, 83262188269], "postTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4991922524", "decimals": 6, "uiAmount": 4991.922524, "uiAmountString": "4991.922524"}}, {"accountIndex": 3, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "0", "decimals": 6, "uiAmount": null, "uiAmountString": "0"}}, {"accountIndex": 4, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1467320811", "decimals": 6, "uiAmount": 1467.320811, "uiAmountString": "1467.320811"}}, {"accountIndex": 10, "mint": "So11111111111111111111111111111111111111112", "owner": "CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2786820106354", "decimals": 9, "uiAmount": 2786.820106354, "uiAmountString": "2786.820106354"}}, {"accountIndex": 12, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "134225154020", "decimals": 6, "uiAmount": 134225.15402, "uiAmountString": "134225.15402"}}, {"accountIndex": 14, "mint": "So11111111111111111111111111111111111111112", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "993782000", "decimals": 9, "uiAmount": 0.993782, "uiAmountString": "0.993782"}}, {"accountIndex": 15, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3073221114", "decimals": 6, "uiAmount": 3073.221114, "uiAmountString": "3073.221114"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3041513017067", "decimals": 9, "uiAmount": 3041.513017067, "uiAmountString": "3041.513017067"}}, {"accountIndex": 18, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "46210653387115", "decimals": 6, "uiAmount": 46210653.387115, "uiAmountString": "46210653.387115"}}], "preBalances": [123721845385, 9160838, 2039280, 2039280, 2039280, 22519973749, 1, 1, 2729681025, 8352000, 2781151276130, 52784640, 2079311, 8352000, 995823284, 2039380, 3047186042411, 70421476, 2039281, 0, 1141441, 3596047, 418938902554, 214648494, 1000004, 5289313643, 32335376897, 2817789979, 83262188269], "preTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3891610333", "decimals": 6, "uiAmount": 3891.610333, "uiAmountString": "3891.610333"}}, {"accountIndex": 3, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "86215691298", "decimals": 6, "uiAmount": 86215.691298, "uiAmountString": "86215.691298"}}, {"accountIndex": 4, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1467320811", "decimals": 6, "uiAmount": 1467.320811, "uiAmountString": "1467.320811"}}, {"accountIndex": 10, "mint": "So11111111111111111111111111111111111111112", "owner": "CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2781149130294", "decimals": 9, "uiAmount": 2781.149130294, "uiAmountString": "2781.149130294"}}, {"accountIndex": 12, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "135326677887", "decimals": 6, "uiAmount": 135326.677887, "uiAmountString": "135326.677887"}}, {"accountIndex": 14, "mint": "So11111111111111111111111111111111111111112", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "993782000", "decimals": 9, "uiAmount": 0.993782, "uiAmountString": "0.993782"}}, {"accountIndex": 15, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3072009438", "decimals": 6, "uiAmount": 3072.009438, "uiAmountString": "3072.009438"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3047183993127", "decimals": 9, "uiAmount": 3047.183993127, "uiAmountString": "3047.183993127"}}, {"accountIndex": 18, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "46124437695817", "decimals": 6, "uiAmount": 46124437.695817, "uiAmountString": "46124437.695817"}}], "rewards": [], "status": {"Ok": null}}, "transaction": {"message": {"accountKeys": ["gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB", "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "46pxCL7Upm36T5YbA5od3KfY9QVRwY8aWmuzSnzzmUcA", "8ZK9R45iiJhUkXrKxy9dFcuEnvxLfJMdDwKAZM5wZQAR", "dWxMwYfmqkkhCddeorj61EA4bRcwBbRnATX7vepPj2p", "FzESY59j4xCef1EjqoprVBDXEFTWcrx8hGq6AYYvGH1v", "11111111111111111111111111111111", "ComputeBudget111111111111111111111111111111", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"], "addressTableLookups": [{"accountKey": "2iUJxrahG52bPemKUWw8CSceESan6K75M6XwfuRmtjcS", "readonlyIndexes": [42, 44], "writableIndexes": [43, 40, 45, 38, 41]}, {"accountKey": "3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW", "readonlyIndexes": [0, 40, 11, 1, 20], "writableIndexes": [32, 49]}, {"accountKey": "FTZdCrncV1GHwm56C766vJxrHGPUpZB8VBDaoctNTCSv", "readonlyIndexes": [19, 46, 43], "writableIndexes": [153, 155, 156]}], "header": {"numReadonlySignedAccounts": 1, "numReadonlyUnsignedAccounts": 3, "numRequiredSignatures": 2}, "instructions": [{"accounts": [], "data": "E7DqgB", "programIdIndex": 7, "stackHeight": 1}, {"accounts": [], "data": "3GquDG1FqyTV", "programIdIndex": 7, "stackHeight": 1}, {"accounts": [23, 1, 3, 4, 15, 2, 28, 22, 25, 25, 21, 8, 15, 27, 25, 17, 26, 16, 18, 4, 14, 23, 20, 11, 9, 10, 13, 12, 14, 15, 23, 25, 19, 24], "data": "6BngFxsVPaKrU5Q1biopYgsGgBee1bGciouzeHXAousyEox3Gsbr14abmyKji1", "programIdIndex": 8, "stackHeight": 1}, {"accounts": [0, 5], "data": "3Bxs4HyDhLXVdjQ3", "programIdIndex": 6, "stackHeight": 1}], "recentBlockhash": "5NK3LC7HExR55yjW1ABktqKHM6buRQBPdTAMzMPokChU"}, "signatures": ["3v9GsuiHTeGmJNJbRNzJGj9ZQ5RhGGgKwZrvvZZvYy7KKhiaRbUqLa3okH8TtumqY4ZU74E2FcWgJExjYFTEJpyC", "3zZYtaTYpAyu8RL3dC9rEgcqvdUzydjWd67MBEQWAvJ7xz6y4i1JfHyBBLojLoEjfag174Fzbim46dyngfZduHeD"]}, "parsed_tx": {"dex": "unknown", "action": "unknown", "mint": null, "amount": null, "signature": null, "source_wallet": null, "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "unknown", "confidence": 0}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: live_test_III.py:51

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-12 18:55:40,201 - __main__ - DEBUG - [DEBUG] Received trade_info: {"signature": "3gLH2B4rDTgq8qMjSKh61h9AtbZn36abXHS2UktaTZS1eggAFGA73RNEXPmCPXSw8dbSVu4coKQQ7JCnNpyskQCv", "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 186300 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb consumed 3096 of 180951 compute units", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 175024 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 42791 of 210584 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 130802 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123009 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZSwbiOzRqOUKdaF59hqnk/X414MJlQxyEvWyJLEbfQ/gFjXcUkmcITMAAAAAAAAAAAslkPrT+AEzAAAAAAAAAAAKC7aL0AAAAA63KtBgAAAAAAAAAAAAAAAAAAAAAAAAAAxd8QAAAAAAB7hQIAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 49650 of 164497 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 72455 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 64753 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZPyvg2fhqvmAEvwpTa+l2JaZFOoQ0YSwIzBjan3NHI9gExzQIUVRHsWAIAAAAAAAAAgNIlFrR/6VgCAAAAAAAAAOtyrQYAAAAAyyDJJAAAAAAAAAAAAAAAAAAAAAAAAAAAJ0wAAAAAAABgCwAAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 54962 of 111553 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 54816 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 52564 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 46128 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 177486 of 218838 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 78S+JAAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "timestamp": "2025-10-12 17:55:40.200530+00:00", "detection_method": "websocket_logs", "meta": {"computeUnitsConsumed": 177936, "costUnits": 187276, "err": null, "fee": 111825, "innerInstructions": [{"index": 2, "instructions": [{"accounts": [29, 16, 30, 27, 6, 25, 43, 39, 28, 44, 1, 41, 40, 33, 42, 44, 11, 10, 14], "data": "fx9RHbGFfZ9dVZGcnvi17XZDninrTwuEUzcXf5", "programIdIndex": 44, "stackHeight": 2}, {"accounts": [42], "data": "yCGxBopjnVNQkNP5usq1PoiCnL8LHyZvPRm5uDStNq7g14uayjoyheSQ3MpKeUUpNFZx9PnsczEYwyiNa2tyNF9CX5HF87hDhUX7TMqwGGhSxDv3N97NVvH74aHCeGS8K4QAQMXayoGkCNnQKKVrZS2Xi8fB23zj7aFcYiQ9rvFcgnmaE4VmC3bwzpEQWt5zUpeqwm", "programIdIndex": 44, "stackHeight": 3}, {"accounts": [6, 43, 30, 1], "data": "iQhWu1CGDz2vU", "programIdIndex": 41, "stackHeight": 3}, {"accounts": [27, 39, 25, 29], "data": "i9cPwL1rydo6p", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [40, 37, 19, 25, 21, 3, 20, 7, 12, 5, 31], "data": "59p8WydnSZtVSnejym9vy2cReqgJNDdtMYbk7foEm62n7WxHXASY3oMrf2", "programIdIndex": 34, "stackHeight": 2}, {"accounts": [25, 21, 37], "data": "3gLs8vwRjgqM", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [20, 3, 19], "data": "3tqhiuBKVS23", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [40, 37, 23, 3, 22, 26, 24, 8, 4, 13, 32], "data": "59p8WydnSZtX8kdsj2YYZMLAPjdABpZWQ1WSUK4e5K4gQcykKV8CSTdUTr", "programIdIndex": 34, "stackHeight": 2}, {"accounts": [3, 22, 37], "data": "3tqhiuBKVS23", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [24, 26, 23], "data": "3oSAD44x5Vwd", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [35], "data": "2C3FxF4wtCk1WPKYcjNvfKxBQp63XuDdX4hcikNH3TZECZZDX6cg4mZDsLxWxh5BKovt6F8pDNn3gYQPSpYfUxAQo6Q4EqXcYAkGiZF7W3kiqgcSyUpUnuRjbgHbLaVEXDvuKRkooqYkduEZui8Wv5ZdYG8uNkmihegVq42vQzX13tbTz9k1LWynm2VaLjJPYE9ZFMsqxrJ5bUyiC6QhCkJy8inVrufcTQh1DbSGFQ7goHG7DPp6A1RSC3AFZ9BSdSGUXm1RSdwzXEwv1FmLwY2yrVkifhjSqqa7sdBMna22sEmyftuQW9CTPM5zRgVPY9wJj56Z3Vd9exRb3e4vKkEBhySiiH5iKcjq", "programIdIndex": 18, "stackHeight": 2}, {"accounts": [26, 26, 37], "data": "3rKHgTZRH5Zq", "programIdIndex": 40, "stackHeight": 2}, {"accounts": [26, 2, 37], "data": "3uZcntACUGvT", "programIdIndex": 40, "stackHeight": 2}]}], "loadedAddresses": {"readonly": ["4zKPdJqfhFW9FRPbUd3iuZmX4jHi2Lwsqbvh86B5AYEK", "8HchJS2ufNvZv6i3Q6zRLvBDpVe1P72ArR86p2hUHvg6", "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr", "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc", "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "jitodontfront11111111111JustUseJupiterU1tra", "So11111111111111111111111111111111111111112", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "D1ZN9Wj1fRSUQfCjhvnu1hqDMT7hzjzBBpi12nVniYD6", "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"], "writable": ["6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "EQCDoN8WHzYxCRmhxHBSEYCL5muMaZ2HHWbY121fEYsu", "Gg5msGGYPXGt9JpAC5oVdimjWZEXzKpunRDALaJ1Ny1U", "2KiAy13bDCMGfJ8MqbpTC7g3CunHjLQYMs3wK14XM5LZ", "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "GoJSsR8AwPWCbbbFfwVtT97vTEdKs3kwGkahgvhiybMU", "GyY4VgEpJQhiKZRAJJmoM4hv5Q2xC4pvX68MGrGidxyG", "HoBCz6z9AG92GGozMWEkBPE9UhQWGZ5cXhYcjoGJvwP2", "6qxaasNgXsfVp8tKkoJavp29hZYiDrcEirsS3oAsYCLc", "AFH1UXkECQwYoWkkCSydxU8UGciH8jxqB9EebV1NJVHs", "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "DfWWLJvVHDM9byp6y7Rpw5Rx4mGizSwB5GEoUMegi3z8"]}, "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 186300 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb consumed 3096 of 180951 compute units", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 175024 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 42791 of 210584 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 130802 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123009 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZSwbiOzRqOUKdaF59hqnk/X414MJlQxyEvWyJLEbfQ/gFjXcUkmcITMAAAAAAAAAAAslkPrT+AEzAAAAAAAAAAAKC7aL0AAAAA63KtBgAAAAAAAAAAAAAAAAAAAAAAAAAAxd8QAAAAAAB7hQIAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 49650 of 164497 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 72455 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 64753 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZPyvg2fhqvmAEvwpTa+l2JaZFOoQ0YSwIzBjan3NHI9gExzQIUVRHsWAIAAAAAAAAAgNIlFrR/6VgCAAAAAAAAAOtyrQYAAAAAyyDJJAAAAAAAAAAAAAAAAAAAAAAAAAAAJ0wAAAAAAABgCwAAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 54962 of 111553 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 54816 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 52564 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 46128 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 177486 of 218838 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 78S+JAAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "postBalances": [123712265076, 9160839, 2039280, 2039280, 70407360, 70407360, 2157600, 70407360, 70407360, 22712666216, 71437440, 71437441, 70407360, 70407360, 71437440, 1, 11859840, 1, 2729681025, 10175860, 2039282, 11674462861006, 2039285, 5444104, 2039284, 1492977215, 2039280, 4301610167098, 23385600, 7183729, 2129760, 0, 0, 521498895, 1161445, 3596047, 418938902554, 122611498, 1000004, 1171250707549, 5289313643, 1151489, 4000419, 1805481849230, 32941452], "postTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "5608404555", "decimals": 6, "uiAmount": 5608.404555, "uiAmountString": "5608.404555"}}, {"accountIndex": 3, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1998298", "decimals": 6, "uiAmount": 1.998298, "uiAmountString": "1.998298"}}, {"accountIndex": 6, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "0", "decimals": 9, "uiAmount": null, "uiAmountString": "0"}}, {"accountIndex": 20, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "225575433987", "decimals": 6, "uiAmount": 225575.433987, "uiAmountString": "225575.433987"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "11674460368718", "decimals": 9, "uiAmount": 11674.460368718, "uiAmountString": "11674.460368718"}}, {"accountIndex": 22, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "514139470456", "decimals": 6, "uiAmount": 514139.470456, "uiAmountString": "514139.470456"}}, {"accountIndex": 24, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1592142888516", "decimals": 6, "uiAmount": 1592142.888516, "uiAmountString": "1592142.888516"}}, {"accountIndex": 25, "mint": "So11111111111111111111111111111111111111112", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1490936932", "decimals": 9, "uiAmount": 1.490936932, "uiAmountString": "1.490936932"}}, {"accountIndex": 26, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1560224830", "decimals": 6, "uiAmount": 1560.22483, "uiAmountString": "1560.22483"}}, {"accountIndex": 27, "mint": "So11111111111111111111111111111111111111112", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4301608127814", "decimals": 9, "uiAmount": 4301.608127814, "uiAmountString": "4301.608127814"}}, {"accountIndex": 30, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "5971184163803041", "decimals": 9, "uiAmount": 5971184.163803041, "uiAmountString": "5971184.163803041"}}], "preBalances": [123712403357, 9160839, 2039280, 2039280, 70407360, 70407360, 2157600, 70407360, 70407360, 22712639760, 71437440, 71437441, 70407360, 70407360, 71437440, 1, 11859840, 1, 2729681025, 10175860, 2039282, 11671285103406, 2039285, 5444104, 2039284, 1492977215, 2039280, 4304787924698, 23385600, 7183729, 2129760, 0, 0, 521498895, 1161445, 3596047, 418938902554, 122611498, 1000004, 1171250707549, 5289313643, 1151489, 4000419, 1805481849230, 32941452], "preTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4991922524", "decimals": 6, "uiAmount": 4991.922524, "uiAmountString": "4991.922524"}}, {"accountIndex": 3, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1998298", "decimals": 6, "uiAmount": 1.998298, "uiAmountString": "1.998298"}}, {"accountIndex": 6, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "6480659491765", "decimals": 9, "uiAmount": 6480.659491765, "uiAmountString": "6480.659491765"}}, {"accountIndex": 20, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "225687464430", "decimals": 6, "uiAmount": 225687.46443, "uiAmountString": "225687.46443"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "11671282611118", "decimals": 9, "uiAmount": 11671.282611118, "uiAmountString": "11671.282611118"}}, {"accountIndex": 22, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "514027440013", "decimals": 6, "uiAmount": 514027.440013, "uiAmountString": "514027.440013"}}, {"accountIndex": 24, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1592760049423", "decimals": 6, "uiAmount": 1592760.049423, "uiAmountString": "1592760.049423"}}, {"accountIndex": 25, "mint": "So11111111111111111111111111111111111111112", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1490936932", "decimals": 9, "uiAmount": 1.490936932, "uiAmountString": "1.490936932"}}, {"accountIndex": 26, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1559545954", "decimals": 6, "uiAmount": 1559.545954, "uiAmountString": "1559.545954"}}, {"accountIndex": 27, "mint": "So11111111111111111111111111111111111111112", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4304785885414", "decimals": 9, "uiAmount": 4304.785885414, "uiAmountString": "4304.785885414"}}, {"accountIndex": 30, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "5964703524311276", "decimals": 9, "uiAmount": 5964703.524311276, "uiAmountString": "5964703.524311276"}}], "rewards": [], "status": {"Ok": null}}, "transaction": {"message": {"accountKeys": ["gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB", "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "46pxCL7Upm36T5YbA5od3KfY9QVRwY8aWmuzSnzzmUcA", "5cwXmKE4Hfo1pwNmaqNN3G2sFxaPmh99KzzKqxxpUGtc", "5tfDjs6dMBDJCvy8KzBQc9wHNRQBv7Ld55V8P42qjbxS", "5vYhTkbZ1eHVT2gtWpcqNfJtrH93GozY7cp77mv4FEQ1", "7jPcYwKiZCqL8AejDj3fWX2HSsXMPtk8ynb9gaaT92Uk", "7qsvwKqCxTYqzmGnZ7wiFfF9JAuT9ZSkqbesjKKoBorB", "84HBfGQM6s66jvtHADW3yRZboDnSvgB4vepaiLhpfike", "9fBpwxcudpLyJskhiiKmU8wPszeUuCB8sSjhPi44QuFb", "9KLsBy8WLiRQXiaKvQfP2QpUKmKogkkXAnp3R2js1LnG", "Ej5MvFYhUzUXYK6GUhtHG8Kza3r4PBJkMn5WnkULnQiE", "EKybzWj9NGuMcNUMc5U3c8YZ2bVJm1VXfdczxHCvDsXC", "FgEvXp2vtH3rFfV2U6YmN1T2QeeySzTgig8ZaXaVAofc", "GGe31JNjegWrBFAxN3rJr8N4dCGP7mA7iDY19uRPmSu7", "11111111111111111111111111111111", "7X4pHkWzDWEFwrKiZ4TzuxubQDNFdimjuiJyUk3rYhwb", "ComputeBudget111111111111111111111111111111", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"], "addressTableLookups": [{"accountKey": "3GHqLHQa6e2tJ8boEy7WGUi69ngyGGiGiqgbbYNyGLX7", "readonlyIndexes": [223], "writableIndexes": [229, 225, 231]}, {"accountKey": "3ko8XWJLLPTmsC7pJbrENEVbfrM2x4Ps4Peu8STgphfx", "readonlyIndexes": [152, 10, 3], "writableIndexes": [142, 153, 146]}, {"accountKey": "3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW", "readonlyIndexes": [0, 40, 17, 1, 23, 20, 21], "writableIndexes": [38, 55]}, {"accountKey": "AZ3jABe1GEVW5XKdiYQheEZBMFULiQYEkpGNqh5Vsrs", "readonlyIndexes": [62, 154, 61], "writableIndexes": [157, 146, 148, 149]}], "header": {"numReadonlySignedAccounts": 1, "numReadonlyUnsignedAccounts": 4, "numRequiredSignatures": 2}, "instructions": [{"accounts": [], "data": "E9YCTR", "programIdIndex": 17, "stackHeight": 1}, {"accounts": [], "data": "3GpTfWHWDg3Z", "programIdIndex": 17, "stackHeight": 1}, {"accounts": [37, 1, 6, 6, 26, 2, 43, 36, 41, 40, 35, 18, 26, 44, 29, 16, 30, 27, 6, 25, 43, 39, 28, 44, 1, 41, 40, 33, 42, 44, 11, 10, 14, 18, 34, 40, 37, 19, 25, 21, 3, 20, 7, 12, 5, 31, 34, 40, 37, 23, 3, 22, 26, 24, 8, 4, 13, 32, 38], "data": "6gDU5q1ft98C3rMZmqq6QvefXmdfhjq6PY5wpqsfdCqoioSKqfWHVodb9nDJTAqJdSdJcZjvehvnn", "programIdIndex": 18, "stackHeight": 1}, {"accounts": [0, 9], "data": "3Bxs4FeGqCF4jJBR", "programIdIndex": 15, "stackHeight": 1}], "recentBlockhash": "F17TfDAPYLBt3AHGCuxeyKb6aT31ucSPFvWchZTVPBCQ"}, "signatures": ["3gLH2B4rDTgq8qMjSKh61h9AtbZn36abXHS2UktaTZS1eggAFGA73RNEXPmCPXSw8dbSVu4coKQQ7JCnNpyskQCv", "5bFzC9knoCKJxydoNjKt7m4kPruHE3pm8YoTJnfd6qQ3xL9h6oKwP54WfQUNFDdtewmktPGw3hMbXsioqhzDsLmy"]}, "parsed_tx": {"dex": "unknown", "action": "unknown", "mint": null, "amount": null, "signature": null, "source_wallet": null, "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "unknown", "confidence": 0}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: log.py:139

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
2025-10-20 21:04:34,661 - __main__ - DEBUG - [DEBUG] Before infer_missing_fields: {"detection_method": "websocket_account_change", "timestamp": "2025-10-20 20:04:34.140822+00:00", "requires_full_analysis": true, "signature": "ndhfRpYBMeaUdcF4S1GD8iASnDSBiqQMUUkMBWgYQKJhf5Pz8Xd5mBvrTaJW3bfCJHvtvGLRsHqUHp4sq8Ufi6g", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success"], "transaction": {"message": {"accountKeys": [{"pubkey": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "signer": true, "source": "transaction", "writable": true}, {"pubkey": "5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW", "signer": true, "source": "transaction", "writable": true}, {"pubkey": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "signer": true, "source": "transaction", "writable": false}, {"pubkey": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "FY3t5nGT4xgK1XMPAik2uipSZrwUpxmTdhivTdFTWD4Y", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "3BUzjXnM7a7Ju1kGekv9zJfeXCuYdKJMRDZ7cwxWTw49", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "ComputeBudget111111111111111111111111111111", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "So11111111111111111111111111111111111111112", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "11111111111111111111111111111111", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "9dkYPFpVTA9tBSmkAkdRoMmnoB3WPBG9UYfUPFfhvFJj", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "signer": false, "source": "transaction", "writable": false}], "addressTableLookups": [], "instructions": [{"accounts": [], "data": "HAWR3M", "programId": "ComputeBudget111111111111111111111111111111", "stackHeight": 1}, {"accounts": [], "data": "3atJtxCCtbsV", "programId": "ComputeBudget111111111111111111111111111111", "stackHeight": 1}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "mint": "So11111111111111111111111111111111111111112", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "createIdempotent"}, "program": "spl-associated-token-account", "programId": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "stackHeight": 1}, {"parsed": {"info": {"account": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "create"}, "program": "spl-associated-token-account", "programId": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "stackHeight": 1}, {"parsed": {"info": {"destination": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "lamports": 940000000, "source": "5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW"}, "type": "transfer"}, "program": "system", "programId": "11111111111111111111111111111111", "stackHeight": 1}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk"}, "type": "syncNative"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 1}, {"accounts": ["FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "9dkYPFpVTA9tBSmkAkdRoMmnoB3WPBG9UYfUPFfhvFJj", "FY3t5nGT4xgK1XMPAik2uipSZrwUpxmTdhivTdFTWD4Y", "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "3BUzjXnM7a7Ju1kGekv9zJfeXCuYdKJMRDZ7cwxWTw49", "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "So11111111111111111111111111111111111111112", "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF", "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"], "data": "TGq5We4Uqkt8c4w8B5kdTTEdKKtT3on6hN", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "stackHeight": 1}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "destination": "5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "closeAccount"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 1}], "recentBlockhash": "D5rK86h2ejRCSBeZvkKwwJaJpHVASFrUBHaGxj2GGJ8f"}, "signatures": ["ndhfRpYBMeaUdcF4S1GD8iASnDSBiqQMUUkMBWgYQKJhf5Pz8Xd5mBvrTaJW3bfCJHvtvGLRsHqUHp4sq8Ufi6g", "47WyeWpBW2sVWniBeQVmsvbpSxnmrkUSFMxNyknkp76u5noJpDabjDFoFUYTnGJgjU4xmhFQvcQs2cdUWHcREwaD", "61sRNdvPjPNezo39daywXVrLZi8aaKQx12F2nYY5pthFmyoGqBD1BkNhHskgrFB9XeYSNaeZEMGgsEnwYjMwQRn4"]}, "meta": {"computeUnitsConsumed": 122222, "costUnits": 126559, "err": null, "fee": 77000, "innerInstructions": [{"index": 2, "instructions": [{"parsed": {"info": {"extensionTypes": ["immutableOwner"], "mint": "So11111111111111111111111111111111111111112"}, "type": "getAccountDataSize"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"lamports": 2039280, "newAccount": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "space": 165}, "type": "createAccount"}, "program": "system", "programId": "11111111111111111111111111111111", "stackHeight": 2}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk"}, "type": "initializeImmutableOwner"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "mint": "So11111111111111111111111111111111111111112", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "initializeAccount3"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}]}, {"index": 3, "instructions": [{"parsed": {"info": {"extensionTypes": ["immutableOwner"], "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c"}, "type": "getAccountDataSize"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"lamports": 2039280, "newAccount": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "space": 165}, "type": "createAccount"}, "program": "system", "programId": "11111111111111111111111111111111", "stackHeight": 2}, {"parsed": {"info": {"account": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k"}, "type": "initializeImmutableOwner"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"account": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "initializeAccount3"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}]}, {"index": 6, "instructions": [{"parsed": {"info": {"authority": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "destination": "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "mint": "So11111111111111111111111111111111111111112", "source": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "tokenAmount": {"amount": "940000000", "decimals": 9, "uiAmount": 0.94, "uiAmountString": "0.94"}}, "type": "transferChecked"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"authority": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "destination": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "source": "3BUzjXnM7a7Ju1kGekv9zJfeXCuYdKJMRDZ7cwxWTw49", "tokenAmount": {"amount": "4223021417000", "decimals": 6, "uiAmount": 4223021.417, "uiAmountString": "4223021.417"}}, "type": "transferChecked"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"authority": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "destination": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "mint": "So11111111111111111111111111111111111111112", "source": "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "tokenAmount": {"amount": "10093", "decimals": 9, "uiAmount": 1.0093e-05, "uiAmountString": "0.000010093"}}, "type": "transferChecked"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"accounts": ["8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF"], "data": "2ioXo9nkAt26bphRv6PYrqXu1WqZas5QXLCJAHm29gH8gmiPimCsd4v3qQEiPFtPXTfAY2Zhx1kqTtaLZWjdw1zaFftu7xg5whxTgbfcUgwzXhQz5m8pbYcjx4xaDRNhYeYPxzvi5ffg1ZSySas1DJNHj7TjNLXCmiEnacu92rmywVYKto6oEUNxYEgX6yAeqj7yPqHAVTGHH2Ag5tbPCeTZp9ZWssUzeiV4r5h2P", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "stackHeight": 2}, {"accounts": ["8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF"], "data": "44FY2SKwMbUFWgV1yoKm6d53JBJqdzq9UBVTHSyQn8CJHezoTCqcrXDubvZntJdC73qAmoAyhGikAnLG3uHJoNxTbwyyRJLu9iaSB1y7AVs8JvE1JQD8MiKd2X78pbBdZuNCp35u9uZmtGzDQkRbcocraihGTdiQhvoQnuSk3eBE3Cg8izhB5ZhUNGussdAm9pmQg34WvnMoGn6awXQemdEPzWQnb3tYwZV4KJk3BVCV4n3ik5XDUVCj6H1xrsW4p5izvS37CP9", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "stackHeight": 2}]}], "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success"], "postBalances": [2410783040, 17000071918, 0, 0, 2039280, 3841920, 2039280, 96274935166, 1, 789146954, 1176160029876, 1, 5299607121, 1461600, 1151512, 1602282239974, 8184960, 1000055, 1187659450], "postTokenBalances": [{"accountIndex": 4, "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4223021417000", "decimals": 6, "uiAmount": 4223021.417, "uiAmountString": "4223021.417"}}, {"accountIndex": 6, "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "519274406509051", "decimals": 6, "uiAmount": 519274406.509051, "uiAmountString": "519274406.509051"}}, {"accountIndex": 7, "mint": "So11111111111111111111111111111111111111112", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "96272895886", "decimals": 9, "uiAmount": 96.272895886, "uiAmountString": "96.272895886"}}], "preBalances": [2414938600, 17938022545, 0, 0, 0, 3841920, 2039280, 95334945259, 1, 789146954, 1176160029876, 1, 5299607121, 1461600, 1151512, 1602282239974, 8184960, 1000055, 1187659450], "preTokenBalances": [{"accountIndex": 6, "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "523497427926051", "decimals": 6, "uiAmount": 523497427.926051, "uiAmountString": "523497427.926051"}}, {"accountIndex": 7, "mint": "So11111111111111111111111111111111111111112", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "95332905979", "decimals": 9, "uiAmount": 95.332905979, "uiAmountString": "95.332905979"}}], "rewards": [], "status": {"Ok": null}}, "parsed_tx": {"dex": "meteora", "action": "swap", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "amount": null, "signature": "ndhfRpYBMeaUdcF4S1GD8iASnDSBiqQMUUkMBWgYQKJhf5Pz8Xd5mBvrTaJW3bfCJHvtvGLRsHqUHp4sq8Ufi6g", "wallet_address": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "possible_trade", "confidence": 0.3}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}, "dex": "meteora", "action": "buy", "token_mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "wallet_address": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "confidence": "MEDIUM", "dex_type": "unknown", "trade_type": "buy", "analysis_method": "full_analyzer_with_dex_detection", "programs_used": [], "router_program_id": null, "account_metas": [], "instruction_data": null}
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### SCAFFOLD_EXECUTOR: mev_meteora_executor.py:95

**Description:** Scaffold/nonfunctional executor not gated behind config flag

**Code:**
```python
class RPCConfig:
```

**Suggested Fix:**
```python
Add config gating: if not os.getenv('ENABLE_SCAFFOLD_EXECUTORS'): return BuildResult(ok=False, reason='Executor disabled')
```

---

#### MISSING_BUILD_ALTS: mev_meteora_executor.py:1533

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
alt_lookups = msg.get("addressTableLookups", [])
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### SCAFFOLD_EXECUTOR: mev_raydium_executor.py:60

**Description:** Scaffold/nonfunctional executor not gated behind config flag

**Code:**
```python
class MEVRaydiumExecutor:
```

**Suggested Fix:**
```python
Add config gating: if not os.getenv('ENABLE_SCAFFOLD_EXECUTORS'): return BuildResult(ok=False, reason='Executor disabled')
```

---

#### MISSING_BUILD_ALTS: mev_router_account_resolver.py:42

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
lookups = getattr(msg, 'address_table_lookups', [])
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: simulate_clone.py:170

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
if hasattr(msg, 'address_table_lookups') and msg.address_table_lookups:
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: temp_clean.py:141

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
# Handle addressTableLookups for versioned transactions
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: test_alt_integration.py:43

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
"addressTableLookups": [
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: test_alt_reconstruction.py:106

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
# Check for addressTableLookups detection
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### ATA_EXISTS_USAGE: test_ata_utilities.py:96

**Description:** Call to ensure_ata function passes 'exists' boolean instead of querying RPC

**Code:**
```python
instructions_exists = ensure_ata_for(owner, mint, payer, exists=True)
```

**Suggested Fix:**
```python
Remove 'exists' parameter and let the function query RPC directly
```

---

#### ATA_EXISTS_USAGE: test_ata_utilities.py:103

**Description:** Call to ensure_ata function passes 'exists' boolean instead of querying RPC

**Code:**
```python
instructions_not_exists = ensure_ata_for(owner, mint, payer, exists=False)
```

**Suggested Fix:**
```python
Remove 'exists' parameter and let the function query RPC directly
```

---

#### MISSING_BUILD_ALTS: test_build_and_sign_integration_v2.py:33

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
"addressTableLookups": []
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: transaction_analyzer.py:279

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
address_table_lookups = message.get('addressTableLookups', [])
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: transaction_analyzer_severely_corrupted.py:141

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
# Handle addressTableLookups for versioned transactions
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: utils/alts.py:34

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
# from the message.addressTableLookups field
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

#### MISSING_BUILD_ALTS: wallet_tx_parser.py:575

**Description:** File references addressTableLookups but doesn't call build_alts_from_tables

**Code:**
```python
alt_info["lookup_tables"] = tx_data.get("addressTableLookups", [])
```

**Suggested Fix:**
```python
Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)
```

---

### 🔵 LOW Priority

#### SOLANA_PY_IMPORT: 1_Jupiter.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: 1_Jupiter.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: 1_Jupiter.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: 1_Pump.fun.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: 1_Pump.fun.py:24

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: 1_Pump.fun.py:25

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: CRITICAL_ATA_FIX.py:100

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: EMERGENCY_ATA_PATCH.py:183

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: advanced_trading_components.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: advanced_trading_components.py:24

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: advanced_trading_components.py:29

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_clmm_transaction.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_cpmm_pool.py:19

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_cpmm_pool.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_detected_transactions.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_detected_transactions.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_log.py:2

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_missed_tx.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_missed_tx.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_programs.py:6

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_recent_trades.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_recent_trades.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_sell_transaction.py:5

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_specific_missing_transactions.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_specific_missing_transactions.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_specific_successful_tx.py:6

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_specific_successful_tx.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Commitment
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_success.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: analyze_transaction.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: base_solana_executor.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: base_solana_executor.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: base_solana_executor.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: check_ata_exists.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: check_dex_pools.py:5

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: check_token_program.py:6

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clean_main.py:33

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clean_main_v2.py:33

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_execute_trade.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_execute_trade.py:38

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_execute_trade.py:39

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_hybrid_copy_executor.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_hybrid_copy_executor.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_hybrid_copy_executor.py:31

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Finalized, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_hybrid_copy_executor.py:254

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_hybrid_copy_executor.py:255

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_jupiter_hybrid.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_jupiter_hybrid.py:27

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_jupiter_hybrid.py:28

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Finalized, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_jupiter_trader.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_jupiter_trader.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: clmm_jupiter_trader.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: comprehensive_fix.py:325

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: comprehensive_tx_analysis.py:29

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: comprehensive_tx_analysis.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: coordinator_balance_utils.py:4

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: copy_trading_verification.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: copy_trading_verification.py:190

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: coverage_audit_tool.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: cpmm_copy_bot_integration_guide.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: cpmm_pool_analyzer.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: cpmm_pool_analyzer.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation_final.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation_final.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Commitment
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation_final.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation_official.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation_official.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Commitment
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: create_observation_official.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_account_structure.py:19

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_account_structure.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_account_structure.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_fake_signature.py:35

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_jupiter_account_keys.py:43

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_missed_transaction.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_new_missed_transaction.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_program_address_error.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_program_address_error.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_specific_transaction.py:47

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_specific_transaction.py:48

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_token_issue.py:5

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_transaction.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_transaction.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_transaction_analysis.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: debug_transaction_analysis.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: deep_debug_transaction.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: deep_debug_transaction.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: demonstrate_execution_flow.py:31

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: dex_token_validator.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: diagnostic.py:70

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_dex_transaction_builder.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_dex_transaction_builder.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_pumpfun.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_pumpfun.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_pumpfun.py:18

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_raydium_executor.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: direct_raydium_executor.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: dry_run_raydium_link_test.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: enhanced_cpmm_discovery.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: enhanced_cpmm_discovery.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: enhanced_transaction_builder.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: enhanced_transaction_builder.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: enhanced_transaction_builder.py:450

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: get_complete_logs.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: get_complete_logs.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: get_exact_16_accounts.py:6

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: get_exact_16_accounts.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Commitment
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: hybrid_clmm_trader.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: hybrid_clmm_trader.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: hybrid_clmm_trader.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: hybrid_trader.py:45

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: hybrid_trader.py:52

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: hybrid_trader.py:53

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Finalized, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: init_observation_via_clmm.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: init_observation_via_clmm.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Commitment
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: init_observation_via_clmm.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: initialize_observation.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: initialize_observation.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: initialize_observation.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: integrated_trade_monitor.py:192

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jito_tips.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jito_tips.py:11

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_copy_bot.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_copy_bot.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_copy_bot.py:24

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_trade_executor.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_trade_executor.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_trade_executor.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_trader.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_trader.py:31

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_trader.py:32

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: jupiter_utils.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_complex.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_complex.py:26

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_complex.py:31

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts  # Added for direct RPC execution options
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:33

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:40

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:1150

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:3044

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:3045

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:3575

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TokenAccountOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_backup_corrupted.py:4201

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:33

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:40

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:1150

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:3044

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:3045

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:3575

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TokenAccountOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_corrupted_backup.py:4201

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_modular.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_modular.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:33

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:40

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:1152

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:3046

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:3047

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:3577

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TokenAccountOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: main_monolithic_backup.py:4203

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: manual_trade_all_methods.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: manual_trade_all_methods.py:31

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: manual_trade_all_methods.py:32

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: mev_router_account_resolver.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: mev_router_account_resolver.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.publickey import PublicKey
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: official_executor_wrappers.py:6

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient as SolanaRpcClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: official_executor_wrappers.py:1062

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: official_executor_wrappers.py:1238

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: official_executor_wrappers.py:1293

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: official_wallet_perspective_analyzer.py:19

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: official_wallet_perspective_analyzer.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_copy_executor.py:59

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_copy_executor.py:66

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_copy_executor.py:67

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Finalized, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_copy_executor.py:527

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_copy_executor.py:528

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_manual_trader.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_manual_trader.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: orca_manual_trader.py:31

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_copy_executor.py:37

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_copy_executor.py:44

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_copy_executor.py:45

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Finalized, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_copy_executor.py:463

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_copy_executor.py:464

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_manual_trader.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_manual_trader.py:29

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: phoenix_manual_trader.py:30

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pool_discovery_service.py:11

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pool_discovery_service.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: position_diagnostic.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: position_diagnostic.py:19

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Finalized
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: position_diagnostic.py:41

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TokenAccountOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_CC_copy_executor_OLD_BACKUP.py:1853

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_CC_copy_executor_OLD_BACKUP.py:1854

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:45

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:46

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:47

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:182

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:183

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:1026

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:1027

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:1199

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_copy_executor_old.py:1200

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_executor.py:32

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_executor.py:33

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_executor.py:34

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_manual_trader.py:270

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_manual_trader.py:271

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.transaction import Transaction
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_token_validator.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_trade_executor.py:19

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_trade_executor.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: pumpfun_trade_executor.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed, Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_clmm_trade_executor.py:26

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_clmm_trade_executor.py:27

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_clmm_trade_executor.py:28

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_copy_executor.py:79

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_copy_executor.py:80

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_copy_executor.py:185

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_copy_executor.py:186

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_official_structure.py:19

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_official_structure.py:20

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_v4_amm_trader.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_v4_amm_trader.py:23

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: raydium_v4_amm_trader.py:24

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: run_execution_smoke_test.py:27

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: send_mev_router_example.py:4

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: send_mev_router_example.py:5

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: send_mev_router_example.py:6

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.publickey import PublicKey
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: send_mev_router_example.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.keypair import Keypair
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: simple_bot.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: simple_dex_test.py:22

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: simple_main.py:17

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: simple_test.py:25

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: simplified_official_websocket.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: speed_optimizer.py:152

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: temp_clean.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_aggressive_fallback.py:11

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_aggressive_logs_fallback.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_ata_creation.py:5

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_balance_fix.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_balance_fix.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_balance_fix.py:11

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TokenAccountOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_dex_detection.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_execution_readiness.py:39

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_finalized_commitment.py:21

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_fixed_balance.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_fixed_balance.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_fixed_balance.py:11

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TokenAccountOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_full_routing.py:10

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_imports.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_meteora_executor.py:34

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_official_method.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_real_execution_final.py:58

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_router_extraction_fix.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_token_compatibility.py:8

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_token_extraction.py:7

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_transaction_simulation.py:39

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: test_ultra_aggressive_account_keys.py:47

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: token_validator.py:11

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: transaction_analyzer.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: transaction_analyzer_severely_corrupted.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: transaction_history_analyzer.py:13

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: transaction_history_analyzer.py:14

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Confirmed, Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: transaction_history_analyzer.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import MemcmpOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: tx_builder.py:4

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient  # At top with other imports
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: tx_builder.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.types import TxOpts
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: tx_builder.py:16

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.commitment import Processed
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: tx_translator.py:12

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.api import Client
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: validate_modules.py:155

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: verify_fix.py:15

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

#### SOLANA_PY_IMPORT: verify_official_program_id.py:9

**Description:** Using solana-py import (should use solders)

**Code:**
```python
from solana.rpc.async_api import AsyncClient
```

**Suggested Fix:**
```python
Replace with solders equivalent: from solders.* import ...
```

---

## Detailed Findings by File

### 1_Jupiter.py

**Issues:** 4

- **Line 78** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `sig = await self.client.send_transaction(tx, opts=TxOpts(skip_preflight=True, max_retries=1))`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### 1_Pump.fun.py

**Issues:** 10

- **Line 157** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 307** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 471** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 844** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `signature = await self.client.send_transaction(transaction, opts=opts)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 940** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `buy_sig = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 983** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `sell_sig = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 1229** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 24** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 25** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### CRITICAL_ATA_FIX.py

**Issues:** 2

- **Line 186** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 100** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### EMERGENCY_ATA_PATCH.py

**Issues:** 2

- **Line 194** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 183** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### advanced_trading_components.py

**Issues:** 3

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 24** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 29** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_clmm_transaction.py

**Issues:** 1

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_cpmm_pool.py

**Issues:** 2

- **Line 19** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_detected_transactions.py

**Issues:** 2

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_log.py

**Issues:** 1

- **Line 2** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_missed_tx.py

**Issues:** 2

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_programs.py

**Issues:** 1

- **Line 6** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_recent_trades.py

**Issues:** 2

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_sell_transaction.py

**Issues:** 1

- **Line 5** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_specific_missing_transactions.py

**Issues:** 2

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_specific_successful_tx.py

**Issues:** 2

- **Line 6** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Commitment`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_success.py

**Issues:** 1

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### analyze_transaction.py

**Issues:** 1

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### base_solana_executor.py

**Issues:** 4

- **Line 174** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### check_ata_exists.py

**Issues:** 1

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### check_dex_pools.py

**Issues:** 1

- **Line 5** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

### check_token_program.py

**Issues:** 1

- **Line 6** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### clean_main.py

**Issues:** 1

- **Line 33** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### clean_main_v2.py

**Issues:** 1

- **Line 33** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### clmm_copy_executor.py

**Issues:** 1

- **Line 137** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### clmm_execute_trade.py

**Issues:** 8

- **Line 319** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 471** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 651** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 697** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 761** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 38** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 39** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### clmm_hybrid_copy_executor.py

**Issues:** 6

- **Line 207** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 31** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Finalized, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 254** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 255** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### clmm_jupiter_hybrid.py

**Issues:** 6

- **Line 173** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 270** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 356** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 27** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 28** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Finalized, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### clmm_jupiter_trader.py

**Issues:** 4

- **Line 144** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### comprehensive_fix.py

**Issues:** 1

- **Line 325** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### comprehensive_tx_analysis.py

**Issues:** 2

- **Line 29** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

### coordinator_balance_utils.py

**Issues:** 1

- **Line 4** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### copy_trading_verification.py

**Issues:** 2

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 190** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

### coverage_audit_tool.py

**Issues:** 1

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### cpmm_copy_bot_integration_guide.py

**Issues:** 1

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### cpmm_copy_executor.py

**Issues:** 2

- **Line 288** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 327** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### cpmm_pool_analyzer.py

**Issues:** 2

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### create_observation.py

**Issues:** 2

- **Line 91** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### create_observation_final.py

**Issues:** 4

- **Line 136** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Commitment`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### create_observation_official.py

**Issues:** 4

- **Line 130** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Commitment`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_account_structure.py

**Issues:** 3

- **Line 19** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_fake_signature.py

**Issues:** 1

- **Line 35** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_jupiter_account_keys.py

**Issues:** 1

- **Line 43** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_missed_transaction.py

**Issues:** 1

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_new_missed_transaction.py

**Issues:** 1

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_program_address_error.py

**Issues:** 2

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_specific_transaction.py

**Issues:** 2

- **Line 47** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 48** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_token_issue.py

**Issues:** 1

- **Line 5** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_transaction.py

**Issues:** 2

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### debug_transaction_analysis.py

**Issues:** 2

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### deep_debug_transaction.py

**Issues:** 2

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### demo_alt_fetch.py

**Issues:** 1

- **Line 200** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `print("    new_message = Message.new_with_blockhash(")`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

### demonstrate_execution_flow.py

**Issues:** 1

- **Line 31** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### dex_token_validator.py

**Issues:** 1

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### diagnostic.py

**Issues:** 1

- **Line 70** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### direct_dex_transaction_builder.py

**Issues:** 2

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### direct_pumpfun.py

**Issues:** 5

- **Line 80** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.rpc_client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 148** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.rpc_client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 18** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### direct_raydium_executor.py

**Issues:** 2

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### dry_run_raydium_link_test.py

**Issues:** 1

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### enhanced_cpmm_discovery.py

**Issues:** 2

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### enhanced_transaction_builder.py

**Issues:** 3

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 450** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### execution_coordinator.py

**Issues:** 1

- **Line 631** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `kwargs['addressTableLookups'] = required_accounts.get('lookup_tables', [])`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### full_output.py

**Issues:** 1

- **Line 3** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-06 18:55:55,427 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': '41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 55, 427124, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 393367, 'costUnits': 403892, 'err': None, 'fee': 310654, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [2, 16, 1], 'data': '3awy1w6vdVeX', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [39, 23, 24, 25, 15, 16, 41, 44], 'data': 'J9A6eM58XaLWXKsmqBa2NbWp', 'programIdIndex': 43, 'stackHeight': 2}, {'accounts': [16, 25, 39], 'data': '3JpGTWoUyaDu', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [24, 15, 23], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42], 'data': '59p8WydnSZtV29EZJ5EPHbUYgwcyEPuwe7SXrhmNB83k1QhfcFC71rtXHa', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [15, 17, 39], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [19, 3, 21], 'data': '3Z6sYHBgK6Ky', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35], 'data': '59p8WydnSZtSYqyRFuqQPv9H538j1vw22B54xWsoUsCA53MawYHzdhGF2x', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [16, 14, 39], 'data': '3JvGaqeJM4Hd', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [12, 3, 13], 'data': '3YMxHtDwKwzF', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28], 'data': 'wZRp7wZ3czsp8TiBYg9eUvG8CbxCoDYm42UzZBycSgh5Z3PVpMQRnwuz', 'programIdIndex': 46, 'stackHeight': 2}, {'accounts': [16, 27, 39], 'data': '3QJJ2xEUe3q1', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [32, 3, 26], 'data': '3FDG456PfyrP', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [37], 'data': '4KbP49BdVApjtHuXZdNzDMRzUrFad32msbNDnEYAYPQjzkC9HQWsZg1bqYcV42HqWmzj35W86LMLAaDsXdQGXr8ABcyjSB2Yy87SyzmryVoMFg2uka2ui24a42mTckbKcFwx3Y2Eb9shgn5HevkmfzSeLBWjMYtYsaPqPgxPAghFzqsn88EC9wz8HdnuK9FYZjzy5wnjFY3g8pXfG8cLUUWa3V2U2YjRfFBCC35KxSZrwp7j7rSBAvVyRuoyaMG4xEpfdd2jLcJMMwcipiYk9YxfgYAgNgogzLaApf2JjMX59N2GBCHAQFQDYCQYMEvao1PwTBGz9hAZC562sXP9oJLAkrmUQz4Y3JNyL1A28SLxuPuK8tnf5yKx4mwe8rWLKv1S1DfEUbQrq4xP9vmgFEJJZ5i4QX5kyyJbcikf8Q7Bz4jKf4X8HDWNc6YigxvzPMBhT8X82kqsNojDZ', 'programIdIndex': 8, 'stackHeight': 2}, {'accounts': [2, 16, 1], 'data': '3avKVPuic5LT', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [3, 5, 39], 'data': '3uktGuL5uriK', 'programIdIndex': 41, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'GrzzQpVYkCoDnXGVpANW9iDGJk9EbcJJRj9FgY3GeVNm', 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'jitodontfront11111111111JustUseJupiterU1tra', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'FovDWEsftJv4X1EfapqVwG2VDcEDG2vsa7vaje3qAo56', 'SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe', 'Sysvar1nstructions1111111111111111111111111', 'A1BBtTYJd4i3xU8D6Tc2FzU6ZN4oXZWXKZnCxwbHXr8x', 'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK'], 'writable': ['4ZEwCEENfgAqzbyKLBDLZxSeixbKpZknirkWLFVcaLBw', '7yUHJWhvRnspqZKezhVHxJmsLLcfNyDn4dhYTCNNPTxe', '8z95LBWmSRKkQv1XPczvN6s2Fc3Rk5X6oi1ueW3nndBV', 'Bc1Ki733Cv9Fu2qGwar3n6EjQBofTpwrVAg2uSo5uLUV', 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'Efe7p9ZEbd99dCoGU3mbYbRRxU9tJuSmHX6jYDtbKC4x', '2p29nqD7DN1PczBMmgrFdtYKTfv6rJ7H3yMut4eu7nYT', '5SPztfEn1VAaWDBAXjQKwVrGbr6e8g3F6JJnUc9eCuSe', '2rJJP6RAyfo5HaoR9T6SDjWU885RkQBH3PyRpnoFrkDU', '3aSDFqAyFJPniaZpJf7Vn9PxZqT6dcuxzg9HXwWkbpVP', 'E83CnZbE1cz2ww5rqYuvWmAdMwWh3ZkJJcrbo49TaaGU', 'E9TL1PrwPxpdvMGjSXJQidJSmdBG4LYJJWoHDF5gSVv2', 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'H1j2gqzW61MrdjJsu6s5gamLq9wcKkinw1a7GWyjdd6k', 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'CTaDZW2LhvHPRnA9JWcZF8R5y2mpkV2RcHAXyEoKLbzp', 'JHVJLsPsbzNW8JP8cPYmrwfzD2M9aHXdFHSjeeCDERu', '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', '4LCiADXLEBW2JepG5iue3iTB3ozXb3YLGqheQNEWTSAY', '666Sz6bUgQwS2vgGDkPSwfqSsxtmBUh7Zvya6p2nkTJF', '7B5dskPoP5r2vXPDJgzvwCNTtuYwXVgV6KEeaWn8o2Ph', 'C86icgvRMBRHZWnTFjHnLh4o3BVroZYx5CHueZzAqByo', 'DnrPPNMp3ZqcCcrF8LEPLiXBiwMDPwELKFAy8ToHwUsD', 'FSGuR2PvoUqZvuQNxQVgyUeP4Mcsa89JxeqvAFWqSJdo', 'GwXt2aQ8gT39XT7HhcSdiDyTdxNgLY3pyJQm56mcbzWE']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121763506924, 9204256, 2039280, 2039280, 20152947666, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8769954653, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599752863345, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2430379783', 'decimals': 6, 'uiAmount': 2430.379783, 'uiAmountString': '2430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1290180175863', 'decimals': 6, 'uiAmount': 1290180.175863, 'uiAmountString': '1290180.175863'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3329485185848465', 'decimals': 6, 'uiAmount': 3329485185.848465, 'uiAmountString': '3329485185.848465'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '519465211363', 'decimals': 6, 'uiAmount': 519465.211363, 'uiAmountString': '519465.211363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4059641614', 'decimals': 6, 'uiAmount': 4059.641614, 'uiAmountString': '4059.641614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8767915373', 'decimals': 9, 'uiAmount': 8.767915373, 'uiAmountString': '8.767915373'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4072118737060', 'decimals': 6, 'uiAmount': 4072118.73706, 'uiAmountString': '4072118.73706'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599731804056', 'decimals': 9, 'uiAmount': 7599.731804056, 'uiAmountString': '7599.731804056'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713647633243', 'decimals': 6, 'uiAmount': 1713647.633243, 'uiAmountString': '1713647.633243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '751162111', 'decimals': 6, 'uiAmount': 751.162111, 'uiAmountString': '751.162111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3625092093786', 'decimals': 6, 'uiAmount': 3625092.093786, 'uiAmountString': '3625092.093786'}}], 'preBalances': [121763893741, 9204256, 2039280, 2039280, 20152871503, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8559129552, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599963688446, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3430379783', 'decimals': 6, 'uiAmount': 3430.379783, 'uiAmountString': '3430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18533267719', 'decimals': 6, 'uiAmount': 18533.267719, 'uiAmountString': '18533.267719'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3330667810953218', 'decimals': 6, 'uiAmount': 3330667810.953218, 'uiAmountString': '3330667810.953218'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '518536327363', 'decimals': 6, 'uiAmount': 518536.327363, 'uiAmountString': '518536.327363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4058441614', 'decimals': 6, 'uiAmount': 4058.441614, 'uiAmountString': '4058.441614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8557090272', 'decimals': 9, 'uiAmount': 8.557090272, 'uiAmountString': '8.557090272'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4135662209305', 'decimals': 6, 'uiAmount': 4135662.209305, 'uiAmountString': '4135662.209305'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599942629157', 'decimals': 9, 'uiAmount': 7599.942629157, 'uiAmountString': '7599.942629157'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713597693243', 'decimals': 6, 'uiAmount': 1713597.693243, 'uiAmountString': '1713597.693243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '731186111', 'decimals': 6, 'uiAmount': 731.186111, 'uiAmountString': '731.186111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3650570424932', 'decimals': 6, 'uiAmount': 3650570.424932, 'uiAmountString': '3650570.424932'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', '5ht281axHQXoQ2PWD6vrxxnHEa8TmsLuzs7XTDnmTdCt', '7QRKuCbdjxRjno55LE1GGFVKqxeFUWeNtUaLQ4a9Gz9X', '9fBpwxcudpLyJskhiiKmU8wPszeUuCB8sSjhPi44QuFb', 'B95oUgde4SfoekubbV1hbFanLBRV7UL26zXqcZZhHdrx', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'], 'addressTableLookups': [{'accountKey': '2z84tgaUYNWMwotQjmSpRygdH96m5M5VpUqZQH1L24UF', 'readonlyIndexes': [70, 68, 12], 'writableIndexes': [67, 64, 65, 66, 58, 63]}, {'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 40, 11, 1, 20], 'writableIndexes': [32, 49]}, {'accountKey': 'DWSgR97yTc3WENhkddFBkoBsute6mKpaJ5Kkfix8KWXb', 'readonlyIndexes': [225], 'writableIndexes': [219, 229, 188, 227, 222, 223]}, {'accountKey': 'EE8XintbVcFLm3CR3rNLfW5WcBKDtsniQwLKsWz3enYi', 'readonlyIndexes': [168, 173], 'writableIndexes': [169, 170, 171]}, {'accountKey': 'JBMZHmsCUZEfXpNPm4N1XQ2seJbDo3CFSfmQjK4mShDh', 'readonlyIndexes': [34, 40], 'writableIndexes': [37, 29, 38, 35, 33, 41, 39, 31]}], 'header': {'numReadonlySignedAccounts': 1, 'numReadonlyUnsignedAccounts': 3, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'KGAnEb', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [], 'data': '3QZwSzAJHXSo', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [39, 1, 2, 16, 3, 5, 38, 34, 41, 41, 37, 8, 16, 43, 39, 23, 24, 25, 15, 16, 41, 44, 36, 41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42, 36, 41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35, 46, 39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28, 8, 40], 'data': '2uadBoC4kUfkSytM1gJGnMJKGK8Uu9K455iqA8iRquZaLonKccX4BABoNf9v5VVL7q1N21BztbkGU7cw', 'programIdIndex': 8, 'stackHeight': 1}, {'accounts': [0, 4], 'data': '3Bxs4No5VVsho7hh', 'programIdIndex': 6, 'stackHeight': 1}], 'recentBlockhash': 'EZUJNZw94LezE4g9mf2Ku8FJ1dkMqyRQ4ieEUxBWnhMj'}, 'signatures': ['41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', '3pXHMYvd5xKeyxUMUNNPEWK2Meu6Kwnb3HYkFdNW4dbpY1dN72nL1e75H1oX8BrWfoNgRXz6gbpcW1RLttDavnGt']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### full_output_I.py

**Issues:** 1

- **Line 93** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-07 17:14:40,238 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': '2WdPgL6BQMDtYkmZnVKPCUpdxV8NnQcvvJ7KCwcdDcmYDX749LmA5z26ThVNchy6RPvusn9pXh7Gz5n8Jiahgv89', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 193054 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: 2xZ84zrhN1YTP9LmrgIw+WTDZUb11jWFmyBjlf69q5XGIxwAAAAAABSUKRYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 138328 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 132262 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 54935 of 181109 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 114425 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 108608 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/uW6GCBOJyhzLYupFgDTqgrWfMy3sZsErvz0sUXMNh+8m0O00xeDnPr+KH1bD1V2cVrqHHbJe7iXRF+vmW3fGN5Ucd2/T74cJwEbZ9oaJ31u0Nm/LcdKppcJDcAAeFSusgjDGSoLLvptLbVdn3hF3e9HVYSX54eAxcJmWVvl+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9GcYyX54eAxcDwTSPl+0ZYzm8cCt0LXR76s7xbZxcUGQajN1aDW/WV4PgxQuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 39154 of 123133 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]', 'Program log: ray_log: A2+2ET0AAAAAAAAAAAAAAAACAAAAAAAAAGhChbwAAAAAqHhQaykAAACsdy882KIAADyV+CHuAAAA', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66410 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 59205 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 26733 of 80600 compute units', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 52094 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 50191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 43488 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 159138 of 197850 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 PJX4Ie4AAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 7, 16, 14, 40, 237716, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 159588, 'costUnits': 167043, 'err': None, 'fee': 475325, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [3, 2, 1], 'data': '3mMeLYZHv31q', 'programIdIndex': 31, 'stackHeight': 2}, {'accounts': [28, 21, 32, 11, 19, 20, 2, 18, 33, 29, 31, 31, 25], 'data': 'KdeEDKHxrmWGNkvCP6n5cEh5', 'programIdIndex': 34, 'stackHeight': 2}, {'accounts': [2, 19, 28], 'data': '3mMeLYZHv31q', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [20, 18, 21], 'data': '3dm7JxVbCvTH', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [14, 16, 15, 12, 13, 18, 17, 28, 31, 25], 'data': '4acasGboxW9ycmr5GDkkPdR', 'programIdIndex': 26, 'stackHeight': 2}, {'accounts': [18, 15, 28], 'data': '3dm7JxVbCvTH', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [13, 17, 13], 'data': '3Y9JSGqCfGmD', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [31, 24, 35, 24, 23, 22, 24, 24, 24, 24, 24, 24, 24, 24, 17, 5, 28], 'data': '69JXzprawbsnmbefSGhpw9Z', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [17, 23, 28], 'data': '3Y9JSGqCfGmD', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [22, 5, 35], 'data': '3PbKaghc6T5y', 'programIdIndex': 31, 'stackHeight': 3}, {'accounts': [27], 'data': '2C3FxF4wtCk1WPKYcjNvfKxBQp63XmmB7XbdK96PrfUPSGPAGM3Y2JsW2y2rYDAKkUArJC9qEWv2VrfDPx3yPdtwdE2BYpVEhnNZpE1iXZQxVMbXXmB39j2FDqHNnSou7GnJVKpNFqwtyyKhuZitXdw1fsYGtcFNUTxAWP4sboxrfRbiAKLXvXBUVuPncUUse3HzK1dh6kf8FX94UMsJSYQgFh3WXLHRsMgRWGA5SgKDccryGpdG82w5vfQ62Sv5BRYh5zi9ZJLH7BhwgiHeuzz6FWJog2pvB9U3DAc3sK1poBp1UbbWjtEGaaSMzwwdSuSZJDpCs9cKwHuU11BbWPstezw1mLczCw3D', 'programIdIndex': 10, 'stackHeight': 2}, {'accounts': [3, 2, 1], 'data': '3W1GURjhLEgX', 'programIdIndex': 31, 'stackHeight': 2}, {'accounts': [5, 6, 28], 'data': '3PbKaghc6T5y', 'programIdIndex': 31, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['Sysvar1nstructions1111111111111111111111111', 'ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'CyCUgmaCYUZxbux3J2svDzxSryVFMtZNPrnMKS41nc4G', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8'], 'writable': ['8943FQrCirbp2kNk8cVKS5P7vjNzhas3L9fDoqpnv8mw', 'CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU', 'f2FsCiguf172T9achZzJcTjJuM9BLf5nmf18WKaaWUZ', 'fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1', 'GC2yqyD6ZYnAXc8DNy4d7uiYnQ9TBhZBA4WMPbsMKUxK', 'EUvpCGh4qiMtq9wKgp28f9Bjv5Xz2WJqrM83XmYAqkEq', 'FbruxBVHi463Agw2B3Vy27cBkGnEN5g1f4NcHe3REXfe', '5bHD9xdEzJdkVuhs54mGPC9BZgUshqgMg4tqmTwhWggc', 'ARWaajRJyF6PKQryJ4HLzLBfTWM2qmVQUQVtBjk6PgPc', 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', '39fBZjAdwAxwTvrTW5RLDM7zTTRupYE7UJJvuuCJrnfg', 'Dqsmrr3x4JkffT7J9rpi8D3CupVyLCyHvLEbkHGpPBwB', 'DrgGbUa6SMEDeY2YbwgfoKKNx5rLRG5kNkNgunxzp4G3']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 193054 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: 2xZ84zrhN1YTP9LmrgIw+WTDZUb11jWFmyBjlf69q5XGIxwAAAAAABSUKRYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 138328 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 132262 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 54935 of 181109 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 114425 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 108608 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/uW6GCBOJyhzLYupFgDTqgrWfMy3sZsErvz0sUXMNh+8m0O00xeDnPr+KH1bD1V2cVrqHHbJe7iXRF+vmW3fGN5Ucd2/T74cJwEbZ9oaJ31u0Nm/LcdKppcJDcAAeFSusgjDGSoLLvptLbVdn3hF3e9HVYSX54eAxcJmWVvl+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9GcYyX54eAxcDwTSPl+0ZYzm8cCt0LXR76s7xbZxcUGQajN1aDW/WV4PgxQuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 39154 of 123133 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]', 'Program log: ray_log: A2+2ET0AAAAAAAAAAAAAAAACAAAAAAAAAGhChbwAAAAAqHhQaykAAACsdy882KIAADyV+CHuAAAA', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66410 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 59205 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 26733 of 80600 compute units', 'Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 52094 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 50191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 43488 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 159138 of 197850 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 PJX4Ie4AAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [64909369989, 9395859, 2039680, 2039280, 19719074822, 2039280, 2039280, 1, 8995008256, 1, 2729681025, 7298979842, 8352000, 2020397051241, 52784640, 2079311, 8352000, 2140321390, 2039381, 2039280, 2039280, 12917764, 2039280, 178920705287, 14124800, 0, 1141440, 3596047, 156269933, 418700053208, 1000004, 5065007155, 2060160, 141900721504, 1141441, 32327908436, 2500659979], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '239208668', 'decimals': 6, 'uiAmount': 239.208668, 'uiAmountString': '239.208668'}}, {'accountIndex': 3, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 5, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '19114626117', 'decimals': 6, 'uiAmount': 19114.626117, 'uiAmountString': '19114.626117'}}, {'accountIndex': 6, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1022772155708', 'decimals': 6, 'uiAmount': 1022772.155708, 'uiAmountString': '1022772.155708'}}, {'accountIndex': 13, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2020394905405', 'decimals': 9, 'uiAmount': 2020.394905405, 'uiAmountString': '2020.394905405'}}, {'accountIndex': 15, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '228619882592', 'decimals': 6, 'uiAmount': 228619.882592, 'uiAmountString': '228619.882592'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2138278905', 'decimals': 9, 'uiAmount': 2.138278905, 'uiAmountString': '2.138278905'}}, {'accountIndex': 18, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '433400576', 'decimals': 6, 'uiAmount': 433.400576, 'uiAmountString': '433.400576'}}, {'accountIndex': 19, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '408027626684', 'decimals': 6, 'uiAmount': 408027.626684, 'uiAmountString': '408027.626684'}}, {'accountIndex': 20, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '403455858852', 'decimals': 6, 'uiAmount': 403455.858852, 'uiAmountString': '403455.858852'}}, {'accountIndex': 22, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '178026834223728', 'decimals': 6, 'uiAmount': 178026834.223728, 'uiAmountString': '178026834.223728'}}, {'accountIndex': 23, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '178918666007', 'decimals': 9, 'uiAmount': 178.918666007, 'uiAmountString': '178.918666007'}}], 'preBalances': [64909962645, 9395859, 2039680, 2039280, 19718957491, 2039280, 2039280, 1, 8995008256, 1, 2729681025, 7298979842, 8352000, 2021421622232, 52784640, 2079311, 8352000, 2140321390, 2039381, 2039280, 2039280, 12917764, 2039280, 177896134296, 14124800, 0, 1141440, 3596047, 156269933, 418700053208, 1000004, 5065007155, 2060160, 141900721504, 1141441, 32327908436, 2500659979], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '238820218', 'decimals': 6, 'uiAmount': 238.820218, 'uiAmountString': '238.820218'}}, {'accountIndex': 3, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '228500000', 'decimals': 6, 'uiAmount': 228.5, 'uiAmountString': '228.5'}}, {'accountIndex': 5, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '19114626117', 'decimals': 6, 'uiAmount': 19114.626117, 'uiAmountString': '19114.626117'}}, {'accountIndex': 6, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 13, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2021419476396', 'decimals': 9, 'uiAmount': 2021.419476396, 'uiAmountString': '2021.419476396'}}, {'accountIndex': 15, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '228391601359', 'decimals': 6, 'uiAmount': 228391.601359, 'uiAmountString': '228391.601359'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2138278905', 'decimals': 9, 'uiAmount': 2.138278905, 'uiAmountString': '2.138278905'}}, {'accountIndex': 18, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'DSN3j1ykL3obAVNv7ZX49VsFCPe4LqzxHnmtLiPwY6xg', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '433400576', 'decimals': 6, 'uiAmount': 433.400576, 'uiAmountString': '433.400576'}}, {'accountIndex': 19, 'mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '407799515134', 'decimals': 6, 'uiAmount': 407799.515134, 'uiAmountString': '407799.515134'}}, {'accountIndex': 20, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'FkEB6uvyzuoaGpgs4yRtFtxC4WJxhejNFbUkj5R6wR32', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '403684140085', 'decimals': 6, 'uiAmount': 403684.140085, 'uiAmountString': '403684.140085'}}, {'accountIndex': 22, 'mint': '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '179049606379436', 'decimals': 6, 'uiAmount': 179049606.379436, 'uiAmountString': '179049606.379436'}}, {'accountIndex': 23, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '177894095016', 'decimals': 9, 'uiAmount': 177.894095016, 'uiAmountString': '177.894095016'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', 'HWNQj3wxLuFraXGyDPu89E7euKr9ponHhQ8DXJBjYszh', '4jVFS4iFYaYL4G94Be9eKejW3aNVmsK73DgyDxeF1zeb', '8TGRD1ZSLGGpWnB6A218DZAZdDWJJQz3cT8qnfePRSiK', 'AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw', 'Dp8YMGEG9k9mFy56QtbEBQoKG2fFjrcYmchFag14LK2c', 'G46QTpwZMjBCemM739xa61h7tfKym88omEE4bcetMHRM', '11111111111111111111111111111111', '4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ'], 'addressTableLookups': [{'accountKey': '2iUJxrahG52bPemKUWw8CSceESan6K75M6XwfuRmtjcS', 'readonlyIndexes': [42, 44], 'writableIndexes': [43, 40, 45, 38, 41]}, {'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 12, 40, 1, 20], 'writableIndexes': [33, 50]}, {'accountKey': 'Cebe9n1UmhceqQMWpZpkLHTGUZSks33XTzM62n984s8Z', 'readonlyIndexes': [146, 149, 147], 'writableIndexes': [153, 145, 150]}, {'accountKey': 'HQEo1L5u8hDiqFYmHgUwz3WLa1h1t5mAwgB54FZEB38g', 'readonlyIndexes': [9, 4], 'writableIndexes': [159, 160, 156]}], 'header': {'numReadonlySignedAccounts': 1, 'numReadonlyUnsignedAccounts': 5, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'EEzc6T', 'programIdIndex': 9, 'stackHeight': 1}, {'accounts': [], 'data': '3NxujFR17Tbu', 'programIdIndex': 9, 'stackHeight': 1}, {'accounts': [28, 1, 3, 2, 5, 6, 33, 8, 31, 31, 27, 10, 2, 34, 28, 21, 32, 11, 19, 20, 2, 18, 33, 29, 31, 31, 25, 26, 14, 16, 15, 12, 13, 18, 17, 28, 31, 25, 36, 31, 24, 35, 24, 23, 22, 24, 24, 24, 24, 24, 24, 24, 24, 17, 5, 28, 30], 'data': 'CQ7Z1iuQV9mhfcuNXTLayQHmFDFwAH9L8WzN2mrgXgbuW7dmCJcV1uEioaubey277fLsuU', 'programIdIndex': 10, 'stackHeight': 1}, {'accounts': [0, 4], 'data': '3Bxs4EsX5CFe8UZD', 'programIdIndex': 7, 'stackHeight': 1}], 'recentBlockhash': 'B7n7K3ZPUi8toxgCH14jZx5r91jPt9mPWE12atTCS8wV'}, 'signatures': ['2WdPgL6BQMDtYkmZnVKPCUpdxV8NnQcvvJ7KCwcdDcmYDX749LmA5z26ThVNchy6RPvusn9pXh7Gz5n8Jiahgv89', 'dqJgwbh2tHS7WUPEW4UaaFscV7SqYUUJoXEW85k5RBACu2FF786vFes833fsKoiWS1i4SuAfmzme8tRMT2QBaw7']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### full_output_II.py

**Issues:** 1

- **Line 3** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-06 18:55:20,053 - execution_coordinator - ERROR -    Input params: token_mint=7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk, source_wallet=suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK, trade_info={'signature': 'kGo2toyarf9z8UX2ajqcG3vU8JEcjXhfQYLeGceY9GjGmbtThC8gStH6MeBu1YAwuweWT1j6ohdWHeMT1HRqjYT', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 258345 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 261903 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]', 'Program log: Instruction: SellExactIn', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [3]', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 2039 of 216326 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program data: vdt/007mYe4v729nUnxNTIPERAhplCfJfDf9y6UhzLaf2npUDDGGIwB4xftR0QIAY3EOPunPAwDbGfgGAQAAAJyTbxmx+AAA1uHtWQAAAAA2E3sOOPcAALpIN1kAAAAAZoD0CnkBAABsObQAAAAAAN50AAAAAAAAc9MBAAAAAABfFwAAAAAAAAAAAAAAAAAAAQAB', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 210792 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 201525 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 186515 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 177191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 78407 of 247148 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh7lNA0AAAAAAPl7JhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 121358 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 115292 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 52182 of 161347 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp invoke [2]', 'Program log: 🦐', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 83284 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 77384 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: uzk28I9BxQZ484fWSzqZ3uRB544IUuDeeH1C4MV62fQcrneXpYLIS/F1G4rvWKU8C5OQGVO7h+OudgDex33l1UUKp5Q6jO/Vv5UvDS6eN94wSzulVKGgC/xW3GTCeByOgWtRMH78x2t9mKcEx0+H2l804ruYvH+6HFAqZ4NXRe6wKmcoKoYNVkN7vUR2RfKpWktR95FdWO+Y8MZnn1dZ7wHb14bvP17vnvDAZ5lXX++d8MNnmldc75zwwmebV13v9aDQ1LxWUu/dQhrzHVdT73AGN2WWV1DvuLJ6Z5dXUe+aFmDdCVZW737zyGeRV1fvlfDLZ5JXVO+V8Mpnk1dV7w==', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp consumed 34268 of 106189 compute units', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 70153 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4735 of 68079 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 192640 of 255163 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 L4PGAgAAAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 62523 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 19, 753362, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 202745, 'costUnits': 210206, 'err': None, 'fee': 814009, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [0, 2], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 15, 'stackHeight': 2}, {'accounts': [2, 27], 'data': '6QR9nxorLs8pns5qcUs55CVfrLWHMQf92wS29j4F7zpMp', 'programIdIndex': 14, 'stackHeight': 2}]}, {'index': 3, 'instructions': [{'accounts': [1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 15, 8, 9], 'data': 'B3F1THDgKfWQNoqGkJRTMRi3faUjyQLsQoWRt9HLviQF', 'programIdIndex': 29, 'stackHeight': 2}, {'accounts': [31], 'data': 'EwDfpErTWwQhCAycT1hw3kgHYnu5XfSffnwsXbjvzoi62MCw8U9cB97RyMStDmh9HVqRzgbgjG1bcXcbRvTNifx9K118nrFjmhwTxUKbx2Z5UZbUHGJGDbbX9d6VnDAzcySaj2SWmkXaqewAFqq8EvVxczotqjKhjWSyhHT6a1Qonwmbg1oTp7VfYj3mFbGVUcySmbzxRFKRi1tKpzhN', 'programIdIndex': 29, 'stackHeight': 3}, {'accounts': [3, 16, 6, 1], 'data': 'hQd6eFvBGU7RP', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 5, 30], 'data': 'hUr6YwLadcviq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 8, 30], 'data': 'haTUQVQeEbAtu', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 9, 30], 'data': 'hK9e7r43JdfeV', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34], 'data': 'JrgsXFj1RYPjW8Y8GT2wMrgf', 'programIdIndex': 38, 'stackHeight': 2}, {'accounts': [5, 25, 1], 'data': '3XZV5DYw7S8w', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [26, 10, 24], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 21, 22, 23, 2, 10, 36, 14, 34], 'data': 'EYwtd5cZ2x46GzRdaBV4ncpS7NWF7QPXVE', 'programIdIndex': 35, 'stackHeight': 2}, {'accounts': [22, 2, 21], 'data': '3sFhmXiKHtcf', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [10, 23, 1], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [28], 'data': '2C3FxF4wtCk1WPKYcjNvfKxBQp63Ne2UoU49PzYeeFYQPkQSyK8deGyJeNb3TzpxdREMvnBqqD1SJvxUVZ8VUowXtsZTWuGaMTA39aXtwzCT1vie5JSSK7o7CpHrSSqmMx3B9fbxBn2VwKxb6w9Xek6Qf5oSjCnNVvGqzTQ3coLN7E56GBXemtNt52rNX5azya1jAXc9qXaRQNLhXQDqfAPGntqw8jTp6Cfwrmk61trP1mHs7Dq4rbQiqfgfemviKiPUutgukwoJUgA6ejiLo3NUf3TgyLMAiCPWULy8wuLzy3W8iUVUGFauGCeZSScjWrQ15G6nfribhqmh8u7hDwhKkboTxJXP791H', 'programIdIndex': 13, 'stackHeight': 2}, {'accounts': [2, 20, 1], 'data': '3jJkXKqVVD8T', 'programIdIndex': 14, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['So11111111111111111111111111111111111111112', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj', 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', '2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'Sysvar1nstructions1111111111111111111111111', '9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp', 'SysvarC1ock11111111111111111111111111111111', 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', 'By9zHEbZJvYrBws27SqPXggfSAH3fjnJcdxKgdogyXUm'], 'writable': ['qqdJ4z1yu4sTbAitwXZsGNDoGZFgL2HfVKSVwAXWCfq', 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'ECEPWwZJ1U1Vjsj1X5sUbZYETKMSCjYHuoTMVitCn64t', 'FBWtVVvzsRuAAzVX8ua1hden9KmgPrC2rFijuwEn1ngJ', '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'CRF6Tegjtv3k9tuvKKbXroq4UmKXh9ZP92tn17sjjsFY', 'CT8B2qJAqy93GAU5Qor9s5xGGQEoiEwSSNRPAaDFYrgL']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 258345 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 261903 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]', 'Program log: Instruction: SellExactIn', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [3]', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 2039 of 216326 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program data: vdt/007mYe4v729nUnxNTIPERAhplCfJfDf9y6UhzLaf2npUDDGGIwB4xftR0QIAY3EOPunPAwDbGfgGAQAAAJyTbxmx+AAA1uHtWQAAAAA2E3sOOPcAALpIN1kAAAAAZoD0CnkBAABsObQAAAAAAN50AAAAAAAAc9MBAAAAAABfFwAAAAAAAAAAAAAAAAAAAQAB', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 210792 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 201525 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 186515 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 177191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 78407 of 247148 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh7lNA0AAAAAAPl7JhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 121358 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 115292 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 52182 of 161347 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp invoke [2]', 'Program log: 🦐', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 83284 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 77384 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: uzk28I9BxQZ484fWSzqZ3uRB544IUuDeeH1C4MV62fQcrneXpYLIS/F1G4rvWKU8C5OQGVO7h+OudgDex33l1UUKp5Q6jO/Vv5UvDS6eN94wSzulVKGgC/xW3GTCeByOgWtRMH78x2t9mKcEx0+H2l804ruYvH+6HFAqZ4NXRe6wKmcoKoYNVkN7vUR2RfKpWktR95FdWO+Y8MZnn1dZ7wHb14bvP17vnvDAZ5lXX++d8MNnmldc75zwwmebV13v9aDQ1LxWUu/dQhrzHVdT73AGN2WWV1DvuLJ6Z5dXUe+aFmDdCVZW737zyGeRV1fvlfDLZ5JXVO+V8Mpnk1dV7w==', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp consumed 34268 of 106189 compute units', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 70153 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4735 of 68079 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 192640 of 255163 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 L4PGAgAAAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 62523 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121815835862, 54559143, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338271045, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18393311302, 13018008, 1274267537134, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'postTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '728179866823882', 'decimals': 6, 'uiAmount': 728179866.823882, 'uiAmountString': '728179866.823882'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1610430361', 'decimals': 6, 'uiAmount': 1610.430361, 'uiAmountString': '1610.430361'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11898116474', 'decimals': 6, 'uiAmount': 11898.116474, 'uiAmountString': '11898.116474'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22726813', 'decimals': 6, 'uiAmount': 22.726813, 'uiAmountString': '22.726813'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18391272020', 'decimals': 9, 'uiAmount': 18.39127202, 'uiAmountString': '18.39127202'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274265491845', 'decimals': 9, 'uiAmount': 1274.265491845, 'uiAmountString': '1274.265491845'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586624463991', 'decimals': 6, 'uiAmount': 586624.463991, 'uiAmountString': '586624.463991'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176684933430', 'decimals': 6, 'uiAmount': 176684.93343, 'uiAmountString': '176684.93343'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32339272204', 'decimals': 6, 'uiAmount': 32339.272204, 'uiAmountString': '32339.272204'}}], 'preBalances': [121818891153, 5955720, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338069043, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18390004884, 13018008, 1274317407695, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'preTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1619386466406', 'decimals': 6, 'uiAmount': 1619386.466406, 'uiAmountString': '1619386.466406'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '726560480357476', 'decimals': 6, 'uiAmount': 726560480.357476, 'uiAmountString': '726560480.357476'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1622367191', 'decimals': 6, 'uiAmount': 1622.367191, 'uiAmountString': '1622.367191'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11897996807', 'decimals': 6, 'uiAmount': 11897.996807, 'uiAmountString': '11897.996807'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22720830', 'decimals': 6, 'uiAmount': 22.72083, 'uiAmountString': '22.72083'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18387965602', 'decimals': 9, 'uiAmount': 18.387965602, 'uiAmountString': '18.387965602'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274315362406', 'decimals': 9, 'uiAmount': 1274.315362406, 'uiAmountString': '1274.315362406'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586612650575', 'decimals': 6, 'uiAmount': 586612.650575, 'uiAmountString': '586612.650575'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176673122250', 'decimals': 6, 'uiAmount': 176673.12225, 'uiAmountString': '176673.12225'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32351085620', 'decimals': 6, 'uiAmount': 32351.08562, 'uiAmountString': '32351.08562'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'instructions': [{'accounts': [], 'data': 'FbXwDZ', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [], 'data': '3w56bdfNkcwH', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [2, 1, 27, 14, 15, 0], 'data': '2tDqDdUmhLW1t', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [1, 3, 2, 16, 27, 14, 14, 13, 28, 13, 20, 29, 1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 0, 15, 8, 9, 13, 38, 1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34, 35, 1, 21, 22, 23, 2, 10, 36, 14, 34, 33], 'data': '6ZARjK8Vuzcec2q5gZSKfeFAiRPD2NBawoAqfMk75i1qiqXn4W8jQobUuaD4Nx2eV9Lvh3jEtBpajvJjJ3cG1o6qq4Zx', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [2, 1, 1], 'data': 'A', 'programIdIndex': 14, 'stackHeight': 1}, {'accounts': [0, 11], 'data': '3Bxs43t5YK1vh4TZ', 'programIdIndex': 15, 'stackHeight': 1}], 'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', '8JrWPvg2ZiB2xaBKhRZiwXQzwhwbcii8ySYboGWnCnAB', '3rRjPpCB14e3eXLgE1BueVaHxUekBFfHMCDmTuD6ApbH', '4E7vL7FnDsdrUpqpJqb8C5q8JEoQAoaEKRS5pD6mjBWz', 'BehsFyHbsdea9ixfXx5dPL5DgukyD9ripZXCa6AXi3VW', '5Yt4ff98wjmy2xgRBc4u7MkuLDBzxrHNL3fKdTujvBPo', 'EAxfzwbMfxYJdLeHKpg3SWqajk88aycxSCqfixtdC1Xx', '67pirGqYiCT6j56DdQmAivWZSuZEtYbzSqMTWUNcHZAL', 'EzFT73bzdGAY52VuNKL2rfq8GPkSxBTK6Wd8zSGjJD1N', '5L1uEnJ96z4kgQ4zY9Rg1VWC1RmbtVrfutyMSiJQpVFg', 'E8iYKQbhTywHbncCagNBbZ58JY6cX1SiYk5ZDPJeWFFq', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', '11111111111111111111111111111111', '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'EPiZbnrThjyLnoQ6QQzkxeFqyL5uyg9RzNHHAudUPxBz', 'FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1', 'QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}, 'transaction_full': {'blockTime': 1759773320, 'meta': {'computeUnitsConsumed': 202745, 'costUnits': 210206, 'err': None, 'fee': 814009, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [0, 2], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 15, 'stackHeight': 2}, {'accounts': [2, 27], 'data': '6QR9nxorLs8pns5qcUs55CVfrLWHMQf92wS29j4F7zpMp', 'programIdIndex': 14, 'stackHeight': 2}]}, {'index': 3, 'instructions': [{'accounts': [1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 15, 8, 9], 'data': 'B3F1THDgKfWQNoqGkJRTMRi3faUjyQLsQoWRt9HLviQF', 'programIdIndex': 29, 'stackHeight': 2}, {'accounts': [31], 'data': 'EwDfpErTWwQhCAycT1hw3kgHYnu5XfSffnwsXbjvzoi62MCw8U9cB97RyMStDmh9HVqRzgbgjG1bcXcbRvTNifx9K118nrFjmhwTxUKbx2Z5UZbUHGJGDbbX9d6VnDAzcySaj2SWmkXaqewAFqq8EvVxczotqjKhjWSyhHT6a1Qonwmbg1oTp7VfYj3mFbGVUcySmbzxRFKRi1tKpzhN', 'programIdIndex': 29, 'stackHeight': 3}, {'accounts': [3, 16, 6, 1], 'data': 'hQd6eFvBGU7RP', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 5, 30], 'data': 'hUr6YwLadcviq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 8, 30], 'data': 'haTUQVQeEbAtu', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [7, 37, 9, 30], 'data': 'hK9e7r43JdfeV', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34], 'data': 'JrgsXFj1RYPjW8Y8GT2wMrgf', 'programIdIndex': 38, 'stackHeight': 2}, {'accounts': [5, 25, 1], 'data': '3XZV5DYw7S8w', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [26, 10, 24], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [1, 21, 22, 23, 2, 10, 36, 14, 34], 'data': 'EYwtd5cZ2x46GzRdaBV4ncpS7NWF7QPXVE', 'programIdIndex': 35, 'stackHeight': 2}, {'accounts': [22, 2, 21], 'data': '3sFhmXiKHtcf', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [10, 23, 1], 'data': '3LC97bVa1LKq', 'programIdIndex': 14, 'stackHeight': 3}, {'accounts': [28], 'data': '2C3FxF4wtCk1WPKYcjNvfKxBQp63Ne2UoU49PzYeeFYQPkQSyK8deGyJeNb3TzpxdREMvnBqqD1SJvxUVZ8VUowXtsZTWuGaMTA39aXtwzCT1vie5JSSK7o7CpHrSSqmMx3B9fbxBn2VwKxb6w9Xek6Qf5oSjCnNVvGqzTQ3coLN7E56GBXemtNt52rNX5azya1jAXc9qXaRQNLhXQDqfAPGntqw8jTp6Cfwrmk61trP1mHs7Dq4rbQiqfgfemviKiPUutgukwoJUgA6ejiLo3NUf3TgyLMAiCPWULy8wuLzy3W8iUVUGFauGCeZSScjWrQ15G6nfribhqmh8u7hDwhKkboTxJXP791H', 'programIdIndex': 13, 'stackHeight': 2}, {'accounts': [2, 20, 1], 'data': '3jJkXKqVVD8T', 'programIdIndex': 14, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['So11111111111111111111111111111111111111112', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj', 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', '2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'Sysvar1nstructions1111111111111111111111111', '9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp', 'SysvarC1ock11111111111111111111111111111111', 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', 'By9zHEbZJvYrBws27SqPXggfSAH3fjnJcdxKgdogyXUm'], 'writable': ['qqdJ4z1yu4sTbAitwXZsGNDoGZFgL2HfVKSVwAXWCfq', 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'ECEPWwZJ1U1Vjsj1X5sUbZYETKMSCjYHuoTMVitCn64t', 'FBWtVVvzsRuAAzVX8ua1hden9KmgPrC2rFijuwEn1ngJ', '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'CRF6Tegjtv3k9tuvKKbXroq4UmKXh9ZP92tn17sjjsFY', 'CT8B2qJAqy93GAU5Qor9s5xGGQEoiEwSSNRPAaDFYrgL']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 258345 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 261903 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]', 'Program log: Instruction: SellExactIn', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [3]', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 2039 of 216326 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program data: vdt/007mYe4v729nUnxNTIPERAhplCfJfDf9y6UhzLaf2npUDDGGIwB4xftR0QIAY3EOPunPAwDbGfgGAQAAAJyTbxmx+AAA1uHtWQAAAAA2E3sOOPcAALpIN1kAAAAAZoD0CnkBAABsObQAAAAAAN50AAAAAAAAc9MBAAAAAABfFwAAAAAAAAAAAAAAAAAAAQAB', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 210792 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 201525 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 186515 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 177191 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj consumed 78407 of 247148 compute units', 'Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]', 'Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh7lNA0AAAAAAPl7JhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 121358 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 115292 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 52182 of 161347 compute units', 'Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp invoke [2]', 'Program log: 🦐', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 83284 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 77384 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: uzk28I9BxQZ484fWSzqZ3uRB544IUuDeeH1C4MV62fQcrneXpYLIS/F1G4rvWKU8C5OQGVO7h+OudgDex33l1UUKp5Q6jO/Vv5UvDS6eN94wSzulVKGgC/xW3GTCeByOgWtRMH78x2t9mKcEx0+H2l804ruYvH+6HFAqZ4NXRe6wKmcoKoYNVkN7vUR2RfKpWktR95FdWO+Y8MZnn1dZ7wHb14bvP17vnvDAZ5lXX++d8MNnmldc75zwwmebV13v9aDQ1LxWUu/dQhrzHVdT73AGN2WWV1DvuLJ6Z5dXUe+aFmDdCVZW737zyGeRV1fvlfDLZ5JXVO+V8Mpnk1dV7w==', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp consumed 34268 of 106189 compute units', 'Program 9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 70153 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4735 of 68079 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 192640 of 255163 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 L4PGAgAAAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 62523 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121815835862, 54559143, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338271045, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18393311302, 13018008, 1274267537134, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'postTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '728179866823882', 'decimals': 6, 'uiAmount': 728179866.823882, 'uiAmountString': '728179866.823882'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1610430361', 'decimals': 6, 'uiAmount': 1610.430361, 'uiAmountString': '1610.430361'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11898116474', 'decimals': 6, 'uiAmount': 11898.116474, 'uiAmountString': '11898.116474'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22726813', 'decimals': 6, 'uiAmount': 22.726813, 'uiAmountString': '22.726813'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18391272020', 'decimals': 9, 'uiAmount': 18.39127202, 'uiAmountString': '18.39127202'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274265491845', 'decimals': 9, 'uiAmount': 1274.265491845, 'uiAmountString': '1274.265491845'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586624463991', 'decimals': 6, 'uiAmount': 586624.463991, 'uiAmountString': '586624.463991'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176684933430', 'decimals': 6, 'uiAmount': 176684.93343, 'uiAmountString': '176684.93343'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32339272204', 'decimals': 6, 'uiAmount': 32339.272204, 'uiAmountString': '32339.272204'}}], 'preBalances': [121818891153, 5955720, 0, 2039280, 3876720, 2039280, 2039280, 2039280, 2039280, 2039280, 2039280, 20338069043, 1, 2729681025, 5065007155, 1, 1461600, 3473040, 8928332, 7298979842, 18390004884, 13018008, 1274317407695, 2039280, 12917760, 2039280, 2039280, 1158072388620, 3596047, 37580031, 0, 0, 418677002208, 1000004, 0, 1141545, 1169280, 98390920, 1141441, 2060160], 'preTokenBalances': [{'accountIndex': 3, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1619386466406', 'decimals': 6, 'uiAmount': 1619386.466406, 'uiAmountString': '1619386.466406'}}, {'accountIndex': 5, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '726560480357476', 'decimals': 6, 'uiAmount': 726560480.357476, 'uiAmountString': '726560480.357476'}}, {'accountIndex': 7, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': 'WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1622367191', 'decimals': 6, 'uiAmount': 1622.367191, 'uiAmountString': '1622.367191'}}, {'accountIndex': 8, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '56XVRVAsgWv6ADaxzoNnbL38LMoWKM5WiSAhrAWUbd2p', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '11897996807', 'decimals': 6, 'uiAmount': 11897.996807, 'uiAmountString': '11897.996807'}}, {'accountIndex': 9, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '9sHpTfmVpCfP2zexRNK6j38NBchMv1RWpdXPK5NEcZan', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '22720830', 'decimals': 6, 'uiAmount': 22.72083, 'uiAmountString': '22.72083'}}, {'accountIndex': 10, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 6, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 20, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18387965602', 'decimals': 9, 'uiAmount': 18.387965602, 'uiAmountString': '18.387965602'}}, {'accountIndex': 22, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1274315362406', 'decimals': 9, 'uiAmount': 1274.315362406, 'uiAmountString': '1274.315362406'}}, {'accountIndex': 23, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '586612650575', 'decimals': 6, 'uiAmount': 586612.650575, 'uiAmountString': '586612.650575'}}, {'accountIndex': 25, 'mint': 'USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '176673122250', 'decimals': 6, 'uiAmount': 176673.12225, 'uiAmountString': '176673.12225'}}, {'accountIndex': 26, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '32351085620', 'decimals': 6, 'uiAmount': 32351.08562, 'uiAmountString': '32351.08562'}}], 'rewards': [], 'status': {'Ok': None}}, 'slot': 371620859, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '4HT82cKYaHYxbbk6PhsjiXETqchXzusLEWrJEUZJhfvr', '8JrWPvg2ZiB2xaBKhRZiwXQzwhwbcii8ySYboGWnCnAB', '3rRjPpCB14e3eXLgE1BueVaHxUekBFfHMCDmTuD6ApbH', '4E7vL7FnDsdrUpqpJqb8C5q8JEoQAoaEKRS5pD6mjBWz', 'BehsFyHbsdea9ixfXx5dPL5DgukyD9ripZXCa6AXi3VW', '5Yt4ff98wjmy2xgRBc4u7MkuLDBzxrHNL3fKdTujvBPo', 'EAxfzwbMfxYJdLeHKpg3SWqajk88aycxSCqfixtdC1Xx', '67pirGqYiCT6j56DdQmAivWZSuZEtYbzSqMTWUNcHZAL', 'EzFT73bzdGAY52VuNKL2rfq8GPkSxBTK6Wd8zSGjJD1N', '5L1uEnJ96z4kgQ4zY9Rg1VWC1RmbtVrfutyMSiJQpVFg', 'E8iYKQbhTywHbncCagNBbZ58JY6cX1SiYk5ZDPJeWFFq', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', '11111111111111111111111111111111', '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'EPiZbnrThjyLnoQ6QQzkxeFqyL5uyg9RzNHHAudUPxBz', 'FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1', 'QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ'], 'addressTableLookups': [{'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [23, 0, 91, 92, 93, 40, 1], 'writableIndexes': [34]}, {'accountKey': '6JjsmWMgQtjUrBmA1obh4NZpc2CPqLcQ9cRPd2C5WBoM', 'readonlyIndexes': [126, 124, 128], 'writableIndexes': [129, 127, 125]}, {'accountKey': 'DMQiFwkdPjts3db8RiYpeiSu4R4CyBjUVhX2v7y8HUWF', 'readonlyIndexes': [58, 55, 52], 'writableIndexes': [51, 53, 59]}], 'header': {'numReadonlySignedAccounts': 0, 'numReadonlyUnsignedAccounts': 8, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'FbXwDZ', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [], 'data': '3w56bdfNkcwH', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [2, 1, 27, 14, 15, 0], 'data': '2tDqDdUmhLW1t', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [1, 3, 2, 16, 27, 14, 14, 13, 28, 13, 20, 29, 1, 30, 17, 18, 4, 3, 5, 6, 7, 16, 37, 14, 14, 31, 29, 0, 15, 8, 9, 13, 38, 1, 24, 39, 19, 25, 26, 5, 10, 37, 32, 14, 14, 34, 35, 1, 21, 22, 23, 2, 10, 36, 14, 34, 33], 'data': '6ZARjK8Vuzcec2q5gZSKfeFAiRPD2NBawoAqfMk75i1qiqXn4W8jQobUuaD4Nx2eV9Lvh3jEtBpajvJjJ3cG1o6qq4Zx', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [2, 1, 1], 'data': 'A', 'programIdIndex': 14, 'stackHeight': 1}, {'accounts': [0, 11], 'data': '3Bxs43t5YK1vh4TZ', 'programIdIndex': 15, 'stackHeight': 1}], 'recentBlockhash': 'KoYoGnVuPgzZCSdWKBT2ajwkqKvTj2GtnG5bnMw1QN9'}, 'signatures': ['kGo2toyarf9z8UX2ajqcG3vU8JEcjXhfQYLeGceY9GjGmbtThC8gStH6MeBu1YAwuweWT1j6ohdWHeMT1HRqjYT', 'JZeajkzGMhpPdKBmsfaXW5qYZraekpAUeyXaApK6rPWeubWTEFxHM5qxciGNuD2BzfgHMmXDPvZNuNXNPqgXFTH']}, 'version': 0}, 'extracted_info': {'output_mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'token_mint': '7cioAEbG59s54pDXrJ6r9PGzA8QGpVtoN3fdUY5Fbonk', 'source': 'sophisticated_extraction', 'confidence': 'high'}, 'router_program_id': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'dex_type': 'jupiter', 'action': 'sell'}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### full_output_III.py

**Issues:** 1

- **Line 3** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-06 18:55:33,700 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': 'Df8EmUzNvbLT7FZvZHdrZr7Vq1kwpSB67hW43XrX3xZTYrXrFzXMPvPnvRsv1tGQF5JMqRvtWrb1piVnSwPPwYM', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]', 'Program log: CreateIdempotent', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: GetAccountDataSize', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 338794 compute units', 'Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program log: Initialize the associated token account', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeImmutableOwner', 'Program log: Please upgrade to SPL Token 2022 for immutable owner support', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 332207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 328325 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20442 of 344275 compute units', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 320275 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 323833 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 297844 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 292027 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU31rwC+8NeoW5ahnmHWb9iCYrT3cfO79wpk92QvqJ9W3ELwcfs2SZeoT6jUitWveLrWf7NXKuei1OfEzE3UX7jr9gTJTy+DnPr8V3nWq612cVgUiVfuqM9nRF+vmW3fGN5X5SW7T74cJwEbZ9oaJ31u0y5A0jtKppcKHj//h6NRTfWEZLYzLvptL8pZEty93e9FsZiX54eAxcFlQR/l+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FZnNoG4eAxcCYWSPl+0ZYzKcYCt0LXR76U6xbZxcUGQaDMC6XW/WV4N+Rfuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 46763 of 309830 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 227225 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 219520 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJaJ8GZhEw5RuMaegm7Kp2J14F+MzacEwMQH5MU0KK306AAmfg0LX6DKyx4AAAAAAAAAL8SNqLvhQ88eAAAAAAAAAPB3MlQ+AAAA5P3OEAAAAAAAAAAAAAAAAAAAAAAAAAAA0+HwBgAAAADYggkBAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 48542 of 259809 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 198974 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 193140 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19683 of 208058 compute units', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [2]', 'Program log: Instruction: Buy', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ invoke [3]', 'Program log: Instruction: GetFees', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ consumed 4655 of 128795 compute units', 'Program return: pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ AgAAAAAAAABdAAAAAAAAAB4AAAAAAAAA', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 120025 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 111078 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 102056 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 93031 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Z/RSHyz1d3eWAuRoAAAAANQ2JJlUBQAA8PO6GAAAAAAAAAAAAAAAAPDzuhgAAAAAa6E3VavpAQA5TveqCAAAAOLQaxgAAAAAAgAAAAAAAAAYQAEAAAAAAF0AAAAAAAAAUyQ6AAAAAAD6EG0YAAAAALP2uRgAAAAAE2qrvCNj2IGSTJgIQW4lMDytD7YR7arIohmaVZ+qT9In23x60LKtrZbdNGyuGyj0ADl01fYU0EHbq2rZ6ng8yZeo75gq2QDn0AMZwNBnejFqXNlNYIlQ1kDmU4MBS5bgbG+mNnUhLe1gc/XMF7vvYC7/Zono+DGtS5riV7jnU1lgjMwd/OlhtDt3nBkVBabi079F1aTbRhitdsgtYXVFNV0OMm1Matf/fY9TP8MJCFS9H+8ykQhAD19V155Lh4BRiyUYBwQiLWWBvRgv+FbkGcAeqnLxzVwgEEPSplv+/VoeAAAAAAAAAGbBEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [3]', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 2027 of 79902 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 102460 of 175611 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 71322 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 69501 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 253054 of 317093 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 1DYkmVQFAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 64039 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 33, 700370, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 283601, 'costUnits': 293836, 'err': None, 'fee': 1610000, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [50], 'data': '84eT', 'programIdIndex': 16, 'stackHeight': 2}, {'accounts': [0, 6], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 11, 'stackHeight': 2}, {'accounts': [6], 'data': 'P', 'programIdIndex': 16, 'stackHeight': 2}, {'accounts': [6, 50], 'data': '6PpHgoYBYjXp1psXZyvNVUGrzNw4ndQDEbsKAfPRkZDJG', 'programIdIndex': 16, 'stackHeight': 2}]}, {'index': 3, 'instructions': [{'accounts': [0, 4], 'data': '11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL', 'programIdIndex': 11, 'stackHeight': 2}, {'accounts': [4, 39], 'data': '6PpHgoYBYjXp1psXZyvNVUGrzNw4ndQDEbsKAfPRkZDJG', 'programIdIndex': 16, 'stackHeight': 2}]}, {'index': 4, 'instructions': [{'accounts': [21, 18, 19, 20, 22, 2, 5, 1, 16, 40], 'data': '4gTFnZ4t8u23XWnxLZnM8kP', 'programIdIndex': 42, 'stackHeight': 2}, {'accounts': [2, 19, 1], 'data': '3mfrCyRWtp1V', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [22, 5, 22], 'data': '3ugP2GsRwXnf', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [16, 1, 32, 4, 33, 5, 34, 10, 9, 7, 51], 'data': '59p8WydnSZtXFLDenLKcwdBR6qjZAp36uw1FMSkCNDfjLmRWHMNV8q6TpB', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [5, 34, 1], 'data': '3ugP2GsRwXnf', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [33, 4, 32], 'data': '3sm4p3kSk6KH', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [1, 23, 4, 2, 25, 24, 14, 40, 16], 'data': '2d6dWj1mbWkTsAvaXudkTbtJM5r', 'programIdIndex': 45, 'stackHeight': 2}, {'accounts': [2, 24, 1], 'data': '3DWFNscvX9cK', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [25, 4, 23], 'data': '3FdLP6sMt8Uo', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [27, 1, 44, 50, 39, 6, 4, 31, 26, 43, 29, 16, 16, 11, 12, 46, 47, 28, 49, 30, 8, 48, 38], 'data': 'AJTQ2h9DXrC5M2wm3yq8UFHCVvePMuJ8f', 'programIdIndex': 47, 'stackHeight': 2}, {'accounts': [48, 47], 'data': '2BfZXS1GQrCLYxNyN28stskDGyVX2YQ3nqcFzKDzWJsLqu', 'programIdIndex': 38, 'stackHeight': 3}, {'accounts': [31, 50, 6, 27], 'data': 'iociATzmWB4x5', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [4, 39, 26, 1], 'data': 'jHZY3pXyxwy6g', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [4, 39, 29, 1], 'data': 'hAL2BgMEGim9J', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [4, 39, 28, 1], 'data': 'hQopfA1UXFBKW', 'programIdIndex': 16, 'stackHeight': 3}, {'accounts': [46], 'data': 'CTu2YvT3DVurkJGfs6YDcKYxjZ6CZLKYgEgTy4MAgTsvecJPQzwXw7bUBWRgMEUVRnQok1qKxMazsqzd3Ds4XoiirZEkL28Xc5CCY2g4SWsFtpPKeM2bvihFa7ASgZVXo6jZKNsfasnCXHUCbhr9AfpNaDa63Q8K3RyjpWfCtdhb2EDqmmQ42S1Yz2q4HqkzktZzSUizgz46SdmDUUnDAHG96VqQDZg8xBqSv5j8RFfM9tS9xVqhbXbXMoBuK2XS1YoZ6Eu5So9qWAYjCf5bFCDMPnS9FNbLi7hgY27L2y9FhbkUjNFfAxfXuJai53JxDRwfZjDCtgwm48VzJjQ4pavBCwZ3RY6Aeg6uFTnPczKUFjvPFZNuSDpDtptTkzLNAzVNP2jYyV7tQtR82AoWcih45favJT95LubRdWi1K5WfMRNefUvWwMezVUqwt5XU3vFKydj8t4kw7WtZ3QaLxLkdAuz2NS83zo8FpigiN5P8kPpn1xkFLLnmAcw9ByQ7a7JZjjNswsmHzo9jP4uDrbNe1MfGYkXCRzj9', 'programIdIndex': 47, 'stackHeight': 3}, {'accounts': [35], 'data': '4KbP49BdVApjtHuXZdNzDMRzUrFad32msbNDnEYAYPQjzkC9HQWsZg1bqYcV42HqWmzj35WAJByTR9p2U8k9R5rpJKUkh33noRHpWHZ8mhGVdXbozcmg4EboPYACZrKoU9UmgybDRMSXT1zTmUHrKa5kbPtygTDa784hdqtA9Qjr92s85QrNwZzUAHwfKvjTuXcH79M23AVC7AodKhbH3F2eU8ku6KWxFaqiFPaMJTkkuzF3VaKtv3vbBaBk77GRkgAd1qm3WFWk3YsZDMtWrXnM5dHonKbTShGDiYaPAN2s761jbzfX8BjgCgZ1PEZ47xGXU4q1n6GsFW5wEsCMmuub5bKCeS68BpJv8mzfUpE8nNREkPEGvGghoVjfDTSg5AFqefGTVRiJA11je4fynrwN6yhaUXHiddenQM2b8jkzegEjxDLe8pbw1fWyaDHqAuaqxH4dwjGq9ZcbZ', 'programIdIndex': 15, 'stackHeight': 2}, {'accounts': [2, 17, 1], 'data': '3QAg3utWGhiF', 'programIdIndex': 16, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'jitodontfront11111111111JustUseJupiterU1tra', 'pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ', 'So11111111111111111111111111111111111111112', 'Sysvar1nstructions1111111111111111111111111', 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY', '7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ', 'ADyA8hdefvWN2dbGGWFotbzWxrAvLW83WG6QCVXvJKqw', 'goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j', 'GS4CU59F31iL7aR2Q8zVS8DRrcRnXX1yjQ66TqNVQnaR', 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA', '5PHirr8joyTMp9JMm6nW7hNDVyEYdkzDqazxPD7RaTjx', 'DRdByGXTqxpVr72bZFXJ27Y2UQ2gfjtbr5tFDeEb8RG3', 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', '7T9uvDmpdKVzxsWkEQvpnZKnEsaK6LQ7tnDpd6pNJfZH'], 'writable': ['DY6pE7aiDafuk35REZF9p9av3vbV2VQrvdZ4YyB1pZ4C', '4Un9yaV18EBHApYRkEEpYWY3NsBPaABofWLNC21LapVE', 'Ai4kU7H79HHtK6pRTX13kqAgihH41afgLqnDAuPkekMC', 'CTUhs66Gph5q4BcdWKmRAYqWDvwkrU1xFukivEh2GXm2', 'EciLGydSE5RvGLQ3YutztkAzgcA48kNMrbASVigVKCZg', 'H75FJTVxzKcXsyxMsp2R1TSDP85m6LXiDFW5cFU4gL4W', '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'Gsy5Zr7Vxn5KckAbduPHHGR1qzPJ4w3GSYmcinWAkhrC', 'pKiUC9hDXv52xqU1p3BKypV9AQjAMgfZUGRnoBsdkKm', '2DjchPNarSqGJNNPCpXJCCagFv7Cn3wAhLd3nJCMpsE8', '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', '4Rvyik5jWSxXSapXrAJsnDdUrgU5cFRzNcvHygVpYQRH', '7GFUN3bWzJMKMRZ34JLsvcqdssDbXnp589SiE33KVwcC', 'C2aFPdENg4A2HQsmrd5rTw5TaYBX5Ku887cWjbFKtZpw', 'E8NKrYjZPstjbBXPPJp3qkEGjdw9BeVGvHMQpWGM9GQ3', 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'ATUMydDvNcELzNk9GP1Ky7i2Mgx2t2ej5aNPMhA6F2VH', 'ChcWkmUbWDbBspDjPX6ZXi7Hb9kZ7VTbNUf6nMtWF1YH']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]', 'Program log: CreateIdempotent', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: GetAccountDataSize', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 338794 compute units', 'Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program log: Initialize the associated token account', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeImmutableOwner', 'Program log: Please upgrade to SPL Token 2022 for immutable owner support', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 332207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 328325 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20442 of 344275 compute units', 'Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: CreateTokenAccount', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: InitializeAccount3', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 320275 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 6740 of 323833 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: RouteV2', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]', 'Program log: Instruction: swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 297844 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 292027 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Q3AAHurUU31rwC+8NeoW5ahnmHWb9iCYrT3cfO79wpk92QvqJ9W3ELwcfs2SZeoT6jUitWveLrWf7NXKuei1OfEzE3UX7jr9gTJTy+DnPr8V3nWq612cVgUiVfuqM9nRF+vmW3fGN5X5SW7T74cJwEbZ9oaJ31u0y5A0jtKppcKHj//h6NRTfWEZLYzLvptL8pZEty93e9FsZiX54eAxcFlQR/l+0ZYzm8cCt0LXR7586BbZxcUGQZ/VoR9P/GV4Kph5rP2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FZnNoG4eAxcCYWSPl+0ZYzKcYCt0LXR76U6xbZxcUGQaDMC6XW/WV4N+Rfuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 46763 of 309830 compute units', 'Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 227225 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 219520 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJaJ8GZhEw5RuMaegm7Kp2J14F+MzacEwMQH5MU0KK306AAmfg0LX6DKyx4AAAAAAAAAL8SNqLvhQ88eAAAAAAAAAPB3MlQ+AAAA5P3OEAAAAAAAAAAAAAAAAAAAAAAAAAAA0+HwBgAAAADYggkBAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 48542 of 259809 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 198974 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 193140 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19683 of 208058 compute units', 'Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [2]', 'Program log: Instruction: Buy', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ invoke [3]', 'Program log: Instruction: GetFees', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ consumed 4655 of 128795 compute units', 'Program return: pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ AgAAAAAAAABdAAAAAAAAAB4AAAAAAAAA', 'Program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 120025 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 111078 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 102056 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: TransferChecked', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 93031 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: Z/RSHyz1d3eWAuRoAAAAANQ2JJlUBQAA8PO6GAAAAAAAAAAAAAAAAPDzuhgAAAAAa6E3VavpAQA5TveqCAAAAOLQaxgAAAAAAgAAAAAAAAAYQAEAAAAAAF0AAAAAAAAAUyQ6AAAAAAD6EG0YAAAAALP2uRgAAAAAE2qrvCNj2IGSTJgIQW4lMDytD7YR7arIohmaVZ+qT9In23x60LKtrZbdNGyuGyj0ADl01fYU0EHbq2rZ6ng8yZeo75gq2QDn0AMZwNBnejFqXNlNYIlQ1kDmU4MBS5bgbG+mNnUhLe1gc/XMF7vvYC7/Zono+DGtS5riV7jnU1lgjMwd/OlhtDt3nBkVBabi079F1aTbRhitdsgtYXVFNV0OMm1Matf/fY9TP8MJCFS9H+8ykQhAD19V155Lh4BRiyUYBwQiLWWBvRgv+FbkGcAeqnLxzVwgEEPSplv+/VoeAAAAAAAAAGbBEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [3]', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 2027 of 79902 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA consumed 102460 of 175611 compute units', 'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 71322 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 69501 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 253054 of 317093 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 1DYkmVQFAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]', 'Program log: Instruction: CloseAccount', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2915 of 64039 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121796250128, 9912007, 2039280, 18938098122, 0, 2039280, 2039280, 70407360, 1844400, 70407360, 70407360, 1, 789146954, 1, 0, 2729681025, 5065007155, 2039380, 8352000, 2039283, 8352000, 52784640, 2039281, 6849541, 2039280, 2538088049828, 37639912739, 2978880, 97567361710, 53577114376, 25068895, 2039280, 5532941, 56513762977, 2039280, 3596047, 418677002208, 1000004, 1141472, 1158072388620, 0, 1161444, 1141440, 6551763765953, 4457500, 1142440, 1002022, 109153247, 18374406, 0, 1461600, 0], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '74463650', 'decimals': 6, 'uiAmount': 74.46365, 'uiAmountString': '74.46365'}}, {'accountIndex': 5, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 9, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 6, 'mint': 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '5860904679124', 'decimals': 6, 'uiAmount': 5860904.679124, 'uiAmountString': '5860904.679124'}}, {'accountIndex': 17, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HU23r7UoZbqTUuh3vA7emAGztFtqwTeVips789vqxxBw', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '6045215880', 'decimals': 6, 'uiAmount': 6045.21588, 'uiAmountString': '6045.21588'}}, {'accountIndex': 19, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'Ai4kU7H79HHtK6pRTX13kqAgihH41afgLqnDAuPkekMC', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '115303496137', 'decimals': 6, 'uiAmount': 115303.496137, 'uiAmountString': '115303.496137'}}, {'accountIndex': 22, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'H75FJTVxzKcXsyxMsp2R1TSDP85m6LXiDFW5cFU4gL4W', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '350235198190070', 'decimals': 9, 'uiAmount': 350235.19819007, 'uiAmountString': '350235.19819007'}}, {'accountIndex': 24, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '374025903438', 'decimals': 6, 'uiAmount': 374025.903438, 'uiAmountString': '374025.903438'}}, {'accountIndex': 25, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2538086010544', 'decimals': 9, 'uiAmount': 2538.086010544, 'uiAmountString': '2538.086010544'}}, {'accountIndex': 26, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '37637873459', 'decimals': 9, 'uiAmount': 37.637873459, 'uiAmountString': '37.637873459'}}, {'accountIndex': 28, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DRdByGXTqxpVr72bZFXJ27Y2UQ2gfjtbr5tFDeEb8RG3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '97565322430', 'decimals': 9, 'uiAmount': 97.56532243, 'uiAmountString': '97.56532243'}}, {'accountIndex': 29, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '53575075096', 'decimals': 9, 'uiAmount': 53.575075096, 'uiAmountString': '53.575075096'}}, {'accountIndex': 31, 'mint': 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '532536150420119', 'decimals': 6, 'uiAmount': 532536150.420119, 'uiAmountString': '532536150.420119'}}, {'accountIndex': 33, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '56511703659', 'decimals': 9, 'uiAmount': 56.511703659, 'uiAmountString': '56.511703659'}}, {'accountIndex': 34, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '480163480699117', 'decimals': 9, 'uiAmount': 480163.480699117, 'uiAmountString': '480163.480699117'}}], 'preBalances': [121802339687, 7807898, 2039280, 18937697123, 0, 2039280, 0, 70407360, 1844400, 70407360, 70407360, 1, 789146954, 1, 0, 2729681025, 5065007155, 2039380, 8352000, 2039283, 8352000, 52784640, 2039281, 6849541, 2039280, 2538220954288, 37230111785, 2978880, 97566132552, 53573303989, 25068895, 2039280, 5532941, 56795763845, 2039280, 3596047, 418677002208, 1000004, 1141472, 1158072388620, 0, 1161444, 1141440, 6551763765953, 4457500, 1142440, 1002022, 109153247, 18374406, 0, 1461600, 0], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '174463650', 'decimals': 6, 'uiAmount': 174.46365, 'uiAmountString': '174.46365'}}, {'accountIndex': 5, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '0', 'decimals': 9, 'uiAmount': None, 'uiAmountString': '0'}}, {'accountIndex': 17, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HU23r7UoZbqTUuh3vA7emAGztFtqwTeVips789vqxxBw', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '6043575880', 'decimals': 6, 'uiAmount': 6043.57588, 'uiAmountString': '6043.57588'}}, {'accountIndex': 19, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'Ai4kU7H79HHtK6pRTX13kqAgihH41afgLqnDAuPkekMC', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '115236611337', 'decimals': 6, 'uiAmount': 115236.611337, 'uiAmountString': '115236.611337'}}, {'accountIndex': 22, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'H75FJTVxzKcXsyxMsp2R1TSDP85m6LXiDFW5cFU4gL4W', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '350502898756070', 'decimals': 9, 'uiAmount': 350502.89875607, 'uiAmountString': '350502.89875607'}}, {'accountIndex': 24, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '373994428238', 'decimals': 6, 'uiAmount': 373994.428238, 'uiAmountString': '373994.428238'}}, {'accountIndex': 25, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2538218915004', 'decimals': 9, 'uiAmount': 2538.218915004, 'uiAmountString': '2538.218915004'}}, {'accountIndex': 26, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '37228072505', 'decimals': 9, 'uiAmount': 37.228072505, 'uiAmountString': '37.228072505'}}, {'accountIndex': 28, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'DRdByGXTqxpVr72bZFXJ27Y2UQ2gfjtbr5tFDeEb8RG3', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '97564093272', 'decimals': 9, 'uiAmount': 97.564093272, 'uiAmountString': '97.564093272'}}, {'accountIndex': 29, 'mint': 'So11111111111111111111111111111111111111112', 'owner': '7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '53571264709', 'decimals': 9, 'uiAmount': 53.571264709, 'uiAmountString': '53.571264709'}}, {'accountIndex': 31, 'mint': 'GVFJbBNZubBv1XqsBmakWKkCZsMEDnRZ55vXQSgMRCpd', 'owner': '2Jo61wyqPZBTvR154axVPgcQpLSWiQeViJXstvbmaPNH', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '538397055099243', 'decimals': 6, 'uiAmount': 538397055.099243, 'uiAmountString': '538397055.099243'}}, {'accountIndex': 33, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '56793704527', 'decimals': 9, 'uiAmount': 56.793704527, 'uiAmountString': '56.793704527'}}, {'accountIndex': 34, 'mint': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'owner': 'AHTTzwf3GmVMJdxWM8v2MSxyjZj8rQR6hyAC3g9477Yj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '479895780133117', 'decimals': 9, 'uiAmount': 479895.780133117, 'uiAmountString': '479895.780133117'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '3gb1sLekSgYBZPS3tmB9zJRbt3UyDewXtx9KAojwG4sJ', '76U6Ds3W2g9SY284AKQ5usDTv8B6TvJnupbM889a9EFA', '77N86XfcBSAvcGNPYMAVjjyf2feUJwmUoiJ96HzPtySd', '8JHmvYWTvgMCM4XZn3WpngwZRWWWgd9jxPB2c8rdnQ9e', 'AXNMeXbbEsK7LDMmFPgiEt9Msok3MBWetaZLWvaNtpx6', 'BD1yGZNeyTR6i2yaPCYR8zfXoEyXS8DFWx21g3WG25zo', 'CGYWxf8vWAeBVV2WSeu4hZGe8sjWc7ZPJZnFW7s3PCKy', 'DsVNyEhcD1F9apxPxeCb5Xdcia54uaZrcmjmLzk7qkAs', 'DWe8o233ok6muipK3qcnnuD1b5N1voao2GvReiy3bYzD', 'GBm5LJcFuJmhqsMi9Un1ooAeUdLkrUZGgGPFoWFLS5FB', '11111111111111111111111111111111', 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL', 'ComputeBudget111111111111111111111111111111', 'CTCAsP51f2jfXZUBxwgixoZmJ3EAM595N61Fq1gVm7Ni', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'], 'addressTableLookups': [{'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 40, 1, 86, 23], 'writableIndexes': [52]}, {'accountKey': 'AFfzVh7qC5MdvYj1fmfeyL6tvRDqLrxdwhooATZaST47', 'readonlyIndexes': [146, 14, 144], 'writableIndexes': [147, 148, 143, 142, 145]}, {'accountKey': 'D4QBMf27hQbL2JkaM1xy5gvQavLpPyXqf4SMcEsWwg43', 'readonlyIndexes': [148, 38, 206, 36, 22], 'writableIndexes': [203, 207, 204]}, {'accountKey': 'DxDSaPr5vw9g5kBFHjuNLgKXvXEaEAZJe4uVirn94haR', 'readonlyIndexes': [16, 141, 109], 'writableIndexes': [142, 138, 137, 136, 11, 106]}, {'accountKey': 'HpZkwQHLVJZE864sq7eR2hDtpJ9LZH65ZqrYUBzuQVsT', 'readonlyIndexes': [221], 'writableIndexes': [220, 229, 54]}], 'header': {'numReadonlySignedAccounts': 0, 'numReadonlyUnsignedAccounts': 6, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'LcVLq5', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [], 'data': '3ReKnJZaqz8P', 'programIdIndex': 13, 'stackHeight': 1}, {'accounts': [0, 6, 1, 50, 11, 16], 'data': '2', 'programIdIndex': 12, 'stackHeight': 1}, {'accounts': [4, 1, 39, 16, 11, 0], 'data': '2tDqDdUmhLW1t', 'programIdIndex': 15, 'stackHeight': 1}, {'accounts': [1, 2, 6, 36, 50, 16, 16, 15, 35, 15, 17, 42, 21, 18, 19, 20, 22, 2, 5, 1, 16, 40, 41, 16, 1, 32, 4, 33, 5, 34, 10, 9, 7, 51, 45, 1, 23, 4, 2, 25, 24, 14, 40, 16, 47, 27, 1, 44, 50, 39, 6, 4, 31, 26, 43, 29, 16, 16, 11, 12, 46, 47, 28, 49, 30, 8, 48, 38, 0, 37], 'data': 'PQB5t7vv4wRsESuAKYpvJqqrSdcR8oDZM7qKmD4s8zhhDPVKFwW78HSLenTTATdo2vMKSVcJATEoLw', 'programIdIndex': 15, 'stackHeight': 1}, {'accounts': [4, 1, 1], 'data': 'A', 'programIdIndex': 16, 'stackHeight': 1}, {'accounts': [0, 3], 'data': '3Bxs4J72XK7NHUAT', 'programIdIndex': 11, 'stackHeight': 1}], 'recentBlockhash': 'r9L2MGdbiRtVLH2gvQoZVs6rN667RrbWFRczMVE1U2n'}, 'signatures': ['Df8EmUzNvbLT7FZvZHdrZr7Vq1kwpSB67hW43XrX3xZTYrXrFzXMPvPnvRsv1tGQF5JMqRvtWrb1piVnSwPPwYM', '2Tsya2ZNFTYhnhe2nZ16nfrefa2MK8c2HLCqxnSzuBDT8FtLcr1QTmCuvYD7XozryM3PinwnH3scvN8syZwB8GQy']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### full_output_IV.py

**Issues:** 1

- **Line 2** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-06 18:55:42,747 - __main__ - ERROR - Uncertain action or token mint detected in main: action=unknown, token_mint=UNKNOWN, trade_info={'signature': '62GzueLZRbm4sfURKdnL13AasTJJhHCAogTosdR2BoffZMUDp1fvBmkcc2qetfKfCft731ZL1wqdqhkG24UsS5hy', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 42, 618259, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 300, 'costUnits': 1632, 'err': None, 'fee': 5000, 'innerInstructions': [], 'loadedAddresses': {'readonly': [], 'writable': []}, 'logMessages': ['Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success'], 'postBalances': [19258274510, 121776879239, 1, 1], 'postTokenBalances': [], 'preBalances': [19258280510, 121776878239, 1, 1], 'preTokenBalances': [], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'instructions': [{'accounts': [0, 1], 'data': '3Bxs4ffTu9T19DNF', 'programIdIndex': 2, 'stackHeight': 1}, {'accounts': [], 'data': 'FDJTAf', 'programIdIndex': 3, 'stackHeight': 1}], 'accountKeys': ['AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw', 'gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}, 'transaction_full': {'blockTime': 1759773343, 'meta': {'computeUnitsConsumed': 300, 'costUnits': 1632, 'err': None, 'fee': 5000, 'innerInstructions': [], 'loadedAddresses': {'readonly': [], 'writable': []}, 'logMessages': ['Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success'], 'postBalances': [19258274510, 121776879239, 1, 1], 'postTokenBalances': [], 'preBalances': [19258280510, 121776878239, 1, 1], 'preTokenBalances': [], 'rewards': [], 'status': {'Ok': None}}, 'slot': 371620916, 'transaction': {'message': {'accountKeys': ['AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw', 'gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111'], 'addressTableLookups': [], 'header': {'numReadonlySignedAccounts': 0, 'numReadonlyUnsignedAccounts': 2, 'numRequiredSignatures': 1}, 'instructions': [{'accounts': [0, 1], 'data': '3Bxs4ffTu9T19DNF', 'programIdIndex': 2, 'stackHeight': 1}, {'accounts': [], 'data': 'FDJTAf', 'programIdIndex': 3, 'stackHeight': 1}], 'recentBlockhash': 'JAsKK2HTaDjzXwiVh48uodAAhT6StqRazcPGk2GXXe6H'}, 'signatures': ['62GzueLZRbm4sfURKdnL13AasTJJhHCAogTosdR2BoffZMUDp1fvBmkcc2qetfKfCft731ZL1wqdqhkG24UsS5hy']}, 'version': 0}, 'router_program_id': None, 'dex_type': 'unknown'}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### full_output_V.py

**Issues:** 1

- **Line 3** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-06 18:55:55,427 - __main__ - INFO - 🚨 ⚡ SPEED TRADE DETECTION: {'signature': '41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', 'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'timestamp': datetime.datetime(2025, 10, 6, 17, 55, 55, 427124, tzinfo=datetime.timezone.utc), 'detection_method': 'websocket_logs', 'meta': {'computeUnitsConsumed': 393367, 'costUnits': 403892, 'err': None, 'fee': 310654, 'innerInstructions': [{'index': 2, 'instructions': [{'accounts': [2, 16, 1], 'data': '3awy1w6vdVeX', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [39, 23, 24, 25, 15, 16, 41, 44], 'data': 'J9A6eM58XaLWXKsmqBa2NbWp', 'programIdIndex': 43, 'stackHeight': 2}, {'accounts': [16, 25, 39], 'data': '3JpGTWoUyaDu', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [24, 15, 23], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42], 'data': '59p8WydnSZtV29EZJ5EPHbUYgwcyEPuwe7SXrhmNB83k1QhfcFC71rtXHa', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [15, 17, 39], 'data': '3dCWzEBYLYb9', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [19, 3, 21], 'data': '3Z6sYHBgK6Ky', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35], 'data': '59p8WydnSZtSYqyRFuqQPv9H538j1vw22B54xWsoUsCA53MawYHzdhGF2x', 'programIdIndex': 36, 'stackHeight': 2}, {'accounts': [16, 14, 39], 'data': '3JvGaqeJM4Hd', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [12, 3, 13], 'data': '3YMxHtDwKwzF', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28], 'data': 'wZRp7wZ3czsp8TiBYg9eUvG8CbxCoDYm42UzZBycSgh5Z3PVpMQRnwuz', 'programIdIndex': 46, 'stackHeight': 2}, {'accounts': [16, 27, 39], 'data': '3QJJ2xEUe3q1', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [32, 3, 26], 'data': '3FDG456PfyrP', 'programIdIndex': 41, 'stackHeight': 3}, {'accounts': [37], 'data': '4KbP49BdVApjtHuXZdNzDMRzUrFad32msbNDnEYAYPQjzkC9HQWsZg1bqYcV42HqWmzj35W86LMLAaDsXdQGXr8ABcyjSB2Yy87SyzmryVoMFg2uka2ui24a42mTckbKcFwx3Y2Eb9shgn5HevkmfzSeLBWjMYtYsaPqPgxPAghFzqsn88EC9wz8HdnuK9FYZjzy5wnjFY3g8pXfG8cLUUWa3V2U2YjRfFBCC35KxSZrwp7j7rSBAvVyRuoyaMG4xEpfdd2jLcJMMwcipiYk9YxfgYAgNgogzLaApf2JjMX59N2GBCHAQFQDYCQYMEvao1PwTBGz9hAZC562sXP9oJLAkrmUQz4Y3JNyL1A28SLxuPuK8tnf5yKx4mwe8rWLKv1S1DfEUbQrq4xP9vmgFEJJZ5i4QX5kyyJbcikf8Q7Bz4jKf4X8HDWNc6YigxvzPMBhT8X82kqsNojDZ', 'programIdIndex': 8, 'stackHeight': 2}, {'accounts': [2, 16, 1], 'data': '3avKVPuic5LT', 'programIdIndex': 41, 'stackHeight': 2}, {'accounts': [3, 5, 39], 'data': '3uktGuL5uriK', 'programIdIndex': 41, 'stackHeight': 2}]}], 'loadedAddresses': {'readonly': ['FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'GrzzQpVYkCoDnXGVpANW9iDGJk9EbcJJRj9FgY3GeVNm', 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'jitodontfront11111111111JustUseJupiterU1tra', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'FovDWEsftJv4X1EfapqVwG2VDcEDG2vsa7vaje3qAo56', 'SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe', 'Sysvar1nstructions1111111111111111111111111', 'A1BBtTYJd4i3xU8D6Tc2FzU6ZN4oXZWXKZnCxwbHXr8x', 'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK'], 'writable': ['4ZEwCEENfgAqzbyKLBDLZxSeixbKpZknirkWLFVcaLBw', '7yUHJWhvRnspqZKezhVHxJmsLLcfNyDn4dhYTCNNPTxe', '8z95LBWmSRKkQv1XPczvN6s2Fc3Rk5X6oi1ueW3nndBV', 'Bc1Ki733Cv9Fu2qGwar3n6EjQBofTpwrVAg2uSo5uLUV', 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'Efe7p9ZEbd99dCoGU3mbYbRRxU9tJuSmHX6jYDtbKC4x', '2p29nqD7DN1PczBMmgrFdtYKTfv6rJ7H3yMut4eu7nYT', '5SPztfEn1VAaWDBAXjQKwVrGbr6e8g3F6JJnUc9eCuSe', '2rJJP6RAyfo5HaoR9T6SDjWU885RkQBH3PyRpnoFrkDU', '3aSDFqAyFJPniaZpJf7Vn9PxZqT6dcuxzg9HXwWkbpVP', 'E83CnZbE1cz2ww5rqYuvWmAdMwWh3ZkJJcrbo49TaaGU', 'E9TL1PrwPxpdvMGjSXJQidJSmdBG4LYJJWoHDF5gSVv2', 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'H1j2gqzW61MrdjJsu6s5gamLq9wcKkinw1a7GWyjdd6k', 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'CTaDZW2LhvHPRnA9JWcZF8R5y2mpkV2RcHAXyEoKLbzp', 'JHVJLsPsbzNW8JP8cPYmrwfzD2M9aHXdFHSjeeCDERu', '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', '4LCiADXLEBW2JepG5iue3iTB3ozXb3YLGqheQNEWTSAY', '666Sz6bUgQwS2vgGDkPSwfqSsxtmBUh7Zvya6p2nkTJF', '7B5dskPoP5r2vXPDJgzvwCNTtuYwXVgV6KEeaWn8o2Ph', 'C86icgvRMBRHZWnTFjHnLh4o3BVroZYx5CHueZzAqByo', 'DnrPPNMp3ZqcCcrF8LEPLiXBiwMDPwELKFAy8ToHwUsD', 'FSGuR2PvoUqZvuQNxQVgyUeP4Mcsa89JxeqvAFWqSJdo', 'GwXt2aQ8gT39XT7HhcSdiDyTdxNgLY3pyJQm56mcbzWE']}, 'logMessages': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]', 'Program log: Instruction: SharedAccountsRouteV2', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 481240 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe invoke [2]', 'Program data: pdh0TD0K2EXg1EaJuOpAfML0kdG7eTH1XNQIEOVX4arCcGUFAAAAAFR8JhYAAAAAAAAAAAAAAAA=', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 329042 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 322257 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe consumed 156232 of 473513 compute units', 'Program SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 279648 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 271855 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbE9igrwVFQLItc6ZZ7SFyFaBP2yKFuol9OmxZQyTXehQEfLfERU7/3eBEAAAAAAAAAW3JAPlTypGwRAAAAAAAAAI3vkAwAAAAAdXB8yw4AAAAAAAAAAAAAAAAAAAAAAAAAxPwbAAAAAACYLgQAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 50294 of 313987 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 222909 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 215207 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: 4cpJr5MroJbEfUf/rGK5gbB3j1i9SOV3OvJnNUa214qEuf7HuPxM9QGxaFSONmXM4iMAAAAAAAAAhf4pUAQnKNYjAAAAAAAAACClXTcAAAAAcQPzWRMBAAAAAAAAAAAAAAAAAAAAAAAAi097AAAAAAD9bBIAAAAAAA==', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 53099 of 260144 compute units', 'Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK invoke [2]', 'Program log: Instruction: Swap', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 126055 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 118750 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program data: QMbN6CYIceIZgsvldDwQ5dniClXHJhtLQRLYtVLKhQRvzPxIAg95AvGIUF6HpIvZ2Z7BHOYYqMz0tba64TJcsynpxUM2jtAdQfBFoL2Q+hTIr9i6OxAd6c2qX0PXm3UplKxcPpJZymdfJfxKK6vSVShD3WDotAiA59j1uOLR13muMnrDRuLOqkDPMAEAAAAAAAAAAAAAAAAKe6DuBQAAAAAAAAAAAAAAAYajGoe4suDXIwAAAAAAAAB3iI44OwAAAAAAAAAAAAAAohcBAA==', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK consumed 94312 of 203194 compute units', 'Program CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 107023 compute units', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 105120 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 98417 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 392917 of 486558 compute units', 'Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 8O4PFCgBAAA=', 'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success'], 'postBalances': [121763506924, 9204256, 2039280, 2039280, 20152947666, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8769954653, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599752863345, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'postTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '2430379783', 'decimals': 6, 'uiAmount': 2430.379783, 'uiAmountString': '2430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1290180175863', 'decimals': 6, 'uiAmount': 1290180.175863, 'uiAmountString': '1290180.175863'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3329485185848465', 'decimals': 6, 'uiAmount': 3329485185.848465, 'uiAmountString': '3329485185.848465'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '519465211363', 'decimals': 6, 'uiAmount': 519465.211363, 'uiAmountString': '519465.211363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4059641614', 'decimals': 6, 'uiAmount': 4059.641614, 'uiAmountString': '4059.641614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8767915373', 'decimals': 9, 'uiAmount': 8.767915373, 'uiAmountString': '8.767915373'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4072118737060', 'decimals': 6, 'uiAmount': 4072118.73706, 'uiAmountString': '4072118.73706'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599731804056', 'decimals': 9, 'uiAmount': 7599.731804056, 'uiAmountString': '7599.731804056'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713647633243', 'decimals': 6, 'uiAmount': 1713647.633243, 'uiAmountString': '1713647.633243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '751162111', 'decimals': 6, 'uiAmount': 751.162111, 'uiAmountString': '751.162111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3625092093786', 'decimals': 6, 'uiAmount': 3625092.093786, 'uiAmountString': '3625092.093786'}}], 'preBalances': [121763893741, 9204256, 2039280, 2039280, 20152871503, 2039280, 1, 1, 2729681025, 70407360, 70407360, 70407360, 2039280, 5444261, 2039280, 17262759852, 2039380, 8559129552, 70407360, 2039280, 70407360, 5475295, 70407360, 1103058290, 7599963688446, 2039286, 11637120, 2039280, 72161280, 72161280, 13641600, 32092560, 2039280, 72161280, 1388736628, 0, 1161444, 3596047, 418677002208, 214148060, 1000004, 5065007155, 0, 1141546, 0, 1705200, 1844545650], 'preTokenBalances': [{'accountIndex': 2, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3430379783', 'decimals': 6, 'uiAmount': 3430.379783, 'uiAmountString': '3430.379783'}}, {'accountIndex': 3, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '36977127185', 'decimals': 6, 'uiAmount': 36977.127185, 'uiAmountString': '36977.127185'}}, {'accountIndex': 5, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '18533267719', 'decimals': 6, 'uiAmount': 18533.267719, 'uiAmountString': '18533.267719'}}, {'accountIndex': 12, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3330667810953218', 'decimals': 6, 'uiAmount': 3330667810.953218, 'uiAmountString': '3330667810.953218'}}, {'accountIndex': 14, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'EE1i59YUAELZj4qe8sHgsYd7wYuwe2YRoJMmkCjJEiGt', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '518536327363', 'decimals': 6, 'uiAmount': 518536.327363, 'uiAmountString': '518536.327363'}}, {'accountIndex': 15, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '17260718568', 'decimals': 9, 'uiAmount': 17.260718568, 'uiAmountString': '17.260718568'}}, {'accountIndex': 16, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4058441614', 'decimals': 6, 'uiAmount': 4058.441614, 'uiAmountString': '4058.441614'}}, {'accountIndex': 17, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '8557090272', 'decimals': 9, 'uiAmount': 8.557090272, 'uiAmountString': '8.557090272'}}, {'accountIndex': 19, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': 'EFrcT2vfjJkk4coTVXShgbApQV5mdQbrQpbxjvLMfGK6', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '4135662209305', 'decimals': 6, 'uiAmount': 4135662.209305, 'uiAmountString': '4135662.209305'}}, {'accountIndex': 24, 'mint': 'So11111111111111111111111111111111111111112', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '7599942629157', 'decimals': 9, 'uiAmount': 7599.942629157, 'uiAmountString': '7599.942629157'}}, {'accountIndex': 25, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': 'CAPhoEse9xEH95XmdnJjYrZdNCA8xfUWdy3aWymHa1Vj', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '1713597693243', 'decimals': 6, 'uiAmount': 1713597.693243, 'uiAmountString': '1713597.693243'}}, {'accountIndex': 27, 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '731186111', 'decimals': 6, 'uiAmount': 731.186111, 'uiAmountString': '731.186111'}}, {'accountIndex': 32, 'mint': 'FRySi8LPkuByB7VPSCCggxpewFUeeJiwEGRKKuhwpKcX', 'owner': '2iasS1t2jFKxSifaT7McxEGPQN2xL5QfsPmu55n8dMP7', 'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'uiTokenAmount': {'amount': '3650570424932', 'decimals': 6, 'uiAmount': 3650570.424932, 'uiAmountString': '3650570.424932'}}], 'rewards': [], 'status': {'Ok': None}}, 'transaction': {'message': {'accountKeys': ['gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB', '7BP2NKc858GkJ6pwALbtEraroMGE3Tax68SGxzhuwT7F', '5ht281axHQXoQ2PWD6vrxxnHEa8TmsLuzs7XTDnmTdCt', '7QRKuCbdjxRjno55LE1GGFVKqxeFUWeNtUaLQ4a9Gz9X', '9fBpwxcudpLyJskhiiKmU8wPszeUuCB8sSjhPi44QuFb', 'B95oUgde4SfoekubbV1hbFanLBRV7UL26zXqcZZhHdrx', '11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111', 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'], 'addressTableLookups': [{'accountKey': '2z84tgaUYNWMwotQjmSpRygdH96m5M5VpUqZQH1L24UF', 'readonlyIndexes': [70, 68, 12], 'writableIndexes': [67, 64, 65, 66, 58, 63]}, {'accountKey': '3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW', 'readonlyIndexes': [0, 40, 11, 1, 20], 'writableIndexes': [32, 49]}, {'accountKey': 'DWSgR97yTc3WENhkddFBkoBsute6mKpaJ5Kkfix8KWXb', 'readonlyIndexes': [225], 'writableIndexes': [219, 229, 188, 227, 222, 223]}, {'accountKey': 'EE8XintbVcFLm3CR3rNLfW5WcBKDtsniQwLKsWz3enYi', 'readonlyIndexes': [168, 173], 'writableIndexes': [169, 170, 171]}, {'accountKey': 'JBMZHmsCUZEfXpNPm4N1XQ2seJbDo3CFSfmQjK4mShDh', 'readonlyIndexes': [34, 40], 'writableIndexes': [37, 29, 38, 35, 33, 41, 39, 31]}], 'header': {'numReadonlySignedAccounts': 1, 'numReadonlyUnsignedAccounts': 3, 'numRequiredSignatures': 2}, 'instructions': [{'accounts': [], 'data': 'KGAnEb', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [], 'data': '3QZwSzAJHXSo', 'programIdIndex': 7, 'stackHeight': 1}, {'accounts': [39, 1, 2, 16, 3, 5, 38, 34, 41, 41, 37, 8, 16, 43, 39, 23, 24, 25, 15, 16, 41, 44, 36, 41, 39, 21, 15, 17, 3, 19, 18, 22, 20, 42, 36, 41, 39, 13, 16, 14, 3, 12, 10, 11, 9, 35, 46, 39, 45, 26, 16, 3, 27, 32, 31, 41, 29, 30, 33, 28, 8, 40], 'data': '2uadBoC4kUfkSytM1gJGnMJKGK8Uu9K455iqA8iRquZaLonKccX4BABoNf9v5VVL7q1N21BztbkGU7cw', 'programIdIndex': 8, 'stackHeight': 1}, {'accounts': [0, 4], 'data': '3Bxs4No5VVsho7hh', 'programIdIndex': 6, 'stackHeight': 1}], 'recentBlockhash': 'EZUJNZw94LezE4g9mf2Ku8FJ1dkMqyRQ4ieEUxBWnhMj'}, 'signatures': ['41XddLGpKhzGDZAb6VfPVuErRu42CRxMVqL4jgcKTCQwYwRrBq76GH93bx7Dd4Exv4j4nfT5Fvx3Qkm6xtvc1cxH', '3pXHMYvd5xKeyxUMUNNPEWK2Meu6Kwnb3HYkFdNW4dbpY1dN72nL1e75H1oX8BrWfoNgRXz6gbpcW1RLttDavnGt']}, 'parsed_tx': {'dex': 'Unknown', 'parsed': False}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### generic_executor.py

**Issues:** 1

- **Line 85** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `send_result = await self.rpc_client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

### get_complete_logs.py

**Issues:** 2

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

### get_exact_16_accounts.py

**Issues:** 2

- **Line 6** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Commitment`
  - Fix: Replace with solders equivalent: from solders.* import ...

### hybrid_clmm_trader.py

**Issues:** 6

- **Line 155** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 254** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 332** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### hybrid_trader.py

**Issues:** 5

- **Line 215** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 334** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 45** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 52** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 53** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Finalized, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### init_observation_via_clmm.py

**Issues:** 3

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Commitment`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### initialize_observation.py

**Issues:** 4

- **Line 116** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### integrated_trade_monitor.py

**Issues:** 1

- **Line 192** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### jito_tips.py

**Issues:** 2

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 11** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### jupiter_copy_bot.py

**Issues:** 5

- **Line 374** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 506** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(tx, opts=opts)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 24** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### jupiter_copy_executor.py

**Issues:** 8

- **Line 250** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 253** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 283** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 286** 🔴 [NONE_RETURN] Function 'execute_copy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 345** 🔴 [NONE_RETURN] Function 'execute_buy_copy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 351** 🔴 [NONE_RETURN] Function 'execute_buy_copy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 360** 🔴 [NONE_RETURN] Function 'execute_buy_copy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 363** 🔴 [NONE_RETURN] Function 'execute_buy_copy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### jupiter_trade_executor.py

**Issues:** 5

- **Line 403** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `sig = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 472** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `sig = await self.client.send_transaction(tx, opts=opts)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### jupiter_trader.py

**Issues:** 8

- **Line 375** 🔴 [NONE_RETURN] Function 'execute_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 379** 🔴 [NONE_RETURN] Function 'execute_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 394** 🔴 [NONE_RETURN] Function 'execute_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 415** 🔴 [NONE_RETURN] Function 'execute_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 419** 🔴 [NONE_RETURN] Function 'execute_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 31** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 32** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### jupiter_utils.py

**Issues:** 1

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### live_test.py

**Issues:** 1

- **Line 144** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-12 19:52:43,676 - __main__ - DEBUG - [DEBUG] Received trade_info: {"signature": "5qbjjcFhxCvrTHGekucWQZ1vQkg1Ymv7779yFJ748VkKsi6iu8rP1Z21LYKbtBrrDLMPwCWTjZ4BSUDhCByAhTCG", "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 248857 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C invoke [2]", "Program log: Instruction: SwapBaseInput", "Program data: QMbN6CYIceJI4udx59A3ofmMlP1m9B+Pj46toZZSB/5r+9rwnJg3BZlv5SAKAAAAtlc+b/E5AAAMmVgVAAAAACIxqNt3AAAAAAAAAAAAAAAAAAAAAAAAAAEHBy8FSrSNmH2k5ZaeYyzd843WQUE0naQbC2lbkdFcOgFKMZOdXl4qu+33PLDiIfHZfFZQAESzDEeFcAC2PkEXX6U2AAAAAAB4uwIAAAAAAAE=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 217120 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 207784 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C consumed 40848 of 240875 compute units", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]", "Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh5Hlw8AAAAAAKGPOhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 148467 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 142401 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 56610 of 192614 compute units", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123744 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 117910 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19743 of 132888 compute units", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 83032 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 74271 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 65162 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 46765 of 108843 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 60219 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 58316 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 51614 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 207568 of 254407 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 Pq5fS3oAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "timestamp": "2025-10-12 18:52:43.676305+00:00", "detection_method": "websocket_logs", "meta": {"computeUnitsConsumed": 208018, "costUnits": 217583, "err": null, "fee": 1327265, "innerInstructions": [{"index": 2, "instructions": [{"accounts": [6, 3, 1], "data": "3o6gTY92PWS3", "programIdIndex": 39, "stackHeight": 2}, {"accounts": [19, 42, 46, 28, 3, 5, 31, 30, 39, 39, 47, 32, 29], "data": "E73fXHPWvSR26xdrkcn61Mfy9PBXZeF11", "programIdIndex": 40, "stackHeight": 2}, {"accounts": [3, 47, 31, 19], "data": "gGFSQLtFifcMK", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [30, 32, 5, 42], "data": "gYC7zK6KnzT65", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [19, 25, 44, 11, 26, 27, 3, 20, 47, 36, 39, 39, 43], "data": "KcznxBaB6yLt1qxnuAtjGA3q", "programIdIndex": 45, "stackHeight": 2}, {"accounts": [3, 26, 19], "data": "3mAA1WCjWQ39", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [27, 20, 25], "data": "3axGPDMLwZFu", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [19, 22, 21, 20, 24, 23, 8, 43, 39], "data": "2d6h89NAF1vPVgxDFFpt5ctHNXr", "programIdIndex": 41, "stackHeight": 2}, {"accounts": [20, 23, 19], "data": "3axGPDMLwZFu", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [24, 21, 22], "data": "3NuWBSfJDtT1", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [17, 34, 14, 16, 21, 5, 32, 38, 15, 34, 19, 39, 39, 33, 34, 18, 13, 12], "data": "PgQWtn8oziwwmBJTsh8GDDrdH3tAuFKtT", "programIdIndex": 34, "stackHeight": 2}, {"accounts": [21, 38, 16, 19], "data": "gpeTSRCfp74UY", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [14, 32, 5, 17], "data": "gTyviGyM6hC53", "programIdIndex": 39, "stackHeight": 3}, {"accounts": [33], "data": "yCGxBopjnVNQkNP5usq1Pp1LotWgFqhshb2FwZvZaweHPpnc6jtd3TYTRQKLLqwJB3B3AvrSdvAaw1d3JCvZJyhaZft26fdbqfh6CTFkcvxYo64ekV4ikyVVmGwScaJaML7PaE4ShmAfMADuCyTh85PQmuUoeGBAZLJYpPSjnc7QMtXdmwni9DCLD6h7XDLYrZLkr3", "programIdIndex": 34, "stackHeight": 3}, {"accounts": [35], "data": "4KbP49BdVApjtHuXZdNzDMRzUrFZqdN9HrSffmYR1ngUfG8AxF9yxqkSPQhzo1FH8DcWEYzgW7gThnehHfaYLLHcUPBMFT4hunDc4scFAugqeVeh4A1NaVfFniBRPfDXbAKjPFRe5nnDjmwuSQ8rV5A8DMGwiePWaH1kZeB2t8gdzosXTx3nQmJ7tNKHSoTTbpwd88k3S1mP9ARCNT5CdcAyC9Lh7ZuQNUuScM45UxcpdN5vuFDVzdXuDPLrSKXjQVvF5zYSufRDnsJyiMbVNUqGymvjZWsVoxj7Y5jQBr9LskESY8F91LCr5KTvyTiNPdjLp95p7erPpYpiUZqB5goFZU68NY31bHEgJPb8TXBQ3AdpGqL1Xi3tjAYcXMt1emenAhrTicnPL3DviwMycqEeUnxHgZ5JYijHh6V4Gx9xxbRix41FF4TqQwwrg51VpUAMQM42pCoxSL1qy", "programIdIndex": 10, "stackHeight": 2}, {"accounts": [6, 3, 1], "data": "3EkbcbviRwzF", "programIdIndex": 39, "stackHeight": 2}, {"accounts": [5, 4, 19], "data": "3PweZcmXEcz3", "programIdIndex": 39, "stackHeight": 2}]}], "loadedAddresses": {"readonly": ["632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "D1ZN9Wj1fRSUQfCjhvnu1hqDMT7hzjzBBpi12nVniYD6", "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo", "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "jitodontfront11111111111JustUseJupiterU1tra", "So11111111111111111111111111111111111111112", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C", "goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j", "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "Sysvar1nstructions1111111111111111111111111", "By9zHEbZJvYrBws27SqPXggfSAH3fjnJcdxKgdogyXUm", "SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF", "G95xxie3XbkCqtE39GgQ9Ggc7xBC8Uceve7HFDEFApkc", "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB"], "writable": ["4LzG4fCcbxMYDYzPcmfRzAQeVSkkB2qeaZnHDVK4zrkp", "5oQuwHERHx3E5TptB8HpeUWfbUs7EzjboFZiFyAkiFes", "9PBsqbBF1zEDck2YbkeAFNmAFMH75ZUWW7BA2Wv2Z7SY", "Ax3hzMZDuJjRoHuj86MkF9p5Vq8bWFKC7GZBs5mgfntq", "C4Y3AhocJzHZFK3gjjanjCxoFxBjZsBpo8BdU8dEbx2L", "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "FamNAW9SyTjDivRAPAaZfzSqgDgbAHNVb7oxYSpipoSS", "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "E6LAwCLSHLkDCoMXZPtnDtpcvCYWcs3ZZLHLreiFwjUi", "qqdJ4z1yu4sTbAitwXZsGNDoGZFgL2HfVKSVwAXWCfq", "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "Gsy5Zr7Vxn5KckAbduPHHGR1qzPJ4w3GSYmcinWAkhrC", "pKiUC9hDXv52xqU1p3BKypV9AQjAMgfZUGRnoBsdkKm", "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "CRF6Tegjtv3k9tuvKKbXroq4UmKXh9ZP92tn17sjjsFY", "CT8B2qJAqy93GAU5Qor9s5xGGQEoiEwSSNRPAaDFYrgL", "5uX2hmJJMUwXynsisoiCbQfD9mkos3uCkqhDgQWPRDSk", "C45FMw2N3n5ZE5A74jkvL6LNAjSLxiL6bn2oESu29rFh", "Ekt1x1kLzMxiq9XU2oPHU1GDHZg7SKKZTqjpEkD6WMoH", "HpHh4LdNtcfGrJAjuABcdWUP1fAADr3USvpkX81rnrki"]}, "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 248857 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C invoke [2]", "Program log: Instruction: SwapBaseInput", "Program data: QMbN6CYIceJI4udx59A3ofmMlP1m9B+Pj46toZZSB/5r+9rwnJg3BZlv5SAKAAAAtlc+b/E5AAAMmVgVAAAAACIxqNt3AAAAAAAAAAAAAAAAAAAAAAAAAAEHBy8FSrSNmH2k5ZaeYyzd843WQUE0naQbC2lbkdFcOgFKMZOdXl4qu+33PLDiIfHZfFZQAESzDEeFcAC2PkEXX6U2AAAAAAB4uwIAAAAAAAE=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 217120 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 207784 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C consumed 40848 of 240875 compute units", "Program CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF invoke [2]", "Program data: G9/8BaOeaFroXq/f9TKJxhu2PPWIJe6cIOnugHaZDh5Hlw8AAAAAAKGPOhYAAAAAAAAAAAAAAAAAAAAAAAAAAA==", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 148467 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 142401 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF consumed 56610 of 192614 compute units", "Program SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j invoke [2]", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123744 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 117910 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j consumed 19743 of 132888 compute units", "Program goonERTdGsjnkZqWuVjs73BZ3Pb9qoCUdBUL17BnS5j success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 83032 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 74271 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 65162 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 46765 of 108843 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 60219 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 58316 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4644 of 51614 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 207568 of 254407 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 Pq5fS3oAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "postBalances": [121435305597, 9760911, 21545145300, 2039280, 2039280, 2039280, 2039280, 1, 0, 1, 2729681025, 7298979842, 71437440, 71437440, 2039280, 23385600, 67490882898, 7182720, 71437440, 171551098, 2039280, 2415112199, 6849547, 2039281, 2776792400852, 12917769, 2039280, 2039280, 5324400, 29252880, 2039280, 2039280, 1461600, 4000419, 32941452, 3596047, 418938902554, 1000004, 1171250707549, 5289313643, 45791780, 1142441, 1221496159635, 0, 2060160, 1141441, 2533440, 98390921], "postTokenBalances": [{"accountIndex": 3, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "6360473", "decimals": 6, "uiAmount": 6.360473, "uiAmountString": "6.360473"}}, {"accountIndex": 4, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "525250571838", "decimals": 6, "uiAmount": 525250.571838, "uiAmountString": "525250.571838"}}, {"accountIndex": 5, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "7677766270", "decimals": 6, "uiAmount": 7677.76627, "uiAmountString": "7677.76627"}}, {"accountIndex": 6, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "366205648", "decimals": 6, "uiAmount": 366.205648, "uiAmountString": "366.205648"}}, {"accountIndex": 14, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "26626085502162", "decimals": 6, "uiAmount": 26626085.502162, "uiAmountString": "26626085.502162"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "67488843618", "decimals": 9, "uiAmount": 67.488843618, "uiAmountString": "67.488843618"}}, {"accountIndex": 20, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2685286213", "decimals": 6, "uiAmount": 2685.286213, "uiAmountString": "2685.286213"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2413072917", "decimals": 9, "uiAmount": 2.413072917, "uiAmountString": "2.413072917"}}, {"accountIndex": 23, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "371709943212", "decimals": 6, "uiAmount": 371709.943212, "uiAmountString": "371709.943212"}}, {"accountIndex": 24, "mint": "So11111111111111111111111111111111111111112", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2776790361568", "decimals": 9, "uiAmount": 2776.790361568, "uiAmountString": "2776.790361568"}}, {"accountIndex": 26, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "145137051061", "decimals": 6, "uiAmount": 145137.051061, "uiAmountString": "145137.051061"}}, {"accountIndex": 27, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "64414390274", "decimals": 6, "uiAmount": 64414.390274, "uiAmountString": "64414.390274"}}, {"accountIndex": 30, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "63202802214455", "decimals": 6, "uiAmount": 63202802.214455, "uiAmountString": "63202802.214455"}}, {"accountIndex": 31, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "48032353295", "decimals": 6, "uiAmount": 48032.353295, "uiAmountString": "48032.353295"}}], "preBalances": [121436963178, 9760911, 21544814984, 2039280, 2039280, 2039280, 2039280, 1, 0, 1, 2729681025, 7298979842, 71437440, 71437440, 2039280, 23385600, 67452971546, 7182720, 71437440, 171551098, 2039280, 2415112199, 6849547, 2039281, 2776830312204, 12917769, 2039280, 2039280, 5324400, 29252880, 2039280, 2039280, 1461600, 4000419, 32941452, 3596047, 418938902554, 1000004, 1171250707549, 5289313643, 45791780, 1142441, 1221496159635, 0, 2060160, 1141441, 2533440, 98390921], "preTokenBalances": [{"accountIndex": 3, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "5591442", "decimals": 6, "uiAmount": 5.591442, "uiAmountString": "5.591442"}}, {"accountIndex": 4, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "0", "decimals": 6, "uiAmount": null, "uiAmountString": "0"}}, {"accountIndex": 5, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "7677766270", "decimals": 6, "uiAmount": 7677.76627, "uiAmountString": "7677.76627"}}, {"accountIndex": 6, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "732411296", "decimals": 6, "uiAmount": 732.411296, "uiAmountString": "732.411296"}}, {"accountIndex": 14, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "26636549732846", "decimals": 6, "uiAmount": 26636549.732846, "uiAmountString": "26636549.732846"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "DHU9TY7NdtYsqgZk92PfitkoG5AV8rDxMaX2ibBVcMzz", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "67450932266", "decimals": 9, "uiAmount": 67.450932266, "uiAmountString": "67.450932266"}}, {"accountIndex": 20, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2685286213", "decimals": 6, "uiAmount": 2685.286213, "uiAmountString": "2685.286213"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "69yhtoJR4JYPPABZcSNkzuqbaFbwHsCkja1sP1Q2aVT5", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2413072917", "decimals": 9, "uiAmount": 2.413072917, "uiAmountString": "2.413072917"}}, {"accountIndex": 23, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "371702635308", "decimals": 6, "uiAmount": 371702.635308, "uiAmountString": "371702.635308"}}, {"accountIndex": 24, "mint": "So11111111111111111111111111111111111111112", "owner": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2776828272920", "decimals": 9, "uiAmount": 2776.82827292, "uiAmountString": "2776.82827292"}}, {"accountIndex": 26, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "145129742328", "decimals": 6, "uiAmount": 145129.742328, "uiAmountString": "145129.742328"}}, {"accountIndex": 27, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "2sp6rCc4VaXJ5qCbrPukpQVjZVZey42pj7QkynYNDdw3", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "64421698178", "decimals": 6, "uiAmount": 64421.698178, "uiAmountString": "64421.698178"}}, {"accountIndex": 30, "mint": "632SvBrfaep51NGKnKtUHTR9J2T4uYGKEQkCgy42USA", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "63717588555609", "decimals": 6, "uiAmount": 63717588.555609, "uiAmountString": "63717588.555609"}}, {"accountIndex": 31, "mint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB", "owner": "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "47674225411", "decimals": 6, "uiAmount": 47674.225411, "uiAmountString": "47674.225411"}}], "rewards": [], "status": {"Ok": null}}, "transaction": {"message": {"accountKeys": ["gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB", "BX3fp8BAedrtixA2G1opJ81e3M3t2J3kZfpiv1TTe7iz", "77N86XfcBSAvcGNPYMAVjjyf2feUJwmUoiJ96HzPtySd", "8cHRSqBtNw4sbzq1aSGZYaMPsfG7CsksZLik9AWF29z", "9itSauTyTV1TqepGGSFE1Xqpr8QrwU896ejDqoCsc41Y", "FswGbE4Drue6KiDYzXWfhoSWdtnhJLHarc4xqeDZU2Xq", "FX2cJi3TQ7fehdNEo9P4y5Ye2FR1bt6cSKmYJ9Md95eN", "11111111111111111111111111111111", "9FcdAZrMX1zxd3mBDAzCqfoYCw3ubRrG3Ch9ZnTRmq8g", "ComputeBudget111111111111111111111111111111", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", "QoFvFhDZg9TaZEi4SsasWpH5xXzk3zBqfRyicGexfNQ"], "addressTableLookups": [{"accountKey": "2MU934HtM4i8wzemrCcx1TfSHer5ryGPt9UKL81VgNJ6", "readonlyIndexes": [29, 30, 62], "writableIndexes": [65, 24, 27, 25, 28, 64, 31]}, {"accountKey": "3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW", "readonlyIndexes": [0, 40, 1, 23, 20], "writableIndexes": [13, 51, 34]}, {"accountKey": "D4QBMf27hQbL2JkaM1xy5gvQavLpPyXqf4SMcEsWwg43", "readonlyIndexes": [6, 206, 0, 201], "writableIndexes": [203, 207, 204]}, {"accountKey": "DMQiFwkdPjts3db8RiYpeiSu4R4CyBjUVhX2v7y8HUWF", "readonlyIndexes": [52, 55], "writableIndexes": [51, 53, 59]}, {"accountKey": "ESb1zo7dy5VvQ7yfuWqmkpw6Fm3bVi5PEcqPrRUB1jeu", "readonlyIndexes": [251, 244], "writableIndexes": [245, 250, 249, 246]}], "header": {"numReadonlySignedAccounts": 1, "numReadonlyUnsignedAccounts": 5, "numRequiredSignatures": 2}, "instructions": [{"accounts": [], "data": "LKdZq1", "programIdIndex": 9, "stackHeight": 1}, {"accounts": [], "data": "3skHkfbuoXPV", "programIdIndex": 9, "stackHeight": 1}, {"accounts": [19, 1, 6, 3, 5, 4, 47, 32, 39, 39, 35, 10, 3, 40, 19, 42, 46, 28, 3, 5, 31, 30, 39, 39, 47, 32, 29, 45, 19, 25, 44, 11, 26, 27, 3, 20, 47, 36, 39, 39, 43, 41, 19, 22, 21, 20, 24, 23, 8, 43, 39, 34, 17, 34, 14, 16, 21, 5, 32, 38, 15, 34, 19, 39, 39, 33, 34, 18, 13, 12, 10, 37], "data": "2uadBoC4kUfkUzUFsLsCUVVvSkycFZqiQaEFzCJ4hkQLvh6N3egyDzFA2nr5xBAoBJrSYjNvcX7KDBXH", "programIdIndex": 10, "stackHeight": 1}, {"accounts": [0, 2], "data": "3Bxs4DaLPq2VNELw", "programIdIndex": 7, "stackHeight": 1}], "recentBlockhash": "3AxLkueqDtPJz3T3JALraJpfye5S3FQs4UQJWZZwQxRE"}, "signatures": ["5qbjjcFhxCvrTHGekucWQZ1vQkg1Ymv7779yFJ748VkKsi6iu8rP1Z21LYKbtBrrDLMPwCWTjZ4BSUDhCByAhTCG", "5mpH1hSbF9BXgSu7sYmoeoZh4G46DpQAn2ntyia96MaUAwRPrh8pLMJaAYzaA2oAGtZSr5xcqqLnek8GAm9bEbW8"]}, "parsed_tx": {"dex": "unknown", "action": "unknown", "mint": null, "amount": null, "signature": null, "source_wallet": null, "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "unknown", "confidence": 0}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### live_test_II.py

**Issues:** 1

- **Line 50** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-12 18:55:28,558 - __main__ - DEBUG - [DEBUG] Received trade_info: {"signature": "3v9GsuiHTeGmJNJbRNzJGj9ZQ5RhGGgKwZrvvZZvYy7KKhiaRbUqLa3okH8TtumqY4ZU74E2FcWgJExjYFTEJpyC", "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 112754 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]", "Program log: ray_log: AyIM2xIUAAAAAAAAAAAAAAABAAAAAAAAAA2WUGoUAAAAJ8lResUCAABJbbku8ykAADw6BFIBAAAA", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 91974 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 84860 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 25831 of 105380 compute units", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]", "Program log: Instruction: swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66442 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 60534 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/ufnQT/ggSLdQ/BT3+/o5a1Dxa89BYqFP/RkXA2L0UEcBfZyrmuHnPr9+QuC/1V2cVtYRScnWsSHRF+vmW3fGN5XioGHT74cJwEbZ9oaJ31u0Nm/LcdOppcK9j//h69RTfaAuMhjLvptLWB32/hF3e9ERYSX54eAxcJmWVvl+0ZYzm8cCt0LXR75HfzZjxcUGQd46hztP/GV4Np15rP2WBjTBIrHI4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FinNoG4eAxcF4TSPl+0ZYzm8cCt0LXR76s7xbZxcUGQc3wMcbW/WV4xvVDuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 40513 of 76513 compute units", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 34275 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 32023 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 25587 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 95625 of 116436 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 f26VQQAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "timestamp": "2025-10-12 17:55:28.557756+00:00", "detection_method": "websocket_logs", "meta": {"computeUnitsConsumed": 96075, "costUnits": 102072, "err": null, "fee": 88330, "innerInstructions": [{"index": 2, "instructions": [{"accounts": [3, 4, 1], "data": "3K9tj26pg5EP", "programIdIndex": 25, "stackHeight": 2}, {"accounts": [25, 17, 26, 16, 18, 4, 14, 23], "data": "9nznFBXsXGEtbXLdbbuBQdD", "programIdIndex": 27, "stackHeight": 2}, {"accounts": [4, 18, 23], "data": "3K9tj26pg5EP", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [16, 14, 26], "data": "3PXqUYe8heWj", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [11, 9, 10, 13, 12, 14, 15, 23, 25, 19], "data": "4Q7KEgP54q45GpgmEPEvVcB", "programIdIndex": 20, "stackHeight": 2}, {"accounts": [14, 10, 23], "data": "3PXqUYe8heWj", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [12, 15, 12], "data": "3fYBp4GtthRh", "programIdIndex": 25, "stackHeight": 3}, {"accounts": [21], "data": "RkQoknrFGESHWQ2WBEU8ZchvjAkGNA8o8CneJpdndrKUUiBtSBbrEFTk5Dv3oybgNqNh8j6VMgCrnNyvQ8sxHcyjboDEHiUS1so6f28yxrcPMYaRfMeV6ZZX2FgyTn7YXosmTBE8ZiujQgN8Cui5SZjirChSgYfJyjYCDADaDsYH1pbUcpBsKP2Jm8LE1MW591H8DKGYaPprJ4D2P1BhvtSsaTHdxwQAnTHt2zsuT6jxQyDkVxWDqy", "programIdIndex": 8, "stackHeight": 2}, {"accounts": [15, 15, 23], "data": "3JDwL7DuHRdy", "programIdIndex": 25, "stackHeight": 2}, {"accounts": [15, 2, 23], "data": "3amp5dzsRGFy", "programIdIndex": 25, "stackHeight": 2}]}], "loadedAddresses": {"readonly": ["Sysvar1nstructions1111111111111111111111111", "ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY", "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "jitodontfront11111111111JustUseJupiterU1tra", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump"], "writable": ["8943FQrCirbp2kNk8cVKS5P7vjNzhas3L9fDoqpnv8mw", "CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU", "f2FsCiguf172T9achZzJcTjJuM9BLf5nmf18WKaaWUZ", "fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1", "GC2yqyD6ZYnAXc8DNy4d7uiYnQ9TBhZBA4WMPbsMKUxK", "2p29nqD7DN1PczBMmgrFdtYKTfv6rJ7H3yMut4eu7nYT", "5SPztfEn1VAaWDBAXjQKwVrGbr6e8g3F6JJnUc9eCuSe", "4YAgjfFQYjqezqco9y6ZtHN2idDgazFC6ivPLmsMSEQU", "AemYRZmJryzAQ9Z4RLfUBLnPRUY5ecooc94EJvemfti4", "EqmuG7mdMjLfdGxXDEasm3gc16RGhZ3dAgcVfPmkAJSC"]}, "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 112754 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 invoke [2]", "Program log: ray_log: AyIM2xIUAAAAAAAAAAAAAAABAAAAAAAAAA2WUGoUAAAAJ8lResUCAABJbbku8ykAADw6BFIBAAAA", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 91974 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 84860 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 consumed 25831 of 105380 compute units", "Program 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8 success", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY invoke [2]", "Program log: Instruction: swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 66442 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4554 of 60534 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: Q3AAHurUU32oMKxNV5M8megqKXmnG3YtKcEKJ9tudj/5F0kfzsl/ufnQT/ggSLdQ/BT3+/o5a1Dxa89BYqFP/RkXA2L0UEcBfZyrmuHnPr9+QuC/1V2cVtYRScnWsSHRF+vmW3fGN5XioGHT74cJwEbZ9oaJ31u0Nm/LcdOppcK9j//h69RTfaAuMhjLvptLWB32/hF3e9ERYSX54eAxcJmWVvl+0ZYzm8cCt0LXR75HfzZjxcUGQd46hztP/GV4Np15rP2WBjTBIrHI4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Z1jJfnh4DFwGRJI+X7RljObxwK3QtdHvnzoFtnFxQZBn9WhH0/8ZXgqmHms/ZYGNEGmr8jg5z6/5alH/tVdnFbG8SH/82zp7rkRujayONiqbEuKu++HCcBG2faGid9btMmQNI7SqaXCQnAAHurUU32hjdGPy76bSwLhduMRd3vRnWMl+eHgMXAZEkj5ftGWM5vHArdC10e+fOgW2cXFBkGf1aEfT/xleCqYeaz9lgY0QaavyODnPr/lqUf+1V2cVsbxIf/zbOnuuRG6NrI42KpsS4q774cJwEbZ9oaJ31u0yZA0jtKppcJCcAAe6tRTfaGN0Y/LvptLAuF24xF3e9FinNoG4eAxcF4TSPl+0ZYzm8cCt0LXR76s7xbZxcUGQc3wMcbW/WV4xvVDuv2WBjRBpq/I4Oc+v+WpR/7VXZxWxvEh//Ns6e65Ebo2sjjYqmxLirvvhwnARtn2honfW7TJkDSO0qmlwkJwAB7q1FN9oY3Rj8u+m0sC4XbjEXd70Q==", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY consumed 40513 of 76513 compute units", "Program ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 34275 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 32023 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 25587 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 95625 of 116436 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 f26VQQAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "postBalances": [123721736473, 9160838, 2039280, 2039280, 2039280, 22519994331, 1, 1, 2729681025, 8352000, 2786822252190, 52784640, 2079311, 8352000, 995823284, 2039380, 3041515066351, 70421476, 2039281, 0, 1141441, 3596047, 418938902554, 214648494, 1000004, 5289313643, 32335376897, 2817789979, 83262188269], "postTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4991922524", "decimals": 6, "uiAmount": 4991.922524, "uiAmountString": "4991.922524"}}, {"accountIndex": 3, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "0", "decimals": 6, "uiAmount": null, "uiAmountString": "0"}}, {"accountIndex": 4, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1467320811", "decimals": 6, "uiAmount": 1467.320811, "uiAmountString": "1467.320811"}}, {"accountIndex": 10, "mint": "So11111111111111111111111111111111111111112", "owner": "CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2786820106354", "decimals": 9, "uiAmount": 2786.820106354, "uiAmountString": "2786.820106354"}}, {"accountIndex": 12, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "134225154020", "decimals": 6, "uiAmount": 134225.15402, "uiAmountString": "134225.15402"}}, {"accountIndex": 14, "mint": "So11111111111111111111111111111111111111112", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "993782000", "decimals": 9, "uiAmount": 0.993782, "uiAmountString": "0.993782"}}, {"accountIndex": 15, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3073221114", "decimals": 6, "uiAmount": 3073.221114, "uiAmountString": "3073.221114"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3041513017067", "decimals": 9, "uiAmount": 3041.513017067, "uiAmountString": "3041.513017067"}}, {"accountIndex": 18, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "46210653387115", "decimals": 6, "uiAmount": 46210653.387115, "uiAmountString": "46210653.387115"}}], "preBalances": [123721845385, 9160838, 2039280, 2039280, 2039280, 22519973749, 1, 1, 2729681025, 8352000, 2781151276130, 52784640, 2079311, 8352000, 995823284, 2039380, 3047186042411, 70421476, 2039281, 0, 1141441, 3596047, 418938902554, 214648494, 1000004, 5289313643, 32335376897, 2817789979, 83262188269], "preTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3891610333", "decimals": 6, "uiAmount": 3891.610333, "uiAmountString": "3891.610333"}}, {"accountIndex": 3, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "86215691298", "decimals": 6, "uiAmount": 86215.691298, "uiAmountString": "86215.691298"}}, {"accountIndex": 4, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1467320811", "decimals": 6, "uiAmount": 1467.320811, "uiAmountString": "1467.320811"}}, {"accountIndex": 10, "mint": "So11111111111111111111111111111111111111112", "owner": "CvKXXfxq2YzgQ9V7PBfNCzFmRSrj1VX49tjAJqJy68AU", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "2781149130294", "decimals": 9, "uiAmount": 2781.149130294, "uiAmountString": "2781.149130294"}}, {"accountIndex": 12, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "fEe1SXYGDYGY7c7ttEY2Jyffzotx12heiw8xdrctvi1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "135326677887", "decimals": 6, "uiAmount": 135326.677887, "uiAmountString": "135326.677887"}}, {"accountIndex": 14, "mint": "So11111111111111111111111111111111111111112", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "993782000", "decimals": 9, "uiAmount": 0.993782, "uiAmountString": "0.993782"}}, {"accountIndex": 15, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "HFqp6ErWHY6Uzhj8rFyjYuDya2mXUpYEk8VW75K9PSiY", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3072009438", "decimals": 6, "uiAmount": 3072.009438, "uiAmountString": "3072.009438"}}, {"accountIndex": 16, "mint": "So11111111111111111111111111111111111111112", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "3047183993127", "decimals": 9, "uiAmount": 3047.183993127, "uiAmountString": "3047.183993127"}}, {"accountIndex": 18, "mint": "Cy1GS2FqefgaMbi45UunrUzin1rfEmTUYnomddzBpump", "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "46124437695817", "decimals": 6, "uiAmount": 46124437.695817, "uiAmountString": "46124437.695817"}}], "rewards": [], "status": {"Ok": null}}, "transaction": {"message": {"accountKeys": ["gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB", "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "46pxCL7Upm36T5YbA5od3KfY9QVRwY8aWmuzSnzzmUcA", "8ZK9R45iiJhUkXrKxy9dFcuEnvxLfJMdDwKAZM5wZQAR", "dWxMwYfmqkkhCddeorj61EA4bRcwBbRnATX7vepPj2p", "FzESY59j4xCef1EjqoprVBDXEFTWcrx8hGq6AYYvGH1v", "11111111111111111111111111111111", "ComputeBudget111111111111111111111111111111", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"], "addressTableLookups": [{"accountKey": "2iUJxrahG52bPemKUWw8CSceESan6K75M6XwfuRmtjcS", "readonlyIndexes": [42, 44], "writableIndexes": [43, 40, 45, 38, 41]}, {"accountKey": "3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW", "readonlyIndexes": [0, 40, 11, 1, 20], "writableIndexes": [32, 49]}, {"accountKey": "FTZdCrncV1GHwm56C766vJxrHGPUpZB8VBDaoctNTCSv", "readonlyIndexes": [19, 46, 43], "writableIndexes": [153, 155, 156]}], "header": {"numReadonlySignedAccounts": 1, "numReadonlyUnsignedAccounts": 3, "numRequiredSignatures": 2}, "instructions": [{"accounts": [], "data": "E7DqgB", "programIdIndex": 7, "stackHeight": 1}, {"accounts": [], "data": "3GquDG1FqyTV", "programIdIndex": 7, "stackHeight": 1}, {"accounts": [23, 1, 3, 4, 15, 2, 28, 22, 25, 25, 21, 8, 15, 27, 25, 17, 26, 16, 18, 4, 14, 23, 20, 11, 9, 10, 13, 12, 14, 15, 23, 25, 19, 24], "data": "6BngFxsVPaKrU5Q1biopYgsGgBee1bGciouzeHXAousyEox3Gsbr14abmyKji1", "programIdIndex": 8, "stackHeight": 1}, {"accounts": [0, 5], "data": "3Bxs4HyDhLXVdjQ3", "programIdIndex": 6, "stackHeight": 1}], "recentBlockhash": "5NK3LC7HExR55yjW1ABktqKHM6buRQBPdTAMzMPokChU"}, "signatures": ["3v9GsuiHTeGmJNJbRNzJGj9ZQ5RhGGgKwZrvvZZvYy7KKhiaRbUqLa3okH8TtumqY4ZU74E2FcWgJExjYFTEJpyC", "3zZYtaTYpAyu8RL3dC9rEgcqvdUzydjWd67MBEQWAvJ7xz6y4i1JfHyBBLojLoEjfag174Fzbim46dyngfZduHeD"]}, "parsed_tx": {"dex": "unknown", "action": "unknown", "mint": null, "amount": null, "signature": null, "source_wallet": null, "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "unknown", "confidence": 0}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### live_test_III.py

**Issues:** 1

- **Line 51** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-12 18:55:40,201 - __main__ - DEBUG - [DEBUG] Received trade_info: {"signature": "3gLH2B4rDTgq8qMjSKh61h9AtbZn36abXHS2UktaTZS1eggAFGA73RNEXPmCPXSw8dbSVu4coKQQ7JCnNpyskQCv", "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 186300 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb consumed 3096 of 180951 compute units", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 175024 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 42791 of 210584 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 130802 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123009 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZSwbiOzRqOUKdaF59hqnk/X414MJlQxyEvWyJLEbfQ/gFjXcUkmcITMAAAAAAAAAAAslkPrT+AEzAAAAAAAAAAAKC7aL0AAAAA63KtBgAAAAAAAAAAAAAAAAAAAAAAAAAAxd8QAAAAAAB7hQIAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 49650 of 164497 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 72455 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 64753 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZPyvg2fhqvmAEvwpTa+l2JaZFOoQ0YSwIzBjan3NHI9gExzQIUVRHsWAIAAAAAAAAAgNIlFrR/6VgCAAAAAAAAAOtyrQYAAAAAyyDJJAAAAAAAAAAAAAAAAAAAAAAAAAAAJ0wAAAAAAABgCwAAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 54962 of 111553 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 54816 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 52564 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 46128 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 177486 of 218838 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 78S+JAAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "timestamp": "2025-10-12 17:55:40.200530+00:00", "detection_method": "websocket_logs", "meta": {"computeUnitsConsumed": 177936, "costUnits": 187276, "err": null, "fee": 111825, "innerInstructions": [{"index": 2, "instructions": [{"accounts": [29, 16, 30, 27, 6, 25, 43, 39, 28, 44, 1, 41, 40, 33, 42, 44, 11, 10, 14], "data": "fx9RHbGFfZ9dVZGcnvi17XZDninrTwuEUzcXf5", "programIdIndex": 44, "stackHeight": 2}, {"accounts": [42], "data": "yCGxBopjnVNQkNP5usq1PoiCnL8LHyZvPRm5uDStNq7g14uayjoyheSQ3MpKeUUpNFZx9PnsczEYwyiNa2tyNF9CX5HF87hDhUX7TMqwGGhSxDv3N97NVvH74aHCeGS8K4QAQMXayoGkCNnQKKVrZS2Xi8fB23zj7aFcYiQ9rvFcgnmaE4VmC3bwzpEQWt5zUpeqwm", "programIdIndex": 44, "stackHeight": 3}, {"accounts": [6, 43, 30, 1], "data": "iQhWu1CGDz2vU", "programIdIndex": 41, "stackHeight": 3}, {"accounts": [27, 39, 25, 29], "data": "i9cPwL1rydo6p", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [40, 37, 19, 25, 21, 3, 20, 7, 12, 5, 31], "data": "59p8WydnSZtVSnejym9vy2cReqgJNDdtMYbk7foEm62n7WxHXASY3oMrf2", "programIdIndex": 34, "stackHeight": 2}, {"accounts": [25, 21, 37], "data": "3gLs8vwRjgqM", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [20, 3, 19], "data": "3tqhiuBKVS23", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [40, 37, 23, 3, 22, 26, 24, 8, 4, 13, 32], "data": "59p8WydnSZtX8kdsj2YYZMLAPjdABpZWQ1WSUK4e5K4gQcykKV8CSTdUTr", "programIdIndex": 34, "stackHeight": 2}, {"accounts": [3, 22, 37], "data": "3tqhiuBKVS23", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [24, 26, 23], "data": "3oSAD44x5Vwd", "programIdIndex": 40, "stackHeight": 3}, {"accounts": [35], "data": "2C3FxF4wtCk1WPKYcjNvfKxBQp63XuDdX4hcikNH3TZECZZDX6cg4mZDsLxWxh5BKovt6F8pDNn3gYQPSpYfUxAQo6Q4EqXcYAkGiZF7W3kiqgcSyUpUnuRjbgHbLaVEXDvuKRkooqYkduEZui8Wv5ZdYG8uNkmihegVq42vQzX13tbTz9k1LWynm2VaLjJPYE9ZFMsqxrJ5bUyiC6QhCkJy8inVrufcTQh1DbSGFQ7goHG7DPp6A1RSC3AFZ9BSdSGUXm1RSdwzXEwv1FmLwY2yrVkifhjSqqa7sdBMna22sEmyftuQW9CTPM5zRgVPY9wJj56Z3Vd9exRb3e4vKkEBhySiiH5iKcjq", "programIdIndex": 18, "stackHeight": 2}, {"accounts": [26, 26, 37], "data": "3rKHgTZRH5Zq", "programIdIndex": 40, "stackHeight": 2}, {"accounts": [26, 2, 37], "data": "3uZcntACUGvT", "programIdIndex": 40, "stackHeight": 2}]}], "loadedAddresses": {"readonly": ["4zKPdJqfhFW9FRPbUd3iuZmX4jHi2Lwsqbvh86B5AYEK", "8HchJS2ufNvZv6i3Q6zRLvBDpVe1P72ArR86p2hUHvg6", "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr", "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc", "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "jitodontfront11111111111JustUseJupiterU1tra", "So11111111111111111111111111111111111111112", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "D1ZN9Wj1fRSUQfCjhvnu1hqDMT7hzjzBBpi12nVniYD6", "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"], "writable": ["6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "EQCDoN8WHzYxCRmhxHBSEYCL5muMaZ2HHWbY121fEYsu", "Gg5msGGYPXGt9JpAC5oVdimjWZEXzKpunRDALaJ1Ny1U", "2KiAy13bDCMGfJ8MqbpTC7g3CunHjLQYMs3wK14XM5LZ", "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "GoJSsR8AwPWCbbbFfwVtT97vTEdKs3kwGkahgvhiybMU", "GyY4VgEpJQhiKZRAJJmoM4hv5Q2xC4pvX68MGrGidxyG", "HoBCz6z9AG92GGozMWEkBPE9UhQWGZ5cXhYcjoGJvwP2", "6qxaasNgXsfVp8tKkoJavp29hZYiDrcEirsS3oAsYCLc", "AFH1UXkECQwYoWkkCSydxU8UGciH8jxqB9EebV1NJVHs", "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "DfWWLJvVHDM9byp6y7Rpw5Rx4mGizSwB5GEoUMegi3z8"]}, "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]", "Program log: Instruction: SharedAccountsRouteV2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [2]", "Program log: Instruction: Swap2", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo invoke [3]", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 2203 of 186300 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb consumed 3096 of 180951 compute units", "Program TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 175024 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo consumed 42791 of 210584 compute units", "Program LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 130802 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 123009 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZSwbiOzRqOUKdaF59hqnk/X414MJlQxyEvWyJLEbfQ/gFjXcUkmcITMAAAAAAAAAAAslkPrT+AEzAAAAAAAAAAAKC7aL0AAAAA63KtBgAAAAAAAAAAAAAAAAAAAAAAAAAAxd8QAAAAAAB7hQIAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 49650 of 164497 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc invoke [2]", "Program log: Instruction: Swap", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 72455 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 64753 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program data: 4cpJr5MroJZPyvg2fhqvmAEvwpTa+l2JaZFOoQ0YSwIzBjan3NHI9gExzQIUVRHsWAIAAAAAAAAAgNIlFrR/6VgCAAAAAAAAAOtyrQYAAAAAyyDJJAAAAAAAAAAAAAAAAAAAAAAAAAAAJ0wAAAAAAABgCwAAAAAAAA==", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc consumed 54962 of 111553 compute units", "Program whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [2]", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 199 of 54816 compute units", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4375 of 52564 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: Transfer", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 46128 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 consumed 177486 of 218838 compute units", "Program return: JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 78S+JAAAAAA=", "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success"], "postBalances": [123712265076, 9160839, 2039280, 2039280, 70407360, 70407360, 2157600, 70407360, 70407360, 22712666216, 71437440, 71437441, 70407360, 70407360, 71437440, 1, 11859840, 1, 2729681025, 10175860, 2039282, 11674462861006, 2039285, 5444104, 2039284, 1492977215, 2039280, 4301610167098, 23385600, 7183729, 2129760, 0, 0, 521498895, 1161445, 3596047, 418938902554, 122611498, 1000004, 1171250707549, 5289313643, 1151489, 4000419, 1805481849230, 32941452], "postTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "5608404555", "decimals": 6, "uiAmount": 5608.404555, "uiAmountString": "5608.404555"}}, {"accountIndex": 3, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1998298", "decimals": 6, "uiAmount": 1.998298, "uiAmountString": "1.998298"}}, {"accountIndex": 6, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "0", "decimals": 9, "uiAmount": null, "uiAmountString": "0"}}, {"accountIndex": 20, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "225575433987", "decimals": 6, "uiAmount": 225575.433987, "uiAmountString": "225575.433987"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "11674460368718", "decimals": 9, "uiAmount": 11674.460368718, "uiAmountString": "11674.460368718"}}, {"accountIndex": 22, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "514139470456", "decimals": 6, "uiAmount": 514139.470456, "uiAmountString": "514139.470456"}}, {"accountIndex": 24, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1592142888516", "decimals": 6, "uiAmount": 1592142.888516, "uiAmountString": "1592142.888516"}}, {"accountIndex": 25, "mint": "So11111111111111111111111111111111111111112", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1490936932", "decimals": 9, "uiAmount": 1.490936932, "uiAmountString": "1.490936932"}}, {"accountIndex": 26, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1560224830", "decimals": 6, "uiAmount": 1560.22483, "uiAmountString": "1560.22483"}}, {"accountIndex": 27, "mint": "So11111111111111111111111111111111111111112", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4301608127814", "decimals": 9, "uiAmount": 4301.608127814, "uiAmountString": "4301.608127814"}}, {"accountIndex": 30, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "5971184163803041", "decimals": 9, "uiAmount": 5971184.163803041, "uiAmountString": "5971184.163803041"}}], "preBalances": [123712403357, 9160839, 2039280, 2039280, 70407360, 70407360, 2157600, 70407360, 70407360, 22712639760, 71437440, 71437441, 70407360, 70407360, 71437440, 1, 11859840, 1, 2729681025, 10175860, 2039282, 11671285103406, 2039285, 5444104, 2039284, 1492977215, 2039280, 4304787924698, 23385600, 7183729, 2129760, 0, 0, 521498895, 1161445, 3596047, 418938902554, 122611498, 1000004, 1171250707549, 5289313643, 1151489, 4000419, 1805481849230, 32941452], "preTokenBalances": [{"accountIndex": 2, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4991922524", "decimals": 6, "uiAmount": 4991.922524, "uiAmountString": "4991.922524"}}, {"accountIndex": 3, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1998298", "decimals": 6, "uiAmount": 1.998298, "uiAmountString": "1.998298"}}, {"accountIndex": 6, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "6480659491765", "decimals": 9, "uiAmount": 6480.659491765, "uiAmountString": "6480.659491765"}}, {"accountIndex": 20, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "225687464430", "decimals": 6, "uiAmount": 225687.46443, "uiAmountString": "225687.46443"}}, {"accountIndex": 21, "mint": "So11111111111111111111111111111111111111112", "owner": "6a3m2EgFFKfsFuQtP4LJJXPcAe3TQYXNyHUjjZpUxYgd", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "11671282611118", "decimals": 9, "uiAmount": 11671.282611118, "uiAmountString": "11671.282611118"}}, {"accountIndex": 22, "mint": "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "514027440013", "decimals": 6, "uiAmount": 514027.440013, "uiAmountString": "514027.440013"}}, {"accountIndex": 24, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "6NUiVmsNjsi4AfsMsEiaezsaV9N4N1ZrD4jEnuWNRvyb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1592760049423", "decimals": 6, "uiAmount": 1592760.049423, "uiAmountString": "1592760.049423"}}, {"accountIndex": 25, "mint": "So11111111111111111111111111111111111111112", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1490936932", "decimals": 9, "uiAmount": 1.490936932, "uiAmountString": "1.490936932"}}, {"accountIndex": 26, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "owner": "GP8StUXNYSZjPikyRsvkTbvRV1GBxMErb59cpeCJnDf1", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "1559545954", "decimals": 6, "uiAmount": 1559.545954, "uiAmountString": "1559.545954"}}, {"accountIndex": 27, "mint": "So11111111111111111111111111111111111111112", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4304785885414", "decimals": 9, "uiAmount": 4304.785885414, "uiAmountString": "4304.785885414"}}, {"accountIndex": 30, "mint": "Ey59PH7Z4BFU4HjyKnyMdWt5GGN76KazTAwQihoUXRnk", "owner": "AjM8Qn62EhR4ikJ1rvyeezB1NyvrSsb4zwJiFUFs9ycs", "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "uiTokenAmount": {"amount": "5964703524311276", "decimals": 9, "uiAmount": 5964703.524311276, "uiAmountString": "5964703.524311276"}}], "rewards": [], "status": {"Ok": null}}, "transaction": {"message": {"accountKeys": ["gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB", "7buZeCKVFiNhRBFgm6Dz7Vpe74p9UF63vorv3fhA6Qct", "46pxCL7Upm36T5YbA5od3KfY9QVRwY8aWmuzSnzzmUcA", "5cwXmKE4Hfo1pwNmaqNN3G2sFxaPmh99KzzKqxxpUGtc", "5tfDjs6dMBDJCvy8KzBQc9wHNRQBv7Ld55V8P42qjbxS", "5vYhTkbZ1eHVT2gtWpcqNfJtrH93GozY7cp77mv4FEQ1", "7jPcYwKiZCqL8AejDj3fWX2HSsXMPtk8ynb9gaaT92Uk", "7qsvwKqCxTYqzmGnZ7wiFfF9JAuT9ZSkqbesjKKoBorB", "84HBfGQM6s66jvtHADW3yRZboDnSvgB4vepaiLhpfike", "9fBpwxcudpLyJskhiiKmU8wPszeUuCB8sSjhPi44QuFb", "9KLsBy8WLiRQXiaKvQfP2QpUKmKogkkXAnp3R2js1LnG", "Ej5MvFYhUzUXYK6GUhtHG8Kza3r4PBJkMn5WnkULnQiE", "EKybzWj9NGuMcNUMc5U3c8YZ2bVJm1VXfdczxHCvDsXC", "FgEvXp2vtH3rFfV2U6YmN1T2QeeySzTgig8ZaXaVAofc", "GGe31JNjegWrBFAxN3rJr8N4dCGP7mA7iDY19uRPmSu7", "11111111111111111111111111111111", "7X4pHkWzDWEFwrKiZ4TzuxubQDNFdimjuiJyUk3rYhwb", "ComputeBudget111111111111111111111111111111", "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"], "addressTableLookups": [{"accountKey": "3GHqLHQa6e2tJ8boEy7WGUi69ngyGGiGiqgbbYNyGLX7", "readonlyIndexes": [223], "writableIndexes": [229, 225, 231]}, {"accountKey": "3ko8XWJLLPTmsC7pJbrENEVbfrM2x4Ps4Peu8STgphfx", "readonlyIndexes": [152, 10, 3], "writableIndexes": [142, 153, 146]}, {"accountKey": "3oy9ojnsDzqmMNi87Gs7Hn5v3MPVqnWjG9k8BmzKR7yW", "readonlyIndexes": [0, 40, 17, 1, 23, 20, 21], "writableIndexes": [38, 55]}, {"accountKey": "AZ3jABe1GEVW5XKdiYQheEZBMFULiQYEkpGNqh5Vsrs", "readonlyIndexes": [62, 154, 61], "writableIndexes": [157, 146, 148, 149]}], "header": {"numReadonlySignedAccounts": 1, "numReadonlyUnsignedAccounts": 4, "numRequiredSignatures": 2}, "instructions": [{"accounts": [], "data": "E9YCTR", "programIdIndex": 17, "stackHeight": 1}, {"accounts": [], "data": "3GpTfWHWDg3Z", "programIdIndex": 17, "stackHeight": 1}, {"accounts": [37, 1, 6, 6, 26, 2, 43, 36, 41, 40, 35, 18, 26, 44, 29, 16, 30, 27, 6, 25, 43, 39, 28, 44, 1, 41, 40, 33, 42, 44, 11, 10, 14, 18, 34, 40, 37, 19, 25, 21, 3, 20, 7, 12, 5, 31, 34, 40, 37, 23, 3, 22, 26, 24, 8, 4, 13, 32, 38], "data": "6gDU5q1ft98C3rMZmqq6QvefXmdfhjq6PY5wpqsfdCqoioSKqfWHVodb9nDJTAqJdSdJcZjvehvnn", "programIdIndex": 18, "stackHeight": 1}, {"accounts": [0, 9], "data": "3Bxs4FeGqCF4jJBR", "programIdIndex": 15, "stackHeight": 1}], "recentBlockhash": "F17TfDAPYLBt3AHGCuxeyKb6aT31ucSPFvWchZTVPBCQ"}, "signatures": ["3gLH2B4rDTgq8qMjSKh61h9AtbZn36abXHS2UktaTZS1eggAFGA73RNEXPmCPXSw8dbSVu4coKQQ7JCnNpyskQCv", "5bFzC9knoCKJxydoNjKt7m4kPruHE3pm8YoTJnfd6qQ3xL9h6oKwP54WfQUNFDdtewmktPGw3hMbXsioqhzDsLmy"]}, "parsed_tx": {"dex": "unknown", "action": "unknown", "mint": null, "amount": null, "signature": null, "source_wallet": null, "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "unknown", "confidence": 0}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### log.py

**Issues:** 1

- **Line 139** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `2025-10-20 21:04:34,661 - __main__ - DEBUG - [DEBUG] Before infer_missing_fields: {"detection_method": "websocket_account_change", "timestamp": "2025-10-20 20:04:34.140822+00:00", "requires_full_analysis": true, "signature": "ndhfRpYBMeaUdcF4S1GD8iASnDSBiqQMUUkMBWgYQKJhf5Pz8Xd5mBvrTaJW3bfCJHvtvGLRsHqUHp4sq8Ufi6g", "logs": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success"], "transaction": {"message": {"accountKeys": [{"pubkey": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "signer": true, "source": "transaction", "writable": true}, {"pubkey": "5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW", "signer": true, "source": "transaction", "writable": true}, {"pubkey": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "signer": true, "source": "transaction", "writable": false}, {"pubkey": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "FY3t5nGT4xgK1XMPAik2uipSZrwUpxmTdhivTdFTWD4Y", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "3BUzjXnM7a7Ju1kGekv9zJfeXCuYdKJMRDZ7cwxWTw49", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "signer": false, "source": "transaction", "writable": true}, {"pubkey": "ComputeBudget111111111111111111111111111111", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "So11111111111111111111111111111111111111112", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "11111111111111111111111111111111", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "9dkYPFpVTA9tBSmkAkdRoMmnoB3WPBG9UYfUPFfhvFJj", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF", "signer": false, "source": "transaction", "writable": false}, {"pubkey": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "signer": false, "source": "transaction", "writable": false}], "addressTableLookups": [], "instructions": [{"accounts": [], "data": "HAWR3M", "programId": "ComputeBudget111111111111111111111111111111", "stackHeight": 1}, {"accounts": [], "data": "3atJtxCCtbsV", "programId": "ComputeBudget111111111111111111111111111111", "stackHeight": 1}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "mint": "So11111111111111111111111111111111111111112", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "createIdempotent"}, "program": "spl-associated-token-account", "programId": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "stackHeight": 1}, {"parsed": {"info": {"account": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "create"}, "program": "spl-associated-token-account", "programId": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", "stackHeight": 1}, {"parsed": {"info": {"destination": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "lamports": 940000000, "source": "5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW"}, "type": "transfer"}, "program": "system", "programId": "11111111111111111111111111111111", "stackHeight": 1}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk"}, "type": "syncNative"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 1}, {"accounts": ["FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "9dkYPFpVTA9tBSmkAkdRoMmnoB3WPBG9UYfUPFfhvFJj", "FY3t5nGT4xgK1XMPAik2uipSZrwUpxmTdhivTdFTWD4Y", "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "3BUzjXnM7a7Ju1kGekv9zJfeXCuYdKJMRDZ7cwxWTw49", "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "So11111111111111111111111111111111111111112", "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF", "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"], "data": "TGq5We4Uqkt8c4w8B5kdTTEdKKtT3on6hN", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "stackHeight": 1}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "destination": "5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "closeAccount"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 1}], "recentBlockhash": "D5rK86h2ejRCSBeZvkKwwJaJpHVASFrUBHaGxj2GGJ8f"}, "signatures": ["ndhfRpYBMeaUdcF4S1GD8iASnDSBiqQMUUkMBWgYQKJhf5Pz8Xd5mBvrTaJW3bfCJHvtvGLRsHqUHp4sq8Ufi6g", "47WyeWpBW2sVWniBeQVmsvbpSxnmrkUSFMxNyknkp76u5noJpDabjDFoFUYTnGJgjU4xmhFQvcQs2cdUWHcREwaD", "61sRNdvPjPNezo39daywXVrLZi8aaKQx12F2nYY5pthFmyoGqBD1BkNhHskgrFB9XeYSNaeZEMGgsEnwYjMwQRn4"]}, "meta": {"computeUnitsConsumed": 122222, "costUnits": 126559, "err": null, "fee": 77000, "innerInstructions": [{"index": 2, "instructions": [{"parsed": {"info": {"extensionTypes": ["immutableOwner"], "mint": "So11111111111111111111111111111111111111112"}, "type": "getAccountDataSize"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"lamports": 2039280, "newAccount": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "space": 165}, "type": "createAccount"}, "program": "system", "programId": "11111111111111111111111111111111", "stackHeight": 2}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk"}, "type": "initializeImmutableOwner"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"account": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "mint": "So11111111111111111111111111111111111111112", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "initializeAccount3"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}]}, {"index": 3, "instructions": [{"parsed": {"info": {"extensionTypes": ["immutableOwner"], "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c"}, "type": "getAccountDataSize"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"lamports": 2039280, "newAccount": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "source": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "space": 165}, "type": "createAccount"}, "program": "system", "programId": "11111111111111111111111111111111", "stackHeight": 2}, {"parsed": {"info": {"account": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k"}, "type": "initializeImmutableOwner"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"account": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv"}, "type": "initializeAccount3"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}]}, {"index": 6, "instructions": [{"parsed": {"info": {"authority": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "destination": "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "mint": "So11111111111111111111111111111111111111112", "source": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "tokenAmount": {"amount": "940000000", "decimals": 9, "uiAmount": 0.94, "uiAmountString": "0.94"}}, "type": "transferChecked"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"authority": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "destination": "B8TXpmDAPxT1P2fhYxEL3PT6Bs6z1sG6Fexk8LFrKz6k", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "source": "3BUzjXnM7a7Ju1kGekv9zJfeXCuYdKJMRDZ7cwxWTw49", "tokenAmount": {"amount": "4223021417000", "decimals": 6, "uiAmount": 4223021.417, "uiAmountString": "4223021.417"}}, "type": "transferChecked"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"parsed": {"info": {"authority": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "destination": "DNRSwUqG21yteKXvxTxViq9mTwiKajfRgQig1VFuWNLk", "mint": "So11111111111111111111111111111111111111112", "source": "B4MWJwqGLDjpFRGt3VYxHe2rR7zBndcYCRkz5WpmMZwR", "tokenAmount": {"amount": "10093", "decimals": 9, "uiAmount": 1.0093e-05, "uiAmountString": "0.000010093"}}, "type": "transferChecked"}, "program": "spl-token", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "stackHeight": 2}, {"accounts": ["8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF"], "data": "2ioXo9nkAt26bphRv6PYrqXu1WqZas5QXLCJAHm29gH8gmiPimCsd4v3qQEiPFtPXTfAY2Zhx1kqTtaLZWjdw1zaFftu7xg5whxTgbfcUgwzXhQz5m8pbYcjx4xaDRNhYeYPxzvi5ffg1ZSySas1DJNHj7TjNLXCmiEnacu92rmywVYKto6oEUNxYEgX6yAeqj7yPqHAVTGHH2Ag5tbPCeTZp9ZWssUzeiV4r5h2P", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "stackHeight": 2}, {"accounts": ["8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF"], "data": "44FY2SKwMbUFWgV1yoKm6d53JBJqdzq9UBVTHSyQn8CJHezoTCqcrXDubvZntJdC73qAmoAyhGikAnLG3uHJoNxTbwyyRJLu9iaSB1y7AVs8JvE1JQD8MiKd2X78pbBdZuNCp35u9uZmtGzDQkRbcocraihGTdiQhvoQnuSk3eBE3Cg8izhB5ZhUNGussdAm9pmQg34WvnMoGn6awXQemdEPzWQnb3tYwZV4KJk3BVCV4n3ik5XDUVCj6H1xrsW4p5izvS37CP9", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "stackHeight": 2}]}], "logMessages": ["Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ComputeBudget111111111111111111111111111111 invoke [1]", "Program ComputeBudget111111111111111111111111111111 success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: CreateIdempotent", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 147718 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 141131 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3158 of 137248 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 20914 of 154700 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]", "Program log: Create", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: GetAccountDataSize", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1569 of 114842 compute units", "Program return: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA pQAAAAAAAAA=", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program 11111111111111111111111111111111 invoke [2]", "Program 11111111111111111111111111111111 success", "Program log: Initialize the associated token account", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeImmutableOwner", "Program log: Please upgrade to SPL Token 2022 for immutable owner support", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1405 of 108255 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: InitializeAccount3", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4188 of 104372 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL consumed 33906 of 133786 compute units", "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL success", "Program 11111111111111111111111111111111 invoke [1]", "Program 11111111111111111111111111111111 success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: SyncNative", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3045 of 99730 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]", "Program log: Instruction: Swap2", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 73672 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6147 of 64964 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]", "Program log: Instruction: TransferChecked", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6238 of 56354 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 46968 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [2]", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 3577 of 40086 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN consumed 60894 of 96685 compute units", "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN success", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]", "Program log: Instruction: CloseAccount", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 3013 of 35791 compute units", "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success"], "postBalances": [2410783040, 17000071918, 0, 0, 2039280, 3841920, 2039280, 96274935166, 1, 789146954, 1176160029876, 1, 5299607121, 1461600, 1151512, 1602282239974, 8184960, 1000055, 1187659450], "postTokenBalances": [{"accountIndex": 4, "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "7JTTvfadgR32FR72FhNLMz1DwKinQkJGa3M3Hd5RF6nv", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "4223021417000", "decimals": 6, "uiAmount": 4223021.417, "uiAmountString": "4223021.417"}}, {"accountIndex": 6, "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "519274406509051", "decimals": 6, "uiAmount": 519274406.509051, "uiAmountString": "519274406.509051"}}, {"accountIndex": 7, "mint": "So11111111111111111111111111111111111111112", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "96272895886", "decimals": 9, "uiAmount": 96.272895886, "uiAmountString": "96.272895886"}}], "preBalances": [2414938600, 17938022545, 0, 0, 0, 3841920, 2039280, 95334945259, 1, 789146954, 1176160029876, 1, 5299607121, 1461600, 1151512, 1602282239974, 8184960, 1000055, 1187659450], "preTokenBalances": [{"accountIndex": 6, "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "523497427926051", "decimals": 6, "uiAmount": 523497427.926051, "uiAmountString": "523497427.926051"}}, {"accountIndex": 7, "mint": "So11111111111111111111111111111111111111112", "owner": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "uiTokenAmount": {"amount": "95332905979", "decimals": 9, "uiAmount": 95.332905979, "uiAmountString": "95.332905979"}}], "rewards": [], "status": {"Ok": null}}, "parsed_tx": {"dex": "meteora", "action": "swap", "mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "amount": null, "signature": "ndhfRpYBMeaUdcF4S1GD8iASnDSBiqQMUUkMBWgYQKJhf5Pz8Xd5mBvrTaJW3bfCJHvtvGLRsHqUHp4sq8Ufi6g", "wallet_address": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "original_result": {"dex": "Unknown", "parsed": false, "unknown_info": {"user_wallet": null, "action": "possible_trade", "confidence": 0.3}, "detected_action": "unknown", "action_confidence": 0, "instruction_actions": [], "instruction_details": [], "has_trade_instructions": false}}, "dex": "meteora", "action": "buy", "token_mint": "GmhuSKmueUZJJbPCkkmgD8CPw4QY94BQPm2nLXy1X76c", "wallet_address": "Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj", "confidence": "MEDIUM", "dex_type": "unknown", "trade_type": "buy", "analysis_method": "full_analyzer_with_dex_detection", "programs_used": [], "router_program_id": null, "account_metas": [], "instruction_data": null}`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### main_backup_complex.py

**Issues:** 3

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 26** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 31** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts  # Added for direct RPC execution options`
  - Fix: Replace with solders equivalent: from solders.* import ...

### main_backup_corrupted.py

**Issues:** 7

- **Line 33** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 40** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1150** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3044** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3045** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3575** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TokenAccountOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 4201** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### main_corrupted_backup.py

**Issues:** 7

- **Line 33** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 40** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1150** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3044** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3045** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3575** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TokenAccountOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 4201** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### main_modular.py

**Issues:** 2

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### main_monolithic_backup.py

**Issues:** 7

- **Line 33** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 40** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1152** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3046** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3047** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 3577** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TokenAccountOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 4203** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### manual_trade_all_methods.py

**Issues:** 3

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 31** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 32** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### meteora_copy_executor.py

**Issues:** 5

- **Line 553** 🔴 [NONE_RETURN] Function 'build_and_submit_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 564** 🔴 [NONE_RETURN] Function 'build_and_submit_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 575** 🔴 [NONE_RETURN] Function 'build_and_submit_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 586** 🔴 [NONE_RETURN] Function 'build_and_submit_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 592** 🔴 [NONE_RETURN] Function 'build_and_submit_sell' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### mev_meteora_executor.py

**Issues:** 2

- **Line 95** 🟡 [SCAFFOLD_EXECUTOR] Scaffold/nonfunctional executor not gated behind config flag
  - Code: `class RPCConfig:`
  - Fix: Add config gating: if not os.getenv('ENABLE_SCAFFOLD_EXECUTORS'): return BuildResult(ok=False, reason='Executor disabled')

- **Line 1533** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `alt_lookups = msg.get("addressTableLookups", [])`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### mev_pumpfun_executor.py

**Issues:** 2

- **Line 290** 🔴 [NONE_RETURN] Function 'execute_sell_all' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 300** 🔴 [NONE_RETURN] Function 'execute_sell_all' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### mev_raydium_executor.py

**Issues:** 1

- **Line 60** 🟡 [SCAFFOLD_EXECUTOR] Scaffold/nonfunctional executor not gated behind config flag
  - Code: `class MEVRaydiumExecutor:`
  - Fix: Add config gating: if not os.getenv('ENABLE_SCAFFOLD_EXECUTORS'): return BuildResult(ok=False, reason='Executor disabled')

### mev_router_account_resolver.py

**Issues:** 3

- **Line 42** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `lookups = getattr(msg, 'address_table_lookups', [])`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.publickey import PublicKey`
  - Fix: Replace with solders equivalent: from solders.* import ...

### official_executor_wrappers.py

**Issues:** 4

- **Line 6** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient as SolanaRpcClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1062** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1238** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1293** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### official_wallet_perspective_analyzer.py

**Issues:** 2

- **Line 19** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### orca_copy_executor.py

**Issues:** 5

- **Line 59** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 66** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 67** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Finalized, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 527** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 528** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### orca_manual_trader.py

**Issues:** 4

- **Line 183** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 31** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### phoenix_copy_executor.py

**Issues:** 5

- **Line 37** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 44** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 45** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Finalized, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 463** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 464** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### phoenix_manual_trader.py

**Issues:** 4

- **Line 180** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(tx)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 29** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 30** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pool_discovery_service.py

**Issues:** 2

- **Line 11** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### position_diagnostic.py

**Issues:** 3

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 19** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Finalized`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 41** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TokenAccountOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pump_router_executor.py

**Issues:** 3

- **Line 204** 🔴 [NONE_RETURN] Function 'execute_router_buy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 208** 🔴 [NONE_RETURN] Function 'execute_router_buy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 267** 🔴 [NONE_RETURN] Function 'execute_router_buy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### pumpfun_CC_copy_executor_OLD_BACKUP.py

**Issues:** 2

- **Line 1853** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1854** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pumpfun_copy_executor_old.py

**Issues:** 13

- **Line 190** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(tx, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 369** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 650** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 963** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 45** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 46** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 47** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 182** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 183** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1026** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1027** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1199** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 1200** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pumpfun_executor.py

**Issues:** 6

- **Line 129** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 371** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 533** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 32** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 33** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 34** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pumpfun_manual_trader.py

**Issues:** 2

- **Line 270** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 271** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.transaction import Transaction`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pumpfun_token_validator.py

**Issues:** 1

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### pumpfun_trade_executor.py

**Issues:** 5

- **Line 159** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 427** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 19** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed, Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### raydium_clmm_copy_executor.py

**Issues:** 1

- **Line 407** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

### raydium_clmm_trade_executor.py

**Issues:** 4

- **Line 156** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await self.client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 26** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 27** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 28** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### raydium_copy_executor.py

**Issues:** 6

- **Line 888** 🔴 [NONE_RETURN] Function 'try_raydium_buy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 891** 🔴 [NONE_RETURN] Function 'try_raydium_buy' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 79** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 80** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 185** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 186** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### raydium_official_structure.py

**Issues:** 3

- **Line 86** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `result = await client.send_transaction(tx, opts=TxOpts(skip_preflight=True))`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 19** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 20** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### raydium_trade_executor.py

**Issues:** 9

- **Line 275** 🔴 [NONE_RETURN] Function 'execute_buy_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 378** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 398** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 453** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 465** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 469** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 517** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 556** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

- **Line 560** 🔴 [NONE_RETURN] Function 'execute_sell_trade' declares BuildResult return type but returns None
  - Code: `return None`
  - Fix: Return BuildResult(ok=False, tx=None, reason='...') instead of None

### raydium_v4_amm_trader.py

**Issues:** 4

- **Line 392** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 23** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 24** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### real_clmm_executor.py

**Issues:** 1

- **Line 165** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = await self.client.send_transaction(transaction)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

### run_execution_smoke_test.py

**Issues:** 1

- **Line 27** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### send_mev_router_example.py

**Issues:** 5

- **Line 52** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `response = client.send_transaction(transaction, sender)`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 4** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 5** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.transaction import Transaction, TransactionInstruction, AccountMeta`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 6** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.publickey import PublicKey`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.keypair import Keypair`
  - Fix: Replace with solders equivalent: from solders.* import ...

### simple_bot.py

**Issues:** 1

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### simple_dex_test.py

**Issues:** 1

- **Line 22** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### simple_main.py

**Issues:** 1

- **Line 17** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### simple_test.py

**Issues:** 1

- **Line 25** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### simplified_official_websocket.py

**Issues:** 1

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### simulate_clone.py

**Issues:** 1

- **Line 170** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `if hasattr(msg, 'address_table_lookups') and msg.address_table_lookups:`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### speed_optimizer.py

**Issues:** 1

- **Line 152** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### temp_clean.py

**Issues:** 2

- **Line 141** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `# Handle addressTableLookups for versioned transactions`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_aggressive_fallback.py

**Issues:** 1

- **Line 11** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_aggressive_logs_fallback.py

**Issues:** 1

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_alt_integration.py

**Issues:** 1

- **Line 43** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `"addressTableLookups": [`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### test_alt_reconstruction.py

**Issues:** 1

- **Line 106** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `# Check for addressTableLookups detection`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### test_ata_creation.py

**Issues:** 1

- **Line 5** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_ata_utilities.py

**Issues:** 2

- **Line 96** 🟡 [ATA_EXISTS_USAGE] Call to ensure_ata function passes 'exists' boolean instead of querying RPC
  - Code: `instructions_exists = ensure_ata_for(owner, mint, payer, exists=True)`
  - Fix: Remove 'exists' parameter and let the function query RPC directly

- **Line 103** 🟡 [ATA_EXISTS_USAGE] Call to ensure_ata function passes 'exists' boolean instead of querying RPC
  - Code: `instructions_not_exists = ensure_ata_for(owner, mint, payer, exists=False)`
  - Fix: Remove 'exists' parameter and let the function query RPC directly

### test_balance_fix.py

**Issues:** 3

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 11** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TokenAccountOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_build_and_sign_integration_v2.py

**Issues:** 1

- **Line 33** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `"addressTableLookups": []`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### test_dex_detection.py

**Issues:** 1

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_execution_readiness.py

**Issues:** 1

- **Line 39** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_finalized_commitment.py

**Issues:** 1

- **Line 21** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_fixed_balance.py

**Issues:** 3

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 11** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TokenAccountOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_full_routing.py

**Issues:** 1

- **Line 10** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_imports.py

**Issues:** 1

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_integration_submit_methods.py

**Issues:** 1

- **Line 74** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `'JitoClient call': 'await self.jito_client.send_transaction(signed_tx_bytes)' in method_content,`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

### test_meteora_executor.py

**Issues:** 1

- **Line 34** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_official_method.py

**Issues:** 1

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_real_execution_final.py

**Issues:** 1

- **Line 58** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_router_extraction_fix.py

**Issues:** 1

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_submit_methods.py

**Issues:** 2

- **Line 27** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `"await self.jito_client.send_transaction(signed_tx_bytes)",`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

- **Line 213** 🔴 [RAW_SUBMISSION] Using raw submission call instead of unified send_and_confirm_v0_tx
  - Code: `"result = await self.jito_client.send_transaction(signed_tx_bytes)",`
  - Fix: Use send_and_confirm_v0_tx from executors.submit: result = await send_and_confirm_v0_tx(vtx, rpc_url)

### test_token_compatibility.py

**Issues:** 1

- **Line 8** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_token_extraction.py

**Issues:** 1

- **Line 7** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_transaction_simulation.py

**Issues:** 1

- **Line 39** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### test_ultra_aggressive_account_keys.py

**Issues:** 1

- **Line 47** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### token_validator.py

**Issues:** 1

- **Line 11** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### tools/diagnose_execution_pipeline.py

**Issues:** 9

- **Line 240** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `"""Check MessageV0.compile / VersionedTransaction creation for missing ALTs"""`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 284** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `"""Check if with_compute_budget is used before MessageV0.compile"""`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 286** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `if "MessageV0.compile" in line:`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 305** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `description="with_compute_budget called AFTER MessageV0.compile (should be before)",`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 307** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `suggestion="Call with_compute_budget BEFORE MessageV0.compile: ixs = with_compute_budget(ixs, ...); message = MessageV0.compile(...)"`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 409** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `# Look for MessageV0.compile or transaction building`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 410** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `has_message_compile = "MessageV0.compile" in content or "Message.new_with_blockhash" in content`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 416** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `if "MessageV0.compile" in line or "Message.new_with_blockhash" in line:`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 427** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `description="MessageV0.compile without apparent blockhash fetch",`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

### transaction_analyzer.py

**Issues:** 2

- **Line 279** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `address_table_lookups = message.get('addressTableLookups', [])`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### transaction_analyzer_severely_corrupted.py

**Issues:** 2

- **Line 141** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `# Handle addressTableLookups for versioned transactions`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### transaction_cloner.py

**Issues:** 2

- **Line 333** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `new_message = Message.new_with_blockhash(`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

- **Line 384** 🔴 [MISSING_ALTS_COMPILE] MessageV0.compile/VersionedTransaction may be missing address_lookup_tables parameter
  - Code: `new_message = Message.new_with_blockhash(`
  - Fix: Pass address_lookup_tables parameter when message has addressTableLookups: MessageV0.compile(..., address_lookup_tables=[...])

### transaction_history_analyzer.py

**Issues:** 3

- **Line 13** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 14** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Confirmed, Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import MemcmpOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

### tx_builder.py

**Issues:** 3

- **Line 4** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient  # At top with other imports`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.types import TxOpts`
  - Fix: Replace with solders equivalent: from solders.* import ...

- **Line 16** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.commitment import Processed`
  - Fix: Replace with solders equivalent: from solders.* import ...

### tx_translator.py

**Issues:** 1

- **Line 12** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.api import Client`
  - Fix: Replace with solders equivalent: from solders.* import ...

### utils/alts.py

**Issues:** 1

- **Line 34** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `# from the message.addressTableLookups field`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

### utils/ata.py

**Issues:** 2

- **Line 42** 🔴 [ATA_PLACEHOLDER] Placeholder ATA PDA derivation returns mint instead of proper PDA
  - Code: `return mint  # placeholder!`
  - Fix: Replace with: seeds = [bytes(owner), bytes(SPL_TOKEN_PROGRAM_ID), bytes(mint)]; ata, _ = Pubkey.find_program_address(seeds, SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID); return ata

- **Line 70** 🔴 [ATA_EXISTS_BOOLEAN] ensure_ata function uses 'exists' boolean parameter instead of RPC query
  - Code: `def ensure_ata_for(owner: Pubkey, mint: Pubkey, payer: Pubkey, exists: bool) -> List[Instruction]:`
  - Fix: Replace 'exists' parameter with actual RPC query: response = await rpc_client.get_token_accounts_by_owner(owner, {'mint': str(mint)}); exists = response.value is not None and len(response.value) > 0

### validate_modules.py

**Issues:** 1

- **Line 155** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### verify_fix.py

**Issues:** 1

- **Line 15** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### verify_official_program_id.py

**Issues:** 1

- **Line 9** 🔵 [SOLANA_PY_IMPORT] Using solana-py import (should use solders)
  - Code: `from solana.rpc.async_api import AsyncClient`
  - Fix: Replace with solders equivalent: from solders.* import ...

### wallet_tx_parser.py

**Issues:** 1

- **Line 575** 🟡 [MISSING_BUILD_ALTS] File references addressTableLookups but doesn't call build_alts_from_tables
  - Code: `alt_info["lookup_tables"] = tx_data.get("addressTableLookups", [])`
  - Fix: Import and use build_alts_from_tables: from utils.alt_fetch import build_alts_from_tables; alts = build_alts_from_tables(rpc_url, address_table_lookups)

## General Recommendations

1. **Address HIGH priority issues first** - These directly impact execution reliability
2. **Fix ATA-related issues** - Proper PDA derivation and RPC queries are critical
3. **Standardize on send_and_confirm_v0_tx** - Replace all raw submission calls
4. **Gate scaffold executors** - Prevent incomplete code from running in production
5. **Complete BuildResult migration** - Ensure all builders return BuildResult properly
6. **Fix ALT handling** - Proper address lookup table usage prevents transaction failures
7. **Migrate from solana-py to solders** - Use solders exclusively for consistency

