Chapter 6: Time for Tableau
===========================

Now that we've built our extension, we need to add it to a Tableau dashboard! Open up Tableau and create a sample dashboard that connects to your Salesforce account. We opted for creating a simple quilt:

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/sf_screenshot.PNG

Now we're ready to add our extension to our dashboard.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image055.png

In Anvil, press the green "Test in Tableau" button in the top right of your screen and click the link in Step 1 ("Click here to download the manifest..."):

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image057.png

* Once the ``.trex`` file has downloaded, open your Tableau Dashboard and locate the "Extension" button in the Objects pane.
* Click and drag this button on to the dashboard to add the extension.
* A dialogue box named "Add an Extension" will open. Click "Access Local Extensions" and select the ``.trex`` you downloaded from Anvil
* Accept the dialogue by clicking the blue button.

Congrats! 
---------

You now have a working Tableau Extension that writes back to Salesforce:

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/SF+Tutorial.gif


.. button-link:: https://anvil.works/build#clone:TAWMOYGIRY6H5TJZ=6QQ44YM276G5BBGH7J5VTGGS
    :color: primary
    :shadow:

    :octicon:`link;1em;` Click here to clone the Anvil App

