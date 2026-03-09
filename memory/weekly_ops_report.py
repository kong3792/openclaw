#!/usr/bin/env python3
import os,glob
from datetime import datetime
out=[]
# collect recent issues: last week's cleanup and db health logs, open tickets
ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
out.append(f'Weekly Ops Report generated at {ts}')
# open tickets excerpt
try:
    with open('memory/tickets/TICKET-INDEX.md') as f:
        idx=f.read()
    idx_lines = idx.splitlines()
    out.append('\n-- TICKET-INDEX (excerpt) --\n')
    out.append('\n'.join(idx_lines[:50]))
except:
    out.append('TICKET-INDEX not readable')
# last db health logs
import glob
d_logs=sorted(glob.glob('memory/logs/db_health_*.log'))
if d_logs:
    out.append('\n-- DB Health latest --\n'+d_logs[-1])
# migration logs
m_logs=sorted(glob.glob('memory/logs/migration_run_*.log'))
if m_logs:
    out.append('\n-- Migration latest --\n'+m_logs[-1])
# CI runs summary note
out.append('\n-- CI Note --\nRefer to PRs and Actions for details')
# compose 3-line summary (template)
summary_lines = []
# 1) Overall status
overall = 'OK' if (not m_logs or 'All tables migrated successfully' in open(m_logs[-1]).read()) else 'ISSUES'
summary_lines.append(f'Overall status: {overall}')
# 2) Key items (top 2 tickets)
try:
    top_tickets = [l for l in idx_lines if l.startswith('- [TKT-')][:2]
    summary_lines.append('Top items: ' + ' | '.join([t.strip() for t in top_tickets]))
except:
    summary_lines.append('Top items: N/A')
# 3) Action & logs
latest_log = (m_logs[-1] if m_logs else 'No migration logs')
summary_lines.append('Logs: '+ latest_log)

# write report
path='memory/reports/weekly_ops_'+datetime.utcnow().strftime('%Y%m%d')+'.md'
os.makedirs(os.path.dirname(path),exist_ok=True)
with open(path,'w') as R:
    R.write('SUMMARY:\n' + '\n'.join(summary_lines) + '\n\n' + '\n\n'.join(out))
print('written',path)
# also write a short summary file for auto-delivery
with open('memory/reports/weekly_ops_summary_'+datetime.utcnow().strftime('%Y%m%d')+'.txt','w') as S:
    S.write('\n'.join(summary_lines))
print('summary written')
