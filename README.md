# workshop_lua_generator
A script written in Python that generates a GarrysMod server's `workshop.lua` (found in /lua/autorun/server)  automatically from their collection URL.

Server's use this file to send their clients the workshop addons that are necessary to play on their server.

### Requirements: 
* Python 3.x (*might* work with 2.7.x)
   * Beautiful Soup 4 - `pip install bs4`

### Arguments When Ran Directly:
* -o, --output_dir: The output directory to send the file to. Defaults to current working directory.
    
* -f, --filename: The filename to write to. Defaults to `workshop.lua`.
    
* -i, --id: The collection ID to replicate in the generated LUA file. Defaults to my favorite server's collection.
    
* -q, --quiet: Want this darn script to shutup (no output)? Set this flag!


### Usage in Another Script:
* Importing:
  ```python
  from workshop_generator import WorkshopGenerator
  ```

* The most simple case:
  ```python
  wg = WorkshopGenerator(collection_id=123456789)
  
  wg.write_workshop_file()
  ```

* A more involved case:
  ```python
  wg = WorkshopGenerator()
  
  wg.configure(output_directory='/path/to/output/', collection_id=123456789)
  
  first_collection = wg.get_workshop_collection()
  
  print(collection['name'], collection['url'])
  
  second_collection = wg.get_workshop_collection(987654321)
  
  wg.write_workshop_file(collection=first_collection, filename='renamed.lua')
  
  ...
  
  ```
The only thing that the `WorkshopGenerator` requires is the `collection_id`. 
The filename defaults to `workshop.lua`, and the output directory to the current working directory.

An example output file can be found [here](example_output/workshop.lua)!
