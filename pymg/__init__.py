"""
██████╗ ██╗   ██╗ ███╗   ███╗  ██████╗
██╔══██╗╚██╗ ██╔╝ ████╗ ████║ ██╔════╝
██████╔╝ ╚████╔╝  ██╔████╔██║ ██║  ███╗
██╔═══╝   ╚██╔╝   ██║╚██╔╝██║ ██║   ██║
██║        ██║    ██║ ╚═╝ ██║ ╚██████╔╝
╚═╝        ╚═╝    ╚═╝     ╚═╝  ╚═════╝


pymg is a CLI tool that can interpret Python files and display errors in a more readable form.

This tool interprets the selected Python file using the Python interpreter that is already
installed on the system, and in case of errors, it displays the errors in separate, diverse
and more readable forms.

In short, by replacing the exceptionhook from the sys module with a customized function that
is called when an exception occurs, pymg can access information about exceptions and then display
them in various and separated templates.

For more information about how pymg works:
https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_does_pymg_work.md

For more information about how to use pymg:
https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_to_use_pymg.md

pymg Github repository:
https://github.com/mimseyedi/pymg
"""

from .pymg import display_error_message