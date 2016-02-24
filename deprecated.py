"""
This section contains functions that organize an excel based version of the
timetable. Originally in schedule.py.
"""

class Stop:
    
    @staticmethod
    def _stack_times(a, n):
        i = 0
        b = []
        c = []
        for entry in sorted(a):
            if i < n:
                c.append(entry)
                i += 1
            elif i == n:
                b.append(c)
                c = [entry]
                i = 1
        while i < n:
            c.append('')
            i += 1
        b.append(c)
        return [list(x) for x in zip(*b)]

    @staticmethod
    def prepare_table(D):
        cells = {}
        temp = []
        for route in sorted(D.keys()):
            temp.append(Stop._stack_times(D[route], 15))
            cells[route] = len(temp[-1][0])
        i = 0
        stop_matrix = []
        while i < len(temp[0]):
            cur = []
            for route in temp:
                cur += route[i]
            stop_matrix.append(cur)
            i += 1
        return stop_matrix, cells

    @staticmethod
    def publish():
        if not os.path.exists(System.path +
                              '/reports/schedules/timetables'):
            os.makedirs(System.path +
                        '/reports/schedules/timetables')
        # Iterate through each stop
        for stop in sorted(Stop.objects.keys()):
            # Set object
            obj = Stop.objects[stop]
            # Build a timetable for each sign at the stop (by gps_ref)
            for ref in sorted(obj._records.keys()):
                # Create stop_matrix table with cell widths for the headers
                stop_matrix, cells = Stop.prepare_table(obj._records[ref])
                summation = 0
                for cell in cells:
                    summation += cells[cell]
                # Open workbook and worksheet
                workbook = xlsxwriter.Workbook(System.path +
                    '/reports/schedules/timetables/' + str(stop) + '_' +
                    str(ref) + '.xlsx')
                worksheet = workbook.add_worksheet('Timetable')
                
                # Set column widths
                alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
                i = 0
                while i < summation:
                    worksheet.set_column(eval('\'' + alphabet[i] + ':' +
                                         alphabet[i] + '\''), 12)
                    i += 1
                
                # Format declarations
                merge_format = workbook.add_format({'bold': True,
                                                    'align': 'center',
                                                    'fg_color': '#D7E4BC',
                                                    'font_size': 18,
                                                    })
                bold_format = workbook.add_format({'bold': True,
                                                   'align': 'center',
                                                   })
                center_format = workbook.add_format({'align': 'center',
                                                     'valign': 'vcenter',
                                                     })
                
                # Write header
                worksheet.merge_range(eval('\'A1:' + alphabet[summation - 1] +
                    '1\''), re.sub('_', ' ', str(stop)), merge_format)
                # Write subheaders for each route
                i = 0
                for cell in sorted(cells.keys()):
                    worksheet.merge_range(eval('\'' + alphabet[i] + '2:' +
                        alphabet[i + cells[cell] - 1] + '2\''), 'Route ' +
                        str(cell), bold_format)
                    i += cells[cell]
                
                # Write data
                row = 3
                for line in stop_matrix:
                    worksheet.write_row('A' + str(row), line , center_format)
                    row += 1
                    
                # Close workbook
                workbook.close()
        return True
