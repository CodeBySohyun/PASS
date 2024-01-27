import numpy as np
import matplotlib.pyplot as plt
import sys
from lmfit.models import QuadraticModel
from uncertainties import ufloat
from matplotlib import use
# Save for latex
#use("pgf")
#plt.rcParams.update({
#    "pgf.texsystem" : "pdflatex",
#    "pgf.preamble" : "\n".join([
#        r"\usepackage[utf8x]{inputenc}"
#        ]),
#    'font.family' : 'serif',
#    'text.usetex' : True,
#    'pgf.rcfonts' : False,
#    })

#create lists for output and input
list_of_max_L = []
path_list = []
list_of_lengths = sys.argv[1:]

drop = 0

#parse each list of lengths to find maximum distance fallen 
for i in list_of_lengths:
    drop += 1
    # set up graphs
    plt.figure(figsize=(3.5,4))
    plt.xlabel('Frame No.')
    plt.ylabel('Height (cm)')

    lengths = np.loadtxt(i,unpack = True)
    
    #list of y and x vals for each drop
    y = (lengths[0] + lengths[1])/2
    x = np.arange(0,len(y))
    
    #parse filename
    path = str(i).removeprefix(r'.\Parabolas\air')
    path.removeprefix(r'\\')
    gas = path.split('_')[1]

    #fit curve to x and y vals
    model = QuadraticModel()
    params = model.guess(y, x=x)
    fit = model.fit(y,params,x=x)
    print('Eval\n',fit.eval())
    print(fit.values, fit.fit_report())
    print('-------------------')
    print(fit.params['a'].value, fit.params['a'].stderr)

    xspace = np.linspace(0,len(y),100)
    yspace = fit.eval(x=xspace)
    points, = plt.plot(x,y,'o')
    line, = plt.plot(xspace, yspace,'-',color = points.get_color())
    #make ufloats from fit params
    a, b, c = fit.params['a'].value, fit.params['b'].value, fit.params['c'].value
    aerr, berr, cerr = fit.params['a'].stderr, fit.params['b'].stderr, fit.params['c'].stderr
    ua = ufloat(a, aerr)
    ub = ufloat(b, berr)
    uc = ufloat(c,cerr)

    #calculate max fall distance
    xmax = -ub/(2*ua)
    ymax = ua*(xmax**2)+ub*(xmax)+uc
    list_of_max_L.append(ymax)
    path_list.append(path)

    Lmaxhack, = plt.plot(xmax.nominal_value, ymax.nominal_value, 'x', color = points.get_color())
    Lmax = plt.errorbar(xmax.nominal_value, ymax.nominal_value, xerr=xmax.std_dev, yerr=ymax.std_dev, fmt='x', color = points.get_color())
    #plt.text(xmax.nominal_value,ymax.nominal_value,f'({xmax},{ymax})')
    plt.legend([(points,line),Lmaxhack],[f'{gas}: drop {drop}',f'$L$={ymax.nominal_value:.2f} cm $\pm${ymax.std_dev:.2f} cm'])
  #  plt.savefig(f'{gas}{drop}parabola.pgf',bbox_inches='tight')
    plt.show()

    #plot label = f'$L$={xmax.nominal_value:.2f} cm $\pm${xmax.std_dev:.2f} cm', label=f'{gas}: drop {drop}',


L_arr = np.array(list_of_max_L)
path_arr = np.array(path_list)

output = np.column_stack((path_list,list_of_max_L))
print(output)
np.savetxt(f'output.txt',output,fmt='%s')

# run python3 parabola_fit.py 20221128T1221_air_36_c.txt
# if u uncomment lines 9-17 and 75, that should save a pgf