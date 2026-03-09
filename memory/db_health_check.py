#!/usr/bin/env python3
import sqlite3,glob,os
from datetime import datetime
base='memory/db'
out=[]
for f in glob.glob(os.path.join(base,'*.db')):
    try:
        con=sqlite3.connect(f,timeout=5)
        cur=con.cursor()
        cur.execute('PRAGMA wal_checkpoint(FULL);')
        cur.execute('PRAGMA integrity_check;')
        res=cur.fetchone()
        con.close()
        out.append((f,str(res)))
    except Exception as e:
        out.append((f,'ERROR:'+str(e)))
logf='memory/logs/db_health_'+datetime.utcnow().strftime('%Y%m%d%H%M%S')+'.log'
with open(logf,'w') as L:
    for p,r in out:
        L.write(p+' -> '+r+'\n')
print('healthcheck written to',logf)
