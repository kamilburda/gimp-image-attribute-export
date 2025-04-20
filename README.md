# Image Attribute Export Plug-in for GIMP

This [GIMP](https://www.gimp.org/) plug-in exports various attributes from the specified image into an XML, JSON or YAML file. Attributes include (among many others) image name, width, height, a list of layers, layer effects, channels, paths and their attributes (width, height, offsets, visibility, color tags, ...).

[**Download latest release**](https://github.com/kamilburda/gimp-image-attribute-export/releases)


## Installation

GIMP 3.0.0 or later is required.

1. In GIMP, locate the folder containing GIMP plug-ins - open GIMP and go to Edit → Preferences → Folders → Plug-Ins.
2. Copy the `image-attribute-export` folder inside one of the folders identified in step 1.

For Windows, make sure you have GIMP installed with support for Python plug-ins.


## Usage

Simply export an image like you normally would (`File → Export...`) and replace the file extension at the top of the export dialog with `xml`, `json`, or `yaml`. Alternatively, you may select one of these file extensions at the bottom of the export dialog.

To export the attributes programmatically (e.g. from the Python-Fu Console), the file export procedures are `file-xml-export`, `file-json-export` and `file-yaml-export`.


## Example of image attributes in the JSON format

Only a select few entries are shown for brevity.

```
{
    "image": {
        "name": "loading_screen_template.xcf",
        "width": 1024,
        "height": 512,
        ...
        "layers": [
            {
                ...
                "name": "Frames",
                "visible": True,
                "width": 688,
                "height": 386,
                "opacity": 100.0,
                "offsets": [
                    168,
                    30
                ],
                ...
                "children": [
                    {
                        ...
                        "name": "top-frame",
                        ...
                    },
                    {
                        ...
                        "name": "bottom-frame",
                        ...
                    }
                ]
            },
            {
                ...
                "name": "main-background",
                ...
            }
        ],
        "channels": [],
        "paths": []
    }
}
```


## License

This plug-in is licensed under the [BSD 3-Clause](LICENSE) license.
