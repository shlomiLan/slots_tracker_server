from datetime import datetime

import pandas as pd
import re
from abc import ABC, abstractmethod
from pathlib import Path

from slots_tracker_server.models import Expense, Categories, PayMethods
from slots_tracker_server.utils import read_file

ISRACARD_NAME = 'isracard'
VISA_NAME = 'visa'


class ExpenseParser(ABC):
    @abstractmethod
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = read_file(self.filepath)
        self.card_digits = None
        self.pay_method = None
        self.new_categories = set()
        self.new_expenses = set()
        self.bill_month = None

    def validate_pay_method(self, pay_method):
        if len(pay_method) != 1:
            if len(pay_method) > 1:
                raise Exception(f'Found more than 1 pay method with card digits: {self.card_digits}')
            else:
                raise Exception(f'Did not found any pay method with card digits: {self.card_digits}')
        return pay_method[0]

    def get_pay_method(self):
        regex = re.compile(f'.*{self.card_digits}.*')
        pay_method = PayMethods.objects(name=regex)

        return self.validate_pay_method(pay_method)

    def process_new_expense(self, business_name, amount, date, is_payments, bill_date):
        expense = Expense(amount=amount, timestamp=date, business_name=business_name, pay_method=self.pay_method)
        if is_payments and bill_date.month != expense.timestamp.month:
            expense.timestamp = bill_date

        if not Expense.is_new_expense(expense):
            return

        category, is_new_category = Categories.get_or_create_category_by_business_name(business_name)
        if category:
            if is_new_category:
                self.new_categories.add(business_name)
            expense.category = category
            expense.save()
            self.new_expenses.add(expense)


class VisaParser(ExpenseParser):
    BUSINESS_NAME_KEY = "שם בית העסק"
    AMOUNT_KEY = "סכום החיוב"
    DATE_KEY = "תאריך העסקה"
    PAYMENTS_COLUMN = 'פירוט נוסף'
    IS_PAYMENTS_KEY_1 = 'תשלומים'
    IS_PAYMENTS_KEY_2 = 'תשלום'
    BILL_DEFAULT_DAY = 10

    def __init__(self, filepath):
        super().__init__(filepath)
        self.path_obj = Path(filepath)
        self.card_digits = self.get_card_digits()
        self.pay_method = self.get_pay_method()
        self.bill_month, self.bill_year = map(int, self.path_obj.stem.split('_'))

    def get_card_digits(self):
        return self.path_obj.parts[-2]

    def get_bill_date_from_file_name(self):
        p = Path(self.filepath)

    def check_if_payments_expense(self, row):
        payment_value = row[self.PAYMENTS_COLUMN]
        if pd.notna(payment_value) and (self.IS_PAYMENTS_KEY_1 in payment_value or self.IS_PAYMENTS_KEY_2 in payment_value):
            return True

        return False

    def process_section(self):
        for inx, row in self.df.iterrows():
            if inx == len(self.df) - 1:
                continue

            business_name = row[self.BUSINESS_NAME_KEY]
            amount = row[self.AMOUNT_KEY]
            amount = float("".join(d for d in amount if d.isdigit() or d == '.'))
            date = row[self.DATE_KEY]
            date = datetime.strptime(date, '%d/%m/%y')
            is_payments = self.check_if_payments_expense(row)
            bill_date = datetime(self.bill_year, self.bill_month, self.BILL_DEFAULT_DAY)

            self.process_new_expense(business_name, amount, date, is_payments, bill_date)

    def parse_file(self):
        self.process_section()
        return self.new_expenses, self.new_categories


class IsracardParser(ExpenseParser):
    BUSINESS_NAME_KEY = "שם בית עסק"
    BASE_DATE_KEY = 'חיוב לתאריך'
    DATE_KEY = "תאריך"
    AMOUNT_KEY = "סכום חיוב בש''ח"
    LOCAL_EXPENSES_KEY = "פירוט עבור הכרטיסים בארץ"
    ABROAD_EXPENSES_KEY = "פירוט עבור הכרטיסים בחו''ל בדולר"
    ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY = "פירוט עבור הכרטיסים בחו''ל בשקל"
    CARD_NAME = "שם כרטיס"
    PAYMENTS_COLUMN = 'תאור סוג עסקת אשראי'
    IS_PAYMENTS_KEY = 'תשלומים'

    def __init__(self, filepath):
        super().__init__(filepath)

        self.titles_col = self.df['Unnamed: 0']
        self.card_digits = self.titles_col.value_counts().idxmax()
        self.pay_method = self.get_pay_method()
        self.card_name_rows = self.df.index[self.titles_col == self.card_digits].tolist()

    def find_inx(self, keyword, is_start):
        data = self.df[self.titles_col.str.contains(keyword, na=False)]
        if len(data) != 1:
            raise Exception(f"Didnt found a single value for start index, data: {data}")
        keyword_inx = data.index[0]
        if is_start:
            return min(i for i in self.card_name_rows if i > keyword_inx)
        else:
            return max(i for i in self.card_name_rows if i < keyword_inx)

    def get_section_data(self, start_keyword, end_keyword):
        section_start_inx = self.find_inx(start_keyword, is_start=True)
        if end_keyword:
            section_end_inx = self.find_inx(end_keyword, is_start=False)
        else:
            section_end_inx = self.card_name_rows[-1] + 1

        section_data = self.df.iloc[section_start_inx:section_end_inx, :]
        section_data.columns = self.df.iloc[section_start_inx - 1]

        return section_data

    def check_if_payments_expense(self, row):
        payment_value = row[self.PAYMENTS_COLUMN]
        if payment_value and payment_value == self.IS_PAYMENTS_KEY:
            return True

        return False

    def process_section(self, start_keyword, end_keyword):
        section = self.get_section_data(start_keyword, end_keyword)

        for _, row in section.iterrows():
            business_name = row[self.BUSINESS_NAME_KEY]
            amount = row[self.AMOUNT_KEY]
            bill_date = row[self.BASE_DATE_KEY]
            date = row[self.DATE_KEY]
            is_payments = self.check_if_payments_expense(row)

            self.process_new_expense(business_name, amount, date, is_payments, bill_date)

    def parse_file(self):
        self.process_section(self.LOCAL_EXPENSES_KEY, self.ABROAD_EXPENSES_KEY)
        self.process_section(self.ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY, end_keyword=None)

        return self.new_expenses, self.new_categories


def get_parser_from_file_path(filepath):
    if ISRACARD_NAME in filepath.lower():
        return IsracardParser(filepath)
    elif VISA_NAME in filepath.lower():
        return VisaParser(filepath)
    else:
        raise Exception('Unknown file, not matching parser')
