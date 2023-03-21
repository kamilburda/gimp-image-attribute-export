Metadata Export for GIMP
========================

This [GIMP](https://www.gimp.org/) plug-in exports various metadata from the specified image into an XML, JSON or YAML file.

Metadata include image properties (e.g. name, dimensions) and a list of layers, channels, vectors and their properties (e.g. dimensions, position, visibility, color tags).

[**Download latest release**](https://github.com/kamilburda/gimp-metadata-export/releases)


Installation
------------

GIMP 2.10 is required.

1. In GIMP, locate the folder containing GIMP plug-ins - open GIMP and go to Edit → Preferences → Folders → Plug-Ins.
2. Copy the `metadata_export` folder inside one of the folders identified in step 1.

For Windows, make sure you have GIMP installed with support for Python scripting.

For Linux, make sure you use a GIMP installation bundled as Flatpak (which can be downloaded from the [official GIMP page](https://www.gimp.org/downloads/)) or AppImage.

For macOS, make sure you have Python 2.7 installed.


Usage
-----

Simply export an image like you normally would (File → Export...) and replace the file extension at the top of the export dialog with `xml`, `json`, or `yaml`. Alternatively, you may select one of these file extensions at the bottom of the export dialog.

To save the metadata programmatically (from the command line), use `file-metadata-xml-save`, `file-metadata-json-save` or `file-metadata-yaml-save` from the GIMP procedural database (PDB).


Example
-------

Below is an example of image metadata in the JSON format.
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
                "name": "Frames",
                "height": 386,
                ...
                "width": 688,
                ...
                "opacity": 100.0,
                ...
                "offsets": [
                    168,
                    30
                ],
                ...
                "children": [
                    {
                        "name": "top-frame",
                        ...
                    },
                    {
                        "name": "bottom-frame",
                        ...
                    }
                ]
            },
            {
                "name": "main-background",
                ...
            }
        ],
        "channels": [],
        "vectors": []
    }
}
```


Support
-------

You can report issues, ask questions or request new features on the [GitHub issues page](https://github.com/kamilburda/gimp-metadata-export/issues).


License
-------

This plug-in is licensed under the [BSD 3-Clause](LICENSE) license.
