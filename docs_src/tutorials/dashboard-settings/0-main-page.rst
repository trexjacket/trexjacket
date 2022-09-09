Configuring 'Settings' for your Dashboard
------

In this tutorial we will define some "Settings" that allow you to configure your Extension for your users. Settings are persisted in the Workbook, so you can use them to set parameters used by your dashboard.

In this tutorial, we'll use Settings to select a column name, so that you can configure your extension to work with that column.

1. Create a Settings Page
2. Make that Settings Page accessible when the workbook is in Author mode
3. Use dropdowns to give users the ability to select from a list of options
4. Get a list of fields from a worksheet, and set one of those to a settings
5. Use that Setting to control which field we act on in the workbook.

We'll start with the Superstore example that comes packaged with Tableau.

.. raw:: html

  <hr>
  <h2>Adding Anvil Code</h2>

To start, you'll need to create 2 forms in Anvil.

.. raw:: html

  <h3>Homepage (form)</h3>


This is main page of the extension, which is what the user will see embedded in the dashboard. It should have the following components:

- Button named ``btn_settings``, click bound to ``btn_settings_click``
- Label named ``lbl_field``
- Label named ``lbl_field_sum``

.. raw:: html

  <h3>Settings (form)</h3>

This is the page we'll show to the user for them to select a Field:

- Label named ``label_1``
- dropdown named ``dropdown_field_options``

    .. image:: media/homepage.PNG

.. raw:: html

  <h3>Configure (form)</h3>

This is the form that will appear in the popup window, and it has the following components:

- Button named: ``btn_submit``, click bound to ``btn_submit_click``
- Label named: ``lbl_config``
- Text box named: ``tb_config``

    .. image:: media/config.PNG

Once you've added the above components, the "Client Code" section of the Anvil IDE should look like this:

.. image:: media/sidebar.PNG

Note that the ``startup`` module has the lightning bolt next to it, indicating that it has been selected as the startup module.


.. raw:: html

  <hr>
  <h2>How is this going to work?</h2>

Before we dive into the code, let's discuss at a high level how this will work.

- When the extension is loaded, the ``startup`` module will look at the url of the Anvil app and determine whether to open the ``Homepage`` or ``Configure`` form.

  - If the URL is the root URL of the app, open ``Homepage``
  - If the URL has parameters, open ``Configure``

    - Whether or not the URL has parameters is something we will control in our form code


.. important:: The ``startup`` module is loaded on 2 occasions:

    1. When the Tableau dashboard is opened for the first time
    2. When the user clicks the "Configure" button and opens the popup

Because the startup form opens forms based on the URL, we will be able to determine whether the extension was loaded inside the dashboard or the popup window.

Now that we have a general idea of how this'll work, let's dive into the details.

.. raw:: html

  <hr>
  <h2>The startup module</h2>

Let's start by adding some code into the ``startup`` module:

.. code-block:: python
  :linenos:

  # startup
  import anvil

  url_hash = anvil.get_url_hash()

  if isinstance(url_hash, dict):
    anvil.open_form('Configure')
  else:
    anvil.open_form('Homepage')


Here we see the conditional logic discussed earlier. By using ``anvil.get_url_hash()`` we can determine whether or not the URL has parameters and route the user appropriately.

.. raw:: html

  <h2>The Homepage Form</h2>

Now let's add some code into the ``Homepage`` form.


.. code-block:: python
  :linenos:

  # Homepage
  from ._anvil_designer import HomepageTemplate
  import anvil
  from anvil import tableau
  from tableau_extension.api import get_dashboard

  class Homepage(HomepageTemplate):
    def __init__(self, **properties):
      self.init_components(**properties)
      self.dashboard = get_dashboard()

    def btn_config_click(self, **event_args):
      popup_url = f"{anvil.server.get_app_origin()}/#?entry=popup"

      tableau.extensions.initializeDialogAsync()
      out = tableau.extensions.ui.displayDialogAsync(popup_url)

      self.lbl_config_setting.text = out
      self.dashboard.get_parameter('config_value').value = out

When the user clicks the "Configure" button, the ``btn_config_click`` method is called, which:

- Adds parameters to the url (``popup_url``) and shows the popup using ``displayDialogAsync``

  - Note that this is what causes the ``startup`` module to show the ``Configure`` form!

- Saves the response into a variable (``out``)
- Uses ``out`` to set the label text and updates a parameter in Tableau

.. raw:: html

  <h2>Configure form</h2>

Let's move to the ``Configure`` form. Add the following:

.. code-block:: python
  :linenos:

  # Configure
  from ._anvil_designer import ConfigureTemplate
  from anvil import tableau

  class Configure(ConfigureTemplate):
    def __init__(self, **properties):
      self.init_components(**properties)

    def btn_submit_click(self, **event_args):
      tableau.extensions.ui.closeDialog(self.tb_config.text)

When the submit button in the popup window is clicked, ``btn_submit_click`` is called and we return whatever the user entered in the text box using ``closeDialog``.

.. important:: Note that whatever is passed to ``closeDialog`` in the ``Configure`` form will be returned by ``displayDialogAsync`` in the ``Homepage`` form.

.. raw:: html

  <hr>

Now add the trex file to the Tableau dashboard (see :doc:`/getting_started`) and click the "Configure" button. The popup should appear, and whatever text you enter in the text box will appear once you close the dialog box with "Submit Configuration".

.. dropdown:: Here's what your extension should look like now
    :open:

    .. image:: media/popupdemo.gif


.. button-link:: https://anvil.works/build#clone:REN6GWNXX6Y5PODR=5UYQ4J4JS3U3X7O2LJEVOHRZ
   :color: primary
   :shadow:

   Click here to clone the Anvil app
