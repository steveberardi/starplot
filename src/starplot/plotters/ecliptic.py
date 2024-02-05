from starplot.data import ecliptic


class EclipticPlotter:
    def plot_ecliptic2(self):
        if not self.style.ecliptic.line.visible:
            return

        x = [(ra * 15) for ra, dec in ecliptic.RA_DECS]
        y = [dec for ra, dec in ecliptic.RA_DECS]

        self.ax.plot(
            x,
            y,
            dash_capstyle=self.style.ecliptic.line.dash_capstyle,
            **self.style.ecliptic.line.matplot_kwargs(self._size_multiplier),
            **self._plot_kwargs(),
        )

        if self.style.ecliptic.label.visible:
            inbounds = []
            for ra, dec in ecliptic.RA_DECS:
                if self.in_bounds(ra, dec):
                    inbounds.append((ra, dec))

            if len(inbounds) > 4:
                label_spacing = int(len(inbounds) / 3) or 1

                for i in range(0, len(inbounds), label_spacing):
                    ra, dec = inbounds[i]
                    self._plot_text(
                        ra,
                        dec - 0.4,
                        "ECLIPTIC",
                        **self.style.ecliptic.label.matplot_kwargs(
                            self._size_multiplier
                        ),
                    )
