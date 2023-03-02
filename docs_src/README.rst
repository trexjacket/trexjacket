|WrapperName|, a Pythonic wrapper for the Tableau Extensions API
=================================================================

Welcome to the online documentation for ``trexjacket``, an open source Python wrapper for the Tableau Extensions API.

.. card:: New here?

    Consider viewing the :doc:`getting_started` document.

.. card:: Want to start building?

    Head to the :doc:`/tutorials/chat-extension/0-main-page` tutorial.


.. card:: Here to dive into the details?

    Head to the :doc:`reference/index` section.


Installation
------------

To get started using ``trexjacket`` :

1. (If using Anvil X) Add the following third party dependency token: ``4WJSBYGUAK63RAJO``.

2. Import it like this:

.. code-block:: python

    from trexjacket.api import get_dashboard

3. Start building!

.. code-block:: python
    :linenos:

    from trexjacket.api import get_dashboard

    dashboard = get_dashboard()
    dashboard.get_worksheet('Sale Map').register_event_handler('selection_change', handle_selection)

    def handle_selection(event):
        """ This function executes when a user clicks a mark on a dashboard """
        print(f'A user chose these marks: {event.get_selected_marks()}')
