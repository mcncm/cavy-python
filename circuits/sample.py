from collections import defaultdict, namedtuple
from typing import Dict, List, Any

class Sample:
    """Samples from running a quantum circuit"""

    def __init__(self, results: Dict[str, List[Any]]):
        self.results = results
        self.Result = namedtuple('Result', results.keys())

    def __getitem__(self, key) -> List[Any]:
        return self.results[key]

    def frequencies(self) -> Dict[Dict[str, Any], int]:
        """Return a dictionary mapping assignments to the number of times this
        environment is observed"""
        frequencies = defaultdict(int)
        keys, values = zip(*self.results.items())
        for value_tup in zip(*values):
            frequencies[self.Result(*value_tup)] += 1
        return frequencies

    def most_likely(self):
        """Get the most common environment that was sampled"""
        max_keyval = max(self.frequencies().items(), key=(lambda keyval: keyval[1]))
        return max_keyval[0]
