import bpy
import imp   
 
curve_helper = imp.load_source('curve_helper','curve_helper.py')
material_helper = imp.load_source('material_helper','material_helper.py')
hull_maker = imp.load_source('hull_maker','hull_maker.py')

def make_chines(the_hull):

	#bpy.ops.transform.translate(value=(0.001, 0.001, 0.01))

	curve_helper.select_object(the_hull.hull_object,False)

	new_chine=hull_maker.chine_helper(the_hull)

	new_chine.rotation=[0,0,0]
	new_chine.offset=[0,0,0]
	new_chine.name="top"
	new_chine.make_chine()

	new_chine.rotation=[-25,0,0]
	new_chine.offset=[0,0,-0.5]
	new_chine.name="mid"
	new_chine.make_chine()

	new_chine.rotation=[45,0,0]
	new_chine.offset=[0,0,-0.5]
	new_chine.name="upper"
	new_chine.make_chine()

	new_chine.rotation=[-72,0,0]
	new_chine.offset=[0,0,-0.5]
	new_chine.name="low"
	new_chine.make_chine()

	new_chine.rotation=[-90,0,0]
	new_chine.offset=[0,0,0.3]
	new_chine.name="roof"
	new_chine.curve_width=-0.4
	new_chine.curve_length=13
	new_chine.symmetrical=False
	new_chine.make_chine()

the_hull=hull_maker.hull_maker()

the_hull.make_hull_object()

make_chines(the_hull)


# =========================================
# Make bulkheads
edge_offset=0.18
#hull_stations=[ -the_hull.hull_length/2+edge_offset, -1.7, -1.5, 0, 1.5, 1.7, the_hull.hull_length/2-edge_offset]


bulkhead_definitions=[]
for station_position in curve_helper.frange(-the_hull.hull_length/2+edge_offset,the_hull.hull_length/2-edge_offset,0.4):

	bulkhead_definitions.append([station_position,-0.9,False])

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()
	
the_hull.hull_object.hide_set(True)
the_hull.hull_object.hide_render=True

