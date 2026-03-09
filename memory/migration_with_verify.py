# Wrapper: run safe migration then verification and produce report
import subprocess
import datetime

ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
logpath = f'memory/logs/migration_run_{ts}.log'
print('Running migration (safe) and verification. Log ->', logpath)
with open(logpath,'w') as f:
    p = subprocess.run(['python3','memory/bridge_migrate_split_v2.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    f.write(p.stdout.decode())
    q = subprocess.run(['python3','memory/bridge_migrate_verify_v2.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    f.write('\n-- VERIFY --\n')
    f.write(q.stdout.decode())

print('Done. See', logpath)
