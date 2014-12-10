#!/usr/bin/env python
print 'starting up'
import par
if par.use_mpi:
    from mpi4py import MPI as mpi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import healpy as hp
from scipy.constants import degree, arcmin, arcsec
import pickle
import os
import sys
import pylab
from planckcolors import colombi1_cmap
import mollview_hpcp as mv

if par.use_mpi:
    rank = mpi.COMM_WORLD.Get_rank()
    nproc = mpi.COMM_WORLD.Get_size()
else:
    rank = 0
    nproc = 1

base_step = sys.argv[1]
current_step = rank + int(base_step)
print 'rank %d of %d processing %d'%(rank, nproc, current_step)

# Predefined, official Planck colormap
cmap = colombi1_cmap
# Horizontal resolution of an individual map image
xsize = 1200
# Gaussian smoothing kernel width to smooth out small scale white noise
# structure
fwhm = 60 * arcmin
# expansion order of the map when applying the smoothing kernel. About 4 times
# fwhm in arcmin is sufficient
lmax = 512
# Resolution of the map after smoothing. Number of Healpix pixels is 12 x
# nside^2
nside = 256
# there are 9 frequencies on Planck in total
freqs = 30, 44, 70, 100, 143, 217, 353, 545, 857
# These are the plotting amplitudes and need be re-adjusted if the plotting
# resolution (nside) or smoothing kernel width (fwhm) change
amps = {
    30 : 10,
    44 : 10,
    70 : 10,
    100 : 3,
    143 : 3,
    217 : 3,
    353 : 10,
    545 : 1e-2,
    857 : 1e-2,
    }

real_batch = current_step / 100

dpi = 96
layouts = \
    { '1080p' : {'res':[1920, 1080], 'label_font_size':18, 'title_font_size':24, 'cbar_fraction':0.08, 'margins':[0.0, 0.0, 0.0, 0.0], 'axes':[0.0, 0.05, 1.0, 0.9]},
      '720p' : {'res':[1280, 720], 'label_font_size':16, 'title_font_size':22, 'cbar_fraction':0.08, 'margins':[0.0, 0.0, 0.0, 0.0], 'axes':[0.0, 0.05, 1.0, 0.89]},
      '480p' : {'res':[720, 480], 'label_font_size':14, 'title_font_size':20, 'cbar_fraction':0.08, 'margins':[0.0, 0.0, 0.0, 0.0], 'axes':[0.015, 0.05, 0.97, 1.2]} }

# loop over Planck frequencies
for ifreq, freq in enumerate( freqs ):
    for layout in layouts.itervalues():

        # file names for the input high resolution FITS map and an optional
        # downgraded and smoothed version of the same map (when save_lowres is
        # enabled)

        fn_hires \
            = '/project/projectdirs/planck/data/ffp8/mc_noise/{:03}/{:03}_{:02}/ffp8_noise_{:03}_full_map_mc_{:05}.fits'.format( \
               freq, freq, real_batch, freq, current_step )

        # Read the map from the appropriate Monte Carlo directory.
        map = hp.read_map( fn_hires )
        # Remove a global offset from the map (ignores unobserved pixels)
        map = hp.remove_monopole( map )
        # Reduce the resolution first, makes the smoothing faster
        map = hp.ud_grade( map, nside )
        # Apply the smoothing kernel
        map = hp.smoothing( map, fwhm=fwhm, lmax=lmax )

        if freq < 545:
            map[ map != hp.UNSEEN ] *= 1e6
            unit = r'$\mu$K'
        else:
            unit = r'MJy/sr'

        # Retrieve the fixed plotting amplitude
        amp = amps[ freq ]

        # create a new figure with the desired resolution
        dims = np.array(layout['res'])/dpi
        fig = plt.figure(frameon=True, figsize=dims, dpi=dpi)
        fig.add_axes(layout['axes'])

        # Plot the map, the sub argument tells the size of the grid and which panel
        # to use.
        mv.mollview( \
            map, hold=True, min=-amp, max=amp,
            cmap=cmap, xsize=xsize, unit=unit,
            margins=layout['margins'],
            cbar_fraction=layout['cbar_fraction'],
            title_font_size=layout['title_font_size'],
            label_font_size=layout['label_font_size'],
            title='{} GHz'.format(freq) )

        # write the image and destroy the figure
        fig.suptitle( \
            'RE %d'%(current_step), x=0.01, y=0.01,
            horizontalalignment='left', verticalalignment='bottom',
            fontweight='medium', fontsize=layout['label_font_size'])

        pylab.savefig( \
            'figures/ffp8_noise_{}_{}_r_{:05}.png'.format(freq, layout['res'][1], current_step),
            dpi=96 )

        plt.close(fig)
