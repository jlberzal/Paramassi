# Sample platypus document
# From the FAQ at reportlab.org/oss/rl-toolkit/faq/#1.1

from flask import redirect, render_template, flash, render_template_string, Blueprint,g
from flask import request, url_for
from flask import send_file
from flask import send_from_directory

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from datetime import datetime

from app.core.models import CalcForm
from xhtml2pdf import pisa
import StringIO
import requests


PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

# Programa de generacion de informes
# Cada parte del documento se genera a partir de los datos del form

# Titulo
	
Title = "Hello world"
pageinfo = "platypus example"

def title (form):
	text = "%s_%s_%s" % (form.TipoProt.data,form.TipoC.data,datetime.utcnow())
	return(text)

def indice (Story,form):
	style = styles["Normal"]
	
	Story.append(Paragraph("1) DATOS DE PARTIDA ", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2) ANALISIS DE ESTABILIDAD ", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.1) Modelo de rotura", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.2) Coeficiente de seguridad inicial", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.3) Medidas de estabilizacioon", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.4) Fuerza resultante", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.5) Cable de cosido", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.6) Resistencia de la red", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.7) Bulones", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.7.1 Tensioon admisible del acero", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.7.2 Arrancamiento", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.7.3 Deslizamiento entre el acero y la lechada", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("2.8) Coeficiente de seguridad final", style))
	Story.append(Spacer(1,0.2*inch))
	Story.append(Paragraph("3) CONCLUSIooN", style))
	Story.append(Spacer(1,0.2*inch))
	return (Story)

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica',16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
    canvas.setFont('Helvetica',9)
    canvas.drawString(inch, 0.75 * inch,"First Page / %s" % pageinfo)
    canvas.restoreState()
    
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch,"Page %d %s" % (doc.page, pageinfo))
    canvas.restoreState()
    
def generate_pdf(form):
	
	global Title
	
	file_name ="test.pdf" 
	#% (form.id.data)
	file_name1 ="app/reports/"+ file_name

	
	doc = SimpleDocTemplate(file_name1)
	Story = [Spacer(1,2*inch)]
	style = styles["Normal"]
	Title = title(form)
	print Title
	
	# empezamos a generar el documento
	indice (Story,form)
	datos_de_partida(Story, form)
	
	doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
	return (1)
	
	#return redirect(url_for(file_name), code=301)

 