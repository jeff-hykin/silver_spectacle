## What is this?

Silver Spectacle is a python library for displaying data designed as a superior alternative to **matplotlib**; beautiful by default, fully customizable, minimal coding required, and lightweight.

## How do I use it?

Install just like any other pip module

`pip install silver_spectacle`

Then inside a python file (or the commandline)
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

Open the address in your browser and you'll see these <br>
<img src="/documentation/images/quick_scatter_2.png" alt="description">


## What kind of features does it have?

- Works everywhere: WSL, Docker, and ssh over VPN's. No more 5 page tutorials trying to get X11 forwarding to function
- Multiple plots are effortless: no more complex cramming of graphs together, or accidentally x-ing out that one graph you meant to take a screenshot of. Just call the function and forget about it, because you'll always be able to scroll down and find the graph later.
- Non-blocking: no more hacky workarounds or confusion about how to display data while performing additional computations in the background. `ss.display` is non-blocking by default, so use it without worrying if your overnight computation is going to stop in the middle because its waiting for user input.
- Interactive: I'm not saying its impossible for tools like matplotlib to be interactive, but lets just say nobody is doing it unless they have an unusual level of determination. Silver Spectacles are interactive almost by default.
- Independent runtime: your python program can crash, and as long as you were viewing the data in a browser, your graphs will still be there.

## What kind of plots can it do?

Well one of the libraries it includes is [Chart JS](https://www.chartjs.org/docs/latest/general/data-structures.html). So any of the examples there, such as this [line chart](https://www.chartjs.org/docs/latest/charts/line.html) can be converted like so:
<br>

Take a look at their `setup` tab

<img src="/documentation/images/setup_tab.png" alt="description">

Look at the `config` tab

<img src="/documentation/images/config_tab.png" alt="description">

<br>
Then make a *very* similar structure with a python dictionary

```python
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

## Documentation?

There is some additional documentation below for fully fledged customization of the javascript and css. However, this readme is currently all of the documentation. The power is in the flexibilty, not in the breadth of tools. Don't be afraid to open an issue asking for examples.

## Whats the status of the library?

There are many planned features, and this library is under active development, and as not been optimized. However, the API is stable, and effectively all changes will only be adding tools to the toolbox. Some of the planned features are small, like a button for clearing the screen of existing graphs, or options to save all the data as a file. Other features will be a major addition, like theming, notifications for errors, and integration with other major Javascript charts/graphing libraries. Development probably will be sporadic, PR's are welcome.

## How can I contribute?

- All the dependencies / setup instuctions are in `documentation/SETUP.md`.
- That^ will automatically create a venv environment for testing/development
- You can modify the files under `./main/silver_spectacle/`
    - `./main/silver_spectacle/library.py` is the code that actually gets imported
    - `./main/silver_spectacle/server.py` is the code that is run inside of a subprocess
    - `./main/silver_spectacle/index.html` is simply imported by the server
- After modification, you can use the `commands/project/local_install` command to install the local version you've created
- Then you can test to your 

## How does it work? 

- The system uses `socket.io` and `aiohttp` to get a push notification-like effect within browser windows.
- Everytime the `display` function is called the library checks if the display server is running (using an http request). If the server is not running, then it starts the server as a subprocess in the background. It waits until the server is responding, then it uses http requests to tell the server about the data it wants to display.
- The server does two things
    1. It embeds this data into the html as JSON data. This way any newly-opened pages already have all the available data. In terms of files, the server only serves the one html+js+css file.
    2. When the backend gets a http display request from the python process, it uses socket.io to notify all existing browser windows about the new data. 
- This seems trivial, but it is important: exising browswer windows do not replace existing data with incoming data. That would be bad because browser windows can be open longer than both the server process or python process. So, the browser window can have more information than the server does. For that reason, all data is timestamped and stored inside the global `displayRequests` variable. Those timestamps are used as keys, allowing the browser windows to simply merge incoming data without duplication and without loosing old information.
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