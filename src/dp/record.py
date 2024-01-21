from collections import namedtuple
from copy import deepcopy as _deepcopy
from typing import Any, Dict, List, Tuple

import pandas as pd
from IPython.core.display import Markdown, display


class DpStep:
    @staticmethod
    def from_dict(item: Dict):
        return namedtuple("DpStepTuple", list(item.keys()))


class DpList(List):
    def __init__(self, a: List[int] | List[List[int]]):
        super().__init__(a)
        self.track_changes = False
        self.current_step = None
        self.current_changeset = None
        self.current_changeset_type = None
        self.steps_by_type: Dict[str, Tuple[Any, List]] = {}

    def deepcopy(self):
        if self.is_grid:
            return DpList([i[:] for i in self])

        return _deepcopy(super())

    def start(self, type: str, **kwargs):
        assert not self.track_changes
        self.track_changes = True
        self.current_step = DpStep.from_dict(kwargs)
        self.current_changeset = self.current_step(**kwargs)
        self.current_changeset_type = type
        if self.steps_by_type.get(self.current_changeset_type) is None:
            self.steps_by_type[self.current_changeset_type] = (self.current_step, [])
        return self

    def record(self, **kwargs):
        assert self.track_changes
        assert self.current_changeset is not None
        self.current_changeset = self.current_changeset._replace(**kwargs)

        return self

    def stop(self):
        assert self.track_changes
        assert self.current_changeset_type is not None
        assert self.steps_by_type[self.current_changeset_type] is not None
        self.steps_by_type[self.current_changeset_type][1].append(
            self.current_changeset
        )

        self.track_changes = False
        self.current_changeset = self.current_step = self.current_changeset_type = None

        return self

    def to_markdown(self, type: str, **kwargs):
        step_tuple, steps = self.steps_by_type.get(type, (None, []))
        if step_tuple is None or steps is None:
            return f"No {type} steps recorded."

        return pd.DataFrame(steps, columns=step_tuple._fields).to_markdown(
            **({"index": False, "tablefmt": "github", **kwargs})
        )

    def __str__(self) -> str:
        if self.is_grid:
            return self.to_grid()

        return super().__str__()

    def to_grid(self):
        return (
            "$$"
            + (
                pd.DataFrame(self, columns=list(range(len(self))))
                .to_markdown(tablefmt="latex", index=False)
                .replace("tabular", "array")
                .replace("\n", " ")
            )
            + "$$"
        )

    def render_markdown(self, type: str, **kwargs):
        return display(Markdown(self.to_markdown(type, **kwargs)))

    @property
    def is_grid(self):
        return all(map(lambda x: isinstance(x, List), self))

    @staticmethod
    def from_list(a: List[int]):
        return DpList(a)


if __name__ == "__main__":
    d = DpList([1, 2, 3])

    d.start("insert", index=0, value=1).record(index=1, value=2).stop()

    print(d.to_markdown("insert"))
