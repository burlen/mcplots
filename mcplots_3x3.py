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

# Make python pickle files out of the downgraded low resolution maps to
# facilitate quick plotting later
save_lowres = True
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

maps = {}

real_batch = current_step / 100


# loop over Planck frequencies
for ifreq, freq in enumerate( freqs ):

    if not par.use_mpi and (ifreq % 3) != 0:
        continue

    # file names for the input high resolution FITS map and an optional
    # downgraded and smoothed version of the same map (when save_lowres is
    # enabled)

    fn_hires \
        = '/project/projectdirs/planck/data/ffp8/mc_noise/{:03}/{:03}_{:02}/ffp8_noise_{:03}_full_map_mc_{:05}.fits'.format( \
           freq, freq, real_batch, freq, current_step )

    fn_lowres \
        = 'maps/mc_noise/{:03}/{:03}_{:02}/ffp8_noise_{:03}_full_map_mc_{:05}.fits'.format( \
          freq, freq, real_batch, freq, current_step )

    # Read the map from the appropriate Monte Carlo directory.
    maps[ifreq] = hp.read_map( fn_hires )
    # Remove a global offset from the map (ignores unobserved pixels)
    maps[ifreq] = hp.remove_monopole( maps[ifreq] )
    # Reduce the resolution first, makes the smoothing faster
    maps[ifreq] = hp.ud_grade( maps[ifreq], nside )
    # Apply the smoothing kernel
    maps[ifreq] = hp.smoothing( maps[ifreq], fwhm=fwhm, lmax=lmax )

    if freq < 545:
        maps[ifreq][ maps[ifreq] != hp.UNSEEN ] *= 1e6

dpi = 96
layouts = \
    { '1080p' : {'res':[1920, 1080], 'label_font_size':12, 'title_font_size':14, 'cbar_fraction':0.1, 'margins':None},
      '720p' : {'res':[1280, 720], 'label_font_size':10, 'title_font_size':12, 'cbar_fraction':0.15, 'margins':None},
      '480p' : {'res':[720, 480], 'label_font_size':8, 'title_font_size':10, 'cbar_fraction':0.1, 'margins':None} }

for layout in layouts.itervalues():

    # create a new figure with the desired resolution
    dims = np.array(layout['res'])/dpi
    fig = plt.figure(frameon=True, figsize=dims, dpi=dpi)

    # add the subplot for each frequency
    for ifreq, freq in enumerate( freqs ):

        if not par.use_mpi and (ifreq % 3) != 0:
            continue

        if freq < 545:
            unit = r'$\mu$K'
        else:
            unit = r'MJy/sr'

        # Retrieve the fixed plotting amplitude
        amp = amps[ freq ]

        # Plot the map, the sub argument tells the size of the grid and which panel
        # to use.
        mv.mollview( \
            maps[ifreq], min=-amp, max=amp, cmap=cmap,
            xsize=xsize, unit=unit, sub=[3,3,ifreq+1],
            margins=(0.01,0.01,0.01,0.02),
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
        'figures/ffp8_noise_{}_r_{:05}.png'.format(layout['res'][1], current_step),
        dpi=96 )

    plt.close(fig)
