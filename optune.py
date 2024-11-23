# coding: utf-8
"""
- Genetic algorithm (mlopt.ga)
- Random and parallel search
"""
import logging
import os
import signal
import sys
from multiprocessing.pool import Pool
from mlopt.resources.llvm_config import llvm_opt_options
from typing import List
from mlopt.params import Params
from mlopt.utils import run_cmd
from mlopt.ga_opt import GA

m_logging = logging.getLogger(__name__)

# Some configurations for this script
# FIXME: load some configuration files?
g_strategy = "random"
g_target_tool_timeout = 600
g_iterations = 3
g_is_parallel = False
g_default_time = 0
g_input_file = None
g_tool = None


def run_target_tool(input_file: str, cmd_args=" ") -> float:
    """Run the target_tool"""
    try:
        cmd_tool = [i for i in g_tool]
        cmd_tool.append(cmd_args)
        cmd_tool.append(input_file)
        logging.debug(cmd_tool)
        duration = run_cmd(cmd_tool, g_target_tool_timeout)
        # logging.debug("time: \n", duration)
        if duration >= g_target_tool_timeout:
            return 4294967295.0
        return duration
    except Exception as ex:
        print(ex)
        return 4294967295.0


def init_run(input_file: str):
    global g_default_time
    g_default_time = run_target_tool(input_file)


def ga_optimize(file_name: str):
    """Run Genetic algorithm to optimize the config.
    """
    # global g_iterations
    minimum_time = g_default_time
    minimum_opt = "init"

    def _ga_callback(para: Params) -> float:
        """for evaluating the fitness function"""
        try:
            extra_args = para.toc_cmd_args()
            time_new_config = run_target_tool(input_file=file_name, cmd_args=extra_args)
            return time_new_config

        except Exception as ee:
            print(ee)
            return 4294967295.0

    try:
        ga = GA(llvm_opt_options)
        for i in range(g_iterations):
            ga.evaluate(callback=_ga_callback)
            ga.repopulate()
            m_logging.info("finish {}-th iteration of GA...".format(i))
        minimum_time, minimum_opt = ga.retained()
    except Exception as ex:
        print(ex)

    return minimum_time, minimum_opt


def random_optimize(file_name: str):
    """Use random sampling/mutations (Different samplers can run in parallel)
    """
    minimum_time = g_default_time
    minimum_opt = "init"
    for _ in range(g_iterations):
        try:
            # randomly generate options
            para = Params()
            para.load(llvm_opt_options)
            para.mutate()
            cmd_args = para.to_cmd_args()

            time_new_config = run_target_tool(input_file=file_name, extra_args=cmd_args)
            logging.debug("finish running new configuration")
            logging.debug("------------------------")

            if time_new_config <= minimum_time:
                minimum_time = time_new_config
                minimum_opt = cmd_args

        except Exception as ex:
            print(ex)

    return minimum_time, minimum_opt


def optimize(file_name: str):
    """
    Choose a configuration
    """
    # global g_iterations
    if g_strategy == "random":
        return random_optimize(file_name)
    elif g_strategy == "ga":
        return ga_optimize(file_name)
    else:
        return random_optimize(file_name)
    # signal.alarm(signal.SIGTERM)


# this is the global Pool (workers)
g_pool = None


def signal_handler(sig, frame):
    global g_pool
    if g_pool:
        g_pool.terminate()
    print("We are finish here, have a good day!")
    sys.exit(0)


def parallel_optimize(input_file: str, m_num_process=10):
    global g_pool
    init_run(input_file)
    m_logging.info("Finish the first run!!")
    m_logging.info("Default time: {}".format(g_default_time))
    if g_default_time >= g_target_tool_timeout:
        print("Default run timeout. Please set a longer timeout via --target_tool_timeout!")
        exit(0)
    m_logging.info("Start to optimize the parameters")

    g_pool = Pool(m_num_process)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    results = []
    for _ in range(0, m_num_process):
        result = g_pool.apply_async(optimize, args=(g_input_file,))
        results.append(result)
    g_pool.close()
    g_pool.join()

    time_data = []
    opt_data = []
    for result in results:
        time_data.append(result.get()[0])
        opt_data.append(result.get()[1])

    m_time = min(time_data)
    m_opt = opt_data[time_data.index(min(time_data))]
    m_logging.info("minimum time: {}".format(m_time))
    m_logging.info("opt: {}".format(m_opt))

    return m_time, m_opt


def sequential_optimize(input_file: str):
    logging.debug("run sequential optimizer")

    init_run(input_file)
    m_logging.info("Finish the first run, time: {}".format(g_default_time))
    if g_default_time >= g_target_tool_timeout:
        print("Default run timeout!")
        exit(0)
    m_logging.info("Start to optimize")

    def seq_signal_handler(sig, frame):
        print("We are finish here, have a good day!")
        sys.exit(0)

    signal.signal(signal.SIGINT, seq_signal_handler)
    signal.signal(signal.SIGTERM, seq_signal_handler)
    signal.signal(signal.SIGQUIT, seq_signal_handler)
    signal.signal(signal.SIGHUP, seq_signal_handler)

    m_time, m_opt = optimize(input_file)
    m_logging.info("minimum time: {}".format(m_time))
    m_logging.info("opt: {}".format(m_opt))

    return m_time, m_opt


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', dest='workers', default=1, type=int, help="num threads")
    parser.add_argument('--opt_timeout', dest='opt_timeout', default=600, type=int,
                        help="timeout of opt")
    parser.add_argument('--target_tool_timeout', dest='target_tool_timeout', default=600, type=int,
                        help="timeout of the target_tool")
    parser.add_argument('--iterations', dest='iterations', default=6, type=int,
                        help="number of iterations for the opt")
    parser.add_argument('--strategy', dest='strategy', default='random', type=str)
    parser.add_argument('--tool', dest='tool', default='z3', type=str)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("infile", type=str, help="Path to input filed")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    g_input_file = args.infile
    if not os.path.isfile(g_input_file):
        print("Input file not found!")
        exit(0)

    # initialize global variables
    g_strategy = args.strategy
    g_opt_timeout = args.opt_timeout
    g_target_tool_timeout = args.target_tool_timeout
    g_iterations = args.iterations
    g_tool = args.tool.split(' ')

    if args.workers > 1:
        g_is_parallel = True
        min_time, min_opt = parallel_optimize(g_input_file, args.workers)
    else:
        min_time, min_opt = sequential_optimize(g_input_file)

    m_logging.info("Writing result to file...")
    output_filename = "{0}-{1}-{2}-iterations.txt".format(os.path.basename(g_input_file), g_strategy, g_iterations)
    with open(output_filename, "w") as file:
        file.write("{}\n".format(g_input_file))
        file.write("default time: {}\n".format(g_default_time))
        file.write("min time: {}\n".format(min_time))
        file.write("min opt: {}\n".format(min_opt))
        file.close()
    m_logging.info("Good bye!")
