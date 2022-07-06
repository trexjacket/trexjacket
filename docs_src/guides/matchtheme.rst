Style the extension using Tableau workbook formatting
=====

It can be helpful to match the Anvil extensions theme to the Tableau workbooks theme. This can be done using custom html in the Anvil app itself.

.. code-block:: html

    <h1 class="tableau-worksheet-title"> Subheader, using tableau-worksheet-title class </h1>

Elements using the :code:`tableau-worksheet-title` will now match the styling selected using Format > Workbook > Worksheet Titles.

There are a few more css classes that can be used, read more on the Tableau documentation here: https://tableau.github.io/extensions-api/docs/trex_format.html