
.. maybe move this somewhere else, seems like too much detail for right here
.. admonition:: Important!

    In order to use the ``dialogs`` in |ProductName| you need to use a startup form. For our scenario we have a startup module named ``startup``, a homepage named ``Homepage``, and a configure form (that we want to open as a dialog box) named ``Configure``.

    * In ``startup``, import the popup form and open the home form

        * .. code-block:: python

            from tableau_extension import dialogs
            from .Configure import Configure
            dialogs.open_start_form('Homepage')

    * In ``Configure``, register the form as a popup

        * .. code-block:: python

            from tableau_extension import dialogs

            @dialogs.dialog_form('configure_form')
            class Configure(ConfigureTemplate):
              def __init__(self, **properties):
                pass

    * In ``Homepage``, open the dialog using:

        * .. code-block:: python

            from tableau_extension import dialogs

            dialogs.show_form('configure_form', width=900, height=900)
