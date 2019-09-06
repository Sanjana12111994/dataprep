"""
This module implements functions for plotting visualizations for a single field.
"""
# pytype: disable=import-error
# pylint: disable=R0903
# pylint: disable=R0914
import math
from typing import Any, Dict, Optional, Tuple

import holoviews as hv
from holoviews import Cycle
import numpy as np
import pandas as pd
import bokeh.palettes as bp
from bokeh.models import (BoxZoomTool, ColumnDataSource, FixedTicker,
                          FuncTickFormatter, Grid, HoverTool, LinearAxis, Plot,
                          Range1d, ResetTool, SaveTool, WheelZoomTool)
from bokeh.models.annotations import Title
from bokeh.models.glyphs import Circle, Rect, Segment, VBar
from bokeh.models.ranges import FactorRange
from bokeh.plotting import figure
from bokeh.transform import cumsum

TOOLS = "wheel_zoom, box_zoom,reset, box_select"


class UniViz:
    """
    Encapsulation for Univariate visualizations.
    """
    pie = False  # to know if the pie chart is plotted error-lessly.
    barplot = False  # to know if the bar plot is plotted error-lessly.
    box = False  # to know if the box plot is plotted error-lessly.
    hist = False  # to know if the histogram is plotted error-lessly.
    qqnorm = False  # to know if the QQ norm plot is plotted error-lessly.
    kde = False  # to know if the kernel density plot is plotted error-lessly.
    cat_caption = "{} Categories"
    num_caption = "{} - {}"

    def pie_viz(self, data: Dict[str, int], col_x: str) -> Any:
        """
        Pie chart vizualisation for categorical data
        :param data: the result from the intermediate
        :param name: the name of the field
        :return: Bokeh plot figure
        """
        chart_radius = 0.4
        data_df = pd.Series(data).dropna().reset_index(name="count").rename(
            columns={"index": "cat"})
        total_count = sum(data_df["count"])
        data_df["percen"] = data_df["count"]/total_count * 100
        data_df["angle"] = (data_df["percen"]/100) * 2 * math.pi
        color_list = bp.d3["Category20c"]  # pylint: disable=E1101
        color_list.update({1: ["#084594"], 2: ["#084594", "#9ecae1"]})
        data_df["colour"] = color_list[len(data_df)]
        plot_figure = figure(title="{}".format(col_x), tools=TOOLS,
                             toolbar_location=None)

        plot_figure.wedge(
            x=0,
            y=1,
            radius=chart_radius,
            start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"),
            line_color="white",
            fill_color="colour",
            legend="cat",
            source=data_df
        )
        hover = HoverTool(
            tooltips=[(""+col_x+"", "@cat"), ("Count", "@count"), ("Percentage", "@percen{0.2f}%")],
            mode="mouse"
        )
        plot_figure.add_tools(hover)
        plot_figure.axis.axis_label = None
        plot_figure.axis.visible = False
        plot_figure.grid.grid_line_color = None
        plot_figure.title.text_font_size = "10pt"
        self.pie = True
        return plot_figure

    def bar_viz(self, data: Dict[Any, Any], col_x: str) -> Any:
        """
        Bar chart vizualisation for the categorical data
        :param data: the result from the intermediate
        :param col_x: the name of the field
        :return: Bokeh plot figure
        """
        data_sorted = sorted(data.items(), key=lambda x: x[1])
        data_source = pd.DataFrame({"count": [i[1] for i in data_sorted],
                                    "cat": [str(x[0]) for x in data_sorted]})
        data_source["percen"] = data_source["count"]/data_source["count"].sum() * 100
        interm = ColumnDataSource(data_source)
        plot_figure = figure(tools=TOOLS,
                             title="{}".format(col_x),
                             x_range=FactorRange(factors=[str(x[0]) for x in data_sorted]),
                             #y_range=[0, max(data_source["count"])+10],
                             toolbar_location=None)

        hover = HoverTool(
            tooltips=[(""+col_x+"", "@cat"), ("Count", "@count"), ("Percentage", "@percen{0.2f}%")],
            mode="mouse"
        )
        bars = VBar(x="cat", top="count", bottom=0, width=0.3, fill_color="purple")
        plot_figure.add_glyph(interm, bars)
        plot_figure.add_tools(hover)
        plot_figure.xaxis.major_label_orientation = math.pi/4
        plot_figure.xgrid.grid_line_color = None
        plot_figure.ygrid.grid_line_color = None
        plot_figure.xgrid.grid_line_color = None
        plot_figure.ygrid.grid_line_color = None
        plot_figure.yaxis.major_label_text_font_size = "0pt"
        plot_figure.xaxis.major_label_text_font_size = "0pt"
        plot_figure.yaxis.major_tick_line_color = None
        plot_figure.yaxis.minor_tick_line_color = None
        plot_figure.xaxis.axis_label = col_x
        plot_figure.yaxis.axis_label = "Count"
        plot_figure.title.text_font_size = "10pt"
        plot_figure.xaxis.axis_label = self.cat_caption.format(data_source.shape[0])
        self.barplot = True
        return plot_figure

    def hist_viz(self, data: Tuple[np.array, np.array], col_x: str,
                 element_color: str = "purple") -> Any:
        """
        Histogram for a column
        :param data: intermediate result
        :param col_x: name of the column
        :param element_color: color of bins
        :return: Bokeh Plot Figure
        """
        hist_array = data[0]
        bins_array = data[1]
        data_source = pd.DataFrame({"left": bins_array[: -1], "right":
                                    bins_array[1:], "freq": hist_array,
                                    "percen": (hist_array/np.sum(hist_array))*100})
        interm = ColumnDataSource(data_source)

        plot_figure = figure(tools=TOOLS,
                             title="{}".format(col_x),
                             toolbar_location=None)
        hover = HoverTool(
            tooltips=[("Bin", "[@left, @right]"), ("Frequency", "@freq"),
                      ("Percentage", "@percen{0.2f}%")],
            mode='vline')
        plot_figure.quad(source=interm, left="left", right="right", bottom=0,
                         top="freq",
                         color=element_color)
        plot_figure.add_tools(hover)
        plot_figure.yaxis.major_label_text_font_size = "0pt"
        plot_figure.yaxis.major_tick_line_color = None
        plot_figure.yaxis.minor_tick_line_color = None

        plot_figure.xaxis.major_label_text_font_size = "0pt"
        plot_figure.xaxis.major_tick_line_color = None
        plot_figure.xaxis.minor_tick_line_color = None

        plot_figure.xgrid.grid_line_color = None
        plot_figure.ygrid.grid_line_color = None
        plot_figure.xaxis.axis_label = col_x
        plot_figure.yaxis.axis_label = "Frequency"
        plot_figure.title.text_font_size = "10pt"
        plot_figure.xaxis.axis_label = self.num_caption.format(bins_array[0], bins_array[-1])
        self.box = True
        return plot_figure

    def qqnorm_viz(self, in_data: Dict[str, Any], col_x: str) -> Any:
        """
        QQ-Norm plot for a column
        :param in_data: intermediate result
        :param col_x: name of the field
        :return: Bokeh Plot Figure
        """
        plot = figure(tools=TOOLS, title="{}".format(col_x),
                      toolbar_location=None)
        plot.circle(x=list(in_data["theory"]), y=list(in_data["sample"]), size=3, color="#4292c6")
        all_values = np.concatenate((in_data["theory"], in_data["sample"]))
        plot.line(x=[np.min(all_values), np.max(all_values)],
                  y=[np.min(all_values), np.max(all_values)], color="red")
        hover = HoverTool(tooltips=[("x", "@x"), ("y", "@y")], mode="mouse")
        plot.add_tools(hover)
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None

        plot.xaxis.axis_label = "Normal Quantiles"
        plot.yaxis.axis_label = "Quantiles of {}".format(col_x)
        plot.title.text_font_size = "10pt"
        self.qqnorm = True
        return plot

    def hist_kde_viz(self, data: np.core.array, bandwidth: float, col_x: str) -> Any:
        """
        histogram + KDE visualization
        :param data: tuple containing frequency, bins and values
        :param bandwidth: required bandwidth of the kde
        :param col_x: the name of the column
        :return: the Bokeh Plot Figure
        """
        hover_hist = HoverTool(tooltips=[("Bin", "$edges"), ("Count", "$freq")], mode="vline")
        hover_dist = HoverTool(tooltips=[("x", "$x{0.2f}"), ("y", "$y{0.2f}")], mode="mouse")
        freq, edges = np.histogram(data, density=True)
        hist = hv.Histogram((edges, freq)).opts(tools=[hover_hist], color="#c6dbef",
                                                line_color="#c6dbef")
        dist = hv.Distribution(data).opts(
            filled=False,
            line_color=Cycle(),
            bandwidth=bandwidth, tools=[hover_dist])
        plot_figure = hv.render(hist * dist, backend="bokeh")
        plot_figure.toolbar_location = None
        plot_figure.title = Title(text=col_x)
        plot_figure.title.text_font_size = "10pt"
        plot_figure.xaxis.axis_label = self.num_caption.format(np.min(data), np.max(data))
        plot_figure.sizing_mode = "fixed"
        plot_figure.xaxis.major_label_text_font_size = "0pt"
        plot_figure.yaxis.major_label_text_font_size = "0pt"
        self.kde = True
        return plot_figure

    def box_viz(self, data: Dict[str, Dict[str, Any]], col_x: str, col_y: Optional[str] = None,
                box_width: float = 0.25) -> Any:
        """
        *SPECIAL CASE
        Box plot for any number of categories or a single column
        :param data: intermediate result
        :param col_x: name in case of a single column
        :param col_y: name of column y in plot(df, x, y)
        :param box_width: width of each box
        :return: Bokeh Plot Figure
        """
        d_f = pd.DataFrame(data)  # , index=range(0, len(data)))
        d_f = d_f.append(pd.Series({col: i for col, i in
                                    zip(d_f.columns, range(1, len(d_f.columns) + 1))}, name="x"))
        d_f = d_f.transpose()
        d_f["y"], d_f["w"] = (d_f["tf"] + d_f["sf"]) / 2, [box_width] * len(d_f)
        d_f["x0"], d_f["x1"] = d_f["x"] - box_width/2, d_f["x"] + box_width/2
        d_f["uw"], d_f["lw"] = d_f["sf"] + 1.5 * d_f["iqr"], d_f["tf"] - 1.5 \
            * d_f["iqr"]
        d_f["h"] = d_f["sf"] - d_f["tf"]

        # Bokeh plotting code from here
        y_min = min(d_f["lw"]) / 2 if min(d_f["lw"]) > 0 else min(d_f["lw"]) * 2
        y_max = max(d_f["uw"]) if np.isnan(max(d_f["max_outlier"])) else max(d_f["max_outlier"])

        if col_y is None:
            title = "{}".format(col_x)
        else:
            title = "{} in {}".format(col_x, col_y)

        plot = Plot(
            plot_width=300,
            plot_height=500,
            min_border=0,
            toolbar_location=None,
            y_range=Range1d(y_min, 1.25 * y_max),
            title=Title(text=title)
        )

        hover_box = HoverTool(
            tooltips=[("25%", "@tf"), ("50%", "@fy"), ("75%", "@sf")],
            mode="mouse", names=["box"])

        plot.add_glyph(ColumnDataSource(data=d_f), Rect(x="x", y="y", width="w",
                                                        height="h",
                                                        fill_color="#cab2d6"), name="box")
        plot.add_glyph(ColumnDataSource(data=d_f), Segment(x0="x0", y0="fy",
                                                           x1="x1", y1="fy",
                                                           line_width=1.5,
                                                           line_color="black"))

        for cat in d_f.index:
            series = d_f.loc[cat]
            temp_list = [series["x"]] * len(series["outliers"])
            source = ColumnDataSource(data=pd.DataFrame({"x": temp_list,
                                                         "y": series[
                                                             "outliers"]}))
            outliers = Circle(x="x", y="y", size=3, fill_color="red")
            plot.add_glyph(source, outliers, name="outlier")

        plot.add_glyph(ColumnDataSource(data=d_f), Segment(x0="x", y0="uw",
                                                           x1="x", y1="sf",
                                                           line_width=1.5,
                                                           line_color="black"))
        plot.add_glyph(ColumnDataSource(data=d_f), Segment(x0="x", y0="lw",
                                                           x1="x", y1="tf",
                                                           line_width=1.5,
                                                           line_color="black"))
        plot.add_glyph(ColumnDataSource(data=d_f), Segment(x0="x0", y0="uw",
                                                           x1="x1", y1="uw",
                                                           line_width=1.5,
                                                           line_color="black"),
                       name="upper")
        plot.add_glyph(ColumnDataSource(data=d_f), Segment(x0="x0", y0="lw",
                                                           x1="x1", y1="lw",
                                                           line_width=1.5,
                                                           line_color="black"),
                       name="lower")

        # Add Tools
        plot.add_tools(WheelZoomTool())
        plot.add_tools(SaveTool())
        plot.add_tools(BoxZoomTool())
        plot.add_tools(ResetTool())
        plot.add_tools(hover_box)
        plot.add_tools(HoverTool(tooltips=[("Upper Whisker", "@uw")],
                                 mode="mouse", names=["upper"]))
        plot.add_tools(HoverTool(tooltips=[("Lower Whisker", "@lw")],
                                 mode="mouse", names=["lower"]))
        plot.add_tools(HoverTool(tooltips=[("Value", "@y")], names=["outlier"]))

        yaxis = LinearAxis()
        xaxis = LinearAxis()

        plot.add_layout(yaxis, 'left')
        plot.add_layout(xaxis, 'below')

        plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
        plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
        plot.xaxis.major_label_orientation = math.pi / 4
        plot.yaxis.axis_label = col_y
        plot.xaxis.ticker = FixedTicker(ticks=list(d_f["x"]))
        plot.xaxis.formatter = FuncTickFormatter(code="""
            var mapping = """ + str({key: value for key, value in zip(d_f["x"], d_f.index)})+""";
            return mapping[tick];
        """)
        self.box = True
        plot.title.text_font_size = "10pt"
        return plot
        # pytype: enable=import-error