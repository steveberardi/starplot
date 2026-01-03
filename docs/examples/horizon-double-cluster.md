---
title: Finding the Double Cluster in Perseus
---
[:octicons-arrow-left-24: Back to Examples](/examples)

# Finding the Double Cluster in Perseus {.example-header}

![horizon-double-cluster](/images/examples/horizon_double_cluster.png)


Here's a chart you might create to help you find the [Double Cluster](https://en.wikipedia.org/wiki/Double_Cluster) (NGC 884 and 869) in Perseus and to visualize the field of view with 10x binoculars (the red dashed circle).

This example uses many of Starplot's features:

- [Looking up objects][starplot.Constellation.get]
- Using properties on those objects to [selectively plot stars](/reference-selecting-objects/) (in this example, we use the constellation models to _only_ plot stars that are part of the lines in the constellation)
- Drawing a circle to [show the field of view for bincoulars][starplot.HorizonPlot.optic_fov]
- Drawing an [arrow][starplot.HorizonPlot.arrow] to show which stars you can use as guides to finding the double cluster

```python
--8<-- "examples/horizon_double_cluster.py"
```


