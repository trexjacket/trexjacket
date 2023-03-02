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

The training material is divided into 3 categories: beginner, intermediate, and advanced.

Beginner
--------

.. button-link:: tutorials/chat-extension/0-main-page.html
    :ref-type: doc
    :color: primary
    :shadow:
    :class: tut-btn

    Recommended Tutorial: Chat

Beginners should be comfortable performing the following tasks:

- Add extensions to a tableau dashboard using a trex file
- Debugging code using the Tableau Output pane
- Retrieving a specific worksheet from the dashboard
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

- Use dialogs to display a new window instead of using ``anvil.alert``
- Whitelist the extension and deploy to Tableau server
- Use data bindings to connect Anvil components to the dashboard
- Use settings to persist data in the workbook
- Call external code using uplink

Advanced
--------

.. button-link:: guides/js_api.html
    :ref-type: doc
    :color: primary
    :shadow:
    :class: tut-btn

    Recommended Resource: Accessing the underlying JS API

Advanced users should be comfortable performing the following tasks:

- Styling the extension to match the Tableau dashboard
- Using the underlying JS API directly
