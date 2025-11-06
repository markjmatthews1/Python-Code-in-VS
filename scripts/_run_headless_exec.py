import runpy
import sys

try:
    runpy.run_path('run_headless_charts_retry.py', run_name='__main__')
except Exception as e:
    print('ERROR_WHILE_RUNNING_HEADLESS:', e)
    import traceback
    traceback.print_exc()
    sys.exit(1)
print('HEADLESS_RUN_COMPLETE')
