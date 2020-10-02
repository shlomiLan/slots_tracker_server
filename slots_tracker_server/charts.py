from datetime import datetime
import json
from typing import Dict, Any, List, Union, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from slots_tracker_server import app
from slots_tracker_server.models import Expense, Categories, PayMethods
from slots_tracker_server.utils import get_bill_cycles

NUM_OF_CHARTS = 3


def print_date(date):
    date_format = '%d/%m/%Y'
    return date.strftime(date_format)


class Charts:
    def __init__(self):
        pd.set_option('precision', 3)
        self.ref_summary: Dict[str, Dict[str, str]] = {}
        self.expense_data: Optional[pd.DataFrame] = None
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.days: Optional[datetime] = None

        self.today: datetime = datetime.today()
        self.charts: List[Any] = [None] * NUM_OF_CHARTS
        self.ref_fields_summary()
        self.start_cycle1, self.end_cycle1, self.start_cycle2, self.end_cycle2 = get_bill_cycles(self.today)

        self.last_month = None
        self.last_month_dates = None

    def ref_fields_summary(self):
        methods_summary = PayMethods.get_summary()
        categories_summary = Categories.get_summary()
        self.ref_summary = dict(pay_method=methods_summary, category=categories_summary)

    def is_db_empty(self):
        return self.expense_data.empty

    def get_expense_data(self):
        self.expense_data = pd.DataFrame(Expense.objects().to_json())
        if self.is_db_empty():
            app.logger.info('No data in DB, can not create charts')
            return None

        self.translate_expense_data()
        self.expense_data = self.expense_data[self.expense_data.timestamp <= self.today]

        self.last_month = (self.expense_data.timestamp >= self.start_cycle1) & \
                          (self.expense_data.timestamp <= self.end_cycle1)
        self.last_month_dates = f'{print_date(self.end_cycle1)} - {print_date(self.start_cycle1)}'

        return True

    def translate_expense_data(self):
        self.expense_data.category.replace(to_replace=self.ref_summary['category'], inplace=True)
        self.expense_data.pay_method.replace(to_replace=self.ref_summary['pay_method'], inplace=True)
        self.expense_data.timestamp = pd.to_datetime(self.expense_data.timestamp, format='%Y-%m-%d')

    def clac_charts(self):
        if self.get_expense_data():
            self.time_charts()

            return json.dumps(self.charts)

        return None

    def time_charts(self):
        # Chart 2 - All expenses - last month
        temp = round(self.expense_data[self.last_month].groupby('category').sum().amount.sort_values(ascending=False), 1)  # noqa
        title = f'All expenses - last month ({self.last_month_dates}) - new'
        self.charts[1] = self.to_chart_data(series=temp, title=title)

        table = []
        # Chart 1 (table) - All expenses since the last 10th
        # All expenses in previous month (10th to 10th)
        total = self.expense_data[self.last_month].amount.sum().round()
        title = f'All expenses in previous month ({self.last_month_dates})'
        table.append([title, total])

        self.charts[0] = self.to_chart_data(table=table, title=title, c_type='table')

        # Chart 3 - Total expenses by month
        number_of_months = 6
        start_date = self.today - relativedelta(months=+number_of_months, day=1, hour=0, minute=0, second=0, microsecond=0)
        chart_data = self.expense_data[self.expense_data.timestamp >= start_date]
        chart_data = chart_data.groupby(pd.Grouper(key='timestamp', freq='1M')).sum().round().amount

        chart_data.index = chart_data.index.strftime('%B %Y')
        title = 'All expenses by month - last 6 months - Total'
        self.charts[2] = self.to_chart_data(series=chart_data, title=title, c_type='line')

    def get_summary_table(self):

        self.clac_charts()
        if self.charts:
            return self.charts[0]

        return None

    @staticmethod
    def to_chart_data(title: str, series: pd.Series = None, c_type: str = 'horizontalBar',
                      table: List[List[Union[str, float]]] = None):

        if c_type in ['horizontalBar', 'line']:
            if series is not None:
                labels: List[str] = series.index.tolist()
                c_data: Dict[str, Any] = dict(labels=labels, datasets=[dict(data=series.values.tolist(), label='')])
                options: Dict[str, Any] = \
                    dict(scales=dict(xAxes=[dict(ticks=dict(autoSkip=False))]), title=dict(text=title, display=True),
                         maintainAspectRatio=False)

                if c_type == 'line':
                    for data_point in c_data.get('datasets'):
                        data_point['fill'] = False

                return dict(type=c_type, data=c_data, options=options)
        elif c_type == 'table':
            return dict(type=c_type, data=table)
        else:
            raise ValueError('Unsupported chart type')
