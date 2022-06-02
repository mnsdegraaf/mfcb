import math

class Calculator():
    def __init__(self):
        self.shear_stress=0
        self.pressure_vessel=0
        self.pressure_delta=0
        self.pressure_setting=0
        
    def ShearStress(entry_shear,entry_pressure,TEQ,l=0.0105,dmin=180,dmed=230,u=0.00072):
        
        d=(dmin+dmed)/2
        d=d*1E-6
        
        try:
            Target_WSS=float(entry_shear)
            Target_IP=float(entry_pressure)  
        except:
            print("NaN")
    
        dP= (Target_WSS*((4*l/d)+((math.pi*d**3)/(32*u))*TEQ))
        Pin= round(Target_IP+(dP/200),1)
        Pout= round(Target_IP-((dP/200)),1)

        if (Pin < 0 or Pout < 0):
            Pin=0
            Pout=0            
            print("Setting Not Possible")
      
        return (Pin,Pout)

    def dP(entry_dP,entry_pressure):
        
        try:
            Target_dP=float(entry_dP)
            Target_IP=float(entry_pressure)  
        except:
            print("NaN")
    
        Pin= round(Target_IP+(Target_dP/2),1)
        Pout= round(Target_IP-((Target_dP/2)),1)

        if (Pin < 0 or Pout < 0):
            Pin=0
            Pout=0            
            print("Setting Not Possible")
        return(Pin,Pout)
    def dPAndPres(self,entry_inlet,entry_outlet):
         try:
           entry_inlet=float(entry_inlet)
           entry_outlet=float(entry_outlet)  
         except:
           print("NaN")
           
         dP= (entry_inlet-entry_outlet)
       
         Pressure = (entry_inlet+entry_outlet)/2
         return(dP,Pressure)
          
    def dPtoVolume(dp):
        V=0.8*dp
        return V
    
    def ShearAndPres(self,entry_inlet,entry_outlet,TEQ,l=0.0105,dmin=180,dmed=230,u=0.00072):
        d=(dmin+dmed)/2
        d=d*1E-6
        dP= (entry_inlet-entry_outlet)*100
        Shear= dP/((4*l/d)+((math.pi*d**3)/(32*u))*TEQ)
        Pressure = (entry_inlet+entry_outlet)/2
        return(Shear,Pressure)
        
        print("Display parameters")
        
    def calculate_wss(self,d,l,TEQ,dP_Pa):
        WSS= dP_Pa/((4*l/d)+((math.pi*d**3)/(32*0.0072))*TEQ)
        return WSS
         
class ref_commands():
    def __init__(self):
        self.ref_dict=dict()
        
