import json
from typing import Dict, Any, List, Union

import pandas as pd

from slots_tracker_server.models import Expense, Categories, PayMethods
from slots_tracker_server.utils import get_bill_cycles


def print_date(date):
    date_format = '%d/%m/%Y'
    return date.strftime(date_format)


class Charts:
    ref_summary: Dict[str, Dict[str, str]]
    expense_data: pd.DataFrame
    datasets: Dict[str, pd.DataFrame]
    charts: List[Any]
    today: pd.datetime
    next_10th: pd.datetime
    current_10th: pd.datetime
    previous_10th: pd.datetime

    def __init__(self):
        pd.set_option('precision', 3)
        self.today = pd.datetime.today()
        self.charts = []
        self.ref_fields_summary()
        self.start_cycle1, self.end_cycle1, self.start_cycle2, self.end_cycle2 = get_bill_cycles(self.today)

    def ref_fields_summary(self):
        methods_summary = PayMethods.get_summary()
        categories_summary = Categories.get_summary()
        self.ref_summary = dict(pay_method=methods_summary, category=categories_summary)

    def get_expense_data(self):
        self.expense_data = pd.DataFrame(Expense.objects().to_json())
        self.translate_expense_data()
        self.expense_data = self.expense_data[self.expense_data.timestamp <= self.today]

    def translate_expense_data(self):
        self.expense_data.category.replace(to_replace=self.ref_summary['category'], inplace=True)
        self.expense_data.pay_method.replace(to_replace=self.ref_summary['pay_method'], inplace=True)
        self.expense_data.timestamp = pd.to_datetime(self.expense_data.timestamp, format='%Y-%m-%d')

    def get_datasets(self):
        self.get_expense_data()
        one_time = self.expense_data[self.expense_data.one_time]
        not_one_time = self.expense_data[~self.expense_data.one_time]
        self.datasets = dict(one_time=one_time, not_one_time=not_one_time)

    def clac_charts(self):
        self.get_datasets()
        self.regular_expense_charts()
        self.oen_time_charts()
        self.time_charts()

        return json.dumps(self.charts)

    def regular_expense_charts(self):
        chart_data = self.datasets.get('not_one_time')

        # Chart 4 - Regular (not one time) expenses
        temp = chart_data.groupby('category').sum().round().amount.sort_values(ascending=False)
        title = 'Regular (not one time) expenses'
        self.charts.insert(3, self.to_chart_data(series=temp, title=title))

        # Chart 3 - Regular expenses by card
        temp = chart_data.groupby('pay_method').sum().round().amount.sort_values(ascending=False)
        title = 'Regular expenses by card'
        self.charts.append(self.to_chart_data(series=temp, title=title))

        # Chart 5 - Regular expenses by month
        temp = chart_data.groupby(pd.Grouper(key='timestamp', freq='1M')).sum().round().amount
        temp.index = temp.index.strftime('%B %Y')
        title = 'Regular expenses by month'
        self.charts.insert(4, self.to_chart_data(series=temp, title=title, c_type='line'))

    def oen_time_charts(self):
        chart_data = self.datasets.get('one_time')

        # Chart 6 - One time expenses
        temp = chart_data.groupby('description').sum().round().amount.sort_values(ascending=False)
        title = 'One time expenses'
        self.charts.insert(5, self.to_chart_data(series=temp, title=title))

    def time_charts(self):

        # Chart 7 - All expenses by month
        chart_data = self.expense_data.groupby(pd.Grouper(key='timestamp', freq='1M')).sum().round().amount
        chart_data.index = chart_data.index.strftime('%B %Y')
        title = 'All expenses by month'
        self.charts.insert(6, self.to_chart_data(series=chart_data, title=title, c_type='line'))

        table = []
        # Chart 1 (table) - All expenses since the last 10th
        condition = (self.expense_data.timestamp > self.start_cycle1) & \
                    (self.expense_data.timestamp < self.end_cycle1)

        total = self.expense_data[condition].amount.sum().round()
        title = f'All expenses since the last 10th ({print_date(self.end_cycle1)} - {print_date(self.start_cycle1)})'
        table.append([title, total])

        # All expenses in previous month (10th to 10th)
        condition = (self.expense_data.timestamp > self.start_cycle1) & \
                    (self.expense_data.timestamp < self.end_cycle2)

        total = self.expense_data[condition].amount.sum().round()
        title = f'All expenses since the last 10th ({print_date(self.end_cycle2)} - {print_date(self.start_cycle1)})'
        table.append([title, total])

        self.charts.insert(0, self.to_chart_data(table=table, title=title, c_type='table'))

    @staticmethod
    def to_chart_data(title: str, series: pd.Series = None, c_type: str = 'horizontalBar',
                      table: List[List[Union[str, float]]] = None):

        if c_type in ['horizontalBar', 'line']:
            if series is not None:
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
        elif c_type == 'table':
            return dict(type=c_type, data=table)
        else:
            raise ValueError('Unsupported chart type')
