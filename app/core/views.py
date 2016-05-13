# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template, flash, render_template_string, Blueprint,g
from flask import request, url_for

from flask import send_file
import StringIO

from flask_user import current_user, login_required, roles_accepted
from datetime import datetime
from app import app, db, constants
from app.core.models import UserProfileForm
from app.core.models import Question
from app.core.models import QuestionForm
from app.core.models import AnswerForm
from app.core.models import CalcProt
from app.core.models import CalcForm
from app.core.pdf_par import generate_pdf


from flask import make_response

from reportlab.pdfgen import canvas



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
	form.TipoC.data = TipoC
	form.TipoProt.data = TipoProt
	
	if request.method == 'POST':
			
		if form.validate() == False:
			for field, errors in form.errors.items():
				for error in errors:
					flash((u"Error en la entrada: %s - %s" % (getattr(form, field).label.text,error)),'error')
		
			return render_template('core/calc_prot.html', TipoC = TipoC, TipoProt = TipoProt, form=form)
			
		# a = form.initialize_results()
		
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
			
				
			form.TipoProt.data = TipoProt
	
			# Guardamos la infomracion en un registro de BD
			# Preparamos query 
			query = 'insert into calculations (timestamp, user_id, user_email, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, \
			TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, \
			R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple) \
			values ("%s",%s,"%s","%s",%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s",%s,%s,%s,%s,%s,%s,\
			%s,%s,%s,%s,%s,%d,%s,%d,%s,%d,%s,%s,%d,%s,%d,%s,%d,%s,%d)'\
			% (datetime.utcnow(),\
			current_user.id,\
			current_user.email,\
			form.TipoC.data, \
			form.h1.data, \
			form.h2.data, \
			form.d.data, \
			form.b.data, \
			form.L.data, \
			form.Coh.data, \
			form.Roz.data, \
			form.Dens.data, \
			form.AcSis.data, \
			form.TipoProt.data, \
			form.DistCor.data, \
			form.SH_B.data, \
			form.SV_B.data, \
			form.LongBulon.data, \
			form.DiamAcero.data, \
			form.Adh.data, \
			form.fck.data, \
			form.DiamPerf.data, \
			form.FSI.data, \
			form.FR.data, \
			form.R1.data, \
			form.R1Cumple.data, \
			form.R2.data, \
			form.R2Cumple.data, \
			form.R1R2.data, \
			form.R1R2Cumple.data, \
			form.PNd.data,\
			form.P1.data, \
			form.P1Cumple.data, \
			form.P2.data, \
			form.P2Cumple.data, \
			form.P3.data, \
			form.P3Cumple.data, \
			form.FSfinal.data, \
			form.FSfinalCumple.data)
	
			cur = db.session.execute(query)
	
	
			id = cur.lastrowid
			
			cur = db.session.commit()
			form.id.data= id
			
			print "id=", id
			
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
	
	form.id.data = calc_id
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
	
@core_blueprint.route('change_calc(/<int:calc_id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def change_calc (calc_id):
	query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple from calculations where id = %s" % calc_id
	cur = db.session.execute(query)
	
	# reutilizamos el template de presentacion de resultados
	
	form = CalcForm()
	
	results = cur.fetchone()
	
	form.id.data = calc_id
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
	
	return render_template('core/calc_prot.html', title ='Calculo de Protecciones', TipoC = form.TipoC.data, TipoProt = form.TipoProt.data, Estable = False, form=form,success=True)


@core_blueprint.route('change_prot/String:<TipoProt>/<int:calc_id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def change_prot (TipoProt, calc_id=1):
	query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple from calculations where id = %s" % calc_id
	cur = db.session.execute(query)
	form = CalcForm()
	results = cur.fetchone()
	
	# reutilizamos el template de presentacion de resultados
	print " Change prot to TipoC = ",  form.TipoC.data
	print "TipoProt = ",  TipoProt

	form.id.data = calc_id
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

	form.TipoProt.data = TipoProt

	return render_template('core/calc_prot.html', TipoC = form.TipoC.data, TipoProt = TipoProt, form=form,  method = "POST")

#pruebas de pdf


@app.route('/foo/')
def document_html():
    return render_template(
        'core/test_pdf.html', data=[42, 27.3, 63], labels=['Lorem', 'ipsum', 'sit'])


@app.route('/foo/graph')
def graph():
    svg = render_template(
        'graph.svg',
        # Turn ?data=3,2,1&labels=A,B,C into
        # [(0, ('A', 3, color0)), (1, ('B', 2, color1)), (2, ('C', 1, color2))]
        series=enumerate(zip(
            request.args['labels'].split(','),
            map(float, request.args['data'].split(',')),
            app.config['GRAPH_COLORS'])))
    return svg, 200, {'Content-Type': 'image/svg+xml'}


### The code specific to Flask-WeasyPrint follows. Pretty simple, eh?

from flask_weasyprint import render_pdf, HTML


@app.route('/foo.pdf')
def document_pdf():
	calc_id = 22
	query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple from calculations where id = %s" % calc_id
	cur = db.session.execute(query)
	form = CalcForm()
	results = cur.fetchone()
	
	# reutilizamos el template de presentacion de resultados
	
	form.id.data = calc_id
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
	
	#html = render_template('core/calc_prot.html', TipoC = form.TipoC.data, TipoProt = "NetProtect", form=form,  method = "POST")

	html =render_template('core/test_pdf.html', TipoC = "C1" )
	print "Html ok"
	
	return render_pdf(HTML(string=html))


@app.route('/foo.png')
def document_png():
    # We didnt bother to make a ``render_png`` helper
    # but of course you can still use WeasyPrints PNG output.
    return Response(HTML('/').write_png(), mimetype='image/png')















@core_blueprint.route('pdf/<int:calc_id>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def pdf (calc_id=1):

	
	query = "select id, timestamp, TipoC, h1, h2, d, b, L, Coh, roz, Dens, AcSis, TipoProt, DistCor, SH_B, SV_B, LongBulon, DiamAcero, Adh, fck, DiamPerf, FSI, FR, R1, R1Cumple, R2, R2Cumple, R1R2, R1R2Cumple, PNd,  P1, P1Cumple, P2, P2Cumple, P3, P3Cumple,FSfinal, FSfinalCumple from calculations where id = %s" % calc_id
	cur = db.session.execute(query)
	
	
	# reutilizamos el template de presentacion de resultados
	
	form = CalcForm()
	
	results = cur.fetchone()
	
	form.id.data = calc_id
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
	
	html =render_template('core/report.html', form=form )
	
	return render_pdf(HTML(string=html))


	
# Esto tiene que estar al final !!!!!! 
# Register blueprint
app.register_blueprint(core_blueprint)







