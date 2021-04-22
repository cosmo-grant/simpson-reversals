# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 13:20:10 2021

@author: Cosmo

Generates and visualizes indefinitely many Simpson reversals.

A Simpson reversal is when an association between two variables changes
sign when you condition on the value of a third variable, no matter what
the value of the third variable is. For example, in a drug trial, the rate of
recovery is higher in the treatment group than the control group overall, but
lower among men *and* lower among women.

In fact, you can get indefinitely many Simpson reversals. For example,
comparing treatment group and control group, there might be:
    overall, a lower recovery rate
    in each of two sub-populations, a higher recovery rate
    in each of four sub-sub-populations, a lower recovery rate
    in each of eight sub-sub-sub-populations, a higher recovery rate
    and so on.

The function simpson_tree generates an example of k reversals, for any k. The
function draw_layers visualizes each layer: e.g. the recovery rates in the
relevant populations, across treatment and control groups. And the function
to_data prints count data corresponding to a given Simpson tree.

For more explanation see the accompanying README.md.
"""

import matplotlib.pyplot as plt
import itertools
import more_itertools
import fractions
import math


def reverse_columns(tall_col, short_col):
    """Creates a Simpson reversal by dividing each column in two.

    A column is represented as a tuple (height, width). Assumes that tall_col
    is taller than short_col and that the heights are between 0 and 1.

    Args:
        tall_col: Tuple of floats. The height and width of the taller column.
        short_col: Tuple of floats. The height and width of the shorter column.

    Returns:
        Four columns. The first column is taller than the third, and the second
        is taller than the fourth. The sum of the areas of the first two columns
        equals the area of tall_col, and the sum of the areas of the last two
        columns equals the area of short_col.
    """

    # Must have: A, B, C, D in (0, 1), A < B, and C < D.
    # I chose the four values below somewhat arbitrarily, aiming
    #   to get easily interpreted images.
    A = 9/20
    B = 11/20
    C = 9/20
    D = 11/20

    # heights and widths of the given columns
    h_t, w_t = tall_col
    h_s, w_s = short_col

    # heights of the new columns
    h_tl = h_t + A*(1 - h_t)
    h_sl = h_t + B*(1 - h_t)
    h_tr = C*h_s
    h_sr = D*h_s

    # how far along, as a proportion of its width, to break each given column
    z_t = (h_t - C*h_s) / ((1 - A)*h_t + A - C*h_s)
    z_s = (h_s - D*h_s) / ((1 - B)*h_t + B - D*h_s)

    # defining the new columns
    tall_l = (h_sl, z_s * w_s)
    tall_r = (h_sr, (1 - z_s)*w_s)
    short_l = (h_tl, z_t * w_t)
    short_r = (h_tr, (1 - z_t)*w_t)

    return tall_l, tall_r, short_l, short_r


def next_layer(taller, shorter):
    """Returns the next layer in a Simpson tree.

    A layer in a Simpson tree is a list of two lists. Each list contains columns.
    Each column in the first list is taller than its counterpart in the second
    list.

    Args:
        taller: List of columns.
        shorter: List of columns.

    Returns:
        List of two lists. The first is a list of the new taller columns,
        constructed out of the given shorter columns. The second is a list of
        the new shorter columns, constructed out of the given taller columns.
    """
    new_taller, new_shorter = [], []

    for tall_col, short_col in zip(taller, shorter):
        tall_l, tall_r, short_l, short_r = reverse_columns(tall_col, short_col)
        new_taller += [tall_l, tall_r]
        new_shorter += [short_l, short_r]

    return [new_taller, new_shorter]


def simpson_tree(first_layer, k):
    """Returns a Simpson tree, k layers deep.

    Args:
        first_layer: List of two lists, the two initial columns.
        k: The depth of the tree to be generated.

    Returns:
        A Simpson tree, which is a dictionary, mapping an index to the
        corresponding layer in the tree.
    """
    tree = {1 : first_layer}

    for i in range(2, k+1):
        taller, shorter = tree[i-1]
        tree[i] = next_layer(taller, shorter)

    return tree


def cum_steps(lst):
    """Returns a stream of pairs, overlapping, in the accumulated list.

    For example, [1, 2, 3, 4] -> (0, 1), (1, 3), (3, 6), (6, 10).
    """
    return more_itertools.pairwise(
        itertools.accumulate([0] + lst))


def draw_layer(layer):
    """Creates a matplotlib figure to visualize a layer in a Simpson tree.

    Args:
        layer: List of two lists, a layer in a Simpson tree.
    """

    colors = ['orange', 'lightgreen', 'yellow', 'hotpink',
              'lightseagreen', 'tomato', 'beige', 'khaki',
              'cyan', 'lightsalmon', 'thistle', 'gainsboro',
              'lavenderblush', 'goldenrod', 'lightskyblue', 'greenyellow']

    taller, shorter = layer
    heights = [tall[0] for tall in taller] + [short[0] for short in shorter]
    widths = [tall[1] for tall in taller] + [short[1] for short in shorter]
    n = len(heights)
    xx = cum_steps(widths)

    fig, ax = plt.subplots()

    for (x1, x2), height, i in zip(xx, heights, itertools.count()):
        hatch = 'x' if i >= n/2 else ''
        ax.fill_between([x1, x2], 0, height,
                        hatch=hatch, facecolor=colors[i % (n//2)])

    ax.set_xlabel('proportion in sub-population')
    ax.set_ylabel('recovery rate')
    ax.set_ylim([0, 1])

    return fig, ax


def draw_layers(first_layer, k):
    """Creates multiple matplotlib figures to visualize each layer in a Simpson tree.

    Args:
        first_layer: List of two lists, each containing a single column.
          Represents the size and recovery rates of the treatment and
          control groups.
        k: The number of images to draw, one for each layer in the
          tree to be generated.
    """
    tree = simpson_tree(first_layer, k)

    for i in tree:
        # Because the taller columns come first in each layer, we need to
        #   reverse every other layer, so that (e.g.) the treatment population
        #   stays on the left and the control population stays on the right.
        layer = tree[i][::-1] if i%2 == 0 else tree[i]
        draw_layer(layer)


def to_fractions(layer):
    """Returns a new layer, where each float has been converted to a Fraction.

    Args:
        layer: List of two lists, a layer in a Simpson tree.
    """
    try:
        return [fractions.Fraction(i).limit_denominator() for i in layer]
    except:
        return [to_fractions(i) for i in layer]


def lcm(iterable):
    """Returns the least common multiple of an iterable of numbers."""
    lcm = 1
    for i in iterable:
        lcm = lcm * i // math.gcd(lcm, i)
    return lcm


def to_data(tree):
    """Prints integer data corresponding to a Simpson tree.

    A Simpson tree contains floats, representing various proportions of the
    population. This function "denormalizes" the tree, turning proportions into
    counts, and prints them. It should find the smallest population size
    consistent with the given tree.

    Args:
        tree: A Simpson tree, which is a dictionary, mapping an index to the
        corresponding layer in the tree.
    """
    f_tree = {k: to_fractions(v) for k, v in tree.items()}
    height_denoms, width_denoms = [], []

    # extract denominators
    for k in f_tree:
        taller, shorter = f_tree[k]
        for h, w in taller:
            height_denoms.append(h.denominator)
            width_denoms.append(w.denominator)
        for h, w in shorter:
            height_denoms.append(h.denominator)
            width_denoms.append(w.denominator)

    height_multiplier = lcm(height_denoms)
    width_multiplier = lcm(width_denoms)
    n = height_multiplier * width_multiplier # total population size

    for k in f_tree:

        # Taller columns always come first in f_tree
        #   so we need to reverse every other layer.
        treatment, control = f_tree[k][(k+1) % 2], f_tree[k][k%2]

        # e.g. subpopulations in the third layer are labeled 00, 01, 10, 11
        labels = [''.join(word)
                  for word in itertools.product(('0', '1'), repeat=k-1)]

        # When k==1, we should just print: a out of b people recovered.
        # When k>1, we should prefix that with the subpopulation's label.
        prefix = 'In sub-population ' if k > 1 else ''
        middle = ', ' if k > 1 else ''
        print(f'\n***LAYER {k}***')

        print('\nTREATMENT GROUP')
        for (h, w), label in zip(treatment, labels):
            print(prefix + f'{label}' \
                  + middle + f'{h*w*n} out of {w*n} people recovered.')

        print('\nCONTROL GROUP')
        for (h, w), label in zip(control, labels):
            print(prefix + f'{label}' + \
                  middle + f'{h*w*n} out of {w*n} people recovered.')


# first_layer = [[(3/5, .5)], [(2/5, .5)]]
# tree = simpson_tree(first_layer, 3)
# to_data(tree)

