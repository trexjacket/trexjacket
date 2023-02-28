|WrapperName|, a wrapper for |ProductName|
============================================

Welcome to the online documentation for ``trexjacket``, an open source Python wrapper for |ProductName|. |ProductName| is a platform for building Tableau Extensions using nothing but Python.

The documentation you are currently looking at is for an Anvil App you can import to make building Tableau Extensions with |ProductName| much simpler.

- If you're new to |ProductName| in general, consider viewing the :doc:`whatisthis` document.

- If you'd like to start building a Tableau Extension, head to the :doc:`/tutorials/chat-extension/0-main-page` document.

- If you're here to dive into the details, the more technical documentation can be found in the :doc:`reference/index` section.


Installation
------------

To get started using ``trexjacket`` :

1. Add the following third part dependency token: ``4WJSBYGUAK63RAJO``.

2. Import it into your app using:

.. code-block:: python

    from trexjacket.api import get_dashboard

3. Start building!

.. code-block:: python

    dashboard = get_dashboard()
    dashboard.worksheets
