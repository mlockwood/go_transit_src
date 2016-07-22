from src.scripts.utils.IOutils import load_json, export_json


class DataModelTemplate(object):

    json_path = ''
    objects = {}

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k != 'self']
        self.set_objects()
        if 'set_object_attrs' in dir(self):
            self.set_object_attrs()

    def set_objects(self):
        try:
            self.__class__.objects[self.id] = self
        except KeyError:
            raise NotImplementedError('DataModelTemplate classes must define a set_objects object method if the ' +
                                      'object\'s primary key is not `id`.')

    @classmethod
    def load(cls):
        load_json(cls.json_path, cls)
        if 'set_class_vars' in dir(cls):
            cls.set_class_vars()

    @classmethod
    def export(cls):
        export_json(cls.json_path, cls)

    @classmethod
    def print_stats(cls, view=10):
        print(cls.__name__, 'has a total of', len(cls.objects), 'objects.')
        index = len(cls.objects) if len(cls.objects) < view else view
        for key in list(cls.objects.keys())[:view]:
            print('\t', key, cls.objects[key].__dict__)