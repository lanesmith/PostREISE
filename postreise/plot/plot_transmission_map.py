import numpy as np
import pandas as pd
import matplotlib
import matplotlib.cm as cm
from bokeh.plotting import figure, show
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import ColumnDataSource, ColorBar
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap

from postreise.plot.projection_helpers import project_branch

get_provider(Vendors.CARTODBPOSITRON)


def map_risk(congestion_stats, branch):
    """Makes map showing branches at risk of congestion.

    :param pandas.DataFrame congestion_stats: data frame as returned by
        :func:`postreise.analyze.transmission.generate_cong_stats`.
    :param pandas.DataFrame branch: branch data frame.
    """
    lines = congestion_stats.loc[
        congestion_stats['branch_device_type'] == 'Line']
    congestion_stats = congestion_stats.drop(['branch_device_type'], axis=1)
    branch_congestion = pd.concat(
        [branch.loc[congestion_stats.index], congestion_stats], axis=1)

    min_val = lines['risk'].min()
    max_val = lines['risk'].max()

    mapper1 = linear_cmap(field_name='risk', palette=Spectral6, low=min_val,
                          high=max_val)
    color_bar = ColorBar(color_mapper=mapper1['transform'], width=8,
                         location=(0, 0), title="risk")
    norm = matplotlib.colors.Normalize(vmin=min_val, vmax=max_val, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.jet)
    mapper.set_array(np.array([]))

    branch_map = project_branch(branch_congestion)

    multi_line_source = ColumnDataSource({
        'xs': branch_map[['from_x', 'to_x']].values.tolist(),
        'ys': branch_map[['from_y', 'to_y']].values.tolist(),
        'risk': branch_map.risk})

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title="Risk of congestion", tools=tools,
               x_axis_location=None, y_axis_location=None, plot_width=800,
               plot_height=800)
    p.add_layout(color_bar, 'right')
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.multi_line('xs', 'ys', color=mapper1, line_width=8,
                 source=multi_line_source)

    show(p)


def map_utilization(utilization, branch):
    """Makes map showing utilization.

    :param pandas.DataFrame utilization: utilization data fame as returned by
        :func:`postreise.analyze.transmission.get_utilization`.
    :param pandas.DataFrame branch: branch data frame.
    """

    branch_utilization = pd.concat(
        [branch.loc[branch.rateA != 0],
         utilization[branch.loc[branch.rateA != 0].index].median().rename(
             'median_utilization')], axis=1)
    lines = branch_utilization.loc[
        (branch_utilization['branch_device_type'] == 'Line')]

    min_val = lines['median_utilization'].min()
    max_val = lines['median_utilization'].max()

    mapper1 = linear_cmap(field_name='median_utilization', palette=Spectral6,
                          low=min_val, high=max_val)

    color_bar = ColorBar(color_mapper=mapper1['transform'], width=8,
                         location=(0, 0), title="median utilization")

    norm = matplotlib.colors.Normalize(vmin=min_val, vmax=max_val, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.jet)
    mapper.set_array(np.array([]))

    branch_map = project_branch(branch_utilization)

    multi_line_source = ColumnDataSource({
        'xs': branch_map[['from_x', 'to_x']].values.tolist(),
        'ys': branch_map[['from_y', 'to_y']].values.tolist(),
        'median_utilization': branch_map.median_utilization})

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title="Utilization", tools=tools, x_axis_location=None,
               y_axis_location=None, plot_width=800, plot_height=800)
    p.add_layout(color_bar, 'right')
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.multi_line('xs', 'ys', color=mapper1, line_width=8,
                 source=multi_line_source)
    show(p)


def map_binding(utilization, branch):
    """Makes map showing binding incidents. Green dots show transformers winding
        and blue dots show transformers. Lines show binding incidents with
        varying color indicating degree of incidents.

    :param pandas.DataFrame utilization: utilization data fame as returned by
        :func:`postreise.analyze.transmission.get_utilization`.
    :param branch: branch data frame.
    """

    branch_utilization = pd.concat(
        [branch, utilization.max().rename('max_utilization')], axis=1)
    branch_binding = branch_utilization.loc[
        (branch_utilization['max_utilization'] >= 1)]

    branch_map = project_branch(branch_binding)

    multi_line_source = ColumnDataSource({
        'xs': branch_map[['from_x', 'to_x']].values.tolist(),
        'ys': branch_map[['from_y', 'to_y']].values.tolist()})

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title="Binding Incidents", tools=tools, x_axis_location=None,
               y_axis_location=None, plot_width=800, plot_height=800)
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.multi_line('xs', 'ys', line_width=8, source=multi_line_source)
    transformers = branch_map.loc[
        (branch_map['branch_device_type'] == 'Transformer')]
    transformers_winding = branch_map.loc[
        (branch_map['branch_device_type'] == 'TransformerWinding')]
    p.circle(transformers['from_x'], transformers['from_y'], color="blue",
             alpha=0.6, size=10)
    p.circle(transformers_winding['from_x'], transformers_winding['from_y'],
             color="green", size=10, alpha=0.6)
    show(p)