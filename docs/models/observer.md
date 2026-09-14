# Observer

The `Observer` model represents an observer at a specific time and place on Earth. It's used by every plot type, and it's one of the few models you'll often instantiate directly.


### Basic usage
Create an observer at Palomar Mountain (California, USA) for October 13, 2025 at 9pm Pacific time:
```python
observer = Observer(
    dt=datetime(2025, 10, 13, 21, 0, 0, tzinfo=ZoneInfo('US/Pacific')),
    lat=33.363484,
    lon=-116.836394,
)
```

### Observer at Specific Epoch
```python

observer = Observer.at_epoch(2000) # J2000

```

::: starplot.Observer
    options:
        inherited_members: true
        show_root_heading: true
        show_docstring_attributes: true
