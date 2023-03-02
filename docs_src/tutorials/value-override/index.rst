Value Override
==============

This intermediate tutorial builds off of the skills learned in the Chat Extension. If you haven't yet completed that tutorial, click here: :doc:`/tutorials/chat-extension/0-main-page`.

.. admonition:: Learning objectives

    * Configuring settings for your workbook
    * Opening a pop up window using ``dialogs``
    * Connecting a Tableau Dashboard to an Anvil data table

We'll be building an extension that will extend further than the chat extension. While the chat extension allowed users to comment on marks, the value override extension will allow users to override the values and leave a comment. Additionally, while the chat extension hard coded values like the name of the work sheet and some column names, the value override extension will avoid hardcoding names using dashboard settings to configure our extension.

Once we're done, we'll have something like this:

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/finished_product.gif

Click chapter 1 below to get started!

.. toctree::
   :maxdepth: 1

   1-building-ui
   2-capturing-overrides
   3-enabling-writeback
