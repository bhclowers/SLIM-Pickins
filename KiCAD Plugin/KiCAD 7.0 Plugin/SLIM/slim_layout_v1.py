'''
## SLIM Pickins: An Interactive Circuit Layout Tool for Planar Traveling Wave Ion Guides
* BHC 01.Feb.2022
* [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
* This research product was developed with the support of the [NIGMS](https://www.nigms.nih.gov/) R01-GM140129

This is to be placed in the KiCAD 6 plugins folder. 

BEWARE -- The correct number of SLIM monomers MUST be present on the board in order for this to occur. 

SAVE A COPY OF YOUR WORK BEFORE EXECUTING THIS SCRIPT

For example if you need 70 SLIM monomers total
* 40 SLIM Monomers with the guard on top
* 30 SLIM monomers with the guard on bottom 

(These numbers will be output by the SLIM Pickins layout tool)

Select all of these monomers and starte the layout plugin.  

IF YOU DON'T HAVE THE CORRECT NUMBER OF MONOMERS, THIS WILL FAIL.

Known Issue: This script aims to layout the monomers based upon their sequential numbering. If the numbering is wonky through some sort of
KiCAD annotation setting you can get odd results where the monomers get placed in positions that were not originally intended.  Generally, it
is best to start with the fresh KiCAD project when running this script. 

Finally, this does not wire the tracks for you.  That is something that you must do, though the wiring template can surely help as KiCAD
supports Copy and Paste along with grouping. 



'''


import pcbnew
from pcbnew import VECTOR2I, EDA_ANGLE
import re
import datetime
import wx
import os
import json

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def dumpJSON(outputName, dataDict):
    # Serialization
    with open(outputName, "w") as write_file:
        json.dump(dataDict, write_file)
        print("Done Writing %s to disk"%outputName)
    
def restoreJSON(inputName):
    # Deserialization
    with open(inputName, "r") as read_file:
        dataDict = json.load(read_file)    
        print("Dont reading %s from disk"%inputName)
        return dataDict

def reportDialog(winFrame, message, caption = "Yo!"):
    dlg = wx.MessageDialog(winFrame, message, caption, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def restoreJSON(inputName):
    # Deserialization
    read_file = open(inputName, "r")
    dataDict = json.load(read_file)    
    print("Dont reading %s from disk"%inputName)
    return dataDict



def arrangeFPbyJSON(winFrame, jsonFile):

    pcbDict = restoreJSON(jsonFile)

    pcb = pcbnew.GetBoard()
    fpList = pcb.GetFootprints()
    origin = pcbnew.wxPointMils(0, 0)


    selectedList = []
    for fp in fpList:
        if fp.IsSelected():
            fpName = str(fp.GetReference()) 
            selectedList.append(fpName)    

    trackCoreNames = ['TW1GT', 'TW1GB', 'TW1_0G', 'TWFW', 'TWFC']#need to have this embedded in the json file
    keyList = list(pcbDict.keys())

    unusedFP = []

    TWGTCount = 0
    TWBTCount = 0
    TWNCount = 0
    TWWingCount = 0
    TWFocusCount = 0
    TWGT3PCount = 0
    TWGB3PCount = 0

    countList = [TWGTCount, TWBTCount, TWNCount, TWWingCount, TWFocusCount]#this needs to have the same length as the trackCoreNames

    #the first loop here attempts to recognize that the labels in kicad may not be 
    #what they are from python
    #the assumption, however, is that each list is sequential
    #the fpDict is basically a decoder ring
    fpDict = {}
    for fp in fpList:
        if fp.IsSelected():
            fpName = str(fp.GetReference())
            for j,coreName in enumerate(trackCoreNames):
                if coreName in fpName:
                    countList[j]+=1 #increase count by one
                    pythonName = coreName+str(countList[j])
                    fpDict[fpName] = pythonName
                    print(fpName, pythonName)


    for fp in fpList:
        if fp.IsSelected():

            fpName = str(fp.GetReference())

            if fpName in fpDict:
                compName = fpDict[fpName]


                if compName in pcbDict:
                    curX = float(pcbDict[compName][0][0])
                    curY = float(pcbDict[compName][0][1])*-1#to account for the way matplotlib and kicad count differently
                    curX += pcbnew.ToMils(origin.x)
                    curY += pcbnew.ToMils(origin.y)
                    curAngle = pcbDict[compName][1]
                    newPos = pcbnew.wxPointMils(curX, curY)
                    # newPos = pcbnew.wxPointMils(curX, curY)
                    # fp.SetPosition(newPos) #OLD V1 Code
                    fp.SetPosition(VECTOR2I(newPos))
                    # fp.SetOrientation(curAngle*10)#angle is angle*10 (not sure why probably cuz of C)
                    fp.SetOrientationDegrees(curAngle)
                else:
                    unusedFP.append(str(fp.GetReference()))


    caption = 'Unused Footprints'
    message = str(unusedFP)
    reportDialog(winFrame, message, caption)    

def distributeX(winFrame, xStep = 360):


    pcb = pcbnew.GetBoard()
    fpList = pcb.GetFootprints()
    origin = pcbnew.wxPointMils(0, 0)


    selectedList = []
    m = 0
  
    for fp in fpList:
        if fp.IsSelected():

            fpName = str(fp.GetReference())

            curX = fp.GetPosition()[0]
            curY = fp.GetPosition()[1]

            curX = pcbnew.ToMils(curX)
            curX += xStep*m
            m+=1
            curY = pcbnew.ToMils(curY)            

            newPos = pcbnew.wxPointMils(curX, curY)
            # newPos = pcbnew.wxPointMils(curX, curY)
            fp.SetPosition(VECTOR2I(newPos))


    caption = 'Done with Distribution'
    message = 'Step Size = %d mils'%xStep
    reportDialog(winFrame, message, caption) 


class distributeFootprints(pcbnew.ActionPlugin):
    def defaults( self ):
        self.name = "Distribution Footprints X"
        self.category = "Modify PCB"
        self.description = "Distribute Select Footprints"
 
    def Run( self ):

        winFrame = [x for x in wx.GetTopLevelWindows() if 'pcb editor' in x.GetTitle().lower()][0]

        distributeX(winFrame, xStep = 360)
        
        # caption = 'Yo!'
        # message = "Done Sortted"
        # reportDialog(winFrame, message, caption) 

        return


class moveSLIM(pcbnew.ActionPlugin):
    def defaults( self ):
        self.name = "Layout SLIM"
        self.category = "Modify PCB"
        self.description = "Move components to conform to a SLIM layout"
 
    def Run( self ):

        winFrame = [x for x in wx.GetTopLevelWindows() if 'pcb editor' in x.GetTitle().lower()][0]

        # Create open file dialog
        openFileDialog = wx.FileDialog(winFrame, "Open", "", "", 
              "SLIM Board Layouts (*.JSON)|*.json", 
               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        openFileDialog.ShowModal()
        selectedFile = openFileDialog.GetPath()
        
        fileName = selectedFile
        openFileDialog.Destroy()

        if not os.path.isfile(fileName):
            return

        message = "%s Selected"%str(fileName)
        # reportDialog(winFrame, message)

        arrangeFPbyJSON(winFrame, fileName)
        
        caption = 'Process Complete!'
        message = "The Footprints are now sorted..."
        reportDialog(winFrame, message, caption) 

        return


class moveSLIMDlg(pcbnew.ActionPlugin):
    def defaults( self ):
        self.name = "Layout Dialog"
        self.category = "Modify PCB"
        self.description = "Move components to conform to a SLIM layout"
 
    def Run( self ):

        winFrame = [x for x in wx.GetTopLevelWindows() if 'pcb editor' in x.GetTitle().lower()][0]
        
        caption = 'Hmmm.'
        message = "Try Next Dialog"
        reportDialog(winFrame, message, caption) 

        ex = Example(parent = winFrame)
        ex.Show()

        return



class ChangeDepthDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(ChangeDepthDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Change Color Depth")


    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label='Colors')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        sbs.Add(wx.RadioButton(pnl, label='256 Colors',
            style=wx.RB_GROUP))
        sbs.Add(wx.RadioButton(pnl, label='16 Colors'))
        sbs.Add(wx.RadioButton(pnl, label='2 Colors'))

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.RadioButton(pnl, label='Custom'))
        hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)
        sbs.Add(hbox1)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)


    def OnClose(self, e):

        self.Destroy()


class Example(wx.Frame):

    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.InitUI()


    def InitUI(self):

        tb = self.CreateToolBar()
        tb.AddTool(toolId=wx.ID_ANY, label='', bitmap=wx.Bitmap('color.png'))

        tb.Realize()

        tb.Bind(wx.EVT_TOOL, self.OnChangeDepth)

        self.SetSize((350, 250))
        self.SetTitle('Custom dialog')
        self.Centre()

    def OnChangeDepth(self, e):

        cdDialog = ChangeDepthDialog(None,
            title='Change Color Depth')
        cdDialog.ShowModal()
        cdDialog.Destroy()



class moveSLIMORIG(pcbnew.ActionPlugin):
    def defaults( self ):
        self.name = "Layout SLIM"
        self.category = "Modify PCB"
        self.description = "Move components to conform to a SLIM layout"
 
    def Run( self ):
        pcb = pcbnew.GetBoard()
        fpList = pcb.GetFootprints()
        origin = pcbnew.wxPointMils(3000, 3000)
        offset = 360

        fpNames = []
        for fp in fpList:
            fpNames.append(str(fp.GetReference()))


        fpNames = natural_sort(fpNames)
        
        sortedFP = [x for _,x in sorted(zip(fpNames,fpList))]
        

        for i,fp in enumerate(sortedFP):
            # print(fp.GetReference())
            newX = pcbnew.ToMils(origin.x)
            newY = pcbnew.ToMils(origin.y)
            newPos = pcbnew.wxPointMils(newX+offset*i, newY)
            fp.SetPosition(newPos)
            fp.SetOrientation(0)#angle is angle*10 (not sure why probably cuz of C)


        _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if 'pcb editor' in x.GetTitle().lower()][0]
        caption = 'Sorted'
        message = "Boom!"
        dlg = wx.MessageDialog(_pcbnew_frame, message, caption, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        # Create open file dialog
        openFileDialog = wx.FileDialog(_pcbnew_frame, "Open", "", "", 
              "SLIM Board Layouts (*.JSON)|*.json", 
               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        openFileDialog.ShowModal()
        print(openFileDialog.GetPath())
        openFileDialog.Destroy()

        return
