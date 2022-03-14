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

bl_info = {
    "name" : "Animation Retargetter",
    "author" : "Asbibi",
    "description" : "Allows to retarget",
    "blender" : (3, 0, 0),
    "version" : (0, 0, 1),
    "location" : "Properties",
    "warning" : "",
    "category" : "Armature"
}



import bpy
from . aar_properties import *
from . aar_labelOperator import *
from . aar_actionOperator import *
from . aar_retargetOperator import *
from . aar_panel import *

classes = (AAR_PROP_ActionListProperty,
            AAR_PROP_SingleBoneProperty,
            AAR_PROP_MemberProperty,
            AAR_PROP_Quaternion,
            AAR_PROP_SingleBoneLink,
            AAR_PROP_MemberLink,
            AAR_PROP_GroupNameListProperty,
            AAR_OT_LabelBone,
            AAR_OT_UnlabelBone,
            AAR_OT_UnlabelBoneAll,
            AAR_OT_AutoLabel,
            AAR_OT_RegisterAction,
            AAR_OT_UnregisterAction,
            AAR_OT_UnregisterAllActions,
            AAR_OT_CheckLabels,
            AAR_OT_CheckSourceLabels,
            AAR_OT_LinkArmatures,
            AAR_OT_Retarget,
            AAR_PT_Panel)



def register():
    for c in classes:
        bpy.utils.register_class(c)
    AAR_RegisterProps()

def unregister():
    AAR_DelProps()
    for c in classes:
        bpy.utils.unregister_class(c)