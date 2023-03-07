Chapter 1: Setting up the environment
=====================================

Before we dive in to building our extension we'll need to do 3 things:

1. Create an Anvil app with the ``trexjacket`` dependency
2. Create a Tableau dashboard to use our extension inside of
3. Add our Anvil app to our Tableau dashboard using a ``.trex`` file

Step 1: Create your Anvil app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've created an Anvil app for you to start from: `click here to make your own copy <https://anvil.works/build#clone:KIKWE6ZTOXCWRBAN=NVL6DAXCZCC5WWDRZTPW4SOS>`_.

Note that this app already has the ``trexjacket`` dependency added to it, but if you need to add the ``trexjacket`` dependency manually, select "Settings" > "Dependencies" and add the third party dependency using the following token: ``4WJSBYGUAK63RAJO``

Step 2: Create your Tableau Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've also created a starter workbook that is available for download. Click :download:`here <https://extension-documentation.s3.amazonaws.com/tutorials/chat/Chat+Extension+Starter+Tableau+Workbook.twbx>` to download the Tableau dashboard your extension will extend off.

Step 3: Connect your Anvil app to your Tableau dashboard using a trex file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For our Tableau Dashboard to communicate with our Anvil app, we need to create a ``.trex`` file. The ``.trex`` file allows us to add our Anvil app into our dashboard as an extension.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/addtrex.gif

To generate a ``.trex`` file:

* Click the green "Test in Tableau" button in the top right of our screen
* Click "Click here to download the manifest file for your extension" in Step 1. Steps 2 and forward are relevant if you plan to deploy your extension to Tableau Server, but for this tutorial we'll just do step 1.
* Once the ``.trex`` file has downloaded, open your Tableau Dashboard and locate the "Extension" button in the Objects pane.
* Click and drag this button on to the dashboard to add the extension.
* A dialogue box named "Add an Extension" will open. Click "Access Local Extensions" and select the ``.trex`` file from the second step.
* Accept the dialogue by clicking the blue button.

And we're done! In the next chapter we'll start interacting with our dashboard with |ProductName|
