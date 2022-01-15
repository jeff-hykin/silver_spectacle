def init_spectacle(function_being_wrapped):
    def wrapper(*args, **kwargs):
        output = function_being_wrapped(*args, **kwargs)
        # FIXME: check output right here
        return output
    return wrapper

class TellBackend:
    def update_cached_data(self, keylist, value):
        # TODO
        pass
    
    def send_event(self, card_id, event_name):
        pass
    
    def add_new_tool(self, tool_info):
        # on_page_load
        # on_create_card
        # events={
        #     "clear": str, 
        #     "send": str,
        # }
        pass
    
    def update_theme(self,):
        # colors
        # css_vars
        # custom css
        pass

class CardMakerCore:
    @property
    def __cached_json_data__(self,):
        return self.___cached_json_data___
    
    def __update_cached_json_data__(self, keylist, new_value):
        # FIXME: make sure data is jsonable first
        TellBackend.update_cached_data([ "cards", self.__id__, *keylist ], new_value)
    
    # for iPython
    def __to_html__(self):
        # create an iframe
        #    create a simplified silver spectacle
        #       socket.io event handling?
        #    have a script that runs 
        #        on page load
        #        on create card
        #        then pushes it into the iframe body
        pass

# 
# example
# 
class QuickLine:
    class CardMaker(CardMakerCore):
        def __init__(self, *args, **kwargs):
            args = to_pure(each for each in args)
            if not isinstance(args[0], (tuple, list)):
                raise Exception(f"QuickLine needs an array [[x1,y1],[x2,y2] ...] but it got this instead:\n    {data}")
            
            self.__update_cached_json_data__([], new_value={ "elements": args })
        
        def clear(self, *args, **kwargs):
            # remove all the data
            self.__update_cached_json_data__([ "elements" ], new_value=[])
        
        def send(self, *args, **kwargs):
            new_elements = self.__cached_json_data__["elements"] + args
            self.__update_cached_json_data__([ "elements" ], new_value=new_elements)
        
    class JavaScript:
        __on_page_load__ = r"""
            async function(silverSpectacle) {
                import lodash from 'https://cdn.skypack.dev/lodash'
                return {
                    "lodash": lodash,
                    "silverSpectacle": silverSpectacle,
                }
            }
        """
        
        __on_create_card__ = r"""
            async function(libraries, cachedJsonData) {
                const silverSpectacle = libraries.silverSpectacle
                const _ = libraries.lodash
                
                //
                // check arguments
                //
                let data = cachedJsonData.values
                if (!(data instanceof Array)) {
                    throw Exception(`quickLine needs an array [[x1,y1],[x2,y2] ...] but it got this instead:\n    ${JSON.stringify(data)}`)
                }
                // if single numbers instead of pairs
                if (! _.isNaN(_.toNumber(data[0])) ) {
                    // make them pairs
                    data = data.map((each,index)=>([index,each]))
                }
                
                //
                // create element
                //
                return = silverSpectacle.createComponent("chartjs", config = {
                    type: "line",
                    data: {
                        datasets: [
                            {
                                label: "Quick Line",
                                data: data.map(([x, y])=>({x,y})),
                                backgroundColor: silverSpectacle.colors(0),
                                borderColor: silverSpectacle.colors(0),
                                color: silverSpectacle.colors(0),
                                cubicInterpolationMode: 'monotone',
                                tension: 0.4,
                            },
                        ],
                    },
                    options: {
                        pointRadius: 3,
                        pointHoverRadius: 8,
                        color: "whitesmoke",
                        scales: {
                            x: {
                                type: "linear",
                                position: "bottom",
                            },
                            y: {
                                type: "linear",
                                position: "left",
                            },
                        },
                    },
                })
            }
        """
        
        clear = r"""
            async function(libraries, cachedJsonData, element) {
                const silverSpectacle = libraries.silverSpectacle
                const _ = libraries.lodash
                
                // remove the data, then have it refresh itself
                element.chartJsChart.data.datasets[0].data = cachedJsonData.values
                element.chartJsChart.update()
            }
        """
        
        send = r"""
            async function(libraries, cachedJsonData, element) {
                
                const arg = args[0]
                if (arg instanceof Array && arg.length) {
                    if (!(arg[0] instanceof Array)) {
                        const [x,y] = arg
                        card.chartJsChart.data.datasets[0].data.push({x,y})
                    } else {
                        for (const [x,y] of arg) {
                            card.chartJsChart.data.datasets[0].data.push({x,y})
                        }
                        card.chartJsChart.update()
                    }
                }
            }
        """