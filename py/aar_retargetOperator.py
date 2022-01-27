import bpy
from bpy.types import Operator



def print_StrList(self, strList):
    List = "["
    for n in strList:
        List += n + ", "
    List += "]"
    self.report({'INFO'}, List)


def checkStart_End(self, member, member_end_List, member_start_List, member_start_group, pose_bones, armature_bones, base_bone_name):          # returns if the check failed (=> False if everything is ok)
    for end_bone_name in member_end_List:
        start_bone_name = ""
        curBone = pose_bones[end_bone_name]
        searchingStart = member_start_group is not None
        searchingBase = True
        
        # --------------- Searching ----------------
        while curBone.parent is not None:
            curBone = curBone.parent
            if searchingStart:
                if curBone.bone_group == member_start_group:
                    start_bone_name = curBone.name
                    searchingStart = False
                    continue
            if curBone.name == base_bone_name:
                searchingBase = False
                break
        
        # ---------------- Checking ----------------
        # Base bone Check
        if searchingBase:
            self.report({'ERROR'}, member + " Bone '" + end_bone_name + "' is not a child of the Base bone '" + base_bone_name + "'.")            
            return True
        
        # Start not already used Check
        if start_bone_name in member_start_List:
            self.report({'WARNING'}, member + " Start bone '" + start_bone_name + "' already used as start of another bone.\nCannot use it for " + member + " End bone '" + end_bone_name + "'.")
            searchingStart = True     # This arm start has already been used by another arm-end
        
        # Start not parented Check
        start_bone_Final_name = end_bone_name if searchingStart else start_bone_name
        start_bone_Final = armature_bones[start_bone_Final_name]
        if (start_bone_Final.parent is not None) & (start_bone_Final.use_connect):
            self.report({'ERROR'}, member + " Start bone '" + start_bone_Final_name + "' must not be connected to a parent.\nEither use 'Keep Offset' or no parent.")
            return True
        
        member_start_List.append(None if searchingStart else start_bone_name)
    
    return False



def checkArmatureLabels(self, obj):
    if obj.type != "ARMATURE":
        return
    
    armature = obj.data
    bone_groups = obj.pose.bone_groups
    pose_bones = obj.pose.bones
    
    # --------------- Preparation ---------------
    if not "AAR_Base" in bone_groups:
        self.report({'ERROR'}, "No bone labelled as Base.\nThere must be one and only one Base bone.")
        obj.data.aar_labelChecked = False
        return;
    base_Group = bone_groups["AAR_Base"]
    base_Name = ""
    base_found = False
    
    head_Group = bone_groups["AAR_Head"] if "AAR_Head" in bone_groups else None
    head_Names = []
    neck_Group = bone_groups["AAR_Neck"] if "AAR_Neck" in bone_groups else None
    neck_Names = []
    arm_Group = bone_groups["AAR_Arm End"] if "AAR_Arm End" in bone_groups else None
    arm_Names = []
    leg_Group = bone_groups["AAR_Leg End"] if "AAR_Leg End" in bone_groups else None
    leg_Names = []
    wing_Group = bone_groups["AAR_Wing End"] if "AAR_Wing End" in bone_groups else None
    wing_Names = []
    tail_Group = bone_groups["AAR_Tail End"] if "AAR_Tail End" in bone_groups else None
    tail_Names = []
    
    
    # --------------- Hierarchy Loop ---------------
    for b in pose_bones:
        
        # ---------------- Get Base ----------------
        
        if b.bone_group == base_Group:
            if not base_found:
                base_Name = b.name
                base_found = True
            else:
                self.report({'ERROR'}, "Base is associated to more than one bone.\nThere must be one and only one Base bone.")
                obj.data.aar_labelChecked = False
                return;
            
        # ------------------------------------------
        
        elif b.bone_group == head_Group:
            head_Names.append(b.name)
        elif b.bone_group == neck_Group:
            neck_Names.append(b.name)
        elif b.bone_group == arm_Group:
            arm_Names.append(b.name)
        elif b.bone_group == leg_Group:
            leg_Names.append(b.name)
        elif b.bone_group == wing_Group:
            wing_Names.append(b.name)
        elif b.bone_group == tail_Group:
            tail_Names.append(b.name)
        
    
    # ----------------- Check Base -----------------
    if not base_found:
        self.report({'ERROR'}, "No bone labelled as Base.\nThere must be one and only one Base bone.")
        obj.data.aar_labelChecked = False
        return;
    elif (armature.bones[base_Name].parent is not None) & (armature.bones[base_Name].use_connect):
        self.report({'ERROR'}, "Base bone must not be connected to a parent.\nEither use 'Keep Offset' or no parent.")
        obj.data.aar_labelChecked = False
        return;
    # save base bone name
    # ----------------------------------------------
    
    # save head bone name if exists
    # save neck bone name if exists
    
    
    # ----------------- Check Arm ------------------
    arm_Names_S = []
    if checkStart_End(self, "Arm", arm_Names, arm_Names_S, bone_groups["AAR_Arm Start"] if "AAR_Arm Start" in bone_groups else None, pose_bones, armature.bones, base_Name):
        obj.data.aar_labelChecked = False
        return;
    
    # ----------------- Check Leg ------------------
    leg_Names_S = []
    if checkStart_End(self, "Leg", leg_Names, leg_Names_S, bone_groups["AAR_Leg Start"] if "AAR_Leg Start" in bone_groups else None, pose_bones, armature.bones, base_Name):
        obj.data.aar_labelChecked = False
        return;
    
    # ----------------- Check Wing -----------------
    wing_Names_S = []
    if checkStart_End(self, "Wing", wing_Names, wing_Names_S, bone_groups["AAR_Wing Start"] if "AAR_Wing Start" in bone_groups else None, pose_bones, armature.bones, base_Name):
        obj.data.aar_labelChecked = False
        return;
    
    # ----------------- Check Tail -----------------
    tail_Names_S = []
    if checkStart_End(self, "Tail", tail_Names, tail_Names_S, bone_groups["AAR_Tail Start"] if "AAR_Tail Start" in bone_groups else None, pose_bones, armature.bones, base_Name):
        obj.data.aar_labelChecked = False
        return;
    

    # ----------------------------------------------
    
    #self.report({'INFO'}, base_Name)
    obj.data.aar_labelChecked = True
    
    
    
    
    
    
    

class AAR_OT_CheckLabels(Operator):
    bl_idname = "pose.aar_check_labels"
    bl_label = "Check Bone Labels"
    bl_description = "Check the armature's bones label, and store important data needed by the Retarget Operation"
   

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if not obj.data.aar_labelChecked:
                    return True
        return False


    def execute(self, context):
        checkArmatureLabels(self, context.object)
        return {'FINISHED'}
    
    
    
class AAR_OT_CheckSourceLabels(Operator):
    bl_idname = "pose.aar_check_source_labels"
    bl_label = "Check Source's Bones Labels"
    bl_description = "Check the Source's bones label, and store important data needed by the Retarget Operation"
   

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if obj.data.aar_source is not None:
                    if not obj.data.aar_source.data.aar_labelChecked:
                        return True
        return False


    def execute(self, context):
        checkArmatureLabels(self, context.object.data.aar_source)
        return {'FINISHED'}




class AAR_OT_Retarget(Operator):
    bl_idname = "pose.aar_retarget"
    bl_label = "Retarget Actions"
    bl_description = "Retarget the selected actions from the source armature to the active armature"
   

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if obj.data.aar_source is not None:
                    if obj.data.aar_labelChecked & obj.data.aar_source.data.aar_labelChecked:
                        return True
        return False


    def execute(self, context):
        return {'FINISHED'}
    
    

if __name__ == "__main__":
    bpy.utils.register_class(AAR_OT_CheckLabels)
    bpy.utils.register_class(AAR_OT_CheckSourceLabels)
    bpy.utils.register_class(AAR_OT_Retarget)