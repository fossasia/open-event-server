"""Copyright 2015 Rafal Kowalski"""
import sys
import os
try:
    PWD = os.environ['PWD']
    sys.path.extend([PWD])
except Exception as error:
    print error

import xlrd
from open_event.tools.fossasia.session_saver import Saver


def get_time(row, date):
    time = xlrd.xldate_as_tuple(row[1].value, xl_workbook.datemode)
    return '2016 ' + date + ' ' + str(time[3]) + ':' + str(time[4])

if __name__ == "__main__":
    xl_workbook = xlrd.open_workbook('open_event/tools/fossasia/FOSSASIA 2016 - Schedule.xlsx')
    sheet_names = xl_workbook.sheet_names()
    print('Sheet Names', sheet_names)

    for sheet_n in sheet_names:
        print sheet_n
        if sheet_n in ["Tech Kids I", "OpenTech"]:

            xl_sheet = xl_workbook.sheet_by_name(sheet_n)
            date = ""

            print xl_sheet.row(1)
            for index in xrange(xl_sheet.nrows):
                row = xl_sheet.row(index)

                if "Sunday" in row[0].value or "Saturday" in row[0].value or "Friday" in row[0].value:
                    date = row[0].value
                try:
                    next_row = xl_sheet.row(index+1)
                    time = get_time(row, date)
                    end_time = get_time(next_row, date)

                    Saver(row, 4, time, end_time, sheet_n)._save()
                except Exception as e:
                    print e

