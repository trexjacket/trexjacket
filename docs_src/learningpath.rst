.. raw:: html

   <style>
        .tut-btn {
            font-size: .8em;
        }
   </style>

.. index::
	Beginner Lesson

Recommended Learning Path
=========================

Prerequisites
~~~~~~~~~~~~~

Before diving in to |ProductName|, you'll need to have basic skills and practical experience with Tableau, Python, and Anvil.

Tableau
-------

- Creating worksheets and dashboards
- Connecting to local data sources and databases
- Working with filters and parameters
- :bdg-link-primary:`Click here for additional Tableau learning resources <https://www.tableau.com/learn/training/20212>`

Python
------

- Variables, functions, classes, methods
- Importing modules
- :bdg-link-primary:`Click here for additional Python learning resources <https://www.python.org/about/gettingstarted/>`

Anvil
-----

- Creating a startup module
- Using Forms as components
- Event handlers
- Adding and naming components
- Writing server code and calling it from client code
- :bdg-link-primary:`Click here for additional Anvil learning resources <https://anvil.works/learn/tutorials>`

Once you are comfortable completing the basic tasks of each section above, you're ready to dive into |ProductName|!

.. raw:: html

   <hr>

Extension curriculum
~~~~~~~~~~~~~~~~~~~~

Training material is broadly divided between 3 categories: beginner, intermediate, and advanced.

Beginner
--------

.. button-link:: tutorials/chat-extension/0-main-page.html
    :ref-type: doc
    :color: primary
    :shadow:
    :class: tut-btn

    Recommended Tutorial: Chat

Beginners should be comfortable performing the following tasks:

- Add your extension to a tableau dashboard with a trex file
- Debug your code using the Tableau Output pane
- Get a specific worksheet from your dashboard
- Register event handlers for selection_change, filter_change, and parameter_change events

    - To the dashboard and to a particular worksheet

- Get the selected marks from a worksheet
- Get the underlying worksheet data as a list of dicts
- Navigate the online documentation to find more information about available methods and functions

Intermediate
------------

.. button-link:: tutorials/value-override/index.html
    :ref-type: doc
    :color: primary
    :shadow:
    :class: tut-btn

    Recommended Tutorial: Value Override

.. button-link:: tutorials/salesforce/index.html
    :ref-type: doc
    :color: primary
    :shadow:
    :class: tut-btn

    Recommended Tutorial: Salesforce Writeback

Intermediate users should be comfortable performing the following tasks:

- Use dialogs to display a new window instead of using anvil.alert
- Whitelist your extension and deploy to your Tableau server
- Use data bindings to connect Anvil components to your dashboard
- Use settings to persist data in your workbook
- Call uplink code
- Deploying extensions

Advanced
--------

.. button-link:: guides/js_api.html
    :ref-type: doc
    :color: primary
    :shadow:
    :class: tut-btn

    Recommended resource: Sales Forecasting

Advanced users should be comfortable performing the following tasks:

- Style your extension to match the Tableau dashboard
- Use the JS API directly using either ._proxy or just import them directly
