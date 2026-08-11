import random
import math
from typing import List, Tuple
from backend.app.hyperagent.archive import Generation, archive_manager
from backend.app.config import settings

class ParentSelector:
    """
    Score-Proportional Parent Selection engine inspired by Meta's HyperAgents research.
    Combines Softmax temperature scaling and Roulette Wheel selection over evaluated generation scores.
    """
    def __init__(self, temperature: float = settings.SELECTION_TEMPERATURE):
        self.temperature = temperature

    def select_parent(self, generations: List[Generation] = None) -> Generation:
        """Selects a parent generation proportionally based on its evaluation score."""
        if not generations:
            generations = archive_manager.get_all_generations()
        
        if len(generations) == 1:
            return generations[0]

        scores = [g.score for g in generations]
        
        # Softmax sampling with temperature
        exp_scores = [math.exp(s / (self.temperature * 20.0)) for s in scores]
        sum_exp = sum(exp_scores)
        probabilities = [e / sum_exp for e in exp_scores]

        # Fitness proportionate selection (Roulette Wheel)
        rand_val = random.random()
        cumulative = 0.0
        for gen, prob in zip(generations, probabilities):
            cumulative += prob
            if rand_val <= cumulative:
                return gen
        
        # Fallback to highest scoring generation if numerical precision edge-case
        return max(generations, key=lambda g: g.score)

    def get_selection_distribution(self, generations: List[Generation] = None) -> List[Tuple[str, float, float]]:
        """Returns tuples of (generation_id, score, selection_probability) for visual analysis."""
        if not generations:
            generations = archive_manager.get_all_generations()

        scores = [g.score for g in generations]
        exp_scores = [math.exp(s / (self.temperature * 20.0)) for s in scores]
        sum_exp = sum(exp_scores)
        probabilities = [e / sum_exp for e in exp_scores]

        return [
            (gen.generation_id, gen.score, round(prob * 100, 2))
            for gen, prob in zip(generations, probabilities)
        ]

parent_selector = ParentSelector()
