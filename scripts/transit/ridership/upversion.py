"""
# IN READ SHEET
# Columns (for older versions)
            if columns == True:
                i = 3
                while i < len(row):
                    exec('self.' + str(row[0]).lower() + '_' + str(i) +'=\'' +
                         str(row[i]) + '\'')
                    if (not self.start_shift and not self.time_key and
                        row[0].lower() != 'start'):
                        try:
                            self.time_key = int(re.sub(':', '', row[i]))
                        except:
                            pass
                    i += 1


# Rewrite files of lower versions
        if self.pvn == '2' or self.pvn == '1' or self.pvn == '3':
            # Convert metadata Dictionary to ordered List
            self.meta_L = []
            for index in sorted(Sheet.order.keys()):
                if Sheet.order[index] in meta_D:
                    self.meta_L.append([Sheet.order[index].title(),
                                         meta_D[Sheet.order[index]]])
            # Send to have file rewritten
            Sheet.rewrite[self] = True
"""

@staticmethod
def write_sheets():
    # Define sheet names

    for date in Sheet.structure:
        for schedule in Sheet.structure[date]:
            i = 0
            for time in sorted(Sheet.structure[date][schedule].keys()):
                if time == 0:
                    print('Please examine the time for', date,
                          'for all sheets with a schedule of', schedule)
                Sheet.sheet_names[(date[0], date[1], date[2], schedule,
                                   time)] = 'S' + str(schedule) + chars[i]
                i += 1

    # Write each sheet to file
    for obj in Sheet.rewrite:
        obj.sheet = Sheet.sheet_names[(obj.year, obj.month, obj.day,
                                        obj.schedule, obj.time_key)]
        writer = obj.set_writer()
        writer.writerow(['METADATA'])
        obj.meta_L[Sheet.index][1] = obj.sheet
        for row in obj.meta_L:
            writer.writerow(row)
        writer.writerow([])
        writer.writerow(['DATA'])
        writer.writerow(['Boarding', 'Time', 'Count', 'Destination'])
        for entry in obj.entries:
            writer.writerow(entry)
    return True

def set_writer(self):
    date = datetime.datetime(int(self.year), int(self.month),
                             int(self.day))
    directory = (System.path + '/reports/ridership/formatted/' +
        date.strftime('%Y_%m') + '/' + date.strftime('%y%m%d'))
    if not os.path.exists(directory):
        os.makedirs(directory)
    writer = csv.writer(open(directory + '/' + date.strftime('%y%m%d') +
        '_' + self.sheet + '.csv', 'w', newline=''), delimiter=',',
        quotechar='|')
    return writer

def set_1_and_2_records(self, row, direction):
    if row[0] == 'Return':
        direction = '2'
        return direction
    i = 3
    while i < len(row):
        if re.sub(' ', '', row[i]):
            # Set time base
            # Version 2 time
            if self._pvn == '2':
                if direction == '1':
                    time = eval('self._depart_' +
                        self._direction_2[-2:].lower() + '_' + str(i))
                    if (i == 3 and self._start_3 == '1J' and not
                        self._depart_mh_3):
                        if self._schedule == '3':
                            time = '640'
                elif direction == '2':
                    time = eval('self._depart_' +
                        self._direction_1[-2:].lower() + '_' + str(i))
                    if (i == 3 and self._start_3 == '1J' and not
                        self._depart_wz_3):
                        if self._schedule == '2':
                            time = '650'
                        elif self._schedule == '3':
                            time = '710'
            # Version 1 time
            elif self._pvn == '1':
                time = eval('self._time_' + str(i))
            # Modify time to actual stop
            time = re.sub(':', '', time)
            dt = datetime.datetime(int(self._year), int(self._month),
                int(self._day), int(time[:-2]), int(time[-2:]))
            if self._version == '1' and direction == '2':
                dt = dt + datetime.timedelta(0, 60 * 30)
            time = dt + datetime.timedelta(0, 60 * int(eval(
                'st.Stop.obj_map[row[1].upper()]._historic_time_' +
                str(direction))))
            # Add (time, on|off) to temp with [stop, count]
            self._temp[(time.strftime('%H%M'), row[2])] = [row[1],
                                                           int(row[i])]
        i += 1
    return direction

def upversion_1_and_2(self):
    stack = {}
    cur_key = 0
    new_key = 0
    final = {}
    # record is (time, on|off)
    for entry in sorted(self._temp.keys()):
        if entry[1] == 'On':
            # stack is [on_stop, time, count]
            stack[new_key] = [self._temp[entry][0], entry[0],
                              self._temp[entry][1]]
            new_key += 1
        elif entry[1] == 'Off':
            # final is (on_stop, time, count, off_stop) = True
            count = self._temp[entry][1]
            while count > 0:
                if stack[cur_key][2] > count:
                    final[(stack[cur_key][0], stack[cur_key][1], count,
                           self._temp[entry][0])] = True
                    stack[cur_key][2] -= count
                    count = 0
                else:
                    final[(stack[cur_key][0], stack[cur_key][1],
                        stack[cur_key][2], self._temp[entry][0])
                        ] = True
                    count -= stack[cur_key][2]
                    del stack[cur_key]
                    cur_key += 1
    for entry in sorted(final.keys(), key=lambda x:x[1]):
        self._entries.append(list(entry))
    return True