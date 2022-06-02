from __future__ import print_function
from LineUP_Middleware import *
from LineUP_lowLevel import PRESSURE_UNIT   # Explicit import of available enumerations
from LineUP_lowLevel import FLOW_UNIT
from LineUP_lowLevel import PRESSURE_MODE
from LineUP_lowLevel import FLOW_UNIT_CALIBRATION_TABLE
from LineUP_lowLevel import TTL_PORT
from LineUP_lowLevel import TTL_MODE
from LineUP_lowLevel import POWER_STATE
from LineUP_lowLevel import FLOW_UNIT_TYPE
import LineUP_Middleware                #Fluigent LineUP LineUP Middleware
from Fluigent.ESS import Switchboard
import random
import math
import datetime
import time
import numpy as np
import pandas as pd
import io
import serial
import csv
from scipy.stats import iqr

class fluigent(object):
    def __init__(self):
        self.LineUP = LineUPClassicalSessionFactory().Create(0)
        try:
            self.switchboard   = Switchboard()
            self.switch_inlet  = self.switchboard[1]
            self.switch_outlet = self.switchboard[2]
            print("Switchboard connected")
        except:
            print("No Switchboard  connected")
            self.switchboard=None
        self._InverseCorrection=0#60.85189
        self.EZmax=min(self.LineUP.GetPressureRangeMax(0),self.LineUP.GetPressureRangeMax(1))+2
         
    def SetSwitch(self,position1,position2):
        self.switch_inlet.position = position1 
        self.switch_outlet.position = position2

    def switchSwitchDirection(self,direction):
        if direction == 1:
            try:
                self.switch_inlet.position =  1
                self.switch_outlet.position = 2
            except:
                print("No Switch Connected")
        elif direction == 2:
            try:
                self.switch_inlet.position =  2
                self.switch_outlet.position = 1
            except:
                print("No Switch Connected")
        #elif direction == 0:
        #    self.switch_inlet.position =  1
        #   self.switch_outlet.position = 1
        return print("Switched")
    
    def getEZP(self):
        
       EZ1 = self.LineUP.GetPressure(0)
       EZ2 = self.LineUP.GetPressure(1)
       Q   = self.LineUP.GetFlowrate(0)
       Q2  = self.LineUP.GetFlowrate(1)
       
       if math.isnan(EZ1):
           print("dummy data")
           EZ1= 80+ 2*random.random()
           EZ2= 20+ 2*random.random()
           Q= 1500+ 50*random.random()
           Q2= 100+ 50*random.random()
       return EZ1,EZ2,Q,Q2
    
    def setInverseCorrection(self,IN):
        self._InverseCorrection=IN
        
    def getInverseCorrection(self):
          return self._InverseCorrection      
    
    def KillCommands(self):
        """resets and sends EZ commands to Zero
        requires no arguments"""
        self.LineUP.SetPressure(0, 0)
        self.LineUP.SetPressure(1, 0)
        print('Kill EZ Commands')
        #____________________________kill commands zero pressures
    def ZeroSensors(self):
        """Calibrates lineup sensors to zero"""
        self.LineUP.CalibratePressureSensor(0)
        self.LineUP.CalibratePressureSensor(1)
        print("Calibrate Pressure Sensors")

    def SendPressure(self,inletP,outletP,direction,medium,switch):
        """ input :targetP,Direction,switch
            outpout: Fluigent action"""
        if direction==1:
            input_EZ=0
            output_EZ=1
        elif direction==2:
            input_EZ=1
            output_EZ=0
        elif direction==0:
            input_EZ=0
            output_EZ=1
            
        if switch==False:
            self.LineUP.SetPressure(input_EZ, inletP)                                                                            
            self.LineUP.SetPressure(output_EZ, outletP)                                                                            
        elif switch==True:
            if medium=="medium":
                self.LineUP.SetPressure(output_EZ, outletP)
                self.LineUP.SetPressure(input_EZ, inletP)
            elif medium=="air":
                self.LineUP.SetPressure(0, inletP)
                self.LineUP.SetPressure(1, outletP)

class PressureSensor(object):
    """microcontroler 8 sensors"""

    def __init__(self,comPort="COM3"):
        try:
            self.ser = serial.Serial(comPort,baudrate=250000,timeout=0.05)
            print("Pressure sensor connected")
        except:
            print("no Pressure sensors connected")
        try:#load Pressure calibration
            self.calibration=pd.read_csv("Settings\PressureZero.csv",header=None,dtype="float64")[0]
            self.ramp_calibration=pd.read_csv("Settings\PressureZero_ramp.csv",header=None,dtype="float64")[0]
            print("calibration loaded")
        except:
            self.calibration=(0,0,0,0,0,0,0,0)
        
        try:
            self.ser_io = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),  
                               newline = '\r',
                               line_buffering = True)
        except: 
            print("dont care")
        self.Catch=(np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan)
       
        self._S1=self._S2=self._S3=self._S4=self._S5=self._S6=self._S7=self._S8=0
        self.Raw=(0,0,0,0,0,0,0,0)

    def connectToSensor(self):
        if self.ser.is_open==False:
            self.ser.open() 
        self.ser.reset_input_buffer()
        temp=self.ser_io.readline()
        #self.ser.flushInput()
        temp=temp[:-2]
        temp=temp.split(',')
        
        try:
            temp = list(map(int, temp))
        except:
            temp=[0,0,0,0,0,0,0,0]
        self.Raw= tuple(temp)
    
    def measurePressure(self):
        try:
            if self.ser.is_open==True:

                self.connectToSensor()
                try:
                    temp=self.Raw
                except:
                
                    temp=self.Catch
            temp=self.convertToPressure(temp)
            temp=round(temp-self.calibration,2)

            try:
                self.PressureData=temp
                self._S1,self._S2,self._S3,self._S4,self._S5,self._S6,self._S7,self._S8=temp
            
            except:
                print("failed tuple")
        except:
            print("sensor connection failed")
            temp=(50.5,49.5,86,23,80,20,0,0)
        return temp

    def convertToPressure(self,count):
        outputMin=0.025*2**24#419430.4
        outputMax=0.225*2**24
        minmax=outputMax-outputMin
        Pmin=0
        Pmax=300
        count=pd.Series(count)
        Pressure=(((count-outputMin)*(Pmax-Pmin))/minmax)*1.333222368
        return np.around(Pressure,2)
 
    def Zero(self,Command=0,counts=100,S1=False,S2=False,S3=False,S4=False,S5=False,S6=False,
             S7=False,S8=False):
        calibration= []
        for i in range (0,counts):
            self.connectToSensor()
            calibration.append(self.Raw)
        calibration=pd.DataFrame(calibration)
        
        temp_file=pd.read_csv("Settings\PressureZero.csv",header=None,dtype="float64")[0]
        
        calibration=calibration.median(axis=0,numeric_only=True)
        calibration=self.convertToPressure(calibration)

        if S1==True:
            temp_file[0]=calibration[0]    
        if S2==True:
            temp_file[1]=calibration[1]
        if S3==True:
            temp_file[2]=calibration[2]
        if S4==True:
            temp_file[3]=calibration[3]
        if S5==True:
            temp_file[4]=calibration[4]     
        if S6==True:
            temp_file[5]=calibration[5]
        if S7==True:
            temp_file[6]=calibration[6]
        if S8==True:
            temp_file[7]=calibration[7]
        temp_file.to_csv("Settings\PressureZero.csv" ,header=False,index=False)
        
        
        self.calibration=pd.read_csv("Settings\PressureZero.csv",header=None,dtype="float64")[0]
        
        print("calibration loaded")
        print(self.calibration)
        
        
        
    def Zero(self,Command=0,counts=100,S1=False,S2=False,S3=False,S4=False,S5=False,S6=False,
             S7=False,S8=False):
        calibration= []
        for i in range (0,counts):
            self.connectToSensor()
            calibration.append(self.Raw)
        calibration=pd.DataFrame(calibration)
        
        temp_file=pd.read_csv("Settings\PressureZero.csv",header=None,dtype="float64")[0]
        
        calibration=calibration.median(axis=0,numeric_only=True)
        calibration=self.convertToPressure(calibration)

        if S1==True:
            temp_file[0]=calibration[0]    
        if S2==True:
            temp_file[1]=calibration[1]
        if S3==True:
            temp_file[2]=calibration[2]
        if S4==True:
            temp_file[3]=calibration[3]
        if S5==True:
            temp_file[4]=calibration[4]     
        if S6==True:
            temp_file[5]=calibration[5]
        if S7==True:
            temp_file[6]=calibration[6]
        if S8==True:
            temp_file[7]=calibration[7]
        temp_file.to_csv("Settings\PressureZero.csv" ,header=False,index=False)
        
        
        self.calibration=pd.read_csv("Settings\PressureZero.csv",header=None,dtype="float64")[0]
        
        print("calibration loaded")
        print(self.calibration)
    
    def averageMeasurement(self,dataframe,k=200):
       datapoint= np.nanmedian(dataframe[-k:])
       maxDP=np.nanmax(dataframe[-k:])
       minDP=np.nanmin(dataframe[-k:])
       print(datapoint,minDP,maxDP)
       return datapoint

class mFCB(object):
     def __init__(self,version="v1",med="wm"):
         """input: platform ID and medium 
             'wm':warm medium
            'cw':cold water 
            'ww':warm water"""
         self.version=version
         self.TEQ=24058305351.1005
         if med=="wm":
             self.viscosity= 0.00078
             self.density= 1.002
         elif med=="cw":
             self.viscosity= 0.001
             self.density= 1.0
         elif med=="ww":
             self.viscosity= 0.0006
             self.density= 0.998

class Commandos(object):
    def __init__(self):
        self._command_in= 0
        self._command_out= 0
        self._command_Q= 0
        self._command_Pin= 0
        self._command_dP=0

    def setCommandIN(self,IN):    
        self._command_in=IN
        
    def setCommandOUT(self,OUT):    
        self._command_out=OUT
        
    def setCommandQ(self,Qin):
        self._command_Q= Qin
        
    def setCommanddP(self,dp):
        self._command_dP= dp
    
    def setCommandPin(self,IN):    
        self._command_Pin=IN
        
    def getCommandIN(self):    
        return self._command_in
    
    def getCommandOUT(self):
        return self._command_out
    
    def getCommanddP(self):
        return self._command_dP
            
    def getCommandQ(self):
        return self._command_Q
    
    def getCommandPin(self):    
        return self._command_Pin

    
class sensorsData(object):
    def __init__(self):
         self.ts=self.tss=datetime.datetime.now()
         self.new_switch=datetime.datetime.now()
         self.own_switch=self.new_switch
         self.frameSize=500
         self.kProp=0.0
         self.kInt=0.0
         self.kDeriv=0.0
         #single numbers
         
         self.PressureData=[]
         
         self._PEZ1=0
         self._PEZ2=0
         self._PFeeder=0
         self._PWaste=0
         self._RP1=0
         self._RP2=0
         
         self._dpR1=0
         self._RP1a=0
         self._dpR2=0
         self._RP2a=0
         self._dpPF=0
         self._dpPW=0
         self._Q=0
         self._Q2=0
         self._tauA=0
         self._tauMin=0
         self._tauMax=0
         self._vR1=0
         self._vR2=0
         self._dv=0
         
         self._Rhi=0
         self._Rho=0
         self._Rhs=0
         
         self._dPi=0
         self._dPsamp=0
         self._dPo=0
            
         self.RRef="MPR"
         
      
         self.nexttimestamp=datetime.datetime.now()
        #Frames
         self.FramePressureData=np.empty([self.frameSize,8])
         self.FrameEZ=np.empty([self.frameSize,3])
         self.FramePara=np.empty([self.frameSize,8])
         
         self.t = self.fillTimeframe(self.frameSize)
         self.P1 = np.empty(self.frameSize)
         self.P2 = np.empty(self.frameSize)
         self.P1a = np.empty(self.frameSize)
         self.P2a = np.empty(self.frameSize)
         self.Pf = np.empty(self.frameSize)
         self.Pw = np.empty(self.frameSize)

        
         self.pS1 = np.empty(self.frameSize)
         self.pS2 = np.empty(self.frameSize)
         self.dpR1= np.empty(self.frameSize)
         self.dpR2= np.empty(self.frameSize)
         self.dpPF=np.empty(self.frameSize)
         self.dpPW=np.empty(self.frameSize)
         self.Volume=np.empty(self.frameSize)
         
         self.Rhi=np.empty(self.frameSize)
         self.Rho=np.empty(self.frameSize)
         self.Rhs=np.empty(self.frameSize)
         
         self.dPi=np.empty(self.frameSize)
         self.dPsamp=np.empty(self.frameSize)
         self.dPo=np.empty(self.frameSize)
        
         self.listQ = np.empty(self.frameSize)
         self._Volume=np.empty(self.frameSize)
         self._Temperature=np.nan
         
         self.Cin=0
         self.Cout=0
         self.Prev_ErrorIN=0
         self.Prev_ErrorOut=0
         self.Sum_ErrorIN=0
         self.Sum_ErrorOUT=0
         
    def setPID(self,kP=0.1,kI=0.05,kD=0.025):
         self.kProp=kP
         self.kInt=kI
         self.kDeriv=kD
         
    def OverwritePIDcommand(self,inlet,outlet):
        self.Cin  = inlet
        self.Cout = outlet
        
    def ReservoirPID(self,Tin,Tout,Refin,Refout,kP=0.1,kI=0.05,kD=0.0,limit=345):
        ErrorIN = Tin - Refin
            
        ErrorOUT= Tout - Refin

        if np.isnan(ErrorIN) or np.isnan(ErrorOUT):
            pass
        else:
            CorIN = (ErrorIN*kP)  + (self.Prev_ErrorIN*kD)  + (self.Sum_ErrorIN*kI)
            CorOUT= (ErrorOUT*kP) + (self.Prev_ErrorOut*kD) + (self.Sum_ErrorOUT*kI)
            
            if np.isnan(CorIN) or np.isnan(CorOUT):
                pass
            else:
                self.Cin  += CorIN
                self.Cout += CorOUT
                
                self.Prev_ErrorIN=ErrorIN
                self.Prev_ErrorOut=ErrorOUT
                    
                if self.Cin<limit or self.Sum_ErrorOUT<limit:
                    self.Sum_ErrorIN += ErrorIN
                    self.Sum_ErrorOUT += ErrorOUT
                else:
                    if self.Cin*ErrorIN>0 or self.Cout*ErrorOUT*self.Cin*ErrorIN>0:
                        self.Sum_ErrorIN = 0
                        self.Sum_ErrorOUT = 0
                    
            self.Cin=max(min(self.Cin,limit),0)
            self.Cout=max(min(self.Cout,self.Cin),0)
            
            return self.Cin, self.Cout
         
    def BoardPID(self,Tin,Tout,Refin,Refout,kP=0.1,kI=0.05,kD=0.0,limit=345):
            ErrorIN = Tin - Refin
            
            ErrorOUT=  (Refin-Refout)- Tout 

            if np.isnan(ErrorIN) or np.isnan(ErrorOUT):
                pass
            else:
                CorIN = (ErrorIN*kP)  + (self.Prev_ErrorIN*kD)  + (self.Sum_ErrorIN*kI)
                CorOUT= (ErrorOUT*kP) + (self.Prev_ErrorOut*kD) + (self.Sum_ErrorOUT*kI)
                
                if np.isnan(CorIN) or np.isnan(CorOUT):
                    pass
                else:
                    self.Cin  += CorIN
                    self.Cout += CorOUT
                    
                    self.Prev_ErrorIN=ErrorIN
                    self.Prev_ErrorOut=ErrorOUT
                    
                    if self.Cin<limit or self.Sum_ErrorOUT<limit:
                        self.Sum_ErrorIN += ErrorIN
                        self.Sum_ErrorOUT += ErrorOUT
                    else:
                        if self.Cin*ErrorIN>0 or self.Cout*ErrorOUT*self.Cin*ErrorIN>0:
                            self.Sum_ErrorIN = 0
                            self.Sum_ErrorOUT = 0
                    
            self.Cin=max(min(self.Cin,limit),0)
            self.Cout=max(min(self.Cout,self.Cin),0)
            
            return self.Cin, self.Cout
         
    def dataCycle(self,ez=(1,2,3,4),pressure=(1,2,3,4,5,6,7,8),direction=1):
        self.setSensorData(ez,pressure)
        self.calcParameter(direction)
        self.moveFrame()

    def setSensorData(self,ez,pressure):
        try:
            self.PressureData=pressure
            self._PFeeder,self._PWaste,self._RP1,self._RP2,self._RP1a,self._RP2a,s7,s8=pressure
        except:
            self.PressureData=(0,0,0,0,0,0,0,8)
            self._PFeeder,self._PWaste,self._RP1,self._RP2,self._RP1a,self._RP2a,s7,s8=(np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan)
        try:
            self._PEZ1,self._PEZ2,self._Q,self._Q2=ez
        except:
            self._PEZ1,self._PEZ2,self._Q,self._Q2=(np.nan,np.nan,np.nan,np.nan)
    
    def calcParameter(self,direction):
        
        if self.RRef=="EZ":
            self._dpR1=self.PressureData[2]-self._PEZ1
            self._dpR2=self.PressureData[3]-self._PEZ2
            
        elif self.RRef=="MPR":
            self._dpR1=self.PressureData[2]-self.PressureData[4]#self._RP1-self._RP1a
            self._dpR2=self.PressureData[3]-self.PressureData[5]
        
        self._dpPF=self.PressureData[0]-self.PressureData[1]#self._PFeeder-self._PEZ1
        self._dpPW=self._PWaste-self._PEZ2
        self._dPsamp=self.PressureData[0]-self.PressureData[1]#self._PFeeder-self._PWaste
        
        Qs=self.dampData(self.listQ)/60
        
        dP= self.dampData(self.Pf,kernel=3)-self.dampData(self.Pw,kernel=3)
        
        try:
            self._Rhs=dP/Qs
        except:
            self._Rhs=99
            
        if direction == 1:
            self._dPi=self.dampData(self.pS1,kernel=3)-self.dampData(self.Pf,kernel=3)
            self._dPo=self.dampData(self.Pw,kernel=3)-self.dampData(self.pS2,kernel=3)
        elif direction == 2:
            self._dPi=self.dampData(self.pS2,kernel=3)-self.dampData(self.Pf,kernel=3)
            self._dPo=self.dampData(self.Pw,kernel=3)-self.dampData(self.pS1,kernel=3)
            
        try:
            self._Rhi=self._dPi/Qs
            self._Rho=self._dPo/Qs
        except:
            self._Rhi=99
            self._Rho=99
        
        self._tauA=0
        self._tauMin=0
        self._tauMax=0


    def fillTimeframe(self,length):
        z=datetime.datetime.now()
        t=np.ones(length,dtype='datetime64')
        for i in range(0,length):
            td = datetime.timedelta(seconds=0.01)
            t= np.delete(t,[0])
            t= np.append(t,(z-(length*td))+(i*td))
        return t
 
 
    def moveFrame(self):#_____________________________delete first entry
        #self.FramePressureData=np.delete(self.FramePressureData,0,axis=0)
        self.t  = np.delete(self.t,[0])
        self.listQ  = np.delete(self.listQ,[0])
        self.P1 = np.delete(self.P1,[0]) 
        self.P2 = np.delete(self.P2,[0])
        self.P1a = np.delete(self.P1a,[0]) 
        self.P2a = np.delete(self.P2a,[0])
        
        self.Pf=np.delete(self.Pf,[0])
        self.Pw=np.delete(self.Pw,[0])
        #self.dP=np.delete(self.dP,[0])
        self.pS1=np.delete(self.pS1,[0])
        self.pS2=np.delete(self.pS2,[0])
        self.dpR1= np.delete(self.dpR1,[0])
        self.dpR2= np.delete(self.dpR2,[0])
        self.dpPF= np.delete(self.dpPF,[0])
        self.dpPW= np.delete(self.dpPW,[0])
        self.Volume=np.delete(self.Volume,[0])
        #_______________________________________________________append new entry
        self.t  = np.append(self.t, self.tss)
        self.listQ  = np.append(self.listQ,self._Q )
        self.P1 = np.append(self.P1, self._PEZ1)
        self.P2 = np.append(self.P2, self._PEZ2)
        self.P1a = np.append(self.P1a, self._RP1a)
        self.P2a = np.append(self.P2a, self._RP2a)
        
        self.Pf = np.append(self.Pf,self.PressureData[0])#self._PFeeder)
        self.Pw = np.append(self.Pw,self.PressureData[1])#)
        

        self.pS1=np.append(self.pS1, self.PressureData[2])#self._RP1)
        self.pS2=np.append(self.pS2,self.PressureData[3])#self._RP2)
        self.dpR1= np.append(self.dpR1,self._dpR1)
        self.dpR2= np.append(self.dpR2,self._dpR2)
        self.dpPF= np.append(self.dpPF,self._dpPF)
        self.dpPW= np.append(self.dpPW,self._dpPW)
        self.Volume=np.append(self.Volume,self._dv)
        #print(self.PressureData,self.PressureData)
        
        #self.FramePressureData=np.append(self.FramePressureData,self.PressureData,axis=0)
        
    def dampData(self,dataframe,kernel=1,Hz=20): 
       k=int(kernel*Hz)
       datapoint= np.nanmedian(dataframe[-k:])
       return datapoint
   
    def dampPastData(self,dataframe,kernel=5,Hz=1,minutes=1): 
       test=ts-datetime.timedelta(minutes=minutes)
       past = (np.abs(T-test)).argmin()
       k=kernel*Hz
       datapoint=dataframe[(past-k):past]
       return datapoint
   
    def __str__(self):
        return "EZ1="+str(round(self._PEZ1,2))+ ", EZ2 ="+str(round(self._PEZ2,2))+ ", Q ="+str(round(self._Q,2))+", Pf ="+str(self._PFeeder)+", Pw ="+str(self._PWaste)+", PR1 ="+str(self._RP1)+ ", PR2 ="+str(self._RP2)
    
    def CreateLogFile(self,samplename,startTime):
        file_name="LogFiles/"+samplename+startTime.strftime("_%d%m%Y_%H%M")+".csv"
        with open(file_name,"w",newline='') as file:
            self.datalogger=csv.writer(file)
            self.datalogger.writerow(["time","P1", "P2","S5","S6",
                                      "S1", "S2","Pf","Pw","dP","pin",
                                      "Q","dpR1","dpR2","direction","Command In",
                                      "Rhi","Rhs","Rho","SwitchTime"])
        return file_name

    def WriteLogfile(self,filename,time,direction,interval=2,Hz=20):
        test=(time>self.nexttimestamp)
        
        if interval=="live":
            Q=self._Q
            P1=self._PEZ1
            P2=self._PEZ2
            P1a=self._RP1a
            P2a=self._RP2a
            Pf=self._PFeeder
            Pw=self._PWaste
            pin=(Pf+Pw)/2
            S1=self._RP1
            S2=self._RP2
            dP=self._dPsamp
            dpR1=self._dpR1
            dpR2=self._dpR2
            Rhi=self._Rhi
            Rhs=self._Rhs
            Rho=self._Rho
            SwitchTime=self.new_switch
            CIN=self.Cin
            
            with open(filename,"a",newline='') as file:
                self.datalogger=csv.writer(file)
                self.datalogger.writerow([time,P1, P2,P1a,P2a,
                                      S1, S2, Pf,Pw,dP,Q,dpR1,dpR2,direction,CIN,
                                      Rhi,Rhs,Rho,SwitchTime])
        else:
            if test:
                Q= self.dampData(self.listQ,interval,Hz=Hz)
                P1= self.dampData( self.P1,interval,Hz=Hz)
                P2= self.dampData(self.P2,interval,Hz=Hz)
                P1a=self.dampData(self.P1a,interval,Hz=Hz)
                P2a=self.dampData(self.P2a,interval,Hz=Hz)
                Pf= self.dampData(self.Pf,interval,Hz=Hz)
                Pw= self.dampData(self.Pw,interval,Hz=Hz)
                pin=(Pf+Pw)/2
                dP= Pf-Pw
                S1= self.dampData(self.pS1,interval,Hz=Hz)
                S2= self.dampData(self.pS2,interval,Hz=Hz)
                dpR1=self.dampData(self.dpR1,interval,Hz=Hz)
                dpR2=self.dampData(self.dpR2,interval,Hz=Hz)
                Rhi=self._Rhi
                Rhs=self._Rhs
                Rho=self._Rho
                SwitchTime=self.new_switch
                CIN=self.Cin
                self.nexttimestamp=time+datetime.timedelta(seconds=interval)
                
                
                with open(filename,"a",newline='') as file:    
                    self.datalogger=csv.writer(file)
                    self.datalogger.writerow([time,P1, P2,P1a,P2a,
                                      S1, S2, Pf,Pw,dP,pin,Q,dpR1,dpR2,direction,CIN,
                                       Rhi,Rhs,Rho,SwitchTime])
                    print("log with interval: ", interval)
                    
    def createSitreport(self,filename):
        with open(filename,"w",newline='') as file:
            self.datalogger=csv.writer(file)
            self.datalogger.writerow(["time","direction","duration",
                                      "Q","iqrQ",
                                      "dP","iqrdP","Pinternal",
                                      "Rhi","Rhs","Rho"])
        
    def SitRep(self,filename,Sitrep,target):
        target=str(target)
        data=pd.read_csv(filename)

        temp=data.loc[(data["SwitchTime"] == target)]
        Starttime=target
        duration=len(temp)
        direction=temp["direction"].iloc[0]
        Q=temp["Q"].median()
        Pdt=1
        iqrQ=iqr(temp["Q"])
        slope=4
        dP=temp["dP"].median()
        iqrdP=iqr(temp["dP"])
        slope=7
        Pin=temp["pin"].median()
        iqrdp=9
        slope=10
        Rhi=temp["Rhi"].median()
        Rhs=temp["Rhs"].median()
        Rho=temp["Rho"].median()
        with open(Sitrep,"a",newline='') as file:    
            self.datalogger=csv.writer(file)
            self.datalogger.writerow([Starttime,direction,duration,
                                      round(Q,2),round(iqrQ,2), round(dP,2),round(iqrdP,2),round(Pin,2),
                                      round(Rhi,2),round(Rhs,2),round(Rho,2)])

class reservoirs(mFCB):
    def __init__(self,V1=0,V2=0):
        self._v1 = V1
        self._v2 = V2
        self._TLL_R1=None
        self._TLL_R2=None
        self._injection_volume=1
        self._injected_volume=0
        self._direction= 1
        self.limitR1=1  
        self.limitR2=1

        self.switched_time=datetime.datetime.now()
      
    def __str__(self):
        return "Volume Reservoir one: " + str(self.Vone) + ", Volume Reservoir two: " + str(self.Vtwo) + "Low fluid level: "+ str(self._lwl)
    #setters________________________________________________
    def set_V1(self, newVone):
        self._v1 = newVone
    def set_V2(self, newVtwo):
        self._v2 = newVtwo

    def set_lwl1(self, newlwl):
        
        self._lwlR1 = newlwl
        print("Low level is changed to: ",self._lwlR1)
        
    def set_lwl2(self):
         
        self._lwlR2 = newlwl
        print("Low level is changed to: ",self._lwlR2)

    def set_Hwl1(self, newlwl):
        
        self._lwlR1 = newlwl
        print("High level is changed to: ",self._lwlR1)
        
    def set_Hwl2(self):
        #newlwl=self.
        self._lwlR2 = newlwl
        print("High level is changed to: ",self._lwlR2)

        
    def setDirection(self,change):
        self._direction= change

    def LeakDetection(self,R1,R2,LEAK,timestamp):
        V=R1+R2
     
        print(timestamp,self.switched_time,timestamp-self.switched_time,datetime.timedelta(seconds=5))
        
        test=(timestamp-self.switched_time)>datetime.timedelta(seconds=5)
        test2=V<LEAK
        test3=R1<self.limitR1 and R2<self.limitR2

        if test==True:
            if test3==True:
                self._direction = 0
        
        print(self._direction,"Direction")
                 
    def dpcheck_TLL(self,R1,R2,timestamp):
        old = self._direction
        self._TLL_R1= R1 > self.limitR1
        self._TLL_R2= R2 > self.limitR2
        print(self._TLL_R1,self._TLL_R2,R1,R2)
        test=(timestamp-self.switched_time)>datetime.timedelta(seconds=20)
        if test:
            if self._TLL_R1 == True and self._TLL_R2 == False:
                self._direction= 1
                self.switched_time=datetime.datetime.now()
            elif self._TLL_R1== False and self._TLL_R2== True:
                self._direction = 2
                self.switched_time=datetime.datetime.now()
        return old,self._direction
        
    def setInjectionV(self, target):
        self._injection_volume=target
    def setInjectedVolume(self,dv):
        """input: volume delta or 'reset'
            output: change total injection, 'reset:zero"""
        if dv=="reset" or  dv== "zero":
            self._injected_volume= 0
        else:    
            self._injected_volume += dv

    #getters_______________________________________________
    def get_V1 (self):
        return self._v1

    def get_V2 (self):
        return self._v2

    def get_lwl (self):
        return self._lwl

    
    def getDirection(self):
        return self._direction
    
    def getInjectionV(self):
        return self._injection_volume
    
    def getInjectedV(self):
        return self._injected_volume


    #________________________________________methods_______________________________________________


    def dPvolume(self):
        h=dP*1.01974428892
        return h

    def balanceReservoirs(self,flowrate,dt,direction):
        """ Input: flowratesensor, time difference between
            Output: volume of reservoirs"""
        if direction==2:
            flowrate*=-1
        dV=((flowrate/60)*(dt))/1000
        self.set_V1(self.get_V1()-dV)#Calculate volume R1
        self.set_V2(self.get_V2()+dV)#Calculate volume R2
       
        return dV
