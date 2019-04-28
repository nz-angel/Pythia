import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

DAYS = ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes')


def plot_(plot_type, data_frame, x_col=None, y_col=None, x_ticks_label=None, x_label=None, y_label=None,
          plot_title=None, ticks=None, **kwargs):
    if plot_type in ['boxplot', 'barplot']:
        style = 'white'
    else:
        style = 'whitegrid'

    if ticks is not None:
        sns.set_style('ticks')

    with sns.axes_style(style):
        if y_col is None and x_col is None:
            getattr(sns, plot_type)(x=data_frame.index.values, y=data_frame.index.values, **kwargs)
        elif y_col is None and x_col is not None:
            getattr(sns, plot_type)(x=data_frame[x_col].values, y=data_frame.index.values, **kwargs)
        elif y_col is not None and x_col is None:
            getattr(sns, plot_type)(x=data_frame.index.values, y=data_frame[y_col].values, **kwargs)
        else:
            getattr(sns, plot_type)(x=data_frame[x_col].values, y=data_frame[y_col].values, **kwargs)

        if plot_type in ['boxplot', 'barplot']:
            sns.despine()
        if x_ticks_label is not None:
            plt.xticks(np.arange(5), x_ticks_label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plot_title)
        plt.tight_layout()
        plt.show()


# Dollar evolution
df = pd.read_csv('data.csv', sep=';')
plot_('lineplot', df, y_col='Value')

# Dollar increase by weekday
plot_('barplot', df, x_col='Weekday', y_col='Increase', x_ticks_label=DAYS, capsize=0.2, ticks=1)

# Dollar value fluctuation pby weekday
plot_('boxplot', df, x_col='Weekday', y_col='Delta', x_label=DAYS)

# Dollar increse by day
plot_('barplot', df, x_col='Day', y_col='Increase', errwidth=0)

plot_('boxplot', df, 'Day', 'Delta')