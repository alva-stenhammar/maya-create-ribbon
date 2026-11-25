"""
CREATE RIBBON SCRIPT V.26.1
Created by Alva Stenhammar

Create custom ribbons and ribbons based on joint chains.

TO DO:
- fix the create nurbs from curves function !! + make work on non closed curves
- make create ribbon from surface work
- make get joint chain function work even with multiple child joints
- add visibility option for tweak controls

"""


import maya.cmds as cmds
import maya.api.OpenMaya as om
import functools
import math



def _______________UI_______________(): pass


def curveButtonHandler(curveType: str,
                       simplifyCurveBox: str,
                       innerCurveButton: str,
                       outerCurveButton: str,
                       createSurfaceRibbonButton: str,
                       *args):
    """ Curve button handler for the create curve button. """
    
    createCurveFromEdge(curveType, simplifyCurveBox)
    toggleCurveButton(curveType, innerCurveButton, outerCurveButton, createSurfaceRibbonButton)



def toggleCurveButton(curveType: str,
                      innerCurveButton: str,
                      outerCurveButton: str,
                      createSurfaceRibbonButton: str):
    """ Create curve and disable the pressed curve button. """

    # disable curve button after it's pressed
    if curveType == "inner":
        cmds.button(innerCurveButton, edit=True, enable=False)
    else:
        cmds.button(outerCurveButton, edit=True, enable=False)

    # if both curve buttons are disabled, enable the generate button
    if cmds.button(innerCurveButton, query=True, enable=True) == False:
        if cmds.button(outerCurveButton, query=True, enable=True) == False:
            cmds.button(createSurfaceRibbonButton, edit=True, enable=True)



def toggleControlOptions(addControlsBox: str,
                         controlSuffixField: str,
                         controlSizeField: str,
                         customMidControlsField: str,
                         controlOffsetField: str,
                         controlRatioMenu: str,
                         jointMidControlsField: str,
                         IKsplineBox: str,
                         *args):
    """ Toggle the control options when the add controls checkbox is toggled. """

    if cmds.checkBox(addControlsBox, query=True, value=True) == True:
        cmds.textField(controlSuffixField, edit=True, enable=True)
        cmds.floatField(controlSizeField, edit=True, enable=True)
        cmds.intField(customMidControlsField, edit=True, enable=True)
        cmds.floatField(controlOffsetField, edit=True, enable=True)
        cmds.optionMenu(controlRatioMenu, edit=True, enable=True)
        cmds.intField(jointMidControlsField, edit=True, enable=True)
    else:
        cmds.textField(controlSuffixField, edit=True, enable=False)
        cmds.floatField(controlSizeField, edit=True, enable=False)
        cmds.intField(customMidControlsField, edit=True, enable=False)
        cmds.floatField(controlOffsetField, edit=True, enable=False)
        cmds.optionMenu(controlRatioMenu, edit=True, enable=False)
        cmds.intField(jointMidControlsField, edit=True, enable=False)
        cmds.checkBox(IKsplineBox, edit=True, enable=False, value=False)



def createLineSeparator(parent: str) -> str:
    """ Create custom line separator.
    
    Return separator. """

    return cmds.separator(height=2,
                          style="none",
                          backgroundColor=(0.2, 0.2, 0.2),
                          parent=parent)



def createBlankSeparator(parent: str) -> str:
    """ Create custom blank separator.
    
    Return separator. """

    return cmds.separator(height=5,
                          style="none",
                          parent=parent)



def createColumnLayout(parent: str) -> str:
    """ Create row/column layout with custom settings.

    Return layout. """

    return cmds.rowColumnLayout(numberOfColumns=2,
                                columnWidth=[(1, 130), (2, 130)],
                                columnOffset=[(1, "right", 10), (2, "left", 10)],
                                rowSpacing=(1, 5),
                                parent=parent)



def createFrameLayout(label: str, parent: str) -> str:
    """ Create frame layout layout with custom settings.

    Return layout. """

    return cmds.frameLayout(label=label,
                            width=300,
                            marginWidth=20,
                            marginHeight=10,
                            backgroundShade=True,
                            font="boldLabelFont",
                            parent=parent)



def createButton(label: str, parent: str) -> str:
    """ Create button with custom settings.
    
    Return button. """

    cmds.rowLayout(numberOfColumns=1,
                   columnWidth=(1, 260),
                   parent=parent)
    
    return cmds.button(label=label, width=260)



def createUI(buildCustomRibbon, buildJointRibbon, buildSurfaceRibbon):
    """ Create and open the UI. """


    # WINDOW CREATION
    windowID = "createRibbonWindowID"
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    cmds.window(windowID, title=f"Create Ribbon", sizeable=False)


    # LAYOUTS
    mainLayout = cmds.columnLayout(width=310, margins=5)

    cmds.columnLayout(margins=10, parent=mainLayout)
    cmds.text(label="Create Ribbon Tool",
              width=280,
              font="boldLabelFont")
    cmds.separator(height=10, style="none")


    # LAYOUT SETUP
    layout1 = createFrameLayout("Global Settings", mainLayout)
    createBlankSeparator(parent=mainLayout)

    
    layout2 = createFrameLayout("Custom Ribbon", mainLayout)
    cmds.text(label="Create ribbon with custom settings.",
              width=260, height=10,
              font="smallPlainLabelFont")
    createLineSeparator(layout2)
    createBlankSeparator(parent=mainLayout)


    layout3 = createFrameLayout("Ribbon from Joint Chain", mainLayout)
    cmds.text(label="Create ribbon from a joint chain. Select start and end joint.",
              width=260, height=10,
              font="smallPlainLabelFont")
    createLineSeparator(layout3)
    createBlankSeparator(parent=mainLayout)
    
    """
    layout4 = createFrameLayout("Ribbon from Surface", mainLayout)

    cmds.text(label="Create ribbon from a surface. Select edges and create",
              width=260, height=10,
              font="smallPlainLabelFont")
    cmds.text(label="inner & outer curves, then create ribbon.",
              width=260, height=10,
              font="smallPlainLabelFont")
    createLineSeparator(parent=layout4)
    createBlankSeparator(parent=mainLayout)
    """

    # LAYOUT-1: GLOBAL SETTINGS
    createColumnLayout(parent=layout1)
    
    cmds.text(label="Ribbon name:")
    ribbonNameField = cmds.textField(text="ribbon")
    
    cmds.text(label="Global scale:")
    globalScaleField = cmds.floatField(value=1, precision=2, width=50)

    createColumnLayout(parent=layout1)
    
    cmds.text(label="Add controls:")
    addControlsBox = cmds.checkBox(label="",
                                  value=True)

    cmds.text(label="Control size:")
    controlSizeField = cmds.floatField(value=1, precision=2, width=50)


    # LAYOUT-2: CUSTOM RIBBON
    createColumnLayout(parent=layout2)
    
    cmds.text(label="Divisions:")
    spansField = cmds.intField(value=8, width=50)

    cmds.text(label="Mid controls:")
    customMidControlsField = cmds.intField(value=1, width=50)

    cmds.text(label="Ribbon size:")
    ribbonSizeField = cmds.floatField(value=50, precision=2, width=50)

    cmds.text("Direction:")
    directionMenu = cmds.optionMenu()
    cmds.menuItem(label="Horizontal")
    cmds.menuItem(label="Vertical")

    cmds.text("Orientation:")
    orientationMenu = cmds.optionMenu()
    cmds.menuItem(label="X")
    cmds.menuItem(label="Y")
    cmds.menuItem(label="Z")

    # apply button
    cmds.separator(height=1, style="none", enableBackground=False, parent=layout2)
    createCustomRibbonButton = createButton("Create Ribbon", layout2)


    # LAYOUT-3: RIBBON FROM JOINT CHAIN
    createColumnLayout(parent=layout3)

    cmds.text(label="Mid controls:")
    jointMidControlsField = cmds.intField(value=1, width=50)

    cmds.text(label="Tweak controls:")
    tweakControlsBox = cmds.checkBox(label="", enable=True, value=True)

    cmds.text(label="FK hybrid controls:")
    FKhybridControlsBox = cmds.checkBox(label="", enable=True, value=False)
    
    cmds.text(label="IK spline:")
    IKsplineBox = cmds.checkBox(label="", enable=True, value=False)
    
    # apply button
    cmds.separator(height=1, style="none", enableBackground=False, parent=layout3)
    createJointRibbonButton = createButton("Create Ribbon", layout3)

    
    # LAYOUT-4: RIBBON FROM SURFACE
    """
    createColumnLayout(parent=layout4)

    cmds.text(label="Control Offset:")
    controlOffsetField = cmds.floatField(value=0, precision=2, width=50)

    cmds.text(label="Control Ratio:")
    controlRatioMenu = cmds.optionMenu()
    cmds.menuItem(label="1:1")
    cmds.menuItem(label="1:2")
    cmds.menuItem(label="1:2 +1")
    cmds.menuItem(label="1:3")
    cmds.menuItem(label="1:3 +1")
    cmds.menuItem(label="1:3 +2")

    cmds.text(label="Invert Surface:")
    reverseRibbonBox = cmds.checkBox(label="",
                                     enable=True, value=False)
    
    cmds.text(label="Closed Loop:")
    closedRibbonBox = cmds.checkBox(label="",
                                    enable=True, value=False)
    
    cmds.text(label="Simplify Curve:")
    simplifyCurveBox = cmds.checkBox(label="",
                                     enable=True, value=False)
    

    # create curve buttons
    cmds.separator(height=1, style="none", enableBackground=False, parent=layout4)
    
    cmds.rowLayout(numberOfColumns=2,
                   columnWidth=[(1, 130), (2, 130)],
                   columnAttach=[(1, "left", 0), (2, "right", 0)],
                   parent=layout4)

    innerCurveButton = cmds.button(label="Inner Curve",
                                   width=127.5)
    outerCurveButton = cmds.button(label="Outer Curve",
                                   width=127.5)
    
    # apply button
    createSurfaceRibbonButton = createButton("Create Ribbon", layout4)
    """

    # CREDITS TEXT
    cmds.columnLayout(margins=10, parent=mainLayout)
    createBlankSeparator(parent=mainLayout)
    
    cmds.text(label="Created by Alva Stenhammar", width=280,
              font="obliqueLabelFont")
    

    # ADD COMMANDS
    # control options
    cmds.checkBox(addControlsBox, edit=True,
                  onCommand=functools.partial(toggleControlOptions,
                                              addControlsBox,
                                              controlSizeField,
                                              customMidControlsField,
                                            #   controlOffsetField,
                                            #   controlRatioMenu,
                                              jointMidControlsField,
                                              IKsplineBox),
                  offCommand=functools.partial(toggleControlOptions,
                                              addControlsBox,
                                              controlSizeField,
                                              customMidControlsField,
                                            #   controlOffsetField,
                                            #   controlRatioMenu,
                                              jointMidControlsField,
                                              IKsplineBox))
    
    
    # custom ribbon button
    cmds.button(createCustomRibbonButton, edit=True,
                command=functools.partial(buildCustomRibbon,
                                          ribbonNameField,
                                          globalScaleField,
                                          addControlsBox,
                                          controlSizeField,
                                          spansField,
                                          customMidControlsField,
                                          ribbonSizeField,
                                          directionMenu,
                                          orientationMenu))
    
    # joint ribbon button
    cmds.button(createJointRibbonButton, edit=True,
                command=functools.partial(buildJointRibbon,
                                          ribbonNameField,
                                          globalScaleField,
                                          addControlsBox,
                                          controlSizeField,
                                          jointMidControlsField,
                                          tweakControlsBox,
                                          FKhybridControlsBox,
                                          IKsplineBox))

    """
    # curve buttons
    cmds.button(innerCurveButton, edit=True,
                command=functools.partial(curveButtonHandler,
                                          "inner",
                                          simplifyCurveBox,
                                          innerCurveButton,
                                          outerCurveButton,
                                          createSurfaceRibbonButton))
    
    cmds.button(outerCurveButton, edit=True,
                command=functools.partial(curveButtonHandler,
                                          "outer",
                                          simplifyCurveBox,
                                          innerCurveButton,
                                          outerCurveButton,
                                          createSurfaceRibbonButton))
    

    # surface ribbon button
    cmds.button(createSurfaceRibbonButton, edit=True,
                command=functools.partial(buildSurfaceRibbon,
                                          ribbonNameField,
                                          globalScaleField,
                                          addControlsBox,
                                          controlSizeField,
                                          controlOffsetField,
                                          controlRatioMenu,
                                          reverseRibbonBox,
                                          closedRibbonBox))
    """


    cmds.showWindow()



def _______________GENERIC_______________(): pass


def lerp(a: float, b: float, t: float) -> float:
    """ Linear interpolate on the scale given by a to b, using t as the point on that scale.
        
    Return interpolated value. """

    return (1 - t) * a + t * b



def dist(a: list[float], b: list[float]) -> float:
    """ Calculate distance between two points in 3D space.
        
    Return distance. """
    
    return math.sqrt(((b[0] - a[0]) ** 2) + ((b[1] - a[1]) ** 2) + ((b[2] - a[2]) ** 2))


def averagePosition(a: list[float], b: list[float]) -> float:
    """ Average two positions using XYZ coordinates.
    
    Return new XYZ values in a list. """

    averagedPosition = []

    for i in range(len(a)):
        averagedPosition.append((float(a[i]) + float(b[i])) / 2)

    return averagedPosition



def checkNameForDup(name: str) -> str:
    """ Check if the name is taken and add integers to the end until it's not.
    
    Return checked name. """

    n = 1

    while cmds.objExists(name):
        n += 1
        name = name + str(n)

    return name



def transferTransformsToOPM(node: str):
    """ Transfer object's transform to the Offset Parent Matrix then clear the object's transforms. """

    localMatrix = om.MMatrix(cmds.xform(node, q=True, m=True, ws=False))
    offsetParentMatrix = om.MMatrix(cmds.getAttr(f"{node}.offsetParentMatrix"))
    newMatrix = localMatrix * offsetParentMatrix

    cmds.setAttr(f"{node}.offsetParentMatrix", newMatrix, type="matrix")

    # attributes to clear, add jointOrient if attr exists (for joints)
    transformList = [".translate", ".rotate", ".scale",]
    transformList.append(".jointOrient") if cmds.attributeQuery('jointOrient', node=node, exists=True) else False

    # reset transform values
    for attribute in transformList:
        value = 1 if attribute == ".scale" else 0
        for axis in ["X", "Y", "Z"]:
            cmds.setAttr(node + attribute + axis, value)

    cmds.select(clear=True)



def skinJoints(geometryName: str, jointList: list[str]):
    """ Skin joints to a geometry, like a ribbon or curve. """

    for controlJoint in jointList:
        cmds.select(controlJoint, add=True)
    cmds.select(geometryName, add=True)

    cmds.skinCluster(name=f"{geometryName}SkinCluster")
    cmds.select(clear=True)



def connectRibbonToJoints(jointChain: list[str],
                          followJointList: list[str]):
    """ Parent each follow joint to the respective bind joint in the joint chain. """

    for i, joint in enumerate(jointChain):
        cmds.parentConstraint(followJointList[i], joint, maintainOffset=True)



def _______________GET_______________(): pass


def getClosestObject(refObject: str,
                     objectList: list[str]) -> str:
    """ Get the closest object in a list of objects.
    
    Return name of closest object. """

    refPosition = om.MVector(*cmds.xform(refObject, q=True, ws=True, t=True))
    distanceList = []

    for object in objectList:
        objectPosition = om.MVector(*cmds.xform(object, q=True, ws=True, t=True))

        distance = (objectPosition - refPosition).length()
        distanceList.append((object, distance))

    distanceList.sort(key=lambda x: x[1])

    return distanceList[0][0]



def getJointChain(startJoint: str, endJoint: str) -> list[str]:
    """ Get the entire joint chain between the start joint and end joint.
    
    Return joint chain. """

    # check if end joint is in start joint chain
    descendents = cmds.listRelatives(startJoint, type="joint", allDescendents=True)
    descendents.reverse()
    result = False

    for child in descendents:
        if child == endJoint:
            result = True
            break

    if result == False:
        cmds.error("End joint is not in the same joint chain as start joint.",
                    noContext=True)

    # get joint chain
    jointChain = [startJoint]

    for joint in descendents:
        jointChain.append(joint)
        if joint == endJoint:
            break
    
    return jointChain



def getStartEndPosition(list: list[str]) -> tuple[list[float], list[float]]:
    """ Get position of the start and end of a list of objects.

    Return start position and end position. """

    startPosition = []
    endPosition = []
    
    for i, position in [(0, startPosition), (-1, endPosition)]:
        decomposeMatrix = cmds.createNode("decomposeMatrix")
        cmds.connectAttr(f"{list[i]}.worldMatrix[0]", f"{decomposeMatrix}.inputMatrix")
        translate = cmds.getAttr(f"{decomposeMatrix}.outputTranslate")[0]

        # round values to 10 decimals and add to list
        for n in translate:
            n = round(n, 10)
            position.append(n)
        
        cmds.delete(decomposeMatrix)

    return (startPosition, endPosition)



def getMidControlJointPositions(midControls: int, startPosition: list[float], endPosition: list[float]):
    """ Get a list of the positions for the mid control joints on a ribbon.

    Return mid control joint positions. """

    midControlJointPositionList = []

    for i in range(midControls):
        midControlJointPosition = []
        t = (1 / (midControls + 1)) * (i + 1)

        for i in range(3):
            midControlJointPosition.append(lerp(startPosition[i], endPosition[i], t))
        
        midControlJointPositionList.append(midControlJointPosition)

    # add the start and end positions of the ribbon
    controlJointPositionList = [startPosition] + midControlJointPositionList + [endPosition]

    return controlJointPositionList


def getRibbonWidth(ribbonName: str,
                   reverse: bool = False) -> float:
    """ Get width of ribbon by comparing CV positions. Reverse if it returns length instead.
    
    Return ribbon width. """
    
    startPosition = cmds.xform(f"{ribbonName}_RIBBON.cv[0][0]", query=True, worldSpace=True, translation=True)
    endPosition = cmds.xform(f"{ribbonName}_RIBBON.cv[0][1]", query=True, worldSpace=True, translation=True)

    if reverse:
        startPosition = cmds.xform(f"{ribbonName}_RIBBON.cv[0][0]", query=True, worldSpace=True, translation=True)
        endPosition = cmds.xform(f"{ribbonName}_RIBBON.cv[1][0]", query=True, worldSpace=True, translation=True)

    difference = []

    for i in range(3):
        difference.append(abs(endPosition[i] - startPosition[i]))

    return max(difference)



def _______________CREATE_______________(): pass


# def createFollicles(ribbonName: str,
#                     jointChain: list[str] = [],
#                     isJointRibbon = False) -> list[str]:
#     """
#     Create the follicles and connect to ribbon.

#     Return list of follicles.
#     """

#     follicleName = f"{ribbonName}_FOLLICLE#"
#     ribbonShape = f"{ribbonName}_RIBBONShape"
#     follicleGroup = f"{ribbonName}_follicles"
#     follicleList = []
    
#     # create follicle group
#     cmds.group(empty=True, name=follicleGroup)
    
#     cmds.select(clear=True)
#     cmds.select(f"{ribbonName}_RIBBON")

    
#     # get ribbon cvs
#     cvList = cmds.ls(f"{ribbonName}_RIBBON.cv[*][0]", flatten=True)

#     # remove extra cvs at start and end of ribbon
#     cvList.pop(1)
#     cvList.pop(-2)

#     cvPositions = []

#     for cv in cvList:
#         cv_pos = cmds.pointPosition(cv, w=True)
#         cps = cmds.createNode("closestPointOnSurface")
#         cmds.connectAttr(f"{ribbonName}_RIBBON.local", f"{cps}.inputSurface", force=True)
#         cmds.setAttr(f"{cps}.inPosition", *cv_pos, type="double3")
#         u = cmds.getAttr(f"{cps}.parameterU")
#         cmds.delete(cps)

#         cvPositions.append(u)

#     maxValueU = cmds.getAttr(f"{ribbonName}_RIBBON.maxValueU")
    

#     for i, valueU in enumerate(cvPositions):
#         if isJointRibbon:
#             follicleName = f"{jointChain[i]}_FOLLICLE"

#         # create and connect follicle shape and transform
#         follicleTransform = cmds.createNode("transform", name=follicleName)
#         follicleShape = cmds.createNode("follicle", name=(f"{follicleName}Shape"), parent=follicleTransform)

#         follicleList.append(follicleTransform)

#         cmds.connectAttr(f"{follicleShape}.outTranslate", f"{follicleTransform}.translate")
#         cmds.connectAttr(f"{follicleShape}.outRotate", f"{follicleTransform}.rotate")

#         # set simulation method to static
#         cmds.setAttr(f"{follicleShape}.simulationMethod", 0)

#         # connect ribbon to influence follicle
#         cmds.connectAttr(f"{ribbonShape}.local", f"{follicleShape}.inputSurface")
#         cmds.connectAttr(f"{ribbonShape}.worldMatrix[0]", f"{follicleShape}.inputWorldMatrix")

#         # move follicle to correct position
#         cmds.setAttr(f"{follicleShape}.parameterV", 0.5)
#         cmds.setAttr(f"{follicleShape}.parameterU", valueU / maxValueU)

#         # add to follicle group
#         cmds.parent(follicleTransform, follicleGroup)


#     return follicleList



# def createBindJoints(ribbonName: str,
#                      globalScale: float,
#                      follicleList: list[str],
#                      isJointRibbon = False):
#     """
#     Create bind joints for each follicle.

#     Return list of bind joints.
#     """

#     bindJointName = ribbonName + "_BINDJNT#"
#     bindJointList = []
#     bindJointRadius = 0.05 * globalScale

#     for follicle in follicleList:
#         if isJointRibbon:
#             follicleName = "_".join(follicle.split("_")[:-1])
#             bindJointName = f"{follicleName}_BINDJNT"

#         # create joints, parent to follicles, and add to the bind joint list
#         cmds.select(clear=True)
#         bindJoint = cmds.joint(name=bindJointName, radius=bindJointRadius)
#         cmds.matchTransform(bindJoint, follicle)
#         cmds.makeIdentity(apply=True, rotate=True, translate=True)

#         cmds.setAttr((bindJoint + ".rotateX"), 90)
#         cmds.makeIdentity(bindJoint, apply=True, rotate=True)

#         cmds.parent(bindJoint, follicle)
#         bindJointList.append(bindJoint)

#         cmds.select(clear=True)

#     return bindJointList


def createFollowJoints(ribbonName: str,
                       globalScale: float,
                       jointChain: list[str] = []) -> list[str]:        #### FIX BY ADDING FINDING POSITIONS WITHOUT JOINTS
    """ Create the follow joints and connect to ribbon.

    Return list of follow joints. """

    followJointName = f"{ribbonName}_FOLLOW_JNT_#"
    followJointGroup = f"{ribbonName}_followJoints"
    followJointRadius = 0.1 * globalScale
    followJointList = []

    # fix hierarchy
    if not cmds.objExists(followJointGroup):
        cmds.group(name=followJointGroup, empty=True)
        cmds.select(clear=True)

    # create joints
    if jointChain == []:
        # get positions of ribbon top and bottom cvs
        cvPositions0 = []
        cvPositions1 = []
        averagedPositions = []

        for i in range(2):
            # get ribbon cvs
            cvList = cmds.ls(f"{ribbonName}_RIBBON.cv[*][{i}]", flatten=True)

            # remove extra cvs at start and end of ribbon
            cvList.pop(1)
            cvList.pop(-2)

            # get positions and add to positions list
            for cv in cvList:
                if i == 0:
                    cvPositions0.append(cmds.pointPosition(cv, world=True))
                else:
                    cvPositions1.append(cmds.pointPosition(cv, world=True))

        # average positions to find middle of the two cvs
        for i in range(len(cvPositions0)):
            averagedPositions.append(averagePosition(cvPositions0[i], cvPositions1[i]))


        for position in averagedPositions:
            # create joint
            followJoint = cmds.joint(name=followJointName, radius=followJointRadius)
            followJointList.append(followJoint)

            # move to correct position
            for i, axis in enumerate(["X", "Y", "Z"]):
                cmds.setAttr(f"{followJoint}.translate{axis}", position[i])

            cmds.select(clear=True)

    else:
        # create joints from the joint chain
        for bindJoint in jointChain:
            followJointName = bindJoint.replace("BIND", "FOLLOW")

            # create joint
            followJoint = cmds.joint(name=followJointName, radius=followJointRadius)
            followJointList.append(followJoint)

            # move to bind joint
            cmds.matchTransform(followJoint, bindJoint)
            cmds.select(clear=True)

        # duplicate original joint chain
        # duplicateChain = cmds.duplicate(jointChain[0], renameChildren=True)

        # for joint in duplicateChain:
        #     # unparent if not already parented to world
        #     if cmds.listRelatives(joint, parent=True) != None:
        #         cmds.parent(joint, world=True)

        #     # rename joint and add to follow joint list
        #     followJoint = cmds.rename(joint, joint.replace("BIND", "FOLLOW")[:-1])
        #     followJointList.append(followJoint)

        #     # set joint radius
        #     cmds.setAttr(f"{followJoint}.radius", followJointRadius)

        #     cmds.makeIdentity(followJoint, apply=True)
        
        cmds.select(clear=True)

    # uv pin to ribbon
    cmds.select(clear=True)
    cmds.select(f"{ribbonName}_RIBBON")

    for joint in followJointList:
        cmds.select(joint, add=True)

    cmds.UVPin(normalAxis="-Y", tangentAxis="X")

    # group follow joints and fix orientations
    for joint in followJointList:
        cmds.parent(joint, followJointGroup)

        for axis in ["X", "Y", "Z"]:
            cmds.setAttr(f"{joint}.jointOrient{axis}", 0)


    return followJointList



def createControlJoints(ribbonName: str,
                        globalScale: float,
                        controlJointPositionList: list[list[float]],
                        followJointList: list[str],
                        isJointChain = False) -> list[str]:
    """ Create control joints in the specified positions.
    
    Return list of control joints. """

    controlJointName = f"{ribbonName}_CTRLJNT_#"
    controlJointList = []
    controlJointRadius = 0.5 * globalScale
    controlJointGroup = f"{ribbonName}_controlJoints"

    if not cmds.objExists(controlJointGroup):
        cmds.group(name=controlJointGroup, empty=True)


    for controlJointPosition in controlJointPositionList:
        cmds.select(clear=True)

        # create control joint and match rotation to the first follow joint
        controlJoint = cmds.joint(name=controlJointName, radius=controlJointRadius)
        cmds.matchTransform(controlJoint, followJointList[0])

        # position control joint
        for i, axis in enumerate(["X", "Y", "Z"]):
            cmds.setAttr(f"{controlJoint}.translate{axis}", controlJointPosition[i])
        
        controlJointList.append(controlJoint)

        cmds.parent(controlJoint, controlJointGroup)
        cmds.makeIdentity(controlJoint, apply=True, rotate=True, translate=True)


    return controlJointList



def createControl(shape: str,
                  name: str,
                  size: float) -> tuple[str, str]:
    """ Create a control of the specified shape.
    
    Return name of control and offset group as a tuple.
     
    Control shapes:
    - Circle
    - Plus
    - Star
    - Box """

    if shape == "circle":
        control = cmds.circle(name=name, radius=size)[0]

    elif shape == "plus":
        positions = [[-1, 5, 0], [1, 5, 0], [1, 1, 0], [5, 1, 0], [5, -1, 0],
                    [1, -1, 0], [1, -5, 0], [-1, -5, 0], [-1, -1, 0], [-5, -1, 0],
                    [-5, 1, 0], [-1, 1, 0], [-1, 5, 0]]
        
        control = cmds.curve(name=name, degree=1, point=positions)
        cmds.select(control)
        cmds.scale(size * 0.1, size * 0.1, size * 0.1)
        cmds.select(clear=True)
        cmds.makeIdentity(control, apply=True, scale=True)

    elif shape == "star":
        control = cmds.circle(name=name, radius=(size * 1.3), sections=16)[0]
        
        count = 0

        for i in range(16):
            if count % 2 == 0:
                cmds.select(f"{control}.cv[{str(i)}]", add=True)
            count += 1
        
        cmds.scale(0.7, 0.7, 0.7)
        cmds.select(clear=True)

    elif shape == "box":
        cmds.select(clear=True)
        curve1 = cmds.curve(point=[[1, 1, 1], [1, 1, -1], [-1, 1, -1], [-1, 1, 1]], degree=1)
        cmds.closeCurve(curve1, replaceOriginal=True)
        curve2 = cmds.curve(point=[[1, -1, 1], [1, -1, -1], [-1, -1, -1], [-1, -1, 1]], degree=1)
        cmds.closeCurve(curve2, replaceOriginal=True)

        curve3 = cmds.curve(point=[[1, 1, 1], [1, -1, 1]], degree=1)
        curve4 = cmds.curve(point=[[1, 1, -1], [1, -1, -1]], degree=1)
        curve5 = cmds.curve(point=[[-1, 1, 1], [-1, -1, 1]], degree=1)
        curve6 = cmds.curve(point=[[-1, 1, -1], [-1, -1, -1]], degree=1)

        for i, curve in enumerate([curve1, curve2, curve3, curve4, curve5, curve6]):
            cmds.rename(curve, f"tempCurve{i+1}")

        for i in range(6):            
            if i != 0:
                cmds.parent(f"tempCurveShape{i+1}", "tempCurve1", relative=True, shape=True)
                cmds.delete(f"tempCurve{i+1}")

        control = cmds.rename("tempCurve1", name)

        cmds.scale(size * 0.1, size * 1, size * 1, control)


    # clean up
    cmds.makeIdentity(control, apply=True)
    cmds.delete(control, constructionHistory=True)

    # correct rotation
    cmds.setAttr(f"{control}.rotateY", 90)
    cmds.makeIdentity(control, apply=True, rotate=True)

    # create offset group
    group = cmds.group(control, name=control.replace("CTRL", "GRP"))

    cmds.select(clear=True)
    
    return (control, group)



def _______________CREATE_CUSTOM_______________(): pass


def createCustomNurbsPlane(ribbonName: str,
                           globalScale: float,
                           spans: int,
                           orientation: str):
    """ Create the nurbs plane. """

    width = globalScale * spans

    if orientation == "X":
        axis = [1, 0, 0]
    elif orientation == "Y":
        axis = [0, 1, 0]
    else:
        axis = [0, 0, 1]

    # create nurbs plane
    ribbon = cmds.nurbsPlane(name=f"{ribbonName}_RIBBON",
                             lengthRatio=0.1, width=width,
                             patchesU=spans, degree=3, axis=axis)[0]
    
    cmds.rebuildSurface(ribbon,
                        degreeU=3, degreeV=1,
                        spansU=spans, spansV=1)

    cmds.delete(ribbon, constructionHistory=True)



def createCustomControlJoints(ribbonName: str,
                              globalScale: float,
                              followJointList: list[str],
                              midControls: int) -> list[str]:
    """ Create control joints for a custom ribbon.
    
    Return list of control joints. """

    startPosition, endPosition = getStartEndPosition(followJointList)
    controlJointPositionList = getMidControlJointPositions(midControls, startPosition, endPosition)
    controlJointList = createControlJoints(ribbonName, globalScale, controlJointPositionList, followJointList)


    return controlJointList



def createCustomControls(ribbonName: str,
                         controlJointList: list[str],
                         controlSize: float):
    """ Create controls for the control joints on a custom ribbon. """

    ribbonWidth = getRibbonWidth(ribbonName)
    controlRadius = ribbonWidth * controlSize
    controlName = f"{ribbonName}_CTRL#"
    controlGroup = f"{ribbonName}_controls"

    if not cmds.objExists(controlGroup):
        cmds.group(name=controlGroup, empty=True)


    for controlJoint in controlJointList:
        
        control, group = createControl(shape="circle", name=controlName, size=controlRadius)
        
        # move to control joint and transfer transforms
        cmds.matchTransform(group, controlJoint)
        transferTransformsToOPM(group)

        # correct rotation
        cmds.setAttr(f"{control}.rotateX", 90)
        cmds.makeIdentity(control, apply=True, rotate=True)

        cmds.parentConstraint(control, controlJoint, maintainOffset=True)
        cmds.parent(group, f"{ribbonName}_controls")
        cmds.select(clear=True)



def _______________CREATE_JOINT_______________(): pass


def createNurbsPlaneFromJoints(ribbonName: str,
                               globalScale: float,
                               jointChain: list) -> int:
    """ Create the nurbs plane from a joint chain.
    
    Return spans. """

    # get joint positions and create curve from them
    positions = [cmds.xform(joint, query=True, worldSpace=True, translation=True) for joint in jointChain]
    curve = cmds.curve(name="jointCurve", degree=3, editPoint=positions)
    
    # width of ribbon calculated from amount of joints and global scale
    offsetAmount = (globalScale * len(jointChain) * 0.1) / 2

    # determine offset direction using cross product
    startVector = om.MVector(*positions[0])
    endVector = om.MVector(*positions[-1])
    forwardVector = (endVector - startVector).normalize()
    upVector = om.MVector(0, 1, 0)
    offsetVector = forwardVector ^ upVector  # cross product

    if offsetVector.length() < 1e-3:
        upVector = om.MVector(0, 0, 1)  # try Z up if Y fails
        offsetVector = forwardVector ^ upVector

    offsetVector = offsetVector.normalize() * offsetAmount

    # offset points for both curves
    offsetPositionsA = [list((om.MVector(*p) + offsetVector)) for p in positions]
    offsetPositionsB = [list((om.MVector(*p) - offsetVector)) for p in positions]

    # create new curves and loft between
    curveA = cmds.curve(name="curveA",
                        degree=3, editPoint=offsetPositionsA)
    curveB = cmds.curve(name="curveB",
                        degree=3, editPoint=offsetPositionsB)

    cmds.loft(curveA, curveB,
              name=f"{ribbonName}_RIBBON",
              constructionHistory=False,
              reverseSurfaceNormals=True,
              uniform=True,
              degree=1)
    
    cmds.delete(curve, curveA, curveB)
    cmds.select(clear=True)

    return len(positions) - 1



def createJointControlJoints(ribbonName: str,
                             globalScale: float,
                             followJointList: list[str],
                             jointChain: list[str],
                             midControls: int) -> list[str]:
    """ Create control joints for a joint ribbon.
    
    Return list of control joints. """

    startPosition, endPosition = getStartEndPosition(followJointList)
    controlJointPositionList = getMidControlJointPositions(midControls, startPosition, endPosition)
    controlJointList = createControlJoints(ribbonName, globalScale, controlJointPositionList, followJointList)
    newControlJointList = []

    # match transform to closest joint and rename
    for joint in controlJointList:
        closestJoint = getClosestObject(joint, jointChain)
        cmds.matchTransform(joint, closestJoint)

        newJointName = closestJoint.replace("BIND", "CTRL")
        cmds.rename(joint, newJointName)

        newControlJointList.append(newJointName)

        cmds.makeIdentity(newJointName, apply=True, rotate=True)
    

    return newControlJointList



def createJointControls(ribbonName,
                        controlJointList: list[str],
                        size: float) -> list[str]:
    """ Create controls for the control joints on a custom ribbon.

    Return list of controls. """

    ribbonWidth = cmds.getAttr(f"{ribbonName}_RIBBON.maxValueV")
    size = ribbonWidth * size
    controlList = []
    controlGroup = f"{ribbonName}_controls"

    if not cmds.objExists(controlGroup):
        cmds.group(name=controlGroup, empty=True)


    for controlJoint in controlJointList:
        controlName = "_".join(controlJoint.split("_")[:-1])

        control, group = createControl(shape="circle", name=controlName, size=size)
        controlList.append(control)
        
        # move to control joint and transfer transforms
        cmds.matchTransform(group, controlJoint)
        transferTransformsToOPM(group)

        cmds.parentConstraint(control, controlJoint, maintainOffset=True)
        cmds.parent(group, f"{ribbonName}_controls")
        cmds.select(clear=True)

    # DRAWING OVERRIDES
    cmds.setAttr(f"{controlGroup}.overrideEnabled", True)
    cmds.setAttr(f"{controlGroup}.overrideRGBColors", True)

    if controlList[0][0] == "L":
        cmds.setAttr(f"{controlGroup}.overrideColorR", 1)
        cmds.setAttr(f"{controlGroup}.overrideColorG", 0)
        cmds.setAttr(f"{controlGroup}.overrideColorB", 0)
    elif controlList[0][0] == "R":
        cmds.setAttr(f"{controlGroup}.overrideColorR", 0)
        cmds.setAttr(f"{controlGroup}.overrideColorG", 0)
        cmds.setAttr(f"{controlGroup}.overrideColorB", 1)
    else:
        cmds.setAttr(f"{controlGroup}.overrideColorR", 1)
        cmds.setAttr(f"{controlGroup}.overrideColorG", 1)
        cmds.setAttr(f"{controlGroup}.overrideColorB", 0)
    
    return controlList



def createTweakControls(ribbonName: str,
                        jointChain: list[str],
                        size: float):
    """ Create tweak controls to control the bind skeleton. """

    ribbonWidth = cmds.getAttr(f"{ribbonName}_RIBBON.maxValueV")
    controlRadius = ribbonWidth * size
    tweakControlsGroup = f"{ribbonName}_tweakControls"
    tweakControlList = []

    if not cmds.objExists(tweakControlsGroup):
        cmds.group(name=tweakControlsGroup, empty=True)
        cmds.parent(tweakControlsGroup, f"{ribbonName}_controls")

    for bindJoint in jointChain:
        tweakControlName = bindJoint.replace("BIND_JNT", "TWEAK_CTRL")
        followJoint = bindJoint.replace("BIND", "FOLLOW")

        control, group = createControl(shape="star", name=tweakControlName, size=controlRadius)

        tweakControlList.append(control)

        # move control to follow joint and transfer transforms
        cmds.matchTransform(group, followJoint)
        transferTransformsToOPM(group)

        # parent constrain control to follow joint
        cmds.parentConstraint(followJoint, group)

        # parent bind joint to control
        cmds.parentConstraint(control, bindJoint, maintainOffset=True)

        # group tweak controls
        cmds.parent(group, tweakControlsGroup)

    # DRAWING OVERRIDES
    cmds.setAttr(f"{tweakControlsGroup}.overrideEnabled", True)
    cmds.setAttr(f"{tweakControlsGroup}.overrideRGBColors", True)

    if tweakControlList[0][0] == "L":
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorR", 1)
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorG", 0.8)
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorB", 0.8)
    elif tweakControlList[0][0] == "R":
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorR", 0.8)
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorG", 0.8)
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorB", 1)
    else:
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorR", 1)
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorG", 1)
        cmds.setAttr(f"{tweakControlsGroup}.overrideColorB", 0.8)



def createFKhybridControls(ribbonName: str,
                           size: float,
                           controlList: list[str]):
    """ Create FK hybrid controls to control the IK controls. """

    ribbonWidth = cmds.getAttr(f"{ribbonName}_RIBBON.maxValueV")
    size = ribbonWidth * size
    FKcontrolList = []

    cmds.group(name=f"{ribbonName}_FK_controls", empty=True)

    for i, IKcontrol in enumerate(controlList[:-1]):
        IKcontrolName = "_".join(IKcontrol.split("_")[:-1])
        controlName = f"{IKcontrolName}_FK_CTRL"

        # create control and control group
        FKcontrol, FKgroup = createControl(shape="box", name=controlName, size=size)
        
        # move to control joint and transfer transforms
        cmds.matchTransform(FKgroup, IKcontrol)
        transferTransformsToOPM(FKgroup)

        # correct rotation
        cmds.setAttr(f"{FKcontrol}.rotateY", 90)
        
        cmds.makeIdentity(FKcontrol, apply=True, rotate=True)
        cmds.parentConstraint(FKcontrol, IKcontrol, maintainOffset=True)

        # if it's the last FK control, also constrain following IK control
        if i == len(controlList[:-1]) - 1:
            cmds.parentConstraint(FKcontrol, controlList[i + 1], maintainOffset=True)

        # parent to previous control (except if it's the first control)
        if i != 0:
            cmds.parentConstraint(f"{FKcontrolList[i-1]}", FKgroup, maintainOffset=True)

        FKhyrbridControlsGroup = f"{ribbonName}_FK_controls"
        cmds.parent(FKgroup, FKhyrbridControlsGroup)
        cmds.select(clear=True)

        FKcontrolList.append(FKcontrol)

    # hierarchy fixes
    cmds.parent(FKhyrbridControlsGroup, f"{ribbonName}_controls")

    # VISIBILITY ATTRIBUTES

    # add attribute divider
    cmds.select(controlList[0])
    cmds.addAttr(attributeType="enum",
                 longName="optionsDivider",
                 niceName="——————————",
                 enumName="OPTIONS")
    cmds.setAttr(f"{controlList[0]}.optionsDivider", channelBox=True)
    cmds.select(clear=True)

    # create attribute
    cmds.select(controlList[0])
    cmds.addAttr(attributeType="bool",
                 longName="FKcontrolVisibility",
                 niceName="FK Control Visibility")
    cmds.setAttr(f"{controlList[0]}.FKcontrolVisibility", keyable=True)
    cmds.select(clear=True)

    # connect to control group visibility
    cmds.connectAttr(f"{controlList[0]}.FKcontrolVisibility", f"{ribbonName}_FK_controls.visibility")


    # create proxy attributes
    cmds.select(clear=True)

    for FKIKcontrolList in [controlList[1:], FKcontrolList]:
        for control in FKIKcontrolList:
            for attribute in ["optionsDivider", "FKcontrolVisibility"]:
                cmds.select(control)
                cmds.addAttr(longName=attribute, proxy=f"{controlList[0]}.{attribute}")
                cmds.setAttr(f"{control}.{attribute}", keyable=True)
                cmds.select(clear=True)

    # DRAWING OVERRIDES
    cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideEnabled", True)
    cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideRGBColors", True)

    if FKIKcontrolList[0][0] == "L":
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorR", 1)
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorG", 0.8)
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorB", 0.8)
    elif FKIKcontrolList[0][0] == "R":
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorR", 0.8)
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorG", 0.8)
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorB", 1)
    else:
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorR", 1)
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorG", 1)
        cmds.setAttr(f"{FKhyrbridControlsGroup}.overrideColorB", 0.8)
    



def createSplineIK(ribbonName: str,
                   jointChain: list[str],
                   controlJointList: list[str],
                   followJointList: list[str]) -> str:
    """ Create spline IK setup.
    
    Return name of spline IK curve. """

    # create spline ik
    positions = [cmds.xform(joint, query=True, worldSpace=True, translation=True) for joint in jointChain]
    curve = cmds.curve(name=f"{ribbonName}_IK_curve", degree=3, editPoint=positions)
    curveShape = cmds.listRelatives(curve, shapes=True)[0]


    cmds.ikHandle(startJoint=jointChain[0], endEffector=jointChain[-1], name=f"{ribbonName}_ikHandle",
                  solver="ikSplineSolver", curve=curve, createCurve=False, parentCurve=False)
    
    
    # set up twist and roll attributes
    cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{ribbonName}_twist_multi")
    cmds.shadingNode("plusMinusAverage", asUtility=True, name=f"{ribbonName}_twist_pma")

    # set roll to root control rotation
    cmds.connectAttr(f"{controlJointList[0]}.rotateX", f"{ribbonName}_ikHandle.roll", force=True)
    cmds.connectAttr(f"{controlJointList[0]}.rotateX", f"{ribbonName}_twist_multi.input1X", force=True)
    cmds.setAttr(f"{ribbonName}_twist_multi.input2X", -1)   # remove double rotation

    cmds.connectAttr(f"{controlJointList[0]}.rotateX", f"{ribbonName}_ikHandle.roll", force=True)

    # set twist to both controls combined rotation
    cmds.connectAttr(f"{controlJointList[-1]}.rotateX", f"{ribbonName}_twist_pma.input1D[0]", force=True)
    cmds.connectAttr(f"{ribbonName}_twist_multi.outputX", f"{ribbonName}_twist_pma.input1D[1]", force=True)

    cmds.connectAttr(f"{ribbonName}_twist_pma.output1D", f"{ribbonName}_ikHandle.twist", force=True)


    # set up middle twist
    # if there is only 1 mid controller, twist more bindjoints with the mid controller
    # else only control the bind joint in the same position as the mid control

    if len(controlJointList) == 3:
        midJoint = len(jointChain) // 2

        cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{ribbonName}_mid_twist_multi")
        cmds.setAttr(f"{ribbonName}_twist_multi.input2Y", 0.5)
        cmds.setAttr(f"{ribbonName}_twist_multi.input2Z", 0.25)

        # connect mid joint
        cmds.connectAttr(f"{controlJointList[1]}.rotateX", f"{ribbonName}_mid_twist_multi.input1X", force=True)
        cmds.connectAttr(f"{ribbonName}_mid_twist_multi.outputX", f"{followJointList[midJoint]}.rotateX", force=True)

        # connect 2nd mid joints
        cmds.connectAttr(f"{controlJointList[1]}.rotateX", f"{ribbonName}_mid_twist_multi.input1Y", force=True)
        cmds.connectAttr(f"{ribbonName}_mid_twist_multi.outputY", f"{followJointList[midJoint - 1]}.rotateX", force=True)
        cmds.connectAttr(f"{ribbonName}_mid_twist_multi.outputY", f"{followJointList[midJoint + 1]}.rotateX", force=True)

        # connect 3nd mid joints
        cmds.connectAttr(f"{controlJointList[1]}.rotateX", f"{ribbonName}_mid_twist_multi.input1Z", force=True)
        cmds.connectAttr(f"{ribbonName}_mid_twist_multi.outputZ", f"{followJointList[midJoint - 2]}.rotateX", force=True)
        cmds.connectAttr(f"{ribbonName}_mid_twist_multi.outputZ", f"{followJointList[midJoint + 2]}.rotateX", force=True)

    else:
        for midJoint in controlJointList[1:-1]:
            midJointName = "_".join(midJoint.split("_")[:-1])
            bindJointName = f"{midJointName}_BIND_JNT"
            
            cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{midJoint}_twist_multi")
            cmds.setAttr(f"{midJoint}_twist_multi.input2Y", 0.5)
            cmds.setAttr(f"{midJoint}_twist_multi.input2Z", 0.25)

            cmds.connectAttr(f"{midJoint}.rotateX", f"{midJoint}_twist_multi.input1X", force=True)
            cmds.connectAttr(f"{midJoint}_twist_multi.outputX", f"{bindJointName}.rotateX", force=True)


    # add squash and stretch
    cmds.shadingNode("curveInfo", asUtility=True, name=f"{ribbonName}_IK_curve_info")
    cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{ribbonName}_stretchFactor")

    cmds.connectAttr(f"{curveShape}.worldSpace[0]", f"{ribbonName}_IK_curve_info.inputCurve", force=True)
    cmds.connectAttr(f"{ribbonName}_IK_curve_info.arcLength", f"{ribbonName}_stretchFactor.input1X", force=True)

    # store length of curve
    curveLength = cmds.getAttr(f"{ribbonName}_IK_curve_info.arcLength")
    cmds.setAttr(f"{ribbonName}_stretchFactor.input2X", curveLength)

    # set to divide
    cmds.setAttr(f"{ribbonName}_stretchFactor.operation", 2)
    
    # connect scale factor to  driver joints scale x
    for joint in jointChain:
        cmds.connectAttr(f"{ribbonName}_stretchFactor.outputX", f"{joint}.scaleX", force=True)
    

    # update hierarchy
    cmds.parent(curve, f"{ribbonName}_GRP")
    cmds.parent(f"{ribbonName}_ikHandle", f"{ribbonName}_GRP")


    return curve



def _______________CREATE_SURFACE_______________(): pass


def createCurveFromEdge(curveType: str,
                        simplifyCurveBox: str, *args):
    """ Create a curve from an edge selection. """

    selection = cmds.ls(selection=True)
    simplifyCurve = cmds.checkBox(simplifyCurveBox, query=True, value=True)

    if not selection:
        cmds.error("No edges selected.",
                noContext=True)
    else:
        curveName = (f"{curveType}Curve_TEMP")

        if cmds.objExists(curveName):
            cmds.delete(curveName)


        """positionList = []

        # convert to vertices
        vertexSelection = cmds.polyListComponentConversion(selection, toVertex=True)[0]
        objectName = vertexSelection.split(".")[0]
        indexRange = vertexSelection.split("[")[1][:-1]
        indexStart = int(indexRange.split(":")[0])
        indexEnd = int(indexRange.split(":")[1])

        vertexList = []

        for i in range(indexStart, indexEnd):
            vertexList.append(f"{objectName}.vtx[{i}]")

        print(vertexList)

        for vertex in vertexList:
            position = cmds.xform(vertex, query=True, worldSpace=True, translation=True)
            print(position)
            positionList.append(position)

        cmds.curve(name=curveName, degree=3, point=positionList)
        cmds.closeCurve(curveName)"""

        curve = cmds.polyToCurve(name=curveName, form=2, degree=3)[0]
        spans = cmds.getAttr((f"{curve}.spans"))
        """
        # rebuild curve
        curvePointList = []
        for i in range(int(spans)):
            curvePoint = cmds.xform(f"{curve}.cv[{i}]", query=True, worldSpace=True, translation=True)
            curvePointList.append(curvePoint)
        """
        """newCurve = cmds.curve(degree=3, point=curvePointList)
        cmds.delete(curveName)
        cmds.rename(newCurve, curveName)

        cmds.closeCurve(curveName, constructionHistory=True, replaceOriginal=True)
        cmds.rebuildCurve(curve, spans=spans)"""

        if simplifyCurve:
            cmds.rebuildCurve(curve, spans=(spans / 2))

        cmds.delete(curveName, constructionHistory=True)



def createNurbsPlaneFromCurves(ribbonName: str,
                               innerCurve: str,
                               outerCurve: str,
                               reverseRibbon: bool) -> int:
    """ Create the nurbs plane from two curves.
    
    Return spans/divisons. """

    # USE mel.eval("ikSpringSolver") to evaluate the command?

    curveSpans = cmds.getAttr((f"{innerCurve}Shape.maxValue"))
    innerCurveSeam = cmds.pointOnCurve(innerCurve, parameter=1, position=True)
    outerCurveShape = cmds.listRelatives(outerCurve, shapes=True)[0]
    """
    # get original curves knots
    cmds.shadingNode("curveInfo", asUtility=True, name=f"{outerCurve}_curveInfo")
    cmds.connectAttr(f"{outerCurveShape}.worldSpace[0]", f"{outerCurve}_curveInfo.inputCurve", force=True)
    knotList = cmds.getAttr(f"{outerCurve}_curveInfo.knots[*]")

    # find point on outer curve that is closest to inner curve's curve seam
    outerCurveCVList = []
    for i in range(int(curveSpans)):
        outerCurveCV = f"{outerCurve}.cv[{i}]"
        outerCurveCVList.append(outerCurveCV)

    closestCV = getClosestObject(f"{innerCurve}.cv[0]", outerCurveCVList)
    closestCVindex = float(closestCV.split("[")[1][:-1])

    
    # split the position list at the index where the closest point is, then append the first part onto the end to re order them with the closest point at the start
    list1 = outerCurvePointList[:closestPoint]
    list2 = outerCurvePointList[closestPoint:]
    newList = list2 + list1
    
    newList = newList + [newList[:5].reverse()]

    cmds.detachCurve(outerCurve, parameter=closestCVindex, replaceOriginal=True)
    cmds.closeCurve(outerCurve, replaceOriginal=True)
    cmds.rebuildCurve(outerCurve, spans=curveSpans)
    cmds.rebuildCurve(innerCurve, spans=curveSpans)
    """

    #cmds.delete(outerCurve, constructionHistory=True)
    #cmds.delete(innerCurve, constructionHistory=True)

    
    if reverseRibbon:
        cmds.loft(innerCurve, outerCurve,
                  name=f"{ribbonName}_RIBBON",
                  autoReverse=False, reverse=False,
                  reverseSurfaceNormals=True,
                  degree=1, uniform=True, rebuild=True)
    else:
        cmds.loft(outerCurve, innerCurve,
                  name=f"{ribbonName}_RIBBON",
                  autoReverse=False, reverse=False,
                  reverseSurfaceNormals=True,
                  degree=1, uniform=True, rebuild=True)


    # cmds.rebuildSurface(ribbonName, spansV = 1, spansU = curveSpans)

    spans = cmds.getAttr((f"{ribbonName}_RIBBONShape.spansU"))

    # delete temp curves
    cmds.delete(innerCurve, outerCurve)
    
    return spans



def createSurfaceControlJoints(ribbonName: str,
                               globalScale: float,
                               followJointList: list[str],
                               controlRatio: str) -> list[str]:
    """ Create control joints for a surface ribbon.
    
    Return list of control joints. """

    controlJointName = f"{ribbonName}_CTRLJNT#"
    controlJointList = []
    controlJointRadius = 0.2 * globalScale
    cmds.group(name=f"{ribbonName}_controlJoints_GRP", empty=True)

    # control ratio
    if controlRatio == "1:2":
        ratio = 2
        count = 1
    elif controlRatio == "1:2 +1":
        ratio = 2
        count = 2
    elif controlRatio == "1:3":
        ratio = 3
        count = 1
    elif controlRatio == "1:3 +1":
        ratio = 3
        count = 2
    elif controlRatio == "1:3 +2":
        ratio = 3
        count = 3
    else:
        ratio = 1
        count = 1

    for bindJoint in followJointList:
            if count % ratio == 0:
                cmds.select(clear=True)

                # create control joint and move to bind joint
                controlJoint = cmds.joint(name=controlJointName, radius=controlJointRadius)
                cmds.matchTransform(controlJoint, bindJoint)

                cmds.parent(controlJoint, f"{ribbonName}_controlJoints_GRP")
                cmds.makeIdentity(controlJoint, apply=True, rotate=True, translate=True)

                controlJointList.append(controlJoint)

            count = count + 1
    
    
    return controlJointList



def createSurfaceControls(ribbonName,
                          controlJointList: list[str],
                          controlSize: float,
                          controlOffset: float):
    """ Create controls for the control joints on a surface ribbon. """

    ribbonWidth = cmds.getAttr(f"{ribbonName}_RIBBON.maxValueV")
    controlRadius = (ribbonWidth / 2) * controlSize
    controlName = f"{ribbonName}_CTRL#"
    controlGroup = f"{ribbonName}_controls"

    if not cmds.objExists(controlGroup):
        cmds.group(name=controlGroup, empty=True)


    for controlJoint in controlJointList:

        control, group = createControl(shape="circle", name=controlName, size=controlRadius)

        # apply offset by moving control out
        cmds.move(0, 0, -controlOffset, control)
        cmds.move(0, 0, 0, f"{control}.scalePivot", f"{control}.rotatePivot")
        cmds.makeIdentity(control, apply=True, translate=True)

        # move to control joint and transfer transforms
        cmds.matchTransform(group, controlJoint)
        transferTransformsToOPM(group)

        # fix rotations
        cmds.setAttr(f"{control}.rotateX", 90)
        cmds.makeIdentity(control, apply=True, rotate=True)

        cmds.parentConstraint(control, controlJoint, maintainOffset=True)
        cmds.parent(group, f"{ribbonName}_controls")
        cmds.select(clear=True)



def _______________BUILD_______________(): pass


def buildCustomRibbon(ribbonNameField: str,
                      globalScaleField: str,
                      addControlsBox: str,
                      controlSizeField: str,
                      spansField: str,
                      customMidControlsField: str,
                      ribbonSizeField: str,
                      directionMenu: str,
                      orientationMenu: str,
                      *args):
    """ Build a custom ribbon using the options specified in the UI. """

    # BUILD NAMES FROM UI
    ribbonName = cmds.textField(ribbonNameField, query=True, text=True)
    globalScale = cmds.floatField(globalScaleField, query=True, value=True)

    addControls = cmds.checkBox(addControlsBox, query=True, value=True)
    controlSize = cmds.floatField(controlSizeField, query=True, value=True)

    spans = cmds.intField(spansField, query=True, value=True)
    midControls = cmds.intField(customMidControlsField, query=True, value=True)
    ribbonSize = cmds.floatField(ribbonSizeField, query=True, value=True)

    direction = cmds.optionMenu(directionMenu, query=True, value=True)
    orientation = cmds.optionMenu(orientationMenu, query=True, value=True)

  
    # build ribbon if no errors occur
    if len(ribbonName) == 0:
        cmds.error("No ribbon name entered.",
                   noContext=True)

    else:
        if direction == "Vertical" and orientation == "Y":
            cmds.error("Direction can't be vertical if the orientation is Y.",
                       noContext=True)

        else:
            ribbonName = checkNameForDup(ribbonName)

            createCustomNurbsPlane(ribbonName=ribbonName,
                                   globalScale=globalScale,
                                   spans=spans,
                                   orientation=orientation)

            followJointList = createFollowJoints(ribbonName=ribbonName,
                                                 globalScale=globalScale)

            if direction == "Vertical":
                cmds.setAttr(f"{ribbonName}_RIBBON.rotate{orientation}", -90)
                cmds.makeIdentity(f"{ribbonName}_RIBBON", apply=True, rotate=True)

            if addControls:
                controlJointList = createCustomControlJoints(ribbonName=ribbonName,
                                                             globalScale=globalScale,
                                                             followJointList=followJointList,
                                                             midControls=midControls)
                skinJoints(f"{ribbonName}_RIBBON", controlJointList)
                createCustomControls(ribbonName=ribbonName,
                                     controlJointList=controlJointList,
                                     controlSize=controlSize)

    cmds.select(clear=True)



def buildJointRibbon(ribbonNameField: str,
                     globalScaleField: str,
                     addControlsBox: str,
                     controlSizeField: str,
                     jointMidControlsField: str,
                     tweakControlsBox: str,
                     FKhybridControlsBox: str,
                     IKsplineBox: str,
                     *args):
    """ Build a custom ribbon using the options specified in the UI. """


    # BUILD NAMES FROM UI
    ribbonName = cmds.textField(ribbonNameField, query=True, text=True)
    globalScale = cmds.floatField(globalScaleField, query=True, value=True)

    addControls = cmds.checkBox(addControlsBox, query=True, value=True)
    controlSize = cmds.floatField(controlSizeField, query=True, value=True)

    midControls = cmds.intField(jointMidControlsField, query=True, value=True)
    tweakControls = cmds.checkBox(tweakControlsBox, query=True, value=True)
    FKhybridControls = cmds.checkBox(FKhybridControlsBox, query=True, value=True)
    IKspline = cmds.checkBox(IKsplineBox, query=True, value=True)

    selection = cmds.ls(selection=True, type="joint")

    # build ribbon if no errors occur
    if len(ribbonName) == 0:
        cmds.error("No ribbon name entered.",
                   noContext=True)
    
    elif not selection:
        cmds.error("No joints selected.",
                   noContext=True)
        
    elif len(selection) < 2:
        cmds.error("Not enough joints selected.",
                   noContext=True)

    else:
        ribbonName = checkNameForDup(ribbonName)

        startJoint = selection[0]
        endJoint = selection[1]

        jointChain = getJointChain(startJoint=startJoint, endJoint=endJoint)
        spans = createNurbsPlaneFromJoints(ribbonName=ribbonName,
                                           globalScale=globalScale,
                                           jointChain=jointChain)

        followJointList = createFollowJoints(ribbonName=ribbonName,
                                             globalScale=globalScale,
                                             jointChain=jointChain)
        
        if addControls:
            controlJointList = createJointControlJoints(ribbonName=ribbonName,
                                                        globalScale=globalScale,
                                                        followJointList=followJointList,
                                                        jointChain=jointChain,
                                                        midControls=midControls)
            controlList = createJointControls(ribbonName=ribbonName,
                                              controlJointList=controlJointList,
                                              size=controlSize)
        
            if IKspline:
                curveName = createSplineIK(ribbonName=ribbonName,
                                           jointChain=jointChain,
                                           controlJointList=controlJointList,
                                           followJointList=followJointList)

                skinJoints(geometryName=curveName, jointList=controlJointList)
                skinJoints(geometryName=f"{ribbonName}_RIBBON", jointList=jointChain)

            else:
                skinJoints(geometryName=f"{ribbonName}_RIBBON", jointList=controlJointList)
                # connectRibbonToJoints(jointChain=jointChain, followJointList=followJointList)
            
            if tweakControls:
                createTweakControls(ribbonName=ribbonName,
                                    jointChain=jointChain,
                                    size=controlSize)

            if FKhybridControls:
                createFKhybridControls(ribbonName=ribbonName,
                                       size=controlSize,
                                       controlList=controlList)


    cmds.select(clear=True)



def buildSurfaceRibbon(ribbonNameField: str,
                       globalScaleField: str,
                       addControlsBox: str,
                       controlSizeField: str,
                       controlOffsetField: str,
                       controlRatioMenu: str,
                       reverseRibbonBox: str,
                       closedRibbonBox: str,
                       *args):
    """ Build a ribbon from a surface using the options specified in the UI. """


    # BUILD NAMES FROM UI
    ribbonName = cmds.textField(ribbonNameField, query=True, text=True)
    globalScale = cmds.floatField(globalScaleField, query=True, value=True)

    addControls = cmds.checkBox(addControlsBox, query=True, value=True)
    controlSize = cmds.floatField(controlSizeField, query=True, value=True)
    controlOffset = cmds.floatField(controlOffsetField, query=True, value=True)
    controlRatio = cmds.optionMenu(controlRatioMenu, query=True, value=True)

    reverseRibbon = cmds.checkBox(reverseRibbonBox, query=True, value=True)
    closedRibbon = cmds.checkBox(closedRibbonBox, query=True, value=True)

    # curve names
    innerCurve = "innerCurve_TEMP"
    outerCurve = "outerCurve_TEMP"


    # build ribbon if no errors occur
    if len(ribbonName) == 0:
        cmds.error("No ribbon name entered.",
                   noContext=True)

    else:
        ribbonName = checkNameForDup(ribbonName)
        
        spans = createNurbsPlaneFromCurves(ribbonName=ribbonName,
                                           innerCurve=innerCurve,
                                           outerCurve=outerCurve,
                                           reverseRibbon=reverseRibbon)
        
        if closedRibbon:
            spans = spans - 1

        followJointList = createFollowJoints(ribbonName=ribbonName,
                                             globalScale=globalScale)
        
        # follicleList = createFollicles(ribbonName=ribbonName)
        # bindJointList = createBindJoints(ribbonName=ribbonName,
        #                                  globalScale=globalScale,
        #                                  follicleList=follicleList)

        if addControls:
            controlJointList = createSurfaceControlJoints(ribbonName=ribbonName,
                                                          globalScale=globalScale,
                                                          followJointList=followJointList,
                                                          controlRatio=controlRatio)
            skinJoints(geometryName=f"{ribbonName}_RIBBON", jointList=controlJointList)
            createSurfaceControls(ribbonName=ribbonName,
                                  controlJointList=controlJointList,
                                  controlSize=controlSize,
                                  controlOffset=controlOffset)


    cmds.select(clear=True)



createUI(buildCustomRibbon, buildJointRibbon, buildSurfaceRibbon)