# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy 
import math
from math import radians, degrees

from ..hullgen import curve_helper
from ..hullgen import material_helper
from ..hullgen import curve_helper
from ..hullgen import chine_helper
from ..hullgen import bulkhead

class hull_maker:
    hull_length=11.4
    hull_width=3.9
    hull_height=3.6
    hull_name="hull_object"
    hull_object=None

    longitudal_list=None
    longitudal_slicer_list=None

    bulkheadlist=[]

    #bool_correction_offset=[ 0.0011, 0.0012, 0.0013 ]
    bool_correction_offset=[ 0.00, 0.00, 0.00 ]

    chine_list=None

    def __init__(self,length=11.4,width=3.9,height=3.6):
        self.hull_height=height
        self.hull_length=length
        self.hull_width=width
        chine_list=list()

        self.longitudal_list=list()
        self.longitudal_slicer_list=list()



    def make_bool_cube(self,name,location=(0,0,0),size=(1,1,1)):

        curve_helper.find_and_remove_object_by_name(name)

        # Booleans behave really strange if origin is 0,0,0 - this works
        #bpy.ops.mesh.primitive_cube_add(size=1.0,enter_editmode=False, location=(0.02, 0.02, 0.02))
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(self.bool_correction_offset[0]+location[0], self.bool_correction_offset[1]+location[1], self.bool_correction_offset[2]))

        new_object=bpy.context.view_layer.objects.active

        bpy.ops.transform.resize(value=size)
        bpy.ops.object.transform_apply(scale=True,location=False)

        new_object.name=name

        return new_object

    def make_hull_object(self):
        self.hull_object=self.make_bool_cube(self.hull_name,size=(self.hull_length, self.hull_width, self.hull_height))

        material_helper.assign_material(self.hull_object,material_helper.get_material_hull())

        return self.hull_object

    def make_bulkheads(self,bulkhead_definitions):
        for station_position in bulkhead_definitions:
            bh=bulkhead.bulkhead(self,station_position[0])
            bh.make_bulkhead(station_position[2])

            # If it's not watertight - there is a void in middle
            if station_position[2]==False:
                material_helper.assign_material(bh.bulkhead_void_object,material_helper.get_material_bool())
                
                if station_position[1]!=False:
                    bh.move_verts_z(bh.bulkhead_void_object,station_position[1])

            self.bulkheadlist.append(bh)

            material_helper.assign_material(bh.bulkhead_object,material_helper.get_material_bulkhead())

            if bh.bulkhead_void_object!=None:
                curve_helper.select_object(bh.bulkhead_void_object,True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')
                curve_helper.hide_object(bh.bulkhead_void_object)
            

            curve_helper.select_object(bh.bulkhead_object,True)

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')



    def make_longitudal_booleans(self):
        for lg in self.longitudal_slicer_list:

            #material_helper.assign_material(lg,material_helper.get_material_stringer())
            
            for bh in self.bulkheadlist:
                modifier=bh.bulkhead_object.modifiers.new(name="bool_slicer", type='BOOLEAN')
                modifier.object=lg
                modifier.operation="DIFFERENCE"
                modifier.double_threshold=0

        for lg in self.longitudal_list:
            #material_helper.assign_material(lg,material_helper.get_material_support())

            for bh in self.bulkheadlist:
                modifier=lg.modifiers.new(name="bool_bh", type='BOOLEAN')
                modifier.object=bh.bulkhead_object
                modifier.operation="DIFFERENCE"



    def cleanup_center(self,clean_location,clean_size):

        view_collection_cleaner=curve_helper.make_collection("cleaner",bpy.context.scene.collection.children)

        object_end_clean = self.make_bool_cube("mid_clean_%s"%clean_location[0],location=clean_location,size=clean_size)

        curve_helper.move_object_to_collection(view_collection_cleaner,object_end_clean)

        material_helper.assign_material(object_end_clean,material_helper.get_material_bool())

        for lg in self.longitudal_list:

            modifier=lg.modifiers.new(name="bool", type='BOOLEAN')
            modifier.object=object_end_clean
            modifier.operation="DIFFERENCE"
            modifier.double_threshold=0
            curve_helper.hide_object(object_end_clean)


    def cleanup_longitudal_ends(self,x_locations,rotations=None):

        view_collection_cleaner=curve_helper.make_collection("cleaner",bpy.context.scene.collection.children)

        end_clean_list=[]

        for index,x_location in enumerate(x_locations):
            # =========================================
            # Clean up ends of longitudal slicers

            block_width=self.hull_width

            adjusted_location=x_location
            if adjusted_location<0:
                adjusted_location=adjusted_location-block_width/2

            if adjusted_location>0:
                adjusted_location=adjusted_location+block_width/2

            object_end_clean = self.make_bool_cube("end_clean_%s"%index,location=[adjusted_location,0,0],size=(block_width,block_width,self.hull_height))

            if rotations!=None:
                curve_helper.select_object(object_end_clean,True)
                bpy.ops.transform.rotate(value=radians(rotations[index]),orient_axis='Y')

            curve_helper.move_object_to_collection(view_collection_cleaner,object_end_clean)

            material_helper.assign_material(object_end_clean,material_helper.get_material_bool())
            end_clean_list.append(object_end_clean)

        # ===================================================================

        for lg in self.longitudal_list:

            for object_end_clean in end_clean_list:		
                modifier=lg.modifiers.new(name="bool", type='BOOLEAN')
                modifier.object=object_end_clean
                modifier.operation="DIFFERENCE"
                modifier.double_threshold=0
                curve_helper.hide_object(object_end_clean)

        #curve_helper.hide_object(view_collection_cleaner)