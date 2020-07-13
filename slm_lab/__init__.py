import os

os.environ['PY_ENV'] = os.environ.get('PY_ENV') or 'development'

# EAI Patch to save to /data/ folder from the current working directory
ROOT_DIR = os.getcwd()
# ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

# valid lab_mode in SLM Lab
EVAL_MODES = ('enjoy', 'eval')
TRAIN_MODES = ('search', 'train', 'dev')
