from flask import Flask, render_template, request, redirect
import json, os
from datetime import date
import urllib.parse

app = Flask(__name__)
FILE = "clinic.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE) as f:
                data = json.load(f)
                for i, p in enumerate(data):
                    p["id"] = i
                    if "visits" not in p: p["visits"] = []
                    if "total" not in p: p["total"] = 0
                return data
        except: return []
    return []

def save(d):
    for p in d:
        if "id" in p: del p["id"]
    with open(FILE,"w") as f:
        json.dump(d,f)

@app.route("/")
def home():
    patients = load()
    q = request.args.get("q","")
    search_result = []
    if q:
        search_result = [p for p in patients if q.lower() in p['name'].lower() or q in p['phone']]
    total_collection = sum(int(p['total']) for p in patients)
    today_str = str(date.today())
    today_patients = 0
    today_collection = 0
    for p in patients:
        for v in p.get("visits",[]):
            if v["date"] == today_str:
                today_patients += 1
                today_collection += int(v["fees"])
    # Top patient
    sorted_p = sorted(patients, key=lambda x: len(x.get("visits",[])), reverse=True)
    top = sorted_p[:3] if sorted_p else []
    return render_template("clinic.html", patients=patients, search_result=search_result, q=q, total_collection=total_collection, total_patients=len(patients), today_patients=today_patients, today_collection=today_collection, top=top)

@app.route("/add", methods=["POST"])
def add():
    p = load()
    p.append({"name": request.form["name"], "phone": request.form["phone"], "age": request.form["age"], "problem": request.form["problem"], "total":0, "visits":[]})
    save(p)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    p = load()
    if id < len(p): p.pop(id); save(p)
    return redirect("/")

@app.route("/patient/<int:id>")
def patient(id):
    all_p = load()
    if id >= len(all_p): return redirect("/")
    p = all_p[id]
    msg = f"Namaste {p['name']} ji 🙏 Dr. Sharma Clinic se - Aapki agli date {p['visits'][-1]['next_date'] if p['visits'] else 'kal'} hai. Kripya time pe aa jaye. Dhanyawad!"
    wa_link = "https://wa.me/91" + p['phone'] + "?text=" + urllib.parse.quote(msg)
    return render_template("patient.html", p=p, id=id, wa_link=wa_link)

@app.route("/visit/<int:id>", methods=["POST"])
def visit(id):
    p = load()
    fees = int(request.form["fees"])
    p[id]["visits"].append({
        "date": str(date.today()),
        "dawa": request.form["dawa"],
        "fees": fees,
        "next_date": request.form["next_date"],
        "note": request.form.get("note","")
    })
    p[id]["total"] = int(p[id]["total"]) + fees
    save(p)
    return redirect(f"/patient/{id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)