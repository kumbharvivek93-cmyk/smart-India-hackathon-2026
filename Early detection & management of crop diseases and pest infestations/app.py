import os, re, secrets
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from uuid import uuid4
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from models import Buyer, BuyerRequirement, Crop, Dispute, Farmer, FarmerCrop, Lot, MarketPrice, Offer, Payment, StorageFacility, Transaction, TransportProvider, TransportRequest, User

app = Flask(__name__)
db_dir = Path(app.root_path) / "instances"; db_dir.mkdir(exist_ok=True)
upload_dir = Path(app.root_path) / "static" / "uploads"; upload_dir.mkdir(parents=True, exist_ok=True)
app.config.update(SQLALCHEMY_DATABASE_URI=f"sqlite:///{(db_dir / 'agrilink.sqlite3').as_posix()}", SQLALCHEMY_TRACK_MODIFICATIONS=False, SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32), PERMANENT_SESSION_LIFETIME=timedelta(hours=24), UPLOAD_FOLDER=str(upload_dir), MAX_CONTENT_LENGTH=5*1024*1024)
db.init_app(app)
REGISTER_ROLES={"farmer","buyer"}; AUTH_ROLES=REGISTER_ROLES|{"admin"}; EMAIL=re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"); IMAGES={"jpg","jpeg","png","webp"}
with app.app_context(): db.create_all()

def user():
    u=db.session.get(User,session.get("user_id"))
    if not u: session.clear()
    return u
def profile(u): return Farmer.query.filter_by(user_id=u.id).first() if u.role=="farmer" else Buyer.query.filter_by(user_id=u.id).first()
def farmer(): return Farmer.query.filter_by(user_id=user().id).first_or_404()
def buyer(): return Buyer.query.filter_by(user_id=user().id).first_or_404()
def login_required(fn):
 @wraps(fn)
 def w(*a,**k):
  if not user(): flash("Please login first."); return redirect(url_for("login_user"))
  return fn(*a,**k)
 return w
def role_required(*roles):
 def d(fn):
  @wraps(fn)
  def w(*a,**k):
   if not user(): return redirect(url_for("login_user"))
   if user().role not in roles: abort(403)
   return fn(*a,**k)
  return w
 return d
def num(name, minimum=0):
 try:
  v=float(request.form.get(name,"")); assert v>=minimum; return v
 except (ValueError,AssertionError): raise ValueError(f"Enter a valid {name.replace('_',' ')}.")
def dt(name):
 v=request.form.get(name,"").strip(); return datetime.strptime(v,"%Y-%m-%d").date() if v else None
def commit(msg):
 try: db.session.commit(); flash(msg); return True
 except Exception: db.session.rollback(); app.logger.exception("Database operation failed"); flash("Could not save changes."); return False
def quality(m,f,d):
 s=max(0,min(100,round(100-m*1.2-f*2-d*2))); return s,"A" if s>=80 else "B" if s>=60 else "C"
def allowed(tx):
 u=user(); return u and (u.role=="admin" or (u.role=="farmer" and tx.farmer.user_id==u.id) or (u.role=="buyer" and tx.buyer.user_id==u.id))

@app.route("/")
def home(): return render_template("index.html")
@app.route("/registration_user",methods=["GET","POST"])
def registration_user():
 if request.method=="GET": return render_template("register_user.html")
 n=request.form.get("username","").strip(); e=request.form.get("email","").strip().lower(); p=request.form.get("password",""); r=request.form.get("role","").lower()
 if len(n)<2 or not EMAIL.match(e) or len(p)<6 or r not in REGISTER_ROLES: flash("Please provide valid account details.")
 elif User.query.filter_by(email=e).first(): flash("An account with that email already exists."); return redirect(url_for("login_user"))
 else:
  u=User(username=n,email=e,password_hash=generate_password_hash(p),role=r); db.session.add(u)
  if commit("Account created. Complete your profile."):
   session.clear(); session.update(user_id=u.id,role=r); session.permanent=True; return redirect(url_for("register_farmer" if r=="farmer" else "register_buyer"))
 return redirect(url_for("registration_user"))
@app.route("/login_user",methods=["GET","POST"])
def login_user():
 if request.method=="GET": return render_template("login_user.html")
 u=User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
 if not u or not check_password_hash(u.password_hash,request.form.get("password","")) or not u.is_active or u.role not in AUTH_ROLES: flash("Invalid email or password."); return redirect(url_for("login_user"))
 session.clear(); session.update(user_id=u.id,role=u.role); session.permanent=True
 return redirect(url_for("dashboard" if u.role=="admin" or profile(u) else ("register_farmer" if u.role=="farmer" else "register_buyer")))
@app.route("/register_farmer",methods=["GET","POST"])
@role_required("farmer")
def register_farmer():
 if profile(user()): return redirect(url_for("dashboard"))
 if request.method=="GET": return render_template("register_farmer.html")
 fields={x:request.form.get(x,"").strip() for x in ("full_name","phone","village","taluka","district","state","pincode")}
 if not all(fields.values()) or not fields["phone"].isdigit() or len(fields["phone"])!=10 or not fields["pincode"].isdigit() or len(fields["pincode"])!=6: flash("Complete all profile fields with valid phone and pincode.")
 else:
  try: size=num("farm_size",0)
  except ValueError as x: flash(str(x))
  else:
   db.session.add(Farmer(user_id=user().id,**fields,farm_size=size,farm_size_unit=request.form.get("farm_size_unit","acre"),fpo_member=request.form.get("fpo_member")=="yes",fpo_name=request.form.get("fpo_name","").strip() or None))
   if commit("Farmer profile saved."): return redirect(url_for("dashboard"))
 return redirect(url_for("register_farmer"))
@app.route("/register_buyer",methods=["GET","POST"])
@role_required("buyer")
def register_buyer():
 if profile(user()): return redirect(url_for("dashboard"))
 if request.method=="GET": return render_template("register_buyer.html")
 fields={x:request.form.get(x,"").strip() for x in ("company_name","contact_person","phone","email","address","village_city","district","state","business_type")}
 if not all(fields.values()) or not EMAIL.match(fields["email"]) or not fields["phone"].isdigit() or len(fields["phone"])!=10: flash("Complete the form with valid details.")
 else:
  db.session.add(Buyer(user_id=user().id,**fields))
  if commit("Buyer profile saved."): return redirect(url_for("dashboard"))
 return redirect(url_for("register_buyer"))
@app.route("/dashboard")
@login_required
def dashboard():
 u=user()
 if u.role=="admin": stats={"Users":User.query.count(),"Farmers":Farmer.query.count(),"Buyers":Buyer.query.count(),"Verified buyers":Buyer.query.filter_by(is_verified=True).count(),"Lots":Lot.query.count(),"Active offers":Offer.query.filter_by(status="pending").count(),"Open disputes":Dispute.query.filter(Dispute.status!="resolved").count()}
 elif u.role=="farmer":
  p=farmer(); stats={"Active lots":Lot.query.filter_by(farmer_id=p.id,status="available").count(),"Received offers":Offer.query.filter_by(farmer_id=p.id,status="pending").count(),"Pending transactions":Transaction.query.filter_by(farmer_id=p.id,transaction_status="pending").count()}
 else:
  p=buyer(); stats={"Active requirements":BuyerRequirement.query.filter_by(buyer_id=p.id,status="open").count(),"My offers":Offer.query.filter_by(buyer_id=p.id,status="pending").count(),"Active transactions":Transaction.query.filter_by(buyer_id=p.id).count()}
 return render_template("dashboard.html",user=u,role=u.role,profile=profile(u),stats=stats)
@app.route("/market")
@login_required
def market():
 q=MarketPrice.query; cid=request.args.get("crop_id",type=int); district=request.args.get("district","")
 if cid:q=q.filter_by(crop_id=cid)
 if district:q=q.filter(MarketPrice.district.ilike(f"%{district}%"))
 rows=q.order_by(MarketPrice.date.desc()).all(); return render_template("market.html",crops=Crop.query.order_by(Crop.name).all(),prices=rows,best=max(rows,key=lambda x:x.modal_price or 0,default=None))
@app.route("/api/price-trend/<int:crop_id>")
@login_required
def price_trend(crop_id):
 rows=MarketPrice.query.filter_by(crop_id=crop_id).order_by(MarketPrice.date).all(); return jsonify(labels=[x.date.isoformat() for x in rows],prices=[x.modal_price for x in rows])
@app.route("/api/price-prediction/<int:crop_id>")
@login_required
def price_prediction(crop_id):
 rows=MarketPrice.query.filter_by(crop_id=crop_id).order_by(MarketPrice.date).all()
 if not rows:return jsonify(error="No market data available"),404
 r=rows[-7:]; cur=r[-1].modal_price; pred=round(sum(x.modal_price for x in r)/len(r),2); return jsonify(current_price=cur,predicted_price=pred,trend="Increasing" if pred>cur else "Decreasing" if pred<cur else "Stable",confidence="Low" if len(rows)<10 else "Moderate",disclaimer="AI-based estimated price. Actual market prices may vary.")
@app.route("/farmer/crops",methods=["GET","POST"])
@role_required("farmer")
def farmer_crops():
 p=farmer()
 if request.method=="POST":
  try: cid=int(request.form.get("crop_id","")); qty=num("expected_quantity",0)
  except (ValueError,TypeError): flash("Select a crop and valid quantity.")
  else:
   if not db.session.get(Crop,cid):abort(404)
   db.session.add(FarmerCrop(farmer_id=p.id,crop_id=cid,variety=request.form.get("variety","").strip(),area=num("area",0) if request.form.get("area") else None,area_unit=request.form.get("area_unit","acre"),sowing_date=dt("sowing_date"),expected_harvest_date=dt("expected_harvest_date"),expected_quantity=qty)); commit("Crop added.")
  return redirect(url_for("farmer_crops"))
 return render_template("crops.html",crops=Crop.query.order_by(Crop.name).all(),entries=FarmerCrop.query.filter_by(farmer_id=p.id).all())
@app.route("/farmer/lots",methods=["GET","POST"])
@role_required("farmer")
def farmer_lots():
 p=farmer()
 if request.method=="POST":
  try:
   cid=int(request.form.get("crop_id","")); q,price=num("quantity",0),num("expected_price",0); m,f,d=num("moisture",0),num("foreign_matter",0),num("damage_percentage",0)
   if not db.session.get(Crop,cid):abort(404)
   pic=request.files.get("image"); name=None
   if pic and pic.filename:
    ext=pic.filename.rsplit(".",1)[-1].lower() if "." in pic.filename else ""
    if ext not in IMAGES:raise ValueError("Use JPG, JPEG, PNG, or WEBP images only.")
    name=f"{uuid4().hex}_{secure_filename(pic.filename)}"; pic.save(upload_dir/name)
   score,g=quality(m,f,d); db.session.add(Lot(farmer_id=p.id,crop_id=cid,lot_number=f"LOT-{uuid4().hex[:10].upper()}",variety=request.form.get("variety","").strip(),quantity=q,unit=request.form.get("unit","quintal"),harvest_date=dt("harvest_date"),moisture=m,foreign_matter=f,damage_percentage=d,quality_score=score,quality_grade=g,expected_price=price,location=request.form.get("location","").strip(),description=request.form.get("description","").strip(),image=name)); commit("Lot created with preliminary digital grading.")
  except ValueError as x:flash(str(x))
  return redirect(url_for("farmer_lots"))
 return render_template("lots.html",own=True,lots=Lot.query.filter_by(farmer_id=p.id).all(),crops=Crop.query.order_by(Crop.name).all())
@app.route("/farmer/lots/<int:lot_id>/delete",methods=["POST"])
@role_required("farmer")
def delete_lot(lot_id):
 x=Lot.query.filter_by(id=lot_id,farmer_id=farmer().id).first_or_404()
 if x.status!="available":flash("Only available lots can be deleted.")
 else:db.session.delete(x);commit("Lot deleted.")
 return redirect(url_for("farmer_lots"))
@app.route("/lots")
@role_required("buyer")
def available_lots():
 q=Lot.query.filter_by(status="available"); cid=request.args.get("crop_id",type=int)
 if cid:q=q.filter_by(crop_id=cid)
 return render_template("lots.html",own=False,lots=q.all(),crops=Crop.query.order_by(Crop.name).all())
@app.route("/buyer/requirements",methods=["GET","POST"])
@role_required("buyer")
def requirements():
 p=buyer()
 if request.method=="POST":
  try:cid=int(request.form.get("crop_id",""));q=num("required_quantity",0)
  except (ValueError,TypeError):flash("Select a crop and valid quantity.")
  else:
   if not db.session.get(Crop,cid):abort(404)
   db.session.add(BuyerRequirement(buyer_id=p.id,crop_id=cid,required_quantity=q,unit=request.form.get("unit","quintal"),min_quality_grade=request.form.get("min_quality_grade","C"),max_price=num("max_price",0) if request.form.get("max_price") else None,delivery_location=request.form.get("delivery_location","").strip(),required_by=dt("required_by"),description=request.form.get("description","").strip()));commit("Requirement created.")
  return redirect(url_for("requirements"))
 return render_template("requirements.html",crops=Crop.query.order_by(Crop.name).all(),requirements=BuyerRequirement.query.filter_by(buyer_id=p.id).all())
@app.route("/offers",methods=["GET","POST"])
@login_required
def offers():
 u=user()
 if u.role=="buyer" and request.method=="POST":
  p=buyer();x=db.session.get(Lot,request.form.get("lot_id",type=int))
  if not x or x.status!="available":abort(404)
  try:q,price=num("quantity",0),num("offered_price",0)
  except ValueError as e:flash(str(e))
  else:
   if q>x.quantity:flash("Offer quantity cannot exceed lot quantity.")
   elif Offer.query.filter_by(lot_id=x.id,buyer_id=p.id,status="pending").first():flash("You already have a pending offer on this lot.")
   else:db.session.add(Offer(lot_id=x.id,buyer_id=p.id,farmer_id=x.farmer_id,quantity=q,offered_price=price,message=request.form.get("message","").strip(),expires_at=datetime.utcnow()+timedelta(days=7)));commit("Offer sent.")
  return redirect(url_for("offers"))
 data=Offer.query.filter_by(farmer_id=farmer().id).all() if u.role=="farmer" else Offer.query.filter_by(buyer_id=buyer().id).all() if u.role=="buyer" else Offer.query.all()
 return render_template("offers.html",offers=data,lots=Lot.query.filter_by(status="available").all() if u.role=="buyer" else [])
@app.route("/offers/<int:offer_id>/<action>",methods=["POST"])
@role_required("farmer")
def decide_offer(offer_id,action):
 x=Offer.query.filter_by(id=offer_id,farmer_id=farmer().id).first_or_404()
 if x.status!="pending" or action not in {"accept","reject"}:abort(400)
 if action=="reject":x.status="rejected";commit("Offer rejected.")
 elif x.lot.status!="available":flash("This lot already has an accepted offer.")
 else:
  x.status="accepted";x.lot.status="sold";db.session.add(Transaction(transaction_number=f"TXN-{uuid4().hex[:10].upper()}",offer_id=x.id,farmer_id=x.farmer_id,buyer_id=x.buyer_id,lot_id=x.lot_id,quantity=x.quantity,price_per_unit=x.offered_price,total_amount=x.quantity*x.offered_price));Offer.query.filter(Offer.lot_id==x.lot_id,Offer.id!=x.id,Offer.status=="pending").update({Offer.status:"rejected"});commit("Offer accepted and transaction created.")
 return redirect(url_for("offers"))
@app.route("/transactions")
@login_required
def transactions():
 u=user();q=Transaction.query.filter_by(farmer_id=farmer().id) if u.role=="farmer" else Transaction.query.filter_by(buyer_id=buyer().id) if u.role=="buyer" else Transaction.query
 return render_template("transactions.html",transactions=q.all())
@app.route("/storage")
@login_required
def storage():return render_template("storage.html",facilities=StorageFacility.query.all())
@app.route("/transport",methods=["GET","POST"])
@login_required
def transport():
 txs=[x for x in Transaction.query.all() if allowed(x)]
 if request.method=="POST":
  x=db.session.get(Transaction,request.form.get("transaction_id",type=int));p=db.session.get(TransportProvider,request.form.get("provider_id",type=int))
  if not x or not p or not allowed(x):abort(403)
  try:d=num("distance_km",0)
  except ValueError as e:flash(str(e))
  else:db.session.add(TransportRequest(transaction_id=x.id,provider_id=p.id,pickup_location=request.form.get("pickup_location","").strip(),delivery_location=request.form.get("delivery_location","").strip(),distance_km=d,estimated_cost=d*p.cost_per_km));commit("Transport requested.")
  return redirect(url_for("transport"))
 return render_template("transport.html",transactions=txs,providers=TransportProvider.query.filter_by(is_available=True).all())
@app.route("/payments",methods=["GET","POST"])
@login_required
def payments():
 txs=[x for x in Transaction.query.all() if allowed(x)]
 if request.method=="POST":
  x=db.session.get(Transaction,request.form.get("transaction_id",type=int))
  if not x or not allowed(x):abort(403)
  if Payment.query.filter_by(transaction_id=x.id).first():flash("A payment record already exists.")
  else:db.session.add(Payment(transaction_id=x.id,amount=x.total_amount,payment_method="Demo",transaction_reference=f"DEMO-{uuid4().hex[:8]}",payment_date=datetime.utcnow(),status="paid",notes="Demo payment"));commit("Demo payment marked paid.")
  return redirect(url_for("payments"))
 return render_template("payments.html",transactions=txs,payments=[p for x in txs for p in x.payments])
@app.route("/disputes",methods=["GET","POST"])
@login_required
def disputes():
 txs=[x for x in Transaction.query.all() if allowed(x)]
 if request.method=="POST":
  x=db.session.get(Transaction,request.form.get("transaction_id",type=int));desc=request.form.get("description","").strip()
  if not x or not allowed(x):abort(403)
  if not desc:flash("Enter a dispute description.")
  else:db.session.add(Dispute(transaction_id=x.id,raised_by=user().id,category=request.form.get("category","Other"),description=desc));commit("Dispute submitted.")
  return redirect(url_for("disputes"))
 return render_template("disputes.html",transactions=txs,disputes=Dispute.query.all() if user().role=="admin" else [d for x in txs for d in x.disputes])
@app.route("/admin/buyers/<int:buyer_id>/verify",methods=["POST"])
@role_required("admin")
def verify_buyer(buyer_id):
 x=db.session.get(Buyer,buyer_id) or abort(404);x.is_verified=True;x.verification_date=datetime.utcnow();commit("Buyer verified.");return redirect(url_for("dashboard"))
@app.route("/logout")
def logout():session.clear();flash("Logged out successfully.");return redirect(url_for("home"))
@app.errorhandler(403)
def e403(_):return render_template("error.html",code=403,message="You do not have permission to access this page."),403
@app.errorhandler(404)
def e404(_):return render_template("error.html",code=404,message="The requested record or page was not found."),404
if __name__=="__main__":app.run(debug=True)
