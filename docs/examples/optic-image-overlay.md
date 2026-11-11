---
title: Image Overlay on an Optic Plot
---
[:octicons-arrow-left-24: Back to Examples](../examples.md)

# Image Overlay on an Optic Plot {.example-header}

![optic-image-overlay](../images/examples/optic_image_overlay.png)

Here's an example of plotting an image of the Andromeda Galaxy (M31) on an optic plot. The image is aligned to the sky using control points, which map pixel positions in the image with the known RA/DEC of the stars at those positions. You can use a plate solver like [tetra3rs](https://tetra3rs.dev/) to find these control points automatically.

```python
--8<-- "examples/optic_image_overlay.py"
```
