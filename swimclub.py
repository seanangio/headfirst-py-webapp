import json
import statistics

import hfpy_utils

CHARTS = "charts/"
FOLDER = "swimdata/"
JSONDATA = "records.json"

def event_lookup(event):
    """Convert from filenames to dictionary keys.

    Given an event descriptor (the name of a swimmer's file), convert the descriptor into a lookup key which can be used with the 'records' dictionary.
    """
    
    conversions = {
        "Free": "freestyle",
        "Back": "backstroke",
        "Breast": "breastroke",
        "Fly": "butterfly",
        "IM": "individual medley",
    }

    *_, distance, stroke = event.removesuffix(".txt").split("-")
    lookup = f"{distance} {conversions[stroke]}"
    return lookup


def read_swim_data(filename):
    """Return swim data from a file.
    
    Given the name of a swimmer's file (in filename), 
    extract data, then return ito th te caller as a tuple.
    """

    swimmer, age, distance, stroke = filename.removesuffix(".txt").split("-")

    with open(FOLDER + filename) as file:
        lines = file.readlines()
        times = lines[0].strip().split(",")
    
    converts = []
    for t in times:
        # check for missing minutes value
        if ":" in t:
            minutes, rest = t.split(":")
            seconds, hundredths = rest.split(".")
        else:
            minutes = 0
            seconds, hundredths = t.split(".")
        converted_time = (int(minutes)*60*100) + (int(seconds)*100) + int(hundredths)   
        converts.append(converted_time)

    average = statistics.mean(converts)
    #mins_secs, hundredths = str(round(average/100, 2)).split(".")
    mins_secs, hundredths = f"{(average / 100):.2f}".split(".")
    mins_secs = int(mins_secs)
    minutes = mins_secs // 60
    seconds = mins_secs - minutes*60
    average = f"{minutes}:{seconds:0>2}.{hundredths}"
    #average = str(minutes) + ":" + str(seconds) + "." + hundredths

    return swimmer, age, distance, stroke, times, average, converts

def produce_bar_chart(fn, location=CHARTS):
    """Given the name of a swimmer's file, produce a HTML/SVG bar chart.
    Save the chart to the CHARTS folder. Return the path to the bar chart file.
    """
    swimmer, age, distance, stroke, times, average, converts = read_swim_data(fn)
    from_max = max(converts)
    times.reverse()
    converts.reverse()
    title = f"{swimmer} (Under {age}) {distance} {stroke}"
    
    header = f"""<!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="/static/webapp.css"/>
        </head>
        <body>
            <h2>{title}</h2>
        """
    
    body = ""
    for n, t in enumerate(times):
        bar_width = hfpy_utils.convert2range(converts[n], 0, from_max, 0, 350)
        body = body + f"""
                        <svg height="30" width="400">
                                    <rect height="30" width="{bar_width}" style="fill:rgb(0,0,255);" />
                                </svg>{t}<br />
                        """

    with open(JSONDATA) as jf:
        records = json.load(jf)

    COURSES = ("LC Men", "LC Women", "SC Men", "SC Women")
    times = []
    for course in COURSES:
        record_time = records[course][event_lookup(fn)]
        times.append(record_time)

    footer = f"""<p>Average time: {average}</p>
                 <p>M: {times[0]} ({times[2]})<br />W: {times[1]} ({times[3]})</p>
                </body>
            </html>
            """
    
    page = header + body + footer
    
    save_to = f"{location}{fn.removesuffix('.txt')}.html"
    with open(save_to, "w") as sf:
        print(page, file=sf)
    
    return save_to