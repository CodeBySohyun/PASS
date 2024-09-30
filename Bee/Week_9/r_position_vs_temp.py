import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import uncertainties 
from uncertainties import unumpy as unp
import numpy as np
import sys
from scipy import constants
from pynverse import inversefunc
###                           STANDARD SETUP STUFF

#define Bose_Einstein
def Bose_Einstein(T,omega):
    return (1/(unp.exp(constants.h*constants.c*100*omega/(T*constants.k))-1))
# def empirical fit
def cui(T,w0,A,B):
    return w0 - A/(unp.exp(B*constants.h*constants.c*w0/constants.k/T)-1)
# define inverse empirical fit
def empirical_inverse(w,w0,A,B):
    return B*constants.h*constants.c*w0/(constants.k*(unp.log((w-w0-A)/(w-w0))))
# load data
num_cols = 16
converters = dict.fromkeys(
        range(num_cols),
        lambda col_bytes: uncertainties.ufloat_fromstr(col_bytes.decode("latin1")))
path = sys.argv[1]
data = np.loadtxt(
        path,
        converters = converters,
        dtype = object,
)
plt.rcParams.update({"pgf.texsystem" : "pdflatex","pgf.preamble" : "\n".join([r"\usepackage[utf8x]{inputenc}"]),'font.family' : 'serif','text.usetex' : True,'pgf.rcfonts' : False,})
###                             SET UP FIGURES
fig_pos, ax_pos = plt.subplots() # position
fig_s,ax_s = plt.subplots()      # shift vs position
fig_as, ax_as = plt.subplots()   # avg shift vs position
fig_w,ax_w = plt.subplots()      # width vs position
fig_aw, ax_aw = plt.subplots()   # avg width vs position
fig_t, ax_t = plt.subplots(figsize=(3.5,4.5))     # temp vs position

###                           POSITION CALIBRATION
# load calibration file
calibration_path = r'SiC_distance_measurements.csv'
pos = [0,0]
ref, pos[0],pos[1] = np.loadtxt(calibration_path,delimiter=',',usecols=(0,3,4),unpack = True)
pos_arr = np.array(pos).transpose()
# create dictionary of reference and [x,y] position
pos_dict = {
        ref[0]:pos_arr[0],
        ref[1]:pos_arr[1],
        ref[2]:pos_arr[2],
       # ref[3]:pos_arr[3],
       # ref[4]:pos_arr[4],
        #ref[5]:pos_arr[5],
        #ref[6]:pos_arr[6],
        #ref[7]:pos_arr[7],
        #ref[8]:pos_arr[8],
        }

###                       DEFINING VARIABLES
# values from fit (Si)
#w0 = uncertainties.ufloat(523.524935,0.02555493)
#Ap = uncertainties.ufloat(13.6160789,0.29373615) 
#Bp = uncertainties.ufloat(0.69232041*100,0.01075106*100)
#values from fit(SiC)
w0 = uncertainties.ufloat(967.573434,0.02157779)
Ap = uncertainties.ufloat(34.4397838,0.71948662)
Bp = uncertainties.ufloat(0.68995795*100,0.00759793*100)
# values from fit (Si)
#w1 = uncertainties.ufloat(341.042837,92.6346786)
#Aw = uncertainties.ufloat(0.89352131,0.89116398)
#Bw = uncertainties.ufloat(0.32954413,0.10829548)
#G0 = uncertainties.ufloat(0.10071560,0.31196640)
# values from fit (SiC)
w1 = uncertainties.ufloat(414.141333,14.4836264)
w2 = uncertainties.ufloat(414.141333,14.4836264)
Aw = uncertainties.ufloat(2.95588286,0.34030298)
Bw = uncertainties.ufloat(0.04406323,0.03459878)
G0 = uncertainties.ufloat(5.9711e-06,0.01004996)
# define inverse width function
width_func = lambda T: unp.nominal_values(G0) +  unp.nominal_values(Aw)*(1+2/(np.exp(constants.h*constants.c*100* unp.nominal_values(w1)/T/constants.k)-1))+ unp.nominal_values(Bw)*(1+3*1/(np.exp(constants.h*constants.c*200* unp.nominal_values(w1)/3/T/constants.k)-1)+3*(1/(np.exp(constants.h*constants.c*200* unp.nominal_values(w1)/3/T/constants.k)-1)**2))
inv_width_func = inversefunc(width_func,domain=[100,400])
# room temperature offset
room_temp_shift_cui = cui(T=273.15+25,w0=w0,A=Ap,B=Bp)
# Si room_temp_shift_correction = uncertainties.ufloat(520.6094215780528,0.003429310263997019)
room_temp_shift_correction = uncertainties.ufloat(965.4944442526472,0.1381608856929722)

###                       MAPPING POSITION
# set up figure
ax_pos.errorbar(pos_arr[:,0],pos_arr[:,1],fmt='x',xerr=50,yerr=50)
# label each point
for i,txt in enumerate(ref):
    ax_pos.add_patch(plt.Circle((pos_arr[i,0],pos_arr[i,1]),50, fill=False))
    ax_pos.annotate(f'Position {txt:.0f}', (pos_arr[i,0]+5,pos_arr[i,1]+5))
#plt.show()

###                   SIMPLIFYING Y POS DATA ARRAY
data_y = data
data_y_10v = []
data_y_15v = []
data_y_20v = []
for i in range(len(data_y)):
    voltage = int(unp.nominal_values(data_y[i,1]))
    #print(pos_dict[int(unp.nominal_values(data_y[i,0]))])
    data_y[i,0] = np.sqrt( (pos_dict[int(unp.nominal_values(data_y[i,0]))][1])**2 + (pos_dict[int(unp.nominal_values(data_y[i,0]))][0])**2 )
   # print(data_y[i,0])
    if voltage == 10:
        data_y_10v.append([data_y[i,:]])
    elif voltage == 15:
        data_y_15v.append([data_y[i,:]])
    elif voltage == 20:
        data_y_20v.append([data_y[i,:]])
    else:
        print('ERROR NOT EQUAL TO EXPECTED VOLTAGE')
data_y_10v = np.array(data_y_10v).reshape(len(data_y_10v),16)
data_y_15v = np.array(data_y_15v).reshape(len(data_y_15v),16)
data_y_20v = np.array(data_y_20v).reshape(len(data_y_20v),16)

###                      MAIN LOOP
data_list = [data_y_10v, data_y_15v, data_y_20v]
labels = {
        0 : '10V',
        1 : '15V',
        2 : '20V'
}
colours = {
        0 : 'C0',
        1 : 'C1',
        2 : 'C2'
}
label_V = 0
for i in data_list:
    # plot shift vs position
    ax_s.errorbar(unp.nominal_values(i[:,0]),unp.nominal_values(i[:,6]),yerr=unp.std_devs(i[:,6]),fmt='x',label=labels[label_V])
    # set up averaging
    position = i[0,0]
    shift = 0
    runs = 0
    output = []
    # average peak pos for same pos
    for j in range(len(i)):
        if i[j,0] == position:
            shift += i[j,6]
            runs += 1
        elif i[j,0] != position:
            avg = shift/runs
            output.append([position,avg])
            position = i[j,0]
            shift = i[j,6]
            runs = 1
    # create array of average peak pos values and plot
    k = np.array(output)
    p=unp.nominal_values(k[:,0])
    y= unp.nominal_values(k[:,1])
    ax_as.errorbar(p,y,yerr=unp.std_devs(k[:,1]),fmt='x',label=labels[label_V])
    # inverse function to find temperature from raman shift, correcting using room temperature offset
    yp = empirical_inverse(
               w=(room_temp_shift_cui-(room_temp_shift_correction-k[:,1])),
               w0=w0,
               A=Ap,
               B=Bp)
    # plot temperature using peak shift
    ax_t.errorbar(p,unp.nominal_values(yp),fmt='o',color=colours[label_V])#,yerr=unp.std_devs(yp))
    # plot width vs position
    ax_w.errorbar(unp.nominal_values(i[:,0]),unp.nominal_values(i[:,13]),yerr=unp.std_devs(i[:,13]),fmt='x',label=labels[label_V])
    # set up averaging
    position = i[0,0]
    width = 0
    runs = 0
    output = []
    # average width for same pos
    for j in range(len(i)):
        if i[j,0] == position:
            width += i[j,13]
            runs += 1
        elif i[j,0] != position:
            avg = width/runs
            output.append([position,avg])
            position = i[j,0]
            width = i[j,13]
            runs = 1
    # create array of average width values and plot
    k = np.array(output)
    p=unp.nominal_values(k[:,0])
    y= unp.nominal_values(k[:,1])
    ax_aw.errorbar(p,y,yerr=unp.std_devs(k[:,1]),fmt='x',label=labels[label_V])
    # temperature from widths
    # inverse function to find temperature from width
    yp = inv_width_func(y)
    y_up = inv_width_func(y + unp.std_devs(k[:,1]))
    y_lo = inv_width_func(y - unp.std_devs(k[:,1]))
    # plot temperature using width
    ax_t.errorbar(p,yp,fmt='^',color=colours[label_V])#,yerr=y_up/2-y_lo/2)
    # change voltage
    label_V += 1

### AXES SETUP
# position axes setup
ax_pos.set_xlim(right=390)
ax_pos.set_xlabel('x-position ($\mu$m)')
ax_pos.set_ylabel('y-position ($\mu$m)')
ax_pos.set_title('Position of measured points relative to TLM')
# shift axes setup 
ax_s.set_xlabel('Distance from TLM ($\mu$m)')
ax_s.set_ylabel('Raman Shift (cm-1)')
ax_s.set_title('Raman Shift at distances away from TLM')
ax_s.legend()
# average shift axes setup
ax_as.set_xlabel('Distance from TLM ($\mu$m)')
ax_as.set_ylabel('Raman Shift (cm-1)')
ax_as.set_title('Average Shift of Raman Peak against Position')
ax_as.legend()
# width axes setup
ax_w.set_xlabel('Distance from TLM ($\mu$m)')
ax_w.set_ylabel('Peak Width (cm-1)')
ax_w.set_title('Peak Width at distances away from TLM')
ax_w.legend()
# avergae width axes setup
ax_aw.set_xlabel('Distance from TLM ($\mu$m)')
ax_aw.set_ylabel('Peak Width (cm-1)')
ax_aw.set_title('Average Peak Width against Position')
ax_aw.legend()
# temperature axes setup
ax_t.set_ylim()
#ax_t.set_title('Temperature dependence on position')
ax_t.set_xlabel('Distance from TLM ($\mu$m)')
ax_t.set_ylabel('Temperature (K)')
label = [
        Line2D([0],[0],marker='o',color='w',label='Raman shift',markerfacecolor='grey',markersize=10),
        Line2D([0],[0],marker='^',color='w',label='Peak width',markerfacecolor='grey',markersize=10),
        Line2D([0],[0], color='w'),
        Line2D([0],[0], color='C0',lw=5, label='10V'),
        Line2D([0],[0], color='C1',lw=5, label='15V'),
        Line2D([0],[0], color='C2',lw=5, label='20V')
]
ax_t.legend(handles=label,ncols=2)
plt.savefig(f'SiC_temp_v_pos_no_err.pgf',bbox_inches='tight')
plt.show()
