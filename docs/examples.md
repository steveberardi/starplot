This page has a few examples to get you familiar with Starplot and how it works.

1. [Star Chart for Time/Location](#star-chart-for-timelocation)
2. [Star Chart with an Extra Object Plotted](#star-chart-with-an-extra-object-plotted)
3. [Map of Orion](#map-of-orion)



## Star Chart for Time/Location
To create a star chart for the sky as seen from [Palomar Mountain](https://en.wikipedia.org/wiki/Palomar_Mountain) in California on July 13, 2023 at 10pm PT:

```python
{% include 'examples/example_1.py' %}
```

The created file should look something like this:

![starchart-blue](images/example_1.png)


## Star Chart with an Extra Object Plotted

Building on the first example, you can also plot additional objects and even customize their style. Here's an example that plots the [Coma Star Cluster](https://en.wikipedia.org/wiki/Coma_Star_Cluster) (Melotte 111) as a red star and also changes the plot style to `GRAYSCALE`:

```python
{% include 'examples/example_2.py' %}
```

![zenith-coma](images/example_2.png)


## Map of Orion

The following code will create a simple map plot that shows the area around the constellation Orion, including an extra marker for M42 - The Great Orion Nebula:

```python
{% include 'examples/example_3.py' %}
```

The result should look something like this:

![map-orion](images/example_3.png)

---

*Check out the code reference to learn more about using starplot!*