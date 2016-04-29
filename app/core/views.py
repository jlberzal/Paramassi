# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template, flash, render_template_string, Blueprint,g
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted
from datetime import datetime
from app import app, db, constants
from app.core.models import UserProfileForm
from app.core.models import Question
from app.core.models import QuestionForm
from app.core.models import AnswerForm
from app.core.models import CalcProt
from app.core.models import CalcForm

core_blueprint = Blueprint('core', __name__, url_prefix='/')



# The Home page is accessible to anyone

@core_blueprint.route('')
@core_blueprint.route('home_page')
def home_page():
    return render_template('core/user_page.html')


# The User page is accessible to authenticated users (users that have logged in)
@core_blueprint.route('user')
@login_required  # Limits access to authenticated users
def user_page():
    return render_template('core/user_page.html')

# The Admin page is accessible to users with the 'admin' role
@core_blueprint.route('admin')
@roles_accepted('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('core/admin_page.html')


@core_blueprint.route('user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('core.home_page'))

    # Process GET or invalid POST
    return render_template('core/user_profile_page.html',
                           form=form)



# Codigo especifico de Paramassi
#********************************

# This is the page for posting questions
@core_blueprint.route('post_question', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def post_question():

	form = QuestionForm()
	if request.method == 'POST':
		if form.validate() == False:
			flash('All fields are required.')
			return render_template('core/post_question.html', title ='Preguntas', form=form)
# Lo unico que se valida es que el texto no este vacio

		else:
# logica de insercion de preguntas en BD
#...
			usermail = current_user.email
			question = Question(body=form.question_text.data,timestamp=datetime.utcnow(), author=current_user, user_email = usermail,answer_email = usermail)
			db.session.add(question)
			db.session.commit()
			flash('Your post is now live!')
			return render_template('core/post_question.html', title ='Preguntas', success=True)
	elif request.method == 'GET':
		return render_template('core/post_question.html', title ='Preguntas', form=form)

# This is the page for answering questions
@core_blueprint.route('answer_question/<int:question_id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def answer_question(question_id):
# Buscamos la pregunta

	query = "select body, timestamp,user_email from Questions where id = %s" % question_id

	cur = db.session.execute(query)	
	
	results = cur.fetchone()
	question = dict( id=question_id, body=results[0], timestamp=results[1], user_email = results[2]  ) 
	
	form = AnswerForm()
	
	if request.method == 'POST':
	
# Aqui se presenta el formulario:
		if form.validate() == False:
			# key = input ("hit key 2")	
			flash('All fields are required.')
			return render_template('core/answer_question.html', title ='Responder', question=question,form=form)
# En realidad esto no hace falta porque siempre se va a aceptar lo que se ponga
		else:
# logica de insercion de preguntas en BD
#...
			answermail = current_user.email
			timestamp=datetime.utcnow()
			query = 'UPDATE Questions SET answer = "%s", answer_email = "%s", answer_timestamp = "%s" WHERE id = %s' % (form.answer_text.data , answermail, timestamp, question_id)
			print query
			cur = db.session.execute(query)	
			db.session.commit()
			
			#key = input ("hit key 3")	

			#question = Question(body=form.question_text.data,timestamp=datetime.utcnow(), author=current_user, user_email = usermail,answer_email = usermail)
			#db.session.add(question)
			#db.session.commit()
			#flash('Your post is now live!')
			return render_template('core/answer_question.html', title ='Preguntas', success=True)
	elif request.method == 'GET':
		return render_template('core/answer_question.html', title ='Preguntas', question=question, form=form)

# This is the page for displaying questions posted by the user
@core_blueprint.route('list_questions')
@login_required  # Limits access to authenticated users
def list_questions():

# El administrados ve todas las preguntas, el usuario solo ve las suyas
	
	if current_user.is_admin():
		query = "select id, body, timestamp,user_email, answer_email,answer_timestamp,answer from Questions order by timestamp desc"
	else:
		query = "select id, body, timestamp, user_email, answer_email,answer_timestamp,answer from Questions where user_id = %s order by timestamp desc" % current_user.id

	cur = db.session.execute(query)
		
	questions = [dict( id=row[0], body=row[1], timestamp=row[2], user_email=row[3], answer_email=row[4], answer_timestamp=row[5], answer=row[6]) for row in cur.fetchall()]
	
	return render_template('core/display_user_questions.html', questions=questions)


# Codigo de Calculos de proteccion

@core_blueprint.route('calc_prot/String:<TipoC>/String:<TipoProt>', methods=['GET', 'POST'])
@core_blueprint.route('calc_prot', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users

def calc_prot(TipoC='C1',TipoProt='ProActive'):

	print "TipoC = ",  TipoC
	print "TipoProt = ",  TipoProt

	form = CalcForm()
#	form.initialize()
	form.TipoC.data = TipoC
	if request.method == 'POST':
			
		if form.validate() == False:
			for field, errors in form.errors.items():
				for error in errors:
					flash(u"Error in the %s field - %s" % (getattr(form, field).label.text,error))
					flash(u"value = %s" % (getattr(form, field).data))
		
			return render_template('core/calc_prot.html', TipoC = TipoC, TipoProt = TipoProt, form=form)
			
		
		estable = form.Estabilidad()
		
		if form.Estabilidad() == 1:
			flash('La cunha introducida es estable')
		else:

			if TipoProt ==  'ProActive':
				a = form.CoefSegProActive() 	
			if TipoProt ==  'ProActiveST':
				a = form.CoefSegProActiveST() 	
			if ((TipoProt ==  'NetProtect') or TipoProt ==  ('NetProtectST')):
				a = form.CoefSegNetProtect()
				
			# Guardamos la infomracion en un registro de BD
			
			form.TipoProt.data = TipoProt
			
			usermail = current_user.email
			question = CalcProt(timestamp=datetime.utcnow(), \
				author=current_user, user_email = usermail, \
				TipoC = form.TipoC.data, \
				h1 = form.h1.data, \
				h2 = form.h2.data, \
				d = form.d.data, \
				b = form.b.data, \
				L = form.L.data, \
				Coh = form.Coh.data, \
				Roz = form.Roz.data, \
				Dens = form.Dens.data, \
				AcSis = form.AcSis.data, \
				TipoProt = form.TipoProt.data, \
				DistCor = form.DistCor.data, \
				SH_B = form.SH_B.data, \
				SV_B = form.SV_B.data, \
				LongBulon = form.LongBulon.data, \
				DiamAcero = form.DiamAcero.data, \
				Adh = form.Adh.data, \
				fck = form.fck.data, \
				DiamPerf = form.DiamPerf.data, \
				FSI = form.FSI.data, \
				FR = form.FR.data, \
				R1 = form.R1.data, \
				R1Cumple = form.R1Cumple.data, \
				R2 = form.R2.data, \
				R2Cumple = form.R2Cumple.data, \
				R1R2 = form.R1R2.data, \
				R1R2Cumple = form.R1R2Cumple.data, \
				PNd = form.PNd.data, \
				P1 = form.P1.data, \
				P1Cumple = form.P1Cumple.data, \
				P2 = form.P2.data, \
				P2Cumple = form.P2Cumple.data, \
				P3 = form.P3.data, \
				P3Cumple = form.P3Cumple.data, \
				FSfinal = form.FSfinal.data, \
				FSfinalCumple = form.FSfinalCumple.data \
			)
			db.session.add(question)
			db.session.commit()
		
		return render_template('core/calc_prot_res.html', title ='Calculo de Protecciones', TipoC = TipoC, TipoProt = TipoProt, Estable = estable, form=form,success=True)
			
	elif request.method == 'GET':
	# esta es la primera llamada a la funcion inicializamos el form
		a = form.initialize()
		
		print 'Request method GET'
			
		return render_template('core/calc_prot.html', title ='Calculo de Protecciones', TipoC = TipoC, TipoProt = TipoProt,form=form)

# This is the page for displaying questions posted by the user
@core_blueprint.route('list_calculations')
@login_required  # Limits access to authenticated users
def list_calculations():

	if current_user.is_admin():
		query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSfinalCumple, user_email from calculations order by timestamp desc"
	else:
			query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSfinalCumple, user_email from calculations where user_id = %s  order by timestamp desc" % current_user.id
	cur = db.session.execute(query)

	calculations = [dict( id=row[0], timestamp=row[1], TipoC=row[2], h1=row[3], h2=row[4], d=row[5], b=row[6], L=row[7], Coh=row[8], roz=row[9], Dens=row[10], AcSis=row[11], TipoProt=row[12], DistCor=row[13], \
	SH_B=row[14], SV_B=row[15], LongBulon=row[16], DiamAcero=row[17], Adh=row[18], fck=row[19], DiamPerf=row[20], FSC =  row[21],  user_email = row[22]) for row in cur.fetchall()]
	

	return render_template('core/display_user_calculations.html', calculations = calculations)


@core_blueprint.route('display_calc(/<int:calc_id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def display_calc (calc_id):

#	query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple where id = %s" % calc_id
	query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple from calculations where id = %s" % calc_id
	cur = db.session.execute(query)
	
	# reutilizamos el template de presentacion de resultados
	
	form = CalcForm()
	
	results = cur.fetchone()
	
	form.TipoC.data = results[2]
	form.h1.data= results[3]
	form.h2.data= results[4]
	form.d.data= results[5]
	form.b.data= results[6]
	form.L.data= results[7]
	form.Coh.data= results[8]
	form.Roz.data= results[9]
	form.Dens.data= results[10]
	form.AcSis.data= results[11]
	form.TipoProt.data= results[12]
	form.DistCor.data= results[13]
	form.SH_B.data= results[14]
	form.SV_B.data= results[15]
	form.LongBulon.data= results[16]
	form.DiamAcero.data= results[17]
	form.Adh.data= results[18]
	form.fck.data= results[19]
	form.DiamPerf.data= results[20]
	form.FSI.data= results[21]
	form.FR.data= results[22]
	form.R1.data= results[23]
	form.R1Cumple.data= results[24]
	form.R2.data= results[25]
	form.R2Cumple.data= results[26]
	form.R1R2.data= results[27]
	form.R1R2Cumple.data= results[28]
	form.PNd.data= results[29]
	form.P1.data= results[30]
	form.P1Cumple.data= results[31]
	form.P2.data= results[32]
	form.P2Cumple.data= results[33]
	form.P3.data= results[34]
	form.P3Cumple.data= results[35]
	form.FSfinal.data= results[36]
	form.FSfinalCumple.data= results[37]
	
	return render_template('core/calc_prot_res.html', title ='Calculo de Protecciones', TipoC = form.TipoC.data, TipoProt = form.TipoProt.data, Estable = False, form=form,success=True)
	
# Esto tiene que estar al final !!!!!! 
# Register blueprint
app.register_blueprint(core_blueprint)







