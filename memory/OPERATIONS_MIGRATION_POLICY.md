Migration Policy (auto-check)

1) Pre-check:
 - Create backup of source DB
 - Run PRAGMA wal_checkpoint(FULL) on source

2) Migration:
 - Use paged copy (chunk size default 1000)
 - Use INSERT OR IGNORE for idempotency
 - Log progress (range and counts)

3) Post-check (automated):
 - Run verification script bridge_migrate_verify_v2.py
 - Verify table counts and report mismatches
 - If mismatch: retry missing-id range copy once, then escalate

4) Retry policy:
 - On mismatch, perform one automated retry limited to missing id ranges
 - If still mismatch, create incident and notify homeAI (팀장님)

5) Reporting:
 - All runs produce a migration log stored at memory/logs/migration_run_<ts>.log
 - RESULT file memory/tickets/TKT-20260309-0003-RESULT.md updated with verification summary
