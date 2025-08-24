---
title: Horizon Gradient Plot
---
[:octicons-arrow-left-24: Back to Examples](/examples)

# Horizon Gradient Plot {.example-header}

![horizon-gradient](/images/examples/horizon_gradient.png)

This plot shows what was in the sky when looking south from Stonehaugh, England on July 26, 2025 at 11pm BST. A color gradient has been applied for visual effect.  

The background_color of the map must be set as a RGBA value with full transparency (e.g. #ffffff00) for the gradient to render correctly. You can use either .extend(), as is done here, or apply the setting in a style sheet.  

```python
--8<-- "examples/horizon_gradient.py"
```

Gradients can be applied in a similar manner to MapPlots and OpticPlots with radial and mollweide gradients available in addition to vertical gradients.  

The range of existing gradient presets can be seen below.  

![gradient-preset-examples](/images/examples/gradient_preset_examples_mollweide.png)  
![gradient-preset-examples](/images/examples/gradient_preset_examples_radial.png)  
![gradient-preset-examples](/images/examples/gradient_preset_examples_mollweide.png)  

Additionally, custom gradient presets can be applied using:

```python
gradient_preset = [[0.0, "#ffffff"],
                    [0.2, "#adafceff"],
                    [0.4, "#7f7baaff"],
                    [0.6, "#3b3a72ff"],
                    [0.8, "#23204eff"],
                    [1.0, "#050505ff"],
                ]
```
