from os.path import dirname, join
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

fits_directory = '../data/'
fits_filename = 'hlsp_hugs_hst_wfc3-uvis_ngc6254_f275w_v1_stack-0790s.fits'
# HST UV Globular Cluster Survey (HUGS) data can be found here: https://archive.stsci.edu/prepds/hugs/

fits_file_path = join(dirname(__file__), fits_directory, fits_filename)

fits_file = fits.open(fits_file_path)

image_data = fits_file[0].data

section1 = image_data[4000:4300, 3990:4290]

plt.figure()
plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys')
plt.colorbar()
plt.show()