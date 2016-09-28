from lxml import etree


def string_with_doctype(tree):
    return etree.tostring(tree, method='html', pretty_print=True, xml_declaration=False, doctype="<!DOCTYPE HTML>")


def add_head(title, css=[]):
    tree = etree.Element('head', lang="en")
    tree.append(etree.Element('meta', charset="UTF-8"))
    tree.append(etree.Element('title'))
    tree[1].text = title
    tree.append(add_style_link(href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.2/css/bootstrap.min.css",
                               integrity="sha384-y3tfxAZXuh4HwSYylfB+J125MxIs6mR5FOHamPBG064zB+AFeWH94NdvaCBm8qnd",
                               crossorigin="anonymous")
                   )
    for style in css:
        tree.append(add_style_link(**style))
    return tree


def add_style_link(href, rel="stylesheet", integrity=None, crossorigin=None):
    link = etree.Element('link', rel=rel, href=href)
    if integrity:
        link.set('integrity', integrity)
    if crossorigin:
        link.set('crossorigin', crossorigin)
    return link


def add_class(element, class_name=None):
    if class_name:
        element.set('class', class_name)
    return element


def add_id(element, id_name=None):
    if id_name:
        element.set('id', id_name)
    return element


def add_type(element, type_name=None):
    if type_name:
        element.set('type', type_name)
    return element


def add_div(class_name=None):
    return add_class(element=etree.Element('div'), class_name=class_name)


def add_image(src, class_name=None, id_name=None):
    return add_id(add_class(etree.Element('img', src=src), class_name=class_name), id_name=id_name)


def add_pdf(src, width="400", height="300", class_name=None, id_name=None):
    return add_id(add_class(add_type(etree.Element('embed', src=src, width=width, height=height),
                                     type_name="application/pdf"),
                            class_name=class_name),
                  id_name=id_name)


def add_route_logo(route):
    tree = etree.Element('div')
    tree.append(add_image('../../img/route{}_logo.jpg'.format(route), class_name="imgHeader"))
    return tree


def add_route_map(route):
    tree = etree.Element('div')
    tree.append(add_pdf('../../pdf/route{}_map.pdf'.format(route), width="1680", height="700"))
    return tree