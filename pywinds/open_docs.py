import webbrowser
from os import path

# This only works after this script is packaged with docs in it.
webbrowser.open('file://' + path.realpath(path.join(path.dirname(path.realpath(__file__)),
                                                    'docs', 'index.html')))
