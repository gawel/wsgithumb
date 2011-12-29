import os

filename = os.path.abspath(__file__).replace('.pyc', '.py')
document_root = filename.split('tests')[0]
