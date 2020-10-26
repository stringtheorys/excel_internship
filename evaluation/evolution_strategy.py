"""Evolve greedy policies; task prioritisation, server selection and resource allocation"""

import pprint

from cma import CMAEvolutionStrategy

from src.core.core import reset_model
from src.extra.io import parse_args
from src.extra.model import ModelDistribution
from src.greedy.greedy import greedy_algorithm
from src.greedy.resource_allocation_policy import EvolutionStrategy as ResourceAllocationEvoStrategy, SumSpeed
from src.greedy.server_selection_policy import EvolutionStrategy as ServerSelectionEvoStrategy, ProductResources
from src.greedy.task_prioritisation import EvolutionStrategy as TaskPriorityEvoStrategy, Value


def evolve_greedy_policies(model_dist: ModelDistribution, repeat: int, iterations: int = 30, population_size:int = 5):
    print(f'Evolves the greedy policies for {model_dist.name} model with '
          f'{model_dist.num_tasks} tasks and {model_dist.num_servers} servers')

    eval_tasks, eval_servers = model_dist.generate()
    lower_bound = greedy_algorithm(eval_tasks, eval_servers, Value(), ProductResources(), SumSpeed()).social_welfare
    print(f'Lower bound is {lower_bound}')
    reset_model(eval_tasks, eval_servers)

    evolution_strategy = CMAEvolutionStrategy(11 * [1], 0.2, {'popsize': population_size})
    for iteration in range(iterations):
        suggestions = evolution_strategy.ask()
        tasks, servers = model_dist.generate()

        solutions = []
        for i, suggestion in enumerate(suggestions):
            solutions.append(greedy_algorithm(tasks, servers, TaskPriorityEvoStrategy(i, *suggestion[:5]),
                                              ServerSelectionEvoStrategy(i, *suggestion[5:8]),
                                              ResourceAllocationEvoStrategy(i, *suggestion[8:11])).social_welfare)
            reset_model(tasks, servers)

        evolution_strategy.tell(suggestions, solutions)
        evolution_strategy.disp()

        if iteration % 2 == 0:
            evaluation = greedy_algorithm(eval_tasks, eval_servers, TaskPriorityEvoStrategy(0, *suggestions[0][:5]),
                                          ServerSelectionEvoStrategy(0, *suggestions[0][5:8]),
                                          ResourceAllocationEvoStrategy(0, *suggestions[0][8:11]))
            print(f'Iter: {iteration} - {evaluation.social_welfare}')

    pprint.pprint(evolution_strategy.result())


if __name__ == '__main__':
    args = parse_args()

    evolve_greedy_policies(ModelDistribution(args.file, args.tasks, args.servers), args.repeat)
