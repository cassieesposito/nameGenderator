// let JSZip = require("jszip")
// let JSZipUtils = require("jszip-utils")

main = () => {
  let data = loadData()
  document.getElementById("preformatted").innerHTML = JSON.stringify(data, null, 2)

}

loadData = () => {

  dataStructure = {
    "Kyle": {
      2010: { "girls": 33, boys: 3574 },
      2011: { "girls": 58, boys: 3265 },
      2013: { "girls": 52, boys: 2965 },
    },
    "Ashley": {
      2010: { "girls": 6314, "boys": 31 },
      2011: { "girls": 5399, "boys": 37 },
      2012: { "girls": 4700, "boys": 17 },
    }
  }
  return dataStructure
}

main()
