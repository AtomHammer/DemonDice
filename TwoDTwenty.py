import matplotlib.pyplot as plt



def compute_fraction_at_max_each_turn(sim_logs, max_die=20):
    max_turn = max(len(log) for log in sim_logs)
    total_sims = len(sim_logs)
    fractions = []
    remaining_fracs = []

    for t in range(1, max_turn + 1):
        count = 0
        still_running = 0
        for log in sim_logs:
            if t <= len(log):
                still_running += 1
                dice = log[t-1]['demon_dice']
                if dice[0] == max_die and dice[1] == max_die:
                    count += 1
        if still_running > 0:
            fractions.append(count / still_running)
            remaining_fracs.append(still_running / total_sims)
        else:
            fractions.append(0)
            remaining_fracs.append(0)
    return list(range(1, max_turn + 1)), fractions, remaining_fracs


def plot_fraction_max_each_turn(sim_logs):
    turns, fractions, remaining_fracs = compute_fraction_at_max_each_turn(sim_logs)
    plt.figure(figsize=(10, 5))
    plt.plot(turns, fractions, color='deepskyblue', linewidth=2.5, label='At Max Dice (20,20)')
    plt.plot(turns, remaining_fracs, color='orange', linewidth=2, linestyle='--', label='Simulations Remaining')
    plt.xlabel('Turn Number')
    plt.ylabel('Fraction')
    plt.title('Fraction of Ongoing Simulations at Max Dice and Survival Over Time')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("fraction_at_max_dice_per_turn.png")
    plt.show()


if __name__ == "__main__":
    from FiveEMultiplier import run_multiple_simulations

    # Run simulations
    _, _, _, _, _, _, sim_logs = run_multiple_simulations(1000)

    # Plot the per-turn fraction
    plot_fraction_max_each_turn(sim_logs)
