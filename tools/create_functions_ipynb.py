"""This modules creates the example notebook for the cvloop.functions
notebook."""

import inspect
import json
import sys

sys.path.insert(0, '../cvloop')
import cvloop.functions  # noqa: E402


GENERATE_ARGS = True


def is_mod_function(mod, fun):
    """Checks if a function in a module was declared in that module.

    http://stackoverflow.com/a/1107150/3004221

    Args:
        mod: the module
        fun: the function
    """
    return inspect.isfunction(fun) and inspect.getmodule(fun) == mod


def is_mod_class(mod, cls):
    """Checks if a class in a module was declared in that module.

    Args:
        mod: the module
        cls: the class
    """
    return inspect.isclass(cls) and inspect.getmodule(cls) == mod


def list_functions(mod_name):
    """Lists all functions declared in a module.

    http://stackoverflow.com/a/1107150/3004221

    Args:
        mod_name: the module name
    Returns:
        A list of functions declared in that module.
    """
    mod = sys.modules[mod_name]
    return [func.__name__ for func in mod.__dict__.values()
            if is_mod_function(mod, func)]


def list_classes(mod_name):
    """Lists all classes declared in a module.

    Args:
        mod_name: the module name
    Returns:
        A list of functions declared in that module.
    """
    mod = sys.modules[mod_name]
    return [cls.__name__ for cls in mod.__dict__.values()
            if is_mod_class(mod, cls)]


def get_linenumbers(functions, module, searchstr='def {}(image):\n'):
    """Returns a dictionary which maps function names to line numbers.

    Args:
        functions: a list of function names
        module:    the module to look the functions up
        searchstr: the string to search for
    Returns:
        A dictionary with functions as keys and their line numbers as values.
    """
    lines = inspect.getsourcelines(module)[0]
    line_numbers = {}
    for function in functions:
        try:
            line_numbers[function] = lines.index(
                    searchstr.format(function)) + 1
        except ValueError:
            print(r'Can not find `{}`'.format(searchstr.format(function)))
            line_numbers[function] = 0
    return line_numbers


def format_doc(fun):
    """Formats the documentation in a nicer way and for notebook cells."""
    SEPARATOR = '============================='
    func = cvloop.functions.__dict__[fun]

    doc_lines = ['{}'.format(l).strip() for l in func.__doc__.split('\n')]
    if hasattr(func, '__init__'):
        doc_lines.append(SEPARATOR)
        doc_lines += ['{}'.format(l).strip() for l in
                      func.__init__.__doc__.split('\n')]

    mod_lines = []
    argblock = False
    returnblock = False
    for line in doc_lines:
        if line == SEPARATOR:
            mod_lines.append('\n#### `{}.__init__(...)`:\n\n'.format(fun))
        elif 'Args:' in line:
            argblock = True
            if GENERATE_ARGS:
                mod_lines.append('**{}**\n'.format(line))
        elif 'Returns:' in line:
            returnblock = True
            mod_lines.append('\n**{}**'.format(line))
        elif not argblock and not returnblock:
            mod_lines.append('{}\n'.format(line))
        elif argblock and not returnblock and ':' in line:
            if GENERATE_ARGS:
                mod_lines.append('- *{}:* {}\n'.format(
                    *line.split(':')))
        elif returnblock:
            mod_lines.append(line)
        else:
            mod_lines.append('{}\n'.format(line))
    return mod_lines


def create_description_cell(fun, line_number):
    """Creates a markdown cell with a title and the help doc string of a
    function."""
    return {
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '## `cvloop.functions.{}` '.format(fun),
            '<small>[[Source](https://github.com/shoeffner/cvloop/blob/',
            'develop/cvloop/functions.py#L{})]</small>\n\n'
            .format(line_number),
            *format_doc(fun),
        ]
    }


def create_code_cell(fun, isclass=False):
    """Creates a code cell which uses a simple cvloop and embeds the function
    in question.

    Args:
        isclass: Defaults to False. If True, an instance will be created inside
                 the code cell.
    """
    return {
        'cell_type': 'code',
        'metadata': {},
        'outputs': [],
        'execution_count': None,
        'source': [
            'from cvloop import cvloop, {}\n'.format(fun),
            'cvloop(function={}{}, side_by_side=True)'.format(fun, '()' if
                                                              isclass else '')
        ]
    }


def main():
    """Main function creates the cvloop.functions example notebook."""
    notebook = {
        'cells': [
            {
                'cell_type': 'markdown',
                'metadata': {},
                'source': [
                    '# cvloop functions\n\n',
                    'This notebook shows an overview over all cvloop ',
                    'functions provided in the [`cvloop.functions` module](',
                    'https://github.com/shoeffner/cvloop/blob/',
                    'develop/cvloop/functions.py).'
                ]
            },
        ],
        'nbformat': 4,
        'nbformat_minor': 1,
        'metadata': {
            'language_info': {
                'codemirror_mode': {
                    'name': 'ipython',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.5.1+'
            }
        }
    }
    classes = list_classes('cvloop.functions')
    functions = list_functions('cvloop.functions')

    line_numbers_cls = get_linenumbers(classes, cvloop.functions,
                                       'class {}:\n')
    line_numbers = get_linenumbers(functions, cvloop.functions)

    for cls in classes:
        line_number = line_numbers_cls[cls]
        notebook['cells'].append(create_description_cell(cls, line_number))
        notebook['cells'].append(create_code_cell(cls, isclass=True))

    for func in functions:
        line_number = line_numbers[func]
        notebook['cells'].append(create_description_cell(func, line_number))
        notebook['cells'].append(create_code_cell(func))

    with open(sys.argv[1], 'w') as nfile:
        json.dump(notebook, nfile, indent=4)


if __name__ == '__main__':
    main()
