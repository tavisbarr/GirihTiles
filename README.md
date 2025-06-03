
# Girih Tiles

This repository contains Python FreeCAD scripts for constructing the five [Girih Tiles](https://en.wikipedia.org/wiki/Girih_tiles).  This tile system was developed in 13th Century Persia and is widely seen in Islamic architecture, most famously at [the Darb-e Imam shrine in Isfahan](https://en.wikipedia.org/wiki/Darb-e_Imam).  The religious significance of this tile pattern is that in its five shapes it produces infinite complexity and is therefore suggestive of the divine.  This pattern also influenced [Jali design](https://en.wikipedia.org/wiki/Jali) in Mughlai Indian architecture. As an aperiodic tile pattern, it is a mathematical precursor by several hundred years to [Penrose Tiling](https://en.wikipedia.org/wiki/Penrose_tiling), which, like the Girih tiling system, forms a quasi-cristalline structure. 

Included are five Python scripts, each of which can be run in the Python console in FreeCAD (or potentially just with the FreeCAD package in a Python interpreter if one does not need a visual rendition) to create 3D models of the tiles.  The main configuration parameters are common across the five files, but are included separately in each file so that each file can be run independently as a script. Therefore, if one wishes to change the parameters (typically one would want to use the same parameters for all five tiles), then one needs to change the relevant lines in all five files, though this is really just a matter of copying and pasting.

The parameters are as follows:
  - *side*: The length of each side of a tile.  The tiles should all have sides of the same length so that they can be aligned.  By default this length is two inches.
  - *THICK*: The total thickness of a tile including the filigree lines. Default is 0.3 inches, which includes roughly a standard tile thickness of 0.25 inches plus 0.05 inches for the filigree embossment.
  - *RECESS*: The amount by which the base tile is recessed from the filigree. In other words, the visible depth of the filigree embossment.
  - *EMBEDDING*: The depth at which the filigree lines are embedded into the main tile.  Embedding the lines may aid in getting the two pieces to adhere if they are printed separately; also it creates potential depth of the color pattern in case of scratching.
  - *WIDTH*: This is the width of the filigree lines.  The default is 0.25 inches.
  - *MOLD BUFFER*: This is the minimum thickness of the mold object (more on this below) -- in other words the buffer distance between the edge of the tile and the edge of the mold.  The default is 0.25 inches.
  - *LINE_COLOR*: The color of the filigree lines in RGB format.  The RGB numbers are given as a decimal triple.
  - *TILE_COLOR*: The color of the base tile in RGB format.  The RGB numbers are given as a decimal triple.  Note that these two color markings will generally not survive the export from FreeCAD to whatever slicer you are using to print, so they are mainly useful for visualization within the CAD program.
  
  When run, each script produces three objects:
   - The base tile is the tile with the indentation for the filigree lines (if EMBEDDING is a positive number).
   - The filigree is the pattern of lines covering the tile
   - In addition, there is a mold built in case one wishes to print the mold in a firm material and use it to mold tiles from a malleable material (such as ceramic). The tiles are made visible by default but the mold is made invisible by default.  Keep in mind that ceramic will shrink roughly 10 percent in each dimension through the drying process (depending on the clay) so the dimensions of the mold would need to be sized accordingly.
   
From FreeCAD, these tiles (or the mold) can be exported, generally to either STL or 3MF format, and either sent to a 3D printing service or loaded into a slicer for printing.  If one wishes to print the tiles in full color (rather expensive), then one can select both the base tile and the filigree together and export them to a 3MF format and simply print it. Far cheaper would be to print the two pieces separately as single-color objects, for which the base tile and the filigree can be selected and exported separately to either 3MF or STL format.  There are numerous other export options in FreeCAD, but these two formats would be the most common ones both for loading into a slicer and for sending to a 3D printing service.
