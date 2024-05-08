# RLG Vertex Tool
RLG Vertex Tool allows you to read data and extract vertices from rlg files. It also allows you to edit the files and make some very basic mods.  
You can extract all the vertices of a .rlg into an .obj, but no faces, edges or anything else.

## How to make your 3d model mod with this tool:
1. Put the .rlg file you want to edit in the rlg folder
2. Run the script and use the e command to generate an .obj file containing the vertices
3. In the output folder you'll find the newly created .obj file, import it in a 3D model editor (such as blender). Here you can move the vertices around, but you **cannot** add or delete any.
4. Once you're done with the edit, you can export the .obj file into the obj folder (make sure to name it the same way as the file that was outputed by the script)
5. Run the script and use the g command to generate a new .rlg (the original .rlg still needs to be in the rlg folder)
6. Now you'll find your new rlg in the output folder. Enjoy!
