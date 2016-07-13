

# This section contains functions that organize an excel based version of the timetable. Originally in schedule.py.
class Stop:
    
    @staticmethod
    def stack_times(a, n):
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
            temp.append(Stop.stack_times(D[route], 15))
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


# This section contains functions that organize csv pivot tables of the ridership data.
class Report(object):

    @staticmethod
    def prepare(features, start, end):
        # If no features, return total only
        if not features:
            count = 0
            for record in Record.objects:
                count += Record.objects[record].count
            return {'Total': count}

        # If features, produce variable data structure
        data = {}
        for record in Record.objects:
            obj = Record.objects[record]

            # If outside of the daterange, continue
            if obj.date < start or obj.date > end:
                continue

            # If inside the daterange, process count information
            i = 0
            DS = 'data'

            # Process all except the last feature
            while i < (len(features) - 1):
                try:
                    if eval('obj.' + features[i]) not in eval(DS):
                        exec(DS + '[\'' + eval('obj.' + features[i]) + '\']={}')
                    DS += '[\'' + eval('obj.' + features[i]) + '\']'
                except TypeError:
                    if eval('obj.' + features[i]) not in eval(DS):
                        exec(DS + '[' + str(eval('obj.' + features[i])) + ']={}')
                    DS += '[' + str(eval('obj.' + features[i])) + ']'
                i += 1

            # Process the counts of the last feature
            try:
                exec(DS + '[\'' + eval('obj.' + features[-1]) + '\']=' + DS + '.get(\'' + eval('obj.' + features[-1]) +
                     '\', 0) + obj.count')
            # Except if boolean
            except TypeError:
                exec(DS + '[' + str(eval('obj.' + features[-1])) + ']=' + DS + '.get(' +
                     str(eval('obj.' + features[-1])) + ', 0) + obj.count')
        return data

    @staticmethod
    def dict_to_matrix(data):
        # Set outer and inner keys
        outer_keys = sorted(data.keys())
        inner_keys_D = {}
        # Find all inner key values
        for o_key in outer_keys:
            for i_key in data[o_key]:
                inner_keys_D[i_key] = True
        inner_keys = sorted(inner_keys_D.keys())
        # Set matrix
        matrix = [[''] + inner_keys]
        for o_key in outer_keys:
            row = [o_key]
            for i_key in inner_keys:
                # If inner key is found for the outer key, set amount
                if i_key in data[o_key]:
                    row.append(data[o_key][i_key])
                # Otherwise inner key DNE for outer key, set to 0
                else:
                    row.append(0)
            matrix.append(row)
        return matrix

    @staticmethod
    def recurse_data(data, features, writer, prev=[], i=0, limit=2):
        if i == (len(features) - limit):
            matrix = Report.dict_to_matrix(data)
            # Write title by previous values
            writer.writerow(prev)
            # Write matrix rows
            for row in matrix:
                writer.writerow(row)
            # Write empty row
            writer.writerow([])
        else:
            for key in sorted(data.keys()):
                Report.recurse_data(data[key], features, writer, prev + [str(features[i]).title() + ': ' + str(key)],
                                     i+1, limit=limit)
        return True

    @staticmethod
    def generate(features, start=datetime.date(2015, 8, 31), end=datetime.date.today()):
        data = Report.prepare(features, start, end)
        if not os.path.isdir(PATH + '/reports/ridership/custom'):
            os.makedirs(PATH + '/reports/ridership/custom')
        writer = csv.writer(open(PATH + '/reports/ridership/custom/Ridership_' + '_'.join(features).title() +
                                 '.csv', 'w', newline=''), delimiter=',', quotechar='|')
        Report.recurse_data(data, features, writer)
        return True

