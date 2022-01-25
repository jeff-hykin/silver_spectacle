# //
# // Quick Line
# //
# quickLine: (args) => {
#     let data = args[0]
#     if (!(data instanceof Array)) {
#         throw Exception(`quickLine needs an array [[x1,y1],[x2,y2] ...] but it got this instead:\n    ${JSON.stringify(data)}`)
#     }
#     // if single numbers instead of pairs
#     if (! _.isNaN(_.toNumber(data[0])) ) {
#         // make them pairs
#         data = data.map((each,index)=>([index,each]))
#     }
    
#     const config = {
#         type: "line",
#         data: {
#             datasets: [
#                 {
#                     label: "Quick Line",
#                     data: data.map(([x, y])=>({x,y})),
#                     backgroundColor: silverSpectacle.colors(0),
#                     borderColor: silverSpectacle.colors(0),
#                     color: silverSpectacle.colors(0),
#                     cubicInterpolationMode: 'monotone',
#                     tension: 0.4,
#                 },
#             ],
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
#     card.receive = (arg) => {
#         if (arg == "clear") {
#             card.chartJsChart.data.datasets[0].data = []
#             card.chartJsChart.update()
#         } else {
#             if (arg instanceof Array && arg.length) {
#                 if (!(arg[0] instanceof Array)) {
#                     const [x,y] = arg
#                     card.chartJsChart.data.datasets[0].data.push({x,y})
#                 } else {
#                     for (const [x,y] of arg) {
#                         card.chartJsChart.data.datasets[0].data.push({x,y})
#                     }
#                     card.chartJsChart.update()
#                 }
#             }
#         }
#     }
#     return card
# },