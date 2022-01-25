# //
# // Quick Image
# //
# quickImage: (args) => {
#     const card = silverSpectacle.createCard({children:[]})
#     const saveImageButton = document.createElement("a")
    
#     //
#     // canvas sizing
#     //
#     // const canvas = document.createElement("canvas")
#     // canvas.style.maxWidth = "100%"
#     // canvas.style.maxHeight = "40rem"
#     // canvas.style.transition = "all 0.25s ease-out 0s"
#     // canvas.style.transform = "scale(1.001)" // fixes a pixel glitch
#     // canvas.style.width = "unset"
#     // canvas.style.padding = "0"
#     // canvas.classList.add("card")
#     // card.style.background = "transparent"
#     // card.style.boxShadow = "unset"
    
#     //
#     // add image data
#     //
#     const putImageIntoCanvas = (rgbImage) => {
#         const width = rgbImage[0].length
#         const height = rgbImage.length
#         canvas.height = height
#         canvas.width = width
#         if (canvas.height > canvas.width) {
#             canvas.style.height = canvas.style.maxHeight
#         } else {
#             canvas.style.width = canvas.style.maxWidth
#         }
#         const listOfPixels = rgbImage.flat()
#         let rgba
#         if (listOfPixels[0].length != 4) {
#             rgba = listOfPixels.map(each=>each.concat([255]))
#         } else {
#             rgba = listOfPixels
#         }
#         const flattenedRgba = rgba.flat()
#         const dataArray = new Uint8ClampedArray(flattenedRgba)
#         let imageData
#         try {
#             imageData = new ImageData(dataArray, width, height)
#         } catch (error) {
#             imageData = canvas.getContext("2d").getImageData(0, 0, width, height)
#             imageData.data = dataArray
#         }
#         try {
#             canvas.getContext("2d").putImageData(imageData, 0, 0)
#         } catch (error) {
#         }
#         // update the save button link
#         saveImageButton.setAttribute("href", canvas.toDataURL("image/png").replace("image/png", "image/octet-stream"))
#     }
#     // putImageIntoCanvas(args[0]) // dimensions: width, height, rgb
#     const putImageIntoCard = (imageExtension)=> {
#         const imageElement = document.createElement("img")
#         imageElement.src = "/large/get/"+imageExtension
#         imageElement.style.width = "100%"
#         imageElement.style.imageRendering = "crisp-edges"
#         card.innerHTML = ""
#         card.appendChild(imageElement)
#     }
    
#     //
#     // dynamic update
#     //
#     card.receive = (imageExtension) => {
#         putImageIntoCard(imageExtension)
#     }
    
#     putImageIntoCard(args[0])
#     return card
# },