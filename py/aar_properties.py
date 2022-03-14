import bpy
from mathutils import Quaternion
from mathutils import Vector




def aar_prop_poll_armature(self, object):
    return object.type == 'ARMATURE'

def aar_prop_poll_action(self, object):
    return True #object.type == 'ARMATURE'




def AAR_RegisterProps():
    bpy.types.Armature.aar_source = bpy.props.PointerProperty(type=bpy.types.Object, poll=aar_prop_poll_armature)
    bpy.types.Armature.aar_labelChecked = bpy.props.BoolProperty(default=False)
    bpy.types.Armature.aar_sourceLinked = bpy.props.BoolProperty(default=False)
    bpy.types.Armature.aar_actionSelected = bpy.props.PointerProperty(type=bpy.types.Action)
    bpy.types.Armature.aar_actionsToCopy = bpy.props.CollectionProperty(type=AAR_PROP_ActionListProperty)
    #symetry Axis
    
    bpy.types.Armature.aar_baseBone = bpy.props.StringProperty()
    bpy.types.Armature.aar_heads = bpy.props.CollectionProperty(type=AAR_PROP_SingleBoneProperty)
    bpy.types.Armature.aar_necks = bpy.props.CollectionProperty(type=AAR_PROP_SingleBoneProperty)
    
    bpy.types.Armature.aar_arms = bpy.props.CollectionProperty(type=AAR_PROP_MemberProperty)
    bpy.types.Armature.aar_legs = bpy.props.CollectionProperty(type=AAR_PROP_MemberProperty)
    bpy.types.Armature.aar_wings = bpy.props.CollectionProperty(type=AAR_PROP_MemberProperty)
    bpy.types.Armature.aar_tails = bpy.props.CollectionProperty(type=AAR_PROP_MemberProperty)
    
    bpy.types.Armature.aar_head_links = bpy.props.CollectionProperty(type=AAR_PROP_SingleBoneLink)
    bpy.types.Armature.aar_neck_links = bpy.props.CollectionProperty(type=AAR_PROP_SingleBoneLink)
    
    bpy.types.Armature.aar_arm_links = bpy.props.CollectionProperty(type=AAR_PROP_MemberLink)
    bpy.types.Armature.aar_leg_links = bpy.props.CollectionProperty(type=AAR_PROP_MemberLink)
    bpy.types.Armature.aar_wing_links = bpy.props.CollectionProperty(type=AAR_PROP_MemberLink)
    bpy.types.Armature.aar_tail_links = bpy.props.CollectionProperty(type=AAR_PROP_MemberLink)
    
    bpy.types.Action.aar_useGround = bpy.props.BoolProperty()
    bpy.types.Action.aar_loopIdle = bpy.props.BoolProperty(default=True)
    
    
def AAR_DelProps():
    del bpy.types.Armature.aar_source
    del bpy.types.Armature.aar_labelChecked
    del bpy.types.Armature.aar_sourceLinked
    del bpy.types.Armature.aar_actionSelected
    del bpy.types.Armature.aar_actionsToCopy
    
    del bpy.types.Armature.aar_baseBone
    del bpy.types.Armature.aar_arms
    del bpy.types.Armature.aar_legs
    del bpy.types.Armature.aar_wings
    del bpy.types.Armature.aar_tails
    
    del bpy.types.Armature.aar_arm_links
    del bpy.types.Armature.aar_leg_links
    del bpy.types.Armature.aar_wing_links
    del bpy.types.Armature.aar_tail_links
    
    del bpy.types.Action.aar_useGround
    del bpy.types.Action.aar_loopIdle





class AAR_PROP_ActionListProperty(bpy.types.PropertyGroup):
    actionProp : bpy.props.PointerProperty(type=bpy.types.Action) #, poll=aar_prop_poll_action)


class AAR_PROP_SingleBoneProperty(bpy.types.PropertyGroup):
    string : bpy.props.StringProperty()
    position : bpy.props.FloatVectorProperty()
    
    
class AAR_PROP_MemberProperty(bpy.types.PropertyGroup):
    hasIK : bpy.props.BoolProperty(default=False)
    
    originBone : bpy.props.StringProperty()
    finalBone : bpy.props.StringProperty()
    IK_controllerBone : bpy.props.StringProperty()
    IK_poleBone : bpy.props.StringProperty()
    
    memberOrigin : bpy.props.FloatVectorProperty()
    memberVector : bpy.props.FloatVectorProperty()
    memberLenght : bpy.props.FloatProperty()
    numberBone : bpy.props.IntProperty()
    
    originBoneOrientation : bpy.props.FloatVectorProperty()
    finalBoneOrientation : bpy.props.FloatVectorProperty()
    IK_contBoneOrientation : bpy.props.FloatVectorProperty()


class AAR_PROP_Quaternion(bpy.types.PropertyGroup):
    w : bpy.props.FloatProperty(default=1)
    x : bpy.props.FloatProperty(default=0)
    y : bpy.props.FloatProperty(default=0)
    z : bpy.props.FloatProperty(default=0)
    
    def quat_get(self):
        return Quaternion((self.w, self.x, self.y, self.z))
    
    def quat_setQuat(self, q):
        self.w = q.w
        self.x = q.x
        self.y = q.y
        self.z = q.z
        
    def quat_setFromTo(self, fromOrientation, toOrientation):
        frO_Vect = Vector((fromOrientation[0], fromOrientation[1], fromOrientation[2]))
        toO_Vect = Vector((toOrientation[0], toOrientation[1], toOrientation[2]))
        a = frO_Vect.cross(toO_Vect)
        self.x = a.x
        self.y = a.y
        self.z = a.z        
        self.w = 1 + frO_Vect.dot(toO_Vect)
    

class AAR_PROP_SingleBoneLink(bpy.types.PropertyGroup):
    myMember_ID : bpy.props.IntProperty(default=-1)
    otherMember_ID : bpy.props.IntProperty(default=-1)
    

class AAR_PROP_MemberLink(bpy.types.PropertyGroup):
    myMember_ID : bpy.props.IntProperty(default=-1)
    otherMember_ID : bpy.props.IntProperty(default=-1) 
    offsetVector : bpy.props.FloatVectorProperty()
    offsetRot_Start : bpy.props.PointerProperty(type=AAR_PROP_Quaternion)
    offsetRot_End : bpy.props.PointerProperty(type=AAR_PROP_Quaternion)
    #offsetRot_Cont : bpy.props.PointerProperty(type=AAR_PROP_Quaternion)
    isMirrored : bpy.props.BoolProperty(default=True)
    
    
    
    
if __name__ == '__main__':
    bpy.utils.register_class(AAR_PROP_ActionListProperty)
    bpy.utils.register_class(AAR_PROP_SingleBoneProperty)
    bpy.utils.register_class(AAR_PROP_MemberProperty)
    bpy.utils.register_class(AAR_PROP_Quaternion)    
    bpy.utils.register_class(AAR_PROP_MemberLink)
    