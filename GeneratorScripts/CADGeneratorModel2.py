import Rhino 
import scriptcontext
import rhinoscriptsyntax as rs
import System.Guid 
import random
import json
import sys
import os
import math


def AddBrepBox(point1, point2):
    box = Rhino.Geometry.BoundingBox(point1, point2)
    brep = box.ToBrep()
    rc = Rhino.Commands.Result.Failure
    return brep
    
    
if( __name__ == "__main__" ):
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
    brepModel = Rhino.Geometry.Brep.CreateBooleanUnion(brepArray,tolerance)
    for brep in brepModel:
        if(scriptcontext.doc.Objects.AddBrep(brep) != System.Guid.Empty ):           
            scriptcontext.doc.Views.Redraw()
        #rs.Command("_-SaveAs"+" F:\ModuleWorks\RhinoNoHoleIGS\\" + str(modelIdx) + ".igs" + " enter" + " enter",True)
        objs = rs.AllObjects(select = True)
        #rs.Command("_Delete ")