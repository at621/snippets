import itertools

# number of items in each list
x = 5
y = 5
z = 5

# maximum number of items in each combination
n = 2

# dynamically create lists
list_x = ['x' + str(i + 1) for i in range(x)]
list_y = ['y' + str(i + 1) for i in range(y)]
list_z = ['z' + str(i + 1) for i in range(z)]

# generate all combinations of up to n items for each list
combos_x = [list(itertools.combinations(list_x, i + 1)) for i in range(n)]
combos_y = [list(itertools.combinations(list_y, i + 1)) for i in range(n)]
combos_z = [list(itertools.combinations(list_z, i + 1)) for i in range(n)]

# flatten the lists of combinations
combos_x = [item for sublist in combos_x for item in sublist]
combos_y = [item for sublist in combos_y for item in sublist]
combos_z = [item for sublist in combos_z for item in sublist]

# combine the combinations from the three lists
all_combos = list(itertools.product(combos_x, combos_y, combos_z))

# print the number of combinations and the combinations themselves
print(f'There are {len(all_combos)} combinations:')
for combo in all_combos:
    # combine tuples from each list into one tuple
    flattened_combo = tuple(itertools.chain.from_iterable(combo))
    print(flattened_combo)
