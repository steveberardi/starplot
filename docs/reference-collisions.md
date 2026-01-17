One of the most important things that influences the visual quality of a map is labeling: both choosing carefully _what_ to label and also choosing good positions for those labels. Obviously, you don't want labels to collide with each other, but there's also a few more subtle things to consider when labeling points and areas on a map. Starplot has a `CollisionHandler` to control some of these things.

When you create a plot, you can specify the default collision handler that'll be used when plotting text. But, you can also override this default on all functions that plot text (either directly or as a side effect). There's one exception to this though: since constellation labels are area-based labels they have their own default collision handler. 

::: starplot.CollisionHandler
    options:
        members_order: source
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
