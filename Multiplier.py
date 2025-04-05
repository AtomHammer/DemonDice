#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:00:51 2024

@author: adamhammond
"""
import os
import contextlib
import matplotlib.pyplot as plt
from collections import Counter
from simulations import sim  # Import your simulation function here

# Suppress print statements
@contextlib.contextmanager
def suppress_print():
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            yield  # Control returns to the block that uses this context manager

# Function to run multiple simulations
def run_multiple_simulations(num_simulations=1000):
    turns_list = []  # To store the number of turns for each simulation
    end_mechanisms = []  # To store which mechanism triggered the end
    fight_count = [] # for the fight count
    first_end_turns = [] 

    for _ in range(num_simulations):
        with suppress_print():  # Suppress print statements during the simulation
            simulation_log, f_count = sim()  # Run the Demon Dice simulation once
        # Retrieve the last log entry to get the number of turns and end mechanism
        last_entry = simulation_log[-1]
        turns_list.append(last_entry['turn'])
        fight_count.append(f_count)
        # Check for the mechanism responsible for ending
        if 'events' in last_entry and last_entry['events']:
            end_mechanisms.extend(last_entry['events'])
           # print(last_entry['events'])
        else: end_mechanisms.append('fault')
        
        first_end_turn = None
        for entry in simulation_log:
            if 'End' in entry['events']:
                first_end_turn = entry['turn']  # Get the turn when the first 'End' event occurs
                break  # Stop after finding the first instance

        if first_end_turn is not None:
            first_end_turns.append(first_end_turn)  # Store the turn number
            
    return turns_list, end_mechanisms, fight_count, first_end_turns

# Main execution block
if __name__ == "__main__":
    turns_list, end_mechanisms, fight_count, first_end_turns = run_multiple_simulations(6000)
    
    #print(first_end_turns)
    # Plotting the histogram of turns using a wider format and more bins
    plt.figure(figsize=(10, 20))  # Increase height for better spacing

    # Histogram for the number of turns (more bins)
    plt.subplot(4, 1, 1)
    plt.hist(turns_list, bins=range(min(turns_list), max(turns_list) + 2), alpha=0.7, color='blue', edgecolor='black')  # Added +2 to the range for more bins
    plt.title('Histogram of Turns Lasted in Demon Dice Simulation')
    plt.xlabel('Number of Turns')
    plt.ylabel('count')

    # Histogram for the first turn 'end' is rolled
    plt.subplot(4, 1, 2)
    plt.hist(first_end_turns, bins=range(min(first_end_turns), max(first_end_turns) + 2), alpha=0.7, color='teal', edgecolor='black')
    plt.title('Histogram of First Turn that an "End" is rolled')
    plt.xlabel('Turn')
    plt.ylabel('Count')

    # Bar graph for end mechanisms
    plt.subplot(4, 1, 3)
    mechanism_counts = Counter(end_mechanisms)
    plt.bar(mechanism_counts.keys(), mechanism_counts.values(), color='orange', alpha=0.7)
    plt.title('End Mechanism Triggers')
    plt.xlabel('Mechanism')
    plt.ylabel('Count')
    
    # Bar graph for fight count
    plt.subplot(4, 1, 4)
    number_fight_counts = Counter(fight_count)
    plt.bar(number_fight_counts.keys(), number_fight_counts.values(), color='teal', alpha=0.7)
    plt.title('Number of Fights Triggered')
    plt.xlabel('Fights')
    plt.ylabel('Count')    

    plt.tight_layout()  # Adjust subplots to fit into the figure area.
    plt.show()
    
    