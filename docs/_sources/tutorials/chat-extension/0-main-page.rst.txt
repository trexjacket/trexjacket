#################################################
Building a Chat Extension
#################################################


Let’s say your team is building dashboards in Tableau that measure performance over time. You see something worth commenting on one of the marks of the dashboard and you want to be able to document it and share with your team. 

You could invest time and energy into a disconnected, shared document where members of the team write down their thoughts and observations or you could use the tools your business already has to help you organize the commenting process. How can we turn Tableau into an interface where we can quickly share thoughts?



With Anvil of course! Anvil is the easy way to build full stack web apps with nothing but Python. We can use Anvil with the Tableau API extension to build an application which will turn a Tableau dashboard into a chat interface where members of the team can select marks and leave comments.


.. Attach picture
.. image:: images/1-heading.png

.. raw:: html 
    
    <h2>What are we going to build?</h2>


In this tutorial we are going to build and deploy a web application that lets team members leave comments on selected marks of a Tableau dashboard and then lets your team track who, when and why a comment was left.


Here’s a basic overview of how our finished Chat Extension will handle each application: 


.. raw:: html 

    <h2>What are we going to learn?</h2>


.. toctree::
   :maxdepth: 1

   1-create-web-form
   2-create-tableau-dashboard
   3-import-tableau-extension-api
   4-register-event-handler
   5-add-data-grid
   6-create-form-to-add-comments
   7-improve-event-handler
   8-tie-everything-together
..   9-clone-the-app

Let’s get started.

.. Button for next