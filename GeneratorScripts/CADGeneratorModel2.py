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
    
def GenerateSlotsForSteppedModel():
    point1 = Rhino.Geometry.Point3d(10 + random.random()*5,
    10 + random.random()*5,
    10 + random.random()*5)
    point2 = Rhino.Geometry.Point3d(point1.X + 10 + random.random()*5,
    point1.Y,
    point1.Z + 10 + random.random())
    brepBox1 = AddBrepBox(Rhino.Geometry.Point3d(0,0,0),point1)
    brepBox2 = AddBrepBox(Rhino.Geometry.Point3d(point1.X,0,0),
    Rhino.Geometry.Point3d(point2))
    brepArray = [brepBox1,brepBox2]
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    orientationIdx = 0 # random.randint(0,5)
    straight = True #bool(random.randint(0,1))
    leftMargin = 3
    if(orientationIdx == 0):
        lowerBlock = bool(random.randint(0,1))
        if(straight):
            xAxis = bool(random.randint(0,1))
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point1.X-leftMargin)
                leftPointY = leftMargin + random.random()*(point1.Y- leftMargin)
                height  = 2 + random.random()*2
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point1.X-leftPointX)
                    rightPointY = leftPointY
                    width = 2.5 + random.random()*(min(leftPointY,point2.Y-leftPointY)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,leftPointY-width/2,point1.Z-height)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX, rightPointY + width/2,point1.Z)
                else:
                    rightPointX = leftPointX
                    rightPointY = leftPointY + random.random()*(point1.Y - leftPointY)
                    width = 2.5 + random.random()*(min(leftPointX,point2.X-leftPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX-width/2,leftPointY,point1.Z-height)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,rightPointY,point1.Z)
            else:
                leftPointX = point1.X + leftMargin + random.random()*(point2.X - point1.X - leftMargin)
                leftPointY = leftMargin + random.random()*(point2.Y- leftMargin)
                height  = 2 + random.random()*2
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point2.X-leftPointX)
                    rightPointY = leftPointY
                    width = 2.5 + random.random()*(min(leftPointY,point2.Y-leftPointY)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,leftPointY-width/2,point2.Z-height)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX, rightPointY + width/2,point2.Z)
                else:
                    rightPointX = leftPointX
                    rightPointY = leftPointY + random.random()*(point2.Y - leftPointY)
                    width = 2.5 + random.random()*(min(leftPointX,point2.X-leftPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX-width/2,leftPointY,point2.Z-height)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,rightPointY,point2.Z)
        brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
    brepSubtractArray = [brepToSubtract]
    
    brepBoxUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArray,tolerance)
    brepAddArray = [brepBoxUnion[0]]
    brepModel = Rhino.Geometry.Brep.CreateBooleanDifference(brepAddArray,brepSubtractArray,tolerance)
    for brep in brepModel:
        if(scriptcontext.doc.Objects.AddBrep(brep) != System.Guid.Empty ):           
            scriptcontext.doc.Views.Redraw()
        #rs.Command("_-SaveAs"+" F:\ModuleWorks\RhinoNoHoleIGS\\" + str(modelIdx) + ".igs" + " enter" + " enter",True)
        objs = rs.AllObjects(select = True)
        #rs.Command("_Delete ")
        
if( __name__ == "__main__" ):
    
    i = 0
    while (i < 10):
        GenerateSlotsForSteppedModel()
        i = i + 1
    