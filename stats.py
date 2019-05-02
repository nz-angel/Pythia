import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict

DAYS = ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes')


def plot_(plot_type, data_frame, x_col=None, y_col=None, x_ticks_label=None, x_label=None, y_label=None,
          plot_title=None, ticks=None, **kwargs):

    if plot_type in ['boxplot', 'barplot']:
        style = 'white'
    else:
        style = 'whitegrid'

    if ticks is not None:
        sns.set_style('ticks')


    if y_col is None:
        y_vals = data_frame.index.values
    else:
        y_vals = data_frame[y_col].values
    if x_col is None:
        x_vals = data_frame.index.values
    else:
        x_vals = data_frame[x_col].values

    with sns.axes_style(style):
        getattr(sns, plot_type)(x=x_vals, y=y_vals, **kwargs)

        if plot_type in ['boxplot', 'barplot']:
            sns.despine()
        if x_ticks_label is not None:
            plt.xticks(np.arange(5), x_ticks_label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plot_title)
        plt.tight_layout()
        plt.show()


def plot_donut(data_frame, criteria, plot_title=None):
    jimmy = plt.pie(data_frame[criteria].value_counts(), startangle=90, autopct='%1.1f%%', pctdistance=0.85, \
            textprops={'weight': 'bold'}, labels=data_frame[criteria].value_counts().index)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    plt.axis('equal')
    plt.gca().add_artist(centre_circle)
    plt.title(plot_title)
    plt.tight_layout()
    plt.show()


def count_patterns(values, pat_len):
    pattern_counter = defaultdict(int)
    for i in range(len(values)):
        pattern = tuple(values[i:i + pat_len])
        if len(pattern) < pat_len:
            break
        pattern_counter[pattern] += 1
    return pattern_counter


def predict_from_pattern(values, pattern_len, binary=True, silent=True):
    pattern_counter = count_patterns(values, pattern_len)
    last_pattern = values[-pattern_len + 1:]
    incr = pattern_counter[(*last_pattern, 1)]
    decr = pattern_counter[(*last_pattern, 0)]
    total = incr + decr
    if not total:
        if not silent:
            print('Longitud de patrón: {}'.format(pattern_len))
            print('No hay datos suficientes\n')
        if binary:
            return np.nan
    else:
        if not silent:
            print('Longitud de patrón: {}'.format(pattern_len))
            print('Incrementa: {:.2f}%'.format(incr/total*100))
            print('Decrece: {:.2f}% \n'.format(decr/total*100))
        if binary:
            return 1*((incr/total*100) > (decr/total*100))


def benchmark_pattern_prediction(values, init_days=30, pattern_lens=tuple(range(2, 8))):
    errors = np.ones((len(values)-init_days-1,len(pattern_lens)))
    error_ratio = np.empty((len(values)-init_days-1,len(pattern_lens)))
    for idx, j in enumerate(range(init_days+1, len(values))):
        available_data = values[:j]
        target = values[j]
        for i, p_len in enumerate(pattern_lens):
            e = abs(target - predict_from_pattern(available_data, p_len))
            if np.isnan(e):
                e = 1

            errors[idx, i] = e
            error_ratio[idx, i] = sum(errors[:idx+1, i])/(idx+1)

    data = pd.DataFrame(data=error_ratio[:, :], columns=pattern_lens)
    list_data = [data.loc[:, c] for c in pattern_lens]
    print(error_ratio)
    sns.lineplot(data=list_data)
    plt.show()
    pass


def plot_descritive_charts():
    # Dollar evolution
    df = pd.read_csv('data.csv', sep=';')
    plot_('lineplot', df, y_col='Value')

    # Dollar increase by weekday
    plot_('barplot', df, x_col='Weekday', y_col='Increase', x_ticks_label=DAYS, capsize=0.2, ticks=1, palette='Paired')

    # Dollar value fluctuation pby weekday
    plot_('boxplot', df, x_col='Weekday', y_col='Delta', x_label=DAYS)

    # Dollar increse by day
    plot_('barplot', df, x_col='Day', y_col='Increase', errwidth=0)

    plot_('boxplot', df, 'Day', 'Delta')

    plot_donut(df[df['After Speech'] == 1], 'Increase')
    plot_donut(df[df['After Speech'] == 0], 'Increase')
    plot_donut(df[df['Day of Speech'] == 1], 'Increase')
    plot_donut(df[df['Day of Speech'] == 0], 'Increase')
    plot_donut(df[df['After Holiday'] == 1], 'Increase')
    plot_donut(df[df['After Holiday'] == 0], 'Increase')


df = pd.read_csv('data.csv', sep=';')
vals = df['Increase'].values
# p_c = count_patterns(vals, 8)
# for k,v in p_c.items():
#     print(k, v)

predict_from_pattern(vals, 2, silent=False)
predict_from_pattern(vals, 3, silent=False)
predict_from_pattern(vals, 4, silent=False)
# benchmark_pattern_prediction(vals)
