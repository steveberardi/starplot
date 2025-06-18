from datetime import datetime
from skyfield.api import N, Star, W, wgs84, load
from skyfield.almanac import find_discrete, find_transits, find_risings, find_settings
from pytz import timezone

tz = timezone("US/Pacific")
ts = load.timescale()

dt0 = tz.localize(datetime(2025, 6, 1, 0, 0, 0, 0))
dt1 = tz.localize(datetime(2025, 6, 3, 0, 0, 0, 0))

t0 = ts.from_datetime(dt0)  # ts.utc(2025, 6, 1)
t1 = ts.from_datetime(dt1)  # ts.utc(2025, 6, 3)


loc = wgs84.latlon(32.9701576, -117.0636201)

eph = load("de421.bsp")
polaris = Star(ra_hours=2.5303, dec_degrees=89.2641)

dubhe = Star(ra_hours=11.0621, dec_degrees=61.7510)

observer = eph["Earth"] + loc

horizon = 25

sky_object = eph["Mars"]

times_rise, _ = find_risings(observer, sky_object, t0, t1, horizon_degrees=horizon)
times_set, _ = find_settings(observer, sky_object, t0, t1, horizon_degrees=horizon)
transits = find_transits(observer, sky_object, t0, t1)

for rs in times_rise:
    print(rs.astimezone(tz).strftime("%a %d %H:%M"))

print("---------")

for tm in times_set:
    print(tm.astimezone(tz).strftime("%a %d %H:%M"))


print("---------")

for tm in transits:
    print(tm.astimezone(tz).strftime("%a %d %H:%M"))

exit()

f = find_risings(eph, sky_object, loc)
transits = find_transits(observer, sky_object, t0, t1)

tz = timezone("US/Pacific")

for tt in transits:
    print(tt.astimezone(tz).strftime("%a %d %H:%M"))

print(f)
print(transits)

for t, updown in zip(*find_discrete(t0, t1, f)):
    print(
        t.astimezone(tz).strftime("%a %d %H:%M"), "MST", "rises" if updown else "sets"
    )
