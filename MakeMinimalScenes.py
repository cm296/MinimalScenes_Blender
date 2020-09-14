import bpy
from math import radians
from mathutils import Vector
import numpy as np 
import os.path
#from bpy import context


def add_sun(): 
    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.data.objects['Sun'].select_set(True)
    #bpy.ops.objects.delete() 
    # create light datablock, set attributes
    light_data = bpy.data.lights.new(name="Sun", type='SUN')
    light_data.energy = 5
    # create new object with our light datablock
    light_object = bpy.data.objects.new(name="Sun", object_data=light_data)
    # link light object
    bpy.context.collection.objects.link(light_object)
    # make it active 
    bpy.context.view_layer.objects.active = light_object
    #change location
    light_object.location = (8, 0, 10)
    # update scene, if needed
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()

def add_camera():
    #This sets up the camera
    #bpy.ops.object.mode_set(mode='OBJECT')
    rot = Vector((radians(70),radians(0),radians(90)))
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=(6,0,1),rotation=rot) 
    scene.camera = bpy.context.object
    bpy.data.objects['Camera']
    bpy.data.cameras['Camera'].lens = 50

def add_ground():
    #This makes the ground and sets the size
    rot = Vector((radians(180),radians(0),radians(90)))
    bpy.ops.mesh.primitive_plane_add(size = 150, location=(0,0,0), rotation=rot)
    ground = bpy.data.objects['Plane']
    ground.name = 'Floor'
    bpy.ops.mesh.primitive_plane_add(size = 8, location=(200,0,0), rotation=rot)
    bpy.context.active_object.name = 'reference'
        
    
def add_texture(JustFileName,file_path_address):
    rot = Vector((radians(180),radians(0),radians(90)))
    
    for material in bpy.data.materials:
        material.user_clear()
        bpy.data.materials.remove(material)

    material = bpy.data.materials.new("groundImage")
    #ground_mat.node_tree.nodes.clear()
    material.use_nodes = True
    #thesenodes.clear()
    #bsdf = mat.node_tree.nodes["Principled BSDF"] #set the material type
    

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # bsdf = thesenodes["Principled BSDF"] 
    # principled_bsdf = nodes.get("Principled BSDF")
    #material_output = nodes.get("Material Output")

   # Find the Material Output node, if it exists
    material_output = None
    for node in nodes:
        if node.type == "OUTPUT_MATERIAL":
            material_output = node
            break

    # Perhaps the nodes hasn't been found then you'll have to create it
    if material_output is None:
        material_output = nodes.new("ShaderNodeOutputMaterial")

    # Create a Principled BSDF nodes
    principled_bsdf = nodes["Principled BSDF"]

    
    texCoord = material.node_tree.nodes.new('ShaderNodeTexCoord') #create a texture coordinates node
    #assign a constant sized object to be used as the reference for the texture size
    texCoord.object = bpy.context.active_object #bpy.data.objects['reference']  
    texCoord.object.scale=(1.5,1.5,0) #make the reference object the desired scale 


    #load base color
    texImage = nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_COLOR' + '.jpg'))

    #load AO
    if os.path.isfile(file_path_address + JustFileName + '_OCC' + '.jpg'):
    	AO_tex = nodes.new('ShaderNodeTexImage')
    	AO_tex.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_OCC' + '.jpg'))
    	AO_tex.image.colorspace_settings.name = "Non-Color"    
    	MixRGB = nodes.new('ShaderNodeMixRGB')
    	MixRGB.blend_type = 'MULTIPLY'
    	
    	# Connect the base color and AO texture to the Principled BSDF
    	links.new(MixRGB.inputs['Color1'], texImage.outputs['Color'])#assign the texture to the material
    	links.new(MixRGB.inputs['Color2'], AO_tex.outputs['Color'])#assign the texture to the material
    	links.new(principled_bsdf.inputs['Base Color'], MixRGB.outputs['Color'])#assign the texture to the material
    else:
    	links.new(principled_bsdf.inputs['Base Color'],  texImage.outputs['Color'])#assign the texture to the material
    
    
    

    # Create Image Texture node and load the norm map
    normal_tex = nodes.new('ShaderNodeTexImage')
    normal_tex.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_NRM' + '.jpg'))
    # Set the color space to non-color, since normal maps contain
    # the direction of the surface normals and not color data
    normal_tex.image.colorspace_settings.name = "Non-Color"
    # Create the NormalMap node
    normal = nodes.new('ShaderNodeNormalMap')
    if  JustFileName == 'Pebbles_010':
        NormStrength = 10
    else:
        NormStrength = 2
    normal.inputs["Strength"].default_value = NormStrength

    #connect to reference coordinates
    links.new(texCoord.outputs['Object'], texImage.inputs['Vector']) #use the reference object coordinates for the texture image
    links.new(texCoord.outputs['Object'], normal_tex.inputs['Vector']) #use the reference object coordinates for the texture image

    
  
    

    # Connect the norm map to the PrincipleBSDF
    links.new(normal.inputs["Color"], normal_tex.outputs["Color"])   
    links.new(principled_bsdf.inputs["Normal"], normal.outputs["Normal"])

    #now roughness map
    if os.path.isfile(file_path_address + JustFileName + '_ROUGH' + '.jpg'):
        rough_tex = nodes.new('ShaderNodeTexImage')
        rough_tex.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_ROUGH' + '.jpg'))
        rough_tex.image.colorspace_settings.name = "Non-Color"
        links.new(texCoord.outputs['Object'], rough_tex.inputs['Vector']) #use the reference object coordinates for the texture image
        #Connect the roughness node to the Principled BSDF
        links.new(principled_bsdf.inputs['Roughness'], rough_tex.outputs['Color'])#assign the texture to the material
 

    if os.path.isfile(file_path_address + JustFileName + '_DISP' + '.jpg'):
        #Now displacement
        disp_tex = nodes.new('ShaderNodeTexImage')  
        disp_tex.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_DISP' + '.jpg'))
        disp_tex.image.colorspace_settings.name = "Non-Color"
        # Create the Displacement node
        displacement = nodes.new('ShaderNodeDisplacement')
        displacement.inputs["Midlevel"].default_value = 0.2
        displacement.inputs["Scale"].default_value = 0.05
        # Connect the disp map to the Displacement node
        links.new(displacement.inputs["Height"], disp_tex.outputs["Color"])
        # Connect the Displacement node to the Material Output node
        links.new(material_output.inputs["Displacement"], displacement.outputs["Displacement"])
 

    if os.path.isfile(file_path_address + JustFileName + '_metallic' + '.jpg'):
        #Now displacement
        metal_tex = nodes.new('ShaderNodeTexImage')  
        metal_tex.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_metallic' + '.jpg'))
        metal_tex.image.colorspace_settings.name = "Non-Color"
        links.new(principled_bsdf.inputs["Metallic"], metal_tex.outputs["Color"])


    if os.path.isfile(file_path_address + JustFileName + '_opacity' + '.jpg'):
        opac_tex = nodes.new('ShaderNodeTexImage')  
        opac_tex.image = bpy.data.images.load(filepath=(file_path_address + JustFileName + '_opacity' + '.jpg'))
        opac_tex.image.colorspace_settings.name = "Non-Color"
        MixShader = nodes.new('ShaderNodeMixShader')
        TranspBSDF = nodes.new('ShaderNodeBsdfTransparent')
        links.new(MixShader.inputs["Fac"], opac_tex.outputs["Color"])
        links.new(MixShader.inputs[1], TranspBSDF.outputs["BSDF"]) ##order is important!
        links.new(MixShader.inputs[2], principled_bsdf.outputs["BSDF"])
        links.new(material_output.inputs["Surface"], MixShader.outputs["Shader"])
    else:
        links.new(material_output.inputs["Surface"], principled_bsdf.outputs["BSDF"])
    
    
    obj = bpy.data.objects['Floor'] #get a reference to the object you want to assign this texture to
    #assign the texture material to the object
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


    


def render(out_path,img_out_name): 
    bpy.data.scenes['Scene'].render.engine = 'CYCLES' 
    bpy.data.scenes['Scene'].render.filepath = out_path + img_out_name
    bpy.data.scenes[0].render.image_settings.file_format='JPEG'
    bpy.ops.render.render(write_still=True)     

def mk_initial_scene():      
    add_sun()
    add_camera()
    add_ground()

#little function to list hidden files
def listdir_nohidden(path):
    thisList = os.listdir(path)
    newList = []
    for f in thisList:
        if not f.startswith('.'):
            newList.append(f)        
    return newList


# Note: we DELETE all objects in the scene and only then create the new mesh!
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

context = bpy.context
scene = context.scene

for c in scene.collection.children:
    scene.collection.children.unlink(c)
 
for c in bpy.data.collections:
    if not c.users:
        bpy.data.collections.remove(c)   
    
    

render_scene = True

top_path = "/Users/cmagri1/Documents/Project-MinimalScenes/"
TDPath = top_path + 'BlenderImages/3DTextures-3-Blender/'
out_path = top_path + 'Stimuli/0-Planes-BlenderOutput/'


FolderNoHiddenList = listdir_nohidden(TDPath)
FolderNoHiddenList.sort() #sort in alphabetical order

im_counter = 1

for word in FolderNoHiddenList:

    SubFolderList =  listdir_nohidden(TDPath + word)
    SubFolderList.sort()
    
    for subword in SubFolderList: #in the smallest folder
        

        file_path_address = TDPath + word + '/' + subword + '/'
        
                        
        ListofFiles =  listdir_nohidden(file_path_address) 
    	BaseColorFile = list(filter(lambda x: '_COLOR.jpg' in x, ListofFiles)) 
    	BaseColorFile = BaseColorFile[0]
		JustFileName = BaseColorFile.replace('_COLOR.jpg', '')#remove _COLOR word

		if (im_counter == 1):
        	mk_initial_scene()                        

    	add_texture(JustFileName,file_path_address)

		if render_scene:
        	img_out_name = 'texture_' + JustFileName + '.jpg'
        	render(out_path,img_out_name)

    	im_counter = im_counter + 1

#bkgNamelist = ['Metal_Grill_011' , 'Crystal_001' , 'Metal_Plate_004' , 
#'Denim_001' , 'Pebbles_009' , 'Agate_001' , 'Engraved_Metal_001' , 'Pebbles_010' , 
#'Agate_002' , 'Fabric_001' , 'Pebbles_011' , 'Alien_Metal_002' , 'Fabric_002' , 'Rock_036' , 
#'Black_Marble_001' , 'Leather_001' , 'Rug_003' , 'Camo_001' , 'Leather_002' , 'Camouflage_fabric_002' , 
#'Marble_Gray_001' , 'Coin_Stack_001' , 'Metal_Grill_001']

#bkgNamelist = ['Metal_Grill_011']


