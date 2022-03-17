import bpy

from bpy.types import Panel


def actionLayout(subBox, action):
    row = subBox.row()
    row.label(text=action.name, icon="ACTION")
    row.prop(action, "aar_loopIdle", text="", icon="POSE_HLT")
    row.prop(action, "aar_useGround", text="", icon="GRID")
    op = row.operator("pose.aar_unregister_action", text="", icon="PANEL_CLOSE")
    op.aar_action = action.name
    

class AAR_PT_Panel(Panel):
    #bl_idname = "ANIMATION_PT_Retargetter"
    bl_label = "Retargetter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_category = "Animation"
    
    #aar_retargetStepByStep = bpy.props.BoolProperty(default=False)
        

    @classmethod
    def poll(cls, context):
        #return (context.object is not None)
        return ((context.object is not None) & (context.object.type == "ARMATURE")) #(context.object.mode == "POSE"))
    
    


    def draw(self, context):
        label_name = ["Base", "Body", "Head", "Neck", "Arm Start", "Arm End", "Leg Start", "Leg End", "Wing Start", "Wing End", "Tail Start", "Tail End"]
        label_normal = [[1,0.4,0.3],[1,0.8,0.15],[1,0,0.4],[1,0.6,0.8],[0.5,0.8,1],[0,0.8,1],[0.5,0.6,1],[0,0.2,1],[0.7,1,0.8],[0,1,0.3],[0.8,0.5,1],[0.6,0,1]]
        label_select = [0.75,0.75,0.75]
        label_active = [1,1,1]
        
        
        layout = self.layout
        layout.label(text="Source")
        row = layout.row()
        row.prop(context.object.data, "aar_source", text="")
        row.operator("pose.aar_check_source_labels", text="Check Source Labels", icon="CHECKMARK")
        
        
        #########################################################
        
        
        layout.separator()
        layout.label(text="Actions")
        box = layout.box()
        for act in context.object.data.aar_actionsToCopy:
            if act.actionProp is None:
                continue
            subBox = box.box()
            actionLayout(subBox, act.actionProp)
            
        row = layout.row()
        col = row.column()
        #col.separator()
        col.prop(context.object.data, "aar_actionSelected", text="")
        col = row.column()
        col.operator("pose.aar_register_action", text="Add Action", icon="ADD")
        col.operator("pose.aar_unregister_actions", text="Clear All", icon="PANEL_CLOSE")
        
        
        #########################################################
        
        
        layout.separator()
        layout.label(text="Label Bones")
        box = layout.box()
        
        for i in range(0, len(label_name)):
            row = box.row()
            col = row.column()
            col.label(text=label_name[i] + ":")
            col = row.column()
            op = col.operator("pose.aar_label_bone", text="Label", icon="ADD")
            op.aar_group = "AAR_" + label_name[i]
            op.aar_colorNormal = label_normal[i]
            op.aar_colorSelect = label_select
            op.aar_colorActive = label_active
            
            col = row.column()
            op = col.operator("pose.aar_unlabel_bone", text="Unlabel", icon="REMOVE")
            op.aar_group = "AAR_" + label_name[i]
        
        row = layout.row()
        op_auto = row.operator("pose.aar_auto_label", text="Auto-Label", icon="PRESET")
        op_uAll = row.operator("pose.aar_unlabel_bones_all", text="Unlabel All Groups", icon="PANEL_CLOSE")
        for label in label_name:
            text = "AAR_" + label
            group_auto = op_auto.aar_groups.add()
            group_auto.groupName = text
            group_uAll = op_uAll.aar_groups.add()
            group_uAll.groupName = text
        
        
        
        #########################################################
        
        
        layout.separator()
        
        row = layout.row()
        row.label(text="Retarget")
        row.prop(context.scene, "aar_retargetStepByStep", text="Step by step", toggle =1, icon="LONGDISPLAY")
        
        if context.scene.aar_retargetStepByStep:
            col = layout.column()        
            col.operator("pose.aar_reset_checks_links", text="Reset Checks & Links", icon="UNLINKED")
            col.operator("pose.aar_check_labels", text="Check Object Labels", icon="CHECKMARK")
            col.operator("pose.aar_link_armatures", text="Link To Source Armature", icon="RESTRICT_INSTANCED_OFF")
            col.operator("pose.aar_retarget", text="Retarget", icon="IMPORT")
        
        else:
            layout.operator("pose.aar_retarget_full", text="Retarget (Full Process)", icon="IMPORT")
        
        
        

if __name__ == '__main__':
    bpy.utils.register_class(AAR_PT_Panel)