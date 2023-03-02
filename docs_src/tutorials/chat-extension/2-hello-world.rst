Chapter 2: Hello World!
~~~~~~~~~~~~~~~~~~~~~~~

Now that we've added the ``trexjacket`` dependency and connected our Anvil app to our Tableau Dashboard using a ``.trex`` file, let's use |ProductName| to access the dashboard from Anvil by adding some code to ``Form1``.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/helloworld.gif

Open up ``Form1`` and click on the "code" button at the top. At the code near the top of the form, import ``get_dashboard`` from ``trexjacket.api`` import ``get_dashboard`` and create an instance of the dashboard in the form:

.. code-block:: python
  :linenos:
  :emphasize-lines: 5, 6

  from ._anvil_designer import Form1Template
  from anvil import *
  from anvil import tableau

  from trexjacket.api import get_dashboard
  dashboard = get_dashboard()

  class Form1(Form1Template):
    def __init__(self, **properties):
      self.init_components(**properties)
      print('Hello, World!')

.. tip::

  ``dashboard`` is an instance of the ``Dashboard`` class, that has gives you access to your dashboard elements, things like filters, parameters, datasources, and marks on the dashboard.

After adding the ``Form1`` code, let's see our changes in action. We've already added our Extension to our dashboard, but because we've changed our app in Anvil we'll need to reload the extension in Tableau. To do this:

* Click inside your extension inside Tableau and click the grey, downward facing caret icon
* Click "Reload"

Once you've reloaded your extension, you should see the output of your "Hello, World!" statement in the "Tableau Output 1" pane inside Anvil (see gif).
