

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('go', 'templates'))

template = env.get_template('timetable.html')
template.render()
