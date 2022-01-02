let allNamesData = new Object()
let db_url = "https://us-west1-portfolio-334101.cloudfunctions.net/nameGenderator?name="
nextCol = 1

loadTable = async(thisCol) => {
    let babyName = document.getElementById("name" + thisCol).value
    await fetchNameData(babyName)
    let table = document.getElementById(`table${thisCol}`)
    let displayBy = document.getElementById(`displayBy${thisCol}`)
    if (displayBy.value == "Decade") { table.replaceWith(decadeTable(thisCol)) }
    if (displayBy.value == "Year") { table.replaceWith(yearTable(thisCol)) }
}


decadeTable = (thisCol) => {
    let babyName = document.getElementById(`name${thisCol}`).value
    let nameData = Object.entries(allNamesData[babyName]).sort()

    let start = findStart(thisCol, nameData)
    let end = findEnd(thisCol, nameData)


    let totals = sumNameData(nameData, start, end)
    let decadeTotals = Object.entries(totals.decade).sort()

    let table = newElement("table", { "id": `table${thisCol}` })
    table.appendChild(tableRow("Decade", "Female", "Male"))

    let onlyDecadePartial = (decade(start) == decade(end) && end % 10 != 9)
    if (onlyDecadePartial) {
        table.appendChild(tableRow(`${start}-${end}`, decadeTotals[0][1].female, decadeTotals[0][1].male))

        decadeTotals.splice(0, 1)
    }

    let partialFirstDecade = (start % 10 && decadeTotals[0])
    if (partialFirstDecade) {
        table.appendChild(tableRow(
            `${start}-${Math.floor(start/10)*10+9}`,
            decadeTotals[0][1].female,
            decadeTotals[0][1].male
        ))
        decadeTotals.splice(0, 1)
    }

    let finalRow = false
    let partialLastDecade = ((end % 10 != 9) && decadeTotals[0])
    if (partialLastDecade) {

        finalRow = tableRow(
            `${Math.floor(end/10)*10}-${end}`,
            decadeTotals[decadeTotals.length - 1][1].female,
            decadeTotals[decadeTotals.length - 1][1].male
        )
        decadeTotals.splice(decadeTotals.length - 1, 1)

    }

    decadeTotals.forEach(([decade, total]) => {

        table.appendChild(tableRow(decade, total.female, total.male))
    })

    if (finalRow) {
        table.appendChild(finalRow)
    }
    table.appendChild(tableRow(`<b>TOTAL</b>`, `${totals.grand.female}`, `${totals.grand.male}`))


    return table
}

findStart = (thisCol, nameData) => {
    let start = document.getElementById(`startYear${thisCol}`).value
    start = start != "" ? start : nameData[0][0]
    return start > nameData[0][0] ? start : nameData[0][0]
}

findEnd = (thisCol, nameData) => {
    let end = document.getElementById(`endYear${thisCol}`).value
    end = end != "" ? end : nameData[nameData.length - 1][0]
    return end < nameData[nameData.length - 1][0] ? end : nameData[nameData.length - 1][0]
}

sumNameData = (nameData, start, end) => {
    let totals = {
        grand: { female: 0, male: 0 },
        decade: {},
    }

    nameData.forEach(([year, data]) => {
        if ((start <= year) && (year <= end)) {
            if (!(decade(year) in totals)) { totals.decade[decade(year)] = { female: 0, male: 0 } }
            totals.grand.female += data["female"]
            totals.grand.male += data["male"]
            totals.decade[decade(year)].female += data["female"]
            totals.decade[decade(year)].male += data["male"]
        }
    })

    return totals
}


decade = (year) => {
    return Math.floor(year / 10) * 10 + "s"
}

yearTable = (thisCol) => {
    let babyName = document.getElementById(`name${thisCol}`).value
    let nameData = Object.entries(allNamesData[babyName]).sort()

    let start = findStart(thisCol, nameData)
    let end = findEnd(thisCol, nameData)


    let grandTotal = { female: 0, male: 0 }

    let table = newElement("table", { "id": `table${thisCol}` })
    table.appendChild(tableRow("Year", "Female", "Male"))
    nameData.forEach(([year, data]) => {
        console.log()
        if ((start <= year) && (year <= end)) {
            table.appendChild(tableRow(year, data["female"], data["male"]))
            grandTotal.female += data["female"]
            grandTotal.male += data["male"]
        }
    })
    table.appendChild(tableRow(`<b>TOTAL</b>`, `<b>${grandTotal.female}</b>`, `<b>${grandTotal.male}</b>`))
    return table
}


tableRow = (data1 = "", data2 = "", data3 = "") => {
    let row = newElement("tr")
    let cell1 = newElement("td")
    let cell2 = newElement("td", { "class": "number" })
    let cell3 = newElement("td", { "class": "number" })

    cell1.innerHTML = data1
    cell2.innerHTML = data2
    cell3.innerHTML = data3

    row.appendChild(cell1)
    row.appendChild(cell2)
    row.appendChild(cell3)

    return row
}




fetchNameData = async(babyName) => {
    console.log(`Fetching ${babyName}`)
    if (babyName && !allNamesData[babyName]) {
        response = await fetch(db_url + babyName, { cache: "force-cache" })
        allNamesData[babyName] = await response.json()
    }
    return
}


closeColumn = (thisCol) => {
    document.getElementById("column" + thisCol).remove()
}


createColumn = () => {
    let columnDiv = newElement("div", {
        "class": "column",
        "id": `column${nextCol}`
    })

    let closeDiv = newElement("div", {
        "class": "close",
        "id": `close${nextCol}`,
        "onclick": `closeColumn(${nextCol})`

    })
    columnDiv.appendChild(closeDiv)

    let inputContainerDiv = newElement("div", {
        "class": "inputContainer",
        "id": `inputContainer${nextCol}`
    })
    columnDiv.appendChild(inputContainerDiv)

    let nameRowDiv = newElement("div", {
        "class": "inputRow",
        "id": `nameRow${nextCol}`
    })
    inputContainerDiv.appendChild(nameRowDiv)

    let nameLabelDiv = newElement("div", { "class": "label" })
    nameRowDiv.appendChild(nameLabelDiv)

    let nameLabel = newElement("label", { "for": `name${nextCol}` })
    nameLabel.innerHTML = "Name"
    nameLabelDiv.appendChild(nameLabel)

    let nameInputDiv = newElement("div", { "class": "name" })
    nameRowDiv.appendChild(nameInputDiv)

    let nameInput = newElement("input", {
        "type": "text",
        "id": `name${nextCol}`,
        "onchange": `loadTable(${nextCol})`,
    })
    nameInputDiv.appendChild(nameInput)

    let startYearRowDiv = newElement("div", {
        "class": "inputRow",
        "id": `startYearRow${nextCol}`
    })
    inputContainerDiv.appendChild(startYearRowDiv)

    let startYearLabelDiv = newElement("div", { "class": "label" })
    startYearRowDiv.appendChild(startYearLabelDiv)

    let startYearLabel = newElement("label", { "for": `startYear${nextCol}` })
    startYearLabel.innerHTML = "Start Year"
    startYearLabelDiv.appendChild(startYearLabel)

    let startYearInputDiv = newElement("div", { "class": "year" })
    startYearRowDiv.appendChild(startYearInputDiv)

    let startYearInput = newElement("input", {
        "type": "text",
        "id": `startYear${nextCol}`,
        "maxlength": "4",
        "onchange": `loadTable(${nextCol})`,
        "oninput": "this.value = numbersOnly(this.value)",

    })
    startYearInputDiv.appendChild(startYearInput)

    let endYearRowDiv = newElement("div", {
        "class": "inputRow",
        "id": `endYearRow${nextCol}`,
    })
    inputContainerDiv.appendChild(endYearRowDiv)

    let endYearLabelDiv = newElement("div", { "class": "label" })
    endYearRowDiv.appendChild(endYearLabelDiv)

    let endYearLabel = newElement("label", { "for": `endYear${nextCol}` })
    endYearLabel.innerHTML = "End Year"
    endYearLabelDiv.appendChild(endYearLabel)

    let endYearInputDiv = newElement("div", { "class": "year" })
    endYearRowDiv.appendChild(endYearInputDiv)

    let endYearInput = newElement("input", {
        "type": "text",
        "id": `endYear${nextCol}`,
        "maxlength": "4",
        "onchange": `loadTable(${nextCol})`,
        "oninput": "this.value = numbersOnly(this.value)",

    })
    endYearInputDiv.appendChild(endYearInput)

    let displayByRowDiv = newElement("div", {
        "class": "inputRow",
        "id": `endYear${nextCol}`
    })
    inputContainerDiv.appendChild(displayByRowDiv)

    let displayByLabelDiv = newElement("div", { "class": "label" })
    displayByRowDiv.appendChild(displayByLabelDiv)

    let displayByLabel = newElement("label", { "for": `displayBy${nextCol}` })
    displayByLabel.innerHTML = "Display by"
    displayByLabelDiv.appendChild(displayByLabel)

    let displayBySelectDiv = newElement("div")
    displayByRowDiv.appendChild(displayBySelectDiv)

    let displayBySelect = newElement("select", {
        "class": "input",
        "id": `displayBy${nextCol}`,
        "onchange": `loadTable(${nextCol})`,
    })
    displayBySelectDiv.appendChild(displayBySelect)

    let byDecadeOption = newElement("option", { "value": "Decade" })
    byDecadeOption.innerHTML = "Decade"
    displayBySelect.appendChild(byDecadeOption)

    let byYearOption = newElement("option", { "value": "Year" })
    byYearOption.innerHTML = "Year"
    displayBySelect.appendChild(byYearOption)



    let tableDiv = newElement("div", {
        "class": "tableContainer",
        "id": `tableContainer${nextCol}`
    })
    columnDiv.appendChild(tableDiv)

    let table = newElement("table", { "id": `table${nextCol}` })
    tableDiv.appendChild(table)



    document.getElementById("columnContainer").appendChild(columnDiv)
    nextCol++

}


numbersOnly = (value) => {
    return value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1')
}


newElement = (tag, attributes = {}) => {
    let e = document.createElement(tag)
    Object.entries(attributes).forEach(([attr, value]) => e.setAttribute(attr, value))
    return e
}