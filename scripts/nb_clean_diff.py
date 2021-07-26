# Reverts inconsequential changes to notebooks (changed path Ids in SVGs / cell execution counts)
# This is to avoid annoying git diffs for notebooks that are otherwise unchanged.

def nbclean(filename, diff_str, check=False):
    """
    Checks notebooks files for:
        - Identical SVG paths with different Ids (Ids should be reverted to avoid large diffs)
        - Execution count for each code cell is same as cell number
    Args:
        filename (str): Filepath of notebook to check
        diff_str (str): Output of git diff <filename> --unified=0
    Returns:
        0: All good
        1: Script encountered something it doesn't know how to handle
        2: Check did not pass (i.e. script needs running on this notebook)
    """
    diff_lines = diff_str.split('\n')
    # Start by fixing SVG outputs
    # collect candidates for reverting
    i = 0
    replacements = []
    while i < len(diff_lines):
        for pattern in ['clip-path=\\"url(#', '<clipPath id=\\"']: 
            if pattern in diff_lines[i]:
                if not pattern in diff_lines[i+1]:
                    return 1
                replacements.append((diff_lines[i], diff_lines[i+1]))
                i += 1
        i += 1

    # replace lines
    with open(filename) as f:
        in_f = f.read()
    for before, after in replacements:
        before, after = before[1:], after[1:]
        if 'clip-path' in before:
            remove_id = lambda x: x.split('(#')[0]+x.split(')')[1]
        else:
            remove_id = lambda x: x.split('=\\"')[0]+x.split('\\">')[1]
        if remove_id(before) == remove_id(after):
            # lines are identical but with different Ids
            if check:
                print(f"Found identical lines with different Ids in {filename}:")
                print(f"  - {before}\n  + {after}\nRun `make nbclean` to fix.")
                return 2
            in_f = in_f.replace(after, before)
    # Now fix execution_count values
    in_f = in_f.split('\n')
    ex_count = 1
    for line in range(len(in_f)):
        if in_f[line].lstrip().startswith('"execution_count":'):
            if check:
                if int(in_f[line].split(':')[1][:-1]) != ex_count:
                    print(f"Cell execution count in wrong order in {filename}")
                    print("Run `make nbclean` to fix.")
                    return 2
            else:
                in_f[line] = in_f[line].split('"')[0] + f'"execution_count": {ex_count},'
            ex_count += 1
    in_f = '\n'.join(in_f)
    with open(filename, 'w') as out_f:
        out_f.write(in_f)
    return 0


if __name__ == '__main__':
    import sys
    from git import Repo

    check = False
    if '--check' in sys.argv:
        # We're just checking if this script needs running, making no changes
        check = True
    if len(sys.argv) > sum((check, 1)):
        print("Unsupported option!")
        sys.exit(1)
    diff = Repo('./').git.diff
    files = diff('origin/main', name_only=True)
    for filename in files.split('\n'):
        if filename.endswith('.ipynb'):
            diff_str = diff('origin/main', filename, no_color=True, unified=0)
            exit_status = nbclean(filename, diff_str, check=check)
            if exit_status == 1:
                print(f"Failed to fix {filename}")
            if exit_status == 2:
                sys.exit(2)
    sys.exit(0)
