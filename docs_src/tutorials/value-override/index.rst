Value Override
==============

This intermediate tutorial builds off of the skills learned in the Chat Extension. If you haven't yet completed that tutorial, click here: :doc:`/tutorials/chat-extension/0-main-page`.

Want to jump straight to the end? Download the Tableau Workbook and the Anvil app below:

* `Anvil App Clone Link <https://anvil.works/build#clone:6N6MNOEIRVC3CK3A=YPSGLJYOYHTQDM3LPEGYXSY2>`_
* :download:`Tableau Workbook <https://extension-documentation.s3.amazonaws.com/tutorials/value-override/Value Override Starter Workbook.twbx>`

.. admonition:: Learning objectives

    * Configuring settings for your workbook
    * Opening pop up window using ``dialogs``
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
