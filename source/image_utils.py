# This file contains functions to help creating, saving, and editing of image files within Blender.

import bpy
import debug_logging
import texture_settings
import random
import os
import platform
import subprocess

def create_image(new_image_name, image_width=-1, image_height=-1, base_color=(0.0, 0.0, 0.0, 1.0), generate_type='BLANK', alpha_channel=False, thirty_two_bit=False, add_unique_id=False, delete_existing=False):
    '''Creates a new image in blend data.'''
    if delete_existing:
        existing_image = bpy.data.images.get(new_image_name)
        if existing_image:
            bpy.data.images.remove(existing_image)

    if add_unique_id:
        new_image_name = "{0}_{1}".format(new_image_name, str(random.randrange(10000,99999)))
        while bpy.data.images.get(new_image_name) != None:
            new_image_name = "{0}_{1}".format(new_image_name, str(random.randrange(10000,99999)))

    # If -1 is passed, use the image resolution defined in the texture set settings.
    if image_width == -1:
        w = texture_settings.get_texture_width()
    else:
        w = image_width

    if image_height == -1:
        h = texture_settings.get_texture_height()
    else:
        h = image_height

    bpy.ops.image.new(name=new_image_name, 
                      width=w, 
                      height=h,
                      color=base_color, 
                      alpha=alpha_channel, 
                      generated_type=generate_type,
                      float=thirty_two_bit,
                      use_stereo_3d=False, 
                      tiled=False)

    return bpy.data.images.get(new_image_name)

def open_folder(folder_path, self):
    '''Opens the folder path in the users file browser based on their operating system.'''
    if os.path.isdir(folder_path):
        if platform.system() == 'Windows':
            os.startfile(folder_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", folder_path])
        else:
            subprocess.Popen(["xdg-open", folder_path])
    else:
        debug_logging.log_status("Folder path is invalid: {0}".format(folder_path), self, type='INFO')