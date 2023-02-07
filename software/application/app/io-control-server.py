from operator import itemgetter
import sys
import os
import datetime
from urllib.parse import urlparse
import socket

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq

import dash_plots
# from tools import *
import tools
import click
import logging

kFinishedPercent = 100
kStartPercent = 0
kHostName = socket.gethostname()
kDataViewUrl = "data-view"

server_host, server_port = "0.0.0.0", 8000

ordered_status_items = [
    "Datetime",
    "version",
    "firmware_version",
    "serial_number",
    "compile_time",
    "compile_date",
    "fault_status",
    "p23_micro_volts",
    "p3_3_micro_volts",
    "p5_micro_volts",
]

kBackground = "#1e2130"

no_entries = [{"value": "", "label": ""}]
external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    # external_scripts=external_scripts
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.config["suppress_callback_exceptions"] = True

app.title = "io-control"
# app.config["suppress_callback_exceptions"] = True
# APP_PATH = str(pathlib.Path(__file__).parent.resolve())

# id_suffix = "-data-view"

cache = {"ideal_data_run_container": None}


def get_ideal_data_run_container():
    entry_name = "ideal_data_run_container"
    if cache[entry_name] is None:
        ideal_data_run_dir = get_ideal_data_run_dir(data_dir=kDataDir)
        if ideal_data_run_dir is not None:
            args = parse_run_directory_path(ideal_data_run_dir)
            cache[entry_name] = load_data_run_container(*args)
    return cache[entry_name]


def UpdateInterval():
    interval = dcc.Interval(
        id="interval-component",
        interval=500,  # * 1000,  # in milliseconds
        n_intervals=0,
        disabled=False,
    )
    return interval


def get_layout(id_suffix="-data-view"):
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div([html.Div(id="content")]),
        ]
    )


app.layout = get_layout("")


def wrap_center_row(children):
    return html.Div(className="row justify-content-center", children=[html.Div(className="col-sm-12 col-md-10 col-lg-8", children=children)])


def RunControl(app_suffix=""):
    return html.Div(
        id="RunControl",
        children=[
            dcc.Store(id="button-state" + app_suffix, data={"control": 0, "reset": 0}),
            html.Div(
                [
                    html.Div(
                        [
                            daq.StopButton(id="control-button" + app_suffix, size=100, n_clicks=0, disabled=True, buttonText="Start"),
                        ]
                    ),
                ]
            ),
        ],
    )


def RunProgress(app_suffix=""):
    return html.Div(
        id="RunProgress",
        style={"text-align": "center"},
        children=[
            html.H4("Run Status"),
            html.Div([html.P(id="run-status" + app_suffix, children="Not Started")]),
            html.Div(
                [
                    html.P(id="time-remaining" + app_suffix, children=0),
                ]
            ),
            html.Div(
                daq.GraduatedBar(
                    id="progress-bar" + app_suffix,
                    color="green",
                    style={"color": "white"},
                    showCurrentValue=True,
                    step=5,
                    max=100,
                    min=0,
                )
            ),
            html.Br(),
        ],
    )


def RenderMainView(app_suffix=""):
    return html.Div(
        className="row justify-content-center",
        style={"background-color": "black"},
        children=[
            html.Div(
                className="col-md-11 col-sm-12 col-lg-10",
                style={"background": kBackground},
                children=[
                    html.H4(dcc.Link("Data View", href="/%s"%kDataViewUrl)),
                    html.Div(
                        id="card-2",
                        children=[
                            html.Div(
                                children=[
                                    html.H2("MSDS Test Jig Control"),
                                    html.H4("Host: %s "%kHostName),
                                ],
                                style={"text-align": "center"},
                            ),
                            RunProgress(),
                            RunControl(),
                        ],
                    ),
                    html.Div(id="run-summary", children=None),
                ],
            ),
            dcc.Store(id="run-status-data" + app_suffix, data=tools.get_run_status(server_host, server_port)),
            dcc.Store(id="run-summary-state" + app_suffix, data=""),
            UpdateInterval(),
        ],  # , style={"width":"100%"}
    )


def RenderRunStatusSummary(data):
    status_file = data.status
    children = []
    try:
        status_entries = sorted(sorted(list(status_file.items()), key=itemgetter(0)), key=lambda x: x[0] in ordered_status_items, reverse=True)
        children.append(
            html.Div([
                html.H4("Status File"),
                dcc.Markdown("\n".join("{}: {}\n".format(key, value) for key, value in status_entries))
            ]))
    except FileNotFoundError:
        pass
    return children


def RenderFullReport(sensor_dir):
    children = [
        html.H4("Host: %s "%kHostName),
        html.H4(dcc.Link("Go Back Home", href="/")),
        html.H4(dcc.Link("Data View", href="/%s"%kDataViewUrl))]
    plots = []
    try:
        args = parse_run_directory_path(sensor_dir)
        data = load_data_run_container(*args)
    except IndexError:
        return "No directory matching criteria"
    except FileNotFoundError:
        return "Incomplete Run Data"

    faults = get_faults(data, get_ideal_data_run_container())
    if len(faults) > 0:
        faults_div = html.Div([html.H3("Faults"), html.Ul([html.Li(str(fault)) for fault in faults])])
    else:
        faults_div = html.Div()

    plots.append(faults_div)
    plots.extend(RenderRunStatusSummary(data))
    try:
        plots.append(dash_plots.plot_analog_output(data.analog_output_0))
        plots.append(dash_plots.plot_analog_output(data.analog_output_1))
    except FileNotFoundError:
        pass
    try:
        plots.extend(dash_plots.make_transducer_plots(data))
    except (FileNotFoundError, IndexError):
        pass
    try:
        plots.extend(dash_plots.make_emitter_board_transducer_plots(data, 1))
        plots.extend(dash_plots.make_emitter_board_transducer_plots(data, 2))
    except (FileNotFoundError, IndexError):
        pass
    try:
        plots.extend(dash_plots.make_dark_histograms(data))
    except (FileNotFoundError, IndexError):
        pass
    # try:
        # plots.extend(make_sensor_ffts(data))
        # plots.extend(make_emitter_board_ffts(data))
    # except (FileNotFoundError, IndexError):
    #    pass

    children.extend(plots)
    if len(plots) == 0:
        children.append(html.H3("No Data Plots"))
    return html.Div(children)


def RenderRunList(df, sn, fwv, time):
    firmware_versions = [html.P(dcc.Link(str(fwv), href=tools.make_run_url(sn=sn, fwv=fwv, time=time))) for fwv in sorted(df.firmware_version.unique())]
    serial_numbers = [html.P(dcc.Link(str(sn), href=tools.make_run_url(sn=sn, fwv=fwv, time=time))) for sn in sorted(df.serial_number.unique())]
    times = [html.P(dcc.Link(str(time), href=tools.make_run_url(sn=sn, fwv=fwv, time=time))) for time in sorted(df.time.unique())]

    children = [
        html.H4("Host: %s "%kHostName),
        html.H4(dcc.Link("Go Back Home", href="/")),
        html.H4(dcc.Link("Data View", href="/%s"%kDataViewUrl))]
    children.append(html.H4("Serial Numbers"))
    children.extend(serial_numbers)
    children.append(html.H4("Firmware Version"))
    children.extend(firmware_versions)
    children.append(html.H4("Time"))
    children.extend(times)
    return html.Div(children, className="container")


def RenderDataView(sn, fwv, time):
    df = DataTree(kDataDir).df

    if sn in list(df["serial_number"]):
        df = df[df["serial_number"] == sn]
    if fwv in list(df["firmware_version"]):
        df = df[df["firmware_version"] == fwv]
    if time in list(df["time"]):
        df = df[df["time"] == time]

    if len(df) == 1:
        run = list(df["dir"])[0]
        children = RenderFullReport(run)
    else:
        children = RenderRunList(df, sn, fwv, time)
    return html.Div(
        className="row justify-content-center",
        style={"background-color": "black"},
        children=[
            html.Div(
                # classname="col-md-12 col-sm-12 col-lg-12",
                className="col-md-11 col-sm-12 col-lg-10",
                style={"background": kBackground},
                children=children,
            )
        ],
    )


def RenderRunSummary(sensor_dir):
    try:
        args = parse_run_directory_path(sensor_dir)
        data = load_data_run_container(*args)
        if data.run_summary is None:
            args = parse_run_directory_path(sensor_dir)
            data = load_data_run_container(*args)
    except IndexError:
        return "No directory matching criteria"

    time = data.time
    if isinstance(time, datetime.datetime):
        time = time.isoformat()
    assert isinstance(time, str)
    url = tools.make_run_url(kDataViewUrl, data.status["serial_number"], data.status["firmware_version"], time)
    faults = get_faults(data, get_ideal_data_run_container())

    result = RunResult.incomplete
    if data.finished and len(faults) == 0:
        result = RunResult.passed
    elif data.finished and len(faults) > 0:
        result = RunResult.failed

    if result == RunResult.passed:
        text = "Passed"
        color = "green"
    elif result == RunResult.failed:
        text = "Failed"
        color = "red"
    else:
        text = "Incomplete"
        color = "gold"

    children = [html.Div(html.H2(text), style={"background": color, "text-align": "center"}), html.H3(dcc.Link("Full Report", href=url))]
    # *RenderRunStatusSummary(data)]

    if len(faults) > 0:
        faults_div = html.Div([html.H3("Faults"), html.Ul([html.Li(str(fault)) for fault in faults])])
    else:
        faults_div = html.Div()

    children.append(html.Div([faults_div, html.H4("Status File"), html.Div([html.P("{}: {}".format(key.replace("_", " ").title(), data.status[key])) for key in ordered_status_items])]))
    return html.Div(children)


@app.callback(output=[dash.dependencies.Output("content", "children")], inputs=[dash.dependencies.Input("url", "pathname")])
def display_page(pathname):
    parse = urlparse(pathname)
    branch, sn, fwv, time = tools.ParseUrl(parse.path)
    if branch.lower() == kDataViewUrl:
        children = RenderDataView(sn, fwv, time)
    else:
        children = RenderMainView()
    return [children]


@app.callback(
    inputs=[Input("run-status-data", "data")],
    # inputs=[Input("interval-component", "n_intervals")],
    output=[Output("run-summary", "children")],
    state=[]
    # state=[State("run-status-data", "data")]
)
def update_run_status(run_status):
    # def update_run_summary(n_intervals, run_status):
    run_summary = ""
    if run_status["percent"] == kFinishedPercent:
        # Request the server to process the data
        path = ""
        try:
            path = run_status["sensor_dir"]
            path_sections = path.split(os.path.sep)
            sensor_path = os.path.join(kDataDir, *path_sections[-3:])
            run_summary = RenderRunSummary(sensor_path)
        except (KeyError, IndexError, AttributeError) as e:
            logging.getLogger().error(f"Error loading summary for %s (%s, %s)", path, type(e), str(e))
    return [run_summary]


"""
@app.callback(
    inputs=[Input("interval-component", "n_intervals"), Input("button-state", "data")],
    output=[Output("run-status-data", "data"), Output("interval-component", "disabled")])
def update_run_status(n_intervals, n_clicks):
    run_status = tools.get_run_status(server_host, server_port)
    return [run_status, run_status["percent"] == kFinishedPercent or run_status["state"] == "Ready"]
"""


@app.callback(inputs=[Input("run-status-data", "data")], output=[Output("time-remaining", "children"), Output("progress-bar", "value"), Output("run-status", "children")])
def update_run_progress(run_status):
    return [int(run_status["time_remaining"]), run_status["percent"], run_status["state"]]


# Store last state from the process monitoring, use this to determine mode
@app.callback(
    inputs=[Input("interval-component", "n_intervals"), Input("control-button", "n_clicks")],
    output=[Output("button-state", "data"), Output("control-button", "disabled"), Output("control-button", "buttonText"), Output("run-status-data", "data"), Output("interval-component", "disabled")],
    state=[State("button-state", "data")],
)
def run_control_buttons(n_intervals, control_nclicks, button_state):
    run_status = tools.get_run_status(server_host, server_port)
    disable_interval = run_status["percent"] == kFinishedPercent or run_status["state"] == "Ready"

    text = "Start"
    command = "start"
    if run_status["state"] != "Ready" and run_status["state"] != "No Data":
        text = "Reset"
        command = "stop"
        disable_interval = run_status["percent"] == kFinishedPercent

    if control_nclicks > button_state["control"]:
        tools.send_command(command, server_host, server_port)
        button_state["control"] = control_nclicks
        disable_interval = False

    return button_state, run_status["state"] == "No Data", text, run_status, disable_interval


@click.option("--host", "-h", type=str, default="localhost", help="Dash server IP Address")
@click.option("--port", "-p", type=int, default=80, help="Dash server port")
@click.option("--app-host", "-h", type=str, default=None, help="Socket server IP Address")
@click.option("--app-port", "-a", type=int, default=8000, help="Socket server port")
@click.option("--data-dir", "-d", type=str, default=SystemSettings.kDataDir, help="Data directory")
@click.command()
def main(host, port, app_host, app_port, data_dir):
    global server_host, server_port, kDataDir
    kDataDir = data_dir

    if app_host is None:
        app_host = host

    server_host = app_host
    server_port = app_port
    app.run_server(host=host, port=port, debug=True, threaded=False, processes=8)

if __name__ == "__main__":
    logging.basicConfig()
    main()
    # app.run_server(debug=True, threaded=True, processes=1)
    # app.run_server(debug=True, threaded=False, processes=8)
    #app.run_server(host="0.0.0.0", port=8000, debug=True, threaded=False, processes=8)
    #app.run_server(host="0.0.0.0", port=80, debug=False, threaded=False, processes=8)
    # app.run_server(host="0.0.0.0", port=8000, debug=True, threaded=False, processes=8)
    # app.server.run()
