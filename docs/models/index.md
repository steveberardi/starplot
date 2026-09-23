<style>
* {
  box-sizing: border-box;
}

.flex-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.flex-column {
  flex: 1; 
  flex-basis: 250px; 
  padding: 0 20px;
}

    </style>
# Models

Starplot has models to represent an observer and some of the objects you can plot, including stars, DSOs, planets, the Sun, and the Moon. These models are used for many things in Starplot:

- Defining an observing time and location
- Selecting objects to plot ([via the `where` kwarg](../reference-selecting-objects.md))
- Creating [callables](../reference-callables.md) to calculate size/color/opacity values
- Keeping track of plotted objects (via [`ObjectList`][starplot.ObjectList])
- Getting the position of an object at a specific time (via `get()`)
- Getting a list of objects that meet a series of conditions (via `find()`)

---

<div class="flex-container" markdown>

<div class="flex-column" markdown>
### :material-creation: Sky Objects

- [Star](star.md)
- [Constellation](constellation.md)
- [DSO](dso.md)
- [Planet](planet.md)
- [Sun](sun.md)
- [Moon](moon.md)
- [Comet](comet.md)
- [Satellite](satellite.md)
- [ObjectList](object-list.md)
</div>

<div class="flex-column" markdown>
### :material-telescope: Optics

- [Binoculars](optics.md#starplot.models.Binoculars)
- [Scope](optics.md#starplot.models.Scope)
- [Refractor](optics.md#starplot.models.Refractor)
- [Reflector](optics.md#starplot.models.Reflector)
- [Camera](optics.md#starplot.models.Camera)
</div>

<div class="flex-column" markdown>
### :material-account: Observer

- [Observer](observer.md)
</div>






</div>