from flask import (
    Flask,
    render_template_string,
    request,
    jsonify,
    redirect,
    url_for,
    send_from_directory
)
from werkzeug.utils import secure_filename

import os
import json
import uuid


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def load_products():

    try:
        with open(
            PRODUCTS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception as e:
        print(
            "BĹÄd odczytu products.json:",
            e
        )
        return []


def filter_products(
    products,
    occasion,
    style,
    budget
):

    occasion = occasion.strip().lower()
    style = style.strip().lower()

    filtered = []

    for product in products:

        product_occasion = str(
            product.get(
                "occasion",
                ""
            )
        ).lower()

        product_style = str(
            product.get(
                "style",
                ""
            )
        ).lower()

        occasion_match = (
            not occasion
            or occasion in product_occasion
        )

        style_match = (
            not style
            or style in product_style
        )

        if occasion_match and style_match:
            filtered.append(product)

    total = sum(
        float(
            product.get(
                "price",
                0
            )
        )
        for product in filtered
    )

    if budget and total > budget:

        filtered = sorted(
            filtered,
            key=lambda x: float(
                x.get(
                    "price",
                    0
                )
            )
        )

        selected = []
        current_total = 0

        for product in filtered:

            price = float(
                product.get(
                    "price",
                    0
                )
            )

            if current_total + price <= budget:

                selected.append(product)
                current_total += price

        filtered = selected
        total = current_total

    return filtered, total


HTML = """
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

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
    background:
    linear-gradient(
        135deg,
        #111,
        #333
    );
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
    box-shadow:
    0 8px 30px
    rgba(0,0,0,.12);
}

input,
select {
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

.main-button:disabled {
    opacity: .6;
    cursor: wait;
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
    grid-template-columns:
    repeat(
        auto-fit,
        minmax(220px,1fr)
    );
    gap: 18px;
}

.card {
    background: white;
    border-radius: 15px;
    padding: 18px;
    box-shadow:
    0 4px 14px
    rgba(0,0,0,.07);
}

.product-image {
    height: 190px;
    background:
    linear-gradient(
        135deg,
        #eee,
        #ddd
    );
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 55px;
}

.brand {
    color: #777;
    font-size: 14px;
}

.price {
    font-size: 22px;
    font-weight: bold;
}

.small-btn {
    padding: 10px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-right: 5px;
}

.try {
    background: #111;
    color: white;
}

.save {
    background: #e9e9e9;
}

.outfit {
    background: white;
    padding: 22px;
    border-radius: 16px;
    margin-top: 20px;
}

.total {
    font-size: 27px;
    font-weight: bold;
}

.ai-box {
    background: #111;
    color: white;
    padding: 25px;
    border-radius: 16px;
    margin-top: 25px;
}

.photo-box {
    background: white;
    padding: 25px;
    border-radius: 16px;
    margin-top: 25px;
}

.photo-upload {
    border: 2px dashed #ccc;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
}

.user-photo {
    width: 100%;
    max-width: 360px;
    max-height: 520px;
    object-fit: contain;
    border-radius: 18px;
    margin-top: 20px;
}

.photo-info {
    background: #eefbf3;
    padding: 15px;
    border-radius: 10px;
    margin-top: 15px;
}

.compress-info {
    margin-top: 12px;
    color: #666;
    font-size: 14px;
}

.progress {
    display: none;
    margin-top: 15px;
    background: #eee;
    border-radius: 10px;
    padding: 15px;
}

.tryon {
    display: none;
    background: white;
    margin-top: 25px;
    padding: 25px;
    border-radius: 16px;
    text-align: center;
}

.person-placeholder {
    width: 220px;
    height: 330px;
    margin: auto;
    border-radius: 20px;
    background:
    linear-gradient(
        180deg,
        #dedede,
        #aaa
    );
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 80px;
}

.wardrobe {
    background: white;
    padding: 20px;
    margin-top: 25px;
    border-radius: 16px;
}

footer {
    margin-top: 50px;
    background: #111;
    color: #aaa;
    text-align: center;
    padding: 25px;
}

@media(max-width:600px) {

    .hero h1 {
        font-size: 30px;
    }

    nav {
        display: none;
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

<button onclick="scrollToSearch()">
Szukaj
</button>

<button onclick="scrollToPhoto()">
Moje zdjÄcie
</button>

<button onclick="showWardrobe()">
Moja szafa
</button>

</nav>

</header>


<section class="hero">

<h1>
TwĂłj osobisty stylista AI
</h1>

<p>
ZnajdĹş ubrania, stwĂłrz stylizacjÄ
i zobacz jÄ na sobie.
</p>

</section>


<div
class="search-box"
id="search"
>

<h2>
Czego potrzebujesz?
</h2>

<input
id="occasion"
placeholder="Np. wesele, randka, praca"
value="{{ occasion }}"
>

<input
id="budget"
type="number"
placeholder="BudĹźet w zĹ"
value="{{ budget }}"
>

<select id="style">

<option
{% if style == "Elegancki casual" %}
selected
{% endif %}
>
Elegancki casual
</option>

<option
{% if style == "Sportowy" %}
selected
{% endif %}
>
Sportowy
</option>

<option
{% if style == "Streetwear" %}
selected
{% endif %}
>
Streetwear
</option>

<option
{% if style == "Klasyczny" %}
selected
{% endif %}
>
Klasyczny
</option>

<option
{% if style == "Minimalistyczny" %}
selected
{% endif %}
>
Minimalistyczny
</option>

</select>

<button
class="main-button"
onclick="findOutfit()"
>

â¨ ZnajdĹş stylizacjÄ

</button>

</div>


<div class="container">


<h2 class="section-title">
Propozycja FitSee
</h2>


<div class="outfit">

<h3>
Stylizacja nr 1
</h3>


{% if products %}

<p>

FitSee dobraĹo zestaw na:

<b>{{ occasion }}</b>

w stylu

<b>{{ style }}</b>.

</p>


<div class="products">


{% for product in products %}


<div class="card">


<div class="product-image">


{% if product.category == "Koszula" %}

đ

{% elif product.category == "Spodnie" %}

đ

{% elif product.category == "Buty" %}

đ

{% else %}

đ§Ľ

{% endif %}


</div>


<p class="brand">
{{ product.brand }}
</p>


<h3>
{{ product.name }}
</h3>


<p class="price">
{{ product.price }} zĹ
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

âĄ Zapisz

</button>


</div>


{% endfor %}


</div>


<hr>


<p>
Cena zestawu:
</p>


<div class="total">
{{ total|round(0)|int }} zĹ
</div>


<button
class="main-button"
onclick="tryWholeOutfit()"
>

đ¤ Przymierz caĹy zestaw na mnie

</button>


{% else %}


<p>
Nie znaleziono produktĂłw
dla podanych kryteriĂłw.
</p>


{% endif %}


</div>


<div
class="photo-box"
id="photo"
>

<h2>
đ¸ Moje zdjÄcie
</h2>

<p>
Dodaj zdjÄcie caĹej sylwetki.
FitSee automatycznie zmniejszy je
przed wysĹaniem.
</p>


<div class="photo-upload">


<form
id="photoForm"
action="/upload-photo"
method="POST"
enctype="multipart/form-data"
>


<input
type="hidden"
name="occasion"
value="{{ occasion }}"
>

<input
type="hidden"
name="budget"
value="{{ budget }}"
>

<input
type="hidden"
name="style"
value="{{ style }}"
>


<input
id="photoInput"
type="file"
name="photo"
accept="image/png,image/jpeg,image/webp"
required
>


<div
class="compress-info"
id="fileInfo"
>
ZdjÄcie zostanie automatycznie
zmniejszone przed wysĹaniem.
</div>


<button
id="uploadButton"
type="submit"
class="main-button"
>

đ¤ Wgraj moje zdjÄcie

</button>


<div
class="progress"
id="progress"
>

âł OptymalizujÄ i wysyĹam zdjÄcie...

</div>


</form>


{% if photo %}


<div class="photo-info">

â ZdjÄcie zostaĹo wgrane.

</div>


<img
class="user-photo"
src="/uploads/{{ photo }}"
alt="ZdjÄcie uĹźytkownika"
>


<p>

To tÄ osobÄ FitSee ma zachowaÄ
podczas wirtualnego przymierzania.

</p>


{% endif %}


</div>

</div>


<div class="ai-box">

<h2>
đ¤ AI Stylista
</h2>

<p>

FitSee analizuje okazjÄ,
styl oraz budĹźet uĹźytkownika.

Docelowo poĹÄczymy te dane
z prawdziwymi produktami
ze sklepĂłw.

</p>

</div>


<div
class="tryon"
id="tryon"
>

<h2>
Wirtualna przymierzalnia
</h2>


{% if photo %}


<img
class="user-photo"
src="/uploads/{{ photo }}"
alt="Osoba do przymierzenia"
>


{% else %}


<div class="person-placeholder">
đ§
</div>


<p>
Najpierw dodaj swoje zdjÄcie.
</p>


{% endif %}


<h3 id="tryText">
Twoja stylizacja
</h3>


<p>

NastÄpny etap:
Virtual Try-On,
ktĂłry zmieni ubranie,
ale zachowa tÄ samÄ osobÄ.

</p>


</div>


<div
class="wardrobe"
id="wardrobe"
>

<h2>
đ Moja szafa
</h2>

<p id="wardrobeText">
Nie zapisano jeszcze Ĺźadnych ubraĹ.
</p>

</div>


</div>


<footer>

FitSee AI â wersja testowa MVP

</footer>


<script>


let wardrobe = [];


function findOutfit() {

    let occasion =
        document.getElementById(
            "occasion"
        ).value;

    let budget =
        document.getElementById(
            "budget"
        ).value;

    let style =
        document.getElementById(
            "style"
        ).value;

    let url =
        "/?occasion="
        + encodeURIComponent(
            occasion
        )
        + "&budget="
        + encodeURIComponent(
            budget
        )
        + "&style="
        + encodeURIComponent(
            style
        );

    window.location.href = url;

}


function tryProduct(name) {

    document
    .getElementById("tryon")
    .style.display = "block";

    document
    .getElementById("tryText")
    .innerText =
        "Przymierzasz: " + name;

    document
    .getElementById("tryon")
    .scrollIntoView({
        behavior:"smooth"
    });

}


function tryWholeOutfit() {

    document
    .getElementById("tryon")
    .style.display = "block";

    document
    .getElementById("tryText")
    .innerText =
        "PeĹna stylizacja FitSee";

    document
    .getElementById("tryon")
    .scrollIntoView({
        behavior:"smooth"
    });

}


function saveProduct(name) {

    if(!wardrobe.includes(name)) {
        wardrobe.push(name);
    }

    document
    .getElementById("wardrobeText")
    .innerHTML =
        "â "
        + wardrobe.join(
            "<br>â "
        );

}


function showWardrobe() {

    document
    .getElementById("wardrobe")
    .scrollIntoView({
        behavior:"smooth"
    });

}


function scrollToSearch() {

    document
    .getElementById("search")
    .scrollIntoView({
        behavior:"smooth"
    });

}


function scrollToPhoto() {

    document
    .getElementById("photo")
    .scrollIntoView({
        behavior:"smooth"
    });

}


const photoInput =
    document.getElementById(
        "photoInput"
    );

const photoForm =
    document.getElementById(
        "photoForm"
    );

const uploadButton =
    document.getElementById(
        "uploadButton"
    );

const progress =
    document.getElementById(
        "progress"
    );

const fileInfo =
    document.getElementById(
        "fileInfo"
    );


photoInput.addEventListener(
    "change",
    function() {

        if(
            photoInput.files.length
            === 0
        ) {
            return;
        }

        const file =
            photoInput.files[0];

        const mb =
            file.size
            /
            1024
            /
            1024;

        fileInfo.innerText =
            "Oryginalne zdjÄcie: "
            +
            mb.toFixed(1)
            +
            " MB. FitSee zmniejszy je przed wysĹaniem.";

    }
);


photoForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        if(
            photoInput.files.length
            === 0
        ) {
            return;
        }

        uploadButton.disabled = true;

        progress.style.display =
            "block";

        progress.innerText =
            "âł Zmniejszam zdjÄcie...";

        try {

            const originalFile =
                photoInput.files[0];

            const compressedBlob =
                await compressImage(
                    originalFile
                );

            const formData =
                new FormData(
                    photoForm
                );

            formData.delete(
                "photo"
            );

            formData.append(
                "photo",
                compressedBlob,
                "fitsee-photo.jpg"
            );

            const compressedMB =
                compressedBlob.size
                /
                1024
                /
                1024;

            progress.innerText =
                "đ¤ WysyĹam zdjÄcie "
                +
                compressedMB.toFixed(2)
                +
                " MB...";

            const response =
                await fetch(
                    "/upload-photo",
                    {
                        method:
                        "POST",

                        body:
                        formData
                    }
                );

            if(
                response.redirected
            ) {

                window.location.href =
                    response.url;

                return;
            }

            if(
                !response.ok
            ) {

                throw new Error(
                    "Upload failed"
                );

            }

            window.location.reload();

        }

        catch(error) {

            console.error(
                error
            );

            progress.innerText =
                "â Nie udaĹo siÄ wysĹaÄ zdjÄcia.";

            uploadButton.disabled =
                false;

        }

    }
);


function compressImage(file) {

    return new Promise(
        (
            resolve,
            reject
        ) => {

            const reader =
                new FileReader();

            reader.onload =
                function(event) {

                    const image =
                        new Image();

                    image.onload =
                        function() {

                            const MAX_SIZE =
                                1600;

                            let width =
                                image.width;

                            let height =
                                image.height;

                            if(
                                width
                                >
                                MAX_SIZE
                                ||
                                height
                                >
                                MAX_SIZE
                            ) {

                                const ratio =
                                    Math.min(
                                        MAX_SIZE
                                        /
                                        width,

                                        MAX_SIZE
                                        /
                                        height
                                    );

                                width =
                                    Math.round(
                                        width
                                        *
                                        ratio
                                    );

                                height =
                                    Math.round(
                                        height
                                        *
                                        ratio
                                    );

                            }

                            const canvas =
                                document
                                .createElement(
                                    "canvas"
                                );

                            canvas.width =
                                width;

                            canvas.height =
                                height;

                            const ctx =
                                canvas
                                .getContext(
                                    "2d"
                                );

                            ctx.drawImage(
                                image,
                                0,
                                0,
                                width,
                                height
                            );

                            canvas.toBlob(
                                function(blob) {

                                    if(blob) {

                                        resolve(
                                            blob
                                        );

                                    }
                                    else {

                                        reject(
                                            new Error(
                                                "Compression failed"
                                            )
                                        );

                                    }

                                },

                                "image/jpeg",

                                0.82

                            );

                        };

                    image.onerror =
                        reject;

                    image.src =
                        event.target.result;

                };

            reader.onerror =
                reject;

            reader.readAsDataURL(
                file
            );

        }
    );

}


</script>


</body>

</html>
"""


@app.route("/")
def home():

    products = load_products()

    occasion = request.args.get(
        "occasion",
        "Wesele"
    )

    style = request.args.get(
        "style",
        "Elegancki casual"
    )

    photo = request.args.get(
        "photo",
        ""
    )

    try:

        budget = float(
            request.args.get(
                "budget",
                1000
            )
        )

    except:

        budget = 1000

    filtered_products, total = (
        filter_products(
            products,
            occasion,
            style,
            budget
        )
    )

    return render_template_string(
        HTML,
        products=filtered_products,
        total=total,
        occasion=occasion,
        budget=int(budget),
        style=style,
        photo=photo
    )


@app.route("/upload-photo", methods=["POST"])
def upload_photo():

    if "photo" not in request.files:
        return redirect(url_for("home"))

    file = request.files["photo"]

    if file.filename == "":
        return redirect(url_for("home"))

    if not allowed_file(file.filename):
        return (
            "Dozwolone formaty: JPG, JPEG, PNG, WEBP",
            400
        )

    original_name = secure_filename(file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = str(uuid.uuid4()) + "." + extension

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(path)

    occasion = request.form.get("occasion", "Wesele")
    budget = request.form.get("budget", "1000")
    style = request.form.get("style", "Elegancki casual")

    return redirect(
        url_for(
            "home",
            occasion=occasion,
            budget=budget,
            style=style,
            photo=filename
        ) + "#photo"
    )


@app.route(
    "/uploads/<filename>"
)
def uploaded_file(
    filename
):

    return send_from_directory(
        app.config[
            "UPLOAD_FOLDER"
        ],
        filename
    )


@app.route("/health")
def health():

    return jsonify({
        "status":
        "ok",

        "app":
        "FitSee",

        "products":
        len(
            load_products()
        )
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
