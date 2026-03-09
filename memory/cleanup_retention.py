#!/usr/bin/env python3
import os, time, shutil
from datetime import datetime, timedelta

BASE = '/home/myhome/.openclaw/workspace'
now = time.time()
# retention in seconds
keep_full = 60*60*24*30*6  # 6 months
keep_index = 60*60*24*30    # 1 month

# paths to clean
paths_full = [os.path.join(BASE,'memory','sessions'), os.path.join(BASE,'memory','logs')]
paths_summ = [os.path.join(BASE,'memory','summaries'), os.path.join(BASE,'memory','tickets')]

removed = []
for p in paths_full:
    if not os.path.exists(p):
        continue
    for root,dirs,files in os.walk(p):
        for f in files:
            fp = os.path.join(root,f)
            try:
                if now - os.path.getmtime(fp) > keep_full:
                    os.remove(fp)
                    removed.append(fp)
            except Exception:
                pass
# summaries/tickets prune older than 6 months
for p in paths_summ:
    if not os.path.exists(p):
        continue
    for root,dirs,files in os.walk(p):
        for f in files:
            fp = os.path.join(root,f)
            try:
                if now - os.path.getmtime(fp) > keep_full:
                    os.remove(fp)
                    removed.append(fp)
            except Exception:
                pass
# vector index pruning placeholder: remove index files older than 1 month
index_dir = os.path.join(BASE,'memory','index')
if os.path.exists(index_dir):
    for root,dirs,files in os.walk(index_dir):
        for f in files:
            fp = os.path.join(root,f)
            try:
                if now - os.path.getmtime(fp) > keep_index:
                    os.remove(fp)
                    removed.append(fp)
            except Exception:
                pass
# write audit
logp = os.path.join(BASE,'memory','logs','cleanup_retention.log')
with open(logp,'a') as L:
    L.write(datetime.utcnow().isoformat() + ' removed ' + str(len(removed)) + ' files\n')
print('done',len(removed))
