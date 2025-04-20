#!/usr/bin/env python

import json
from xml.etree import ElementTree as ET

import gi
gi.require_version('Babl', '0.1')
from gi.repository import Babl
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import GObject

import procedure


_TEXT_ENCODING = 'utf-8'
_INDENT = 4


def file_xml_export(_proc, _run_mode, image, file, _options, _metadata, _config, _data):
  image_attributes = _get_image_attributes(image)

  root = ET.Element('image')
  root.text = '\n' + ' ' * _INDENT
  
  elements = [[key, value, root, 1, False] for key, value in image_attributes['image'].items()]
  elements[-1][-1] = True
  
  while elements:
    key, value, parent, depth, is_last = elements.pop(0)
    
    if isinstance(value, (tuple, list, dict)):
      element = ET.SubElement(parent, key)
      
      child_depth = depth + 1
      
      if not value:
        element.text = '\n' + ' ' * (child_depth - 1) * _INDENT
      else:
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

  filepath = file.get_path() if file.get_path() is not None else ''

  tree = ET.ElementTree(root)
  tree.write(filepath, encoding=_TEXT_ENCODING, method='html')


def file_json_export(_proc, _run_mode, image, file, _options, _metadata, _config, _data):
  attributes = _get_image_attributes(image)

  filepath = file.get_path() if file.get_path() is not None else ''

  with open(filepath, 'w', encoding=_TEXT_ENCODING) as f:
    json.dump(attributes, f, indent=_INDENT, separators=(',', ': '))


def file_yaml_export(_proc, _run_mode, image, file, _options, _metadata, _config, _data):
  list_item_str = '- '
  
  attributes = _get_image_attributes(image)
  data = ''
  
  elements = [[key, value, 0] for key, value in attributes['image'].items()]
  
  while elements:
    key, value, depth = elements.pop(0)
    
    if isinstance(value, (tuple, list, dict)):
      indent = ' ' * depth * _INDENT
      
      if key is not None:
        text = indent + '{}:'.format(key)
        
        if len(value) < 1:
          if isinstance(value, dict):
            text += ' {}'
          else:
            text += ' []'
        
        text += '\n'
        
        data += text
      else:
        data += indent + '{}item:\n'.format(list_item_str)
      
      if isinstance(value, dict):
        for child_key, child_value in reversed(value.items()):
          elements.insert(0, [child_key, child_value, depth + 1])
      else:
        for child_value in reversed(value):
          elements.insert(0, [None, child_value, depth])
    else:
      if isinstance(value, bool):
        text = 'true' if value else 'false'
      else:
        if value is not None:
          text = str(value)
          
          if not isinstance(value, (int, float)):
            text = "'" + text + "'"
        else:
          text = 'null'
      
      indent = ' ' * depth * _INDENT
      
      if key is not None:
        text = indent + '{}: {}\n'.format(key, text)
      else:
        text = indent + '{}{}\n'.format(list_item_str, text)
      
      data += text

  filepath = file.get_path() if file.get_path() is not None else ''

  with open(filepath, 'w', encoding=_TEXT_ENCODING) as f:
    f.write(data)


def _get_image_attributes(image: Gimp.Image):
  attributes = {}
  
  attributes['image'] = {}
  attributes['image']['name'] = image.get_name()
  attributes['image']['width'] = image.get_width()
  attributes['image']['height'] = image.get_height()
  attributes['image']['base_type'] = image.get_base_type().name
  attributes['image']['precision'] = image.get_precision().name
  attributes['image']['resolution'] = list(image.get_resolution()[1:])
  attributes['image']['unit'] = image.get_unit().get_name()
  
  if image.get_palette() is not None:
    attributes['image']['colormap'] = image.get_palette().get_colormap(Babl.format('RGB u8'))
  
  attributes['image']['selected_channels'] = _get_item_names(image.get_selected_channels())
  attributes['image']['selected_drawables'] = _get_item_names(image.get_selected_drawables())
  attributes['image']['selected_layers'] = _get_item_names(image.get_selected_layers())
  attributes['image']['selected_paths'] = _get_item_names(image.get_selected_paths())
  
  _fill_attributes_from_items(attributes, image, 'layers', lambda image_: image_.get_layers())
  _fill_attributes_from_items(attributes, image, 'channels', lambda image_: image_.get_channels())
  _fill_attributes_from_items(attributes, image, 'paths', lambda image_: image_.get_paths())
  
  return attributes


def _fill_attributes_from_items(attributes, image, item_type, get_items_func):
  attributes['image'][item_type] = []
  items_and_item_attributes = []
  
  for item in get_items_func(image):
    item_attributes = {}
    attributes['image'][item_type].append(item_attributes)
    items_and_item_attributes.append((item, item_attributes))
  
  while items_and_item_attributes:
    item, item_attributes = items_and_item_attributes.pop(0)
    
    item_attributes.update(_get_item_attributes(item, item_attributes))
    
    if item.is_group():
      item_attributes['children'] = []
      
      for item in item.get_children():
        child_attributes = {}
        item_attributes['children'].append(child_attributes)
        items_and_item_attributes.append((item, child_attributes))


def _get_item_attributes(item, attributes_dict=None):
  if attributes_dict is None:
    attributes_dict = {}

  attributes_dict['color_tag'] = item.get_color_tag().name
  attributes_dict['expanded'] = item.get_expanded()
  attributes_dict['is_group'] = item.is_group()
  attributes_dict['lock_content'] = item.get_lock_content()
  attributes_dict['lock_position'] = item.get_lock_position()
  attributes_dict['lock_visibility'] = item.get_lock_visibility()
  attributes_dict['name'] = item.get_name()
  attributes_dict['visible'] = item.get_visible()
  attributes_dict['type'] = type(item).__qualname__

  if isinstance(item, Gimp.Drawable):
    attributes_dict['bpp'] = item.get_bpp()
    attributes_dict['width'] = item.get_width()
    attributes_dict['height'] = item.get_height()
    attributes_dict['offsets'] = list(item.get_offsets()[1:])
    attributes_dict['has_alpha'] = item.has_alpha()
    attributes_dict['image_type'] = item.type().name

    attributes_dict['filters'] = []
    for drawable_filter in item.get_filters():
      attributes_dict['filters'].append({
        'blend_mode': drawable_filter.get_blend_mode().name,
        'name': drawable_filter.get_name(),
        'opacity': drawable_filter.get_opacity(),
        'operation_name': drawable_filter.get_operation_name(),
        'visible': drawable_filter.get_visible(),
        'parameters': {
          prop.name: _process_config_property(drawable_filter.get_config().get_property(prop.name))
          for prop in drawable_filter.get_config().list_properties()
        },
      })

  if isinstance(item, Gimp.Layer):
    attributes_dict['apply_mask'] = item.get_apply_mask()
    attributes_dict['blend_space'] = item.get_blend_space().name
    attributes_dict['composite_mode'] = item.get_composite_mode().name
    attributes_dict['composite_space'] = item.get_composite_space().name
    attributes_dict['edit_mask'] = item.get_edit_mask()
    attributes_dict['is_floating_sel'] = item.is_floating_sel()
    attributes_dict['lock_alpha'] = item.get_lock_alpha()
    attributes_dict['mode'] = item.get_mode().name
    attributes_dict['opacity'] = item.get_opacity()
    attributes_dict['show_mask'] = item.get_show_mask()

    if item.get_mask() is not None:
      attributes_dict['mask'] = _get_item_attributes(item.get_mask())

  if isinstance(item, Gimp.Channel):
    attributes_dict['color_rgba'] = list(item.get_color().get_rgba())
    attributes_dict['opacity'] = item.get_opacity()
    attributes_dict['show_masked'] = item.get_show_masked()

  if isinstance(item, Gimp.Path):
    attributes_dict['strokes'] = []

    stroke_ids = item.get_strokes()
    for stroke_id in stroke_ids:
      points = item.stroke_get_points(stroke_id)
      attributes_dict['strokes'].append({
        'id': stroke_id,
        'points_type': points[0].name,
        'points': points[1],
        'points_closed': points[2],
      })
  
  return attributes_dict


def _get_item_names(items):
  return [item.get_name() if item is not None else item for item in items]


def _process_config_property(prop):
  if isinstance(prop, Gegl.Color):
    return list(prop.get_rgba())
  elif isinstance(prop, GObject.GEnum):
    return prop.name
  elif isinstance(prop, (str, int, float, bool, type(None))):
    return prop
  else:
    return str(prop)


def _set_up_xml_format(proc):
  proc.set_extensions('xml')
  proc.set_format_name('XML')
  proc.set_handles_remote(True)


procedure.register_procedure(
  file_xml_export,
  procedure_type=Gimp.ExportProcedure,
  additional_init=_set_up_xml_format,
  menu_label='XML',
  documentation=(
    'Exports image attributes as XML (.xml)',
    'Exports image attributes as XML (.xml)',
  ),
  attribution=('Kamil Burda', '', '2022'),
)


def _set_up_json_format(proc):
  proc.set_extensions('json')
  proc.set_format_name('JSON')
  proc.set_handles_remote(True)


procedure.register_procedure(
  file_json_export,
  procedure_type=Gimp.ExportProcedure,
  additional_init=_set_up_json_format,
  menu_label='JSON',
  documentation=(
    'Exports image attributes as JSON (.json)',
    'Exports image attributes as JSON (.json)',
  ),
  attribution=('Kamil Burda', '', '2022'),
)


def _set_up_yaml_format(proc):
  proc.set_extensions('yaml')
  proc.set_format_name('YAML')
  proc.set_handles_remote(True)


procedure.register_procedure(
  file_yaml_export,
  procedure_type=Gimp.ExportProcedure,
  additional_init=_set_up_yaml_format,
  menu_label='YAML',
  documentation=(
    'Exports image attributes as YAML (.yaml)',
    'Exports image attributes as YAML (.yaml)',
  ),
  attribution=('Kamil Burda', '', '2022'),
)


procedure.main()
