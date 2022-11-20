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
  import xml.etree
except ImportError:
  _xml_module_loaded = False
else:
  _xml_module_loaded = True


import collections


_TEXT_ENCODING = 'utf-8'

_image_base_types = {
  getattr(gimpenums, base_type): base_type
  for base_type in ['RGB', 'GRAY', 'INDEXED']
}


def save_xml(image, drawable, filepath, filename):
  pass


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
  
  layer_attributes_to_exclude = [
    'ID', 'image', 'children', 'layers', 'mask', 'parent']
  channel_attributes_to_exclude = [
    'ID', 'image', 'color', 'colour', 'children', 'layers', 'parent']
  
  metadata['image']['layers'] = []
  layers_and_layer_metadata = []
  
  for layer in image.layers:
    layer_metadata = collections.OrderedDict()
    metadata['image']['layers'].append(layer_metadata)
    layers_and_layer_metadata.append((layer, layer_metadata))
  
  while layers_and_layer_metadata:
    layer, layer_metadata = layers_and_layer_metadata.pop(0)
    
    layer_metadata['name'] = layer.name
    layer_metadata['type'] = 'item'
    layer_metadata.update(_get_item_attributes(layer, layer_attributes_to_exclude))
    
    if layer.mask:
      layer_metadata['mask'] = _get_item_attributes(layer.mask, channel_attributes_to_exclude)
      layer_metadata['mask']['color'] = str(layer.mask.color)
    else:
      layer_metadata['mask'] = None
    
    if pdb.gimp_item_is_group(layer):
      layer_metadata['type'] = 'group'
      layer_metadata['children'] = []
      
      for layer in layer.children:
        child_metadata = collections.OrderedDict()
        layer_metadata['children'].append(child_metadata)
        layers_and_layer_metadata.append((layer, child_metadata))
  
  return metadata


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
