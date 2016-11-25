"""Removes unnecessary information from an *.ipynb to make it
easier to track it with git."""

import json
import sys


def main():
    """Sanitizes the loaded *.ipynb."""
    with open(sys.argv[1], 'r') as nbfile:
        notebook = json.load(nbfile)

    # remove kernelspec (venvs)
    try:
        del notebook['metadata']['kernelspec']
    except KeyError:
        pass

    # remove outputs and metadata, set execution counts to None
    for cell in notebook['cells']:
        try:
            if cell['cell_type'] == 'code':
                cell['outputs'] = []
                cell['metadata'] = {}
                cell['execution_count'] = None
        except KeyError:
            pass

    with open(sys.argv[1], 'w') as nbfile:
        json.dump(notebook, nbfile)


if __name__ == '__main__':
    main()
