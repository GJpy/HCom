import os
import time
import subprocess
import random
import threading

HISTORY_FOLDER = os.path.dirname(__file__) + "\\HCom_History\\"
ICONPATH = os.path.dirname(__file__) + "\\HCom_Icons\\"
RECEIVED_FILES_PATH = os.path.dirname(__file__) + "\\HCom_Received_Files\\"

def readIni():
    
    iniValues = {}
    
    ini = os.path.dirname(__file__) + "\\HCom.ini"
    with open(ini, 'r') as f:
        for i in f.readlines():
            if i.startswith("#"):
                continue
            elif i == "\n":
                continue
            else:
                data = i.split("=")
                if len(data) <= 1:
                    continue
                
                val = data[1].replace("\n", "").replace("\r", "")
                if val.isdigit() and "." in val:
                    val = float(val)
                elif val.isdigit() and not "." in val:
                    val = int(val)
                elif val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                else:
                    val = str(val)
                
                iniValues[str(data[0]).replace("\r", "")] = val
                
    return iniValues

def writeIni(settings):
    
    ini = os.path.dirname(__file__) + "\\HCom.ini"
    with open(ini, 'w') as f:
        f.write('')
        
    data = ["#HCom info file -MAYA CLIENT-\r\n"]
    for k in settings.keys():
        data.append(k + "=" + str(settings[k]))
        
    with open(ini, 'a') as f:
        for d in data: f.write(d + "\r\n")


def writeHistory(sender, timeStamp, data):
    
    historyFile = HISTORY_FOLDER + sender.lower() + "_history.txt"
    with open(historyFile, 'a') as f:
        f.write(timeStamp + "\n")
        f.write("  " + str(data) + "\n")      

def coloredString(string, hexColor=None, rgb=None, italic=False, bold=False):
        
    in_italic_tag = ""
    out_italic_tag = ""
    if italic:
        in_italic_tag = "<i>"
        out_italic_tag = "</i>"
        
    in_bold_tag = ""
    out_bold_tag = ""
    if bold:
        in_bold_tag = "<b>"
        out_bold_tag = "</b>"
    
    if not hexColor and not rgb:
        return "<FONT>{0}{1}{2}{3}{4}</FONT>".format(in_italic_tag, in_bold_tag, string, out_bold_tag, out_italic_tag)
    
    if hexColor:
        if hexColor.startswith("#"):
            hexColor = hexColor.replace("#", "")
        return "<FONT COLOR=#{5}>{0}{1}{2}{3}{4}</FONT>".format(in_italic_tag, in_bold_tag, string, out_bold_tag, out_italic_tag, hexColor)
    else:
        return "<FONT COLOR=rgb({5},{6},{7})>{0}{1}{2}{3}{4}</FONT>".format(in_italic_tag, in_bold_tag, string, out_bold_tag, out_italic_tag, rgb[0], rgb[1], rgb[2])
    
def incrementFile(filePath):
    
    if not os.path.exists(filePath):
        return filePath
    
    baseName = os.path.basename(filePath)
    name = baseName.split(".")[0]
    fileType = baseName.split(".")[1]
    dirName = os.path.dirname(filePath)
    
    fileInc = dirName + os.sep + name + "_1." + fileType
    i = 2
    while os.path.exists(fileInc):
        fileInc = dirName + os.sep + name + "_" + str(i) + "." + fileType
    
    return fileInc

def createOtl(data, sender="", settings=None):
    
    import maya.mel as mel
    
    nodeType = data["OTL_TYPE"]
    subOtlLibs = data["OTL_ALL_LIBS"]
    
    print("NODE TYPE: " + str(nodeType))
    
    libPath = None
    otlToAdd = None
    
    # Check otl libs
    if subOtlLibs:
        
        for e in subOtlLibs:
            libName = e[0]
            libData = e[1]
            
            otlLibToInstall = RECEIVED_FILES_PATH.replace("\\","/") + libName
            
            with open(otlLibToInstall, 'wb') as f:
                f.write(libData)
                
            libs = mel.eval('houdiniAsset -listAssets "' + otlLibToInstall + '"')
            if libs:
                for lib in libs:
                    if nodeType in str(lib):
                        libPath = otlLibToInstall
                        otlToAdd = lib
    
    if libPath and otlToAdd:
        melcmd = 'houdiniAsset -loadAsset "' + libPath + '" "' + otlToAdd + '"'
        
        return {"CMD_TYPE":"mel", "CMD":"import_otl", "DATA":melcmd}
    else:
        print("ERROR: Incoming object is not a valid digital asset")
        return None

        
def setOtlSettings(data, sender="", settings=None):
    return False

def createMesh(data, sender="", settings=None):
    
    import maya.cmds as cmds
    
    meshType = data["MESH_TYPE"]    
    if meshType != ".obj":
        print("ERROR: Mesh type not supported (" + meshType + ")")
        return False
    
    meshName = data["MESH_NAME"]
    meshData = data["MESH_DATA"]
    
    obj = RECEIVED_FILES_PATH + meshName + meshType
    obj = incrementFile(obj)
    with open(obj, 'wb') as f:
        f.write(meshData)
    
    return {"CMD_TYPE":"python","CMD":"import_obj", "DATA":obj}
    
    
def createPic(data, sender="", settings=None):
    
    imageName = data["IMAGE_NAME"]   
    imageData = data["BINARY_DATA"]
    
    imageNameAndFile = imageName.split(".")
            
    outFile = RECEIVED_FILES_PATH + imageNameAndFile[0] + "." + imageNameAndFile[1]
    outFile = incrementFile(outFile)
    
    with open(outFile, 'wb') as f:
        f.write(imageData)
    
    t = threading.Thread(target = openPicFile, args=(outFile,))
    t.start()
            
def openPicFile(picFile):
    
    try:
        subprocess.Popen(["mplay.exe", picFile])
    except Exception as e:
        print "MPLAY ERROR: " + str(e)
        try:
            subprocess.Popen(["explorer", picFile])
        except Exception as e:
            print "EXPLORER ERROR: " + str(e)
    
    
def rdnname():
    names = ["Motoko", "Bato", "Kusanagi", "Frodon", "Sheldon", "Pipo", "Sam", "Gandalf", "Fitz", "Henry"]
    names += ["Leonard", "Batman", "Bobleponge", "rincewind", "carrot", "HelloWorld", "Python", "Houdini"]
    return names[random.randint(0, len(names)-1)]

class CLIENT_TYPE():
    
    NONE = "NONE"
    HOUDINI = "Houdini"
    MAYA_NO_HENGINE = "Maya_no_hengine"
    MAYA_HENGINE = "Maya_hengine"
    NUKE = "nuke"
    