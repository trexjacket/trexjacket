Getting summary / underlying data
-----

Both the summary and underlying data can be retrieved from tableau dashboards using the :py:func:`~client_code.models.Worksheet.get_underlying_records` and :py:func:`client_code.models.Worksheet.get_summary_records` methods which return list of dicts.

.. code-block:: python

    from ._anvil_designer import underlying_dataTemplate
    from anvil import *
    from tableau_extension.api import get_dashboard
    
    class underlying_data(underlying_dataTemplate):
      def __init__(self, **properties):
        self.init_components(**properties)
        self.dashboard = get_dashboard()
        self.chart = self.dashboard.get_worksheet('Bar Chart')
        print(self.chart.get_underlying_records())
        print(self.chart.get_summary_records())
        
.. code-block:: python

    [
      ...
      {'Region': 'The Americas', 'Ease of Business': 104}, 
      {'Region': 'The Americas', 'Ease of Business': 125}, 
      {'Region': 'The Americas', 'Ease of Business': 93},
      ...
    ]

    [
      {'Region': 'The Americas', 'one': 1, 'SUM(Ease of Business)': 2526}, 
      {'Region': 'Europe', 'one': 1, 'SUM(Ease of Business)': 2091}, 
      {'Region': 'Asia', 'one': 1, 'SUM(Ease of Business)': 1542}, 
      {'Region': 'Africa', 'one': 1, 'SUM(Ease of Business)': 1266}, 
      {'Region': 'Oceania', 'one': 1, 'SUM(Ease of Business)': 691}, 
      {'Region': 'Middle East', 'one': 1, 'SUM(Ease of Business)': 671}
    ]
        
    
.. image:: media/underlyingdata.png