---
title: The Milky Way
---
[:octicons-arrow-left-24: Back to Examples](/examples)

# The Milky Way {.example-header}

![map-milky-way-stars](/images/examples/map_milky_way_stars.png)

In this example, we first plot all stars with a limiting magnitude of 11, which clearly shows the Milky Way. And then we use [Pillow](https://pillow.readthedocs.io/en/latest/index.html) to apply a median filter, which helps make the Milky Way stand out more in the image.

```python
--8<-- "examples/map_milky_way_stars.py"
```


