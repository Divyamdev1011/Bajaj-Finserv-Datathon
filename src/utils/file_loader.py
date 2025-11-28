import glob, os
def list_raw_pdfs(data_dir='data/raw'):
    return glob.glob(os.path.join(data_dir, '*.pdf'))
