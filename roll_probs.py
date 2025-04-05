#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 21:21:13 2025

@author: adamhammond
"""
import matplotlib.pyplot as plt
from collections import defaultdict
from FiveESimulations import sim
from contextlib import contextmanager
import numpy as np
from statistics import mean, stdev
import sys
import io


@contextmanager
def suppress_print():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = original_stdout

def extract_roll_data(log):
    actual_totals = []
    die_pairs = []

    for entry in log[:40]:  # Only process the first 35 entries
        if isinstance(entry, dict) and 'total_roll' in entry and 'demon_dice' in entry:
            actual_totals.append(entry['total_roll'])
            die_pairs.append(tuple(entry['demon_dice']))

    return actual_totals, die_pairs


def compute_expected_rolls(die_pairs):
    expected_counts = defaultdict(float)

    for d1, d2 in die_pairs:
        total_possibilities = d1 * d2
        for r1 in range(1, d1 + 1):
            for r2 in range(1, d2 + 1):
                total = r1 + r2
                expected_counts[total] += 1 / total_possibilities

    return expected_counts

def compute_expected_across_simulations(sim_logs):
    all_expected = defaultdict(list)

    for log in sim_logs:
        die_pairs = [tuple(entry['demon_dice']) for entry in log]
        expected_counts = defaultdict(float)
        
        for d1, d2 in die_pairs:
            total_possibilities = d1 * d2
            for r1 in range(1, d1 + 1):
                for r2 in range(1, d2 + 1):
                    total = r1 + r2
                    expected_counts[total] += 1 / total_possibilities

        for total, prob in expected_counts.items():
            all_expected[total].append(prob)

    return all_expected

def compute_mean_stdev(distributions, all_totals=range(2, 41)):
    means = []
    stdevs = []

    for total in all_totals:
        values = [dist.get(total, 0) for dist in distributions]
        means.append(mean(values))
        stdevs.append(stdev(values))

    return means, stdevs

def run_multiple_roll_prob_simulations(num_simulations=1000):
    expected_roll_distributions = []
    actual_roll_distributions = []

    for _ in range(num_simulations):
        with suppress_print():
            log, _ = sim()
        actual_totals, die_pairs = extract_roll_data(log)

        actual_freq = defaultdict(int)
        for roll in actual_totals:
            actual_freq[roll] += 1

        expected_counts = compute_expected_rolls(die_pairs)

        expected_roll_distributions.append(expected_counts)
        actual_roll_distributions.append(actual_freq)

    return actual_roll_distributions, expected_roll_distributions

def plot_mean_std_with_error_bars(means, stdevs, all_totals=range(2, 41)):
    plt.figure(figsize=(14, 6))
    plt.errorbar(all_totals, means, yerr=stdevs, fmt='o-', ecolor='red', capsize=4, label='Mean ± Stdev')
    plt.xlabel('Total Roll')
    plt.ylabel('Expected Frequency')
    plt.title('Expected Value and Variability of Rolls Across Simulations')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("mean_std_plot.png", dpi=300)
    plt.show()

def plot_actual_vs_expected(actual_totals, expected_counts):
    all_totals = range(2, 41)
    actual_freq = defaultdict(int)
    for roll in actual_totals:
        actual_freq[roll] += 1

    actual = [actual_freq[t] for t in all_totals]
    expected = [expected_counts.get(t, 0) for t in all_totals]

    plt.figure(figsize=(14, 6))
    plt.bar(all_totals, actual, width=0.4, label='Actual', align='edge', color='skyblue')
    plt.bar(all_totals, expected, width=-0.4, label='Expected', align='edge', color='salmon')
    plt.xlabel('Total Roll')
    plt.ylabel('Frequency')
    plt.title('Actual vs Expected Total Rolls')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("variance_plot.png", dpi=300)
    plt.show()


# Executable block for running in Spyder or as standalone script
if __name__ == "__main__":
    actual_distributions, expected_distributions = run_multiple_roll_prob_simulations(10000)
    means, stdevs = compute_mean_stdev(expected_distributions)
    plot_mean_std_with_error_bars(means, stdevs)
