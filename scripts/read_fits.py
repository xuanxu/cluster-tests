from os.path import dirname, join
from datetime import datetime
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture, CircularAnnulus, ApertureStats, aperture_photometry
from acstools import acszpt

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
section1 = image_data[5000:5300, 4990:5290]

mean, median, std = sigma_clipped_stats(section1, sigma=3.0)
print((mean, median, std))

plt.figure()
plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys')
plt.colorbar()
plt.show()


# Detect sources in the image
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
mask[220:230, 80:110] = True
mask[80:130, 240:300] = True

sources = daofind(section1 - median, mask=mask)
xpix = sources['xcentroid']
ypix = sources['ycentroid']
positions = np.transpose((xpix, ypix))
apertures = CircularAperture(positions, r=5.0)
plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys', interpolation='nearest')
apertures.plot(color='red', lw=1.5, alpha=0.5)
plt.colorbar()
plt.show()

# Aperture photometry
print(apertures)

annulus_aperture = CircularAnnulus(positions, r_in=10.0, r_out=15.0)

plt.figure()
plt.imshow(section1, origin='lower', norm=LogNorm(), cmap='Greys', interpolation='nearest')
apertures.plot(color='red', lw=1.5, alpha=0.5)
annulus_aperture.plot(color='green', lw=1.5, alpha=0.5)
plt.colorbar()
plt.show()

aperture_stats = ApertureStats(section1, annulus_aperture)
background_mean = aperture_stats.mean 
aperture_area = apertures.area_overlap(section1)
total_background = background_mean * aperture_area

star_data = aperture_photometry(section1, apertures)

star_data['total_background'] = total_background

for col in star_data.colnames:
    star_data[col].info.format = '%.8g'

star_data.pprint(max_width=-1)

# Calculate Magnitudes: M = Mzero - 2.5 * log10((flux - background_radiation)/exposure_time)
instrument = fits_file[0].header['INSTRUME']
filter_name = fits_file[0].header['FILTER']
date_obs = fits_file[0].header['DATE-OBS']

print(instrument, filter_name, date_obs)

# Allowed detectors: ['WFC', 'HRC', 'SBC']
for valid_instrument in ['WFC', 'HRC', 'SBC']:
    if valid_instrument in instrument:
        instrument_formatted = valid_instrument
        break

date_obs_formatted = datetime.strptime(date_obs, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
filter_name_formatted = filter_name.strip()

print(instrument_formatted, filter_name_formatted, date_obs_formatted)

zpt_table = acszpt.Query(date=date_obs_formatted, detector=instrument_formatted).fetch()
filter_zpt = acszpt.Query(date=date_obs_formatted, detector=instrument_formatted, filt='F775W').fetch()

print(filter_zpt)
