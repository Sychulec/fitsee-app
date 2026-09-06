from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

PRODUCTS = [
    {
        "id": 1,
        "name": "Granatowa koszula premium",
        "brand": "Lacoste",
        "price": 329,
        "type": "Koszula"
    },
    {
        "id": 2,
        "name": "Spodnie chino slim",
        "brand": "Tommy Hilfiger",
        "price": 299,
        "type": "Spodnie"
    },
    {
        "id": 3,
        "name": "Białe sneakersy",
        "brand": "Tommy Hilfiger",
        "price": 349,
        "type": "Buty"
    },
    {
        "id": 4,
        "name": "Lekka marynarka casual",
        "brand": "Selected",
        "price": 399,
        "type": "Marynarka"
    }
]

HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FitSee AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f5f6f8;
    color: #151515;
}

header {
    background: #111;
    color: white;
    padding: 18px 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 28px;
    font-weight: bold;
}

.logo span {
    color: #8ee6b3;
}

nav button {
    border: none;
    background: transparent;
    color: white;
    margin-left: 15px;
    cursor: pointer;
    font-size: 15px;
}

.hero {
    padding: 55px 20px;
    text-align: center;
    background: linear-gradient(135deg,#111,#333);
    color: white;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 10px;
}

.hero p {
    font-size: 19px;
    opacity: .85;
}

.search-box {
    max-width: 900px;
    margin: -30px auto 30px;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,.12);
}

input, select {
    width: 100%;
    padding: 14px;
    margin: 7px 0;
    border-radius: 10px;
    border: 1px solid #ddd;
    font-size: 16px;
}

.main-button {
    width: 100%;
    padding: 15px;
    border: none;
    background: #111;
    color: white;
    border-radius: 10px;
    font-size: 17px;
    cursor: pointer;
    margin-top: 10px;
}

.main-button:hover {
    background: #333;
}

.container {
    max-width: 1150px;
    margin: auto;
    padding: 20px;
}

.section-title {
    margin-top: 35px;
    font-size: 25px;
}

.products {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
    gap: 18px;
}

.card {
    background: white;
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,.07);
}

.product-image {
    height: 190px;
    background: linear-gradient(135deg,#eee,#ddd);
    border-radius: 12px;
    display:flex;
    justify-content:center;
    align-items:center;
    font-size:55px;
}

.brand {
    color:#777;
    font-size:14px;
}

.price {
    font-size:22px;
    font-weight:bold;
}

.small-btn {
    padding:10px;
    border:none;
    border-radius:8px;
    cursor:pointer;
    margin-right:5px;
}

.try {
    background:#111;
    color:white;
}

.save {
    background:#e9e9e9;
}

.outfit {
    background:white;
    padding:22px;
    border-radius:16px;
    margin-top:20px;
}

.total {
    font-size:27px;
    font-weight:bold;
}

.ai-box {
    background:#111;
    color:white;
    padding:25px;
    border-radius:16px;
    margin-top:25px;
}

.tryon {
    display:none;
    background:white;
    margin-top:25px;
    padding:25px;
    border-radius:16px;
    text-align:center;
}

.person-placeholder {
    width:220px;
    height:330px;
    margin:auto;
    border-radius:20px;
    background:linear-gradient(180deg,#dedede,#aaa);
    display:flex;
    justify-content:center;
    align-items:center;
    font-size:80px;
}

.wardrobe {
    background:white;
    padding:20px;
    margin-top:25px;
    border-radius:16px;
}

footer {
    margin-top:50px;
    background:#111;
    color:#aaa;
    text-align:center;
    padding:25px;
}

@media(max-width:600px) {

    .hero h1 {
        font-size:30px;
    }

    nav {
        display:none;
    }
}

</style>
</head>

<body>

<header>

<div class="logo">
Fit<span>See</span>
</div>

<nav>
<button onclick="scrollToSearch()">Szukaj</button>
<button onclick="showWardrobe()">Moja szafa</button>
<button>Profil</button>
</nav>

</header>


<section class="hero">

<h1>Twój osobisty stylista AI</h1>

<p>
Znajdź ubrania, stwórz stylizację i zobacz ją na sobie.
</p>

</section>


<div class="search-box" id="search">

<h2>Czego potrzebujesz?</h2>

<input
id="occasion"
placeholder="Np. wesele, randka, praca, codziennie"
value="Wesele"
>

<input
id="budget"
type="number"
placeholder="Budżet w zł"
value="1000"
>

<select id="style">
<option>Elegancki casual</option>
<option>Sportowy</option>
<option>Streetwear</option>
<option>Klasyczny</option>
<option>Minimalistyczny</option>
</select>

<button class="main-button" onclick="findOutfit()">
✨ Znajdź stylizację
</button>

</div>


<div class="container">

<div id="results">

<h2 class="section-title">
Propozycja FitSee
</h2>

<div class="outfit">

<h3>Stylizacja nr 1</h3>

<p>
AI dobrało zestaw na wesele bez pełnego garnituru.
</p>

<div class="products">

{% for product in products %}

<div class="card">

<div class="product-image">

{% if product.type == "Koszula" %}
👕
{% elif product.type == "Spodnie" %}
👖
{% elif product.type == "Buty" %}
👟
{% else %}
🧥
{% endif %}

</div>

<p class="brand">
{{ product.brand }}
</p>

<h3>
{{ product.name }}
</h3>

<p class="price">
{{ product.price }} zł
</p>

<button
class="small-btn try"
onclick="tryProduct('{{ product.name }}')"
>
Przymierz
</button>

<button
class="small-btn save"
onclick="saveProduct('{{ product.name }}')"
>
♡ Zapisz
</button>

</div>

{% endfor %}

</div>

<hr>

<p>
Cena zestawu:
</p>

<div class="total">
977 zł
</div>

<button
class="main-button"
onclick="tryWholeOutfit()"
>
👤 Przymierz cały zestaw na mnie
</button>

</div>


<div class="ai-box">

<h2>🤖 AI Stylista</h2>

<p id="aiText">

Ten zestaw dobrze sprawdzi się na weselu bez garnituru.
Granatowa góra daje elegancki wygląd, a jasne sneakersy
utrzymują nowoczesny, młodszy charakter stylizacji.

</p>

</div>


<div class="tryon" id="tryon">

<h2>Wirtualna przymierzalnia</h2>

<p>
W wersji docelowej tutaj pojawi się Twoje zdjęcie
w wybranym ubraniu.
</p>

<div class="person-placeholder">
🧍
</div>

<h3 id="tryText">
Twoja stylizacja
</h3>

<p>
Virtual Try-On AI — moduł testowy
</p>

</div>


<div class="wardrobe" id="wardrobe">

<h2>👔 Moja szafa</h2>

<p id="wardrobeText">
Nie zapisano jeszcze żadnych ubrań.
</p>

</div>

</div>

</div>


<footer>

FitSee AI — wersja testowa MVP

</footer>


<script>

let wardrobe = [];

function findOutfit() {

    let occasion =
        document.getElementById("occasion").value;

    let budget =
        document.getElementById("budget").value;

    let style =
        document.getElementById("style").value;

    document.getElementById("aiText").innerHTML =
        "Szukam stylizacji na <b>" +
        occasion +
        "</b> w stylu <b>" +
        style +
        "</b> i budżecie do <b>" +
        budget +
        " zł</b>.<br><br>" +
        "FitSee przygotowało zestaw najlepiej dopasowany do podanych kryteriów.";

    document.getElementById("results")
        .scrollIntoView({
            behavior:"smooth"
        });
}


function tryProduct(name) {

    document.getElementById("tryon")
        .style.display = "block";

    document.getElementById("tryText")
        .innerText =
        "Przymierzasz: " + name;

    document.getElementById("tryon")
        .scrollIntoView({
            behavior:"smooth"
        });
}


function tryWholeOutfit() {

    document.getElementById("tryon")
        .style.display = "block";

    document.getElementById("tryText")
        .innerText =
        "Pełna stylizacja FitSee";

    document.getElementById("tryon")
        .scrollIntoView({
            behavior:"smooth"
        });
}


function saveProduct(name) {

    if(!wardrobe.includes(name)) {
        wardrobe.push(name);
    }

    document.getElementById("wardrobeText")
        .innerHTML =
        wardrobe.join("<br>✓ ");
}


function showWardrobe() {

    document.getElementById("wardrobe")
        .scrollIntoView({
            behavior:"smooth"
        });
}


function scrollToSearch() {

    document.getElementById("search")
        .scrollIntoView({
            behavior:"smooth"
        });
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(
        HTML,
        products=PRODUCTS
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "FitSee"
    })


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
