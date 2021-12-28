let nameData = new Object();
let db_url = "https://us-west1-portfolio-334101.cloudfunctions.net/nameGenderator?name="

loadData = async () => {
  babyName = document.getElementById("babyName").value

  if (babyName && !nameData[babyName]) {
    console.log("fetching")
    response = await fetch(db_url + babyName, { cache: "force-cache" })
    nameData[babyName] = await response.json()
  }

  document.getElementById("preformatted").innerHTML = JSON.stringify(nameData[babyName], null, 2)

}
