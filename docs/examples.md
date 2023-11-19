This page has a few examples to get you familiar with Starplot and how it works.

1. [Star Chart for Time/Location](#star-chart-for-timelocation)
2. [Star Chart with an Extra Object Plotted](#star-chart-with-an-extra-object-plotted)
3. [Map of Orion](#map-of-orion)
4. [Map of The Pleiades with a Scope Field of View](#map-of-the-pleiades-with-a-scope-field-of-view)



## Star Chart for Time/Location
To create a star chart for the sky as seen from [Palomar Mountain](https://en.wikipedia.org/wiki/Palomar_Mountain) in California on July 13, 2023 at 10pm PT:

```python
{% include 'examples/example_1.py' %}
```

The created file should look like this:

![starchart-blue](images/example_1.png)


## Star Chart with an Extra Object Plotted

Building on the first example, you can also plot additional objects and even customize their style. Here's an example that plots the [Coma Star Cluster](https://en.wikipedia.org/wiki/Coma_Star_Cluster) (Melotte 111) as a red star and also changes the plot style to `GRAYSCALE`:

```python
{% include 'examples/example_2.py' %}
```

![zenith-coma](images/example_2.png)


## Map of Orion

The following code will create a simple map plot that shows the area around the constellation Orion, including a legend and an extra marker for M42 - [The Great Orion Nebula](https://en.wikipedia.org/wiki/Orion_Nebula):

```python
{% include 'examples/example_3.py' %}
```

The result should look like this:

![map-orion](images/example_3.png)


## Map of The Pleiades with a Scope Field of View

The following code will create a minimal map plot that shows the field of view (red dashed circle) of [The Pleiades (M45)](https://en.wikipedia.org/wiki/Pleiades) when looking through a [Tele Vue 85](https://www.televue.com/engine/TV3b_page.asp?id=26) telescope with a 14mm eyepiece that has a 82 degree FOV:

```python
{% include 'examples/example_4.py' %}
```

The result should look like this:

![map-pleiades-scope](images/example_4.png)

!!! tip "Binocular Field of View"

    You can also plot a circle showing the field of view of binoculars with the `plot_bino_fov` function:

    ```python
    p.plot_bino_fov(ra=3.78361, dec=24.11667, fov=65, magnification=10)
    ```

---

*Check out the code reference to learn more about using starplot!*