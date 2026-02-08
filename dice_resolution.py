import random
import sys


def dice_roll(num_dice):
    roll_list = []
    while num_dice > 0:
        roll = random.randint(1, 6)
        roll_list.append(roll)
        num_dice -= 1
    return roll_list


def print_grouped_dice(dice_dict):
    print(
        ", ".join(f"\nD{face}: {count}x" for face, count in sorted(dice_dict.items()))
    )


def cut_off_amount(rolls, cutoff):
    keep_list = [die for die in rolls if die >= cutoff]  # keep 4+
    print(f"Keep List: {sorted(keep_list)}")
    print(f"All Rolls: {sorted(rolls)}")
    return keep_list


def group_dice(dice_rolls):
    dice_dict = {}
    for die in dice_rolls:
        dice_dict[die] = dice_dict.get(die, 0) + 1
    return dice_dict


rolls = dice_roll(30)
cut_off_amount(rolls, 4)
counts = group_dice(rolls)
print_grouped_dice(counts)
