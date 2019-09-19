"""Tests to run on Southampton's Iridis 4 supercomputer"""

from __future__ import annotations

import json
import random

from tqdm import tqdm

from core.core import load_args, save_filename
from core.model import reset_model, ModelDist, load_dist

from greedy.greedy import greedy_algorithm
from greedy.resource_allocation_policy import policies as resource_allocation_policies
from greedy.server_selection_policy import policies as server_selection_policies
from greedy.value_density import policies as value_densities

from greedy_matrix.allocation_value_policy import policies as matrix_policies
from greedy_matrix.matrix_greedy import matrix_greedy

from optimal.optimal import optimal_algorithm
from optimal.relaxed import relaxed_algorithm


def all_algorithms_test(model_dist: ModelDist, repeat: int, repeats: int = 200,
                        optimal_time_limit: int = 30, relaxed_time_limit: int = 30):
    """
    Greedy test with optimal found
    :param model_dist: The model distribution
    :param repeat: The repeat
    :param repeats: Number of model runs
    :param optimal_time_limit: The compute time for the optimal algorithm
    :param relaxed_time_limit: The compute time for the relaxed algorithm
    """
    print("Greedy test with optimal calculated for {} jobs and {} servers"
          .format(model_dist.num_jobs, model_dist.num_servers))

    data = []

    # Loop, for each run all of the algorithms
    for _ in tqdm(range(repeats)):
        # Generate the jobs and the servers
        jobs, servers = model_dist.create()
        algorithm_results = {}

        # Find the optimal solution
        optimal_result = optimal_algorithm(jobs, servers, optimal_time_limit)
        algorithm_results['optimal'] = optimal_result.store() if optimal_result is None else "failure"
        reset_model(jobs, servers)

        # Find the relaxed solution
        relaxed_result = relaxed_algorithm(jobs, servers, relaxed_time_limit)
        algorithm_results['Relaxed'] = relaxed_result.store() if relaxed_result is None else "failure"
        reset_model(jobs, servers)

        # Loop over all of the greedy policies permutations
        for value_density in value_densities:
            for server_selection_policy in server_selection_policies:
                for resource_allocation_policy in resource_allocation_policies:
                    greedy_result = greedy_algorithm(jobs, servers, value_density, server_selection_policy,
                                                     resource_allocation_policy)
                    algorithm_results[greedy_result.algorithm_name] = greedy_result.store()
                    reset_model(jobs, servers)

        # Loop over all of the matrix policies
        for policy in matrix_policies:
            greedy_matrix_result = matrix_greedy(jobs, servers, policy)
            algorithm_results[greedy_matrix_result.algorithm_name] = greedy_matrix_result.store()
            reset_model(jobs, servers)

        # Add the results to the data
        data.append(algorithm_results)

    # Save the results to the file
    with open(save_filename('optimal_greedy_test', model_dist.file_name, repeat), 'w') as json_file:
        json.dump(data, json_file)
    print(data)
        
    
if __name__ == "__main__":
    print(random.getstate())

    args = load_args()

    model_name, job_dist, server_dist = load_dist(args['model'])
    basic_model_dist = ModelDist(model_name, job_dist, args['jobs'], server_dist, args['servers'])

    all_algorithms_test(basic_model_dist, args['repeat'])
