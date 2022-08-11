How does it work?
=======

The Baker Tilly Extensions Platform works by establishing 2-way communication between an Anvil app and a Tableau Dashboard.

The process typically looks something like this:

.. image:: media/extension_model.PNG

1. First, a user interacts with the tableau dashboard by doing something like clicking a mark.

2. Event handlers (Python functions configured by the extension developer) in Anvil are notified of the interaction.

3. Event handlers are executed in the Anvil App's environment.

4. (Optional) The Extensions Platform also enables write-back, so if desired, other elements on the dashboard can be controlled using Python.

    - For example, you could apply a filter using a :py:class:`~client_code.model.proxies.Worksheet` object's :py:meth:`~client_code.model.proxies.Worksheet.apply_filter` method.

.. raw:: html

    <h2>Code Example</h2>

Walking through the diagram using code

- First you "listen" for #1 with something like:

.. code:: python

    self.dashboard.register_event_handler('selection_changed', self.handle_selection)

- Then 2 becomes possible and a method named ``self.handle_selection`` is executed (3)

- For 4, you might increment a parameter like this:

.. code:: python

    def handle_selection(self, event):
        self.dashboard.get_parameter('my_param') += 1