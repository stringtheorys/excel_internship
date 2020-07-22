"""
Evaluating the effectiveness of the different auction algorithms using different models, number of tasks and servers
"""

from __future__ import annotations

import json
import pprint

from src.auctions.critical_value_auction import critical_value_auction
from src.auctions.decentralised_iterative_auction import optimal_decentralised_iterative_auction
from src.auctions.vcg_auction import vcg_auction, fixed_vcg_auction
from src.core.core import reset_model, set_server_heuristics
from src.core.fixed_task import FixedTask, SumSpeedPowsFixedPolicy
from src.extra.io import parse_args, results_filename
from src.extra.model import ModelDistribution
from src.greedy.resource_allocation_policy import policies as resource_allocation_policies
from src.greedy.server_selection_policy import policies as server_selection_policies
from src.greedy.value_density import policies as value_densities


def auction_evaluation(model_dist: ModelDistribution, repeat_num: int, repeats: int = 50, vcg_time_limit: int = 30,
                       fixed_vcg_time_limit: int = 30, dia_time_limit: int = 3, price_change: int = 3,
                       initial_price: int = 25, with_vcg: bool = True):
    """
    Evaluation of different auction algorithms

    :param model_dist: The model distribution
    :param repeat_num: The repeat number
    :param repeats: The number of repeats
    :param vcg_time_limit: The VCG time limit
    :param fixed_vcg_time_limit: The Fixed VCG time limit
    :param dia_time_limit: Decentralised iterative auction time limit
    :param price_change: The default price change for DIA
    :param initial_price: The default initial price for DIA
    :param with_vcg: If to run the vcg auctions
    """
    print(f'Evaluates the auction algorithms (cva, dia, vcg, fixed vcg) for {model_dist.name} model with '
          f'{model_dist.num_tasks} tasks and {model_dist.num_servers} servers')
    model_results = []
    pp = pprint.PrettyPrinter()
    filename = results_filename('auctions', model_dist, repeat_num)

    for repeat in range(repeats):
        print(f'\nRepeat: {repeat}')
        # Generate the tasks and servers
        tasks, servers = model_dist.generate()
        set_server_heuristics(servers, price_change=price_change, initial_price=initial_price)
        fixed_tasks = [FixedTask(task, SumSpeedPowsFixedPolicy()) for task in tasks]
        algorithm_results = {'model': {
            'tasks': [task.save() for task in tasks], 'servers': [server.save() for server in servers]
        }}
        pp.pprint(algorithm_results)

        if with_vcg:
            # VCG Auctions
            vcg_result = vcg_auction(tasks, servers, time_limit=vcg_time_limit)
            algorithm_results[vcg_result.algorithm] = vcg_result.store()
            vcg_result.pretty_print()
            reset_model(tasks, servers)

            # Fixed VCG Auctions
            fixed_vcg_result = fixed_vcg_auction(fixed_tasks, servers, time_limit=fixed_vcg_time_limit)
            algorithm_results[fixed_vcg_result.algorithm] = fixed_vcg_result.store()
            fixed_vcg_result.pretty_print()
            reset_model(fixed_tasks, servers)

        # Decentralised Iterative auction
        dia_result = optimal_decentralised_iterative_auction(tasks, servers, time_limit=dia_time_limit)
        algorithm_results[dia_result.algorithm] = dia_result.store()
        dia_result.pretty_print()
        reset_model(tasks, servers)

        # Critical Value Auction
        for value_density in value_densities:
            for server_selection_policy in server_selection_policies:
                for resource_allocation_policy in resource_allocation_policies:
                    critical_value_result = critical_value_auction(tasks, servers, value_density,
                                                                   server_selection_policy, resource_allocation_policy)
                    algorithm_results[critical_value_result.algorithm] = critical_value_result.store()
                    critical_value_result.pretty_print()
                    reset_model(tasks, servers)

        # Add the results to the data
        model_results.append(algorithm_results)

        # Save the results to the file
        with open(filename, 'w') as file:
            json.dump(model_results, file)
    print('Finished running')


if __name__ == "__main__":
    args = parse_args()

    if args.extra == '' or args.extra == 'full':
        auction_evaluation(ModelDistribution(args.file, args.tasks, args.servers), args.repeat)
    elif args.extra == 'reduced':
        auction_evaluation(ModelDistribution(args.file, args.tasks, args.servers), args.repeat, with_vcg=False)
