# -*- coding: utf-8 -*-
'''
La intencion de este script es enviar correos electronicos a las personas interesadas en los torneos organizados por la FVT

TODO:
  1) Enviar a los destinatarios segun el tipo de torneo. Algunos solo querran Pelotas de Colores, otros solo en Miranda


URL to parse: http://miranda.fvtenis.com.ve/app/bsindexLoadCalendario.php


Julio - Agosto 2018
Added Leyenda April 2019

rdl7600@gmail.com Rafael de Lima ATC
fnunez@termofluidos.com.ve Frank Nunez
Nanynacad@yahoo.com  Adriana Nacad (solicitado por Rafael de Lima)
idoia582@gmail.com Idoia Sagarzazu
Ramnysg19@hotmail.com
Ramnysgarcia19@gmail.com
tenisatem@gmail.com  Tenis ATEM Cathy
Jose Luis Lopez <lopezjoseluis74@gmail.com>  Profe tenis
antonioyamin@gmail.com  Papa de Antoin Yamin
wblascof00@hotmail.com  William Blasco CRC
inv.adleca@gmail.com Luis Perez CRC
Lauramaurizio@gmail.com Laura Maurizio CIV
coelho.egidio@gmail.com Solicitado por Luis Perez. Sep 2019
blaher.sosa@gmail.com  William Blasco Oct 2019
Vcabrera03@gmail.com Veronica Cabrera
pcozzolino@euroquim.com

'''

import requests #to get URL from Internet
from bs4 import BeautifulSoup #for html parsing
import datetime #For days left calculation, printing today's date & time
import sys #just for getting script name

## // Define global variables // ##
Entidades_a_Reportar=['CAR', 'ZUL', 'MIR', 'ARA','LAR','VAR','FVT']
URL="http://miranda.fvtenis.com.ve/app/bsindexLoadCalendario.php"
WarningDays=35 #How much time in advance between the running date of the script and next tournament
page=requests.get(URL)

recipients = '' #This string contains the recipients of the email
EMAILSERVER="tusmtp.server.com"
EMAILUSERNAME="tuusuario"
EMAILPASS="tuclave"

#We have up to 4 lists, you pass the number as an argument to the script
list1 = 'user@ff.com, user2@fdsf.com' #separate as many addresses as you wish by comma

list2 = ''

list4 = ''

Tournaments=[] #we fill this list with tournaments info. Every item in the list = one tournament

def CheckParameters():
  global recipients, sys, list1,list2, list3, list4
  #First, lets define to whom we are going to send the tournament info to
  if len(sys.argv) == 2: #Lets check number of arguments
    if sys.argv[1] == '1':
      recipients = list1
    elif sys.argv[1] == '2':
      recipients = list2
    elif sys.argv[1] == '3':
      recipients = list3
    elif sys.argv[1] == '4':
      recipients = list4
    else:
      print ('Script only accepts values 1, 2, 3 or 4 as parameter')
      exit()
  else:
    print ('This scripts accepts exactly one parameter')
    exit()

def GetWebPage(URL):
  #We retrieve the URL and based on the return code we decide to continue or not
  page=requests.get(URL)
  if int(page.status_code) == 200:
    ParseContent(str(page.content))
    pass
  else:
    now = datetime.datetime.now()
    print (now, ' something wrong while retrieving webpage') #let's fully stop the execution. Does not worth to continue
    exit()


def SendEmail(MSG, Entidad, Grado):
    global recipients
    from smtplib import SMTP_SSL as SMTP
    import logging
    import logging.handlers
    import sys, datetime
    from email.mime.text import MIMEText

    #Let's add some leyend and the end of the email
    MSG.append('')
    MSG.append('Informacion tomada de:  '+str(URL))
    MSG.append('''Leyenda: 
    G1 Suramericanos 
    G2 Nacionales 
    G3 Regionales 
    G4 Estatales
    ''')
    MSG.append('IMPORTANTE: solo se reportan los torneos en: '+str(Entidades_a_Reportar))
    MSG.append('Este correo se envia una vez a la semana SOLO cuando haya 1 o mas torneos en los proximos '+str(WarningDays)+' dias ')
    MSG.append('Email enviado por: ' + sys.argv[0])

    text = '\r\n'.join(MSG)
    #text = MSG
    if len(text) < 10:
       exit()   #There is a problem
    msg = MIMEText(text, 'plain')
    msg.set_charset('utf8')
    msg['Content-Type']='text/html; charset=utf-8'
    msg['Content-Disposition']='inline'
    msg['Content-Transfer-Encoding']='8bit'
    msg['Date'] = datetime.datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z')
    msg['Subject'] = "Torneos en los proximos "+ str(WarningDays) + " dias - Info automatizada"
    me = 'tu@server.com'
    msg['To'] = recipients  #Note recipients is a global vars defined at the top

    try:
        conn = SMTP(EMAILSERVER)
        conn.set_debuglevel(True)
        conn.login(EMAILUSERNAME, EMAILPASS)
        try:
            #conn.sendmail(me,recipients.split(',') , msg.as_string())
            conn.sendmail(me,recipients.split(',') , str(msg).encode("utf8"))
        finally:
            conn.close()
    except Exception as exc:
        logger.error("ERROR!!!")
        logger.critical(exc)

def ParseContent(pagecontent):
    #Find headers:
    soup = BeautifulSoup(pagecontent, 'html.parser')

    table_head = soup.find('thead')

    for i in table_head.findAll('th'):
       print(i.get_text())

    tablecontent1 = soup.find_all('tr', attrs={'class':' '}) #this way we find every tournament listed
    tablecontent2 = soup.find_all('tr', attrs={'class':'success'}) #this way we find every tournament listed
    tablecontent = tablecontent1 + tablecontent2
    i = 0 #Tournament counter

    for row in tablecontent: #every row is one tournament
         #print ("\n\n Torneo: ", row)
         #continue
         ESTATUS=row.find('td', attrs={'title':'Estatus'}).get_text()
         FechaInicio=row.find('td', attrs={'title':'Fecha Inicio'}).get_text()
         d1=str(FechaInicio)
         ano=d1.split('-')[0]
         mes=d1.split('-')[1]
         dia=d1.split('-')[2]
         dia=dia.split(' ')[0]
         today = datetime.date.today()
         TournamentDate=datetime.date(int(ano), int(mes), int(dia))
         DeltaDays=TournamentDate - today #dates between today and tournament's date
         #print (DeltaDays.days)
         DeltaDays = str(DeltaDays.days) #we need it as string to manage concatenation below
         Grado=row.find('td', attrs={'title':'Grado'}).get_text()
         Categoria=row.find('td', attrs={'title':'Categoria'}).get_text()
         Entidad=row.find('td', attrs={'title':'Entidad'}).get_text()
         if Entidad not in Entidades_a_Reportar: #Not adding some entidades nor states
          continue
         #NombreTorneo=row.find('td', attrs={'title':'Nombre Torneo'}).get_text()
         MSG= 'Torneo: ' + ' Secuencia ' + Grado + ' Categoria '+ Categoria + ' faltan: ' + DeltaDays + ' dias ' + 'con fecha de Inicio ' + d1.split(' ')[0] + ' en ' + Entidad


         try:  #we use a try because sometimes the html is not perfect and math will raise an error
           if (int(DeltaDays) < WarningDays) and (int(DeltaDays) > 0):
              #print (today,TournamentDate,DeltaDays)
              i = i + 1  #This is the tournamente counter that we increment before printing the tournament information (makes things more readable)
              Tournaments.append(str(i)+')')
              Tournaments.append(MSG) #Let's create only one list with all tournaments withinn today's date and WarningDays
              Tournaments.append(' ') #Let's create only one list with all tournaments withinn today's date and WarningDays
         except Exception:
            pass

    if len(Tournaments) > 0: #if there is at least one tournament we send the email
          SendEmail(Tournaments, Entidad, Grado)
          #pass
    else:  #this else is basically for the .log file, just to have more info
      now = datetime.datetime.now()
      print (now, ' No tournaments during the next 30 days ') #let's fully stop the execution. Does not worth to continue
      exit()


    exit()

if __name__ == "__main__":
  CheckParameters()
  GetWebPage(URL)
