from os.path import dirname, join
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture
import numpy as np

fits_directory = '../data/'
fits_filename = 'hlsp_hugs_hst_wfc3-uvis_ngc6254_f275w_v1_stack-0790s.fits'
# HST UV Globular Cluster Survey (HUGS) data can be found here: https://archive.stsci.edu/prepds/hugs/

fits_file_path = join(dirname(__file__), fits_directory, fits_filename)


# Read the data
fits_file = fits.open(fits_file_path)

image_data = fits_file[0].data
print(image_data)
print(image_data.shape)

# Create an image of a region of the data
section1 = image_data[4000:4300, 3990:4290]

plt.figure()
plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys')
plt.colorbar()
plt.show()

# Detect sources in the image
mean, median, std = sigma_clipped_stats(section1, sigma=3.0)
print((mean, median, std))

daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)

sources = daofind(section1 - median)
for col in sources.colnames:
    if col not in ('id', 'npix'):
        sources[col].info.format = '%.2f'
sources.pprint(max_width=-1)

# Add detected sources to the image
positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
apertures = CircularAperture(positions, r=5.0)

plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys', interpolation='nearest')
apertures.plot(color='red', lw=1.5, alpha=0.5)
plt.colorbar()
plt.show()

# Create a mask to not consider the too bright sources
mask = np.zeros(section1.shape, dtype=bool)
mask[170:195, 150:175] = True


sources = daofind(section1 - median, mask=mask)
xpix = sources['xcentroid']
ypix = sources['ycentroid']
positions = np.transpose((xpix, ypix))
apertures = CircularAperture(positions, r=5.0)
plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys', interpolation='nearest')
apertures.plot(color='red', lw=1.5, alpha=0.5)
plt.colorbar()
plt.show()
