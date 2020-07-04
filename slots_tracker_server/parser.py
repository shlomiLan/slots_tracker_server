import re

from slots_tracker_server.models import Expense, Categories, PayMethods
from slots_tracker_server.utils import read_file

# TODO: Move
DEFAULT_TIME = '00:00:00'
BUSINESS_NAME_KEY = "שם בית עסק"
AMOUNT_KEY = "סכום חיוב בש''ח"
DATE_KEY = "תאריך"
LOCAL_EXPENSES_KEY = "פירוט עבור הכרטיסים בארץ"
ABROAD_EXPENSES_KEY = "פירוט עבור הכרטיסים בחו''ל בדולר"
ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY = "פירוט עבור הכרטיסים בחו''ל בשקל"
CARD_NAME = "שם כרטיס"


class ExpenseParser:
    pass


class IsracardParser(ExpenseParser):
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = read_file(self.filepath)
        self.titles_col = self.df['Unnamed: 0']
        card_digits = self.titles_col.value_counts().idxmax()
        regex = re.compile(f'.*{card_digits}.*')
        self.pay_method = PayMethods.objects(name=regex)
        if len(self.pay_method) != 1:
            if len(self.pay_method) > 1:
                raise Exception(f'Found more than 1 pay method with card digits: {card_digits}')
            else:
                raise Exception(f'Did not found any pay method with card digits: {card_digits}')
        self.pay_method = self.pay_method[0]
        self.card_name_rows = self.df.index[self.titles_col == card_digits].tolist()
        self.new_categories = set()
        self.new_expenses = set()

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

    def process_section(self, start_keyword, end_keyword):
        section = self.get_section_data(start_keyword, end_keyword)

        for _, row in section.iterrows():
            business_name = row[BUSINESS_NAME_KEY]
            amount = row[AMOUNT_KEY]
            date = row[DATE_KEY]

            expense = Expense(amount=amount, timestamp=date, business_name=business_name, pay_method=self.pay_method)

            if not Expense.is_new_expense(expense):
                continue

            category, is_new_category = Categories.get_or_create_category_by_business_name(business_name)
            if category:
                if is_new_category:
                    self.new_categories.add(business_name)
                expense.category = category
                expense.save()
                self.new_expenses.add(expense)

    def parse_file(self):
        self.process_section(LOCAL_EXPENSES_KEY, ABROAD_EXPENSES_KEY)
        self.process_section(ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY, end_keyword=None)

        return self.new_expenses, self.new_categories
