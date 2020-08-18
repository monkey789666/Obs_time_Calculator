from calendar import monthrange
from astropy.coordinates import EarthLocation
from astroplan import Observer
import astropy.units as u
from astropy.time import Time

# define the location of Lulin Observatory
latitude = 23.468611 * u.deg
longitude = 120.873611 * u.deg
elevation = 2862 * u.m
location = EarthLocation.from_geodetic(longitude, latitude, elevation)
lulin = Observer(location = location, timezone = 'Asia/Taipei',
                             name = "Lulin", description = "Lulin 1.0-m telescope")
# define functions
def getyearDate(year):
    months = range(1,13)
    date_list = []
    for month in months:
        for day in range(monthrange(year, month)[1] + 1)[1:]:
            str1 = '{}-{:02d}-{:02d}'.format(year,month,day)
            date_list.append(str1)
    return date_list


theyear = int(input('input year\n'))
days = getyearDate(theyear)


txtwrite = []
for day in days:
    t = Time(day) + 15*u.h
    eve_twil = lulin.twilight_evening_astronomical(t, which='previous')
    morn_twil = lulin.twilight_morning_astronomical(t, which='next')
    eve_twil.format = 'unix'
    morn_twil.format = 'unix'
    print('{}\n'.format(day))
    
    txtwrite.append('{} {} {}\n'.format(day, eve_twil.value, morn_twil.value))

with open('twil_time.txt','w') as f:
    list(map(f.write, txtwrite))