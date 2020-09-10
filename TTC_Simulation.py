
# Option 2: solve model with ODEINT
from scipy.integrate import odeint
import numpy as np
import math
import matplotlib.pyplot as plt
import shapely.geometry as SG
import os
import glob
from PIL import Image
import imageio


#dir is not keyword
def makemydir(whatever):
  try:
    os.makedirs(whatever)
  except OSError:
    pass
  # let exception propagate if we just can't
  # cd into the specified directory
  os.chdir(whatever)

def get_a(heli_vel_in_kt,ship_vel_in_kt,dist_heli_ship_in_nm,alt_in_ft,el,seconds,deceleration):

  #initialize array of seconds to be used as x-axis
  t = np.array(range(seconds))
  #convert to meters
  dist_heli_ship_in_nm*=1852
  #convert to m/s
  Vx=heli_vel_in_kt*0.514
  Vs=ship_vel_in_kt*0.514

  #array of velocities after desceleration
  V=Vx-deceleration*t


  #change all -ve velocities to 0
  ind=0
  for v in V:
    if v<=0:
      V[ind]=0
    ind+=1  

 

  #calculate horizontal distance between the ship and the helicopter over time
  dist=dist_heli_ship_in_nm-((t*Vx+0.5*-deceleration*(t*t))-t*Vs)

 #calculate altitude over seconds: will result in an array of the same values if elevation angle is 0  
  z=alt_in_ft*0.3048-((t*Vx+0.5*-deceleration*(t*t)))*math.tan(math.radians(el))
  ind=0
  for z1 in z:
    if ind<len(z)-1:
      if z[ind+1]>z1:
        z[ind+1]=z1
      ind+=1

  # print(z)

  #calculate angle between the helicopter and ship over time
  ang=np.empty(seconds)
  ind=0
  makemydir('new')
  images = []
  ds=0
  plt.xlabel('distance (Eye-Heights)')
  plt.ylabel("Angular velocity (min of arc/sec)")
  for t0 in t:
    q=-(t[ind]*Vx+0.5*-deceleration*(t[ind]**2))
    # print('q= ',q,'ds= ',ds)
    if deceleration*t[ind]>Vx:
      q=ds
    else:
      ds=q
    q+=dist_heli_ship_in_nm 
    plt.clf()
    plt.plot([q],[z[ind]],'ro')
    plt.plot([-t[ind]*Vs],[1],'bo')
    plt.plot([-t[ind]*Vs,q],[1,z[ind]],"k:")
    plt.xlabel("Nautical Miles")
    
    plt.axis([-dist_heli_ship_in_nm, dist_heli_ship_in_nm, 0, 2*alt_in_ft*0.3048])
    v_kt=(round(V[ind],2))
    v_eh=str(v_kt/z[ind])
    
    v_kt=str(round(v_kt/0.514,2))
    plt.legend(['alt= '+str(round(z[ind]/0.3048,2))+'ft\nvel= '+v_kt+'kt ('+v_eh+' eh/s)'+'\n'+'dist= '+str(round(dist[ind]/1852,2))+'Nautical Miles\nttc='+str(round(dist[ind]/(V[ind]-Vs),2))+'s'] )
    # plt.show()
    filename='image_'+str(ind)+'.png'
    plt.savefig(filename)
    ind+=1  
    images.append(imageio.imread(filename))
  imageio.mimsave('./movie.gif', images)
  ind=0
  for a in dist:
    ang[ind]=math.degrees(np.arctan((z[ind]/a))) 
    ind+=1
    
  # ax.plot(t,z)
  return [t,V,z,ang,dist] 
 

def get_angular_velocity_over_distance(heli_vel,ship_vel,z,el,y0,dist):

  #relative horizontal velocity between helicopter and ship
  vel_relative=(heli_vel-ship_vel)

  #relative horizontal velocity in eye-heights
  vel_eh=vel_relative/z

  #range of distance to be used on the x-axis
  x = np.array(range(len(heli_vel)))

  #calculate angular velocity over distance
  # print('z ',z,'x ',x,'el', el )
  
  el=el*0
    
  s=(z/np.sqrt((x**2+z**2)))*np.cos(np.radians(el))
  c=(x/np.sqrt((x**2+z**2)))*np.sin(np.radians(el))
  El_dot=60*(vel_relative/z)*((s-c)**2)


 
  #get distance in front of the helicopter where angular velocity of y0 is achieved
  plt.clf()
  y0=40
  ymin, ymax = ax.get_ylim() 

  line=SG.LineString(list(zip(x,El_dot)))
  yline=SG.LineString([(min(x),y0),(max(x),y0)])
  coords=0
  if len(np.array(line.intersection(yline)))!=0:
    coords =np.array(line.intersection(yline))[0]
  plt.axhline(y=y0,color='k' ,linestyle=':')
  plt.axvline(x=coords,ymax=y0/ymax,color='m',linestyle=':')


  #calculate time-to-contact
  ttc=np.empty(len(heli_vel))
  ind=0
  for a in ttc:
    a=(x[ind]/(vel_relative[ind]/z[ind]))
    ttc[ind]=a
    if vel_relative[ind]==0:
      ttc[ind]='infinity'
    ind+=1

  plt.legend(['40 min of arc/sec='+str(round(coords,2))+'eh\nlookahead time='+str(round(coords*z[0]/vel_relative[0],2))+'s'])

  plt.xlabel('distance (Eye-Heights)')
  plt.ylabel("Angular velocity (min of arc/sec)")
  plt.plot(x,El_dot,label=coords,color='r')
  filename='image_'+str('f')+'.png'
  plt.savefig(filename)
  return [x,El_dot,round(coords,2),ttc]


 
# soap=[[2000,1500,2],[1500,1500,2],[1500,300,1]]
# angles=[]
# for stage in soap:
#   angle=(math.degrees(np.arctan((stage[0]-stage[1])*0.3048/(stage[2]*1852))))
#   angles.append(round(angle,2))
# print (angles) 

y0=40
fig, ax=plt.subplots()

def plot(heli_vel,ship_vel,dist,alt,el,sec,dec,y0,c):
  a=get_a(heli_vel,ship_vel,dist,alt,el,sec,dec)
  t=a[0]
  v=a[1]
  z=a[2]
  ang=a[3]
  dist=a[4]
  b=get_angular_velocity_over_distance(v,ship_vel,z,ang,y0,dist)
  x=b[0]
  El_dot=b[1]
  coords=b[2]
  ttc=b[3]
  
  #  print(ymin)
  return [coords,ttc]
# (heli_vel,ship_vel,dist,alt,el ,sec,dec,y0,c)
a=plot(60  ,  20      ,0.3,200 ,4,100,0.3,40,'m')

plt.show()
