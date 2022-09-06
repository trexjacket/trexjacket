Platform Overview
------

This is a Python library that allows users to create Tableau extensions with Anvil using only Python.

.. raw:: html

  <h3>What's Anvil?</h3>

Anvil is a Python-based, full stack web framework used to rapidly develop and deploy web applications.

.. raw:: html

  <h3>What's a Tableau extension?</h3>

In Tableau's own words,

    "The Extension API enables customer to integrate and interact with data from other applications directly in Tableau"

.. raw:: html

    <h4>...in other words</h4>

Tableau dashboard extensions are web applications that have two-way communication with the dashboard. They enable all sorts of scenarios, like letting you integrate Tableau with custom applications, making possible for you to modify the data for a viz, or even creating custom visualizations inside the dashboard.

.. image:: media/sampleextension.png

.. raw:: html

  <h3>What can you do with an extension?</h3>

Because Tableau extensions are web applications, there is a wide variety of different things you can do with them. Things like:

* Integrate with third-party APIs inside the dashboard
* Use third-party charting libraries like ``visjs`` or ``d3`` to add custom visualizations
* Enable write-back functionality so users can modify data in a viz and have that change automatically update the source data
* Build custom viz and interactivity types, such as a filter replacement and custom interfaces

To get a taste of what other people have built, check out some `dashboard extensions on the Tableau Exchange <https://exchange.tableau.com/extensions>`_

.. raw:: html

  <h3>This Library's Objective: Investment to Insight</h3>

The primary purpose of this Python library is to reduce the amount of time required to go from investment to insight

.. important::

    By making Tableau Extensions more accessible to organizations, Dashboard Developers are unleashed to do more. "More" includes new integrations, sophisticated user interfaces, and more advanced data tools.

This Python library accomplishes this by:

- Creating a Pythonic representation of the Tableau Dashboard
- Enabling one-Click extension deployment
- A modern, efficient development experience
- Enterprise-ready user management and access controls
- Transparent, real-time logging and error handling
- Secure Server environment

The below image outlines how this Python library is related to Anvil and Tableau.

.. image:: media/extension_architecture.PNG


Now that you have a good handle on the extensions framework, head over to the :doc:`getting_started` guide for a short walkthrough of what the development experience is like.


.. raw:: html

  <hr>
  <h2>Further Topics</h2>
  <h3>Extension API vs. Embedding JavaScript API</h3>

Related, but separate from the Extensions API is the Embedding JavaScript API.

While the Extension API puts web applications into a tableau dashboard, the Embedding Javascript API puts tableau dashboards into a web application.

* You can use the Embedding JavaScript API for embedding Tableau dashboards in web pages (for example, blog posts), or in line of business applications.
* You can use the Extensions API for integrating web applications into zones in Tableau dashboards.

The Python documentation you are currently reading is related to the Extensions API and **not** the Embedding Javascript API.

.. raw:: html

  <h3>Challenges with Extension Development</h3>

While the Tableau extension JS API is powerful, extension development has challenges. For data teams with Tableau and Python experience,

* There is a significant learning curve to get started
* Extensions require a significant amount of technical knowledge and supporting tools to operate. This includes networking, dev ops, JS programing, security, etc.
* During several attended in-person trainings from Tableau, it's rare for developers to make it through the tutorial and many gave up along the way
* Lots of effort is required to stand up a development environment (chrome headless / npm / sdks)
