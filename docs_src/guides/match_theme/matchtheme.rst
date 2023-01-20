Style the extension using Tableau workbook formatting
======================================================

It can be helpful to have the styling of the Anvil extension to match the Tableau workbook's theme. This can be accomplished by using the html classes listed `here <https://tableau.github.io/extensions-api/docs/trex_format.html>`_. For example, if you create a blank form with raw html that contains:

.. code-block:: html

    <h1 class="tableau-worksheet-title"> Subheader in Anvil, using tableau-worksheet-title class </h1>

The styling of this ``h1`` element will now match the styling selected in Tableau when navigating through Format > Workbook > Worksheet Titles.


.. dropdown:: Tada!
    :open:

    .. image:: styling_demo.gif

.. button-link:: https://anvil.works/build#clone:DFSSQZK2L4YCLEAW=2RYC5L2DEE5KS4VKVCG6Z675
   :color: primary
   :shadow:

   Click here to clone the Anvil App
