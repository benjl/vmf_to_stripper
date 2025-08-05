import sys
sys.path.append('./pyvmf/src')
from PyVMF import *

# Because dealing there is too much dang string concatenation going on already
def quote(s):
    return '"' + str(s) + '"'

def vtx_to_str(vec):
    return f'{vec.x} {vec.y} {vec.z}'

def list_to_str(lst):
    return f'{lst[0]} {lst[1]} {lst[2]}'

if len(sys.argv) < 2:
    print('No file specified')
    sys.exit(0)
    
print(f'Input file: {sys.argv[1]}')
v = load_vmf(sys.argv[1])

add_entries = []
modify_entries = []

# Add a logic_auto at the position of the first entity
first_center = v.get_entities(include_solid_entities=True)[0].export()[1]['origin']
auto = ['"classname" "logic_auto"', '"spawnflags" "0"', '"targetname" "mmod_added_triggers_ported_by_tools"', '"origin" ' + quote(vtx_to_str(first_center))]
add_entries.append(auto)

brush_ents = 0

for ent in v.get_entities(include_solid_entities=True):
    if len(ent.solids) == 0: # Not a brush entity
        continue

    brush_ents += 1
    solid = ent.solids[0]
    center = solid.center_geo
    
    # Add entity information
    if len(ent.connections) == 0:
        conns = []
    else:
        conns = ent.connections[0].export()[1]
    attrs = ent.export()

    add = []
    add.append('"classname" ' + quote(attrs[0]['classname']))
    add.append('"origin" ' + quote(vtx_to_str(center)))
    add.append('"targetname" ' + quote(attrs[1]['targetname'] + '_ported_by_tools'))
    for att in attrs[1]:
        if att.lower() not in ['origin', 'targetname']:
            add.append(quote(att) + ' ' + quote(attrs[1][att]))
    for c in conns:
        output,info = conns[c].split(',')
        add.append(quote(output) + ' ' + quote(info.replace('\x1b', ',')))
    add_entries.append(add)
    
    # Get the bounding box for this trigger
    rel_mins = [
    solid.get_axis_extremity(x=False).x-center.x, 
    solid.get_axis_extremity(y=False).y-center.y, 
    solid.get_axis_extremity(z=False).z-center.z]

    rel_maxs = [
    solid.get_axis_extremity(x=True).x-center.x,
    solid.get_axis_extremity(y=True).y-center.y,
    solid.get_axis_extremity(z=True).z-center.z]
       
    # This is icky, but currently the only known way to use mins and maxs on most triggers
    # is to add these inputs to a logic_auto for each trigger you want to add
    modify_entries.append('"OnMapSpawn" "' + attrs[1]["targetname"] + '_ported_by_tools,AddOutput,solid 2,0.5,1"')
    modify_entries.append('"OnMapSpawn" "' + attrs[1]["targetname"] + '_ported_by_tools,AddOutput,mins ' + list_to_str(rel_mins) + ',1,1"')
    modify_entries.append('"OnMapSpawn" "' + attrs[1]["targetname"] + '_ported_by_tools,AddOutput,maxs ' + list_to_str(rel_maxs) + ',1,1"')

print(f'{brush_ents} brush entities found')
    
# Generate stripper config
with open('stripper_output.cfg', 'w') as f:
    for add_entry in add_entries:
        f.write('add:\n{\n')
        for kv in add_entry:
            f.write('\t' + kv + '\n')
        f.write('}\n\n')
    
    f.write('modify:\n{\n\tmatch:\n\t{\n\t\t"classname" "logic_auto"\n\t\t"targetname" "mmod_added_triggers_ported_by_tools"\n\t}\n')
    f.write('\tinsert:\n\t{\n')
    for modify_entry in modify_entries:
        f.write('\t\t' + modify_entry + '\n')
    f.write('\t}\n}')

print('Wrote config to stripper_output.cfg')