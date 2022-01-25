# //
# // Multi Line
# //
# multiLine: (args) => {
#     let data = args[0]
#     if (!(data instanceof Object)) {
#         throw Exception(`multLine needs a dict { "name": [[x1,y1],[x2,y2] ...], ... }  but it got this instead:\n    ${JSON.stringify(data)}`)
#     }
    
#     // if single numbers instead of pairs
#     const nameToIndex = {}
#     let index = 0
#     for (const [key, value] of Object.entries(data)) {
#         nameToIndex[key] = index++
#         if (! _.isNaN(_.toNumber(value[0])) ) {
#             // make them pairs
#             data[key] = value.map((each,index)=>([index,each]))
#         }
#     }
    
#     const config = {
#         type: "line",
#         data: {
#             datasets: Object.entries(data).map(([key, value], index)=> ({
#                 label: key,
#                 data: value.map(([x, y])=>({x,y})),
#                 backgroundColor: silverSpectacle.colors(index),
#                 borderColor: silverSpectacle.colors(index),
#                 color: silverSpectacle.colors(index),
#                 cubicInterpolationMode: 'monotone',
#                 tension: 0.4,
#             })),
#         },
#         options: {
#             pointRadius: 3,
#             pointHoverRadius: 8,
#             color: "whitesmoke",
#             scales: {
#                 x: {
#                     type: "linear",
#                     position: "bottom",
#                 },
#                 y: {
#                     type: "linear",
#                     position: "left",
#                 },
#             },
#         },
#     }
#     let card = silverSpectacle.createComponent("chartjs", config)
#     // sender callback
#     card.receive = (data) => {
#         for (const [key, value] of Object.entries(data)) {
#             const index = nameToIndex[key]
#             if (!(value[0] instanceof Array)) {
#                 card.chartJsChart.data.datasets[index].data.push({x: value[0], y: value[1]})
#             } else {
#                 for (const [x,y] of value) {
#                     card.chartJsChart.data.datasets[index].data.push({x,y})
#                 }
#             }
#         }
#         card.chartJsChart.update()
#     }
#     return card
# },