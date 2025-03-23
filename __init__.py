# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import PointerProperty, EnumProperty
from .source.operators import RYWANGLER_OT_AutoLinkNodes, RYWRANGLER_OT_IsolateNode, RYWRANGLER_OT_AddMaterialLayer, RYWRANGLER_OT_AddPaintLayer, RYWRANGLER_OT_AddImageLayer, RYWRANGLER_OT_AddDecalLayer, RYWRANGLER_OT_AddPaintLayer, RYWRANGLER_OT_AddTriplanarLayer, RYWRANGLER_OT_AddTriplanarHexGridLayer, RYWRANGLER_OT_AddBlur, RYWRANGLER_OT_AddGrunge, RYWRANGLER_OT_AddEdgeWear, RYWRANGLER_OT_AdjustNormalIntensity, RYWRANGLER_OT_MixNormalMaps, RYWRANGLER_OT_edit_image_externally
from .source.texture_settings import RYWRANGLER_texture_settings, RYWRANGLER_OT_set_raw_texture_folder, RYWRANGLER_OT_open_raw_texture_folder
from .source.ui import RYWRANGLER_OT_open_menu

bl_info = {
    "name": "RyWrangler",
    "author": "Logan Fairbairn (Ryver)",
    "description": "A quick access panel designed to speed up complex layer based material node editing in Blender",
    "blender": (4, 3, 2),
    "version": (1, 0, 0),
    "location": "Node Editor > Shift + Q",
    "warning": "",
    "category": "Material",
}

# List of classes to be registered.
classes = (
    # Operators
    RYWANGLER_OT_AutoLinkNodes,
    RYWRANGLER_OT_IsolateNode,
    RYWRANGLER_OT_AddMaterialLayer,
    RYWRANGLER_OT_AddPaintLayer,
    RYWRANGLER_OT_AddImageLayer,
    RYWRANGLER_OT_AddDecalLayer,
    RYWRANGLER_OT_AddTriplanarLayer,
    RYWRANGLER_OT_AddTriplanarHexGridLayer,
    RYWRANGLER_OT_AddBlur,
    RYWRANGLER_OT_AddGrunge,
    RYWRANGLER_OT_AddEdgeWear,
    RYWRANGLER_OT_AdjustNormalIntensity,
    RYWRANGLER_OT_MixNormalMaps,
    RYWRANGLER_OT_edit_image_externally,

    # Texture Settings
    RYWRANGLER_texture_settings,
    RYWRANGLER_OT_set_raw_texture_folder,
    RYWRANGLER_OT_open_raw_texture_folder,

    # User Interface
    RYWRANGLER_OT_open_menu
)

# Register classes with Blender.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.rywrangler_shader_node = PointerProperty(type=bpy.types.NodeTree)
    bpy.types.Scene.rywrangler_texture_settings = PointerProperty(type=RYWRANGLER_texture_settings)
    
    # Assign the pie menu to Shift + Q in the Shader Node Editor.
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Node Editor", space_type='NODE_EDITOR')
    km.keymap_items.new("rywrangler.open_menu", "Q", "PRESS", shift=True)

# Unregister classes and properties.
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    # Remove keymapping when the add-on is disabled.
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.get("Node Editor")
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == "wm.call_menu_pie" and kmi.properties.name == "NODE_MT_shader_pie":
                km.keymap_items.remove(kmi)
                break

if __name__ == "__main__":
    register()
