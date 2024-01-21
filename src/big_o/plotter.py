from collections import namedtuple

import matplotlib.pyplot as plt

Opt = namedtuple("Opt", ["fn", "label"])


class Plotter:
    @staticmethod
    def render_plot(n: int, *opts: Opt):
        def iterate(n, fn):
            return [fn(i) for i in range(1, n + 1)]

        for i, opt in enumerate(opts):
            _label = opt.label if opt.label is not None else f"T{i+1}"
            plt.plot(iterate(n, opt.fn), label=_label)

        plt.legend()

        plt.xlabel("input")
        plt.ylabel("steps")

        plt.yscale("log")
        plt.xscale("log")

        plt.show()
