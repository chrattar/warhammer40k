import random


def dice_roll(num_dice):
    roll_list = []
    while num_dice > 0:
        roll = random.randint(1, 6)
        roll_list.append(roll)
        num_dice -= 1
    return roll_list


def group_dice(dice_rolls):
    dice_dict = {}
    for die in dice_rolls:
        dice_dict[die] = dice_dict.get(die, 0) + 1
    return dice_dict


def print_grouped_dice(dice_dict):
    print(
        ", ".join(f"Face {face}: {count}x" for face, count in sorted(dice_dict.items()))
    )


def damage_profile(hits_on, damage):
    damage = hits_on * damage
    print(damage)
    return damage


rolls = dice_roll(25)
counts = group_dice(rolls)
print_grouped_dice(counts)

damage_done = damage_profile(3, 2)
