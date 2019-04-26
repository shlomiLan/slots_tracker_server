# from invoke import task
#
# from pyinvoke.base import init_app
#
#
# @task()
# def fix_gsheet(c, settings=None):
#     init_app(c, settings=settings)
#     import slots_tracker_server.gsheet as gsheet
#     wks = gsheet.get_worksheet()
#     last_row = gsheet.find_last_row(wks)
#     g_data = gsheet.get_all_data(wks)
#
#     # skip the headers row
#     for i, row in enumerate(g_data[1:last_row], start=2):
#         expense_data = row[:gsheet.end_column_as_number()]
#         expense_id = expense_data[0]
#         from slots_tracker_server.models import Expense
#         expense_from_db = Expense.objects.get(id=expense_id)
#         category_name_from_db = expense_from_db.category.name
#
#         if expense_data[2] != category_name_from_db:
#             print(f'Updating expense category, in row: {i}')
#             gsheet.update_with_retry(wks, row=i, col=3, value=category_name_from_db)
