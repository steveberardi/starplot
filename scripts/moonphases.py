from skyfield import almanac
from skyfield.api import load

ts = load.timescale()
eph = load("de421.bsp")

t0 = ts.utc(1998, 1, 1)  # start date/time
t1 = ts.utc(2030, 12, 31)  # end date/time

# find all moon phases in date range
t, moons = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))

# find new moon times in UTC
new_moons = [t[i].utc_datetime() for i, m in enumerate(moons) if m == 2]

degree_ranges = []

for nm_time in new_moons:
    t0 = ts.from_datetime(nm_time - timedelta(hours=12))  # 12 hours before new moon
    t1 = ts.from_datetime(nm_time)
    t2 = ts.from_datetime(nm_time + timedelta(hours=12))  # 12 hours after new moon

    phase_0 = almanac.moon_phase(eph, t0)
    phase_1 = almanac.moon_phase(eph, t1)
    phase_2 = almanac.moon_phase(eph, t2)

    p0 = phase_0.degrees
    p2 = phase_2.degrees

    d_range = (360 - p0) + p2
    d_range = p2 - p0
    degree_ranges.append(d_range)

avg = sum(degree_ranges) / len(degree_ranges)
print(f"Average New Moon Range = {avg}")
print(f"Max: {max(degree_ranges)}")
