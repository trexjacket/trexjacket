Displaying a popup within Tableau
----------------------------------

.. Anvil link here: https://anvil.works/new-build/apps/REN6GWNXX6Y5PODR

In this tutorial we'll create a pop-up window that appears outside the Tableau dashboard. We'll use the :obj:`~client_code.dialogs` module from the |ProductName|.

Let's get started!

Create a new Anvil App
=======================

To begin, create a new Anvil app with the following:

- A Form named ``Home``

    - Button ``btn_config``, click bound to ``btn_config_click``
    - Button ``btn_alert``, click bound to ``btn_alert_click``
    - Button ``btn_confirm``, click bound to ``btn_confirm_click``

- A Form named ``ShowMe``

    - Text Box ``tb_config``
    - Button ``btn_submit``, click bound to ``btn_submit_click``

- A Module named ``startup``

    - Set as the startup module in Anvil

Once you're done, the Client Code pane should now look like this:

.. image:: media/sidebar.PNG

Now let's configure our startup module.

Startup Module
================

Click on the "startup" module and add the following code:

.. code-block:: python
    :linenos:

    # startup
    import anvil
    from tableau_extension import dialogs

    from .ShowMe import ShowMe

    dialogs.open_start_form('Home')

That's it for the startup module! In order to open dialogue boxes, we need to open whatever form we'd like to load when the extension is opened using the ``open_start_form`` function. ``open_start_form`` takes the name (as a string) of the form we'd like to open when the app starts.

Now let's move to the Home form.

Home Form
==========

Open the "Home" form and add the following code:

.. code-block:: python
    :linenos:

    # Home
    from ._anvil_designer import HomeTemplate
    import anvil
    from anvil import tableau
    from tableau_extension.api import get_dashboard
    from tableau_extension import dialogs

    class Home(HomeTemplate):
        def __init__(self, **properties):
            self.init_components(**properties)
            self.dashboard = get_dashboard()
            self.param = self.dashboard.get_parameter('config_value')

        def btn_config_click(self, **event_args):
            """ Executes when the 'Open a custom form' button is clicked. """
            resp = dialogs.show_form('alert_form')
            # Set the parameter on our dashboard to whatever the user
            # puts in the dialogue box.
            self.param.value = resp

        def btn_alert_click(self, **event_args):
            """ Executes when the 'Open an alert' button is clicked. """
            dialogs.alert('Heres a sample alert.')

        def btn_confirm_click(self, **event_args):
            """ Executes when the 'Open a confirm' button is clicked. """
            if dialogs.confirm('Are you sure?'):
                anvil.alert('You chose yes!')
            return
                anvil.alert('You chose no.')

``btn_alert_click`` and ``btn_confirm_click`` work like the standard Anvil alerts, while ``btn_config_click`` opens a custom form. You might be wondering how I decided to pass the string "alert_form" to ``dialogs.show_form``. We'll cover that in the next section!

ShowMe Form
=============

Finally we'll add the following code to the ``ShowMe`` form.

.. code-block:: python
    :linenos:

    # ShowMe
    from ._anvil_designer import ShowMeTemplate
    from anvil import tableau
    from tableau_extension import dialogs

    # use this decorator to register our form
    @dialogs.dialog_form('alert_form')
    class ShowMe(ShowMeTemplate):
        def __init__(self, **properties):
          self.init_components(**properties)

        def btn_submit_click(self, **event_args):
          self.raise_event('x-close-alert', value=self.tb_config.text)

There are 2 important things happening in this form.

1. We register the form as a popup using ``@dialogs.dialog_form``
    - Note that the string we passed this is the value we pass to ``dialogs.show_form`` in the Home form.
2. On the submit click, we return ``self.tb_config.text``.

View the results
==================

.. dropdown:: Here's what the extension should look like now
    :open:

    .. image:: media/demonstration.gif

Summary
=========

In summary, to open a dialogue box:

1. Open the starting form from a startup module using ``dialogs.open_start_form``
2. Create the form you'd like to show in a dialogue box, and decorate its class definition using ``@dialogs.dialog_form``
3. Open the dialogue form using the name you specified in #2 using ``dialogs.show_form``

View the reference material for dialogs by clicking here: :obj:`~client_code.dialogs`

`Click to clone the Anvil app. <https://anvil.works/build#clone:REN6GWNXX6Y5PODR=5UYQ4J4JS3U3X7O2LJEVOHRZ>`_

:download:`Download the tableau dashboard <popup_workbook.twb>`
