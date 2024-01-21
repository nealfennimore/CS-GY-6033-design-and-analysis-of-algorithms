import random
from collections import namedtuple
from contextvars import ContextVar
from enum import Enum
from typing import Any, Callable, List, Optional

from src.mermaid import Mermaid
from src.tree.base import BaseNode, BaseTree

Hash = str
Case = Enum("Case", "CALLED RETURN CACHED SUBCALL")
Step = namedtuple(
    "Step", "index case id parent_id return_value fn args output output_case"
)

ctx: ContextVar["Stepper"] = ContextVar("stepper")


class Stepper:
    steps: List[Step] = []
    index: int = 0

    def __init__(self):
        self.steps = []
        self.index = 0

    def step(
        self,
        case: Case,
        id: Hash,
        parent_id: Optional[Hash],
        return_value: Any,
        fn: Optional[str] = None,
        args: Optional[List[Any]] = None,
        output: Optional[Any] = None,
    ):
        self.steps.append(
            Step(self.index, case, id, parent_id, return_value, fn, args, output, None)
        )
        self.index += 1

    def called_with(
        self, id: Hash, parent_id: Optional[Hash], fn: Callable, args: List[Any]
    ):
        self.step(Case.CALLED, id, parent_id, None, fn.__name__, args)

    def _return(
        self, case: Case, id: Hash, parent_id: Optional[Hash], return_value: Any
    ):
        self.step(case, id, parent_id, return_value)

    def returned_with(self, *args):
        self._return(Case.RETURN, *args)

    def cached_with(self, *args):
        self._return(Case.CACHED, *args)

    def hash(self) -> Hash:
        return hex(random.getrandbits(24))[2:]

    @property
    def called_steps(self):
        return [s for s in self.steps if s.case == Case.CALLED]

    @property
    def return_steps(self):
        return [s for s in self.steps if s.case == Case.RETURN]

    @property
    def cached_steps(self):
        return [s for s in self.steps if s.case == Case.CACHED]

    @property
    def called_with_output_values(self):
        called = {s.id: s for s in self.called_steps}
        returned = {s.id: s for s in self.return_steps}
        cached = {s.id: s for s in self.cached_steps}

        result = {}
        for id, step in called.items():
            if id in cached:
                result[id] = step._replace(
                    output=cached[id].return_value, output_case=Case.CACHED
                )
            elif id in returned:
                result[id] = step._replace(
                    output=returned[id].return_value, output_case=Case.RETURN
                )

        return list(result.values())

    @property
    def called_with_subcalls(self):
        called = {s.id: s for s in self.called_steps}

        result = {}
        for id, step in called.items():
            if step.output is None:
                result[id] = step._replace(output_case=Case.SUBCALL)

        return list(result.values())

    @staticmethod
    def run(fn: Callable, *args, **kwargs):
        token = ctx.set(Stepper())
        result = fn(*args, **kwargs)
        return result, token

    @staticmethod
    def run_gen(fn: Callable, *args):
        token = ctx.set(Stepper())
        result = yield from fn(*args)
        return result, token


class Node(BaseNode):
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    _label: Optional[str] = None
    _step: Step
    include_fn: bool = True
    include_output: bool = True

    def __init__(
        self,
        step: Step,
        label: Optional[str] = None,
        include_fn=True,
        include_output=True,
    ):
        self.step = step
        self._label = label
        self.include_fn = include_fn
        self.include_output = include_output

    @property
    def value(self):
        return self.step.output

    @property
    def label(self):
        if self._label is not None:
            return self._label

        output = ""
        if self.include_output:
            output = f" = {self.step.output}"

        args = ",".join(map(str, self.step.args))

        fn = f"{args}"
        if self.include_fn:
            fn = f"{self.step.fn}({args})"

        return f"{fn}{output}"


class Tree(BaseTree):
    def __init__(self, root: Node):
        super().__init__()
        self.root = root

    def render(self, node: Optional[Node], **kwargs):
        return Mermaid.render_step_tree(node, **kwargs)

    @classmethod
    def build(cls, steps: List[Step], **kwargs):
        tree = {}

        for step in steps:
            # print(step)
            tree[step.id] = Node(step, **kwargs)

        for node in tree.values():
            parent_id = node.step.parent_id
            if parent_id is not None and parent_id in tree:
                if tree[parent_id].left is None:
                    tree[parent_id].left = node
                else:
                    tree[parent_id].right = node

        return cls(tree[steps[0].id])
