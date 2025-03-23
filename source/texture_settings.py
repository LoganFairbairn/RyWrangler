# This file contains texture related settings for this add-on.

import os
import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, StringProperty, EnumProperty
from ..source import debug_logging

# Standard texture resolutions used for textures.
STANDARD_TEXTURE_RESOLUTIONS = [
    ("TWO_FIFTY_SIX", "256", "Low resolution."),
    ("FIVE_TWELVE", "512", "Low resolution."),
    ("ONE_K", "1024", "Standard resolution."),
    ("TWO_K", "2048", "High resolution."),
    ("FOUR_K", "4096", "Very high resolution."),
    ("EIGHT_K", "8192", "Extremely high resolution.")
]

# Shader nodes available in this add-on.
SHADER_NODES = [
    ("PRINCIPLED_BSDF", "Principled BSDF", "The default shader in Blender based on the OpenPBR surface shading model that combines multiple layers into a single easy to use shader."),
    ("DIFFUSE_BSDF", "Diffuse BSDF", "Shader based on the Lambertian and Oren-Nayar diffuse reflection model."),
    ("EMISSION", "Emission", "Lambertian emission shader which can be used for material and light surface outputs."),
    ("GROUP_NODE", "Group Node", "Use a group node as the shader node.")
]

def update_match_image_resolution(self, context):
    texture_set_settings = context.scene.rywrangler_texture_settings
    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    texture_set_settings = context.scene.rywrangler_texture_settings
    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

def get_texture_width():
    '''Returns a numeric value based on the enum for texture width.'''
    match bpy.context.scene.rywrangler_texture_settings.image_width:
        case 'THIRTY_TWO':
            return 32
        case 'SIXTY_FOUR':
            return 64
        case 'ONE_TWENTY_EIGHT':
            return 128
        case 'TWO_FIFTY_SIX':
            return 256
        case 'FIVE_TWELVE':
            return 512
        case 'ONE_K':
            return 1024
        case 'TWO_K':
            return 2048
        case 'FOUR_K':
            return 4096
        case _:
            return 10

def get_texture_height():
    '''Returns a numeric value based on the enum for texture height.'''
    match bpy.context.scene.rywrangler_texture_settings.image_height:
        case 'THIRTY_TWO':
            return 32
        case 'SIXTY_FOUR':
            return 64
        case 'ONE_TWENTY_EIGHT':
            return 128
        case 'TWO_FIFTY_SIX':
            return 256
        case 'FIVE_TWELVE':
            return 512
        case 'ONE_K':
            return 1024
        case 'TWO_K':
            return 2048
        case 'FOUR_K':
            return 4096
        case _:
            return 10

class RYWRANGLER_texture_settings(PropertyGroup):
    '''Settings for textures.'''
    raw_image_folder: StringProperty(
        name="Raw Image Folder",
        description="The path to the folder when unprocessed images are saved", 
        default="Default"
    )

    image_width: EnumProperty(
        items=STANDARD_TEXTURE_RESOLUTIONS, 
        name="Image Width", 
        description="Image width in pixels for all images created with this add-on. Changing this value during through creating a material could result in the pixel resolution between textures used in the material not matching, which will cause exported textures to be blurry", 
        default='TWO_K', 
        update=update_image_width
    )

    image_height: EnumProperty(
        items=STANDARD_TEXTURE_RESOLUTIONS, 
        name="Image Height", 
        description="Image height in pixels for all images created with this add-on. Changing this value during through creating a material could result in the pixel resolution between textures used in the material not matching, which will cause exported textures to be blurry", 
        default='TWO_K'
    )

    shader_node: EnumProperty(
        items=SHADER_NODES,
        name="Shader Node",
        description="The shader node used to create new layers for layers",
        default="PRINCIPLED_BSDF"
    )

    match_image_resolution: BoolProperty(
        name="Match Image Resolution", 
        description="When toggled on, the image width and height will be matched", 
        default=True, 
        update=update_match_image_resolution
    )

    thirty_two_bit: BoolProperty(
        name="32 Bit Color", 
        description="If on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients", 
        default=True
    )

class RYWRANGLER_OT_set_raw_texture_folder(Operator):
    bl_idname = "rywrangler.set_raw_texture_folder"
    bl_label = "Set Raw Texture Folder Path"
    bl_description = "Opens a file explorer to select the folder path where raw textures are saved"
    bl_options = {'REGISTER'}

    directory: StringProperty()

    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
    )

    def execute(self, context):
        if not os.path.isdir(self.directory):
            debug_logging.log_status("Invalid directory.", self, type='INFO')
        else:
            context.scene.RYWRANGLER_raw_textures_folder = self.directory
            debug_logging.log_status("Raw texture folder set to: {0}".format(self.directory), self, type='INFO')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class RYWRANGLER_OT_open_raw_texture_folder(Operator):
    bl_idname = "rywrangler.open_raw_texture_folder"
    bl_label = "Open Raw Texture Folder"
    bl_description = "Opens the folder in your systems file explorer where raw textures will be saved. Raw textures are considered any image that's used in the material editing process, that's not a mesh map, or a completed texture being exported"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        #raw_texture_folder_path = bau.get_texture_folder_path(folder='RAW_TEXTURES')
        #bau.open_folder(raw_texture_folder_path, self)
        return {'FINISHED'}