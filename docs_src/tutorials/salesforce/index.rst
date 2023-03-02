Update Salesforce Opportunities
================================

Today we will be building a Tableau Extension with that can update a Salesforce Opportunity right from our Tableau dashboard! We'll use the ``simple_salesforce`` package to communicate with Salesforce, and Anvil X with ``trexjacket`` to build the rest. Once we're done, we'll have something that looks like this:

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/SF+Tutorial.gif

.. raw:: html

    <h2>Prerequisites</h2>


.. raw:: html

    <h3>Experience with Python & Anvil</h3>

Our demo is developed using Python 3 and `Anvil.Works <https://anvil.works/>`_. We recommend you have some Python programming experience to follow the guide. We also assume you are familiar with the basics of the Anvil platform and already have an account. If you don't, we recommend any of the great tutorials over at the `Anvil Learning Centre <https://anvil.works/learn/tutorials>`_.

.. raw:: html

    <h3>Salesforce Environment</h3>

We will be updating information in Salesforce with the demo and recommend you use a Salesforce development environment to test. You can acquire an account by following `this link <https://developer.salesforce.com/signup>`_.

.. admonition:: Note

    If you use your organizations environment, you will need to coordinate with the administrator to configure API authentication properly.

You should have the System Administrator role for the sake of this tutorial. By default, the user who creates a developer environment will have the system administrator role.

.. raw:: html

    <h3>Tableau Environment</h3>

We will create a simple dashboard to show case Extensions. We will be using Tableau Desktop 2021.2; other versions of Tableau should work as well. If you do not have a Tableau license, you can try it out in a `two-week trial <https://www.tableau.com/products/trial>`_.

.. raw:: html

    <h3>Salesforce Credentials</h3>

Collect your Salesforce Username, Password, and Security Token. We will need all three to connect to the Salesforce API. There are `other authentication methods <https://help.salesforce.com/s/articleView?id=sf.named_credentials_auth_protocols.htm&type=5v>`_ available outside the scope of this tutorial.

* If you do not know your password or security token, resetting your password will allow you to update both via the password reset email.

* If you just need your security token:
    * From your personal settings, in the Quick Find box, enter Reset, and then select Reset My Security Token.
    * Click Reset Security Token. The new security token is sent to the email address in your Salesforce personal settings.

.. raw:: html

    <h2>Let's get started!</h2>

In this tutorial we will:

.. toctree::
   :maxdepth: 1
   :glob:

   *

Click Next to go to Chapter 1.
