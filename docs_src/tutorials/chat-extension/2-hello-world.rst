Chapter 2: Hello World!
~~~~~~~~~~~~~~~~~~~~~~~

Now that we've added the ``trexjacket`` dependency and connected our Anvil app to our Tableau Dashboard using a ``.trex`` file, let's use |ProductName| to access the dashboard from Anvil by adding some code to ``Main``.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/helloworld.gif

Open up ``Main`` and click on the "code" button at the top. At the code near the top of the form, let's use ``get_dashboard`` to create an instance of our dashboard and print a message to the console:

.. code-block:: python
  :linenos:
  :emphasize-lines: 7, 12

  from ._anvil_designer import MainTemplate
  from anvil import *
  from anvil.tables import app_tables
  from anvil import tableau

  from trexjacket.api import get_dashboard
  dashboard = get_dashboard()

  class Main(MainTemplate):
    def __init__(self, **properties):
      self.init_components(**properties)
      print('Hello, World!')

.. tip::

  ``dashboard`` is an instance of the ``Dashboard`` class, which gives you access to all your dashboard elements, things like filters, parameters, datasources, and marks!

Let's see our changes in action. We've already added our Extension to our dashboard, but because we've changed our app in Anvil we'll need to reload the extension in Tableau. To do this:

* Click inside your extension inside Tableau and click the grey, downward facing caret icon
* Click "Reload"

Once you've reloaded your extension, you should see the output of your "Hello, World!" statement in the "Tableau Output 1" pane inside Anvil (see gif).
