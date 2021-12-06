from datetime import datetime
import os
from pymongo.collection import Collection
from flask import Flask, json, render_template, request, abort, session
from flask_pymongo import PyMongo
from bson import json_util
from datetime import datetime


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
# app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = "mongodb+srv://andreac99:tmJXfW55Skt75z@cluster0.7px16.mongodb.net/test?authSource=admin" \
                          "&replicaSet=atlas-i8fr10-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
app.secret_key = '12345'
pymongo = PyMongo(app, tls=True, tlsAllowInvalidCertificates=True)
db = pymongo.cx.SMBUD
certificates: Collection = db.certificates


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/')
@app.route('/login')
def login():
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/personal_area/', methods=['POST', 'GET'])
def personal_area():
    if request.method != 'POST':
        return abort(404)
    else:
        session['tax_code'] = request.form['tax_code']
        person = certificates.find_one_or_404({"tax_code": session["tax_code"]}, {"name": 1, "surname": 1, "_id": 0})
        return render_template('personal_area.html', value=person["name"] + " " + person["surname"])


@app.route('/certificates/', methods=["GET", "POST"])
def get_certificate():
    documents = certificates.find({"tax_code": session["tax_code"]})
    dynamic_value = generate_certificates_page(documents)
    return render_template("certificates.html", value=dynamic_value)

@app.route("/certificates")
def list_certificates():
    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier templates would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    certificates_result = certificates.find().sort("uci")

    certificates_count = certificates.count_documents({})

    return {
        "certificates": [parse_json(certificates_result)]
    }


def generate_certificates_page(docs: list) -> str:
    file_html = ""
    for doc in docs:
        if "vaccination" in doc:
            file_html += generate_certificate_vaccination(doc)
        elif "test" in doc:
            file_html += generate_certificate_test(doc)
        elif "recovery" in doc:
            file_html += generate_certificate_recovery(doc)
    return file_html


def clean_place(place):
    place.pop("authorized_by", None)
    place.pop("gps", None)
    place.pop("type", None)
    return place


def clean_vaccination(vax) -> (dict, str, str, dict):
    doctor = vax["doctor"]["name"] + " " + vax["doctor"]["surname"]
    nurse = vax["nurse"]["name"] + " " + vax["nurse"]["surname"]
    place = clean_place(vax["place"])
    vax.pop("revoked", None)
    vax.pop("doctor", None)
    vax.pop("nurse", None)
    vax.pop("place", None)
    return vax, doctor, nurse, place


def add_dict_to_html(doc: dict, html: str) -> str:
    for element in doc:
        html = html + str(element) + ": " + str(doc[element]) + "<br>"
    return html


def generate_certificate_vaccination(doc):
    certificate = ""
    if doc["vaccination"]["revoked"] or doc["vaccination"]["expiration_date"] < datetime.now():
        certificate = "<div class=expired_document>\n<div class=document_inside>\n"
    else:
        certificate = "<div class=document>\n<div class=document_inside>\n"
    vax = doc["vaccination"]
    vax, doctor, nurse, place = clean_vaccination(vax)
    certificate += "<b>Vaccination</b><br>"
    certificate += "UCI: {}<br>".format(doc["uci"])
    certificate = add_dict_to_html(vax, certificate)
    certificate += "doctor: " + doctor + "<br>"
    certificate += "nurse: " + nurse + "<br>"
    certificate = add_dict_to_html(place, certificate)
    certificate += "</div></div>"
    return certificate


def clean_test(tst):
    place = clean_place(tst["place"])
    operator = tst["sanitary_operator"]["name"] + " " + tst["sanitary_operator"]["surname"]
    place = clean_place(tst["place"])
    tst.pop("revoked", None)
    tst.pop("sanitary_operator", None)
    tst.pop("place", None)
    return tst, operator, place


def generate_certificate_test(doc):
    if doc["test"]["result"] == "Positive":
        return ""
    certificate = ""
    if doc["test"]["revoked"] or doc["test"]["expiration_date"] < datetime.now():
        certificate = "<div class=expired_document>\n<div class=document_inside>\n"
    else:
        certificate = "<div class=document>\n<div class=document_inside>\n"
    test, operator, place = clean_test(doc["test"])
    certificate += "<b>Swab</b><br>"
    certificate += "UCI: {}<br>".format(doc["uci"])
    certificate = add_dict_to_html(test, certificate)
    certificate += "sanitary operator: " + operator + "<br>"
    certificate = add_dict_to_html(place, certificate)
    certificate += "</div></div>"
    return certificate


def generate_certificate_recovery(doc):
    if doc["recovery"]["revoked"] or doc["recovery"]["expiration_date"] < datetime.now():
        certificate = "<div class=expired_document>\n<div class=document_inside>\n"
    else:
        certificate = "<div class=document>\n<div class=document_inside>\n"
    certificate += "<b>Recovery</b><br>"
    certificate += "UCI: {}<br>".format(doc["uci"])
    doc["recovery"].pop("uci_swab", None)
    certificate = add_dict_to_html(doc["recovery"], certificate)
    certificate += "</div></div>"
    return certificate


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
