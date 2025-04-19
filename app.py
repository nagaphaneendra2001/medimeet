# from application import app, db
# from flask import render_template, request, session, redirect, url_for, flash, Flask
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
import re

import datetime
from bson import ObjectId
from flask import render_template, request, session, redirect, url_for, flash, Flask
import pymongo
my_collections = pymongo.MongoClient("mongodb+srv://nagaphaneendra2016:nagaphaneendra2016@cluster0.y9mnl5j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
                                        tls=True,
                                        tlsAllowInvalidCertificates=False,  # Set to True only for testing if needed
                                        connectTimeoutMS=30000,
                                        socketTimeoutMS=30000,
                                        serverSelectionTimeoutMS=30000)
my_db = my_collections['HMS']
doctor_col = my_db['Doctor']
patient_col = my_db['Patient']
appointment_col = my_db['Appointments']
prescription_col = my_db['Prescription']
payments_col = my_db['Payments']
schedule_col = my_db['Schedule']
specialization_col = my_db['Specialization']
admin_col = my_db['Admin']

app = Flask(__name__)
app.secret_key = "HMS"


@app.route("/")
def index():
    return render_template("userLogin.html")


@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")


@app.route("/adminLogin1", methods=['post'])
def adminLogin1():
    username = request.form.get('username')
    password = request.form.get('password')
    print(username,password)
    query = {"username": username, "password": password}
    count = admin_col.count_documents(query)
    if count > 0:
        session['role'] = 'Staff'
        return redirect("/staffHome")
    else:
        return render_template("adminLogin.html", message="Invalid Login Details",color="red")


@app.route("/staffHome")
def staffHome():
    
    return render_template("adminHome.html")

@app.route("/appointments")
def adminAppointments():
    apps = schedule_col.find()
    appoints=[]
    for i in apps:
        appoints.append(i)
    print(appoints)
    return render_template("adminAppointments.html",apps=appoints)

@app.route("/addSpecializationHome")
def addSpecializationHome():
    print("--------------------------------------")
    print(specialization_col.find())
    print("--------------------------------------")
    if specialization_col.find()==None:
        print("in...........")
        specialization=[]
        return render_template("addspecialization.html",specialization=specialization)
    specialization=[]
    for i in specialization_col.find():
        specialization.append(i.get('specialization_name'))
    return render_template("addspecialization.html",Specializations=spliz())

@app.route("/addSpecialization",methods=['post'])
def addSpecialization():
    Specialization=request.form.get('Specialization').capitalize()
    Specializations=[]
    for i in specialization_col.find():
        Specializations.append(i.get('specialization_name'))
    if Specialization in Specializations:
        return render_template("addspecialization.html",message="specialization Already Present!!!",color="red",Specializations=Specializations)
    query = {"specialization_name":Specialization}
    id=specialization_col.insert_one(query)
    Specializations=[]
    for i in specialization_col.find():
        Specializations.append(i.get('specialization_name'))
    return render_template("addspecialization.html",Specializations=Specializations,message="specialization Added.....")


@app.route("/userRegister")
def userRegister():
    return render_template("/userRegister.html")


@app.route("/userRegister1", methods=['post'])
def userRegister1():
    firstname = request.form.get('firstname')
    conf_password = request.form.get('conf_password')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    address = request.form.get('address')
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = patient_col.count_documents(query)
    if count > 0:
        return render_template("userRegister.html", message="Duplicate Details!!!.....", color="red")
    if conf_password != password:
        return render_template("userRegister.html", message="Password Not Matched!!!.....", color="red")
    query = {"name":firstname, "email": email, "phone": phone, "password": password,"address":address  }
    result = patient_col.insert_one(query)
    return render_template("userLogin.html", message="User Registered successfully", color="green")


@app.route("/userLogin")
def userLogin():
    return render_template("/userLogin.html")


@app.route("/userLogin1", methods=['post'])
def userLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = patient_col.count_documents(query)
    if count > 0:
        user = patient_col.find_one(query)
        session['patient_id'] = str(user['_id'])
        session['role'] = 'Patient'
        return redirect("/patientHome")
    else:
        return render_template("userLogin.html", message="Invalid Login Details",color="red")


@app.route("/patientHome")
def patientHome():
    # subject=request.args.get("subject")
    spliz = specialization()
    print(spliz)
    name=patient_col.find_one({"_id":ObjectId(session['patient_id'])})["name"]
    return render_template("patientHome.html",spliz=spliz,name=name)

@app.route("/bookapp1", methods=['post'])
def bookapp1():
    patientname = request.form.get('pname')
    age = request.form.get('age')
    purpose = request.form.get('purpose')
    print(purpose)
    gender = request.form.get('gender')
    doctor = alldoctor(purpose)
    print(doctor)
    return render_template("selectdoc.html" , pname = patientname, age = age, purpose = purpose, gender=gender, doctor=doctor)
    
@app.route("/selectdoc", methods=['post'])
def selectdoc():
    patientname = request.form.get('pname')
    age = request.form.get('age')
    purpose = request.form.get('purpose')
    print(purpose)
    gender = request.form.get('gender')
    doctorid = request.form.get('doctor')
    bookdate = request.form.get('bookdate')
    booktime = request.form.get('booktime')
    query = {"Patient Name": patientname,"patient_id": ObjectId(session['patient_id']), "Doctor_id":ObjectId(doctorid), "Age": age, "Purpose": purpose, "Gender": gender,"Appointment Date":bookdate,"time":booktime,"status":"not visited"  }
    result = schedule_col.insert_one(query)
    query1 = {"patient_id":ObjectId(session['patient_id']),"doctor_id":ObjectId(doctorid),"schedule_id":ObjectId(result.inserted_id)}
    result1=appointment_col.insert_one(query1)
    amount=50
    status="paid"
    bookdate=datetime.datetime.now()
    query2 = {"patient_id":ObjectId(session['patient_id']),"appointment_id":ObjectId(result1.inserted_id),"price":amount,"status":status,"paid date":bookdate}
    print(query2)
    payments_col.insert_one(query2)
    return render_template("payment.html")


def alldoctor(spl):
    alldoc = doctor_col.find()
    doc={}
    for i in alldoc:
        if i["Specialization"]==spl:
            doc[i["_id"]]=i["firstname"]
    return doc

def spliz():
    spz=specialization_col.find()
    spzlist=[]
    for i in spz:
        spzlist.append(i.get("specialization_name"))
    return spzlist

def doctor_id(name):
    alldoc = doctor_col.find()
    id=""
    for i in alldoc:
        if i["firstname"]==name:
            id=i["_id"]
    return id

    
def specialization():
    splztion = doctor_col.find()
    splztionlist = []
    for i in splztion:
        print(i)
        splztionlist.append(i['Specialization'])
    splztionlist = list(set(splztionlist))
    return splztionlist

@app.route("/payment", methods=['post'])
def payment():
    return render_template("userLogin.html", message="Appointment Registered successfully", color="green")


@app.route("/paymentdone", methods=['post'])
def paymentdone():
    apps=get_AllAppointments()
    return render_template("viewAppointments.html", apps=apps)


def get_AllAppointments():
    query={"patient_id":ObjectId(session.get("patient_id"))}
    print(session.get("patient_id"))
    apps=schedule_col.find(query)
    appoints=[]
    for i in apps:
        docname=get_doctorname(i["Doctor_id"])
        i["doctorname"] = docname
        appoints.append(i)
    return appoints


def get_doctorname(doc_id):
    print(doc_id)
    return doctor_col.find_one({"_id":ObjectId(doc_id)})["firstname"]
    
    
    
@app.route("/viewAppointments", methods=['post','get'])
def viewAppointments():
    apps=get_AllAppointments()
    print(apps)
    return render_template("viewAppointments.html",apps=apps)


@app.route("/doctorRegister")
def staffRegister():
    return render_template("/doctorRegister.html",spliz=spliz())

@app.route("/doctorRegister1", methods=['post'])
def staffRegister1():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    conf_password = request.form.get('conf_password')
    address = request.form.get('address')
    Specialization = request.form.get('Specialization')
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = doctor_col.count_documents(query)
    if count > 0:
        return render_template("doctorRegister.html", message="Duplicate Details!!!.....", color="red")
    if conf_password != password:
        return render_template("doctorRegister.html", message="Password Not Matched!!!.....", color="red")
    query = {"lastname": lastname,"firstname":firstname, "email": email, "phone": phone, "password": password,"Specialization":Specialization,"Address":address  }
    result = doctor_col.insert_one(query)
    return render_template("doctorRegister.html", message="Doctor Registered successfully", color="green")

@app.route("/doctorLogin")
def staffLogin():
    return render_template("/DoctorLogin.html")

@app.route("/doctorLogin1", methods=['post'])
def staffLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = doctor_col.count_documents(query)
    if count > 0:
        doc = doctor_col.find_one(query)
        session['doctor_id'] = str(doc['_id'])
        session['role'] = 'Doctor'
        return redirect("/doctorHome")
    else:
        return render_template("DoctorLogin.html", message="Invalid Login Details",color="red")
    

@app.route("/doctorHome")
def doctorHome():
    apps=get_AllAppointmentsdoc()
    print(apps)
    return render_template("doctorHome.html",apps=apps)


@app.route("/reschedule")
def reschedule():
    apps=get_AllAppointmentsdoc()
    pat_id = request.args.get('id')
    return render_template("reschedule.html",pat_id=pat_id)

@app.route("/reschedule1")
def reschedule1():
    pat_id = request.args.get('pat_id')
    resdate = request.args.get('bookdate')
    restime = request.args.get('booktime')
    print(resdate)
    print(restime)
    print(pat_id)
    query = {"_id": ObjectId(pat_id)}
    query2 = {"$set": {"Appointment Date": resdate,"time": restime}}
    schedule_col.update_one(query, query2)
    return redirect("/doctorHome")

@app.route("/visit")
def prescription():
    appid = request.args.get('id')
    return render_template("prescription.html",app_id=appid)

@app.route("/prescription1", methods=['post'])
def prescription1():
    app_id = request.form.get('app_id')
    medname = request.form.get('medname')
    dos = request.form.get('dos')
    inst = request.form.get('inst')
    prescription_col.insert_one({"Medicine Name":medname,"Dosage":dos,"Instructions":inst,"Appointment_id":app_id})
    print("----------------------------")
    print(app_id)
    query={"_id":ObjectId(app_id)}
    sch=appointment_col.find_one(query)['schedule_id']
    print(sch)
    query = {"_id": ObjectId(sch)}
    query2 = {"$set": {"status":"visited"}}
    schedule_col.update_one(query, query2)
    return redirect("/doctorHome")


def get_AllAppointmentsdoc():
    query={"Doctor_id":ObjectId(session.get("doctor_id"))}
    apps=schedule_col.find(query)
    
    appoints=[]
    for i in apps:
        if i["status"] == "not visited":
            appoint = appointment_col.find_one({"schedule_id":ObjectId(i['_id'])})
            print(appoint)
            i['app_id']=appoint["_id"]
            appoints.append(i)
    return appoints



@app.route("/getSlots")
def getSlots():
    doctor_id = request.args.get('doctor_id')
    patient_id = request.args.get('patient_id')
    bookdate = request.args.get('bookdate')
    print(doctor_id)
    print(bookdate)
    print(patient_id)
    slots = []
    if session['role'] == 'Doctor':
        sch  = schedule_col.find({"Doctor_id":ObjectId(session['doctor_id']),"Appointment Date":bookdate})  
    else:
        sch  = schedule_col.find({"Doctor_id":ObjectId(doctor_id),"Appointment Date":bookdate})
    for i in range(9,17):
        for j in ["00","15","30"]:
            sl = str(i)+":"+ j+" - "+str(i)+":"+str(int(j)+15)
            slots.append(sl)
        sl = str(i)+":45"+" - "+str(i+1)+":00"
        slots.append(sl)
    schslots=[]
    for i in sch:
        schslots.append(i["time"])
    for i in schslots:
        print(i)
        if i in slots:
            slots.remove(i)
    print(slots)
    print(schslots)
    return render_template("getSlots.html", slots=slots)




@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    flash('logged out successfully .')
    return redirect( url_for('login') )


if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True,port=5020)
