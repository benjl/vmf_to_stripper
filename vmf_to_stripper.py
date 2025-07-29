import sys
sys.path.append('./pyvmf/src')
from PyVMF import *

def quote(s):
    return '"' + str(s) + '"'

def find_solid_id(v, search):
    for sol in v.get_solids():
        if sol.id == search:
            return sol

if len(sys.argv) < 2:
    print('No file specified.')
    sys.exit(0)
    
v = load_vmf(sys.argv[1])

add_entries = []
modify_entries = []

# Add a logic_auto at the position of the first entity
first_center = v.get_entities(include_solid_entities=True)[0].export()[1]['origin']
auto = ['"classname" "logic_auto"', '"spawnflags" "0"', '"targetname" "mmod_regen_triggers"', '"origin" ' + quote(' '.join([str(first_center.x), str(first_center.y), str(first_center.z)]))]
add_entries.append(auto)

for ent in v.get_entities(include_solid_entities=True):
    # Only care about regen triggers
    if ent.classname != 'trigger_multiple':
        continue
    
    # This assumes the solid is the next id in the vmf, no idea if that's true lol
    solid = find_solid_id(v, ent.id+1)
    center = solid.center_geo
    
    # Add entity information
    conns = ent.connections[0].export()[1]
    attrs = ent.export()
    add = []
    add.append('"classname" ' + quote(attrs[0]['classname']))
    add.append('"origin" ' + quote(' '.join([str(center.x), str(center.y), str(center.z)])))
    add.append('"spawnflags" ' + quote(attrs[1]['spawnflags']))
    add.append('"targetname" ' + quote(attrs[1]['targetname']))
    add.append('"StartDisabled" ' + quote(attrs[1]['StartDisabled']))
    add.append('"wait" ' + quote(attrs[1]['wait']))
    for c in conns:
        add.append(quote(c) + ' ' + quote(','.join(conns[c].split('\x1b'))))
    add_entries.append(add)
    # print(add)
    
    # Get the bounding box for this trigger
    abs_mins = [
    solid.get_axis_extremity(x=False).x, 
    solid.get_axis_extremity(y=False).y, 
    solid.get_axis_extremity(z=False).z]

    abs_maxs = [
    solid.get_axis_extremity(x=True).x,
    solid.get_axis_extremity(y=True).y,
    solid.get_axis_extremity(z=True).z]
    
    rel_mins = [int(abs_mins[0]-center.x), int(abs_mins[1]-center.y), int(abs_mins[2]-center.z)]
    rel_maxs = [int(abs_maxs[0]-center.x), int(abs_maxs[1]-center.y), int(abs_maxs[2]-center.z)]
    
    # We modify a logic_auto previously placed by the stripper config
    modify_entries.append('"OnMapSpawn" "' + attrs[1]["targetname"] + ',AddOutput,solid 2,0.5,1"')
    modify_entries.append('"OnMapSpawn" "' + attrs[1]["targetname"] + ',AddOutput,mins ' + str(rel_mins[0]) + ' ' + str(rel_mins[1]) + ' ' + str(rel_mins[2]) + ',1,1"')
    modify_entries.append('"OnMapSpawn" "' + attrs[1]["targetname"] + ',AddOutput,maxs ' + str(rel_maxs[0]) + ' ' + str(rel_maxs[1]) + ' ' + str(rel_maxs[2]) + ',1,1"')
    
    # print(modify_entries)

# Generate stripper config
with open('stripper_output.cfg', 'w') as f:
    for add_entry in add_entries:
        f.write('add:\n{\n')
        for l in add_entry:
            f.write('\t' + l + '\n')
        f.write('}\n\n')
    
    f.write('modify:\n{\n\tmatch:\n\t{\n\t\t"classname" "logic_auto"\n\t\t"targetname" "mmod_regen_triggers"\n\t}\n')
    f.write('\tinsert:\n\t{\n')
    for modify_entry in modify_entries:
        f.write('\t\t' + modify_entry + '\n')
    f.write('\t}\n}')