import time

import anvil
import anvil.server
import anvil.tableau

from .._utils import _dejsonify, _jsonify
from ._registration import _forms, dialog_form

# Import standard_alert and standard_confirm so they are registered
from ._standard_alert import _standard_alert
from ._standard_confirm import _standard_confirm


class DialogAlreadyOpenError(Exception):
    pass


_large = {"width": 800, "height": 600}


def _guess_form(bad_form):
    is_template = "Template" in str(bad_form.__class__.__bases__)
    if is_template:
        bad_form = str(type(bad_form))
        guess = (
            f"""\nYou could try: "{".".join(bad_form.replace(" object", "").split(".")[1:-1])}" """
            " (don't forget to pass any parameters)."
        )
    else:
        guess = ""

    return guess


def show_form(form_str, *args, width=None, height=None, **kwargs):
    """Pop up the form specified by form_str as a dialog in Tableau.

    The string ``form_str`` can either specify a form using the same string as used by ``open_form``,
    or, can be the name of a form decorated with ``@dialogs.dialog_form("{your_dialog_name}")``.

    Example
    --------
    .. code-block:: python
        :linenos:

        # in your Form code:
        @dialogs.dialog_form("my_dialog_form")
        def UserDialogForm(UserDialogFormTemplate):
            def __init__(self, my_argument, **properties):
                ...
            def button_click_event(self, **event_args):
                self.raise_event('x-close-alert', value="my_return_value")

        # Where you want to raise the dialog:
        response = dialogs.show_form("my_dialog_form", my_argument=my_value)

        # This will pop up UserDialogForm for the user, and wait until that dialog closes,
        # i.e. the x-close-alert event occurs (and optionally returns a value through the
        # `value` argument.)
        print(response)
    """
    if not isinstance(form_str, str):
        guess = _guess_form(form_str)
        raise TypeError(
            f"show_form can only be called with the string identifying a form. "
            f"You provided: {type(form_str)}, but expected a string. This can be "
            "the name of the form decorated wtih @dialog_form, or, the string identifying the form "
            f"as used by open_form. {guess}"
        )

    popup_url = f"{anvil.server.get_app_origin()}/#{form_str}"
    send_data = _jsonify((args, kwargs))
    try:
        if width or height:
            dialog_options = {"width": width, "height": height}
            dialog_options = {k: v for k, v in dialog_options.items() if v is not None}
            return_value = anvil.tableau.extensions.ui.displayDialogAsync(
                popup_url, send_data, dialog_options
            )
        else:
            return_value = anvil.tableau.extensions.ui.displayDialogAsync(
                popup_url, send_data
            )

    except Exception as err:
        if "Error: dialog-closed-by-user" in str(err):
            return None
        elif "Error: dialog-already-open" in str(err):
            raise DialogAlreadyOpenError(
                "You've already opened a dialog here, and nested dialog boxes are not allowed."
            )
        else:
            raise err

    dejsonified_return_value = _dejsonify(return_value)
    return dejsonified_return_value


def alert(text, buttons=None, width=None, height=None, large=False):
    """If you want to simply show some text, you can specify the text to show and
    use this helper method to raise a simple alert.

    Unlike the ``anvil.alert``, you cannot pass an instance of a form object.

    Parameters
    --------
    text : str
        The text to show in the popup window

    width : int
        Width of the window

    height : int
        Height of the window

    large : bool
        Whether or not to make the window large.

    Returns
    --------
    None

    Example
    --------

    .. code-block:: python
        :linenos:

        from trexjacket import dialogs
        dialogs.alert('Hello from an alert!')
    """
    if large:
        width = width or _large["width"]
        height = height or _large["height"]

    if not isinstance(text, str):
        raise TypeError(
            f"Dialog alerts can only be passed text to show in the alert. You passed: {type(text)}, expected a string."
            "To pop up a dialog with a Form object, "
            "use dialogs.show_form, and pass a string identifying the form."
        )

    return show_form(
        "_standard_alert", width=width, height=height, buttons=buttons, text=text
    )


def confirm(text, width=None, height=None, large=False):
    """If you want to simply show an okay/cancel dialog, you can use this method
    use this helper method to raise a simple confirm dialog.

    This dialog will return True if the user clicks okay, False if the user clicks Cancel,
    and None if the user closes the dialog (i.e. hits the X button).

    Parameters
    --------
    text : str
        The text to show in the popup window

    width : int
        Width of the window

    height : int
        Height of the window

    large : bool
        Whether or not to make the window large.

    Returns
    --------
    bool

    Example
    --------

    .. code-block:: python
        :linenos:

        from trexjacket import dialogs
        if dialogs.confirm('Are you sure about that?'):
            print('User clicked yes')
        else:
            print('User clicked no')
    """
    if large:
        width = width or _large["width"]
        height = height or _large["height"]

    return show_form("_standard_confirm", width=width, height=height, text=text)


def _return_payload(value=None, **event_args):
    return_value = _jsonify(value)
    anvil.tableau.extensions.ui.closeDialog(return_value)


def _launch_dialog(show_dialog_form):
    startup_data = anvil.tableau.extensions.initializeDialogAsync()
    startup_data = _dejsonify(startup_data)
    dialog_args = startup_data[0]
    dialog_kwargs = startup_data[1]

    if show_dialog_form in _forms:
        try:
            anvil.open_form(_forms[show_dialog_form](*dialog_args, **dialog_kwargs))
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "No module named 'show_dialog_form'. If you are using the dialog_form decorator, "
                "are you importing your decorated form into your startup module?"
            )

    else:
        anvil.open_form(show_dialog_form, *dialog_args, **dialog_kwargs)

    # Add the handler to catch and return values when x-close-alert is called.
    anvil.get_open_form().add_event_handler("x-close-alert", _return_payload)

    # Print the dialog form loaded. This kicks off log streaming as much as anything.
    if show_dialog_form[0] != "_":
        print(f"Loaded form as dialog: {show_dialog_form}")


def open_start_form(start_form):
    """Routes the form to the ``start_form``, unless this has been opened as a dialog.

    The ``start_form`` should be a string pointing to the default start-up form, just as
    you would specify a form using ``anvil.open_form``.

    If this is opening as a dialog, then the form specified by the ``show_form`` call
    from the main session is used.

    Parameters
    --------
    start_form : str
        A string identifier used in the :obj:`~client_code.dialogs.dialog_form` decorator

    Returns
    --------
    None

    Example
    --------

    .. code-block:: python
        :linenos:

        from trexjacket import dialogs
        from .ShowMe import ShowMe

        dialogs.open_start_form('Home')
    """
    show_dialog_form = anvil.get_url_hash()

    if show_dialog_form:
        _launch_dialog(show_dialog_form)

    else:
        anvil.open_form(start_form)
