Chapter 3: Fetch Data from Salesforce
=====================================

In this chapter we will cover the create two server functions to fetch opportunity information from Salesforce, and add a decorator to our server functions so we can access them from our client code.

.. admonition:: Note!

    If you are using a Salesforce development environment, it will come preloaded with records for you to use.

Salesforce Opportunities
------------------------

We'll be working with Salesforce Opportunities which you can find in your Salesforce environment by going to Marketing, then selecting Opportunities along the top ribbon.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image018.png

We can pick one of the opportunities from the list to open it and see all off the detail. We'll be updating the Stage, Close Date, and Amount.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image020.png

Creating our Server Functions
-----------------------------

We will be using two Salesforce Objects: Opportunity and OpportunityStage, and we can use a SQL query to get the all of the stages then use Opportunity object to get specific opportunity information.

`Salesforce Object Reference Documentation <https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunity.htm>`_

Let's use ``sf.query`` along with our Salesforce connection to get a list of all the different Opportunity Stages. We'll use ``pandas`` to simplify some of the data wrangling:

.. code-block:: python

    import pandas as pd

    def opportunity_stages():
        sf = salesforce_connect()
        df_oppStage = pd.DataFrame(sf.query("SELECT MasterLabel FROM OpportunityStage LIMIT 200")['records'])
        oppStages = df_oppStage['MasterLabel'].tolist()
        return oppStages

Then let's use ``sf.Object.get`` with an object ID to get the specific record we want to update. The ``opp_ID`` parameter will come from the Client side code later on

.. code-block:: python

    def get_opportunity(opp_ID):
        sf = salesforce_connect()
        opportunity = sf.Opportunity.get(opp_ID)
        return opportunity

Decorators
----------

In order for our users to interact with our sever functions we will need to call them using client functions. Server functions are not available to the client side by default, so we need to add a decorator ``@anvil.server.callable``.

Now our functions look like this:

.. code-block:: python

    @anvil.server.callable
    def opportunity_stages():
        sf = salesforce_connect()
        df_oppStage = pd.DataFrame(sf.query("SELECT MasterLabel FROM OpportunityStage LIMIT 200")['records'])
        oppStages = df_oppStage['MasterLabel'].tolist()
        return oppStages

    @anvil.server.callable
    def get_opportunity(opp_ID):
        sf = salesforce_connect()
        opportunity = sf.Opportunity.get(opp_ID)
        return opportunity

Update an Opportunity
---------------------

Finally, we can wrap our server code with an update function. We take the opportunity ID along with a dictionary of opportunity attributes, StageName, CloseDate, and Amount, from the client side as parameters and remove any records that are ``None``.

Then we'll submit the changes using ``sf.Object.update``

.. code-block:: python

    @anvil.server.callable
    def update_opportunity(opp_ID,change_dict):
        sf = salesforce_connect()
        sf_changes = {k:v for k,v in change_dict.items() if v is not None}
        if sf_changes:
          response = sf.Opportunity.update(opp_ID,sf_changes)

You server module should have this code now
--------------------------------------------

.. code-block:: python
    :linenos:

    import anvil.tables as tables
    import anvil.tables.query as q
    from anvil.tables import app_tables
    import anvil.server
    import anvil.secrets

    from simple_salesforce import Salesforce
    import pandas as pd

    def salesforce_connect():
        username = anvil.secrets.get_secret('sf_username')
        password = anvil.secrets.get_secret('sf_password')
        security_token = anvil.secrets.get_secret('sf_token')
        sf = Salesforce(username= username , password= password , security_token= security_token)
        return sf

    @anvil.server.callable
    def opportunity_stages():
        sf = salesforce_connect()
        df_oppStage = pd.DataFrame(sf.query("SELECT MasterLabel FROM OpportunityStage LIMIT 200")['records'])
        oppStages = df_oppStage['MasterLabel'].tolist()
        return oppStages

    @anvil.server.callable
    def get_opportunity(opp_ID):
        sf = salesforce_connect()
        opportunity = sf.Opportunity.get(opp_ID)
        return opportunity

    @anvil.server.callable
    def update_opportunity(opp_ID,change_dict):
        sf = salesforce_connect()
        sf_changes = {k:v for k,v in change_dict.items() if v is not None}
        if sf_changes:
          response = sf.Opportunity.update(opp_ID,sf_changes)
