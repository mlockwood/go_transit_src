

class Day:

    objects = {}

    def __init__(self, year, month, day, date, week, dow):
        self._year = year
        self._month = month
        self._day = day
        self._date = date
        self._week = week
        self._dow = dow
        self._count = 0
        self._average = 0
        self._straight_line = System.increment * abs(date - System.begin
                                                     ).days + System.baseline
        self.set_week()
        self.set_month()
        Day.objects[(year, month, day)] = self

    @staticmethod
    def add_count(date, dow, week, count):
        if (date.year, date.month, date.day) not in Day.objects:
            Day(date.year, date.month, date.day, date, week, dow)
        Day.objects[(date.year, date.month, date.day)]._count += count
        return True

    def set_week(self):
        if self._week not in Week.objects:
            Week(self._week)
        Week.objects[self._week]._days[self._dow] = self
        return True

    def set_month(self):
        month_key = str(self._year) + '_' + Month.convert_m[int(self._month)]
        if month_key not in Month.objects:
            Month(month_key)
        Month.objects[month_key]._days[self._date] = self

class Week:

    objects = {}
    convert_d = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
               'Thursday': 4, 'Friday': 5, 'Saturday': 6}
    convert_a = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wedesday',
                 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}

    def __init__(self, week):
        self._week = week
        self._days = {}
        Week.objects[week] = self

    @staticmethod
    def publish():
        if not os.path.exists(System.path + '/reports/ridership/weekly/excel'):
            os.makedirs(System.path + '/reports/ridership/weekly/excel')
        for week in sorted(Week.objects.keys()):
            # Open workbook and worksheet
            workbook = xlsxwriter.Workbook(System.path +
                '/reports/ridership/weekly/excel/' + str(week) + '.xlsx')
            worksheet = workbook.add_worksheet('Ridership')
            chart = workbook.add_chart({'type': 'column'})
            # Set week object and averages
            obj = Week.objects[week]
            obj.set_averages()
            # Set column widths
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 12)
            worksheet.set_column('C:C', 12)
            worksheet.set_column('D:D', 12)
            worksheet.set_column('E:E', 12)
            # Write header
            worksheet.write_row('A1', ['Weekday', 'Date', 'Riders', 'Average',
                                       'Pilot Target'])
            # Write data
            row = 2
            for dow in sorted(obj._days.keys()):
                worksheet.write_row('A' + str(row),
                    [obj._days[dow]._date.strftime('%A'),
                     obj._days[dow]._date.strftime('%d, %b %Y'),
                     obj._days[dow]._count, round(obj._days[dow]._average, 2),
                     round(obj._days[dow]._straight_line, 2)])
                row += 1
            # Set chart series
            chart.add_series({'name': 'Ridership',
                              'categories': ('=Ridership!$B$2:$B$' +
                                             str(row - 1)),
                              'values': '=Ridership!$C$2:$C$' + str(row - 1),
                              'line': {'color': '#008000'},
                              })
            chart.add_series({'name': 'Average',
                              'categories': ('=Ridership!$B$2:$B$' +
                                             str(row - 1)),
                              'values': '=Ridership!$D$2:$D$' + str(row - 1),
                              'line': {'color': '#000080'},
                              })
            chart.add_series({'name': 'Pilot',
                              'categories': ('=Ridership!$B$2:$B$' +
                                             str(row - 1)),
                              'values': '=Ridership!$E$2:$E$' + str(row - 1),
                              'line': {'color': '#808080'},
                              })
            # Set chart ancillary information
            chart.set_title({'name': 'Weekly Ridership'})
            chart.set_x_axis({'name': 'Day'})
            chart.set_y_axis({'name': 'Riders'})
            # Insert chart into the worksheet
            worksheet.insert_chart('A' + str(row + 2), chart, {'x_offset': 10,
                                                               'y_offset': 10})
            workbook.close()
        return True

    def set_averages(self):
        N = {}
        for week in sorted(Week.objects.keys()):
            if week == self._week:
                break
            for dow in Week.objects[week]._days:
                try:
                    self._days[dow]._average += Week.objects[
                        week]._days[dow]._count
                    N[dow] = N.get(dow, 0) + 1
                except KeyError:
                    pass
        for dow in sorted(self._days.keys()):
            try:
                self._days[dow]._average = self._days[dow]._average / float(
                    N[dow])
            except:
                pass
        return True

class Month:

    objects = {}
    convert_m = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN',
                 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}

    def __init__(self, month):
        self._month = month
        self._days = {}
        Month.objects[month] = self

    @staticmethod
    def publish():
        if not os.path.exists(System.path +
                              '/reports/ridership/monthly/excel'):
            os.makedirs(System.path + '/reports/ridership/monthly/excel')
        for month in sorted(Month.objects.keys()):
            writer = csv.writer(open(System.path +
                '/reports/ridership/monthly/excel/' + str(month) + '.csv', 'w',
                newline=''), delimiter=',', quotechar='|')
            obj = Month.objects[month]
            for date in sorted(obj._days.keys()):
                writer.writerow([Week.convert_a[int(obj._days[date]._dow)],
                    date, obj._days[date]._count, obj._days[date]._average,
                    obj._days[date]._straight_line])
        return True

def publish():
    # Records
    Record.publish_matrix()
    # Weekly
    Week.publish()
    # Monthly
    Month.publish()
    return True

if __name__ == "__main__":
    publish()