Getting Started
----------------

Let's build a simple Tableau extension that displays the summary data from Tableau when a user clicks a bar in a bar chart. When we're done we'll have something like this:

.. image:: https://extension-documentation.s3.amazonaws.com/media/getting-started-demo.gif

To get started, first:

* Click :download:`here <https://anvil.works/build#clone:6GIMOFWXLLVQIVN4=H7DVHBICCFL3IBBNVX2Y7K6O>` to open a starter Anvil app to build off of.

* Click :download:`here <https://extension-documentation.s3.amazonaws.com/media/Getting+Started+Workbook.twb>` to download the sample Tableau workbook that this guide will use.

Download and add the trex file to Tableau
=========================================

In order to add an extension built in Anvil to a Tableau dashboard it needs to be added to the dashboard using a ``.trex`` file. The trex file is first downloaded from Anvil and then dropped in to your Tableau dashboard.

In Anvil:

1. Click the green "Test in Tableau" button in the top right.
2. A popup will appear, click "Download the manifest file" and the ``.trex`` file should download.

In Tableau:

4. Go to your dashboard, drag and drop the "Extension" object wherever you'd like.
5. In the bottom left of the alert that appears, select "Access Local Extensions" and locate the ``.trex`` file from step 2.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/media/download_trex.gif

Write some code
================

Now that we're connected to our dashboard let's add some code to our starter app. Click ``MainForm`` on the left and open the code by clicking the button labeled "Code". Then add the following code:

.. code-block:: python
    :linenos:
    :emphasize-lines: 10-11, 13-16

    from ._anvil_designer import MainFormTemplate
    import anvil

    from anvil import tableau
    from trexjacket.api import get_dashboard

    class MainForm(MainFormTemplate):
        def __init__(self, **properties):
            self.init_components(**properties)
            self.dashboard = get_dashboard()
            self.dashboard.register_event_handler('selection_changed', self.show_selections)

        def show_selections(self, event):
            marks = event.worksheet.get_selected_marks()
            print(marks)
            self.label_output.text = str(marks)

We do 2 things in the code above:

1. Get the current Tableau dashboard using :obj:`~client_code.api.get_dashboard`. This returns a :obj:`~client_code.model.proxies.Dashboard` object and contains many useful attributes and methods such as datasources, filters, parameters, and worksheets.

2. Bind the ``show_selections`` method to the ``selection_changed`` event of the Tableau dashboard using ``register_event_handler``. The ``selection_changed`` event triggers ``show_selections`` whenever the user selects / unselects marks.

Let's reload our extension since we've made changes. In Tableau, click inside the extension you dropped in and click the grey carat icon. Then select "Reload".

.. dropdown:: Click a mark on the dashboard and congrats, you now have a working Tableau extension!
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/media/getting-started-demo.gif

Additionally, output from the ``print`` statement appears in the Anvil IDE:

.. image:: https://extension-documentation.s3.amazonaws.com/media/output_in_anvil.PNG

Eager to keep building? Check out the :doc:`/tutorials/chat-extension/0-main-page` tutorial next!
