How does this work?
===================

|ProductName| connects to the Tableau Extensions API to establish 2-way communication between an Anvil app and a Tableau Dashboard. While the Tableau Extensions API is a JavaScript API, with |ProductName| and ``trexwrapper`` you can harness all the power of the JS API while only writing Python code.

The process building with |ProductName| looks something like this:

.. image:: https://extension-documentation.s3.amazonaws.com/media/extension_model.PNG

1. First, a user interacts with a Tableau dashboard by doing something like clicking a mark.

2. Event handlers (Python functions configured by the extension developer) in Anvil are notified of the interaction.

3. Event handlers are executed in the Anvil App's environment.

4. (Optional) Write-back is possible with |ProductName|, so if desired, other elements on the dashboard can be controlled using Python.

    - For example, you could apply a filter using a :py:class:`~client_code.model.proxies.Worksheet` object's :py:meth:`~client_code.model.proxies.Worksheet.apply_categorical_filter` method when a particular filter on the dashboard is changed.

.. raw:: html

    <h2>(Optional): Code Example</h2>

Let's walk through the above diagram with some code snippets:

- First you "listen" for #1 with something like:

.. code:: python

    self.dashboard.register_event_handler('selection_changed', self.handle_selection)

- Then 2 becomes possible and a method named ``self.handle_selection`` is executed (3)

- For 4, you might increment a parameter like this:

.. code:: python

    def handle_selection(self, event):
        self.dashboard.get_parameter('my_param') += 1
