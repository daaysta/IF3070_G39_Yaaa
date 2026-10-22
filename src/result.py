from dataclasses import dataclass, field


@dataclass
class SearchResult:
    name: str
    params: dict
    initial_state: object
    final_state: object
    history: list
    iterations: int
    duration: float
    extras: dict = field(default_factory=dict)

    @property
    def final_value(self):
        return self.final_state.value()

    def to_dict(self):
        return {
            "name": self.name,
            "params": self.params,
            "final_value": self.final_value,
            "initial_value": self.initial_state.value(),
            "iterations": self.iterations,
            "duration_sec": self.duration,
            "initial_state": self.initial_state.to_dict(),
            "final_state": self.final_state.to_dict(),
            "history": self.history,
            "extras": self.extras,
        }