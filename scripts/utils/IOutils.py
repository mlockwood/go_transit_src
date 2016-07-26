import json
import os
import re


def set_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return True


def load_json(file, cls):
    with open(file, 'r') as infile:
        [cls(**obj) for obj in json.load(infile)]


def export_json(file, cls):
    with open(file, 'w') as outfile:
        if 'get_json' in dir(cls):
            json.dump(list(cls.objects[o].get_json() for o in sorted(cls.objects.keys())), outfile, indent=4,
                      sort_keys=True)
        else:
            json.dump(list(cls.objects[o].__dict__ for o in sorted(cls.objects.keys())), outfile, indent=4,
                      sort_keys=True)


def json_to_txt(json_file, txt_file, header, order=None, booleans=True):
    writer = open(txt_file, 'w')
    writer.write('{}\n'.format(','.join(header)))
    with open(json_file, 'r') as infile:
        for obj in json.load(infile):

            # If no order was provided use alphabetical key order
            if not order:
                order = []
                for key in sorted(obj.keys()):
                    order.append(key)
                writer.write('{}\n'.format(','.join(str(s) for s in order)))

            # Write row values
            row = []
            for key in order:
                row += [obj[key]] if booleans or not isinstance(obj[key], bool) else [int(obj[key])]
            writer.write('{}\n'.format(','.join(str(s) for s in row)))

    return True


def txt_to_json(txt_file, json_file):
    reader = open(txt_file, 'r')
    rows = []
    for row in reader:
        row = row.rstrip()
        rows.append(re.split(',', row))
    reader.close()

    data = []
    for row in rows[1:]:
        data.append(dict((k, v) for k, v in zip(rows[0], row)))

    with open(json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

    return True


def txt_writer(matrix, file):
    if not matrix or len(matrix) == 1:
        return False

    writer = open(file, 'w')

    # Write header
    writer.write('{}\n'.format(','.join(str(s) for s in matrix[0])))
    # Write rows
    for row in sorted(matrix[1:]):
        writer.write('{}\n'.format(','.join(str(s) for s in row)))
    writer.close()
    return True
