#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 12:08:09 2025

@author: adamhammond
"""
import matplotlib.pyplot as plt
import numpy as np

def extract_increasing_path(rolls):
    """
    Given a list of total_rolls, return only the increasing path,
    plus the final roll (even if it's a drop).
    """
    filtered_turns = [1]
    filtered_rolls = [rolls[0]]

    for i in range(1, len(rolls)):
        if rolls[i] > filtered_rolls[-1]:
            filtered_turns.append(i + 1)
            filtered_rolls.append(rolls[i])

    if filtered_turns[-1] != len(rolls):
        filtered_turns.append(len(rolls))
        filtered_rolls.append(rolls[-1])

    return filtered_turns, filtered_rolls

def compute_three_avg_roll_lines(sorted_by_luck, group_size=20):
    """
    Given the sorted list of (first_high_turn, rolls), compute average roll lines
    for the earliest, middle, and latest threshold-crossing simulations.

    Returns:
        (turns, avg_early), (turns, avg_mid), (turns, avg_late)
    """
    total = len(sorted_by_luck)
    if total < 3 * group_size:
        raise ValueError("Not enough simulations to extract all three groups.")

    early_group = [rolls for _, rolls in sorted_by_luck[:group_size]]
    mid_start = total // 2 - group_size // 2
    mid_group = [rolls for _, rolls in sorted_by_luck[mid_start:mid_start + group_size]]
    late_group = [rolls for _, rolls in sorted_by_luck[-group_size:]]

    def avg_line(group):
        max_turns = max(len(r) for r in group)
        turn_totals = [[] for _ in range(max_turns)]
        for run in group:
            for i, val in enumerate(run):
                turn_totals[i].append(val)
        avg = [sum(t)/len(t) if t else None for t in turn_totals]
        turns = list(range(1, len(avg) + 1))
        return turns, avg

    return avg_line(early_group), avg_line(mid_group), avg_line(late_group)

def compute_end_turn_avg_last_rolls(sim_logs, num_last_rolls=6):
    """
    For each turn where at least one sim ends, compute the average of the last N rolls
    (default 6) for those sims. Returns a dict: {turn: average_last_N_rolls}
    """
    from collections import defaultdict

    roll_sums = defaultdict(list)

    for log in sim_logs:
        if not log:
            continue
        end_turn = log[-1]['turn']
        total_rolls = [entry['total_roll'] for entry in log]
        last_n = total_rolls[-num_last_rolls:]
        avg = sum(last_n) / len(last_n)
        roll_sums[end_turn].append(avg)

    # Final average per turn
    return {turn: sum(vals)/len(vals) for turn, vals in roll_sums.items()}


def plot_luck_heatmap(sim_logs, all_turns, all_rolls, filename="luck_heatmap.png"):
    """
    Generate a heatmap of all roll totals over time, with overlays for the
    3 luckiest and 3 unluckiest simulations based on early high rolls (>= 25).

    Parameters:
        sim_logs (list of lists): Each inner list is a simulation_log
        all_turns (list of int): All turn numbers across all sims (flattened)
        all_rolls (list of int): All total rolls across all sims (flattened)
        filename (str): Optional filename to save the output PNG
    """
    threshold = 25  # Defines what counts as a high roll
    # Set up figure
    plt.figure(figsize=(14, 7))

    # Define integer-aligned bin edges
    x_bins = np.arange(min(all_turns), max(all_turns) + 2)  # +2 ensures last bin captures max
    y_bins = np.arange(min(all_rolls), max(all_rolls) + 2)
   
    # Create 2D histogram
    H, xedges, yedges = np.histogram2d(all_turns, all_rolls, bins=(x_bins, y_bins))
   
    # Transpose so rows map to y, columns to x
    H = H.T
   
    # Plot using pcolormesh
    plt.figure(figsize=(14, 7))
    mesh = plt.pcolormesh(xedges, yedges, H, cmap='plasma', vmin=0, vmax=H.max())
    plt.colorbar(mesh, label='Frequency')
    plt.xlabel('Turn Number')
    plt.ylabel('Total Roll')
    plt.title('Total Rolls Over Time (All Simulations)')
    plt.grid(True, linestyle='--', alpha=0.3)
    # --- Analyze and overlay luckiest and unluckiest simulations ---
    roll_data = []
    for log in sim_logs:
        rolls = [entry['total_roll'] for entry in log]
        first_high_turn = next((i for i, r in enumerate(rolls, start=1) if r >= threshold), float('inf'))
        roll_data.append((first_high_turn, rolls))

    sorted_by_luck = sorted(roll_data, key=lambda x: x[0])

    (early_turns, early_avg), (mid_turns, mid_avg), (late_turns, late_avg) = compute_three_avg_roll_lines(sorted_by_luck, group_size=20)

    plt.plot(early_turns, early_avg, color='red', linestyle='--', label='Avg Early')
    plt.plot(mid_turns, mid_avg, color='yellow', linestyle='--', label='Avg Mid')
    plt.plot(late_turns, late_avg, color='green', linestyle='--', label='Avg Late')
    
    # For unluckiest
    for i in range(min(3, len(sorted_by_luck))):
        _, rolls = sorted_by_luck[i]
        t, r = extract_increasing_path(rolls)
        plt.plot(t, r, color='cyan', alpha=0.8, label='Unlucky' if i == 0 else "")

    # For luckiest
    for i in range(1, 4):
        _, rolls = sorted_by_luck[-i]
        t, r = extract_increasing_path(rolls)
        plt.plot(t, r, color='lime', alpha=0.8, label='Lucky' if i == 1 else "")

    """    
    Plot a thick dashed white line showing average of last 6 rolls for sims
    that ended on each turn.
    """
    end_roll_data = compute_end_turn_avg_last_rolls(sim_logs)
    turns = sorted(end_roll_data.keys())
    averages = [end_roll_data[t] for t in turns]
    plt.plot(turns, averages, linestyle='--', color='white', linewidth=2.5, label='Avg Last 6 (End Turn)')

    # Final touches
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Plot saved to {filename}")