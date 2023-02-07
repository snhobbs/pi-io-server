import numpy as np

# import scipy
# from scipy import fftpack
import pandas as pd

# import dash
import dash_core_components as dcc

# import dash_html_components as html
# from dash.dependencies import Input, Output, State
# import dash_table
# import dash_daq as daq

# import plotly.graph_objs as go
# import plotly.express as px
# import plotly.tools as tls
import plotly.subplots as tls
from python_utilities.utilities import fit_line
from MsdsControl import Transducers


def plot_analog_output(analog_file):
    data = pd.DataFrame({"Setting": analog_file.settings, "Reading": analog_file.volts})
    line = fit_line(data["Setting"], data["Reading"])
    xlims = [min(analog_file.settings), max(analog_file.settings)]
    yfit = [
        xlims[0] * line["slope"] + line["intercept"],
        xlims[1] * line["slope"] + line["intercept"],
    ]

    figure = tls.make_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.009,
        horizontal_spacing=0.009,
    )
    figure.append_trace(
        {
            "x": data["Setting"],
            "y": data["Reading"],
            "mode": "markers",
            "type": "scatter",
            "name": "readings",
        },
        1,
        1,
    )
    figure.append_trace(
        {"x": xlims, "y": yfit, "type": "scatter", "mode": "lines", "name": "fit"}, 1, 1
    )
    figure.update_layout(
        xaxis_title="Setting (10 Bit)",
        yaxis_title="Measured Volts",
        title={
            "text": "Analog Output %s\n%.2fx+%.2f %.2f res"
            % (
                analog_file.channel,
                line["slope"],
                line["intercept"],
                line["residual"],
            ),
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )
    return dcc.Graph(figure=figure)


def plot_transducer_response(data, transducer):
    figure = tls.make_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.009,
        horizontal_spacing=0.009,
    )
    for emitter in data["emitter"].unique():
        df_emitter = data[data.emitter == emitter]
        figure.append_trace(
            {
                "x": df_emitter["setting"],
                "y": df_emitter["reading"],
                "mode": "markers",
                "type": "scatter",
                "name": emitter,
            },
            1,
            1,
        )
        figure.update_layout(
            xaxis_title="Emitter Setting (8 Bit)",
            yaxis_title="ADC Reading (14 Bit)",
            title={
                "text": f"{transducer}",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
        )
    return dcc.Graph(figure=figure)


def plot_histograms(data, transducer, emitter_settings):
    hist, edges = np.histogram(data, bins=16)
    figure = tls.make_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.009,
        horizontal_spacing=0.009,
    )
    figure.append_trace(
        {"x": edges[:-1], "y": hist, "mode": "lines+markers", "type": "scatter"}, 1, 1
    )
    # ax1.bar(, hist, align='center', width = 0.9*(edges[1] - edges[0]), color = 'r')
    if len(emitter_settings) == 0:
        title = f"{transducer} Dark"
    else:
        title = "{} {}".format(
            transducer,
            ",".join(
                [
                    "{}: {} ".format(emitter, setting)
                    for emitter, setting in emitter_settings
                ]
            ),
        )

    figure.update_layout(
        xaxis_title="ADC Reading (14 Bit)",
        yaxis_title="Count",
        title={
            "text": title,
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )
    return dcc.Graph(figure=figure)


def make_transducer_plots(data_run_container):
    plots = []
    emitter_runs = data_run_container.emitter_runs
    responses = (
        pd.DataFrame()
    )  # dict([(transducer, dict()) for transducer in GetActiveTransducers()])
    for run in emitter_runs:
        # only one emitter
        emitters = list([item for item in run.emitter_settings.items() if item[1] > 0])
        if len(emitters) != 1 or run.transducer not in [t.name for t in Transducers]:
            continue
        emitter, setting = emitters[0]
        reading = np.mean(run.sensor_data)
        row = {
            "transducer": run.transducer,
            "emitter": emitter,
            "setting": setting,
            "reading": reading,
        }
        responses = responses.append(row, ignore_index=True)

    if len(responses) > 1:
        for transducer in sorted(responses["transducer"].unique()):
            transducer_df = responses[responses["transducer"] == transducer]
            plots.append(plot_transducer_response(transducer_df, transducer))
    return plots


def make_emitter_board_transducer_plots(data_run_container, channel=0):
    plots = []
    emitter_runs = data_run_container.emitter_runs
    responses = (
        pd.DataFrame()
    )  # dict([(transducer, dict()) for transducer in GetActiveTransducers()])
    included_points = []
    for run in emitter_runs:
        # only one emitter
        emitters = list([item for item in run.emitter_settings.items() if item[1] > 0])
        if len(emitters) != 1 or run.transducer not in [t.name for t in Transducers]:
            continue
        if emitters[0] in included_points:
            continue

        emitter, setting = emitters[0]
        included_points.append(emitters[0])
        reading = None
        if channel == 0:
            reading = np.mean(run.adc0)
        elif channel == 1:
            reading = np.mean(run.adc1)
        elif channel == 2:
            reading = np.mean(run.adc2)
        elif channel == 3:
            reading = np.mean(run.adc3)
        else:
            raise ValueError("Channel needs to be 0, 1, 2, or 3: %d"%channel)

        row = {
            "transducer": "Emitter Board Channel {}".format(channel),
            "emitter": emitter,
            "setting": setting,
            "reading": reading,
        }
        responses = responses.append(row, ignore_index=True)

    if len(responses) > 1:
        for transducer in sorted(responses["transducer"].unique()):
            transducer_df = responses[responses["transducer"] == transducer]
            plots.append(plot_transducer_response(transducer_df, transducer))
    return plots


def make_histogram_plots(data_run_container):
    plots = []
    emitter_runs = data_run_container.emitter_runs
    for run in emitter_runs:
        # Emitter data is list of key value pairs
        emitters = list([item for item in run.emitter_settings.items() if item[1] > 0])
        emitters.sort(reverse=True)
        # if len(emitters) > 0:
        #    continue
        assert run.transducer in [t.name for t in Transducers]
        plots.append(
            plot_histograms(run.sensor_data, run.transducer, emitters)
        )
    return plots


def make_dark_histograms(data_run_container):
    plots = []
    adc1 = []
    adc2 = []

    df_dark = data_run_container.emitter_run_df[data_run_container.emitter_run_df.emitter == "None"]
    transducer_dark = {
        t: [] for t in df_dark.transducer.unique()
    }
    for _, line in df_dark.iterrows():
        # Combine all the emitter board readings
        adc1.extend(line.adc1)
        adc2.extend(line.adc2)
        transducer_dark[line.transducer].extend(line.reading)

    plots.append(plot_histograms(adc1, "Emitter Board ADC1", []))
    plots.append(plot_histograms(adc2, "Emitter Board ADC2", []))

    for transducer, data in sorted(transducer_dark.items()):
        plots.append(plot_histograms(data, transducer, []))
    return plots


"""
def plot_fft(data, frequency, transducers, emitter_settings, title_base="Emitter Board"):
    transducer = transducers[0]
    fft = scipy.fft(data)
    dt = 1.0 / frequency
    # x = np.linspace(0.0, len(fft)*dt, len(fft), endpoint=False)
    xf = fftpack.fftfreq(len(fft), dt)
    xf = fftpack.fftshift(xf)
    yplot = np.abs(fftpack.fftshift(fft)) / len(fft)

    figure = tls.make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.009, horizontal_spacing=0.009)
    figure.append_trace({"y": yplot, "x": xf, "mode": "lines+markers", "type": "scatter"}, 1, 1)
    # ax1.bar(, hist, align='center', width = 0.9*(edges[1] - edges[0]), color = 'r')
    if len(emitter_settings) == 0:
        title = "{} {} Dark".format(title_base, transducer)
    else:
        title = "{} {} {}".format(title_base, transducer, ",".join(["{}: {} ".format(emitter, setting) for emitter, setting in emitter_settings]))

    figure.update_layout(title={"text": title, "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"})
    figure.update_yaxes(type="log")
    return dcc.Graph(figure=figure)

def make_emitter_board_ffts(data_run_container):
    plots = []
    emitter_runs = data_run_container.emitter_runs
    for run in emitter_runs:
        emitters = list([item for item in run.emitter_settings.items() if item[1] > 0])
        emitters.sort(reverse=True)
        assert len(run.transducers) == 1
        plots.append(plot_fft([pt[0] for pt in run.emitter_data.data], run.emitter_data.data["frequency"], run.transducers, emitters, title_base="Emitter Board ADC0"))
        plots.append(plot_fft([pt[1] for pt in run.emitter_data.data], run.emitter_data.data["frequency"], run.transducers, emitters, title_base="Emitter Board ADC1"))
    return plots


def make_sensor_ffts(data_run_container):
    plots = []
    emitter_runs = data_run_container.emitter_runs
    for run in emitter_runs:
        emitters = list([item for item in run.emitter_settings.items() if item[1] > 0])
        emitters.sort(reverse=True)
        assert len(run.transducers) == 1
        plots.append(plot_fft(run.sensor_data.data, run.sensor_data.frequency, run.transducers, emitters, title_base="Sensor"))
    return plots
"""
