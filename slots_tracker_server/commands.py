# import click
#
#
# # Google spreadsheet
# @click.command()
# def update_gsheet_header():
#     from slots_tracker_server.gsheet import get_worksheet, get_headers
#     wks = get_worksheet()
#     headers = get_headers(wks)
#     new_headers = ['_id', 'description', 'category', 'timestamp', 'amount', 'pay_method']
#
#     for i, _ in enumerate(headers):
#         headers[i].value = new_headers[i]
#
#     wks.update_cells(headers)
