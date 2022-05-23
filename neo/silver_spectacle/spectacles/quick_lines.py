from blissful_basics import print, flatten, to_pure, stringify, stats, product, countdown, is_generator_like, now, large_pickle_save, large_pickle_load, FS, Object
from super_hash import super_hash

from silver_spectacle.runtime import Spectacle

@Spectacle()
class QuckLine:
    script = """<script>
        import { silverSpectacle } from "https://deno.land/x/silver_spectacle@0.0.1/main.js"
        import { createChart, convertXYData, generateLabelsFor } from "https://deno.land/x/silver_spectacle@0.0.1/imports/96b4defae9008199461a506159967e93.js"
        import { merge } from "https://deno.land/x/good@0.5.12/object.js"

        const quickLinesConfig = ({lines, verticalLabel=null, horizonalLabel=null, title=null, lineColor={}, options={}}) => {
            // generate datasets
            const datasets = []
            let index = 0
            for (const [key, value] of Object.entries(lines)) {
                index += 1
                datasets.push({
                    label: key,
                    data: convertXYData(value),
                    fill: false,
                    tension: 0.4,
                    cubicInterpolationMode: 'monotone',
                    backgroundColor: lineColor[key] || silverSpectacle.theme.colorFor(index),
                    borderColor: lineColor[key] || silverSpectacle.theme.colorFor(index),
                    color: lineColor[key] || silverSpectacle.theme.colorFor(index),
                })
            }
            
            const config = {
                "type": 'line',
                "data": {
                    "datasets": datasets,
                },
                "options": merge({ // merge is done recursively
                    oldData: {
                        "plugins": {
                            "title": {
                                "display": !!title,
                                "text": title,
                            }
                        },
                        pointRadius: 3, // the size of the dots
                        pointHoverRadius: 8,
                        "scales": {
                            "x": {
                                type: "linear",
                                position: "bottom",
                                "title": {
                                    "display": horizonalLabel,
                                    "text": horizonalLabel,
                                },
                            },
                            "y": {
                                type: "linear",
                                position: "left",
                                "title": {
                                    "display": verticalLabel,
                                    "text": verticalLabel,
                                },
                            },
                        }
                    },
                    newData: options,
                })
            }
            generateLabelsFor(config)
            return config
        }
        
        const elements = {}
        const configFor = {}
        silverSpectacle.register({
            spectacleClassId: """+f'"{Spectacle.get_class_id()}"'+""",
        
            // create an element
            async init({instanceId, data}) {
                configFor[instanceId] = quickLinesConfig(data)
                return elements[instanceId] = createChart(configFor[instanceId])
            },
            
            // change the element when data changes
            async onDataChange({ instanceId, data, path, action, args, time }) {
                // change the element somehow when the data changes
                const element = elements[instanceId]
                const oldConfig = configFor[instanceId]
                const newConfig = quickLinesConfig(data)
                
                const chart = element.chartJsChart
                for (const [key, value] of Object.entries(newConfig)) {
                    // ex: chart.data.datasets
                    chart[key] = value
                }
                // chart will update on its own after a second
            }
        })
    </script>"""
    
    def __init__(self, lines, vertical_label=None, horizonal_label=None, title=None, line_color={}, options={}):
        self.data.update(dict(
            lines=lines,
            title=title,
            verticalLabel=vertical_label,
            horizonalLabel=horizonal_label,
            lineColor=line_color,
            options=options,
        ))