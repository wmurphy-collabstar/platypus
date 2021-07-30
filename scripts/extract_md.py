import nbformat, os

def extract_markdown(filepath):
    """Extracts markdown from notebook at <filepath> for linting
    with vale. Stores extracted markdown in `scripts/vale/temp/`.
    """
    nb = nbformat.read(f'notebooks/{filepath}.ipynb', as_version=4)
    md = ""
    for cell in nb.cells:
        if cell['cell_type'] == 'markdown':
            md += cell['source'] + "\n"

    out = ""
    for line in md.split('\n'):
        if '<!--' in line:
            continue
        out += line + '\n'

    newpath = f"scripts/vale/temp/{filepath[::-1].split('/',1)[1][::-1]}"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    with open(f'scripts/vale/temp/{filepath}.md', 'w') as f:
        f.write(out)

if __name__ == '__main__':
    with open('./scripts/notebook_paths.txt') as f:
        filepaths = f.read().split('\n')

    for filepath in filepaths:
        if filepath.startswith('#') or filepath=='':
            continue
        extract_markdown(filepath)
