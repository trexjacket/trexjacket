What's |ProductName|?
----------------------

.. important::

  `Anvil X <https://anvil.works/x>`_ is a toolkit for building and deploying Tableau extensions entirely in Python and provides a framework and IDE for pure-Python full stack web development. It combines the rapid visual design of “low-code” tools with the power and flexibility of a code-first framework.

.. raw:: html

  <h3>What's Anvil?</h3>

`Anvil <https://anvil.works/docs/overview>`_ is a Python-based, full stack web framework used to rapidly develop and deploy web applications.

.. raw:: html

  <h3>What's <code>trexjacket</code></h3>

``trexjacket`` is an open source Python wrapper for the Tableau Extensions API, most easily accessed using `Anvil X <https://anvil.works/x>`_. It provides a Pythonic interface to the elements on your Tableau dashboard: worksheets, filters, dashboards, and more.

With ``trexjacket``, you can write code like:

.. code-block:: python
    :linenos:

    from trexjacket.api import get_dashboard
    dashboard = get_dashboard() # <- a Python object that represents a Tableau dashboard
    dashboard.register_event_handler('selection_changed', handle_selection)

    def handle_selection(event):
      selection = event.get_selected_marks()
      print(f'The user chose: {selection}')

      for ds in dashboard.datasources:
        ds.refresh()

      dashboard.get_worksheet('Sale Map').apply_categorical_filter('State', ['MI', 'WI'])
      dashboard.get_parameter('Salary Cap') = 50000

.. raw:: html

  <h3>What's a Tableau extension?</h3>

In Tableau's own words,

    "The Extension API enables customer to integrate and interact with data from other applications directly in Tableau"

.. raw:: html

    <h4>...in other words</h4>

Tableau dashboard extensions are web applications that have two-way communication with the dashboard. They enable all sorts of scenarios, like letting you integrate Tableau with custom applications, making possible for you to modify the data for a viz, or even creating custom visualizations inside the dashboard.

.. image:: https://extension-documentation.s3.amazonaws.com/media/sampleextension.png

.. raw:: html

  <h3>What can you do with an extension?</h3>

Because Tableau extensions are web applications, there is a wide variety of different things you can do with them. Things like:

* Integrate with third-party APIs inside the dashboard
* Use third-party charting libraries like ``visjs`` or ``d3`` to add custom visualizations
* Enable write-back functionality so users can modify data in a viz and have that change automatically update the source data
* Build custom viz and interactivity types, such as a filter replacement and custom interfaces

To get a taste of what other people have built, check out some `dashboard extensions on the Tableau Exchange <https://exchange.tableau.com/extensions>`_

.. raw:: html

  <h3>The Objective of Anvil X: Investment to Insight</h3>

The primary purpose of |ProductName| is to reduce the amount of time from investment to insight.

By making Tableau Extensions more accessible to organizations, Dashboard Developers are unleashed to do more. "More" includes new integrations, sophisticated user interfaces, and more advanced data tools.

|ProductName| does this by:

- Creating a Pythonic representation of the Tableau Dashboard
- Enabling one-Click extension deployment
- A modern, efficient development experience
- Enterprise-ready user management and access controls
- Transparent, real-time logging and error handling
- Secure Server environment

The below image outlines how this Python library is related to Anvil and Tableau.

.. image:: https://extension-documentation.s3.amazonaws.com/media/extension_architecture.PNG


.. admonition:: Eager to build something?

  Consider following the :doc:`/tutorials/chat-extension/0-main-page` tutorial where you'll build your first Tableau Extension with |ProductName|!
