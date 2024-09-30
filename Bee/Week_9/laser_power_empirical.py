import numpy as np
import sys
from lmfit.models import LinearModel
from matplotlib import pyplot as plt

# import data
path = sys.argv[1]
data = np.loadtxt(
        path)

# average data values
num_rows = int(len(data[:,1])/5)
mW_data = data[:,1].reshape(num_rows,5).mean(1)
pc_data = data[:,0].reshape(num_rows,5).mean(1)
data_avg = np.column_stack((pc_data.reshape(num_rows,1),mW_data.reshape(num_rows,1)))

# plot data points
fig, ax = plt.subplots()
ax.plot(data_avg[:,0],data_avg[:,1],'x',label='data')

# fit data to linear model
model = LinearModel()
result = model.fit(data_avg[:,1],x=data_avg[:,0])
print(result.fit_report(),'\n\n')

# save parameters to variables
m = result.params['slope'].value
c = result.params['intercept'].value
m_err = result.params['slope'].stderr
c_err = result.params['intercept'].stderr

# create new data set to plot a smoother line
xspace = np.linspace(0,100,21)
smooth_result = result.eval(x=xspace)
ax.plot(xspace, smooth_result, label = f'linear fit,\n$m$={m:.3f}+/-{m_err:.3f},\n$c$={c:.3f}+/-{c_err:.3f}')

# set up graph appearance
ax.set_xlabel('Power (%)')
ax.set_ylabel('Power (mW)')
ax.set_title('Power Calibration (100x/0.75NA lens)')
ax.legend()

plt.show()

# save output data
output_data = np.column_stack((xspace,smooth_result))
output_header = (' # Power(%) Power(mW)')
np.savetxt(r'power_calibration.txt',output_data,header=output_header)
print('Saved fitted parameters to power_calibration.txt')
