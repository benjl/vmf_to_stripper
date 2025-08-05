## Intro
This tool lets you add triggers to a map without recompiling it by using Lumper's stripper config feature.

**Caveats:** 
- The triggers must be axis-aligned bounding boxes - if you need a specially shaped trigger, you will still need to recompile the map and add it in yourself  
- The triggers must have unique targetnames  
- The resulting triggers will not be visible in-game when using `showtriggers_toggle`. You can give an indication to their location, however, by adding the model keyvalue to the entities in the stripper config or afterwards in the map with Lumper

## Installation:
You will need [Python 3](https://www.python.org/downloads/) installed to run the script.  
Then, in a directory of your choice, run `git clone https://github.com/benjl/vmf_to_stripper.git --recursive`

## Directions
1. Decompile the map you would like to add triggers to  
2. In hammer, add your triggers to the map  
3. Select all your triggers and press "Create Prefab" on the right hand side  
4. Drag your vmf file onto start.bat, or run vmf_to_stripper in the command line with the new vmf you have created as the argument, something like this: `python vmf_to_stripper.py extra_added_triggers.vmf`  
5. Open the bsp of your map in [Lumper](https://github.com/momentum-mod/lumper)
6. Go to Jobs > + > Stripper (File) and select `stripper_output.cfg` from the vmf_to_stripper directory
7. Press Run at the bottom of the left hand column
8. Save the map
