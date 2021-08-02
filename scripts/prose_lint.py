import nbformat, os, subprocess, sys, json, urllib, zipfile

# Where to store the extracted markdown:
TEMP_PATH = './scripts/temp'

# Where to looks for notebooks:
NB_ROOT = './notebooks'

# Which notebooks to  extract:
NB_PATHS = './scripts/notebook_paths.txt'

# If --CI, the filepath to the style to use:
CI_STYLE = 'https://github.com/frankharkins/qiskit-textbook-styleguide/releases/download/v0.1-alpha/QiskitTextbook.zip'

# Number of warnings allowed in a file before failing test
MAX_WARNINGS = 20

DOCSTR = f"""
This script extracts the markdown from notebooks in `{NB_ROOT}`
(if they are listed in `{NB_PATHS}`) and saves them to markdown
files in `{TEMP_PATH}`. The script then runs Vale prose linter
on these files and can interprets the output as pass / fail if
the `--CI` option is given.

Usage: python3 scripts/text_lint.py <options>
Where <options> can be one of:

    --CI       Use the tests that will be run on Github PRs.
               Script produces minimal output and returns either
               pass / fail. Fail occurs if vale returns an error,
               and/or there are more than {MAX_WARNINGS} found in
               a file.

    -- help    Displays this help message
"""

def extract_markdown(filepath):
    """Extracts markdown from notebook at <filepath> for linting
    with vale. Stores extracted markdown in TEMP_PATH with same
    relative filename (ignoring extensions).
    """
    nb = nbformat.read(f'{NB_ROOT}/{filepath}.ipynb',
                       as_version=4)
    md = ""
    for cell in nb.cells:
        if cell['cell_type'] == 'markdown':
            md += cell['source'] + "\n"

    out = ""
    for line in md.split('\n'):
        if '<!--' in line:
            if 'vale ' not in line:
                continue

        out += line + '\n'

    newpath = f"{TEMP_PATH}/{NB_ROOT}/{filepath[::-1].split('/',1)[1][::-1]}"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    with open(f'{TEMP_PATH}/{NB_ROOT}/{filepath}.md', 'w') as f:
        f.write(out)

if __name__ == '__main__':
    import time
    t0 = time.time()
    with open(NB_PATHS) as f:
        filepaths = f.read().split('\n')

    for filepath in filepaths:
        if filepath.startswith('#'):
            continue
        if filepath == '':
            continue
        extract_markdown(filepath)

    if '--help' in sys.argv or '-h' in sys.argv:
        print(DOCSTR)
        sys.exit(0)
    if '--CI' in sys.argv:
        # download & extract styleguide:
        print(f"Downloading styleguide from {CI_STYLE} to {TEMP_PATH+'/style'}")
        zip_path, _ = urllib.request.urlretrieve(CI_STYLE)
        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(TEMP_PATH+'/style')
        vale = subprocess.run(['vale', '--output', 'JSON', '--config',
                               'scripts/vale.ini', f"{TEMP_PATH}/{NB_ROOT}"],
                               stdout=subprocess.PIPE)
        out = json.loads(vale.stdout)
        for file, data in out.items():
            if len(data) > MAX_WARNINGS:
                print(f"Too many prose warnings or errors in '{file}'"
                      f"({len(data)}/{MAX_WARNINGS})")
                sys.exit(1)
            print(f"{file}".ljust(68),
                  f"({len(data)}/{MAX_WARNINGS})".rjust(7))
    else:
        vale = subprocess.run(['vale', f"{TEMP_PATH}/{NB_ROOT}"])

    print(f"Prose linting took {time.time() - t0:.2f}s")
    sys.exit(vale.returncode)
