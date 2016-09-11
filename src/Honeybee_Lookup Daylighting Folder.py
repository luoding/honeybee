#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Search Simulation Folder
-
Provided by Honeybee 0.0.60
    
    Args:
        _studyFolder: Path to base study folder. If _studyType is empty then it should be full path to study folder
        _studyType_: Optional input for Honeybee study type
                    1 > imageBasedSimulation
                    2 > gridBasedSimulation
                    3 > DF
                    4 > VSC
                    5 > annualSimulation
        refresh_: Refresh
    Returns:
        analysisType: Type of the analysis (e.g. illuminance, luminance,...)
        resultsUnit: Unit of the results (e.g. lux, candela, wh/m2)
        resFiles: List of result files from grid based analysis
        illFiles: List of ill files from annual analysis
        ptsFiles: List of point files
        hdrFiles: List of hdr files
        gifFiles: List of gif files
        annualProfiles: A .csv file generated by Daysim that can be used as an schedule for annual daylight simulation
        
"""

ghenv.Component.Name = "Honeybee_Lookup Daylighting Folder"
ghenv.Component.NickName = 'LookupFolder_Daylighting'
ghenv.Component.Message = 'VER 0.0.60\nAUG_10_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import scriptcontext as sc
import os
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from pprint import pprint

def main(studyFolder):
    
    msg = str.Empty
    
    if not (sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release')):
        msg = "You should first let Ladybug and Honeybee fly..."
        return msg, None

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_serializeObjects = sc.sticky["honeybee_SerializeObjects"]
    hb_readAnnualResultsAux = sc.sticky["honeybee_ReadAnnualResultsAux"]()
    analysisTypesDict = sc.sticky["honeybee_DLAnalaysisTypes"]
    if studyFolder==None:
        msg = " "
        return msg, None
        
    if not os.path.isdir(studyFolder):
        msg = "Can't find " + studyFolder
        return msg, None
        
    resFiles = []
    illFilesTemp = []
    ptsFiles = []
    hdrFiles = []
    gifFiles = []
    tifFiles = []
    bmpFiles = []
    jpgFiles = []
    epwFile = str.Empty
    analysisType = str.Empty
    analysisMesh = []
    iesFiles = []
    radianceFiles = []
    materialFiles = []
    dgpFiles = []
    skyFiles = []
    octFiles = []
    annualProfiles = []
    htmReport = []
    
    if studyFolder!=None:
        fileNames = os.listdir(studyFolder)
        fileNames.sort()
        for fileName in fileNames:
            if fileName.lower().endswith(".res"):
                resFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".ill") and (fileName.find("space")== -1 or fileName.split("_")[-2]!="space"):
                illFilesTemp.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".pts") and (fileName.find("space")== -1 or fileName.split("_")[-2]!="space"):
                ptsFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".epw"):
                epwFile = os.path.join(studyFolder, fileName)
            elif fileName.lower().endswith(".hdr") or fileName.lower().endswith(".pic"):
                hdrFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".gif"):
                gifFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".oct"):
                octFiles.append(os.path.join(studyFolder, fileName))            
            elif fileName.lower().endswith(".tif") or fileName.lower().endswith(".tiff"):
                tifFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".bmp"):
                bmpFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".jpg") or fileName.lower().endswith(".jpeg"):
                jpgFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".rad") and not fileName.lower().startswith("daysim_"):
                if fileName.lower().startswith("material_"):
                    materialFiles.append(os.path.join(studyFolder, fileName))
                else:
                    radianceFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".sky"):
                skyFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".ies"):
                iesFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".typ"):
                with open(os.path.join(studyFolder, fileName), "r") as typf:
                    analysisType = typf.readline().strip()
                try: analysisType = analysisTypesDict[float(analysisType)]
                except: pass
            elif fileName.lower().endswith(".dgp"):
                dgpFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".msh"):
                try:
                    meshFilePath = os.path.join(studyFolder, fileName)
                    serializer = hb_serializeObjects(meshFilePath)
                    serializer.readFromFile()
                    analysisMesh = lb_preparation.flattenList(serializer.data)
                except:
                    pass
            elif fileName.lower().endswith("intgain.csv"):
                annualProfiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith("electriclighting.htm"):
                htmReport.append(os.path.join(studyFolder, fileName))

    # check if there are multiple ill files in the folder for different shading groups
    illFiles = hb_readAnnualResultsAux.sortIllFiles(illFilesTemp)
    
    
    #except: pass
    try: resFiles = sorted(resFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    try: ptsFiles = sorted(ptsFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    
    imgFiles = gifFiles + tifFiles + bmpFiles + jpgFiles
    
    return msg, [illFiles, resFiles, ptsFiles, hdrFiles, imgFiles, iesFiles, \
           epwFile, analysisType, analysisMesh, radianceFiles, materialFiles, \
           skyFiles, dgpFiles, octFiles, annualProfiles, htmReport]
    

ghenv.Component.Params.Output[2].NickName = "resultFiles"
ghenv.Component.Params.Output[2].Name = "resultFiles"
resultFiles = []

studyTypes = {
        1: "imageBasedSimulation",
        2: "gridBasedSimulation",
        3: "DF",
        4: "VSC",
        5: "annualSimulation"
        }


if _studyFolder!=None:
    
    # check if the type is provided
    if _studyType_!=None:
        studyFolder = os.path.join(_studyFolder, studyTypes[_studyType_])
    else:
        studyFolder = _studyFolder
        
    res = main(studyFolder)
    
    if res != -1:
        msg, results = res
        
        if msg!=str.Empty:
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            illFiles, resFiles, ptsFiles, hdrFiles, imageFiles, iesFiles, epwFile, analysisType, \
            analysisMesh, radianceFiles, materialFiles, skyFiles, dgpFiles, octFiles, \
            annualProfiles, htmReport = results
            
            # seperate outputs for type and units
            # https://github.com/mostaphaRoudsari/ladybug/issues/184
            try:
                resultsUnit = analysisType[1]
                analysisType = analysisType[0]
            except:
                pass
                
            if resFiles != []:
                resultFiles = resFiles
            else:
                resultFiles = illFiles
                filesOutputName = "illFiles"
                ghenv.Component.Params.Output[2].NickName = filesOutputName
                ghenv.Component.Params.Output[2].Name = filesOutputName
                exec(filesOutputName + "= resultFiles")
