import IPython
import sympy


def jupyter_setup():
    from IPython.display import set_matplotlib_formats
    import matplotlib
    set_matplotlib_formats('png', 'pdf') # use PNG inline and PDFs when printing
    matplotlib.rcParams['figure.figsize'] = [10, 5]

def print_sympy(*args):
    '''
    Print the sympy argument in a way that jupyter notebook can print as latex
    Takes argument list of
    '''
    import sympy
    import IPython.display

    st = []
    for arg in args:
        if isinstance(arg, str):
            st.append(arg)
        else:
            try:
                st.append(sympy.latex(arg))
            except:
                raise
    IPython.display.display(IPython.display.Math("".join(st)))


'''
Turns passed value to latex with sympy and wraps in a latex equation
environment. This is necessary to get equation numbering with nbextensions.
'''
def display_equation(*values):
    str_outs = []
    for value in values:
        str_out = value
        if not isinstance(value, str):
            str_out = sympy.latex(value)
        str_outs.append(str_out)
    IPython.display.display(IPython.display.Markdown("\\begin{equation}%s\end{equation}"%"".join(str_outs)))

class Figure:
    def __init__(self):
        self._references = dict()
        self._count = 1

    def add_reference(self, name):
        if name not in self._references:
            self._references[name] = self._count
            self._count += 1

    def get_reference(self, name):
        return self._references[name]

    def display(self, name : str, image : IPython.display.Image):
        self.add_reference(name)
        IPython.display.display(image)


__figure_references = dict()
def get_figure_references(name=None):
    global __figure_references
    if not name:
        name = "root"

    if name not in __figure_references:
        __figure_references[name] = Figure()
    return __figure_references[name]
