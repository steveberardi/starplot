One of the biggest contributors to the visual quality of a map is labeling, which includes choosing carefully _what_ to label and also choosing good _positions_ for those labels. Obviously, you don't want labels to collide with each other, but there's also a few more subtle things to consider when labeling points and areas on a map. Starplot has a `CollisionHandler` to control some of these things.

When you create a plot, you can specify the default collision handler that'll be used when plotting text. But, you can also override this default on all functions that plot text (either directly or as a side effect). There's one exception to this though: since constellation labels are area-based labels they have their own default collision handler. 

_See the [Virgo Galaxy Cluster](/examples/map-virgo-cluster/) plot for an example of using a custom collision handler._


!!! tip "New Feature"

    The collision handler is a newer feature of Starplot (introduced in version 0.19.0), and will continue to evolve in future versions. As always, if you notice any unexpected behavior with it, please [open an issue on GitHub](https://github.com/steveberardi/starplot/issues).


::: starplot.CollisionHandler
    options:
        members_order: source
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
