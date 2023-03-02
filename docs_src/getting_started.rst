Getting Started
----------------

Let's build a simple Tableau extension that displays the summary data from Tableau when a user clicks a bar in a bar chart.

First create a new Tableau extension in Anvil by selecting "Blank app" and then "Tableau Extension":

.. image:: https://extension-documentation.s3.amazonaws.com/media/blank_app.PNG
    :width: 300


.. image:: https://extension-documentation.s3.amazonaws.com/media/tableau_extension.PNG
    :width: 300


Download and add a trex file to Tableau
=========================================

In order to add an extension built in Anvil to Tableau it needs to be added to the dashboard using a ``.trex`` file. The trex file is first downloaded from Anvil and then dropped in to your Tableau dashboard.

In Anvil:

1. Click the green "Test in Tableau" button in the top right.
2. A popup will appear, click "Click here to download the manifest file for your extension", the trex file should appear in your downloads.

In Tableau:

4. Go to the dashboard, drag and drop the "Extension" object wherever you'd like.
5. In the bottom left of the alert that appears, select "Access Local Extensions" and locate the ``.trex`` file from step 2.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/media/download_trex.gif

Write some code
================

Now that we're connected to our dashboard let's add some components and code.

- Rename ``Form1`` to ``MainForm``
- Add a label to the UI and change its Python name to ``label_1``
- Paste the following in the code section of the ``MainForm``

.. code-block:: python
    :linenos:

    # client_code/MainForm
    from ._anvil_designer import MainFormTemplate
    from anvil import *
    from trexjacket.api import get_dashboard

    class MainForm(MainFormTemplate):
        def __init__(self, **properties):
            self.init_components(**properties)
            self.dashboard = get_dashboard() # we now have a Python object that represents our dashboard!!
            self.dashboard.register_event_handler('selection_changed', self.show_selections)

        def show_selections(self, event):
            print(event.worksheet.selected_records)
            self.label_1.text = str(event.worksheet.get_selected_marks())

In the form code above, we do 2 important things:

1. Get the current Tableau dashboard using :obj:`~client_code.api.get_dashboard`. This returns a :obj:`~client_code.model.proxies.Dashboard` object and contains many useful attributes and methods such as datasources, filters, parameters, and worksheets.

2. Bind the ``show_selections`` method of our Anvil form to the ``selection_changed`` event of the Tableau dashboard using ``register_event_handler``. The ``selection_changed`` event triggers ``show_selections`` whenever the user selects / unselects marks.


.. dropdown:: Congrats, you now have a working Tableau extension!
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/media/firstexample.gif

Additionally, output from the ``print`` statement appears in the Anvil IDE:

.. image:: https://extension-documentation.s3.amazonaws.com/media/output_in_anvil.PNG


.. admonition:: Download the resources!

    .. button-link:: https://anvil.works/build#clone:UZAM5LB6X3KTWC6G=LRO6QQ5553FPXKPB7VBR55MP
        :color: primary
        :shadow:

        :octicon:`link;1em;` Click here to clone the Anvil App

    .. button-link:: https://extension-documentation.s3.amazonaws.com/media/getting_started_workbook.twb
        :color: primary
        :shadow:

        :octicon:`graph;1em;` Click here to download the Tableau workbook
