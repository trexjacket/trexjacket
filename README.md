
<h1 align="center">
:t-rex: trexjacket :coat:
</h1>

<p align="center">
Tableau Today: The best dashboards give people insight
</p>

<p align="center">
<strong>
Tableau with Extensions: The best dashboards help people take action
</strong>
</p>

***

Welcome to the GitHub repository for ``trexjacket``, an open source Python wrapper for the Tableau Extensions API created by Baker Tilly.

The online documentation for `trexjacket` is hosted on readthedocs [here](https://trexjacket.readthedocs.io/en/latest/).

## Use and Installation

1. (If using Anvil X) Add the third party dependency token: ``4WJSBYGUAK63RAJO``
2. Import it into your app and start building! You now have access to worksheets, parameters, filters, and much more.

```python
from trexjacket.api import get_dashboard

dashboard = get_dashboard()
dashboard.get_worksheet('Sale Map').register_event_handler('selection_change', handle_selection)

def handle_selection(event):
    """ This function executes when a user clicks a mark on a dashboard """
    selected_marks = event.get_selected_marks()  # <- this is a list of dicts

    # Incite action by...
    #   updating a Salesforce opportunity
    #   prompting the user to flag or review suspect transactions
    #   capturing qualitative insights to improve future forecasts
    #   sending a reminder email with the click of a button
```

## What's Anvil X?

Accessing the Tableau Extensions API to use ``trexjacket`` is most easily accessed using [Anvil X](https://anvil.works/x?utm_source=x:trexjacket-github), a toolkit for building and deploying Tableau extensions entirely in Python. It provides a framework and IDE for pure-Python full stack web development. It combines the rapid visual design of “low-code” tools with the power and flexibility of a code-first framework. [Learn more about Anvil X here](https://anvil.works/x?utm_source=x:trexjacket-github).

