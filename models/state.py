from typing import Literal

StateValue = Literal["init", "fetching", "error", "fetched", "downloading", "downloaded"]

class State:
    VALID_STATES = ("init", "fetching", "error", "fetched", "downloading", "downloaded")
    
    def __init__(self, state: StateValue = "init"):
        self._state = state
        if state not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {state}. Must be one of {self.VALID_STATES}")
    
    @property
    def state(self) -> StateValue:
        return self._state
    
    @state.setter
    def state(self, value: StateValue):
        if value not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {value}. Must be one of {self.VALID_STATES}")
        self._state = value