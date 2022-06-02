## THIS VERSION REQUERS MPR SENSOR BOARD

import wx
#import warnings
#warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)   
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
#import csv
import mFCB_controlv9 as MFCB
import Mailsender as mail
from FluidicCalculators import *
import pandas as pd


class TopPanelLeft(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent)
       
     #______LEFT 
     #-----------------------build plot region_______________________________________________________________  
        self.fig= plt.figure(figsize=(9.5, 5.5)) #build plot region
        self.canvas = FigureCanvas(self,1, self.fig)
        self.ax=   plt.subplot2grid((3,3), (1,0), colspan=2,rowspan=3)
        self.Q = plt.subplot2grid((3,2), (0,0), colspan=2)
        self.P = plt.subplot2grid((3,2), (1,0), colspan=2,rowspan=3)
        
        column1=690
        column2=760
        column3=column2+50
        column4=column3+50
        column5=column4+50
        
        #-----------------------build display parameters____________________________
        experimentDurationlabel=wx.StaticText(self, -1, "Duration:" , pos = (column1, 0)) 
        self.expduration=wx.StaticText(self, -1, "-" , pos = (column1+80, 0)) 
        label_Injected_volume = wx.StaticText(self, -1, "Total Volume", pos = (column1,20))
        self.label_Injected_volume = wx.StaticText(self, -1, "0", pos = (column1+80,20))
        label_unitml = wx.StaticText(self, -1, "[ml]", pos = (column3,20))
        
        label_P= wx.StaticText(self, -1, "P", pos = (column1,70))
        label_commandinlet = wx.StaticText(self, -1, "EZ1", pos = (column2,50))
        self.Pinlet = wx.StaticText(self, -1, "-" , pos = (column2, 70))
        
        label_commandoutlet = wx.StaticText(self, -1, "EZ2", pos = (column3,50))
        self.Poutlet = wx.StaticText(self, -1, "-" , pos = (column3, 70))

        Live_label = wx.StaticText(self, -1, "Flowrate:", pos = (column1,90))
        self.Flowrate_DIS = wx.StaticText(self, -1, "-" , pos = (column2, 90))
        Flowrate_label = wx.StaticText(self, -1, "[μL/min]", pos = (column4-20,90))
        
        R1_label = wx.StaticText(self, -1, "R1", pos = (column2,120))
        R2_label = wx.StaticText(self, -1, "R2", pos = (column3,120))
        Tot_label = wx.StaticText(self, -1, "total", pos = (column4,120))
        
        Rdp_label = wx.StaticText(self, -1, "dP", pos = (column1,140))
        self.dpR1 = wx.StaticText(self, -1, "-" , pos = (column2, 140))
        self.dpR2 = wx.StaticText(self, -1, "-" , pos = (column3, 140))
        self.Vtot = wx.StaticText(self, -1, "-" , pos = (column4, 140))
        
        RdV_label = wx.StaticText(self, -1, "R Volume", pos = (column1,160))
        self.VR1 = wx.StaticText(self, -1, "-" , pos = (column2, 160))
        self.VR2 = wx.StaticText(self, -1, "-" , pos = (column3, 160))
        self.VRtot = wx.StaticText(self, -1, "-" , pos = (column4, 160))
        
        V_startlabel= wx.StaticText(self, -1, "Start Volume", pos = (column1,180))
        self.Vstart = wx.StaticText(self, -1, "-" , pos = (column2, 180))
        self.Vperc = wx.StaticText(self, -1, "-" , pos = (column3, 180))
         
        Inlet_label= wx.StaticText(self, -1, "Inlet", pos = (column2,200))
        Outlet_label= wx.StaticText(self, -1, "Outlet", pos = (column3,200))
        
        dp1_label=wx.StaticText(self, -1, "dP", pos = (column1,220))
        self.dpinlet= wx.StaticText(self, -1, "dp in" , pos = (column2, 220))
        self.dpoutlet= wx.StaticText(self, -1, "dp out" , pos = (column3, 220))
        
        RH1_label=wx.StaticText(self, -1, "RH", pos = (column1,240))
        self.Rhi= wx.StaticText(self, -1, "rh in" , pos = (column2, 240))
        self.Rho= wx.StaticText(self, -1, "rh out" , pos = (column3, 240))
        
        Sample_label = wx.StaticText(self, -1, "MFCB", pos = (column1,270))
        Feeder_label = wx.StaticText(self, -1, "Feeder" , pos = (column2, 270)) 
        Feeder_label = wx.StaticText(self, -1, "Waste" , pos = (column3, 270))
        dP_label= wx.StaticText(self, -1, "dP", pos = (column4,270))
        
        Target_label = wx.StaticText(self, -1, "Target:" , pos = (column1, 290))
        self.command_inlet = wx.StaticText(self, -1, "-" , pos = (column2, 290))
        self.command_outlet = wx.StaticText(self, -1, "-" , pos = (column3, 290))
        self.TdP= wx.StaticText(self, -1, "-" , pos = (column4, 290))
        
        Measured_label = wx.StaticText(self, -1, "Measured" , pos = (column1, 310))
        self.dP= wx.StaticText(self, -1, "-" , pos = (column4, 310))
        self.PFeeder = wx.StaticText(self, -1, "-" , pos = (column2, 310))
        self.PWaste = wx.StaticText(self, -1, "-" , pos = (column3, 310))

        Rh_label= wx.StaticText(self, -1, "Board Rh", pos = (column1,330))
        self.Rhboard= wx.StaticText(self, -1, "rh board" , pos = (column2, 330))
        
        Shear_label= wx.StaticText(self, -1, "Shear Stress", pos = (column1,370))
        Pressure_label=wx.StaticText(self, -1, "P sample", pos = (column1,390))
        Measured_label= wx.StaticText(self, -1, "Measured" , pos = (column2, 350))
        Target_label = wx.StaticText(self, -1, "Target:" , pos = (column3+5, 350))
        self.shearTarget=wx.StaticText(self, -1, "-" , pos = (column3+5, 370))
        self.shearMeasured=wx.StaticText(self, -1, "-" , pos = (column2, 370))
        self.IPTarget=wx.StaticText(self, -1, "-" , pos = (column3+5, 390))
        self.IPMeasured=wx.StaticText(self, -1, "-" , pos = (column2, 390))
        

        Directionlabel= wx.StaticText(self, -1, "Direction", pos = (750,410))
        self.direction_DIS = wx.StaticText(self, -1, "-" , pos = (830, 410))
        
    def UpdateLabel(self,kernel=3,Hz=12,Time=np.nan,inV=np.nan,Dir=1,
                    ComInlet=np.nan,ComOutlet=np.nan,
                    EZ1=np.nan,EZ2=np.nan,Q=np.nan,
                    PF=np.nan,PW=np.nan,dP=np.nan,
                    dpR1=np.nan,dpR2=np.nan,
                    V1=np.nan,V2=np.nan,
                    Vstart=np.nan,
                    RHI=np.nan,RHsamp=np.nan,RHO=np.nan,
                    dpin=np.nan,dpout=np.nan,TEQ=np.nan
                    ):
        print("Update left labels")
        try:
            self.expduration.SetLabel(str(Time).split('.', 2)[0])
        except:
            self.expduration.SetLabel("Standby")
        
        self.label_Injected_volume.SetLabel(str(round(inV,3)))
        self.Flowrate_DIS.SetLabel(str(round(MFCB.sensorsData.dampData(self,Q,kernel=kernel,Hz=Hz),1)))
        
        
        self.command_inlet.SetLabel(str(ComInlet))
        self.command_outlet.SetLabel(str(ComOutlet))
        self.TdP.SetLabel(str(round(ComInlet-ComOutlet,1)))
  
        if Dir==1:
            self.Pinlet.SetLabel(str(round(MFCB.sensorsData.dampData(self,EZ1,kernel=kernel,Hz=Hz),1)))
            self.Poutlet.SetLabel(str(round(MFCB.sensorsData.dampData(self,EZ2,kernel=kernel,Hz=Hz),1)))
        elif Dir==2:
            self.Pinlet.SetLabel(str(round(MFCB.sensorsData.dampData(self,EZ2,kernel=kernel,Hz=Hz),1)))
            self.Poutlet.SetLabel(str(round(MFCB.sensorsData.dampData(self,EZ1,kernel=kernel,Hz=Hz),1)))
        
        Temp_PF=round(MFCB.sensorsData.dampData(self,PF,kernel=kernel,Hz=Hz),1)
        Temp_PW=round(MFCB.sensorsData.dampData(self,PW,kernel=kernel,Hz=Hz),1)
        Temp_dp=Temp_PF-Temp_PW
        
        self.PFeeder.SetLabel(str(Temp_PF))
        self.PWaste.SetLabel(str(Temp_PW))
        
        dpR1=MFCB.sensorsData.dampData(self,dpR1,kernel=kernel,Hz=Hz)
        dpR2=MFCB.sensorsData.dampData(self,dpR2,kernel=kernel,Hz=Hz)
        Vtot=dpR1+dpR2
        Vperc=Vtot/Vstart
        
        self.dpR1 .SetLabel(str(round(dpR1,1)))
        self.dpR2 .SetLabel(str(round(dpR2,1)))
        self.VR1 .SetLabel(str(round(V1,3)))
        self.VR2.SetLabel(str(round(V2,3)))
        
        self.Vtot.SetLabel(str(round(Vtot,1)))
        self.Vperc.SetLabel(str(round(Vperc*100,1)) +" %")
        self.Vstart.SetLabel(str(round(Vstart,2)))
        
        
        self.direction_DIS.SetLabel(str(Dir))

        self.dpinlet.SetLabel(str(round(dpin,1)))
        self.dP.SetLabel(str(round(Temp_dp,1)))
        self.dpoutlet.SetLabel(str(round(dpout,1)))
        self.Rhi.SetLabel(str(round(RHI,2)))
        self.Rhboard.SetLabel(str(round(RHsamp,2)))
        self.Rho.SetLabel(str(round(RHO,2)))
        
        mShear,mP=Calculator.ShearAndPres(self,Temp_PF,Temp_PW,TEQ)
        self.shearMeasured.SetLabel(str(round(mShear,2)))
        
        tShear,tP=Calculator.ShearAndPres(self,ComInlet,ComOutlet,TEQ)
        self.shearTarget.SetLabel(str(round(tShear,2)))
        
        self.IPTarget.SetLabel(str(round(tP,2)))
        self.IPMeasured.SetLabel(str(round(mP,2)))
        
    def draw(self,t,flowrate,ez1,ez2):
        self.Q.clear()
        t=np.arange(0,500,1)/7
        self.Q.plot(t,flowrate)
        self.P.clear()
        self.P.plot(t,ez1)
        self.P.plot(t,ez2)#_date 
        self.canvas.draw()


class TopPanelRight(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent)
        
        label = wx.StaticText(self, -1, "Raw sensor data: ", pos = (0,10))
        S1_label = wx.StaticText(self, -1, "S1", pos = (30,30))
        self.S1 = wx.StaticText(self, -1, "-" , pos = (30,50))
        
        S2_label = wx.StaticText(self, -1, "S2", pos = (60, 30))
        self.S2 = wx.StaticText(self, -1, "-" , pos = (60, 50))
        
        S3_label = wx.StaticText(self, -1, "S3", pos = (90,30))
        self.S3 = wx.StaticText(self, -1, "-" , pos = (90, 50))
        
        S4_label = wx.StaticText(self, -1, "S4", pos = (120,30))
        self.S4 = wx.StaticText(self, -1, "-" , pos = (120, 50))
        
        S5_label = wx.StaticText(self, -1, "S5", pos = (30,70))
        self.S5 = wx.StaticText(self, -1, "-" , pos = (30, 90))
        
        S6_label = wx.StaticText(self, -1, "S6", pos = (60,70))
        self.S6 = wx.StaticText(self, -1, "-" , pos = (60, 90))
        
        S7_label = wx.StaticText(self, -1, "S7", pos = (90,70))
        self.S7 = wx.StaticText(self, -1, "-" , pos = (90, 90))
        
        S8_label = wx.StaticText(self, -1, "S8", pos = (120,70))
        self.S8 = wx.StaticText(self, -1, "-" , pos = (120, 90))
        
        EZ1_label = wx.StaticText(self, -1, "EZ1", pos = (180,30))
        self.EZ1 = wx.StaticText(self, -1, "-" , pos = (180, 50))
        
        EZ2_label = wx.StaticText(self, -1, "EZ2", pos = (230,30))
        self.EZ2 = wx.StaticText(self, -1, "-" , pos = (230, 50))
        
        Q_label = wx.StaticText(self, -1, "Q1", pos = (180,70))
        self.Q = wx.StaticText(self, -1, "-" , pos = (180, 90))
        
        Q2_label = wx.StaticText(self, -1, "Q2", pos = (230,70))
        self.Q2 = wx.StaticText(self, -1, "-" , pos = (230, 90))

    def UpdateLabel(self,S1="nan",S2="nan",S3="nan",S4="nan",S5="nan",S6="nan",
                    S7="nan",S8="nan",EZ1="nan",EZ2="nan",Q="nan",Q2="nan"):
        print("Update right top labels")
        self.S1.SetLabel(str(S1))
        self.S2.SetLabel(str(S2))
        self.S3.SetLabel(str(S3))
        self.S4.SetLabel(str(S4))
        self.S5.SetLabel(str(S5))
        self.S6.SetLabel(str(S6))
        self.S7.SetLabel(str(S7))
        self.S8.SetLabel(str(S8))
        self.EZ1.SetLabel(str(EZ1))
        self.EZ2.SetLabel(str(EZ2))
        self.Q.SetLabel(str(Q))
        self.Q2.SetLabel(str(Q2))

class BottomPanel(wx.Panel):
    def __init__(self, parent, Ltop, Rtop):
        
        wx.Panel.__init__(self, parent = parent)
       # self.serial_connection = False
        self.settings=pd.read_excel("Settings\Pref_settings.xlsx", engine='openpyxl',index_col=0)
        self.Command = MFCB.Commandos()
        self.reservoir= MFCB.reservoirs()
        self.Fluigent= MFCB.fluigent()
        self.Pressure= MFCB.PressureSensor()
        self.Data=MFCB.sensorsData()
        self.Mail=mail.Mail()
        self.Calc=Calculator()
        self.graphL = Ltop
        self.graphR = Rtop
        self.old_timestamp=datetime.datetime.now()
        
        
        #start up settings
        self.mode=self.settings.loc['mode'][0]#"recirculation"
        self.FixedParameter=self.settings.loc['fixedparameter'][0]
        self.Freq=int(self.settings.loc['frequency'][0])
        self.cyclecount=0
        self.experimentDuration=0
        self.run = False
        self.switchfluid=self.settings.loc['switchmedium'][0]
        
        self.frameSize=int(self.settings.loc['framesize'][0])
        self.Data.setPID(kP=float(self.settings.loc['P'][0]),
                         kI=float(self.settings.loc['I'][0]),
                         kD=(self.settings.loc['D'][0]))
        self.reservoir.limitR1=float(self.settings.loc['lwl1'][0])
        self.reservoir.limitR2=float(self.settings.loc['lwl2'][0])
        self.TEQ=float(self.settings.loc['TEQ'][0])

        self.startVolume=99
        self.dryFlag=False
        self.dry_Time=None
        
        self.togglebuttonStart = wx.ToggleButton(self, id = -1, label = "Start", pos = (10,10),size = (100,50))
        self.togglebuttonStart.Bind(wx.EVT_TOGGLEBUTTON, self.OnStartClick)
        
        self.togglebuttonPause = wx.ToggleButton(self, id = -1, label = "Pause", pos = (140,10),size = (85,25))
        self.togglebuttonPause.Bind(wx.EVT_TOGGLEBUTTON, self.Pause)
        
        self.buttonSetPressure = wx.Button(self, id = -1, label = "Set Pressure", pos = (30,140),size = (115,-1))
        self.buttonSetPressure.Bind(wx.EVT_BUTTON, self.SetPressure)
        
        labelPin = wx.StaticText(self, -1, "P inlet \n [mbar]", pos = (40,70))
        labelPout = wx.StaticText(self, -1, "P outlet \n [mbar]", pos = (95,70))
        
        self.textboxPressure_inlet = wx.TextCtrl(self, -1, str(self.settings.loc['pressurein'][0]), pos = (45,110), size = (40,-1))
        self.textboxPressure_outlet = wx.TextCtrl(self, -1, str(self.settings.loc['pressureout'][0]), pos = (95 ,110), size = (40,-1))
         
        self.buttonCalculate = wx.Button(self, -1, "Calculate Pressure", pos =(170,140),size = (115,-1))
        self.buttonCalculate.Bind(wx.EVT_BUTTON, self.Calculate)
        #self.label_WARNING= wx.StaticText(self, -1, "WARNING:\nNOT FUNCTIONAL\nWITHOUT BOARD SENSORS", pos = (190,170))
        
        self.buttonPID = wx.Button(self, -1, "Set PID parameters", pos =(30,170),size = (115,-1))
        self.buttonPID.Bind(wx.EVT_BUTTON, self.setPIDpar)
        
        kP_label= wx.StaticText(self, -1, "Proportional", pos = (20,200))
        kD_label= wx.StaticText(self, -1, "Derivative", pos = (20,220))
        kI_label=wx.StaticText(self, -1, "Intergral", pos = (20,240))
        
        self.textboxkP=wx.TextCtrl(self, -1, str(self.Data.kProp), pos = (110,200), size = (40,-1))
        self.textboxkD=wx.TextCtrl(self, -1, str(self.Data.kInt), pos = (110,220), size = (40,-1))
        self.textboxkI=wx.TextCtrl(self, -1,str(self.Data.kDeriv), pos = (110,240), size = (40,-1))
        self.Data.setPID(kP=float(self.textboxkP.GetValue()),kI=float(self.textboxkI.GetValue()),
                             kD=float(self.textboxkD.GetValue()))
        
        self.RefChoice1=wx.ComboBox(self, value="", pos=(160,200), choices=["S1","S2","S3","S4","S5","S6","S7","S8",])
        self.RefChoice1.SetSelection(0)
        self.RefChoice2=wx.ComboBox(self, value="", pos=(160,230), choices=["S1","S2","S3","S4","S5","S6","S7","S8",])
        self.RefChoice2.SetSelection(1)
        
        
        
        self.label_shearstress= wx.StaticText(self, -1, "dP\n [Pa]", pos = (180,70))
        self.textboxShearStress = wx.TextCtrl(self, -1, "0", pos = (185,110), size = (40,-1))
        
        self.label_Pressure= wx.StaticText(self, -1, " Pressure\n [mbar]", pos = (235,70))
        self.textboxPressure = wx.TextCtrl(self, -1, "0", pos = (235,110), size = (40,-1))

        self.label_flowrate= wx.StaticText(self, -1, "Flow rate\n [µl/min]", pos = (355,60))
        self.buttonSetFlowrate = wx.Button(self, -1, "Set Flowrate", pos =(320,140),size = (115,-1))
        self.buttonSetFlowrate.Bind(wx.EVT_BUTTON, self.SetFlowrate)
        self.textboxFlowRate = wx.TextCtrl(self, -1, "0", pos = (355,110), size = (40,-1))


        label_Setsensors = wx.StaticText(self, -1,"Calibrate Sensors", pos =(940,10)) 
        self.button_lwlR1 =wx.Button(self, -1,"Set min R1 " , pos =(940,40)) 
        self.button_lwlR1.Bind(wx.EVT_BUTTON, self.setLWL1)
        self.label_lwlR1 = wx.StaticText(self, -1,str(self.reservoir.limitR1) , pos = (960,65),size=(50,-1)   )
        
        self.button_lwlR2 =wx.Button(self, -1,"Set min R2 " , pos =(1040,40)) 
        self.button_lwlR2.Bind(wx.EVT_BUTTON, self.setLWL2)
        self.label_lwlR2 = wx.StaticText(self, -1,str(self.reservoir.limitR2) , pos = (1050,65),size=(50,-1)   )
        
        self.CalibrateSensors =wx.Button(self, -1,"Zero All Sensors" , pos =(940,100))
        self.CalibrateSensors.Bind(wx.EVT_BUTTON, self.Calibrate_sensor)
        
        self.Calibrateboard =wx.Button(self, -1,"Zero Board sensors" , pos =(940,130))
        self.Calibrateboard.Bind(wx.EVT_BUTTON, self.Zero_board)
        
        self.Calibrateboard =wx.Button(self, -1,"Zero Reservoir sensors" , pos =(940,160))
        self.Calibrateboard.Bind(wx.EVT_BUTTON, self.Zero_Reservoirs)

        self.buttonSetFreq = wx.Button(self, -1, "Sample rate [Hz]", pos = (940, 200),size = (100,-1))
        self.buttonSetFreq.Bind(wx.EVT_BUTTON, self.setFreq) 
        
        self.toggleTimer = wx.ToggleButton(self, id = -1, label = "Stop Refresh", pos = (940,230))
        self.toggleTimer.Bind(wx.EVT_TOGGLEBUTTON, self.ControlTimer)
        
        self.textboxSampleTime = wx.TextCtrl(self, -1, str(self.settings.loc['frequency'][0]), pos = (1080,200), size = (30,-1))
            
        self.togglebuttonPQ = wx.ToggleButton(self, id = -1, label = "Mode: Constant Pressure", pos = (510,10))
        self.togglebuttonPQ.Bind(wx.EVT_TOGGLEBUTTON, self.PorQ)  

        self.togglebuttonMode = wx.ToggleButton(self, id = -1, label = "Mode: Recirculation", pos = (510,40))
        self.togglebuttonMode.Bind(wx.EVT_TOGGLEBUTTON, self.changeMode)
        
        self.togglebuttonRef = wx.ToggleButton(self, id = -1, label = "Ref = MPR", pos = (1040,10))
        self.togglebuttonRef.Bind(wx.EVT_TOGGLEBUTTON, self.SetRef)
        if  self.Data.RRef=="MPR":
            self.togglebuttonRef.SetValue(True)
            
        label_Injection_volume = wx.StaticText(self, -1, "Injection \nVolume [ml]", pos = (510,70))
        self.in_volume = wx.TextCtrl(self, -1, "1", pos = (510,105),size = (50,-1))

        self.buttonDirection= wx.Button(self, -1, "Overwrite direction", pos =(740,10))
        self.buttonDirection.Bind(wx.EVT_BUTTON, self.overwriteDirection) 
        
        column=620
        labelChannels = wx.StaticText(self, -1, "Adjust settings:", pos = (column,75))
        self.cb1 = wx.CheckBox(self, -1, label = "Use Pressure Sensors",pos = (column,125))
        self.cb2 = wx.CheckBox(self, -1, label = "Use switchboard",pos = (column,165))
        self.cb3 = wx.CheckBox(self, -1, label = "Leakage Detection", pos = (column,145))
        self.cb4 = wx.CheckBox(self, -1, label = "Pressure Limit", pos = (column,105))

        self.cb5 = wx.CheckBox(self, -1, label = "Run empty break", pos = (column,185))
        self.cb6 = wx.CheckBox(self, -1, label = "Send Mail", pos = (column,205))
        self.PressureLimit = wx.TextCtrl(self, -1, str(self.settings.loc['pressurelimit'][0]), pos = (column+100,100),size = (50,-1))
        self.mailadress = wx.TextCtrl(self, -1, str(self.settings.loc['mail'][0]), pos = (column+80,205),size = (170,-1))
        
        try:
            if self.Pressure.ser != True:
                self.cb1.SetValue(True)   
        except:
            self.cb1.SetValue(False)
        if self.Fluigent.switchboard != None:
            self.cb2.SetValue(bool(self.settings.loc['cb2'][0]))
        if self.settings.loc['cb3'][0]==1:
            self.cb3.SetValue(True)
        if self.settings.loc['cb4'][0]==1:
            self.cb4.SetValue(True)
        if self.settings.loc['cb5'][0]==1:
            self.cb5.SetValue(True)
        if self.settings.loc['cb6'][0]==1:
            self.cb6.SetValue(True)
            

        
        
        self.Bind(wx.EVT_CHECKBOX, self.OnChecked)

        self.togglebuttonSwitch = wx.ToggleButton(self, id = -1, label = "Switch: Medium", pos = (column,230))
        self.togglebuttonSwitch.Bind(wx.EVT_TOGGLEBUTTON, self.changeSwitchMedium)
        if self.settings.loc['switchmedium'][0]=='medium':
            self.togglebuttonSwitch.SetValue(False)
        elif self.settings.loc['switchmedium'][0]=='air':
            self.togglebuttonSwitch.SetValue(True)
            
        
        label_filename = wx.StaticText(self, -1, "Set sample name:", pos = (300,0))
        self.samplename = wx.TextCtrl(self, -1, self.settings.loc['samplename'][0], pos = (300,20))
        
        label_Loginterval = wx.StaticText(self, -1, "Log interval", pos = (410,0))
        unit_loginterval= wx.StaticText(self, -1, "[s]", pos = (455,20))
        self.LogInterval = wx.TextCtrl(self, -1, "1", pos = (420,20),size = (30,-1))
        
       
#__________________timer__________________________
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Consol, self.timer)
        self.timer.Start(int((1/float(self.Freq))*1000))
#_____________________________________startup
        self.Fluigent.KillCommands()
        self.Fluigent.ZeroSensors()

        
#________________Button actions________________________________________________
    def SetRef(self,event):
        if  self.togglebuttonRef.GetValue()==True:
            self.Data.RRef="MPR"
            self.togglebuttonRef.SetLabel("Ref: MPR")
        else:
            self.Data.RRef="EZ"
            self.togglebuttonRef.SetLabel("Ref: EZ")

    def Calibrate_sensor(self,event):
        print("Calibrate all sensors")
        self.Fluigent.KillCommands()
        time.sleep(5)
        self.Fluigent.ZeroSensors()
        time.sleep(5)
        self.Pressure.Zero(Command=0,S1=True,S2=True,S3=True,S4=True,
                           S5=True,S6=True,S7=True,S8=True)
    
    def Zero_board(self,event):
        print("Calibrate board")
        self.Fluigent.KillCommands()
        time.sleep(5)
        self.Pressure.Zero(Command=0,S1=True,S2=True)

    def Zero_Reservoirs(self,event):
        print("Calibrate all sensors")
        self.Fluigent.KillCommands()
        time.sleep(5)
        self.Fluigent.ZeroSensors()
        time.sleep(5)
        self.Pressure.Zero(S3=True,S4=True,S5=True,S6=True)

    def UpdateBottomLabel(self):
         print("Update bottom labels")
        
    def SetFlowrate(self,event):
        try:
            Qin= float(self.textboxFlowRate.GetValue())
            print("set flowrate")
        except:
            print("Q No valid command")
        else:
            if Qin<self.Fluigent.LineUP.GetFlowrateRangeMin(0) or Qin>self.Fluigent.LineUP.GetFlowrateRangeMax(0):
                print("Q input out of range")
            else:
                self.Sensor.setCommandQ(Qin)
        print("Flowrate")
    
    def setLWL1(self,event):
        print("Set LWL 1")
        self.reservoir.limitR1=self.Data.dampData(self.Data.dpR1,kernel=1,Hz=self.Hz)
        self.label_lwlR1.SetLabel(str(round(self.reservoir.limitR1,2)))
     
    def setLWL2(self,event):
        print("Set LWL 2")
        self.reservoir.limitR2=self.Data.dampData(self.Data.dpR2,kernel=1,Hz=self.Hz)
        self.label_lwlR2.SetLabel(str(round(self.reservoir.limitR2,2)))
        
    def setPIDpar(self,event):
        try:
            P=float(self.textboxkP.GetValue())
        except:
            pass
        try:
            I=float(self.textboxkI.GetValue())
        except:
            pass
        try:
            D=float(self.textboxkD.GetValue())
        except:
            pass
        try:
            self.Data.setPID(kP=P,kI=I,kD=D)
            
            print("PID set")
        except:
            print("nothing happend")
            
    def Calculate(self,event):
        print("calculate target shear")
        Pin,Pout=Calculator.dP(self.textboxShearStress.GetValue(),self.textboxPressure.GetValue()) 
        self.textboxPressure_inlet.SetValue(str(round(Pin,2)))
        self.Command.setCommandIN(Pin)
        self.textboxPressure_outlet.SetValue(str(round(Pout,2)))
        self.Command.setCommandOUT(Pout)
        self.Command.setCommanddP(Pin-Pout)
        self.Command.setCommandPin(float(self.textboxPressure.GetValue()))
        
    def SetPressure(self, event):
        print("Change pressure command")
        """Input: PressureInlet valueconverted to string
           Output: change command in sensor module"""
        try:
            p_inlet = float(self.textboxPressure_inlet.GetValue())
            p_outlet = float(self.textboxPressure_outlet.GetValue())
        except: 
            print("No valid command")
        else:
            tempIn=self.Command.getCommandIN()
            tempOut=self.Command.getCommandOUT()
            
            commandIN=max(min(p_inlet,345),0)
            commandOUT=max(min(p_outlet,345),0)
            
            self.Command.setCommandIN(commandIN)
            self.Command.setCommandOUT(commandOUT)
            self.Command.setCommanddP(commandIN-commandOUT)
                
        Shear,Pres=self.Calc.dPAndPres(self.Command.getCommandIN(), self.Command.getCommandOUT())
        self.textboxShearStress.SetValue(str(round(Shear,3)))
        self.textboxPressure.SetValue(str(round(Pres,2)))
        self.Command.setCommandPin(float(self.textboxPressure.GetValue()))
        self.Data.OverwritePIDcommand(commandIN,commandOUT)


    def overwriteDirection(self,event):
        print("Change direction")
        dp=0#abs(self.Data.dampData(self.Data.dpR1,kernel=1,Hz=self.Hz)-self.Data.dampData(self.Data.dpR2,kernel=1,Hz=self.Hz))
        #self.Data.OverwritePIDcommand(self.Data.Cin-dp,self.Data.Cout+dp)
        if self.reservoir.getDirection()==1:
            self.reservoir.setDirection(2)
        elif self.reservoir.getDirection()==2:
            self.reservoir.setDirection(1)
        else :
            self.reservoir.setDirection(1)
        self.Fluigent.switchSwitchDirection(self.reservoir.getDirection())
        self.Data.old_switch=self.Data.new_switch
        self.Data.new_switch=datetime.datetime.now()
        self.Data.SitRep(self.file_name,self.sitrepName,self.Data.old_switch)
        
        if self.cb6.GetValue()==True:
            try:
                temp=self.Mail.AttachSitRep(self.sitrepName)
                self.Mail.SendMail(temp,self.mailadress.GetValue())
            except:
                print("No server")
        
    def changeSwitchMedium(self,event):
        if  self.togglebuttonSwitch.GetValue()==True:
            self.switchfluid="air"
            self.togglebuttonSwitch.SetLabel("Switch: Air")
        else:
            self.switchfluid="medium"
            self.togglebuttonSwitch.SetLabel("Switch: Medium")
            
    def ControlTimer(self,event):

        if self.toggleTimer.GetValue() == True:
            self.timer.Stop()
            self.toggleTimer.SetLabel("Continue")
            print("Stop Refresh")
        else:
            self.setFreq(event)
            self.toggleTimer.SetLabel("Stop Refresh")
            print("Start Refresh")

    def setFreq(self, event):
        print("Set freqency")
        self.Freq = int(self.textboxSampleTime.GetValue())
        print(self.Freq)
        self.time_freq=int((1/float(self.Freq))*1000)
        
        self.timer.Start(self.time_freq)
    def OnChecked(self, event):
        print("Changed settings")
        print("Pressure head corrector ",self.cb1.GetValue())
        print("Using switch " ,self.cb2.GetValue() )
        print("Leakage detection ", self.cb3.GetValue() )
    
    def Consol(self,event):
        if  self.togglebuttonStart.GetValue()==True:
            self.Running()
            self.run= True
        else:
            self.Standby()
            self.run= False
        
    def Standby(self):
        print("Standby")
        self.standardCycle()

    def Running(self):
        """ 1. time management
            2. data collecion,calculation
            3. Decision switch
            4. Set pressure"""
        #global ts
        print("Experiment running")
        self.standardCycle()
         
        if self.togglebuttonPause.GetValue()==False:
            if self.togglebuttonPQ.GetValue()== True:#fixed flowrated command
                self.FlowrateMode()
            else:
                self.PressureMode()
        
        self.Data._dv = self.reservoir.balanceReservoirs(self.Data.dampData(self.Data.listQ,kernel=1,Hz=self.Hz),self.dt.total_seconds(),self.reservoir.getDirection())
        
        self.reservoir.setInjectedVolume(abs(self.Data._dv))
        if self.mode =="Volume_injection":
           if self.reservoir.getInjectionV() <= self.reservoir.getInjectedV():
               self.Fluigent.KillCommands()
               self.run= False
               self.togglebuttonStart.SetLabel("Start")
               frame.SetStatusText("Standby again")
               self.togglebuttonStart.SetValue(False)
               
        if self.cb3.GetValue()==True:
            self.reservoir.LeakDetection(self.Data.dampData(self.Data.dpR1,kernel=3,Hz=self.Hz),
                                              self.Data.dampData(self.Data.dpR2,kernel=3,Hz=self.Hz),
                                              self.startVolume,self.current_timestamp)
        
        self.Data.WriteLogfile(self.file_name,self.current_timestamp,self.reservoir.getDirection())
        
        if self.reservoir.getDirection() == 0:
            self.Fluigent.KillCommands()
            self.Fluigent.switchSwitchDirection(0)
            self.togglebuttonStart.SetLabel("Leakage Detected")
            frame.SetStatusText("Leakage Detected!")
            
            if self.cb6.GetValue()==True:
                try:
                    self.Mail.SendMail("Subject: je kan gaan dweilen",self.mailadress.GetValue())
                except:
                    print("No server")
            
            self.togglebuttonStart.SetValue(False)
        
        if self.cb5.GetValue()==True:
            if abs(self.Data._Q)<9:
                if self.dryFlag==False:
                    self.dryFlag=True
                    self.dry_Time=self.current_timestamp
                elif self.dryFlag==True:
                      if self.dry_Time== "Message sent":
                          pass
                      elif self.current_timestamp-self.dry_Time>datetime.timedelta(seconds=5):
                          if self.cb6.GetValue()==True:
                              self.Mail.SendMail("Subject: There arose a small technical problem",self.mailadress.GetValue())
                          self.dry_Time="Message sent"
                          self.buttonDirection.invoke()
            else:
                self.dryFlag=False
                self.dry_Time=None
        #______________________________________________________draw and display data
    def TimeManagement(self):
        self.current_timestamp  = datetime.datetime.now()
        self.dt   = self.current_timestamp-self.old_timestamp
        self.Hz =int(1/self.dt.total_seconds())
        self.old_timestamp   = self.current_timestamp
        if self.run==True:
            self.experimentDuration= self.current_timestamp-self.startTime
    
        else:
            self.experimentDuration="Standby"    
    
    def standardCycle(self):
         print("standard Cycle")
         #global ts
         self.TimeManagement()
         self.Data.dataCycle(ez=self.Fluigent.getEZP(),pressure=self.Pressure.measurePressure(),
                             direction=self.reservoir.getDirection())
         
         self.refreshData()
         
         old,new = self.reservoir.dpcheck_TLL(self.Data.dampData(self.Data.dpR1,kernel=3,Hz=self.Hz),
                                              self.Data.dampData(self.Data.dpR2,kernel=3,Hz=self.Hz),
                                              self.current_timestamp)
         if old!=new:
            dp=0#abs(self.Data.dampData(self.Data.dpR1,kernel=1,Hz=self.Hz)-self.Data.dampData(self.Data.dpR2,kernel=1,Hz=self.Hz))#HIERO gaat het fout
            print(dp)
            self.Data.OverwritePIDcommand(self.Data.Cin-dp,self.Data.Cout+dp)
            self.Fluigent.switchSwitchDirection(new)
            
            self.Data.old_switch=self.Data.new_switch
            self.Data.new_switch=datetime.datetime.now()
            self.Data.SitRep(self.file_name,self.sitrepName,self.Data.old_switch)
            if self.cb6.GetValue()==True:
                try:
                    temp=self.Mail.AttachSitRep(self.sitrepName)
                    self.Mail.SendMail(temp,self.mailadress.GetValue())
                except:
                    print("No server")
         self.graphL.draw(self.Data.t, self.Data.listQ, self.Data.Pf, self.Data.Pw)
            
         print(self.Hz,"Hz Standby")
         
    
        
    def refreshData(self):
        print("Refresh Data")
        self.graphL.UpdateLabel(kernel=2,Hz=15,Time=self.experimentDuration,inV=self.reservoir.getInjectedV(),
                                Dir=self.reservoir.getDirection(),
                                ComInlet=self.Command.getCommandIN(),ComOutlet=self.Command.getCommandOUT(),
                                EZ1=self.Data.P1,EZ2=self.Data.P2,Q=self.Data.listQ,
                                PF=self.Data.Pf,PW=self.Data.Pw,
                                dpR1=  self.Data.dpR1,dpR2=  self.Data.dpR2,
                                V1=self.Calc.dPtoVolume(self.Data.dpR1),V2=Calc.dPtoVolume(self.Data.dpR1),
                                Vstart=self.startVolume,
                                RHI=self.Data._Rhi,
                                RHsamp=self.Data._Rhs,
                                RHO=self.Data._Rho,
                                dpin=self.Data._dPi,dpout=self.Data._dPo,TEQ=self.TEQ)
                    
        
        #self.graphR.draw(self.reservoir.get_V1(),self.reservoir.get_V2())
        self.graphR.UpdateLabel(S1=self.Data.PressureData[0],
                                S2=self.Data.PressureData[1],
                                S3=self.Data.PressureData[2],
                                S4=self.Data.PressureData[3],
                                S5=self.Data.PressureData[4],
                                S6=self.Data.PressureData[5],
                                S7=self.Data.PressureData[6],
                                S8=self.Data.PressureData[7],
                                EZ1=round(self.Data._PEZ1,1),
                                EZ2=round(self.Data._PEZ2,1),
                                Q=round(self.Data._Q,1),
                                Q2=round(self.Data._Q2,1))
        self.UpdateBottomLabel()
        
    def PressureMode(self):

        if self.cb4.GetValue()==True:
            
            comin,comout=self.Data.BoardPID(self.Command.getCommandIN(),self.Command.getCommanddP(),
                                        self.Data.PressureData[self.RefChoice1.GetSelection()],
                                        self.Data.PressureData[self.RefChoice2.GetSelection()],
                                        kP=self.Data.kProp,kI= self.Data.kInt,kD=self.Data.kDeriv,
                                        limit=float(self.PressureLimit.GetValue()))
        else:
            comin,comout=self.Data.BoardPID(self.Command.getCommandIN(),self.Command.getCommanddP(),
                                        self.Data.PressureData[self.RefChoice1.GetSelection()],
                                        self.Data.PressureData[self.RefChoice2.GetSelection()],
                                        kP=self.Data.kProp,kI= self.Data.kInt,kD=self.Data.kDeriv)
        
        
        self.Fluigent.SendPressure(comin,comout,self.reservoir.getDirection(),
                                       medium=self.switchfluid,switch=self.cb2.GetValue())
 
    def FlowrateMode(self):
        
        
        if self.cb4.GetValue()==True:
        
            comin,comout=self.Data.BoardPID(self.Command.getCommandQ(),self.Command.getCommandPin(),
                                        self.Data._Q,
                                        self.Data.PressureData[self.RefChoice2.GetSelection()]-self.Data.PressureData[self.RefChoice2.GetSelection()],
                                        kP=self.Data.kProp,kI= self.Data.kInt,kD=self.Data.kDeriv,
                                        limit=float(self.PressureLimit.GetValue()))
        
        else:
            comin,comout=self.Data.BoardPID(self.Command.getCommandQ(),self.Command.getCommandPin(),
                                        self.Data._Q,
                                        self.Data.PressureData[self.RefChoice2.GetSelection()]-self.Data.PressureData[self.RefChoice2.GetSelection()],
                                        kP=self.Data.kProp,kI= self.Data.kInt,kD=self.Data.kDeriv)
        
        self.Fluigent.SendPressure(comin,0,self.reservoir.getDirection(),
                                       medium=self.switchfluid,switch=self.cb2.GetValue())
        
    def getInterval(self):
        print("Change log interval")
    
    def changeMode(self,event):
        self.modus = self.togglebuttonMode.GetValue()
        if self.modus == False:
            self.mode= "recirculation"
            self.togglebuttonMode.SetLabel("Mode: Recirculation")
        elif self.modus== True:
            self.mode= "Volume_injection"
            self.togglebuttonMode.SetLabel("Mode: Injection mode")
            
    def PorQ(self,event):
        self.PQ = self.togglebuttonPQ.GetValue()
        if self.PQ == False:
            self.FixedParameter= "P"
            self.togglebuttonPQ.SetLabel("Mode: Constant Pressure")
        elif self.PQ== True:
            self.FixedParameter= "Q"
            self.togglebuttonPQ.SetLabel("Mode: Constant Q")
        print("recirculation or volume")
            

    def OnStartClick(self, event):
        print("Start")
        self.startTime = self.nexttimestamp=datetime.datetime.now() 
        
        self.startVolume= self.Data.dampData(self.Data.dpR1,kernel=1,Hz=self.Hz)+ self.Data.dampData(self.Data.dpR2,kernel=1,Hz=self.Hz)

        
        self.file_name=self.Data.CreateLogFile(self.samplename.GetValue(),self.startTime)
        self.sitrepName=self.file_name[:-4]+"_SituationReport.csv"
        self.Data.createSitreport(self.sitrepName)
        
        if self.mode== "recirculation":
            Message=("starting recirculation mode")
            self.reservoir.setInjectedVolume("reset")
        elif self.mode=="Volume_injection":    
            self.reservoir.setInjectedVolume("reset")
            Message=("Starting injection mode")
            self.reservoir.setInjectionV(float(self.in_volume.GetValue()))
            
        if ( self.togglebuttonStart.GetValue() == True):
            self.Fluigent.switchSwitchDirection(self.reservoir.getDirection())
            print(Message)
            #self.Volume[:]=np.NaN
            frame.SetStatusText("Running!")
            self.togglebuttonStart.SetLabel("Stop")
            

        else:
            self.Fluigent.KillCommands()
            self.togglebuttonStart.SetLabel("Start")
            frame.SetStatusText("Standby again")
            
    def Pause(self,event):
        
        print("Paused")

class Main(wx.Frame):
    def __init__(self):
        """Built up of GUI frame."""
        self.main = wx.Frame.__init__(self, parent = None, title = "Microfluidic Circuitboard Console", size = (1200,770))
        self.splitter = wx.SplitterWindow(self)
       
        topL = TopPanelLeft(self.splitter)
        topR = TopPanelRight(self.splitter)
        Bottom = BottomPanel(self,topL,topR)
        # SPLIT THE WINDOW
        self.splitter.SplitVertically(topL, topR)
        self.splitter.SetMinimumPaneSize(890)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND)
        sizer.Add(Bottom, 1, wx.EXPAND)
        self.SetSizer(sizer) 
        #topL.draw(0,1,2,3)
        #topR.draw(10,2)
        self.makeMenuBar()
        self.CreateStatusBar()# and a status bar
        self.SetStatusText("Standby!")
 
    def makeMenuBar(self):
            """Built menu."""
        # Make a file menu with Hello and Exit items
            fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
            helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H","Help string shown in status bar for this menu item")
            fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
            exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
            helpMenu = wx.Menu()
            aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
            menuBar = wx.MenuBar()
            menuBar.Append(fileMenu, "&File")
            menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
            self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
            self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
            self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
            self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        
        self.Close(True)

    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("A not so usefull function but maybe later")


    def OnAbout(self, event):
        """Display an About Dialog."""
        wx.MessageBox("MNS","MFCB", wx.OK|wx.ICON_INFORMATION)

if __name__ == "__main__":
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()