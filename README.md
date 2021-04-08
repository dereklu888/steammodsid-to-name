# steammodsid-to-name
A simple script that outputs the game name, mod name, and any rough details of the folders in the your Steam workshop content folder (usually "C:/.../Steam/steamapps/workshop/content/").  

Specifically, for each game ID folder, this script outputs the game name, and for each mod ID folder in that game ID folder, the script then outputs the mod name and any mod details available like file size or date updated.  

Running the script without any other commands loops over all game folders in "C:/Program Files (x86)/Steam/steamapps/workshop/content/". However, with parameters, you can change the path, whether you want to only identify and game ID folder or mod ID folder, or just a game or mod ID.