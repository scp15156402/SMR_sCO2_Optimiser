# Independent check: no solver code, only CoolProp + scipy.
from CoolProp.CoolProp import PropsSI as P
import numpy as np
from scipy.optimize import brentq
f='CO2'; Ph,Pl=20e6,7.7e6; T1=305.15; T4=773.15; ec,et,eps=0.89,0.90,0.90
h1=P('H','T',T1,'P',Pl,f); s1=P('S','T',T1,'P',Pl,f)
h2=h1+(P('H','P',Ph,'S',s1,f)-h1)/ec
h4=P('H','T',T4,'P',Ph,f); s4=P('S','T',T4,'P',Ph,f)
h5=h4-et*(h4-P('H','P',Pl,'S',s4,f))
T2=P('T','P',Ph,'H',h2,f); T5=P('T','P',Pl,'H',h5,f)
qmax=min(h5-P('H','T',T2,'P',Pl,f), P('H','T',T5,'P',Ph,f)-h2)
q=eps*qmax; h3=h2+q; h6=h5-q
eta=((h4-h5)-(h2-h1))/(h4-h3); mdot=100e6/(h4-h3)
def ua(hc0,hh0,Q,Pc,Phh,fc,fh,mc,mh,n):
    x=np.linspace(0,1,n+1)
    Tc=np.array([P('T','P',Pc,'H',hc0+xi*Q/mc,fc) for xi in x])
    Th=np.array([P('T','P',Phh,'H',hh0+xi*Q/mh,fh) for xi in x])
    d=Th-Tc; lm=np.where(abs(d[1:]-d[:-1])<1e-9,(d[1:]+d[:-1])/2,(d[1:]-d[:-1])/np.log(d[1:]/d[:-1]))
    return (Q/n/lm).sum(), d.min()
UAr,pr=ua(h2,h6,q*mdot,Ph,Pl,f,f,mdot,mdot,1000)
print('eta %.7f  mdot %.3f  recup UA %.2f kW/K pinch %.4f'%(eta,mdot,UAr/1e3,pr))
Qc=mdot*(h6-h1); Pw=6e5; hw=P('H','T',298.15,'P',Pw,'Water')
g=lambda mw: ua(hw,h1,Qc,Pw,Pl,'Water',f,mw,mdot,400)[1]-5.0
T6=P('T','P',Pl,'H',h6,f)
lo=Qc/(P('H','T',T6-0.01,'P',Pw,'Water')-hw); hi=Qc/(P('H','T',298.65,'P',Pw,'Water')-hw)
mw=brentq(g,lo,hi,xtol=1e-9)
UAc,pc=ua(hw,h1,Qc,Pw,Pl,'Water',f,mw,mdot,1000)
print('cooler duty %.3f MW  water %.1f kg/s  out %.2f C  UA %.2f kW/K pinch %.4f'%(Qc/1e6,mw,P('T','P',Pw,'H',hw+Qc/mw,'Water')-273.15,UAc/1e3,pc))
print('T2 %.2f T3 %.2f T5 %.2f T6 %.2f C'%(T2-273.15,P('T','P',Ph,'H',h3,f)-273.15,T5-273.15,T6-273.15))
