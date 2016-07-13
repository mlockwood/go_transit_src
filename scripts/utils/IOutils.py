import json
import os


def csv_writer(path, file, matrix):
    if not matrix or len(matrix) == 1:
        return False

    # Set up directories and files
    if not os.path.isdir(path):
        os.makedirs(path)
    writer = open('{}/{}.csv'.format(path, file), 'w')

    # Write header
    writer.write('{}\n'.format(','.join(str(s) for s in matrix[0])))
    # Write sorted rows
    for row in sorted(matrix[1:]):
        writer.write('{}\n'.format(','.join(str(s) for s in row)))
    writer.close()
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
