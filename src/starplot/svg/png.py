from pathlib import Path


def export_png_cairo(filename: str | Path, svg_source: str):
    import cairosvg

    cairosvg.svg2png(svg_source, write_to=filename)


def export_png_resvg(filename: str | Path, svg_source: str):
    from resvg_py import svg_to_bytes

    png_bytes = svg_to_bytes(svg_string=svg_source)

    with open(filename, "wb") as f:
        f.write(png_bytes)
