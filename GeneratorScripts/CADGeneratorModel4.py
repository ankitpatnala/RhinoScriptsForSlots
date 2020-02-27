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
    orientationIdx = random.randint(0,5)
    straight = bool(random.randint(0,1))
    leftMargin = 3
    filled = False
    height  = 2 + random.random()*2
    randomEdge = random.randint(0,3)
    filletRadius = 2+ 2*random.random()
    if(randomEdge == 0):
        filletBrepBox = AddBrepBox(Rhino.Geometry.Point3d(0,0,0),Rhino.Geometry.Point3d(filletRadius,filletRadius,point1.Z))
        filletCylinder = AddCylinder(Rhino.Geometry.Point3d(filletRadius,filletRadius,0),Rhino.Geometry.Vector3d(0,0,1),filletRadius,point1.Z)
        brepFillet = Rhino.Geometry.Brep.CreateBooleanDifference(filletBrepBox,filletCylinder,tolerance)[0]
    elif(randomEdge == 1):
        filletBrepBox = AddBrepBox(Rhino.Geometry.Point3d(point2.X - filletRadius,0,0),Rhino.Geometry.Point3d(point2.X,filletRadius,point2.Z))
        filletCylinder = AddCylinder(Rhino.Geometry.Point3d(point2.X - filletRadius,filletRadius,0),Rhino.Geometry.Vector3d(0,0,1),filletRadius,point2.Z)
        brepFillet = Rhino.Geometry.Brep.CreateBooleanDifference(filletBrepBox,filletCylinder,tolerance)[0]
    elif(randomEdge == 2):
        filletBrepBox = AddBrepBox(Rhino.Geometry.Point3d(point2.X - filletRadius,point2.Y - filletRadius ,0),Rhino.Geometry.Point3d(point2.X,point2.Y,point2.Z))
        filletCylinder = AddCylinder(Rhino.Geometry.Point3d(point2.X - filletRadius,point2.Y - filletRadius ,0),Rhino.Geometry.Vector3d(0,0,1),filletRadius,point2.Z)
        brepFillet = Rhino.Geometry.Brep.CreateBooleanDifference(filletBrepBox,filletCylinder,tolerance)[0]
    else:
        filletBrepBox = AddBrepBox(Rhino.Geometry.Point3d(0,point1.Y - filletRadius ,0),Rhino.Geometry.Point3d(filletRadius,point1.Y,point1.Z))
        filletCylinder = AddCylinder(Rhino.Geometry.Point3d(filletRadius,point1.Y - filletRadius ,0),Rhino.Geometry.Vector3d(0,0,1),filletRadius,point1.Z)
        brepFillet = Rhino.Geometry.Brep.CreateBooleanDifference(filletBrepBox,filletCylinder,tolerance)[0]
    
    if(orientationIdx == 0):
        lowerBlock = bool(random.randint(0,1))
        if(straight):
            xAxis = bool(random.randint(0,1))
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point1.X-leftMargin)
                leftPointY = leftMargin + random.random()*(point1.Y- leftMargin)
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point1.X-leftPointX-3)
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
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            else:
                leftPointX = point1.X + leftMargin + random.random()*(point2.X - point1.X - leftMargin)
                leftPointY = leftMargin + random.random()*(point2.Y- leftMargin)
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point2.X-leftPointX-3)
                    rightPointY = leftPointY
                    width = 2.5 + random.random()*(min(leftPointY,point2.Y-leftPointY)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,leftPointY-width/2,point2.Z-height)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX, rightPointY + width/2,point2.Z)
                else:
                    rightPointX = leftPointX
                    rightPointY = leftPointY + random.random()*(point2.Y - leftPointY-3)
                    width = 2.5 + random.random()*(min(leftPointX,point2.X-leftPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX-width/2,leftPointY,point2.Z-height)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,rightPointY,point2.Z)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(leftPointX,leftPointY,0),
            Rhino.Geometry.Point3d(rightPointX,rightPointY,0))
            
        else:
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point1.X-leftMargin)
                leftPointY = leftMargin + random.random()*(point1.Y-leftMargin)
                rightPointX = leftPointX + random.random()*(point1.X - leftPointX-3)
                rightPointY = leftPointY + random.random()*(point1.Y - leftPointY-3)
                width = 2.5 + random.random()*(min(leftPointY,point1.Y-rightPointY)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(leftPointX,leftPointY,0),
                Rhino.Geometry.Point3d(rightPointX,rightPointY,0))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointX-leftPointX),(rightPointY-leftPointY),0)
                points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2, leftPointY - perpendicularVector.Y*width/2,point1.Z - height),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2, leftPointY + perpendicularVector.Y*width/2,point1.Z - height),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2, rightPointY + perpendicularVector.Y*width/2,point1.Z - height),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2, rightPointY - perpendicularVector.Y*width/2,point1.Z - height),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2, rightPointY - perpendicularVector.Y*width/2,point1.Z),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2, rightPointY + perpendicularVector.Y*width/2,point1.Z),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2, leftPointY + perpendicularVector.Y*width/2,point1.Z),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2, leftPointY - perpendicularVector.Y*width/2,point1.Z)]
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
            else:
                leftPointX = leftMargin + point1.X + random.random()*(point2.X - leftMargin - point1.X)
                leftPointY = leftMargin + random.random()*(point2.Y - leftMargin)
                rightPointX = leftPointX + random.random()*(point2.X - leftPointX-3)
                rightPointY = leftPointY + random.random()*(point2.Y - leftPointY -3)
                width = 2.5 + random.random()*(min(leftPointY, point1.Y - leftPointY)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(leftPointX,leftPointY,0),
                Rhino.Geometry.Point3d(rightPointX,rightPointY,0))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointX-leftPointX),(rightPointY-leftPointY),0)
                points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2, leftPointY - perpendicularVector.Y*width/2,point2.Z - height),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2, leftPointY + perpendicularVector.Y*width/2,point2.Z - height),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2, rightPointY + perpendicularVector.Y*width/2,point2.Z - height),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2, rightPointY - perpendicularVector.Y*width/2,point2.Z - height),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2, rightPointY - perpendicularVector.Y*width/2,point2.Z),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2, rightPointY + perpendicularVector.Y*width/2,point2.Z),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2, leftPointY + perpendicularVector.Y*width/2,point2.Z),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2, leftPointY - perpendicularVector.Y*width/2,point2.Z)]
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox2,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
    elif (orientationIdx == 1):
        leftPointX = leftMargin + random.random()*(point2.X-leftMargin)
        leftPointY = leftMargin + random.random()*(point2.Y-leftMargin)
        if(straight):
            xAxis = bool(random.randint(0,1))
            if(xAxis):
                rightPointX = leftPointX + random.random()*(point2.X - leftPointX-3)
                rightPointY = leftPointY
                width = 2.5 + random.random()*(min(leftPointY,point2.Y - leftPointY)-2.5)
                bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,leftPointY - width/2,0)
                upperDiagonal = Rhino.Geometry.Point3d(rightPointX,rightPointY + width/2,height)
            else:
                rightPointX = leftPointX
                rightPointY = leftPointY + random.random()*(point2.Y - leftPointY -3)
                width = 2.5 + random.random()*(min(leftPointX,point2.X - leftPointX)-2.5)
                bottomDiagonal = Rhino.Geometry.Point3d(leftPointX - width/2,leftPointY,0)
                upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,rightPointY, height)
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(leftPointX,leftPointY,0),
            Rhino.Geometry.Point3d(rightPointX,rightPointY,0))
            brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
            brepTotalVolume = brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
        else:
            rightPointX = leftPointX + random.random()*(point2.X-leftPointX)
            rightPointY = leftPointY + random.random()*(point2.Y -leftPointY)
            width = 2.5 + random.random()*(min(leftPointY,
            point2.Y -leftPointY,
            rightPointY,
            point2.Y -rightPointY)-2.5)
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(leftPointX,leftPointY,0),
            Rhino.Geometry.Point3d(rightPointX,rightPointY,0))
            perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointX-leftPointX),(rightPointY-leftPointY),0)
            points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2, leftPointY - perpendicularVector.Y*width/2,height),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2, leftPointY + perpendicularVector.Y*width/2,height),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2, rightPointY + perpendicularVector.Y*width/2,height),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2, rightPointY - perpendicularVector.Y*width/2,height),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2, rightPointY - perpendicularVector.Y*width/2,0),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2, rightPointY + perpendicularVector.Y*width/2,0),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2, leftPointY + perpendicularVector.Y*width/2,0),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2, leftPointY - perpendicularVector.Y*width/2,0)]
            plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
            brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
            brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArray,tolerance)
            brepTotalVolume = Rhino.Geometry.Brep.CreateBooleanUnion([brepUnion[0],brepToSubtract],tolerance)[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
            if(brepTotalVolume == brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume and brepUnion is not None):
                brepTotalVolume = brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
            else:
                brepTotalVolume = 100000
    elif(orientationIdx == 2):
        lowerBlock = bool(random.randint(0,1))
        if(straight):
            yAxis = bool(random.randint(0,1))
            if(lowerBlock):
                leftPointY = leftMargin + random.random()*(point1.Y - leftMargin)
                leftPointZ = leftMargin + random.random()*(point1.Z - leftMargin)
                if(yAxis):
                    rightPointY = leftPointY + random.random()*(point1.Y-leftPointY-3)
                    rightPointZ = leftPointZ
                    width = 2.5 + random.random()*(min(leftPointZ- point1.Z,point2.Z-rightPointZ)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(point1.X,leftPointY,leftPointZ-width/2)
                    upperDiagonal = Rhino.Geometry.Point3d(point1.X + height, rightPointY, rightPointZ + width/2)
                else:
                    rightPointY = leftPointY
                    rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ)
                    width = 2.5 + random.random()*(min(leftPointY,point1.Y-leftPointY)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(point1.X,leftPointY - width/2,leftPointZ)
                    upperDiagonal = Rhino.Geometry.Point3d(point1.X + height,rightPointY + width/2,rightPointZ)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            else:
                leftPointY = leftMargin + random.random()*(point1.Y -leftMargin)
                leftPointZ = leftMargin + point1.Z + random.random()*(point2.Z -point1.Z - leftMargin)
                if(yAxis):
                    rightPointY = leftPointY + random.random()*(point2.Y-leftPointY-3)
                    rightPointZ = leftPointZ
                    width = 2.5 + random.random()*(min(leftPointZ - point1.Z ,point2.Z - rightPointZ )-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(point1.X,leftPointY,leftPointZ-width/2)
                    upperDiagonal = Rhino.Geometry.Point3d(point1.X + height, rightPointY ,rightPointZ + width/2)
                else:
                    rightPointY = leftPointY
                    rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ-3)
                    width = 2.5 + random.random()*(min(leftPointY,point2.Y-leftPointY)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(0,leftPointY - width/2,leftPointZ)
                    upperDiagonal = Rhino.Geometry.Point3d(height,rightPointY + width/2,rightPointZ)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(0,leftPointY,leftPointZ),
            Rhino.Geometry.Point3d(0,rightPointY,rightPointZ))
        else:
            if(lowerBlock):
                leftPointY = leftMargin + random.random()*(point1.Y-leftMargin)
                leftPointZ = leftMargin + random.random()*(point1.Z-leftMargin)
                rightPointY = leftPointY + random.random()*(point1.Y - leftPointY - 3)
                rightPointZ = leftPointZ + random.random()*(point1.Z - leftPointZ - 3)
                width = 2.5 + random.random()*(min(leftPointY,point1.Y-rightPointY)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(0,leftPointY,leftPointZ),
                Rhino.Geometry.Point3d(0,rightPointY,rightPointZ))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(0,-1*(rightPointZ-leftPointZ),(rightPointY-leftPointY))
                points = [Rhino.Geometry.Point3d(0, leftPointY - perpendicularVector.Y*width/2,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(0, leftPointY + perpendicularVector.Y*width/2,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(0, rightPointY + perpendicularVector.Y*width/2,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(0, rightPointY - perpendicularVector.Y*width/2,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(height, leftPointY - perpendicularVector.Y*width/2,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(height, leftPointY + perpendicularVector.Y*width/2,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(height, rightPointY + perpendicularVector.Y*width/2,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(height, rightPointY - perpendicularVector.Y*width/2,rightPointZ - perpendicularVector.Z*width/2)]
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
            else:
                leftPointY = leftMargin + random.random()*(point1.Y - leftMargin)
                leftPointZ = leftMargin + point1.Z + random.random()*(point2.Z - leftMargin - point1.Z)
                rightPointY = leftPointY + random.random()*(point2.Y - leftPointY -3)
                rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ -3)
                width = 2.5 + random.random()*(min(leftPointY, point1.Y - leftPointY)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(0,leftPointY,leftPointZ),
                Rhino.Geometry.Point3d(0,rightPointY,rightPointZ))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(0,-1*(rightPointZ-leftPointZ),(rightPointY-leftPointY))
                points = [Rhino.Geometry.Point3d(point1.X, leftPointY - perpendicularVector.Y*width/2,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X, leftPointY + perpendicularVector.Y*width/2,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X, rightPointY + perpendicularVector.Y*width/2,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X, rightPointY - perpendicularVector.Y*width/2,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X + height, leftPointY - perpendicularVector.Y*width/2,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X + height, leftPointY + perpendicularVector.Y*width/2,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X + height, rightPointY + perpendicularVector.Y*width/2,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point1.X + height, rightPointY - perpendicularVector.Y*width/2,rightPointZ - perpendicularVector.Z*width/2)]   
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox2,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                
    elif (orientationIdx == 3):
        leftPointY = leftMargin + random.random()*(point2.Y-leftMargin)
        leftPointZ = leftMargin + random.random()*(point2.Z-leftMargin)
        if(straight):
            yAxis = bool(random.randint(0,1))
            if(yAxis):
                rightPointY = leftPointY + random.random()*(point2.Y - leftPointY-3)
                rightPointZ = leftPointZ
                width = 2.5 + random.random()*(min(leftPointZ,point2.Z - leftPointZ)-2.5)
                bottomDiagonal = Rhino.Geometry.Point3d(point2.X -height,leftPointY,leftPointZ - width/2)
                upperDiagonal = Rhino.Geometry.Point3d(point2.X,rightPointY ,rightPointZ + width/2)
            else:
                rightPointY = leftPointY
                rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ -3)
                width = 2.5 + random.random()*(min(leftPointY,point2.Y - leftPointY)-2.5)
                bottomDiagonal = Rhino.Geometry.Point3d(point2.X - height,leftPointY - width/2,leftPointZ)
                upperDiagonal = Rhino.Geometry.Point3d(point2.X,rightPointY + width/2, rightPointZ)
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(0,leftPointY,leftPointZ),
            Rhino.Geometry.Point3d(0,rightPointY,rightPointZ))
            brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
            brepTotalVolume = brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
        else:
            rightPointY = leftPointY + random.random()*(point2.Y -leftPointY - 3)
            rightPointZ = leftPointZ + random.random()*(point2.Z -leftPointZ - 3)
            width = 2.5 + random.random()*(min(leftPointY,
            point2.Y -leftPointY,
            leftPointZ,
            point2.Z -rightPointZ)-2.5)
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(0,leftPointY,leftPointZ),
            Rhino.Geometry.Point3d(0,rightPointY,rightPointZ))
            perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(0,-1*(rightPointZ-leftPointZ),(rightPointY-leftPointY))
            points = [Rhino.Geometry.Point3d(point2.X - height, leftPointY - perpendicularVector.Y*width/2,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X - height, leftPointY + perpendicularVector.Y*width/2,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X - height, rightPointY + perpendicularVector.Y*width/2,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X - height, rightPointY - perpendicularVector.Y*width/2,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X, leftPointY - perpendicularVector.Y*width/2,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X, leftPointY + perpendicularVector.Y*width/2,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X, rightPointY + perpendicularVector.Y*width/2,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(point2.X, rightPointY - perpendicularVector.Y*width/2,rightPointZ - perpendicularVector.Z*width/2)]               
            plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
            brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
            brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArray,tolerance)
            brepTotalVolume = Rhino.Geometry.Brep.CreateBooleanUnion([brepUnion[0],brepToSubtract],tolerance)[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
            if(brepTotalVolume == brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume):
                brepTotalVolume = brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
            else:
                brepTotalVolume = 100000
    elif(orientationIdx == 4):
        lowerBlock = True#bool(random.randint(0,1))
        if(straight):
            xAxis = bool(random.randint(0,1))
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point2.X - leftMargin)
                leftPointZ = leftMargin + random.random()*(point1.Z - leftMargin)
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point2.X-leftPointX-3)
                    rightPointZ = leftPointZ
                    width = 2.5 + random.random()*(min(leftPointZ,point1.Z-rightPointZ)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,0,leftPointZ-width/2)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX,height,rightPointZ + width/2)
                else:
                    rightPointX = leftPointX
                    rightPointZ = leftPointZ + random.random()*(point1.Z - leftPointZ - 3)
                    width = 2.5 + random.random()*(min(leftPointX,point2.X-leftPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX - width/2,0,leftPointZ)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,height,rightPointZ)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            else:
                leftPointX = leftMargin + point1.X + random.random()*(point2.X - point1.X -leftMargin)
                leftPointZ = leftMargin + random.random()*(point2.Z - leftMargin)
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point2.X-leftPointX-3)
                    rightPointZ = leftPointZ
                    width = 2.5 + random.random()*(min(leftPointZ, point2.Z - rightPointZ )-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,0,leftPointZ-width/2)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX , height, rightPointZ + width/2)
                else:
                    rightPointX = leftPointX
                    rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ-3)
                    width = 2.5 + random.random()*(min(leftPointX-point1.X,point2.X-rightPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX - width/2,0,leftPointZ)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,height,rightPointZ)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(leftPointX,0,leftPointZ),
            Rhino.Geometry.Point3d(rightPointX,0,rightPointZ))
        else:
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point2.X-leftMargin)
                leftPointZ = leftMargin + random.random()*(point1.Z-leftMargin)
                rightPointX = leftPointX + random.random()*(point2.X - leftPointX - 3)
                rightPointZ = leftPointZ + random.random()*(point1.Z - leftPointZ - 3)
                width = 2.5 + random.random()*(min(leftPointX,point2.X-rightPointX)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(leftPointX,0,leftPointZ),
                Rhino.Geometry.Point3d(rightPointZ,0,rightPointZ))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointZ-leftPointZ),0,(rightPointX-leftPointX))
                points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,0,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,0 ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,0,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,0,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,height,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,height ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,height,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,height,rightPointZ - perpendicularVector.Z*width/2)]
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox1,brepBox2,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            else:
                leftPointX = leftMargin + point1.X + random.random()*(point2.X - point1.X - leftMargin)
                leftPointZ = leftMargin + random.random()*(point2.Z - leftMargin)
                rightPointX = leftPointX + random.random()*(point2.X - leftPointX -3)
                rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ -3)
                width = 2.5 + random.random()*(min(leftPointX - point1.X, point2.X - rightPointX)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(leftPointX,0,leftPointZ),
                Rhino.Geometry.Point3d(rightPointX,0,rightPointZ))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointZ-leftPointZ),0,(rightPointX-leftPointX))
                points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,0,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,0 ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,0,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,0,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,height,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,height ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,height,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,height,rightPointZ - perpendicularVector.Z*width/2)] 
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox2,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
    else:
        lowerBlock = bool(random.randint(0,1))
        if(straight):
            xAxis = bool(random.randint(0,1))
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point2.X - leftMargin)
                leftPointZ = leftMargin + random.random()*(point1.Z - leftMargin)
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point2.X-leftPointX-3)
                    rightPointZ = leftPointZ
                    width = 2.5 + random.random()*(min(leftPointZ,point1.Z-rightPointZ)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,0,leftPointZ-width/2)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX,height,rightPointZ + width/2)
                else:
                    rightPointX = leftPointX
                    rightPointZ = leftPointZ + random.random()*(point1.Z - leftPointZ - 3)
                    width = 2.5 + random.random()*(min(leftPointX,point2.X-leftPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX - width/2,0,leftPointZ)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,height,rightPointZ)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            else:
                leftPointX = leftMargin + point1.X + random.random()*(point2.X - point1.X -leftMargin)
                leftPointZ = leftMargin + random.random()*(point2.Z - leftMargin)
                if(xAxis):
                    rightPointX = leftPointX + random.random()*(point2.X-leftPointX-3)
                    rightPointZ = leftPointZ
                    width = 2.5 + random.random()*(min(leftPointZ, point2.Z - rightPointZ )-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX,0,leftPointZ-width/2)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX , height, rightPointZ + width/2)
                else:
                    rightPointX = leftPointX
                    rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ-3)
                    width = 2.5 + random.random()*(min(leftPointX-point1.X,point2.X-rightPointX)-2.5)
                    bottomDiagonal = Rhino.Geometry.Point3d(leftPointX - width/2,0,leftPointZ)
                    upperDiagonal = Rhino.Geometry.Point3d(rightPointX + width/2,height,rightPointZ)
                brepToSubtract = AddBrepBox(bottomDiagonal,upperDiagonal)
                brepArrayToCheck = [brepBox1,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            sqrDist = SquareDistanceBetweenTwoPoints(
            Rhino.Geometry.Point3d(leftPointX,0,leftPointZ),
            Rhino.Geometry.Point3d(rightPointX,0,rightPointZ))
        else:
            if(lowerBlock):
                leftPointX = leftMargin + random.random()*(point2.X-leftMargin)
                leftPointZ = leftMargin + random.random()*(point1.Z-leftMargin)
                rightPointX = leftPointX + random.random()*(point2.X - leftPointX - 3)
                rightPointZ = leftPointZ + random.random()*(point1.Z - leftPointZ - 3)
                width = 2.5 + random.random()*(min(leftPointX,point2.X-rightPointX)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(leftPointX,0,leftPointZ),
                Rhino.Geometry.Point3d(rightPointZ,0,rightPointZ))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointZ-leftPointZ),0,(rightPointX-leftPointX))
                points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,0,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,0 ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,0,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,0,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,height,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,height ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,height,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,height,rightPointZ - perpendicularVector.Z*width/2)]
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox1,brepBox2,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                if(brepUnion is not None):
                    brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
                else:
                    brepTotalVolume = 100000
            else:
                leftPointX = leftMargin + point1.X + random.random()*(point2.X - point1.X - leftMargin)
                leftPointZ = leftMargin + random.random()*(point2.Z - leftMargin)
                rightPointX = leftPointX + random.random()*(point2.X - leftPointX -3)
                rightPointZ = leftPointZ + random.random()*(point2.Z - leftPointZ -3)
                width = 2.5 + random.random()*(min(leftPointX - point1.X, point2.X - rightPointX)-2.5)
                sqrDist = SquareDistanceBetweenTwoPoints(
                Rhino.Geometry.Point3d(leftPointX,0,leftPointZ),
                Rhino.Geometry.Point3d(rightPointX,0,rightPointZ))
                perpendicularVector = (1/math.sqrt(sqrDist))*Rhino.Geometry.Vector3d(-1*(rightPointZ-leftPointZ),0,(rightPointX-leftPointX))
                points = [Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,0,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,0 ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,0,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,0,rightPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX - perpendicularVector.X*width/2,height,leftPointZ - perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(leftPointX + perpendicularVector.X*width/2,height ,leftPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX + perpendicularVector.X*width/2,height,rightPointZ + perpendicularVector.Z*width/2),
                        Rhino.Geometry.Point3d(rightPointX - perpendicularVector.X*width/2,height,rightPointZ - perpendicularVector.Z*width/2)] 
                plane  = Rhino.Geometry.Plane(points[0],points[3],points[4])
                brepToSubtract = Rhino.Geometry.Box(plane,points).ToBrep()
                brepArrayToCheck = [brepBox2,brepToSubtract]
                brepUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArrayToCheck,tolerance)
                brepTotalVolume = brepUnion[0].GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
    brepSubtractArray = [brepToSubtract]
    check,curves,points = Rhino.Geometry.Intersect.Intersection.BrepBrep(brepToSubtract,brepFillet,tolerance)
    brepBoxUnion = Rhino.Geometry.Brep.CreateBooleanUnion(brepArray,tolerance)
    brepAddArray = [brepBoxUnion[0]]
    if(len(curves)== 0):
        brepSubtractArray.append(brepFillet)
        brepModel = Rhino.Geometry.Brep.CreateBooleanDifference(brepAddArray,brepSubtractArray,tolerance)
        totalVolume = brepBox1.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume + brepBox2.GetBoundingBox(Rhino.Geometry.Vector3d(0,0,1)).Volume
        if ( brepModel is not None and width > 4 and sqrDist > 16 and brepTotalVolume <= totalVolume):
            for brep in brepModel:
                if(scriptcontext.doc.Objects.AddBrep(brep) != System.Guid.Empty ):           
                    scriptcontext.doc.Views.Redraw()
                #rs.Command("_-SaveAs"+" F:\ModuleWorks\RhinoNoHoleIGS\\" + str(modelIdx) + ".igs" + " enter" + " enter",True)
                objs = rs.AllObjects(select = True)
                #rs.Command("_Delete ")
            filled = True
    if(filled):
       return 1
    else:
       return 0
if( __name__ == "__main__" ):
    
    i = 0
    while (i < 20):
        i = i + GenerateSlotsForSteppedModel()
    