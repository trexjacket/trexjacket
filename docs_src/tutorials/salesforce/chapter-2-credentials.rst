Chapter 2: Enter our Credentials
================================

Next thing we want to do is enter our Salesforce credentials so we can connect from Anvil.
To do this, we will add the App Secrets module to our app then create a function to connect to our Salesforce environment.

App Secrets
-----------

`Anvil App Secrets <https://anvil.works/learn/tutorials/app-secrets>`_ are a way to store sensitive information, so we don't need to store it in our source code. Anvil Secrets is a great way to store API credentials, database passwords, or any other sensitive personal data.

The first thing we need to do is enable App Secrets by clicking the plus button at the bottom of the module list.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image009.png

A pop up will appear with a list of features you can add to your app, we'll be selecting App Secrets.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image011.png

Once you've added Secrets, you'll see the icon appear in the module list. Select it to start creating secrets for our Salesforce credentials.

Note if you are using your organization's Salesforce environment your API authentication procedure may differ.

Select Create a new secret.

A new line will appear where you can enter the name of your secret. We will start with ``sf_username``.

Now we want to select Set Value. A pop up will appear where you can enter your Salesforce username. This is the username you use to login to the Salesforce environment you are connecting to.

Repeat for your Salesforce password, ``sf_password``, and security token, ``sf_token``.

If you don't have your security token, you can reset it in Salesforce, and they will email you a new token.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image013.png

Server Functions
----------------

Now that we have our secrets, we will want to setup our first server function to connect to Salesforce.
The first thing we need to do is add our first server module. Navigate to the App tab in the list on the left and select Add Server Module.

For a more detailed explanation of Server Code see Anvil's documentation `here <https://anvil.works/docs/server>`_.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image015.png

For our connection to Salesforce, we will need to import two libraries. The first is Secrets to access the credentials we created and the second is Simple Salesforce (`docs <https://simple-salesforce.readthedocs.io/en/latest/>`_) which we will use to connect to the Salesforce REST API using Python.

With secrets we use ``get_secret('secret_name')`` to get our credentials.
Once we have our credentials, we can authenticate using simple Salesforce shown below:

.. code-block:: python

    import anvil.secrets
    from simple_salesforce import Salesforce

    def salesforce_connect():
        username = anvil.secrets.get_secret('sf_username')
        password = anvil.secrets.get_secret('sf_password')
        security_token = anvil.secrets.get_secret('sf_token')
        sf = Salesforce(username= username , password= password , security_token= security_token)
        return sf


We can now use this function to fetch records from our Salesforce environment.
