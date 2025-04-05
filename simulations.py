#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 22:15:38 2024

@author: adamhammond
"""
import csv
import random
import numpy as np  # Import NumPy for fitting line calculations
import matplotlib.pyplot as plt

# Goodman Games dice chain: d3, d4, d5, d6, d7, d8, d10, d12, d14, d16, d20
dice_chain = [3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20]

def read_rules_from_csv(file_name):
    rules = []
    try:
        with open(file_name, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                # Check if the row has the correct number of columns before processing
                if len(row) < 4:  # Make sure there are at least four columns
                    print(f"Warning: Row skipped due to insufficient columns: {row}")
                    continue
                
                flavor_text = row[0]  # First column: Flavor text
                
                # Check and convert the second column (die size change)
                die_size_change = int(row[1]) if row[1] else 0  # Convert or use 0 if blank

                # Check and convert the third column (damage)
                damage = int(row[2]) if row[2] else 0  # Convert or use 0 if blank

                event_flag = row[3]  # Fourth column: Event flag, can be blank but not converted
                
                rule = {
                    'flavor_text': flavor_text,
                    'die_size_change': die_size_change,
                    'damage': damage,
                    'event_flag': event_flag
                }
                rules.append(rule)

        # Print rules after reading the file
        print("Rules loaded successfully:")
       # for rule in rules:
           # print(rule)
        
    except FileNotFoundError:
        print(f"Error: The file at {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return rules

def roll_dice(size):
    return random.randint(1, size)  # Simulates rolling a die of specified size

def change_dice_size(demon_dice, change):
    """ Change the size of the demon dice based on change while ensuring the first die is the smaller one. """
    new_demon_dice = demon_dice[:]  # Make a copy of the current sizes
    steps = abs(change)  # Get the absolute value of the change

    if change > 0:  # Positive change (increase)
        if steps % 2 == 0:
            # Even changes - split equally
            increment = steps // 2
            new_demon_dice[0] = change_dice_size_single(new_demon_dice[0], increment)
            new_demon_dice[1] = change_dice_size_single(new_demon_dice[1], increment)
        else:
            # Odd change - the smaller die increases more
            new_demon_dice[0] = change_dice_size_single(new_demon_dice[0], steps // 2 + 1)
            new_demon_dice[1] = change_dice_size_single(new_demon_dice[1], steps // 2)

    elif change < 0:  # Negative change (decrease)
        if steps % 2 == 0:
            # Even changes - split equally
            decrement = steps // 2
            new_demon_dice[0] = change_dice_size_single(new_demon_dice[0], -decrement)
            new_demon_dice[1] = change_dice_size_single(new_demon_dice[1], -decrement)
        else:
            # Odd change - the larger die decreases more
            new_demon_dice[1] = change_dice_size_single(new_demon_dice[1], - (steps // 2 + 1))
            new_demon_dice[0] = change_dice_size_single(new_demon_dice[0], - (steps // 2))

    # Ensure the dice order is maintained, with the first die being the smaller or equal
    if new_demon_dice[0] > new_demon_dice[1]:
        new_demon_dice[0], new_demon_dice[1] = new_demon_dice[1], new_demon_dice[0]

    return new_demon_dice  # Return the updated list of demon dice


def change_dice_size_single(current_size, change):
    """ Change the size of a single die size while ensuring within bounds. """
    if current_size in dice_chain:
        index = dice_chain.index(current_size)

        # Calculate new index
        new_index = index + change

        # Ensure new_index is within valid range
        if new_index < 0:
            new_index = 0  # Minimum size is d3
        elif new_index >= len(dice_chain):
            new_index = len(dice_chain) - 1  # Maximum size is d30

        return dice_chain[new_index]

    return current_size  # If the size is not found in the chain, return it unchanged

def sim(filename="DemonDiceTable4"):  # sim() can be used from the command line to run a simulation
    # Append .csv to the filename
    file_name = f"{filename}.csv"
    
    rules = read_rules_from_csv(file_name)  # Load your rules from the CSV file

    game_state = {
        'turns': 0,
        'cumulative_damage': 0,  # Initialize cumulative damage
        'demon_dice': [6, 6],
        'fight_count': 0,  # Initialize fight count
        'accelerate_mode': False,
        'end_flags_count': 0  # Count of unique "End" flags triggered
    }

    log = []
    print("Starting simulation of the Demon Dice.")
    seen_once_events = set()  # Track which 'Once' events have been used

    while True:
        game_state['turns'] += 1  # Increment turn counter

        # Roll both Demon Dice
        rolls = [roll_dice(size) for size in game_state['demon_dice']]
        total_roll = sum(rolls)

        # Prepare log entry
        log_entry = {
            'turn': game_state['turns'],
            'demon_dice': game_state['demon_dice'][:],
            'rolls': rolls,
            'total_roll': total_roll,
            'cumulative_damage': game_state['cumulative_damage'],
            'events': []
        }

        # Check for end conditions
        if total_roll >= 36:
            total_roll = 35
            print("Achieved total roll of 36 or more.")
#            log_entry['events'].append('Rolled 36')
 #           log.append(log_entry)
#            break
        
        if game_state['turns'] >= 200:
            print("Too many turns!")
            log_entry['events'].append('200 turns')
            log.append(log_entry)
            break
        
        if game_state['cumulative_damage'] >= 100:
            print("Too much damage!")
            log_entry['events'].append('TPK')
            log.append(log_entry)
            break

        # Get the rule based on the total roll
        rule_index = total_roll - 2
        if rule_index < 0 or rule_index >= len(rules):
            print("Invalid rule index. Skipping...")
            continue

        rule = rules[rule_index]
        
        #check if Accelerate mode is on.
        if game_state['accelerate_mode']:
            game_state['demon_dice'] = change_dice_size(game_state['demon_dice'], 1)
        
         # Handle event flags
        if rule['event_flag']:  # Check if event_flag is not empty
            if rule_index not in seen_once_events:
                seen_once_events.add(rule_index)  # Mark as used
        
                # Handle the specific effects of each flag
                if rule['event_flag'] == "Fight":
                    game_state['fight_count'] += 1  # Increase the fight count
                    log_entry['events'].append("Fight")
                
                elif rule['event_flag'] == "Accelerate":
                    game_state['accelerate_mode'] = True
                    log_entry['events'].append("Accelerate mode on")
                
                elif rule['event_flag'] == "End":
                    game_state['end_flags_count'] += 1
                    
                    if game_state['end_flags_count'] >= 4:  # Condition to check if all end flags have been triggered
                        print("All 'End' flags triggered. Ending game.")
                        log_entry['events'].append('End Flags')
                        log.append(log_entry)
                        break  # Break the loop to end the game
                    else:
                       log_entry['events'].append('End')
                
            else:  # This handles rerolls of the same event
                if rule['event_flag'] == "End":
                    game_state['end_flags_count'] += 1
                    
                    if game_state['end_flags_count'] >= 4:  # Condition to check if all end flags have been triggered
                        print("All 'End' flags triggered. Ending game.")
                        log_entry['events'].append('End Flags')
                        log.append(log_entry)
                        break  # Break the loop to end the game
                    else:
                        log_entry['events'].append(f'Repeat End {game_state["end_flags_count"]}')
                
                else:
                    print("Reapplying rule 5 due to repeated event flag.")
                    rule = rules[3]  # Default to rule 5 if it's used again
     

        # Now apply other effects of the rule
        die_size_change = rule['die_size_change']
        if die_size_change != 0:
            game_state['demon_dice'] = change_dice_size(game_state['demon_dice'], die_size_change)

        if rule['damage'] != 0:
            game_state['cumulative_damage'] += rule['damage']  # Update cumulative damage with rule
            log_entry['cumulative_damage'] = game_state['cumulative_damage']  # Update log entry

        log.append(log_entry)
        # Print outcome of the turn
        print(f"{rule['flavor_text']}")
        print(f"Turn {log_entry['turn']}: Demon Dice: {log_entry['demon_dice']}, Rolls: {log_entry['rolls']}, Total: {log_entry['total_roll']}, Cumulative Damage: {game_state['cumulative_damage']}, Events: {log_entry['events']}, Fight Count: {game_state['fight_count']}, End Count: {game_state['end_flags_count']}.")

    return log, game_state['fight_count']


def plog(log):
    if not log:  # Check if the log is empty
        print("No data to plot.")
        return

    turns = [entry['turn'] for entry in log]
    total_rolls = [entry['total_roll'] for entry in log]
    demon_die = [sum(entry['demon_dice']) for entry in log]
    cumulative_damage = [entry['cumulative_damage'] for entry in log]

    plt.figure(figsize=(12, 6))

    # Plotting total rolls and sum of demon dice as scatter points
    plt.subplot(2, 1, 1)
    plt.scatter(turns, total_rolls, label='Total Rolls', color='blue', marker='o', alpha=0.7)  # Total Rolls
    plt.plot(turns, demon_die, label='Sum of Demon Dice', color='green', linestyle='-', linewidth=2)  # Demon Dice solid line

    # Fit line for total rolls
    coefficients = np.polyfit(turns, total_rolls, 1)  # Linear fit (degree 1)
    fit_line = np.polyval(coefficients, turns)
    plt.plot(turns, fit_line, color='teal', linestyle='--', label='Fit Line')  # Add the fit line
    
    plt.title('Demon Dice Rolls and Sum Over Turns')
    plt.xlabel('Turn')
    plt.ylabel('Value')
    plt.axhline(y=36, color='r', linestyle='--', label='Roll Threshold (36)')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(turns, cumulative_damage, marker='o', label='Cumulative Damage', color='orange')
    plt.title('Cumulative Damage Over Turns')
    plt.xlabel('Turn')
    plt.ylabel('Cumulative Damage')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simulation_log = sim()  # Run the simulation
    plog(simulation_log[0])    # Pass the entire log to the plotting function 
    