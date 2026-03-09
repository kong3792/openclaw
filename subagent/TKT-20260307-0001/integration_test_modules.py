import importlib.util, os
WORKSPACE_DESIGN = '/home/myhome/.openclaw/workspace/설계'
modules = ['inspection_manager.py','defect_reg_app.py','quality_manager.py']
results = {}
for m in modules:
    path = os.path.join(WORKSPACE_DESIGN,m)
    if not os.path.exists(path):
        results[m] = 'NOT_FOUND'
        continue
    spec = importlib.util.spec_from_file_location(m.rstrip('.py'), path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        has_main = hasattr(mod,'main')
        results[m] = 'LOADED(main={})'.format(has_main)
    except Exception as e:
        results[m] = f'ERROR: {e}'
print(results)
