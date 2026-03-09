# Run integration imports with lightweight mocks for problematic deps
import sys, types, os
# Create minimal mock for win32com
win32 = types.ModuleType('win32com')
client = types.ModuleType('win32com.client')
def Dispatch(x):
    class Dummy: pass
    return Dummy()
client.Dispatch = Dispatch
win32.client = client
sys.modules['win32com'] = win32
sys.modules['win32com.client'] = client
# Minimal pandas mock with DataFrame class to satisfy imports that only reference it lightly
class MockDataFrame:
    def __init__(self,*args,**kwargs):
        pass

mock_pandas = types.ModuleType('pandas')
mock_pandas.DataFrame = MockDataFrame
mock_pandas.read_csv = lambda *a,**k: MockDataFrame()
# Some modules import pandas as pd, and then use pd.DataFrame, pd.read_csv etc.
sys.modules['pandas'] = mock_pandas
# Also mock numexpr and bottleneck used by pandas internals
sys.modules['numexpr'] = types.ModuleType('numexpr')
sys.modules['bottleneck'] = types.ModuleType('bottleneck')

# Now run the import tests
from importlib import util
WORKSPACE_DESIGN = '/home/myhome/.openclaw/workspace/설계'
if WORKSPACE_DESIGN not in sys.path:
    sys.path.insert(0, WORKSPACE_DESIGN)
modules = ['inspection_manager.py','defect_reg_app.py','quality_manager.py']
results = {}
for m in modules:
    path = os.path.join(WORKSPACE_DESIGN,m)
    if not os.path.exists(path):
        results[m] = 'NOT_FOUND'
        continue
    spec = util.spec_from_file_location(m.rstrip('.py'), path)
    mod = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        has_main = hasattr(mod,'main')
        results[m] = 'LOADED(main={})'.format(has_main)
    except Exception as e:
        results[m] = f'ERROR: {e}'
print(results)
