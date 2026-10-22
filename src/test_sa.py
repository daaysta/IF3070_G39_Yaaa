import math
import random
import unittest
from unittest.mock import patch
from models import Ship, Vehicle
from state import State
from simulated_annealing import simulated_annealing


class SATest(unittest.TestCase):
    def setUp(self):
        self.empty=State([Vehicle('A',1,1,10,1)],Ship(2,2,5))
        self.full=State(self.empty.vehicles,self.empty.ship,{'A':(0,0,'H')})

    def test_worse_move_accepted_and_best_preserved(self):
        with patch.object(State,'random_neighbor',return_value=self.empty):
            r=simulated_annealing(self.full,initial_temp=1000,max_iter=1,rng=random.Random(1))
        self.assertEqual(r.final_value,0)
        self.assertEqual(r.extras['best_value'],10)
        self.assertAlmostEqual(r.extras['trace'][0]['probability'],math.exp(-10/1000))
        self.assertEqual(self.full.value(),10)

    def test_worse_move_rejected_at_low_temperature(self):
        with patch.object(State,'random_neighbor',return_value=self.empty):
            r=simulated_annealing(self.full,initial_temp=.1,min_temp=.001,max_iter=1,rng=random.Random(1))
        self.assertEqual(r.final_value,10)
        self.assertFalse(r.extras['trace'][0]['accepted'])

    def test_stagnation_counted_once_per_episode(self):
        with patch.object(State,'random_neighbor',return_value=None):
            r=simulated_annealing(self.full,max_iter=5,stuck_window=2)
        self.assertEqual(r.extras['stuck_count'],1)
        self.assertEqual(len(r.history),r.iterations+1)
        self.assertTrue(all(x['probability'] is None for x in r.extras['trace']))

    def test_reproducible_and_valid(self):
        a=simulated_annealing(self.full,max_iter=30,rng=random.Random(7))
        b=simulated_annealing(self.full,max_iter=30,rng=random.Random(7))
        self.assertEqual(a.history,b.history)
        self.assertEqual(a.extras['trace'],b.extras['trace'])
        self.assertTrue(a.final_state.is_valid())


if __name__=='__main__':unittest.main()
