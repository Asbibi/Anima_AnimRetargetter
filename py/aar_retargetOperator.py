import bpy
from bpy.types import Operator
from math import sqrt
from math import degrees as deg
from mathutils import Matrix as mat
from mathutils import Quaternion as quat
from mathutils import Vector as vect



# Debug, not used
def print_StrList(self, strList):
    List = "["
    for n in strList:
        List += n + ", "
    List += "]"
    self.report({'INFO'}, List)

# Actually Used
def norm(vector):
    return sqrt(vector[0]*vector[0] + vector[1]*vector[1] + vector[2]*vector[2])


# ==============================================================================================================



def checkStart_End(self, obj, member, member_end_List, member_start_List, member_start_group, pose_bones, armature_bones, base_bone_name, memberCollectionProperty):          # returns if the check failed (=> False if everything is ok)
    memberCollectionProperty.clear()

    for end_bone_name in member_end_List:
        original_end_bone_name = end_bone_name
        # ---------- Check Constraints -----------
        checkingConstraints = True        
        while checkingConstraints:
            checkingConstraints = False
            curConstraints = pose_bones[end_bone_name].constraints
            if len(curConstraints) == 0:
                checkingConstraints = False
                
            for c in reversed(curConstraints):
                if c.type == "COPY_LOCATION":
                    if obj is not c.target:
                        self.report({'ERROR'}, member + " Bone '" + end_bone_name + "' has a 'COPY_LOCATION' constraint that has an incorrect Target.\nSet the target to a " + obj.name + "'s bone.")
                        return True
                    else:
                        if c.subtarget == "":
                            self.report({'ERROR'}, member + " Bone '" + end_bone_name + "' has a 'COPY_LOCATION' constraint that has an incorrect Target.\nSet the target to a " + obj.name + "'s bone.")
                            return True
                        end_bone_name = c.subtarget
                        self.report({'WARNING'}, end_bone_name)
                        checkingConstraints = True
                        break
                    
        checkingIKController = False
        cont_bone_name = end_bone_name
        pole_bone_name = ""
        curConstraints = pose_bones[end_bone_name].constraints
        for c in reversed(curConstraints):
            if c.type == "IK":
                if obj is not c.target:
                    self.report({'ERROR'}, member + " Bone '" + end_bone_name + "' has a 'IK' constraint that has an incorrect Target.\nSet the target to a " + obj.name + "'s bone.")
                    return True
                else:
                    if c.subtarget == "":
                        self.report({'ERROR'}, member + " Bone '" + end_bone_name + "' has a 'IK' constraint that has an incorrect Target.\nSet the target to a " + obj.name + "'s bone.")
                        return True
                    cont_bone_name = c.subtarget
                    #self.report({'WARNING'}, cont_bone_name)
                    checkingIKController = True
                    if obj is c.pole_target:
                        pole_bone_name = c.pole_subtarget                    
                    break        
                
        while checkingIKController:
            checkingIKController = False
            curConstraints = pose_bones[cont_bone_name].constraints
            if len(curConstraints) == 0:
                checkingIKController = False
                
            for c in reversed(curConstraints):
                if c.type == "COPY_LOCATION":
                    if obj is not c.target:
                        self.report({'ERROR'}, member + " Bone Controller '" + cont_bone_name + "' has a 'COPY_LOCATION' constraint that has an incorrect Target.\nSet the target to a " + obj.name + "'s bone.")
                        return True
                    else:
                        if c.subtarget == "":
                            self.report({'ERROR'}, member + " Bone Controller '" + cont_bone_name + "' has a 'COPY_LOCATION' constraint that has an incorrect Target.\nSet the target to a " + obj.name + "'s bone.")
                            return True
                        cont_bone_name = c.subtarget
                        #self.report({'WARNING'}, cont_bone_name)
                        checkingIKController = True
                        break
                
            
            
        
        # --------------- Prepare ----------------
        start_bone_name = ""
        curBone = pose_bones[end_bone_name]
        searchingStart = True
        groupStartExists = member_start_group is not None
        searchingBase = True
        numberBone_EndExcluded = 0
        memberLenght = curBone.length
        memberVector = curBone.vector
        
        # --------------- Searching ----------------
        while curBone.parent is not None:
            curBone = curBone.parent
            if groupStartExists:
                if searchingStart:
                    numberBone_EndExcluded += 1
                    memberLenght += curBone.length
                    memberVector += curBone.vector
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
        
        # Update array to ensure the not already used check
        if not searchingStart:
            member_start_List.append(start_bone_name)
            
                
        # Add Result to Data's Collection Property
        memberProp = memberCollectionProperty.add()
        memberProp.hasIK = (not searchingStart) and (cont_bone_name != end_bone_name)
        memberProp.originBone = end_bone_name if searchingStart else start_bone_name
        memberProp.finalBone = original_end_bone_name
        memberProp.IK_controllerBone = cont_bone_name if memberProp.hasIK else ""
        memberProp.IK_poleBone = pole_bone_name
        memberProp.memberOrigin = start_bone_Final.tail_local
        memberProp.memberVector = armature_bones[memberProp.finalBone].tail_local - start_bone_Final.tail_local #memberVector
        memberProp.memberLenght = memberLenght
        memberProp.finalBoneOrientation = armature_bones[memberProp.finalBone].vector.normalized()
        
    return False



def checkHeads_Necks(self, armature, bones, head_Group, neck_Group, base_bone_name, head_Names, neck_Names):
    # Check neck is related to base
    for neck in neck_Names:
        curBone = bones[neck]
        searchingBase = True
        while (curBone.parent is not None) and (searchingBase):
            curBone = curBone.parent
            if curBone.name == base_bone_name:
               searchingBase = False
        if searchingBase:
            self.report({'ERROR'}, "Neck Bone '" + neck + "' isn't parented to Base Bone '" + base_bone_name + "'.")
            return True
        
        
    # Check head is related to base && if related to a neck
    neck_Checked = [False for i in range(len(neck_Names))] 
    for head in head_Names:
        curBone = bones[head]
        searchingBase = True
        while (curBone.parent is not None) and (searchingBase):
            curBone = curBone.parent
            if curBone.name == base_bone_name:
               searchingBase = False
               break
            for i in range(len(neck_Names)):
               if curBone.name == neck_Names[i]:
                   neck_Checked[i] = True
                   break
               
        if searchingBase:
            self.report({'ERROR'}, "Head Bone '" + head + "' isn't parented to Base Bone '" + base_bone_name + "'.")
            return True
            
        
    # Check every neck is related to an head
    for i in range(len(neck_Names)):
        if not neck_Checked[i]:
            self.report({'ERROR'}, "Neck Bone '" + neck_Names[i] + "' isn't the parent of any Head bone.")
            return True


    # Actually add Head & neck to armature properties
    armature.aar_necks.clear()
    armature.aar_heads.clear()
    
    for neck in neck_Names:
        n_prop = armature.aar_necks.add()
        n_prop.string = neck
        n_prop.position = bones[neck].tail_local
        
    for head in head_Names:
        n_prop = armature.aar_heads.add()
        n_prop.string = head
        n_prop.position = bones[head].tail_local
        
        


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
        
        if b.bone_group is None:
            continue
        
        # ---------------- Get Base ----------------
        
        elif b.bone_group == base_Group:
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
    # Base found ?
    if not base_found:
        self.report({'ERROR'}, "No bone labelled as Base.\nThere must be one and only one Base bone.")
        obj.data.aar_labelChecked = False
        return
    # Has a parent ?
    elif (armature.bones[base_Name].parent is not None) & (armature.bones[base_Name].use_connect):
        self.report({'ERROR'}, "Base bone must not be connected to a parent.\nEither use 'Keep Offset' or no parent.")
        obj.data.aar_labelChecked = False
        return
    # Has a constraint ?
    elif len(pose_bones[base_Name].constraints) != 0:
        self.report({'WARNING'}, "Base bone shouldn't be have any Bone Constraint.")
        
    # save base bone name
    bpy.types.Armature.aar_baseBone = base_Name
    # ----------------------------------------------
    
    
    # ------------ Check Heads & Necks -------------
    if checkHeads_Necks(self, armature, armature.bones, head_Group, neck_Group, base_Name, head_Names, neck_Names):
        obj.data.aar_labelChecked = False
        return
    
    # ----------------- Check Arm ------------------
    arm_Names_Combine = []
    if checkStart_End(self, obj, "Arm", arm_Names, arm_Names_Combine, bone_groups["AAR_Arm Start"] if "AAR_Arm Start" in bone_groups else None, pose_bones, armature.bones, base_Name, armature.aar_arms):
        obj.data.aar_labelChecked = False
        return
    
    # ----------------- Check Leg ------------------
    leg_Names_Combine = []
    if checkStart_End(self, obj, "Leg", leg_Names, leg_Names_Combine, bone_groups["AAR_Leg Start"] if "AAR_Leg Start" in bone_groups else None, pose_bones, armature.bones, base_Name, armature.aar_legs):
        obj.data.aar_labelChecked = False
        return
    
    # ----------------- Check Wing -----------------
    wing_Names_Combine = []
    if checkStart_End(self, obj, "Wing", wing_Names, wing_Names_Combine, bone_groups["AAR_Wing Start"] if "AAR_Wing Start" in bone_groups else None, pose_bones, armature.bones, base_Name, armature.aar_wings):
        obj.data.aar_labelChecked = False
        return
    
    # ----------------- Check Tail -----------------
    tail_Names_Combine = []
    if checkStart_End(self, obj, "Tail", tail_Names, tail_Names_Combine, bone_groups["AAR_Tail Start"] if "AAR_Tail Start" in bone_groups else None, pose_bones, armature.bones, base_Name, armature.aar_tails):
        obj.data.aar_labelChecked = False
        return
    

    # ----------------------------------------------
    
    #self.report({'INFO'}, base_Name)
    obj.data.aar_labelChecked = True
    
    


# ==============================================================================================================


def linkArmatureMembers(self, myMembers, otherMembers, memberLinks):
    memberLinks.clear()
    if len(myMembers) == 0:
        return
    
    if len(otherMembers) == 0:
        self.report({'WARNING'}, "No members on the source armature corresponding to that Category --> Skipped")
        return
            
    
    for i in range(len(myMembers)):
        best_other = 0
        best_offset = [myMembers[i].memberOrigin[0] - otherMembers[0].memberOrigin[0], myMembers[i].memberOrigin[1] - otherMembers[0].memberOrigin[1], myMembers[i].memberOrigin[2] - otherMembers[0].memberOrigin[2]]
        best_dist = norm(best_offset)
        best_quat = quat()
        for j in range(0, len(otherMembers)):
            offsetVector = [myMembers[i].memberOrigin[0] - otherMembers[j].memberOrigin[0], myMembers[i].memberOrigin[1] - otherMembers[j].memberOrigin[1], myMembers[i].memberOrigin[2] - otherMembers[j].memberOrigin[2]]
            dist = norm(offsetVector)
            if dist < best_dist:
                best_dist = dist
                best_other = j
                best_offset = offsetVector
                
        
        link = memberLinks.add()
        link.myMember_ID = i
        link.otherMember_ID = best_other
        link.offsetVector = best_offset
        


def linkArmatureSingleBones(self, myLabels, otherLabels, labelLinks):
    labelLinks.clear()
    if len(myLabels) == 0:
        return
    
    if len(otherLabels) == 0:
        self.report({'WARNING'}, "No members on the source armature corresponding to that Category --> Skipped")
        return
            
    
    for i in range(len(myLabels)):
        my_l = myLabels[i]
        best_other = 0
        offset = vect((my_l.position[0] - otherLabels[0].position[0], my_l.position[1] - otherLabels[0].position[1], my_l.position[2] - otherLabels[0].position[2]))
        best_dist = norm(offset)
        for j in range(0, len(otherLabels)):
            other_l = otherLabels[j]
            offset = vect((my_l.position[0] - other_l.position[0], my_l.position[1] - other_l.position[1], my_l.position[2] - other_l.position[2]))
            dist = norm(offset)
            if dist < best_dist:
                best_dist = dist
                best_other = j                
        
        link = labelLinks.add()
        link.myMember_ID = i
        link.otherMember_ID = best_other
        
            

# ==============================================================================================================



def getDataPath_FCU(boneName, type):
    return "pose.bones[\"" + boneName + "\"]." + type



def getRotationOffset(fromOrientation, toOrientation):
    frO_Vect = vect((fromOrientation[0], fromOrientation[1], fromOrientation[2]))
    toO_Vect = vect((toOrientation[0], toOrientation[1], toOrientation[2]))    
    return frO_Vect.rotation_difference(toO_Vect)




def printVec(self, vec, name = ""):
    self.report({'INFO'}, name + "[%.3f, %.3f, %.3f]" % (vec[0],vec[1],vec[2]))
    
def printVecDeg(self, vec, name = ""):
    self.report({'INFO'}, name + "[%.3f, %.3f, %.3f]" % (deg(vec[0]),deg(vec[1]),deg(vec[2])))

def printMat(self, matrix, name = "------"):
    self.report({'INFO'}, "------" + name + "------")
    self.report({'INFO'}, "|%.3f, %.3f, %.3f|" % (matrix[0][0],matrix[0][1],matrix[0][2]))
    self.report({'INFO'}, "|%.3f, %.3f, %.3f|" % (matrix[1][0],matrix[1][1],matrix[1][2]))
    self.report({'INFO'}, "|%.3f, %.3f, %.3f|" % (matrix[2][0],matrix[2][1],matrix[2][2]))
    self.report({'INFO'}, "------------------")
    



def retargetLoc(my_action, other_action, my_mBone, other_mBone, proportionalFactor=1):
    my_mDataPath = getDataPath_FCU(my_mBone, "location")
    other_mDataPath = getDataPath_FCU(other_mBone, "location")
    
    for axis in range(0,3):
        other_fcu = other_action.fcurves.find(data_path=other_mDataPath, index=axis)        
        if other_fcu is None:
            continue
        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath, index=axis, action_group=my_mBone)
        for kp in other_fcu.keyframe_points:
            my_fcu.keyframe_points.insert(kp.co[0], proportionalFactor * kp.co[1])
            
            

def retargetLoc_withRotationOffset(my_action, other_action, my_mBone, other_mBone, proportionalFactor, rotationOffset, fromMatrix, toMatrix):
    my_mDataPath = getDataPath_FCU(my_mBone, "location")
    other_mDataPath = getDataPath_FCU(other_mBone, "location")
    
    other_fcus = []    
    for axis in range(0,3):
        other_fcus.append(other_action.fcurves.find(data_path=other_mDataPath, index=axis))
    
    # Get frames
    frames = []
    for other_fcu in other_fcus:
        if other_fcu is None:
            continue
        
        for kp in other_fcu.keyframe_points:
            if not(kp.co[0] in frames) :
                frames.append(kp.co[0])
    
    # Get Pos
    posValues = []
    for f in frames:
        v = []
        for axis in range(0,3):
            if other_fcus[axis] is None:
                v.append(0)
            else:
                v.append(other_fcus[axis].evaluate(f) * proportionalFactor)
        posValues.append(vect((v[0],v[1],v[2])))
        
    # Offset Pos
    for i in range(len(posValues)):
        v = fromMatrix @ posValues[i]
        v.rotate(rotationOffset)
        posValues[i] = toMatrix @ v
            
    # Set new keyframes
    for axis in range(0,3):        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath, index=axis, action_group=my_mBone)
        for i in range(len(frames)):            
            my_fcu.keyframe_points.insert(frames[i], posValues[i][axis])


def retargetLoc_fromRotationEuler(my_action, other_action, my_mBone, other_mBone, offsetPosition, fromMatrix, toMatrix):
    my_mDataPath = getDataPath_FCU(my_mBone, "location")
    other_mDataPath = getDataPath_FCU(other_mBone, "rotation_euler")
    
    other_fcus = []    
    for axis in range(0,3):
        other_fcus.append(other_action.fcurves.find(data_path=other_mDataPath, index=axis))
    
    # Get frames
    frames = []
    for other_fcu in other_fcus:
        if other_fcu is None:
            continue
        
        for kp in other_fcu.keyframe_points:
            if not(kp.co[0] in frames) :
                frames.append(kp.co[0])
    
    # Get Euler Rots
    rotValues = []
    for f in frames:
        r = []
        for axis in range(0,3):
            if other_fcus[axis] is None:
                r.append(0)
            else:
                r.append(other_fcus[axis].evaluate(f))
        rotValues.append(quat((r[0],r[1],r[2]), 'XYZ'))
        
    # Offset Pos
    posValues = []
    for i in range(len(posValues)):
        v = fromMatrix @ offsetPosition
        v.rotate(quatValues[i])
        posValues.append(toMatrix @ v)
            
    # Set new keyframes
    for axis in range(0,3):        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath, index=axis, action_group=my_mBone)
        for i in range(len(frames)):            
            my_fcu.keyframe_points.insert(frames[i], posValues[i][axis])
            
            
def retargetLoc_fromRotationQuat(my_action, other_action, my_mBone, other_mBone, offsetPosition, fromMatrix, toMatrix):
    my_mDataPath = getDataPath_FCU(my_mBone, "location")
    other_mDataPath = getDataPath_FCU(other_mBone, "rotation_quaternion")
    q_identity = quat()
    
    other_fcus = []    
    for axis in range(0,4):
        other_fcus.append(other_action.fcurves.find(data_path=other_mDataPath, index=axis))
    
    # Get frames
    frames = []
    for other_fcu in other_fcus:
        if other_fcu is None:
            continue
        
        for kp in other_fcu.keyframe_points:
            if not(kp.co[0] in frames) :
                frames.append(kp.co[0])
    
    # Get Quats
    quatValues = []
    for f in frames:
        q = []
        for axis in range(0,4):
            if other_fcus[axis] is None:
                q.append(q_identity[axis])
            else:
                q.append(other_fcus[axis].evaluate(f))
        quatValues.append(quat((q[0],q[1],q[2],q[3])))
        
    # Offset Pos
    posValues = []
    for i in range(len(quatValues)):
        v = fromMatrix @ offsetPosition
        v.rotate(quatValues[i])
        v = toMatrix @ v
        posValues.append(v)
            
    # Set new keyframes
    for axis in range(0,3):        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath, index=axis, action_group=my_mBone)
        for i in range(len(frames)):            
            my_fcu.keyframe_points.insert(frames[i], posValues[i][axis])


def retargetLoc_fromRotation(my_action, other_action, my_mBone, other_mBone, offsetPosition, fromMatrix, toMatrix, useQuat):
    if useQuat:
        retargetLoc_fromRotationQuat(my_action, other_action, my_mBone, other_mBone, offsetPosition, fromMatrix, toMatrix)
    else:
        retargetLoc_fromRotationEuler(my_action, other_action, my_mBone, other_mBone, offsetPosition, fromMatrix, toMatrix)



def retargetRot_fromLocation(my_action, other_action, my_mBone, other_mBone, initialDirection, fromMatrix):
    my_mDataPath_quat = getDataPath_FCU(my_mBone, "rotation_quaternion")
    my_mDataPath_euler = getDataPath_FCU(my_mBone, "rotation_euler")
    other_mDataPath = getDataPath_FCU(other_mBone, "location")
    q_identity = quat()
    
    other_fcus = []    
    for axis in range(0,3):
        other_fcus.append(other_action.fcurves.find(data_path=other_mDataPath, index=axis))
    
    # Get frames
    frames = []
    for other_fcu in other_fcus:
        if other_fcu is None:
            continue
        
        for kp in other_fcu.keyframe_points:
            if not(kp.co[0] in frames) :
                frames.append(kp.co[0])
    
    # Get Pos
    posValues = []
    for f in frames:
        v = []
        for axis in range(0,3):
            if other_fcus[axis] is None:
                v.append(0)
            else:
                v.append(other_fcus[axis].evaluate(f))
        posValues.append(vect((v[0],v[1],v[2])))
        
    # Offset Pos
    quatValues = []
    for i in range(len(posValues)):
        v = fromMatrix @ posValues[i]        
        quatValues.append(getRotationOffset(initialDirection, v))
            
    # Set new keyframes
    for axis in range(0,4):        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath_quat, index=axis, action_group=my_mBone)
        for i in range(len(frames)):            
            my_fcu.keyframe_points.insert(frames[i], quatValues[i][axis])
    for axis in range(0,3):        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath_euler, index=axis, action_group=my_mBone)
        for i in range(len(frames)):            
            my_fcu.keyframe_points.insert(frames[i], quatValues[i].to_euler()[axis])


            
def retargetRot_Euler(my_action, other_action, my_mBone, other_mBone, offset):
    my_mDataPath = getDataPath_FCU(my_mBone, "rotation_euler")
    other_mDataPath = getDataPath_FCU(other_mBone, "rotation_euler")
    
    for axis in range(0,3):
        other_fcu = other_action.fcurves.find(data_path=other_mDataPath, index=axis)        
        if other_fcu is None:
            continue
        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath, index=axis, action_group=my_mBone)
        for kp in other_fcu.keyframe_points:
            my_fcu.keyframe_points.insert(kp.co[0], deg(offset[axis]) + kp.co[1])
            
            
def retargetRot_Quat(my_action, other_action, my_mBone, other_mBone, offset):
    my_mDataPath = getDataPath_FCU(my_mBone, "rotation_quaternion")
    other_mDataPath = getDataPath_FCU(other_mBone, "rotation_quaternion")
    q_identity = quat()
    
    # Get original FCurves
    other_fcus = []    
    for axis in range(0,4):
        other_fcus.append(other_action.fcurves.find(data_path=other_mDataPath, index=axis))
    
    # Get frames
    frames = []
    for other_fcu in other_fcus:
        if other_fcu is None:
            continue
        
        for kp in other_fcu.keyframe_points:
            if not(kp.co[0] in frames) :
                frames.append(kp.co[0])
                
    # Get Quats
    quatValues = []
    for f in frames:
        q = []
        for axis in range(0,4):
            if other_fcus[axis] is None:
                q.append(q_identity[axis])
            else:
                q.append(other_fcus[axis].evaluate(f))
        quatValues.append(quat((q[0],q[1],q[2],q[3])))
                
    # Offset Quats
    for i in range(len(quatValues)):     
        quatValues[i].rotate(offset)
        
    # Set new keyframes
    for axis in range(0,4):        
        my_fcu = my_action.fcurves.new(data_path=my_mDataPath, index=axis, action_group=my_mBone)
        for i in range(len(frames)):            
            my_fcu.keyframe_points.insert(frames[i], quatValues[i][axis])


def retargetRot(my_action, other_action, my_mBone, other_mBone, offset):
    retargetRot_Quat(my_action, other_action, my_mBone, other_mBone, offset)
    retargetRot_Euler(my_action, other_action, my_mBone, other_mBone, offset.to_euler())




def retargetMember(self, action_ret, action_src, myArmature_pBones, otherArmature_pBones, myArmature_members, otherArmature_members, memberLinks, myArmature_rBones, otherArmature_rBones):
    for mLink in memberLinks:
        self.report({'INFO'}, "=========================")
        my_m = myArmature_members[mLink.myMember_ID]
        other_m = otherArmature_members[mLink.otherMember_ID]
        
        
        # ----------------- Origin Location ------------------
        retargetLoc(action_ret, action_src, my_m.originBone, other_m.originBone)
        
        
        # 4 cases depending on the members.hasIK values
        if my_m.hasIK:
            if other_m.hasIK:
                self.report({'INFO'}, "Case:  IK -> IK")               
                
                # ----------------- Controller Loc  ------------------
                proportionalFactor = my_m.memberLenght / other_m.memberLenght
                retargetLoc(action_ret, action_src, my_m.IK_controllerBone, other_m.IK_controllerBone, proportionalFactor)
                
                # If both have a pole target:
                if my_m.IK_poleBone != "" and other_m.IK_poleBone != "":
                    retargetLoc(action_ret, action_src, my_m.IK_poleBone, other_m.IK_poleBone)


                # ----------------- Controller Rot  ------------------
                retargetRot(action_ret, action_src, my_m.IK_controllerBone, other_m.IK_controllerBone, quat())
                myArmature_pBones[my_m.IK_controllerBone].rotation_mode = otherArmature_pBones[other_m.IK_controllerBone].rotation_mode 
                
                
                # ----------------- Final Rotation  ------------------
                retargetRot(action_ret, action_src, my_m.finalBone, other_m.finalBone, quat())
                myArmature_pBones[my_m.finalBone].rotation_mode = otherArmature_pBones[other_m.finalBone].rotation_mode 
                
            else:
                self.report({'INFO'}, "Case: Seg -> IK")
                
                # ------ Origin Rotation = Controller Location -------
                originUseQuat = otherArmature_pBones[other_m.originBone].rotation_mode == 'QUATERNION'

                my_mContMatrix = myArmature_rBones[my_m.IK_controllerBone].matrix_local
                my_mOrigMatrix = myArmature_rBones[my_m.originBone].matrix_local
                fromContMatrix = (my_mOrigMatrix.inverted_safe()) @ my_mContMatrix            
                toContMatrix  = (my_mContMatrix.inverted_safe()) @ my_mOrigMatrix
                retargetLoc_fromRotation(action_ret, action_src, my_m.IK_controllerBone, other_m.originBone, vect((0,0,0)), fromContMatrix, toContMatrix, originUseQuat)
                                                
                # ----------------- Final Rotation  ------------------
                retargetRot(action_ret, action_src, my_m.finalBone, other_m.originBone, quat())
                
        else:
            if other_m.hasIK:
                self.report({'INFO'}, "Case:  IK -> Seg")
                #self.report({'WARNING'}, "Trying to retarget from IK to non-IK members: not implemented yet")
                
                # ------ Controller Location = Origin Rotation -------
                other_mContMatrix = otherArmature_rBones[other_m.IK_controllerBone].matrix_local
                other_mOrigMatrix = otherArmature_rBones[other_m.originBone].matrix_local
                fromContMatrix = (other_mOrigMatrix.inverted_safe()) @ other_mContMatrix
                retargetRot_fromLocation(action_ret, action_src, my_m.originBone, other_m.IK_controllerBone, otherArmature_rBones[other_m.originBone].z_axis, fromContMatrix)
                
                
            else:
                self.report({'INFO'}, "Case: Seg -> Seg")
                                
                # ----------------- Origin Rotation ------------------
                retargetRot(action_ret, action_src, my_m.originBone, other_m.originBone, quat())
                
                # ----------------- Final Rotation  ------------------
                if my_m.finalBone != "":
                    retargetRot(action_ret, action_src, my_m.finalBone, other_m.originBone, quat()) 
                
                
                              
        self.report({'INFO'}, "=========================")
        
        
        
def retargetMember_AlignToModel(self, action_ret, action_src, myArmature_pBones, otherArmature_pBones, myArmature_members, otherArmature_members, memberLinks, myArmature_rBones):
    for mLink in memberLinks:
        self.report({'INFO'}, "=========================")
        my_m = myArmature_members[mLink.myMember_ID]
        other_m = otherArmature_members[mLink.otherMember_ID]
        
        
        # 4 cases depending on the members.hasIK values
        if my_m.hasIK:
            if other_m.hasIK:
                self.report({'INFO'}, "Case:  IK -> IK")
                
                # ----------------- Origin Location ------------------
                retargetLoc(action_ret, action_src, my_m.originBone, other_m.originBone)
                
                
                # ----------------- Controller Loc  ------------------
                proportionalFactor = my_m.memberLenght / other_m.memberLenght                
                rotationOffset = getRotationOffset(my_m.memberVector, other_m.memberVector)
                
                my_mContMatrix = myArmature_rBones[my_m.IK_controllerBone].matrix_local
                my_mOrigMatrix = myArmature_rBones[my_m.originBone].matrix_local
                fromContMatrix = (my_mOrigMatrix.inverted_safe()) @ my_mContMatrix            
                toContMatrix  = (my_mContMatrix.inverted_safe()) @ my_mOrigMatrix
                
                retargetLoc_withRotationOffset(action_ret, action_src, my_m.IK_controllerBone, other_m.IK_controllerBone, proportionalFactor, rotationOffset, fromContMatrix, toContMatrix)
                
                # If both have a pole target:
                if my_m.IK_poleBone != "" and other_m.IK_poleBone != "":
                    my_mPoleMatrix = myArmature_rBones[my_m.IK_poleBone].matrix_local   
                    fromPoleMatrix = (my_mOrigMatrix.inverted_safe()) @ my_mPoleMatrix         
                    toPoleMatrix  = (my_mPoleMatrix.inverted_safe()) @ my_mOrigMatrix
                                    
                    retargetLoc_withRotationOffset(action_ret, action_src, my_m.IK_poleBone, other_m.IK_poleBone, 1, rotationOffset, fromPoleMatrix, toPoleMatrix)
                    

                # ----------------- Controller Rot  ------------------
                axis, angle = rotationOffset.to_axis_angle()
                axis.rotate((my_mContMatrix.inverted_safe()).to_quaternion())
                retargetRot(action_ret, action_src, my_m.IK_controllerBone, other_m.IK_controllerBone, quat(axis, angle))
                myArmature_pBones[my_m.IK_controllerBone].rotation_mode = otherArmature_pBones[other_m.IK_controllerBone].rotation_mode 
                
                
                # ----------------- Final Rotation  ------------------
                retargetRot(action_ret, action_src, my_m.finalBone, other_m.finalBone, quat())
                myArmature_pBones[my_m.finalBone].rotation_mode = otherArmature_pBones[other_m.finalBone].rotation_mode 
                
            else:
                self.report({'INFO'}, "Case:  IK -> Seg")
                self.report({'WARNING'}, "Trying to retarget from IK to non-IK members: not implemented yet")            #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                
        else:
            if other_m.hasIK:
                self.report({'INFO'}, "Case: Seg -> IK")
                self.report({'WARNING'}, "Trying to retarget from no-IK to IK members: not implemented yet")            #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                
            else:
                self.report({'INFO'}, "Case: Seg -> Seg")
                
                # Get bone names
                my_m_origin = my_m.originBone
                other_m_origin = other_m.originBone
                
                # Retarget Member origin location
                retargetLoc(action_ret, action_src, my_m_origin, other_m_origin)
                
                # Retagert Member origin rotation
                retargetRot(action_ret, action_src, my_m_origin, other_m_origin, quat())                
        self.report({'INFO'}, "=========================")
        
        
                
                
def retargetSingleBone(self, action_ret, action_src, myArmature_singles, otherArmature_singles, singleLinks):
    for sbLink in singleLinks:
        my_sb = myArmature_singles[sbLink.myMember_ID]
        other_sb = otherArmature_singles[sbLink.otherMember_ID]
        
        # Get bone names
        my_sb_bone = my_sb.string
        other_sb_bone = other_sb.string
        
        # Retarget Member origin location
        retargetLoc(action_ret, action_src, my_sb_bone, other_sb_bone)
        
        # Retagert Member origin rotation
        retargetRot(action_ret, action_src, my_sb_bone, other_sb_bone, quat())
                
                

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




def retargetAction(self, action, myArmature_obj, otherArmature_obj):
    myArmature_data = myArmature_obj.data
    otherArmature_data = otherArmature_obj.data
    myArmature_pBones = myArmature_obj.pose.bones
    myArmature_rBones = myArmature_data.bones
    otherArmature_pBones = otherArmature_obj.pose.bones 
    otherArmature_rBones = otherArmature_data.bones       


#    if myArmature_data.pose_position != 'REST':
#        self.report({'ERROR'}, "Set the armature to REST pose mode before retargetting.")
#        return

    action_ret = bpy.data.actions.new(myArmature_obj.name + "_" + action.name)
    
    retargetLoc(action_ret, action, myArmature_data.aar_baseBone, otherArmature_data.aar_baseBone)
    retargetRot(action_ret, action, myArmature_data.aar_baseBone, otherArmature_data.aar_baseBone, quat())
    retargetSingleBone(self, action_ret, action, myArmature_data.aar_heads, otherArmature_data.aar_heads, myArmature_data.aar_head_links)
    retargetSingleBone(self, action_ret, action, myArmature_data.aar_necks, otherArmature_data.aar_necks, myArmature_data.aar_neck_links)
    
    retargetMember(self, action_ret, action, myArmature_pBones, otherArmature_pBones, myArmature_data.aar_arms, otherArmature_data.aar_arms, myArmature_data.aar_arm_links, myArmature_rBones, otherArmature_rBones)
    retargetMember(self, action_ret, action, myArmature_pBones, otherArmature_pBones, myArmature_data.aar_legs, otherArmature_data.aar_legs, myArmature_data.aar_leg_links, myArmature_rBones, otherArmature_rBones)
    retargetMember(self, action_ret, action, myArmature_pBones, otherArmature_pBones, myArmature_data.aar_wings, otherArmature_data.aar_wings, myArmature_data.aar_wing_links, myArmature_rBones, otherArmature_rBones)
    retargetMember(self, action_ret, action, myArmature_pBones, otherArmature_pBones, myArmature_data.aar_tails, otherArmature_data.aar_tails, myArmature_data.aar_tail_links, myArmature_rBones, otherArmature_rBones)


    


# ==============================================================================================================
# ==============================================================================================================
# ==============================================================================================================
# ==============================================================================================================

    
class AAR_OT_ResetCheckAndLinks(Operator):
    bl_idname = "pose.aar_reset_checks_links"
    bl_label = "Reset Checks Links"
    bl_description = "Reset Checks and links of armature's bones and its source's bones"
   

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if obj.data.aar_source is not None:
                    return True
        return False


    def execute(self, context):
        context.object.data.aar_sourceLinked = False
        context.object.data.aar_labelChecked = False
        context.object.data.aar_source.data.aar_labelChecked = False
        return {'FINISHED'}   
    

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
        context.object.data.aar_sourceLinked = False
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
        context.object.data.aar_sourceLinked = False
        return {'FINISHED'}



class AAR_OT_LinkArmatures(Operator):
    bl_idname = "pose.aar_link_armatures"
    bl_label = "Link Armatures"
    bl_description = "Link the selected armature and its source armature"
   

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if obj.data.aar_source is not None:
                    if obj.data.aar_labelChecked & obj.data.aar_source.data.aar_labelChecked & (not obj.data.aar_sourceLinked):
                        return True
        return False


    def execute(self, context):
        armature_this = context.object.data
        armature_other = context.object.data.aar_source.data
        
        linkArmatureSingleBones(self, armature_this.aar_heads, armature_other.aar_heads, armature_this.aar_head_links)
        linkArmatureSingleBones(self, armature_this.aar_necks, armature_other.aar_necks, armature_this.aar_neck_links)
        
        linkArmatureMembers(self, armature_this.aar_arms, armature_other.aar_arms, armature_this.aar_arm_links)
        linkArmatureMembers(self, armature_this.aar_legs, armature_other.aar_legs, armature_this.aar_leg_links)
        linkArmatureMembers(self, armature_this.aar_wings, armature_other.aar_wings, armature_this.aar_wing_links)
        linkArmatureMembers(self, armature_this.aar_tails, armature_other.aar_tails, armature_this.aar_tail_links)
        
        armature_this.aar_sourceLinked = True
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
                    if obj.data.aar_labelChecked & obj.data.aar_source.data.aar_labelChecked & obj.data.aar_sourceLinked:
                        return True
        return False


    def execute(self, context):
        actionProps = context.object.data.aar_actionsToCopy
        bpy.context.area.ui_type = 'DOPESHEET'
        bpy.context.space_data.ui_mode = 'ACTION'
        for actProp in actionProps:
            retargetAction(self, actProp.actionProp, context.object, context.object.data.aar_source)
        bpy.context.area.ui_type = 'PROPERTIES'
        return {'FINISHED'}
    



class AAR_OT_FullRetarget(Operator):
    bl_idname = "pose.aar_retarget_full"
    bl_label = "Full Retarget Actions Process"
    bl_description = "Retarget the selected actions from the source armature to the active armature, including chekcing and linking steps"
   

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if obj.data.aar_source is not None:
                    return True
        return False


    def execute(self, context):
        bpy.ops.pose.aar_reset_checks_links('EXEC_DEFAULT')
        bpy.ops.pose.aar_check_labels('EXEC_DEFAULT')
        bpy.ops.pose.aar_check_source_labels('EXEC_DEFAULT')
        bpy.ops.pose.aar_link_armatures('EXEC_DEFAULT')
        bpy.ops.pose.aar_retarget('EXEC_DEFAULT')
        
        return {'FINISHED'}
    
    

if __name__ == "__main__":
    bpy.utils.register_class(AAR_OT_ResetCheckAndLinks)
    bpy.utils.register_class(AAR_OT_CheckLabels)
    bpy.utils.register_class(AAR_OT_CheckSourceLabels)
    bpy.utils.register_class(AAR_OT_LinkArmatures)
    bpy.utils.register_class(AAR_OT_Retarget)
    bpy.utils.register_class(AAR_OT_FullRetarget)