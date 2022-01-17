import bpy

from bpy.types import Panel


class AAR_PT_Panel(Panel):
    #bl_idname = "ANIMATION_PT_Retargetter"
    bl_label = "Retargetter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_category = "Animation"
    
    #myBoolProp = bpy.props.BoolProperty(name='A bool flag', default=True)


    @classmethod
    def poll(cls, context):
        #return (context.object is not None)
        return ((context.object is not None) & (context.object.type == "ARMATURE")) #(context.object.mode == "POSE"))
    

    def draw(self, context):
        label_name = ["Base", "Head", "Neck", "Arm Start", "Arm End", "Leg Start", "Leg End", "Wing Start", "Wing End", "Tail Start", "Tail End"]
        label_normal = [[1,0.4,0.3],[1,0,0.4],[1,0.6,0.8],[0.5,0.8,1],[0,0.8,1],[0.5,0.6,1],[0,0.2,1],[0.7,1,0.8],[0,1,0.3],[0.8,0.5,1],[0.6,0,1]]
        label_select = [[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75],[0.75,0.75,0.75]]
        label_active = [[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,1]]
        
        layout = self.layout
        layout.prop(context.object.data, "aar_source", text="Source")
        
        layout.separator()
        layout.label(text="Label Bones")
        
        for i in range(0, len(label_name)):
            row = layout.row()
            col = row.column()
            col.label(text=label_name[i] + ":")
            col = row.column()
            op = col.operator("pose.aar_label_bone", text="Label", icon="ADD")
            op.aar_group = "AAR_" + label_name[i]
            op.aar_colorNormal = label_normal[i]
            op.aar_colorSelect = label_select[i]
            op.aar_colorActive = label_active[i]
            
            col = row.column()
            op = col.operator("pose.aar_unlabel_bone", text="Unlabel", icon="REMOVE")
            op.aar_group = "AAR_" + label_name[i]
        
        

if __name__ == '__main__':
    bpy.utils.register_class(AAR_PT_Panel)