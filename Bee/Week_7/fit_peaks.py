#!/usr/bin/python
import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.backend_bases import MouseButton
from lmfit.models import ConstantModel, VoigtModel
from scipy.signal import find_peaks

import calibration_model


class SpectrumFitter:
    # User selected left and right pixel numbers of peak
    peak_left = 0
    peak_right = 0
    # Peak being displayed, start at -1, so first 'Next' goes to 0.
    current_peak = -1
    # Model to use for fitting peaks
    model = ConstantModel() + VoigtModel()

    def __init__(self, spectrum_path, fitted_params_path):
        """
        Args:
            spectrum_path: str, path to SpectraSuite tab separated value file
            fitted_params_path: str, location that fitted parameters should
                be saved to on exit.
        """
        # Get intensity column from SpectraSuite file
        # Number of header lines in the file
        num_header_lines = 17
        # Number of lines in the file
        num_lines = 3666
        self.I = np.loadtxt(
            spectrum_path,
            skiprows=num_header_lines,
            # Intensity is column 1 (0 indexed)
            usecols=1,
            # Don't use last line, which is a footer
            max_rows=num_lines - num_header_lines - 1,
        )
        # Pixel numbers is the indices of the intensity array
        self.pix = np.arange(self.I.size)
        # Get approximate pixel of peak
        # TODO: make min height selectable
        self.peak_pix, peak_properties = find_peaks(self.I, 1090)
        # Array of fitted parameters for each peak
        fitted_params_header = (
            'center center_stderr amplitude amplitude_stderr '
            'sigma sigma_stderr c c_stderr wavelength_nm'
        )
        self.fitted_params = np.zeros((self.peak_pix.size, 9))

        # Plot data around peak, and let self.peak_left and self.peak_right limits of peak be
        # selected graphically.
        self.fig, self.ax = plt.subplots()
        # Leave room for buttons
        self.fig.subplots_adjust(bottom=0.2)
        self.ax.set_xlabel('Pixel')
        self.ax.set_ylabel('Intensity')
        self.ax.plot(
            self.pix,
            self.I,
            'x-',
            # Allow points to be picked
            picker=True
        )
        # Mark found peaks
        self.ax.plot(self.pix[self.peak_pix], self.I[self.peak_pix], 'o')
        
        # Buttons to move between peaks, adapted from matplotlib docs
        axprev = self.fig.add_axes([0.7, 0.05, 0.1, 0.075])
        axnext = self.fig.add_axes([0.81, 0.05, 0.1, 0.075])
        prev_button = Button(axprev, 'Previous')
        next_button = Button(axnext, 'Next')
        prev_button.on_clicked(lambda e: self.change_peak(-1))
        next_button.on_clicked(lambda e: self.change_peak(+1))
        # When a point is picked set that as a limit of the peak
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        plt.show()

        # Save fitted parameters to file
        np.savetxt(
            fitted_params_path,
            # Get rid of zero rows (unfitted peaks)
            self.fitted_params[np.all(self.fitted_params != 0, axis=1)],
            header=fitted_params_header,
        )
        print(f'Saved fitted parameters to {fitted_params_path}')

    def refresh(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def change_peak(self, change):
        self.current_peak += change
        if self.current_peak < 0:
            self.current_peak = 0
        elif self.current_peak >= self.peak_pix.size:
            self.current_peak = self.peak_pix.size - 1

        center = self.peak_pix[self.current_peak]
        # Plot +/- hr pixels either side of center
        hr = 20
        self.ax.set_xlim(center - hr, center + hr)
        self.ax.set_ylim(
            # Minimum intensity in plotted range - padding
            np.amin(self.I[center-hr:center+hr]) - 10,
            # Peak intensity + padding
            self.I[center] + 10,
        )
        self.ax.set_title(
            f'Peak {self.current_peak + 1} of {self.peak_pix.size}'
        )
        self.refresh()

    def onpick(self, event):
        if isinstance(event.artist, Line2D):
            # Pixel number the picked point is the index of the point
            pix = event.ind[0]
            if event.mouseevent.button is MouseButton.LEFT:
                # Remove old line
                try:
                    self.left_artist.remove()
                except AttributeError:
                    pass
                # Draw vertical line at picked pixel number
                self.left_artist = self.ax.axvline(pix, color='green')
                self.peak_left = pix
            elif event.mouseevent.button is MouseButton.RIGHT:
                try:
                    self.right_artist.remove()
                except AttributeError:
                    pass
                self.right_artist = self.ax.axvline(pix, color='red')
                self.peak_right = pix
            else:
                return
            self.refresh()
        # If a valid range less than 100 pixels wide is selected, fit a peak
        if 0 < self.peak_right - self.peak_left < 100:
            self.fit_peak()

    def fit_peak(self):
        # Approximate center of peak from find_peaks
        approx_center = self.peak_pix[self.current_peak]
        # Intensities of selected region
        I_subset = self.I[self.peak_left:self.peak_right]
        result = self.model.fit(
            I_subset,
            x=self.pix[self.peak_left:self.peak_right],
            c=np.amin(I_subset),
            amplitude=self.I[approx_center],
            center=approx_center,
            sigma=1,
        )
        print(result.fit_report(), '\n\n')
        # Save fitted parameters
        self.fitted_params[self.current_peak] = (
            result.params['center'].value,
            result.params['center'].stderr,
            result.params['amplitude'].value,
            result.params['amplitude'].stderr,
            result.params['sigma'].value,
            result.params['sigma'].stderr,
            result.params['c'].value,
            result.params['c'].stderr,
            calibration_model.model.eval(
                x=result.params['center'].value,
                params=calibration_model.params,
            ),
        )

        # Remove old fitted line
        try:
            self.fit_artist.pop(0).remove()
        except AttributeError:
            pass
        # Plot smooth fitted line
        lots_pix = np.linspace(self.peak_left, self.peak_right, 1000)
        self.fit_artist = self.ax.plot(
            lots_pix,
            result.eval(x=lots_pix),
            color='orange',
        )
        self.refresh()


spectrum_path = sys.argv[1]
fitted_params_path = sys.argv[2]
fitter = SpectrumFitter(spectrum_path, fitted_params_path)
