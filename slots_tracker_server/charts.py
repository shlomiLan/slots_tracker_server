import json
from typing import Dict, Any, List

import pandas as pd

from slots_tracker_server.models import Expense, Categories, PayMethods


class Charts:
    ref_summary: Dict[str, Dict[str, str]]
    expense_data: pd.DataFrame
    datasets: Dict[str, pd.DataFrame]
    charts: List[Any]

    def __init__(self):
        pd.set_option('precision', 3)
        self.charts = []
        self.ref_fields_summary()

    def ref_fields_summary(self):
        methods_summary = PayMethods.get_summary()
        categories_summary = Categories.get_summary()
        self.ref_summary = dict(pay_method=methods_summary, category=categories_summary)

    def get_expense_data(self):
        self.expense_data = pd.DataFrame(Expense.objects().to_json())
        self.translate_expense_data()

    def translate_expense_data(self):
        self.expense_data.category.replace(to_replace=self.ref_summary['category'], inplace=True)
        self.expense_data.pay_method.replace(to_replace=self.ref_summary['pay_method'], inplace=True)
        self.expense_data.timestamp = pd.to_datetime(self.expense_data.timestamp)

    def get_datasets(self):
        self.get_expense_data()
        one_time = self.expense_data[self.expense_data.one_time]
        not_one_time = self.expense_data[~self.expense_data.one_time]
        self.datasets = dict(one_time=one_time, not_one_time=not_one_time)

    def clac_charts(self):
        self.get_datasets()

        chart_data = self.datasets.get('not_one_time')
        # TODO: Filter all data to not display futare data
        # TODO: Add chart to display data from the start of the month
        if chart_data is not None:
            # Chart 1 - Regular (not one time) expenses
            temp = chart_data.groupby('category').sum().round().amount.sort_values(ascending=False)
            title = 'Regular (not one time) expenses'
            self.charts.append(self.to_chart_data(temp, title=title))

            # Chart 3 - Regular expenses by card
            temp = chart_data.groupby('pay_method').sum().round().amount.sort_values(ascending=False)
            title = 'Regular expenses by card'
            self.charts.append(self.to_chart_data(temp, title=title))

            # Chart 5 - Regular expenses by month
            temp = chart_data.groupby(pd.Grouper(key='timestamp', freq='1M')).sum().round().amount
            temp.index = temp.index.strftime('%B %Y')
            title = 'Regular expenses by month'
            self.charts.append(self.to_chart_data(temp, title=title, c_type='line'))

        chart_data = self.datasets.get('one_time')
        if chart_data is not None:
            # Chart 2 - One time expenses
            temp = chart_data.groupby('description').sum().round().amount.sort_values(ascending=False)
            title = 'One time expenses'
            self.charts.insert(1, self.to_chart_data(temp, title=title))

        # Chart 4 - All expenses by month
        chart_data = self.expense_data.groupby(pd.Grouper(key='timestamp', freq='1M')).sum().round().amount
        chart_data.index = chart_data.index.strftime('%B %Y')
        title = 'All expenses by month'
        self.charts.insert(3, self.to_chart_data(chart_data, title=title, c_type='line'))

        return json.dumps(self.charts)

    @staticmethod
    def to_chart_data(series: pd.Series, title: str, c_type: str = 'horizontalBar'):
        if c_type in ['horizontalBar', 'line']:
            labels: List[str] = series.index.tolist()
            c_data: List[Dict[str, Any]] = [dict(data=series.values.tolist(), label='')]
            options: Dict[str, Any] = \
                dict(scales=dict(xAxes=[dict(ticks=dict(autoSkip=False))]), title=dict(text=title, display=True),
                     plugins=dict(datalabels=dict(anchor='end', align='end')), legend=dict(display=False))

            if c_type == 'line':
                for d in c_data:
                    d['fill'] = False
                options.update(dict(elements=dict(line=dict(tension=0))))

            return dict(type=c_type, labels=labels, data=c_data, options=options)
        else:
            raise ValueError('Unsupported chart type')
