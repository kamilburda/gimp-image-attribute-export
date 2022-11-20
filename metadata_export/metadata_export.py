#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, print_function, unicode_literals

import gimp
from gimp import pdb
import gimpfu
import gimpenums

import io
import sys


try:
  import json
except ImportError:
  _json_module_loaded = False
else:
  _json_module_loaded = True


try:
  from xml.etree import ElementTree as ET
except ImportError:
  _xml_module_loaded = False
else:
  _xml_module_loaded = True


import collections


_TEXT_ENCODING = 'utf-8'
_INDENT = 4

_image_base_types = {
  getattr(gimpenums, base_type): base_type
  for base_type in ['RGB', 'GRAY', 'INDEXED']
}


def save_xml(image, drawable, filepath, filename):
  metadata = _get_metadata(image)
  
  root = ET.Element('image')
  root.text = '\n' + ' ' * _INDENT
  
  elements = [[key, value, root, 1, False] for key, value in metadata['image'].items()]
  elements[-1][-1] = True
  
  while elements:
    key, value, parent, depth, is_last = elements.pop(0)
    
    if isinstance(value, (tuple, list, dict)):
      element = ET.SubElement(parent, key)
      
      child_depth = depth + 1
      element.text = '\n' + ' ' * child_depth * _INDENT
      if not is_last:
        element.tail = '\n' + ' ' * depth * _INDENT
      else:
        element.tail = '\n' + ' ' * (depth - 1) * _INDENT
      
      if isinstance(value, dict):
        for child_key, child_value in value.items():
          elements.append([child_key, child_value, element, child_depth, False])
      else:
        for child_value in value:
          elements.append(['item', child_value, element, child_depth, False])
      elements[-1][-1] = True
    else:
      element = ET.SubElement(parent, key)
      element.text = str(value) if value is not None else ''
      
      if not is_last:
        element.tail = '\n' + ' ' * depth * _INDENT
      else:
        element.tail = '\n' + ' ' * (depth - 1) * _INDENT
  
  tree = ET.ElementTree(root)
  tree.write(filepath, encoding=_TEXT_ENCODING, method='html')


def save_json(image, drawable, filepath, filename):
  metadata = _get_metadata(image)
  
  with io.open(filepath, 'w', encoding=_TEXT_ENCODING) as f:
    # Workaround for Python 2 code to properly handle Unicode strings
    data = json.dumps(metadata, f, indent=4, ensure_ascii=False)
    f.write(unicode(data))


def _get_metadata(image):
  metadata = collections.OrderedDict()
  
  metadata['image'] = collections.OrderedDict()
  metadata['image']['name'] = image.name
  metadata['image']['width'] = image.width
  metadata['image']['height'] = image.height
  metadata['image']['base_type_name'] = _image_base_types[image.base_type]
  metadata['image']['base_type_value'] = image.base_type
  metadata['image']['precision'] = image.precision
  metadata['image']['resolution'] = image.resolution
  metadata['image']['unit'] = image.unit
  
  if hasattr(image, 'colormap'):
    metadata['image']['colormap'] = repr(image.colormap)
  
  metadata['image']['active_channel'] = _get_item_name(image.active_channel)
  metadata['image']['active_drawable'] = _get_item_name(image.active_drawable)
  metadata['image']['active_layer'] = _get_item_name(image.active_layer)
  metadata['image']['active_vectors'] = _get_item_name(image.active_vectors)
  
  _fill_metadata_from_items(metadata, image, 'layers')
  _fill_metadata_from_items(metadata, image, 'channels')
  _fill_metadata_from_items(metadata, image, 'vectors')
  
  return metadata


def _fill_metadata_from_items(metadata, image, item_type):
  attributes_to_exclude = [
    'ID', 'image', 'color', 'colour', 'children', 'layers', 'mask', 'parent', 'strokes']
  
  metadata['image'][item_type] = []
  items_and_item_metadata = []
  
  for item in getattr(image, item_type):
    item_metadata = collections.OrderedDict()
    metadata['image'][item_type].append(item_metadata)
    items_and_item_metadata.append((item, item_metadata))
  
  while items_and_item_metadata:
    item, item_metadata = items_and_item_metadata.pop(0)
    
    item_metadata.update(_get_item_metadata(item, attributes_to_exclude, item_metadata))
    
    if hasattr(item, 'mask') and item.mask is not None:
      item_metadata['mask'] = _get_item_metadata(item.mask, attributes_to_exclude)
    
    if pdb.gimp_item_is_group(item):
      item_metadata['children'] = []
      
      for item in item.children:
        child_metadata = collections.OrderedDict()
        item_metadata['children'].append(child_metadata)
        items_and_item_metadata.append((item, child_metadata))


def _get_item_metadata(item, attributes_to_exclude, metadata_dict=None):
  if metadata_dict is None:
    metadata_dict = collections.OrderedDict()
  
  metadata_dict['name'] = item.name
  metadata_dict.update(_get_item_attributes(item, attributes_to_exclude))
  if hasattr(item, 'color'):
    metadata_dict['color'] = str(item.color)
  metadata_dict['color_tag'] = pdb.gimp_item_get_color_tag(item)
  metadata_dict['expanded'] = bool(pdb.gimp_item_get_expanded(item))
  
  return metadata_dict


def _get_item_attributes(item, attrs_to_exclude):
  item_attributes = {}
  valid_types = (
    int, float, bool, str, bytes, unicode, type(None), tuple, list, dict, collections.OrderedDict)
  
  for attr_name in dir(item):
    try:
      attr = getattr(item, attr_name)
    except Exception:
      attr = None
    
    if (not attr_name.startswith('__')
        and not callable(attr)
        and isinstance(attr, valid_types)
        and attr_name not in attrs_to_exclude):
      item_attributes[attr_name] = attr
  
  return item_attributes


def _get_item_name(item):
  return item.name if item is not None else item


def register_save_handler(file_ext):
  gimp.register_save_handler('file-metadata-{}-save'.format(file_ext), file_ext, '')


_save_params = [
    (gimpfu.PF_IMAGE, 'image', 'Input image', None),
    (gimpfu.PF_DRAWABLE, 'drawable', 'Drawable to export (ignored)', None),
    (gimpfu.PF_STRING, 'filename', 'The name of the file to export the image in', None),
    (gimpfu.PF_STRING, 'raw-filename', 'The name of the file to export the image in', None),
]


if _xml_module_loaded:
  gimpfu.register(
    proc_name='file-metadata-xml-save',
    blurb='Saves image metadata as XML',
    help='',
    author='Kamil Burda',
    copyright='Kamil Burda',
    date='2022',
    label=None,
    imagetypes='*',
    params=_save_params,
    results=[],
    menu='<Save>',
    on_query=lambda: register_save_handler('xml'),
    function=save_xml)


if _json_module_loaded:
  gimpfu.register(
    proc_name='file-metadata-json-save',
    blurb='Saves image metadata as JSON',
    help='',
    author='Kamil Burda',
    copyright='Kamil Burda',
    date='2022',
    label=None,
    imagetypes='*',
    params=_save_params,
    results=[],
    menu='<Save>',
    on_query=lambda: register_save_handler('json'),
    function=save_json)


if __name__ == '__main__':
  gimpfu.main()
