# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from flask_user.forms import RegisterForm
from flask_wtf import Form

from wtforms import StringField, IntegerField, TextField, SubmitField, SelectField, BooleanField, FloatField, validators
from app import db
import math


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    company = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))
   # Preguntas 
    questions = db.relationship('Question', backref='author', lazy='dynamic')
    calculations = db.relationship('CalcProt', backref='author', lazy='dynamic')
    def is_admin(self):
    	if self.email == 'admin@example.com':
    		return (True)
    	else: 
    		return(False)


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    first_name = StringField('Nombre', validators=[
        validators.DataRequired('Se requiere dar un nombre')])
    last_name = StringField('Apellido', validators=[
        validators.DataRequired('Se requiere un apellido')])
    company = StringField('Empresa', validators=[
        validators.DataRequired('Introduzca el nombre de su empresa')])


# Define the User profile form
class UserProfileForm(Form):
    first_name = StringField('Nombre', validators=[
        validators.DataRequired('Se necesita dar un nombre')])
    last_name = StringField('Apellido', validators=[
        validators.DataRequired('Se necesita un apellido')])
    submit = SubmitField('Guardar')

# Nuevos tipos de datos para la aplicacion de Paramassi


# Define the question
#--------------------------------------------------------
class Question(db.Model):
	__tablename__='questions'
	
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.Text)
	answer = db.Column(db.Text)
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user_email = db.Column(db.Unicode(255), nullable=False, server_default=u'')
	answer_timestamp = db.Column(db.DateTime)
	answer_email = db.Column(db.Unicode(255))	
	
	def __repr__(self):
		return '<Question %r>' % (self.body)


# Define the question form
class QuestionForm(Form):
    question_text = TextField('Escriba su pregunta', validators=[
    	validators.DataRequired('La pregunta no puede estar vacia')])
    submit = SubmitField('Enviar')

# Define the answer form
class AnswerForm(Form):
    answer_text = TextField('Escriba su respuesta', validators=[
    	validators.DataRequired('La respuesta no puede estar vacia')])
    submit = SubmitField('Guardar')


# Definir formulario Calculos
#--------------------------------------------------------------------------------------------------------
#
# Este es el formulario de los calculos de proteccion
# Incluye las dimensiones que se deben introducir en cada caso y los calculos de fuerzas y resistencias
# como propiedades de la Clase.
#

class CalcForm(Form):
# Dimensiones:
# Datos de la cunha
	TipoC= SelectField( label = 'Tipo de C',
	 choices=[('C1','C1'),('C2','C2'),('C3','C3'),('C4','C4')])

	TipoProt= SelectField( label = 'Tipo de Proteccion',
	 choices=[('ProActive','ProActive'),('ProActiveST','ProActiveST'),('NetProtect','NetProtect'),('NetProtectST','NetProtectST')],validators=[validators.Optional()])

# Nota: los valores anteriores se registran mediante cambios en las pestanhas, no son campos que se presenten 

# valor para almacenar el indice de bd

	id = IntegerField(label = 'ID', default=0)


	h1 = FloatField( label = 'Altura, h1 (m)', default=0,validators=[validators.InputRequired()])	
	h2 = FloatField( label = 'Altura, h2 (m)', default=0,validators=[validators.Optional()])
	# nota	se usa h1 como H en los casos correspondientes
	d = FloatField( label = 'Espesor d(m)', default=0,validators=[validators.InputRequired()])
	
	b = FloatField( label = 'Inclinacion b():', default=0,validators=[validators.Optional()])
	L = FloatField( label = 'Longitud, L(m):', default=0,validators=[validators.Optional()])	
	# nota L =1 en casos C1 y C2
		
	Coh = FloatField( label = 'Cohesion(kN/M2)', default=0,validators=[validators.Optional()])	
	Roz = FloatField( label = 'Roz.Interno()', default=0,validators=[validators.Optional()])	
	Dens = FloatField( label = 'Densidad(kN/m3)', default=0,validators=[validators.InputRequired()])	
	AcSis = FloatField( label = 'Ac.Sismica (m/s2)', default=0,validators=[validators.Optional()])	

# Datos de Anclajes
	
	# DistCor es la distancia de los anclajes en coronacion
	DistCor = FloatField( label = 'Coronacion (m)', default=1.0,validators=[validators.Optional(),validators.NumberRange(min=0.00001, message='el valor debe ser mayor que cero') ])
		

	TipoMalla = SelectField( label = 'Tipo de Malla',
	 choices=[('6x8-14','6x8-14'),('8x10-15','8x10-15'),('8x10-16','8x10-16'),('8x10-17','8x10-17') ], default='6x8-14' )
	 
	TipoCableRefuerzo = SelectField( label = 'Cable de Refuerzo',
	 choices=[('8','8mm'),('10','10mm'),('12','12mm'),('14','14mm'),('16','16mm'),('18','18mm'),('20','20mm'),('22','22mm'),('24','24mm')], default='8')

	TipoRedNP = SelectField( label = 'Tipo de Red',
	 choices=[('Paneles 200', 'Paneles 200'),('Paneles 250', 'Paneles 250'),('Paneles 300', 'Paneles 300'),('Paneles 400', 'Paneles 400')],default='Paneles 200') 

	TipoRedNPST = SelectField( label = 'Tipo de Red',
	 choices=[('LitoStop 2/350','LitoStop 2/350'),('LitoStop 2/300','LitoStop 2/300'),('LitoStop 2/250','LitoStop 2/250'),('LitoStop 3/350','LitoStop 3/350'),('LitoStop 3/300','LitoStop 3/300')], default='LitoStop 2/350')
	 
# Datos de los bulones
# --------------------

	SH_B = FloatField( label = 'Separacion horizontal (m)',  default=1.0,validators=[validators.Optional(),validators.NumberRange(min=0.00001, message='el valor debe ser mayor que cero') ])
	SV_B = FloatField( label = 'Separacion vertical (m)',  default=1.0,validators=[validators.Optional(),validators.NumberRange(min=0.00001, message='el valor debe ser mayor que cero') ])
		
# Datos comunes
# ------------- 

	LongBulon = FloatField( label = 'Longitud, L(m)', default=0,validators=[validators.InputRequired()])	
	DiamAcero = SelectField( label = 'D. Acero (mm)',
	 choices=[('16','16mm'),('20','20mm'),('25','25mm'),('28','28mm'),('32','32mm'),('40','40mm'),('50','50mm'),('63','63.5mm')], default='16')
	 
	Adh= FloatField( label = 'Adherencia (Mpa)', default=0,validators=[validators.InputRequired()])	
	fck = FloatField( label = 'fck lechada (Mpa)', default=0,validators=[validators.InputRequired()])	
	DiamPerf = SelectField( label = 'D perforacion (mm)', 
	choices=[('46','46mm'),('51','51mm'),('75','75mm'),('115','115mm'),('130','130mm'),('200','200mm')],default='46')
	
# Resultados de los calculos
# --------------------------
	# La superficie se calcula para cada tipo de cuna
	Superficie = FloatField( label = 'Superficie', default = 0)
	
	# Coeficiente de seguridad inicial FSI 
	FSI = FloatField(label  = 'FS Inicial', default = 0)
	
	# Fuerza Resultante FR
	FR = FloatField(label  = 'FS Inicial', default = 0)
	R1 = FloatField(label  = 'FS Inicial', default = 0)
	R1Cumple = BooleanField( default = 0)
	R2 = FloatField(label  = 'FS Inicial', default = 0)	
	R2Cumple = BooleanField( default = 0)
	# esto solo se usa para el caso MTT en realidad es la suma de R1 y R2
	R1R2 = FloatField(label  = 'R1R2 (kN)', default = 0)
	R1R2Cumple = BooleanField( default = 0)


	PNd = FloatField(label  = 'FS Inicial', default = 0)
	P1 = FloatField(label  = 'FS Inicial', default = 0)
	P1Cumple = BooleanField(default = 0)
	P2 = FloatField(label  = 'FS Inicial', default = 0)	 
	P2Cumple = BooleanField(default = 0)
	P3 = FloatField(label  = 'FS Inicial', default = 0)	 
	P3Cumple = BooleanField(default = 0)
	FR1 = FloatField(label  = 'R2 (kN)', default = 0)
	FR2 = FloatField(label  = 'R2 (kN)', default = 0)

	FP1 = FloatField(label  = 'P1 (kN)', default = 0)
	FP2 = FloatField(label = 'P2 (kN)', default = 0)	
	FP3 = FloatField(label = 'P3 (kN)', default = 0)	
	FSfinal = FloatField (label = 'FS Final', default = 0)	
	FSfinalCumple = BooleanField(default = 0)
	
	submit = SubmitField('Validar')
	
# Resultados de pruebas	

# Funciones de calculo
#---------------------

# Lo primero que se calcula es el coeficiente de seguridad y la fuerza resultante
# Estos valores se rellenan al invocarse a la funcion Estabilidad

	def Estabilidad (self):
		
		if self.TipoC.data == 'C1':

		# Calculo de FSI y Fuerza resultante para C1
				
			DistAux = self.d.data + self.h1.data/math.tan(math.radians(self.b.data))
			Alpha = math.atan2(self.h1.data, DistAux)
			# Alpha esta en radianes
			
			# Para los casos C1 y C2 L = 1 (se hace por unidad de longitud)
			self.L.data = 1
			
			Lr = self.h1.data /math.sin(Alpha)
			L_ext = self.h1.data /math.sin(math.radians(self.b.data))
			Peso = 0.5 * self.h1.data * self.d.data * self.Dens.data * 1
			self.FR.data = 1.25 * (Peso * math.sin(Alpha) - (Peso * math.cos(Alpha)-Peso/9.81*self.AcSis.data*math.sin(Alpha))*math.tan(math.radians(self.Roz.data)) + Peso/9.81*self.AcSis.data*math.cos(Alpha))
			self.FSI.data = (self.Coh.data*1*Lr+(Peso*math.cos(Alpha) - Peso/9.81*self.AcSis.data*math.sin(Alpha))*math.tan(math.radians(self.Roz.data)))/(Peso*math.sin(Alpha)+Peso/9.81*self.AcSis.data*math.cos(Alpha))
			self.Superficie.data = self.L.data * L_ext
					
			# Debug - Comentar en Version final	
		
			print "C1 Alpha = ",math.degrees(Alpha)
			print "C1 Lr = ",Lr
			print "C1 L_ext = ",L_ext
			print "C1 Peso = ",Peso
			print "C1 Fuerza Resultante = ",self.FR.data		
			print "C1 FSinicial = ",self.FSI.data		
			
			if self.FSI.data > 1:
				return_value = 1
			else: 
				return_value = 0
			
		elif self.TipoC.data == 'C2':
		
		
			DistAux = self.d.data + self.h1.data/math.tan(math.radians(self.b.data))
			Alpha = math.atan2(self.h1.data, DistAux)
			# Alpha esta en radianes
			
			self.L.data = 1
			
			Lr = self.h1.data/math.sin(Alpha) + self.h2.data/math.sin(math.radians(self.b.data))
			L_ext = self.h1.data /math.sin(math.radians(self.b.data))+self.h2.data /math.sin(math.radians(self.b.data))
			Peso1 = 0.5 * self.h1.data * self.d.data * self.Dens.data * 1
			Peso2 = self.h2.data * self.d.data * self.Dens.data * 1
			self.FR.data = 1.25 * 	(Peso1 * math.sin(Alpha) - (Peso1 * math.cos(Alpha)-Peso1/9.81*self.AcSis.data*math.sin(Alpha))*math.tan(math.radians(self.Roz.data)) + Peso1/9.81*self.AcSis.data*math.cos(Alpha)+
									 Peso2 * math.sin(math.radians(self.b.data)) - (Peso2 * math.cos(math.radians(self.b.data))-Peso2/9.81*self.AcSis.data*math.sin(math.radians(self.b.data)))*math.tan(math.radians(self.Roz.data)) + Peso2/9.81*self.AcSis.data*math.cos(math.radians(self.b.data)))
			
			
			# Para hacer la formula de FSI mas manejable, separamos numerador y denominador
			
			A = (self.Coh.data * 1 * Lr + (Peso1 * math.cos(Alpha) - Peso1 / 9.81 * self.AcSis.data * math.sin(Alpha)) * math.tan(math.radians(self.Roz.data)) + \
			(Peso2 * math.cos(math.radians(self.b.data)) - Peso2 / 9.81 * self.AcSis.data * math.sin(math.radians(self.b.data))) * math.tan(math.radians(self.Roz.data)))
			# print "A=", A
			
			B = (Peso1 * math.sin(Alpha) + Peso1 / 9.81 * self.AcSis.data * math.cos(Alpha))+ (Peso2 * math.sin(math.radians(self.b.data)) + Peso2 / 9.81 * self.AcSis.data * math.cos(math.radians(self.b.data)))
			# print "B=", B
			
			self.FSI.data = A/B
			

			

			FS4 = (Peso1 * math.sin(Alpha) + Peso1 / 9.81 * self.AcSis.data * math.cos(Alpha) + Peso2 * math.sin(math.radians(self.b.data) + Peso2 / 9.81 * self.AcSis.data * math.cos(math.radians(self.b.data))))
			self.Superficie.data = self.L.data * L_ext

			# Debug - Comentar en Version final	

			
			
			print "C2 Alpha = ",math.degrees(Alpha)
			print "C2 Lr = ",Lr
			print "C2 L_ext = ",L_ext
			print "C2 Peso1 = ",Peso1
			print "C2 Peso2 = ",Peso2
			print "C2 Fuerza Resultante = ",self.FR.data		

			print "C2 FSinicial = ",self.FSI.data	
			
			if self.FSI.data > 1:			
				return_value = 1
			else: 
				return_value = 0
			
		
		elif self.TipoC.data == 'C3':
				
			Peso = self.h1.data * self.d.data * self.L.data * self.Dens.data
			self.FR.data = 1.25 * Peso 
			self.Superficie.data = self.L.data * self.h1.data

		
			# Debug - Comentar en Version final	

			print "C3 Peso = ",Peso
			print "C3 Fuerza Resultante = ",self.FR.data
			# Este tipo de cunha siempre es inestable se vuelve cero
			
			return_value = 0
			
					
		
 		elif self.TipoC.data == 'C4':
		
			DistAux = self.d.data + self.h1.data/math.tan(math.radians(self.b.data))
			Alpha = math.atan2(self.h1.data, DistAux)
			# Alpha esta en radianes
			Lr = self.h1.data/math.sin(Alpha)*self.L.data/2
			L_ext = self.h1.data/math.sin(math.radians(self.b.data))*self.L.data/2
			Peso = self.h1.data * self.d.data * self.Dens.data * self.L.data/3
		
			# 1,25*(PESO*SIN(ALPHA)-(PESO*COS(ALPHA)-PESO/9,81*ACSIS*SIN(ALPHA))*TAN(RADIANS(ROZ))+PESO/9,81*ACSIS*COS(ALPHA))
		
			self.FR.data = 1.25 * (Peso * math.sin(Alpha) - (Peso * math.cos(Alpha)-Peso/9.81*self.AcSis.data*math.sin(Alpha)) * math.tan(math.radians(self.Roz.data)))
			#+ Peso/9.81* self.AcSis.data *math.cos(Alpha))
			self.FSI.data = (self.Coh.data*1*Lr+(Peso*math.cos(Alpha) - Peso/9.81*self.AcSis.data*math.sin(Alpha))*math.tan(math.radians(self.Roz.data)))/(Peso*math.sin(Alpha) + Peso/9.81*self.AcSis.data * math.cos(Alpha))
			
			self.Superficie.data = L_ext

			# Debug - Comentar en Version final	
		
			print "C4 Alpha = ",math.degrees(Alpha)
			print "C4 Lr = ",Lr
			print "C4 L_ext = ",L_ext
			print "C4 Peso = ",Peso
			print "C4 Fuerza Resultante = ",self.FR.data		
			print "C4 FSinicial = ",self.FSI.data		
			
			if self.FSI.data > 1:			
				return_value = 1
			else: 
				return_value = 0

		
		else:
			print "No encuentro tipo de cunha"
			
			

		return (return_value)


# El calculo del coeficiente de seguridad lo hacemos segun el tipp de proteccion

# Valores de la malla de triple torsion Proactive (MTT)
	def CoefSegProActive (self):
	
		# Verificar que se ha realizado el calculo de estabilidad, 
		# ??????????????? TO DO

		# La resistencia minorada depende del tipo de cable, es un valor de tablas que se divide por 1,67
		# R1U =  RD / 1,67 RD se obtiene segun el tipo de malla
	
		
		if self.TipoMalla.data == '6x8-14':
			R1uMTT = 55/1.67
		elif self.TipoMalla.data == '8x10-15':
			R1uMTT = 48/1.67	
		elif self.TipoMalla.data == '8x10-16':
			R1uMTT = 64/1.67	
		elif self.TipoMalla.data == '8x10-17':
			R1uMTT = 78/1.67	
		else:
			R1uMTT = 0
		
		self.R1.data = R1uMTT
	
		# maxima solicitacion

		# Para calcular la resistencia a traccion de los anclajes se usa la formula:
		# PNd= Fr(1/Sh)*1.5 
		
		Sh = self.L.data / self.DistCor.data		
		self.PNd.data = self.FR.data*1.5/Sh
		
		# Tension admisible del acero
		# a fuerza admisible en el acero, P1lim, es la menor de las siguientes condiciones, 
		# referentes al limite elastico y de rotura del acero
		
		fpk = 550
		fyk = 500
		
		SeccionAcero = math.pi * float(self.DiamAcero.data) * float(self.DiamAcero.data) / 4 
		print "SeccionAcero:", SeccionAcero
		self.P1.data = min (fpk/1.3*SeccionAcero, fyk/1.15*SeccionAcero) /1000
		
		# Arrancamiento P3lim
		
		# La maxima solicitacion que puede que puede aguantar un bulon sin que se produzca 
		# fallo por arrancamiento del bulbo viene determinada por los siguientes calculos 	
		# La adherencia admisible se obtiene minorando la adherencia limite, 
		# alim, con el coeficiente para anclajes permanentes:		
		Aadm = self.Adh.data / 1.65
		
		# En este caso:		
		LongBulboBulon = float(self.LongBulon.data)
		
		self.P3.data = Aadm * math.pi * LongBulboBulon * float(self.DiamPerf.data)
				
		# Deslizamiento entre el acero y la lechada
		# Se calcula primero la adherencia limite
		
		#Tau = 6.9 * (math.pow((self.fck.data/22.5),(2/3)))
		power = 0.6666666666667
		Tau = 6.9 * math.pow(self.fck.data/22.5,power)
		
		print "Tau",  Tau

		
		# La carga limite del bulon por deslizamiento es
		
		self.P2.data =  Tau * LongBulboBulon * math.pi * float(self.DiamAcero.data) /1.2
		
		# Resistencia a cortante de los anclajes
		

		self.R2.data = ((SeccionAcero * fyk /1.15) / math.sqrt(3.0)) / 1000 
		
		# Valores finales
		
		self.FR1.data = R1uMTT / self.FR.data
		
		print "R1MTT", R1uMTT
		
		
		
		self.FR2.data = self.R2.data / self.PNd.data
		self.FP1.data = self.P1.data / self.PNd.data
		self.FP2.data = self.P2.data / self.PNd.data
		self.FP3.data = self.P3.data / self.PNd.data
		self.FSfinal.data = min(self.FR1.data,self.FR2.data,self.FP1.data,self.FP2.data,self.FP3.data)
		
		# Cumplimientos
		if self.P1.data >= self.PNd.data:
			self.P1Cumple.data = True
		else:	
			self.P1Cumple.data = False
			
		if self.P2.data >= self.PNd.data:
			self.P2Cumple.data = True
		else:	
			self.P3Cumple.data = False
			
		if self.P3.data >= self.PNd.data:
			self.P3Cumple.data = True
		else:	
			self.P3Cumple.data = False
			
		if self.R1.data >= self.FR.data:
			self.R1Cumple.data = True
		else:	
			self.R1Cumple.data = False
			
		if self.R2.data >= self.FR.data:
			self.R2Cumple.data = True
		else:	
			self.R2Cumple.data = False
			
		if self.FSfinal.data >= 1:
			self.FSfinalCumple.data = True
		else:
			self.FSfinalCumple.data = False
			

					
		''''
		Imprimir valores para pruebas, comentar en version final
		'''
			
		
		print "PNd", self.PNd.data
		print "P1", self.P1.data
		print "P2", self.P2.data
		print "P3", self.P3.data
		if 	self.P3Cumple.data: 
			print "Cumple"
		else:
			print "No Cumple"
		

		print "R2(Vrd)", self.R2.data
		print "_________________________"
		
		print "FR1", self.FR1.data
		print "FR2", self.FR2.data
		print "FP1", self.FP1.data
		print "FP2", self.FP2.data
		print "FP3", self.FP3.data
		print "FSfinal", self.FSfinal.data
		
		return(1) 
		
	def CoefSegProActiveST (self):	
			
		# Verificar que se ha realizado el calculo de estabilidad, 
		# ??????????????? TO DO

		# La resistencia minorada depende del tipo de cable, es un valor de tablas que se divide por 1,67
		# R1U =  RD / 1,67 RD se obtiene segun el tipo de malla
	
		if self.TipoMalla.data == '6x8-14':
			R1uMAR = 22/1.67
		elif self.TipoMalla.data == '8x10-15':
			R1uMAR = 19.2/1.67	
		elif self.TipoMalla.data == '8x10-16':
			R1uMAR = 25.6/1.67	
		elif self.TipoMalla.data == '8x10-17':
			R1uMAR = 31.2/1.67	
		else:
			R1uMAR = 0
		
		# Valores de resistencia del cable
		
		if self.TipoCableRefuerzo.data == '8':
			RCable = 40.3
		elif self.TipoCableRefuerzo.data == '10':
			RCable = 63
		elif self.TipoCableRefuerzo.data == '12':
			RCable = 90.7
		elif self.TipoCableRefuerzo.data == '14':
			RCable = 124
		elif self.TipoCableRefuerzo.data == '16':
			RCable = 161
		elif self.TipoCableRefuerzo.data == '18':
			RCable = 204
		elif self.TipoCableRefuerzo.data == '20':
			RCable = 252
		elif self.TipoCableRefuerzo.data == '22':
			RCable = 305
		elif self.TipoCableRefuerzo.data == '24':
			RCable = 363
		elif self.TipoCableRefuerzo.data == '26':
			RCable = 426	
		
		NumCablesCuna = 2 * self.Superficie.data/(self.SH_B.data * self.SV_B.data)
		self.R2.data = NumCablesCuna * RCable /1.15
		
			
		# Carga maxima de la MTT 
	
		if ((self.TipoC.data == 'C1') or (self.TipoC.data == 'C2')):
			self.R1.data = R1uMAR * self.Superficie.data
		elif ((self.TipoC.data == 'C3') or (self.TipoC.data == 'C4')):
			self.R1.data = R1uMAR * self.SH_B.data * self.SV_B.data

		self.R1R2.data = self.R1.data + self.R2.data 
		
		print "r1r2 ", self.R1R2.data
	


		# Para calcular la carga nominal por cada bulon
		# PNd= Fr(1/(Sh*(h/Sv+1))*1.5 
		
		# Esto hay que calcularlo en cada caso:
		
		if self.TipoC.data == 'C1':
			NumBulCuna = (self.L.data / self.SH_B.data)*(self.h1.data/self.SV_B.data + 1)
		elif self.TipoC.data == 'C2':
			NumBulCuna = (self.L.data / self.SH_B.data)*((self.h1.data + self.h2.data)/self.SV_B.data + 1)
		elif self.TipoC.data == 'C3':
			NumBulCuna = (self.L.data / self.SH_B.data + 1 )*(self.h1.data/self.SV_B.data + 1)
		elif self.TipoC.data == 'C4':
			NumBulCuna = (self.L.data / self.SH_B.data + 1 )*(self.h1.data/self.SV_B.data + 1)
		
		self.PNd.data = self.FR.data*1.5/NumBulCuna
		
		# Tension admisible del acero
		# a fuerza admisible en el acero, P1lim, es la menor de las siguientes condiciones, 
		# referentes al limite elastico y de rotura del acero
		
		fpk = 550
		fyk = 500
		
		SeccionAcero = math.pi * float(self.DiamAcero.data) * float(self.DiamAcero.data) / 4 
		
		self.P1.data = min (fpk/1.3*SeccionAcero, fyk/1.15*SeccionAcero) /1000
		
		# Arrancamiento P3lim
		
		# La maxima solicitacion que puede que puede aguantar un bulon sin que se produzca 
		# fallo por arrancamiento del bulbo viene determinada por los siguientes calculos 	
		# La adherencia admisible se obtiene minorando la adherencia limite, 
		# alim, con el coeficiente para anclajes permanentes:	
		
		Aadm = self.Adh.data / 1.65
		
		# En este caso:		
		LongBulboBulon = float(self.LongBulon.data) - self.d.data
		
		self.P3.data = Aadm * math.pi * LongBulboBulon * float(self.DiamPerf.data)
		
		# Deslizamiento entre el acero y la lechada
		# Se calcula primero la adherencia limite
		
		#Tau = 6.9 * (math.pow((self.fck.data/22.5),(2/3)))
		power = 0.6666666666667
		Tau = 6.9 * math.pow(self.fck.data/22.5,power)
		
		print "Tau",  Tau

		
		# La carga limite del bulon por deslizamiento es
		
		self.P2.data =  Tau * LongBulboBulon * math.pi * float(self.DiamAcero.data) /1.2
		
		
		# Valores finales
		
		self.FR1.data = (self.R1.data + self.R2.data) / self.FR.data	
		self.FR2.data = self.R2.data / self.PNd.data
		self.FP1.data = self.P1.data / self.PNd.data
		self.FP2.data = self.P2.data / self.PNd.data
		self.FP3.data = self.P3.data / self.PNd.data
		self.FSfinal.data = min(self.FR1.data,self.FP1.data,self.FP2.data,self.FP3.data)
		
		# Cumplimientos
		
			
		if self.P1.data >= self.PNd.data:
			self.P1Cumple.data = True
		else:	
			self.P1Cumple.data = False
			
		if self.P2.data >= self.PNd.data:
			self.P2Cumple.data = True
		else:	
			self.P3Cumple.data = False
			
		if self.P3.data >= self.PNd.data:
			self.P3Cumple.data = True
		else:	
			self.P3Cumple.data = False
			
		if self.R1R2.data >= self.FR.data:
			self.R1R2Cumple.data = True
		else:	
			self.R1R2Cumple.data = False
			
		if self.R2.data >= self.FR.data:
			self.R2Cumple.data = True
		else:	
			self.R2Cumple.data = False
		
		if self.FSfinal.data >= 1:
			self.FSfinalCumple.data = True
		else:
			self.FSfinalCumple.data = False
			
		
		''''
		Imprimir valores para pruebas, comentar en version final
		'''
			
		
		print "PNd", self.PNd.data
		print "P1", self.P1.data
		print "R1", self.R1.data
		print "R2", self.R2.data
		print "P2", self.P2.data
		print "P3", self.P3.data
		print "_________________________"
		
		print "FR1", self.FR1.data
		print "FR2 No relevante para este tipo de proteccion"
		print "FP1", self.FP1.data
		print "FP2", self.FP2.data
		print "FP3", self.FP3.data
		print "FSfinal", self.FSfinal.data		
		return(1) 

	# Esta funcion es la misma para NetProtect y NetProtectSR
	def CoefSegNetProtect (self):
	
			
		# Verificar que se ha realizado el calculo de estabilidad, 
		# ??????????????? TO DO

		# La resistencia minorada depende del tipo de cable, es un valor de tablas que se divide por 1,67
		# R1U =  RD / 1,67 RD se obtiene segun el tipo de malla
		
		if self.TipoProt.data ==  'NetProtect':
			print'NetProtect'
			if self.TipoRedNP.data == 'Paneles 200':
				RMin = 62/1.67
			elif self.TipoRedNP.data == 'Paneles 250':
				RMin = 51/1.67
			elif self.TipoRedNP.data == 'Paneles 300':
				RMin = 45/1.67
			elif self.TipoRedNP.data == 'Paneles 400':
				RMin = 34/1.67
			else:
				flash ('Error en definicion de Netprotect')
		else:		
			if self.TipoRedNPST.data == 'LitoStop 2/350':
				RMin = 100/1.67
			elif self.TipoRedNPST.data == 'LitoStop 2/300':
				RMin = 106/1.67
			elif self.TipoRedNPST.data == 'LitoStop 2/250':
				RMin = 125//1.67
			elif self.TipoRedNPST.data == 'LitoStop 3/350':
				RMin = 150/1.67
			elif self.TipoRedNPST.data == 'LitoStop 3/300':
				RMin = 215/1.67
			else:
				flash ('Error en definicion de Netprotect ST')
		# Valores de resistencia del cable
		
		if self.TipoCableRefuerzo.data == '8':
			RCable = 40.3
		elif self.TipoCableRefuerzo.data == '10':
			RCable = 63
		elif self.TipoCableRefuerzo.data == '12':
			RCable = 90.7
		elif self.TipoCableRefuerzo.data == '14':
			RCable = 124
		elif self.TipoCableRefuerzo.data == '16':
			RCable = 161
		elif self.TipoCableRefuerzo.data == '18':
			RCable = 204
		elif self.TipoCableRefuerzo.data == '20':
			RCable = 252
		elif self.TipoCableRefuerzo.data == '22':
			RCable = 305
		elif self.TipoCableRefuerzo.data == '24':
			RCable = 363
		elif self.TipoCableRefuerzo.data == '26':
			RCable = 426
		
		if self.TipoC.data == 'C1':
			NumCablesCuna = self.L.data/self.SH_B.data + self.h1.data/self.SV_B.data + 1
		elif self.TipoC.data == 'C2':
			NumCablesCuna = self.L.data/self.SH_B.data + (self.h1.data+self.h2.data)/self.SV_B.data + 1
		elif self.TipoC.data == 'C3':
			NumCablesCuna = self.L.data/self.SH_B.data + 1 + self.h1.data/self.SV_B.data + 1
		if self.TipoC.data == 'C4':
			NumCablesCuna = self.L.data/self.SH_B.data + 1 + self.h1.data/self.SV_B.data + 1
	
		self.R2.data = NumCablesCuna * RCable/1.15
		
		# Carga maxima de la MTT 
		
		print "RMin", RMin
		print "sup" , self.Superficie.data
		
		if ((self.TipoC.data == 'C1') or (self.TipoC.data == 'C2')):
			self.R1.data = RMin * self.Superficie.data
		elif ((self.TipoC.data == 'C3') or (self.TipoC.data == 'C4')):
			self.R1.data = RMin * self.SH_B.data * self.SV_B.data

		# Para calcular la carga nominal por cada bulon
		# PNd= Fr(1/(Sh*(h/Sv+1))*1.5 
		
		# Esto hay que calcularlo en cada caso:
		
		if self.TipoC.data == 'C1':
			NumBulCuna = (self.L.data / self.SH_B.data)*(self.h1.data/self.SV_B.data + 1)
		elif self.TipoC.data == 'C2':
			NumBulCuna = (self.L.data / self.SH_B.data)*((self.h1.data + self.h2.data)/self.SV_B.data + 1)
		elif self.TipoC.data == 'C3':
			NumBulCuna = (self.L.data / self.SH_B.data + 1 )*(self.h1.data/self.SV_B.data + 1)
		elif self.TipoC.data == 'C4':
			NumBulCuna = (self.L.data / self.SH_B.data + 1 )*(self.h1.data/self.SV_B.data + 1)
		
		self.PNd.data = self.FR.data*1.5/NumBulCuna
		print "PNd-----------", self.PNd.data
	
		# Tension admisible del acero
		# a fuerza admisible en el acero, P1lim, es la menor de las siguientes condiciones, 
		# referentes al limite elastico y de rotura del acero
		
		fpk = 550
		fyk = 500
		
		SeccionAcero = math.pi * float(self.DiamAcero.data) * float(self.DiamAcero.data) / 4 
		print "Seccion Acero", SeccionAcero
		
		self.P1.data = min (fpk/1.3*SeccionAcero, fyk/1.15*SeccionAcero) /1000
		
		# Arrancamiento P3lim
		
		# La maxima solicitacion que puede que puede aguantar un bulon sin que se produzca 
		# fallo por arrancamiento del bulbo viene determinada por los siguientes calculos 	
		# La adherencia admisible se obtiene minorando la adherencia limite, 
		# alim, con el coeficiente para anclajes permanentes:	
		
		Aadm = self.Adh.data / 1.65
		
		# En este caso:		
		LongBulboBulon = float(self.LongBulon.data) - self.d.data
		
		self.P3.data = Aadm * math.pi * LongBulboBulon * float(self.DiamPerf.data)
		
		# Deslizamiento entre el acero y la lechada
		# Se calcula primero la adherencia limite
		
		#Tau = 6.9 * (math.pow((self.fck.data/22.5),(2/3)))
		power = 0.6666666666667
		Tau = 6.9 * math.pow(self.fck.data/22.5,power)
		
		print "Tau",  Tau

		
		# La carga limite del bulon por deslizamiento es
		
		self.P2.data =  Tau * LongBulboBulon * math.pi * float(self.DiamAcero.data) /1.2
		
		
		# Valores finales
		
		self.FR1.data = self.R1.data / self.FR.data	
		self.FR2.data = self.R2.data / self.FR.data
		self.FP1.data = self.P1.data / self.PNd.data
		self.FP2.data = self.P2.data / self.PNd.data
		self.FP3.data = self.P3.data / self.PNd.data
		self.FSfinal.data = min(self.FR1.data,self.FR2.data,self.FP1.data,self.FP2.data,self.FP3.data)
		
		'''
		Imprimir valores para pruebas, comentar en version final
		'''
		# Cumplimientos
		if self.P1.data >= self.PNd.data:
			self.P1Cumple.data = True
		else:	
			self.P1Cumple.data = False
			
		if self.P2.data >= self.PNd.data:
			self.P2Cumple.data = True
		else:	
			self.P3Cumple.data = False
			
		if self.P3.data >= self.PNd.data:
			self.P3Cumple.data = True
		else:	
			self.P3Cumple.data = False
			
		if self.R1.data >= self.FR.data:
			self.R1Cumple.data = True
		else:	
			self.R1Cumple.data = False
			
		if self.R2.data >= self.FR.data:
			self.R2Cumple.data = True
		else:	
			self.R2Cumple.data = False
		
		if self.FSfinal.data >= 1:
			self.FSfinalCumple.data = True
		else:
			self.FSfinalCumple.data = False
			

		
		print "PNd", self.PNd.data
		print "P1", self.P1.data
		print "R1", self.R1.data
		print "R2", self.R2.data
		print "P2", self.P2.data
		print "P3", self.P3.data
		print "_________________________"
		
		print "FR1", self.FR1.data
		print "FR2", self.FR2.data
		print "FP1", self.FP1.data
		print "FP2", self.FP2.data
		print "FP3", self.FP3.data
		print "FSfinal", self.FSfinal.data		
		return(1) 

# Una funcion para inicilizar todos los valores al default
	def initialize (self):
	
		self.TipoProt.data = 'Proactive'

		self.h1.data  = 0
		self.h2.data  = 0.0
		self.d.data  = 0 
		self.b.data  = 0 
		self.L.data  = 0 
		self.Coh.data  = 0 
		self.Roz.data  = 0 
		self.Dens.data  = 0 
		self.AcSis.data  = 0 
		self.DistCor.data  = 0 
		self.TipoMalla.data  = '6x8-14'
		self.TipoCableRefuerzo.data  = 8
		self.TipoRedNP.data  = 'Paneles 200' 
		self.TipoRedNPST.data  = 'LitoStop 2/350' 
		self.SH_B.data  = 0
		self.SV_B.data  = 0 
		self.LongBulon.data  = 0 
		self.DiamAcero.data  = 16.0 
		self.Adh.data  = 0 
		self.fck.data  = 0 
		self.DiamPerf.data  = 46
		
		
		
	# inicializamos los valores de los resultados antes de hacer calculos
	 
	def initialize_results (self):
		
		self.Superficie = 0
		self.FSI = 0
		self.FR = 0
		self.R1 = 0
		self.R1cumple = 0
		self.R1 = 0
		self.R1cumple = 0
		self.R2 = 0
		self.R2cumple = 0
		self.R1R2 = 0
		self.R1R2cumple = 0
		self.PNd = 0
		self.P1 = 0
		self.P1cumple = 0
		self.P2 = 0
		self.P2cumple = 0
		self.P3 = 0
		self.P3cumple = 0
		self.FR1 = 0
		self.FR2 = 0
		self.FP1 = 0
		self.FP2 = 0
		self.FP3 = 0    
		self.FSfinal = 0
		self.FSfinalcumple = 0
		
		return (1) 	

	

# Datos de Calculo de proteccion que se almacenan en BD
#------------------------------------------------------ 

class CalcProt(db.Model):
	__tablename__='calculations'
	
	id = db.Column(db.Integer, primary_key = True)
		

	timestamp = db.Column(db.DateTime)	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user_email = db.Column(db.Unicode(255), nullable=False, server_default=u'')

# Datos de la cunha
	
	TipoC = db.Column(db.Unicode(1))
	
#Se usa 1=C1, 2=C2, 3=C3, 4=C4
	
	h1 = db.Column(db.Float)
	h2 = db.Column(db.Float)
	d = db.Column(db.Float)
	b = db.Column(db.Float)
	L = db.Column(db.Float)
	Coh = db.Column(db.Float)
	Roz = db.Column(db.Float)
	Dens = db.Column(db.Float)
	AcSis = db.Column(db.Float)

# Datos de la proteccion
	TipoProt=db.Column(db.Unicode(1))	
		
# Datos de Anclajes
# -----------------
# Coronacion (m):

	DistCor = db.Column(db.Float)

# Datos de los bulones
# --------------------
# Separacion horizontal (m):
# Separacion Vertical(m):

	SH_B = db.Column(db.Float) 
	SV_B = db.Column(db.Float) 
	
# Datos comunes
# -------------
# Longitud (m);
# D acero (mm):
# Adherencia (Mpa):
# fck lechada (Mpa):
# D perforacion (mm):

	LongBulon = db.Column(db.Float) 
	DiamAcero = db.Column(db.Float)
	Adh = db.Column(db.Float)
	fck = db.Column(db.Float)
	DiamPerf = db.Column(db.Float)
	
# Resultados de los calculos
# --------------------------
	# La superficie se calcula para cada tipo de cunha
	Superficie = db.Column(db.Float)
	
	# Coeficiente de seguridad inicial FSI 
	FSI = db.Column(db.Float)
	
	# Fuerza Resultante FR
	FR = db.Column(db.Float)
	R1 = db.Column(db.Float)
	R1Cumple = db.Column(db.Boolean)
	R2 = db.Column(db.Float)	
	R2Cumple = db.Column(db.Boolean)
	R1R2 = db.Column(db.Float)	
	R1R2Cumple = db.Column(db.Boolean)

	PNd = db.Column(db.Float)

	P1 = db.Column(db.Float)	
	P1Cumple = db.Column(db.Boolean)
	P2 = db.Column(db.Float)	
	P2Cumple = db.Column(db.Boolean)
	P3 = db.Column(db.Float)	
	P3Cumple = db.Column(db.Boolean)

	FR1 = db.Column(db.Float)	
	FR2 = db.Column(db.Float)	

	FP1 = db.Column(db.Float)	
	FP2 = db.Column(db.Float)	
	FP3 = db.Column(db.Float)	
	FSfinal = db.Column(db.Float)	
	FSfinalCumple = db.Column(db.Boolean)
	
