## What is this?

Silver Spectacle is a python library for displaying data. Its designed as a (superior) alternative to **matplotlib**.
  - [Well designed](https://ryxcommar.com/2020/04/11/why-you-hate-matplotlib/) one liners that do everything
  - [Beautiful](https://www.reddit.com/r/learnpython/comments/gaxpbp/does_anyone_else_find_matplotlib_a_bit_ugly_are/) by default
  - Easy to customize, with [total control](https://github.com/jeff-hykin/silver_spectacle/blob/master/README.md#additional-documentation) over every visual element
  - Lightweight and reliable (no X11, QT, or tkinter dependencies)
  - Useful documentation (basic use-cases don't require [stack overflow questions with hundreds of upvotes](https://stackoverflow.com/questions/22276066/how-to-plot-multiple-functions-on-the-same-figure-in-matplotlib))

## How do I use it?

Install just like any other pip module

`pip install silver_spectacle`

Then inside a python file (or python repl) 
```python
import silver_spectacle as ss

ss.display("quickScatter", *[
    [1,2],
    [2,3.2]
])
# >>> Server started at: http://0.0.0.0:9900

ss.display("quickScatter", *[
    [1,2],
    [2,3],
    [5,5],
    [1.5, 2.3],
    [2,3.2]
])
```

Open the address in your browser and you should see these <br>
![quick_scatter_2](https://user-images.githubusercontent.com/17692058/127252592-830874fa-78f4-45ac-84d3-37dbc6cff1bc.png)

## What kind of plots can it do?

If [Chart JS](https://www.chartjs.org/docs/latest/general/data-structures.html) has it, then it is already available in this library. More visualization libraries like [plotly](https://plotly.com/javascript/3d-charts/) will be added to enable additional 2D plots, 3D charts, video/image integration, and more.
<br>

For example:
- Go to [Chart JS's website](https://www.chartjs.org/docs/latest/general/data-structures.html)
- Find a plot, such as [this line chart](https://www.chartjs.org/docs/latest/charts/line.html)
- Then do a near 1-to-1 mapping to python

For example, with that line chart, look at their `setup` tab
![setup_tab](https://user-images.githubusercontent.com/17692058/127252596-90333d78-8cd1-43ee-8764-c92ff90697b6.png)

Look at the `config` tab
![config_tab](https://user-images.githubusercontent.com/17692058/127252590-8542b31b-4f86-44f6-858a-0a89cfdc5fe0.png)
<br>

Then make a *very* similar structure with a python dictionary
```python
#
# setup tab part
#
labels = [ "January", "February", "March", "April", "May", "June", "July", ]
data = {
  "labels": labels,
  "datasets": [{
    "label": 'My First Dataset',
    "data": [65, 59, 80, 81, 56, 55, 40],
    "fill": False,
    "borderColor": 'rgb(75, 192, 192)',
    "tension": 0.1
  }]
}
#
# config tag part
#
config = {
  "type": 'line',
  "data": data,
}

#
# display the data
#
import silver_spectacle as ss
ss.display("chartjs", config)
```

## What kind of features does it have?

- **Works everywhere**: You can run this on your Raspberry Pi and view the results on your phone. It works whether it's WSL, Docker, or ssh over a VPN. No more 5 page tutorials about X11 forwarding, display variables, and editing config files.
- **Non-blocking**: No more [hacky/painful workarounds](https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib#33050617) to get both code to execute, and a graph to update at the same time. `ss.display` is non-blocking by default, so use it without worrying if your overnight computation is going to stop in the middle because its waiting for user input.
- **Multiple plots are effortless**: Graphs are displayed in a stream with the most recent one at the top. Just call display and forget about it. No more complex mashing of graphs together, or hassle of closing window after window, only to realize you meant to screenshot the one you just closed. 
- **Independent runtime**: If your main python program crashes that's fine, the cleanup function will intentionally leave the graph server running instead of killing it so you can still access your data. As long as you don't manually kill the server process, your data will be there.
- **Interactive**: I'm not saying its impossible for tools like matplotlib to have custom interactivity, but lets just say nobody is doing it unless they have an unusual level of determination. Silver Spectacles let's you add custom buttons, effects, etc with ease.

## Documentation?

There is some additional documentation below for fully fledged customization of the javascript and css. However, this readme is currently all of the documentation. The power is in the flexibilty, not in the breadth of tools. Don't be afraid to open an issue asking for examples.

## Whats the status of the library?

There are many planned features. This library is under active development, and has not been optimized. However, the API is stable, and effectively all changes will only be adding tools to the toolbox. Some of the planned features are small:
  - working with numpy/pytorch/tensorflow tensors without needing to convert
  - adding a button for clearing the screen of existing graphs
  - an option to save/load all visual data to a file

Other features will be a major additions 
  - integration with 3D plot libraries
  - graphs that incrementally update
  - tools for displaying images/videos
  - a simple system for combining/shaping graphs
  - a theming system
  - a simple interface for graphical plugins (buttons)
  - visual notifications for errors
 
Development will, more than likely, be sporadic, PR's are welcome.

## How can I contribute?

- All the dependencies / setup instuctions are in `documentation/SETUP.md`.
- That^ will automatically create a venv environment for testing/development
- You can modify the files under `./main/silver_spectacle/`
    - `./main/silver_spectacle/library.py` is the code that actually gets imported
    - `./main/silver_spectacle/server.py` is the code that is run inside of a subprocess
    - `./main/silver_spectacle/index.html` is simply imported by the server
- After modification, you can use the `commands/project/local_install` command to install the local version you've created

## How does it work? 

- The system uses `socket.io` and `aiohttp` to get a push notification-like effect within browser windows.
- Everytime the `display` function is called the library checks if the display server is running (using an http request). If the server is not running, then it starts the server as a subprocess in the background. It waits until the server is responding, then it uses http requests to tell the server about the data it wants to display.
- The server does two things
    1. It embeds this data into the html as JSON data. This way any newly-opened pages already have all the available data. In terms of files, the server only serves the one html+js+css file.
    2. When the backend gets a http display request from the python process, it uses socket.io to notify all existing browser windows about the new data. 
- This seems trivial, but it is important: exising browser windows do not replace existing data with incoming data. That would be bad because browser windows can be open longer than both the server process or python process. So, the browser window can have more information than the server does. For that reason, all data is timestamped and stored inside the global `displayRequests` variable. Those timestamps are used as keys, allowing the browser windows to simply merge incoming data without duplication and without loosing old information.
- On the graphical side, the browser iterates over all the display commands, creating a chart for each one, wrapping the chart in a thin container, and placing it into a vertical list. This vertical list is displayed in reverse; the most-recent graph is at the top.
- Thats it!


## Additional documentation


Here's the basic configuration for full customization.

```python
import silver_spectacle as ss

ss.configure(
    port=9900,
    custom_css="",
    # Note: currently custom CSS and JS only get applied when the server starts.
    # Meaning if the server is still running from an old process
    # (a zombie server beacuse the python program crashed suddenly),
    # then it will look like your custom CSS and javascript are not being applied
    custom_js="",
    server_start_timeout=10, # this is not very important
)
```


Here's a more full example.

```python
import silver_spectacle as ss
ss.configure(
    port=69420,
    custom_css="""
        
        body .card {
            background-color: gray;
            color: whitesmoke; /* font color */
        }
        
        body #stream-container {
            flex-direction: column; /* makes oldest graphs be at the top */
        }
        
        body {
            background: slategray !important; /* needs to be important to override other values */ 
        }
    """,
    custom_js="""
        window.onload = ()=>{
            alert("this is a pointless alert... but you can do it!")
        }
    """,
    server_start_timeout=10, # (seconds)
    # this^ is not very important
    # it is how long to wait if the server doesnt start at all
    # designed to fail without throwing an error encase the user 
    # is performing important computations
)
```

Right now, the javascript isn't designed to be hooked into, but it **is** javascript so there are hacky ways to hook into almost anything if you're creative.
