from dataclasses import dataclass


@dataclass
class Vehicle:
    id: str
    w: int      
    l: int        
    fee: int      
    weight: int
    eta: int = 0  


@dataclass
class Ship:
    w: int
    l: int
    max_capacity: int