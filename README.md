# workshop_lua_generator
A script written in Python that generates a GarrysMod server's `workshop.lua` (found in /lua/autorun/server)  automatically from their collection URL.

Server's use this file to send their clients the workshop addons that are necessary to play on their server.

Requirements: 
* Python 3.x (probably, *might* work with 2.7.x)
   * Beautiful Soup 4 - `pip install bs4`

### Arguments:
* -o, --output_dir: The output directory to send the file to. Defaults to current working directory.
    
* -f, --filename: The filename to write to. Defaults to "workshop.lua".',
    
* -i, --id: The collection ID to replicate in the generated LUA file. Defaults to my favorite server's collection.
    
* -q, --quiet: Want this darn script to shutup (no output)? Set this flag!

An example output file can be found [here](example_output/workshop.lua)!
