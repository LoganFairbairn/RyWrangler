import bpy
from pathlib import Path
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.utils import resource_path
from .texture_settings import SHADER_NODES
from ..source import debug_logging
from ..package import ADDON_PACKAGE
import os
import re

# Dictionary of words / tags that may be in image texture names that could be used to identify material channels from image file names.
MATERIAL_CHANNEL_TAGS = {
    "color": 'BASE_COLOR',
    "colour": 'BASE_COLOR',
    "couleur": 'BASE_COLOR',
    "diffuse": 'BASE_COLOR',
    "diff": 'BASE_COLOR',
    "dif": 'BASE_COLOR',
    "subsurface": 'SUBSURFACE',
    "subsurf": 'SUBSURFACE',
    "ss": 'SUBSURFACE',
    "metallic": 'METALLIC',
    "metalness": 'METALLIC',
    "metal": 'METALLIC',
    "métalique": 'METALLIC',
    "metalique": 'METALLIC',
    "specular": 'SPECULAR',
    "specularité": 'SPECULAR',
    "specularite": 'SPECULAR',
    "spec": 'SPECULAR',
    "roughness": 'ROUGHNESS',
    "rough": 'ROUGHNESS',
    "rugosité": 'ROUGHNESS',
    "rugosite": 'ROUGHNESS',
    "emission": 'EMISSION',
    "émission": 'EMISSION',
    "emit": 'EMISSION',
    "normal": 'NORMAL',
    "normals": 'NORMAL',
    "normale": 'NORMAL',
    "nor": 'NORMAL',
    "ngl": 'NORMAL',
    "ndx": 'NORMAL',
    "height": 'HEIGHT',
    "hauteur": 'HEIGHT',
    "bump": 'HEIGHT',
    "opacity": 'ALPHA',
    "opaque": 'ALPHA',
    "alpha": 'ALPHA',
    "ao": 'AMBIENT_OCCLUSION',
    "occlusion": 'AMBIENT_OCCLUSION',
    "ambient": 'AMBIENT_OCCLUSION',

    # RGB channel packing...
    "orm": 'CHANNEL_PACKED',
    "rmo": 'CHANNEL_PACKED',

    # RGBA channel packing, 'X' is used to identify when nothing is packed into a channel.
    "moxs": 'CHANNEL_PACKED',

    # Naming conventions such as 'MyTextureName_RoughnessMetallic' can't be imported automatically
    # because it's ambiguous for which RGBA channel the values are intended to go into.
}

# https://docs.unrealengine.com/4.27/en-US/ProductionPipelines/AssetNaming/
# With an identifiable material channel format, such as the one used commonly in game engines (T_MyTexture_C_1),
# we can identify material channels using only the first few letters.
MATERIAL_CHANNEL_ABBREVIATIONS = {
    "c": 'BASE_COLOR',
    "m": 'METALLIC',
    "r": 'ROUGHNESS',
    "n": 'NORMAL',
    "ngl": 'NORMAL',
    "ndx": 'NORMAL',
    "h": 'HEIGHT',
    "b": 'HEIGHT',
    "s": 'SPECULAR',
    "ss": 'SUBSURFACE',
    "a": 'ALPHA',
    "cc": 'COAT',
    "e": 'EMISSION',
    "o": 'AMBIENT_OCCLUSION',
    "ao": 'AMBIENT_OCCLUSION'
}

# ==============================================================
# Layers
# ==============================================================

class RYWRANGLER_OT_AddPaintLayer(bpy.types.Operator):
    bl_idname = "rywrangler.add_paint_layer"
    bl_label = "Add Paint Layer"
    bl_description = "Adds an image texture node under the cursor, and a mix node below it if another exists"
    bl_options = {'REGISTER', 'UNDO'}

    # Ensure the operator is only ran in the correct context.
    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR' and context.space_data.tree_type == 'ShaderNodeTree'

    def execute(self, context):
        add_layer_node("UV")

        # TODO: Add a new image texture into the color image texture node.
        return {'FINISHED'}

class RYWRANGLER_OT_AddUVLayer(Operator):
    bl_idname = "rywrangler.add_uv_layer"
    bl_description = "Adds a shader node and a mix shader node"
    bl_label = "Add UV Layer"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.space_data and
            context.space_data.type == 'NODE_EDITOR' and
            context.space_data.tree_type == 'ShaderNodeTree'
        )

    def execute(self, context):
        add_layer_node("UV")
        return {'FINISHED'}

class RYWRANGLER_OT_AddDecalLayer(Operator):
    bl_idname = "rywrangler.add_decal_layer"
    bl_label = "Add Decal Layer"
    bl_description = "Adds a node setup that projects the specified texture using the coordinates of an empty object. This is designed for adding non-destructive sticker style layers"
    bl_options  = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        add_layer_node("Decal")
        return {'FINISHED'}

class RYWRANGLER_OT_AddTriplanarLayer(Operator):
    bl_idname = "rywrangler.add_triplanar_layer"
    bl_label = "Add Triplanar Layer"
    bl_description = "Adds a node setup that projects specified textures onto the X, Y and Z axis of the object, blending the projection at the seams"
    bl_options  = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        add_layer_node("Triplanar")
        return {'FINISHED'}

# ==============================================================
# Masks
# ==============================================================

class RYWRANGLER_OT_AddGrunge(Operator):
    bl_idname = "rywrangler.add_grunge"
    bl_label = "Add Grunge"
    bl_description = "Adds a group node designed for adding grunge to objects"
    bl_options  = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        add_group_node("Mask_Grunge")
        return {'FINISHED'}
    
class RYWRANGLER_OT_AddEdgeWear(Operator):
    bl_idname = "rywrangler.add_edge_wear"
    bl_label = "Add Edge Wear"
    bl_description = "Adds a group node designed for adding edge wear to objects"
    bl_options  = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        add_group_node("Mask_EdgeWear")
        return {'FINISHED'}

# ==============================================================
# Utility Operators
# ==============================================================

class RYWRANGLER_OT_import_texture_set(Operator, ImportHelper):
    bl_idname = "rywrangler.import_texture_set"
    bl_label = "Import Texture Set"
    bl_description = "Imports multiple selected textures into material channels by parsing selected file names. Images with naming conventions that don't accurately identify the material channel they belong to will not import properly"
    bl_options = {'REGISTER', 'UNDO'}

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.exr',
        options={'HIDDEN'}
    )

    # Disable this operator when the material isn't made with this add-on.
    @ classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        def split_filename_by_components(filename):
            '''Helper function to split the file name into components.'''

            # Remove file extension.
            filename = os.path.splitext(filename)[0]

            # Remove numbers (these can't be used to identify a material channel from the texture name).
            filename = ''.join(i for i in filename if not i.isdigit())
            
            # Separate camel case by space.
            filename = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', filename))

            # Replace common separators with a space.
            separators = ['_', '.', '-', '__', '--', '#']
            for seperator in separators:
                filename = filename.replace(seperator, ' ')

            # Return all components split by a space with lowercase characters.
            split_components = filename.split(' ')
            components = []
            for c in split_components:
                if c != '':
                    components.append(c.lower())

            return components

        def get_rgba_channel_from_index(index):
            '''Returns the RGBA channel name for the provided index (i.e 0 = R, 1 = G...).'''
            match index:
                case -1:
                    return 'COLOR'
                case 0:
                    return 'RED'
                case 1:
                    return 'GREEN'
                case 2:
                    return 'BLUE'
                case 3:
                    return 'ALPHA'
                case _:
                    return 'ERROR'

        # Get some information about the layer user later in the function.
        selected_layer_index = bpy.context.scene.RYWRANGLER_layer_stack.selected_layer_index
        layer_type = material_layers.get_layer_type()
        layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)
        shader_info = bpy.context.scene.RYWRANGLER_shader_info
        
        # Compile a list of all unique tags found accross all user selected image file names.
        material_channel_occurance = {}
        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag not in material_channel_occurance and tag in MATERIAL_CHANNEL_TAGS:
                    material_channel = MATERIAL_CHANNEL_TAGS[tag]
                    material_channel_occurance[material_channel] = 0

        # Calculate how many times a unique channel tag appears accross all user selected image files.
        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag in MATERIAL_CHANNEL_TAGS:
                    material_channel = MATERIAL_CHANNEL_TAGS[tag]
                    if material_channel in material_channel_occurance:
                        material_channel_occurance[material_channel] += 1

        # Cycle through all selected image files and try to identify the correct material channel to import them into.
        selected_image_file = False
        no_files_imported = True
        for file in self.files:
            detected_material_channel = 'NONE'
            
            # If the image file starts with a 'T_' assume it's using a commonly used Unreal Engine / game engine naming convention.
            if file.name.startswith('T_'):
                remove_file_extension = file.name.split('.')[0]
                channel_abbreviation = remove_file_extension.split('_')[2].lower()
                if channel_abbreviation in MATERIAL_CHANNEL_ABBREVIATIONS:
                    detected_material_channel = MATERIAL_CHANNEL_ABBREVIATIONS[channel_abbreviation]

            # For all other files, guess the material channel by parsing for tags in the file name that would ID it.
            else:

                # Create a list of tags used in this files name.
                tags = split_filename_by_components(file.name)
                channel_tags_in_filename = []
                for tag in tags:
                    if tag in MATERIAL_CHANNEL_TAGS:
                        channel_tags_in_filename.append(MATERIAL_CHANNEL_TAGS[tag])

                # Don't import files that have no material channel tag detected in it's file name.
                if len(channel_tags_in_filename) > 0:

                    # Start by assuming the correct material channel is the one that appears the least in the file name.
                    # I.E: Selected files: RoughMetal_002_2k_Color, RoughMetal_002_2k_Normal, RoughMetal_002_2k_Metallic, RoughMetal_002_2k_Rough
                    # For the first file in the above example, the correct material channel would be color,
                    # because 'metallic' appears more than once accross all user selected image files.
                    detected_material_channel = channel_tags_in_filename[0]
                    material_channel_occurances_equal = True
                    for material_channel_name in channel_tags_in_filename:
                        if material_channel_occurance[material_channel_name] < material_channel_occurance[detected_material_channel]:
                            detected_material_channel = material_channel_name
                            material_channel_occurances_equal = False
                    
                    # If all material channels identified in the files name occur equally throughout all selected filenames,
                    # use the material channel that occurs the most in the files name.
                    # I.E: Selected files: RoughMetal_002_2k_Color, RoughMetal_002_2k_Normal, RoughMetal_002_2k_Metallic, RoughMetal_002_2k_Rough
                    # For the third file in the above example, the correct material channel is 'metallic' because that tag appears twice in the name.
                    if material_channel_occurances_equal:
                        for material_channel_name in channel_tags_in_filename:
                            if material_channel_occurance[material_channel_name] > material_channel_occurance[detected_material_channel]:
                                detected_material_channel = material_channel_name

            # Only import the image if a material channel was detected.
            if detected_material_channel != 'NONE':
                no_files_imported = False
                folder_directory = os.path.split(self.filepath)
                image_path = os.path.join(folder_directory[0], file.name)
                bpy.ops.image.open(filepath=image_path)
                imported_image = bpy.data.images.get(file.name)
                if imported_image == None:
                    debug_logging.log(
                        "Import texture set operator failed to locate {0} in the blend data.".format(file.name), 
                        message_type='ERROR',
                        sub_process=False
                    )
                    continue

                # To support proper importing of channel packed images,
                # create a list of all material channels that are packed into this image.
                # For images not using channel packing, this list will have a length of 1.
                packed_channels = []
                channel_packed_format = ""
                if detected_material_channel == 'CHANNEL_PACKED':
                    for tag in tags:
                        if tag in MATERIAL_CHANNEL_TAGS:
                            channel_packed_format = tag
                            for i in range(0, len(channel_packed_format)):
                                if channel_packed_format[i] in MATERIAL_CHANNEL_ABBREVIATIONS:
                                    packed_channel = MATERIAL_CHANNEL_ABBREVIATIONS[channel_packed_format[i]]

                                    # If the active material isn't using the specular material channel, the material channel abbreviated with 'S'
                                    # is more likely 'Smoothness', instead of 'Specular'. Swap the packed channel to Roughness and invert the filter
                                    # to convert the smoothness into roughness.
                                    if packed_channel == 'SPECULAR':
                                        packed_channel = 'ROUGHNESS'

                                        invert_r = False
                                        invert_g = False
                                        invert_b = False
                                        invert_a = False
                                        match i:
                                            case 0:
                                                invert_r = True
                                            case 1:
                                                invert_g = True
                                            case 2:
                                                invert_b = True
                                            case 3:
                                                invert_a = True

                                        export_textures.invert_image(imported_image, invert_r, invert_g, invert_b, invert_a)
                                        debug_logging.log_status("Channel packed smoothness was detected and inverted into roughness.", self, type='INFO')

                                    packed_channels.append([packed_channel, get_rgba_channel_from_index(i)])
                else:
                    packed_channels.append([detected_material_channel, -1])                
                
                # Adjust nodes for the layer to support importing of all packed channels in the imported image.
                for packed_channel in packed_channels:
                    channel = packed_channel[0]

                    # Create material channel nodes for all new channels.
                    material_layers.add_material_channel_nodes(channel, layer_node.node_tree, layer_type)

                    # Change all material channels to use texture nodes (if they aren't already).
                    value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel)
                    if value_node.bl_static_type != 'TEX_IMAGE':
                        material_layers.replace_material_channel_node(channel, 'TEXTURE')

                    # Determine the default texture interpolation based on the material channel name.
                    default_texture_interpolation = 'Linear'
                    channel_socket_name = shaders.get_shader_channel_socket_name(channel)
                    shader_material_channel = shader_info.material_channels.get(channel_socket_name)
                    if shader_material_channel:
                        default_texture_interpolation = shader_material_channel.default_texture_interpolation

                    # Place the image into a material nodes based on texture projection and inferred material channel name.
                    projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
                    match projection_node.node_tree.name:
                        case 'RY_UVProjection':
                            value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel)
                            if value_node.bl_static_type == 'TEX_IMAGE':
                                value_node.image = imported_image
                                value_node.interpolation = default_texture_interpolation

                        case 'RY_TriplanarProjection':
                            for i in range(0, 3):
                                value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel, node_number=i + 1)
                                if value_node.bl_static_type == 'TEX_IMAGE':
                                    value_node.image = imported_image
                                    value_node.interpolation = default_texture_interpolation

                # If the image is detected to be using channel packing, adjust the output of the material channel.
                if detected_material_channel == 'CHANNEL_PACKED':
                    for i in range(0, len(packed_channels)):
                        channel = packed_channels[i][0]
                        output_channel = packed_channels[i][1]
                        material_layers.set_material_channel_crgba_output(channel, output_channel, selected_layer_index)

                # Select the first image file in the canvas painting window.
                if selected_image_file == False:
                    context.scene.tool_settings.image_paint.canvas = imported_image
                    selected_image_file = True

                # Update the imported images colorspace based on it's detected material channel.
                image_utilities.set_default_image_colorspace(imported_image, detected_material_channel)

                # Print a warning about using DirectX normal maps for users if it's suspected they are using one.
                if detected_material_channel == 'NORMAL':
                    if image_utilities.check_for_directx(file.name):
                        self.report({'INFO'}, "DirectX normal map import suspected, normals may be inverted. Use an OpenGL normal map instead.")

                # Copy the imported image to a folder next to the blend file for file management purposes.
                # This happens only if 'save imported textures' is on in the add-on preferences.
                image_utilities.save_raw_image(image_path, imported_image.name)

            else:
                debug_logging.log("No material channel detected for file: {0}".format(file.name))

        if no_files_imported:
            debug_logging.log_status("No detected material channel in any selected files.", self, type='WARNING')

        else:
            # Organize all material channel frames.
            material_layers.organize_material_channel_frames(layer_node.node_tree)

        return {'FINISHED'}

class RYWRANGLER_OT_AutoLinkNodes(bpy.types.Operator):
    bl_idname = "rywrangler.auto_link_nodes"
    bl_label = "Auto Link Nodes"
    bl_description = "Attempts to link two nodes together automatically by referencing their node type, socket names, and socket types"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the active node tree (ensure we're in a node editor)
        if not context.space_data or not context.space_data.node_tree:
            self.report({'ERROR'}, "Can't link nodes, there's no active node tree.")
            return {'CANCELLED'}
        
        node_tree = context.space_data.node_tree
        selected_nodes = [node for node in node_tree.nodes if node.select]
        
        # Throw an error if the user selections less or more than two nodes.
        if len(selected_nodes) != 2:
            self.report({'ERROR'}, "Can't link nodes, you must select exactly two nodes for automatic linking.")
            return {'CANCELLED'}
        
        node1, node2 = selected_nodes
        
        # Create a dictionary of output sockets by name for node1
        outputs1 = {socket.name: socket for socket in node1.outputs}
        inputs2 = {socket.name: socket for socket in node2.inputs if not socket.is_linked}
        
        # Link matching sockets
        links = node_tree.links
        link_count = 0
        
        for name, output_socket in outputs1.items():
            if name in inputs2:
                links.new(output_socket, inputs2[name])
                link_count += 1

        if link_count == 0:
            self.report({'WARNING'}, "No matching sockets found to link.")
        else:
            self.report({'INFO'}, f"Linked {link_count} matching sockets.")
        
        return {'FINISHED'}

class RYWRANGLER_OT_IsolateNode(Operator):
    bl_idname = "rywrangler.isolate_node"
    bl_label = "Isolate Node"
    bl_options  = {'REGISTER', 'UNDO'}
    bl_description = "Isolates the active node by connecting it to the material output node"
    
    def execute(self, context):
        # Ensure we're in the node editor and using a material node tree
        if not context.space_data or context.space_data.tree_type != 'ShaderNodeTree':
            self.report({'WARNING'}, "Not in a Shader Node Tree")
            return {'CANCELLED'}

        mat = context.object.active_material
        if not mat or not mat.node_tree:
            self.report({'WARNING'}, "No active material with node tree found")
            return {'CANCELLED'}
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Find the first Material Output node
        output_node = next((node for node in nodes if node.type == 'OUTPUT_MATERIAL'), None)
        if not output_node:
            self.report({'WARNING'}, "No Material Output node found")
            return {'CANCELLED'}
        
        # Get the selected node
        selected_nodes = [node for node in nodes if node.select]
        if not selected_nodes:
            self.report({'WARNING'}, "No node selected")
            return {'CANCELLED'}
        
        selected_node = selected_nodes[0]  # Use the first selected node
        
        # Determine the output socket (assuming first available output socket)
        if not selected_node.outputs:
            self.report({'WARNING'}, "Selected node has no output sockets")
            return {'CANCELLED'}
        
        output_socket = selected_node.outputs[0]
        
        # Determine the input socket of the Material Output node
        input_socket = output_node.inputs.get("Surface")
        if not input_socket:
            self.report({'WARNING'}, "Material Output node has no Surface input")
            return {'CANCELLED'}
        
        # Create the link
        links.new(output_socket, input_socket)
        self.report({'INFO'}, "Connected node to Material Output")
        
        return {'FINISHED'}

class RYWRANGLER_OT_edit_image_externally(Operator):
    bl_idname = "rywrangler.edit_image_externally"
    bl_label = "Edit Image Externally"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Opens the selected image in the 2D image editor defined in the users Blender preferences"

    def execute(self, context):
        return {'FINISHED'}

# ==============================================================
# Helper Functions
# ==============================================================

def get_blend_assets_path():
    '''Returns the path to the blend file where assets are stored for this add-on.'''
    blend_assets_path = str(Path(resource_path('USER')) / "scripts/addons" / ADDON_PACKAGE / "assets" / "Assets.blend")
    return blend_assets_path

def duplicate_node_group(node_group_name):
    '''Duplicates (makes a unique version of) the provided node group.'''
    node_group = bpy.data.node_groups.get(node_group_name)
    if node_group:
        duplicated_node_group = node_group.copy()
        duplicated_node_group.name = node_group_name + "_Copy"
        return duplicated_node_group
    else:
        debug_logging.log("Error: Can't duplicate node, group node with the provided name does not exist.")
        return None
    
def append_group_node(node_group_name, keep_link=False, return_unique=False, append_missing=True, use_fake_user=True):
    '''Appends the group node with the provided name from this add-ons asset blend file.'''

    node_tree = bpy.data.node_groups.get(node_group_name)

    # If the node group doesn't exist, append it from the blend asset file for the add-on.
    if not node_tree and append_missing:
        blend_assets_path = get_blend_assets_path()
        with bpy.data.libraries.load(blend_assets_path, link=keep_link) as (data_from, data_to):
            data_to.node_groups = [node_group_name]
        
        # Check if the node group was successfully appended.
        node_tree = bpy.data.node_groups.get(node_group_name)
        if node_tree:

            # Mark appended node trees with a 'fake user' to stop them from being 
            # auto deleted from the blend file if they are not actively used.
            node_tree.use_fake_user = use_fake_user

        # Throw an error if the node group doesn't exist and can't be appended.
        else:
            debug_logging.log("{0} does not exist and has failed to append from the blend asset file.".format(node_group_name))
            return None

    # Returning a duplicated version of an existing node group (rather than appending a new one) can be beneficial to help avoid appending duplicated of sub node groups.
    # Return a unique (duplicated) version of the node group if specified.
    if return_unique:
        duplicated_node_group = duplicate_node_group(node_group_name)
        return duplicated_node_group
    
    # Return the node tree.
    return node_tree

def set_snapping_mode(snapping_mode, snap_on=True):
    '''Sets snapping settings for working with different scenarios (decals).'''
    match snapping_mode:
        case 'DEFAULT':
            bpy.context.scene.tool_settings.use_snap = snap_on
            bpy.context.scene.tool_settings.use_snap_align_rotation = False
            bpy.context.scene.tool_settings.snap_elements_base = {'INCREMENT'}
            bpy.context.scene.tool_settings.snap_target = 'CLOSEST'

        case 'DECAL':
            bpy.context.scene.tool_settings.use_snap = snap_on
            bpy.context.scene.tool_settings.use_snap_align_rotation = True
            bpy.context.scene.tool_settings.snap_elements = {'FACE'}
            bpy.context.scene.tool_settings.snap_elements_individual = {'FACE_PROJECT'}
            bpy.context.scene.tool_settings.snap_target = 'CENTER'

def add_group_node(group_node_name):
    '''Appends a group node from the asset blend file and adds it to the active material.'''
    pie_menu_location = bpy.context.scene.rywrangler_pie_menu_location

    # If there is no active node tree, abort.
    active_node_tree = bpy.context.space_data.edit_tree
    if not active_node_tree:
        return

    # Create a new empty node group.
    node_tree = append_group_node(group_node_name)
    node_tree.name = bpy.context.active_object.active_material.name + "_NewLayer"

    # Add a Group Node to the material node editor.
    group_node = active_node_tree.nodes.new('ShaderNodeGroup')
    group_node.node_tree = node_tree
    group_node.name = node_tree.name
    group_node.width = 200.0
    group_node.location = (pie_menu_location[0] - 100, pie_menu_location[1] + group_node.height)
    return group_node

def add_layer_node(layer_type):
    '''Adds a default layer node of the specified type, organizes nodes and connects layers if applicable.'''

    mat = bpy.context.object.active_material
    if not mat or not mat.use_nodes:
        return

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Find the selected node with a SHADER output
    selected_node = next(
        (n for n in nodes if n.select and n.outputs and n.outputs[0].type == 'SHADER'),
        None
    )

    # Add the new layer group node based on the specified type
    layer_group_node = None
    match layer_type:
        case "UV":
            layer_group_node = add_group_node("Layer_UV")
        case "DECAL":
            layer_group_node = add_group_node("Layer_Decal")
        case "TRIPLANAR":
            layer_group_node = add_group_node("Layer_Triplanar")
        case _:
            return

    if not layer_group_node:
        return

    if not selected_node:
        # Just add the layer node with no connections
        return

    # Position new layer node below selected
    vertical_offset = -300
    layer_group_node.location = (
        selected_node.location.x,
        selected_node.location.y + vertical_offset
    )

    # Create Mix Shader node to the right and centered vertically
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    horizontal_offset = 300
    mid_y = (selected_node.location.y + layer_group_node.location.y) / 2
    mix_shader.location = (
        selected_node.location.x + horizontal_offset,
        mid_y
    )
    mix_shader.inputs[0].default_value = 0.5  # Default blend factor

    # Unlink any connections from selected_node.outputs[0]
    output_socket = selected_node.outputs[0]
    for link in list(output_socket.links):
        links.remove(link)

    # Connect selected node to first shader input
    links.new(output_socket, mix_shader.inputs[1])

    # Connect new layer node to second shader input
    links.new(layer_group_node.outputs[0], mix_shader.inputs[2])

    # Reconnect to Material Output (Surface)
    output_node = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeOutputMaterial)), None)
    if output_node:
        for link in output_node.inputs['Surface'].links:
            links.remove(link)
        links.new(mix_shader.outputs[0], output_node.inputs['Surface'])

    # Select original, layer, and mix nodes
    for n in nodes:
        n.select = False
    selected_node.select = True
    layer_group_node.select = True
    mix_shader.select = True
    mat.node_tree.nodes.active = mix_shader
