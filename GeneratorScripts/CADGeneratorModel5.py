import Rhino 
import scriptcontext
import rhinoscriptsyntax as rs
import System.Guid 
import random
import json
import sys
import os
import math


def SquareDistanceBetweenTwoPoints(point1,point2):
    difference = Rhino.Geometry.Point3d((point2.X-point1.X),
                    (point2.Y-point1.Y),
                    (point2.Z-point1.Z))
                    
    return difference.X*difference.X + difference.Y*difference.Y +difference.Z*difference.Z
    
    
def AddBrepBox(point1, point2):
    box = Rhino.Geometry.BoundingBox(point1, point2)
    brep = box.ToBrep()
    rc = Rhino.Commands.Result.Failure
    return brep
    
def AddCylinder(centerPoint,orientation,radius,height):
    plane = Rhino.Geometry.Plane(centerPoint, orientation)
    circle = Rhino.Geometry.Circle(plane, radius)
    cylinder = Rhino.Geometry.Cylinder(circle, height)
    brep = cylinder.ToBrep(True, True)
    return brep
    
def GenerateCylindricalSlot():
    filled = False
    radius = 6 + random.random()*6
    length = 15 + random.random()*5
    
    centerPoint = Rhino.Geometry.Point3d(0,0,0)
    orientation = Rhino.Geometry.Vector3d(1,0,0)
    brepCylinder = AddCylinder(centerPoint,orientation,radius,length)
    curveLength = 3 + random.random()*(2*math.pi*radius -3)
    angleCovered = (curveLength/2*math.pi*radius)*2*math.pi
    startAngle = 0 + random.random()*(2*math.pi-angleCovered)
    endAngle = startAngle + angleCovered
    widthOfSlot = 2 + random.random()*(6-2);
    randomPointOnALength = 2 + random.random()*(length -2 - widthOfSlot/2);
    curvPoint1 = Rhino.Geometry.Point3d(randomPointOnALength,radius*(math.cos(startAngle)),radius*(math.sin(startAngle)))
    curvPoint2 = Rhino.Geometry.Point3d(randomPointOnALength,radius*(math.cos(startAngle*0.5 + endAngle*0.5)),radius*(math.sin(startAngle*0.5 + endAngle*0.5)))
    curvPoint3 = Rhino.Geometry.Point3d(randomPointOnALength,radius*(math.cos(endAngle)),radius*(math.sin(endAngle)))
    arc = rs.AddArc3Pt(curvPoint1,curvPoint3,curvPoint2)
    arcBrep = rs.coercecurve(arc)
    height = 2 + random.random()*(4-2)
    point1 = Rhino.Geometry.Point3d(randomPointOnALength - widthOfSlot/2 ,(radius+height/2)*math.cos(startAngle),(radius+height/2)*math.sin(startAngle))
    point2 = Rhino.Geometry.Point3d(randomPointOnALength - widthOfSlot/2 ,(radius-height/2)*math.cos(startAngle),(radius-height/2)*math.sin(startAngle))
    point3 = Rhino.Geometry.Point3d(randomPointOnALength + widthOfSlot/2 ,(radius-height/2)*math.cos(startAngle),(radius-height/2)*math.sin(startAngle))
    point4 = Rhino.Geometry.Point3d(randomPointOnALength + widthOfSlot/2 ,(radius+height/2)*math.cos(startAngle),(radius+height/2)*math.sin(startAngle))
    point5 = point1
    points = [point1,point2,point3,point4,point5]
    rectSrf = rs.AddPolyline(points)
    rectSurfBrep = rs.coercecurve(rectSrf)
    rs.DeleteObjects(arc)
    rs.DeleteObjects(rectSrf)
    breps = Rhino.Geometry.Brep.CreateFromSweep(arcBrep,rectSurfBrep,True,scriptcontext.doc.ModelAbsoluteTolerance)
    brepsCurveBox = Rhino.Geometry.Brep.CapPlanarHoles(breps[0],scriptcontext.doc.ModelAbsoluteTolerance)
    brepArray = Rhino.Geometry.Brep.CreateBooleanDifference([brepCylinder],[brepsCurveBox],scriptcontext.doc.ModelAbsoluteTolerance)
    scriptcontext.doc.Views.Redraw()
    if(brepArray is not None and  brepCylinder.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume == brepArray[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume):
        for brep in brepArray: 
            scriptcontext.doc.Objects.AddBrep(brep)
        scriptcontext.doc.Views.Redraw()
        return 1
    else :
        return 0
    
if(__name__ == "__main__"):
    i = 0
    while(i<10):
        i = i + GenerateCylindricalSlot()
    