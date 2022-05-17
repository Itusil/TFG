from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS, cross_origin

import concurrent.futures

from bs4 import BeautifulSoup as soup
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/tablas.js')
def tablas():
    #return send_file('../ac_check/JS/tablas.js',mimetype='text/js')
    return send_from_directory('../ac_check/JS/','tablas.js', mimetype='text/javascript')

def escribir_texto(texto, html_):
    txt_nuevo=""            
    pos = texto.find("<")
    #pos = texto.find("&lt;")
    entro = False
    while pos != -1:
        entro = True
        txt_nuevo += texto[:pos]+"<code>&lt;"
        texto = texto[pos+1:]
        pos = texto.find(">")
        #pos = texto.find("&gt;")
        txt_nuevo += texto[:pos]+"&gt;</code>"
        texto = texto[pos+1:]
        pos = texto.find("<")
        #pos = texto.find("&lt;")

    if entro:
        txt_nuevo += texto
        html_ += "<td>"+txt_nuevo+"</td>"
    else:
        html_ += "<td>"+texto+"</td>"
    return html_

def escribir_estandares(divc):
    estandars = divc.find_all('li')
    estandares = ""
    coma = False
    for es in estandars:
        if not coma:
            coma=True 
            estandares += es.text[17:24]
        else:
            estandares +=", "+es.text[17:24]

    return estandares

def get_content_of_link(url,browser,tipo):
    array_respuesta= []
    #Ojo no se tiene en cuenta de que pueda fallar (no hay try except finally) porque no se puede hacer el browser quit
    if tipo =='AM' and url.startswith('https://accessmonitor.acessibilidade.gov.pt'):
        #Uno de los links va a w3c
        browser.get(url)
        timeout_in_seconds = 50
        WebDriverWait(browser, timeout_in_seconds).until(ec.presence_of_element_located((By.ID, 'list_tab')))
        #Lo de abajo hace que se imprima la pagina
        html = browser.page_source
        res = soup(html, features="html.parser")

        div = res.find('div',{'id':'list_tab'})

        ol = div.ol

        lis = ol.find_all('li')

        for li in lis:
            table = li.table 
            trs = table.find_all('tr')
            td = trs[1].td
            codigo = td.code.text
            array_respuesta.append(codigo)
    else:
        array_respuesta.append(url)

    return array_respuesta

@app.route('/getJSON/', methods=['POST'])
@cross_origin()
def create_JSON():
    received_json = request.get_json()
    url = received_json['url']
    print("U: "+url)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
      f1 = ex.submit(JSON_access_monitor, url)
      f2 = ex.submit(achecker, url)
      # Wait for results
      informe = f1.result()
      informe_2 = f2.result()

    informe_final = merge_reports(informe, informe_2)
    informe_final = fomat_informe(url,informe_final)
    return informe_final


def JSON_access_monitor(url):
    #Vamos a sacar la web de access monitor
    url = url.replace("/",'%2f')

    url = "https://accessmonitor.acessibilidade.gov.pt/results/"+url

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    #Importante ponerle el lenguaje predefinido el inglés, sino sale en portugués
    options.add_argument("--lang=en");
    # executable_path param is not needed if you updated PATH
    browser = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')

    informe = {
        'Tester_Name' : 'Access_Monitor'
    }

    try:
        browser.get(url)
        timeout_in_seconds = 50
        WebDriverWait(browser, timeout_in_seconds).until(ec.presence_of_element_located((By.CLASS_NAME, 'evaluation-table')))
        #Lo de abajo hace que se imprima la pagina
        html = browser.page_source
        s = soup(html, features="html.parser")

        #https://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table
        tabla = s.find('table', {'class': 'evaluation-table'})
        cabeza = tabla.find('tbody')

        score = s.find('div',{'class':'reading-block'})
        #El score puede venir bien para el resumen
        informe['RESULTADO']=score.text

        rows = cabeza.find_all('tr')

        informe_casos = {}
        for row in rows:
            cols = row.find_all('td')
            divc = cols[1].find('div',{'class':'collapsible-content'})
            nivel = cols[2].text
            nivel = nivel.replace(' ','')
            if str(nivel) == 'A' or str(nivel) =='AA':
                estandares = get_estandares_array(divc)
                array_prueba = []

                cols = row.find_all('td')
                tipo_texto = cols[0].svg.title.text
                tipo = False
                texto_final = ""
                if tipo_texto == 'monitor_icons_praticas_status_incorrect':
                    tipo = True
                    array_prueba.append("Failed")
                    texto_final += "The next ERROR was found: \n\n"
                elif tipo_texto == 'monitor_icons_praticas_status_review':
                    tipo = True
                    array_prueba.append("Cannot Tell")
                    texto_final += "The next WARNING was found: \n\n"
                elif tipo_texto == 'monitor_icons_praticas_status_correct':
                    array_prueba.append("Passed")
                    texto_final += "The next CORRECTION CHECK was found: \n\n"
                
                #Si es un error o un warning habrá que hacer scraping
                link = ""
                texto_link = ""
                if tipo:
                    link = cols[3].a.get('href')
                    link = 'https://accessmonitor.acessibilidade.gov.pt'+link
                    array_respuesta = get_content_of_link(link,browser,'AM')

                    for i in array_respuesta:
                        i=i.replace('\n','')
                        i=i.replace('\t','')
                        texto_link += i+"\n\n"

                texto_final += divc.p.text

                if tipo:
                    texto_final += "On the code: \n\n"
                    texto_final += texto_link


                #Metemos el texto con los links
                array_prueba.append(texto_final)

                #Una vez el array lleno, llenamos los estandares con los valores.
                codes = nombres_por_codigos()
                for estandar in estandares:
                    estandar = estandar.replace(' ','')
                    if estandar in codes:
                        nombre_wag = codes[estandar]
                        if nombre_wag in informe_casos:

                            resultado_Previo = informe_casos[nombre_wag]['Resultado']
                            texto_Previo = informe_casos[nombre_wag]['Texto']
                            resultado_Actual = array_prueba[0]
                            texto_Actual = array_prueba[1]

                            if resultado_Previo =='Failed'or resultado_Actual == 'Failed':
                                informe_casos[nombre_wag]['Resultado'] = 'Failed'
                            elif resultado_Previo =='Cannot Tell'or resultado_Actual == 'Cannot Tell':
                                informe_casos[nombre_wag]['Resultado'] = 'Cannot Tell'
                            else:
                                informe_casos[nombre_wag]['Resultado'] = 'Passed'
    

                            texto_r = texto_Previo +"---------------------------------------- \n\n "+texto_Actual
                            informe_casos[nombre_wag]['Texto'] = texto_r

                        else:
                            informe_casos[nombre_wag] = {
                                'Resultado': array_prueba[0],
                                'Texto' : array_prueba[1]
                            }
    except TimeoutException:
        print("I give up...")
    finally:
        browser.quit()
        informe['Cases'] = informe_casos
        print("AM hecho")
        return informe


    return informe


def nombres_por_codigos():
    cod = {
    '1.1.1':'WCAG21:non-text-content',
    '1.2.1':'WCAG21:audio-only-and-video-only-prerecorded',
    '1.2.2':'WCAG21:captions-prerecorded',
    '1.2.3':'WCAG21:audio-description-or-media-alternative-prerecorded',
    '1.2.4':'WCAG21:captions-live',
    '1.2.5':'WCAG21:audio-description-prerecorded',
    '1.3.1':'WCAG21:info-and-relationships',
    '1.3.2':'WCAG21:meaningful-sequence',
    '1.3.3':'WCAG21:sensory-characteristics',
    '1.3.4':'WCAG21:orientation',
    '1.3.5':'WCAG21:identify-input-purpose',
    '1.4.1':'WCAG21:use-of-color',
    '1.4.2':'WCAG21:audio-control',
    '1.4.3':'WCAG21:contrast-minimum',
    '1.4.4':'WCAG21:resize-text',
    '1.4.5':'WCAG21:images-of-text',
    '1.4.10':'WCAG21:reflow',
    '1.4.11':'WCAG21:non-text-contrast',
    '1.4.12':'WCAG21:text-spacing',
    '1.4.13':'WCAG21:content-on-hover-or-focus',
    '2.1.1':'WCAG21:keyboard',
    '2.1.2':'WCAG21:no-keyboard-trap',
    '2.1.4':'WCAG21:character-key-shortcuts',
    '2.2.1':'WCAG21:timing-adjustable',
    '2.2.2':'WCAG21:pause-stop-hide',
    '2.3.1':'WCAG21:three-flashes-or-below-threshold',
    '2.4.1':'WCAG21:bypass-blocks',
    '2.4.2':'WCAG21:page-titled',
    '2.4.3':'WCAG21:focus-order',
    '2.4.4':'WCAG21:link-purpose-in-context',
    '2.4.5':'WCAG21:multiple-ways',
    '2.4.6':'WCAG21:headings-and-labels',
    '2.4.7':'WCAG21:focus-visible',
    '2.5.1':'WCAG21:pointer-gestures',
    '2.5.2':'WCAG21:pointer-cancellation',
    '2.5.3':'WCAG21:label-in-name',
    '2.5.4':'WCAG21:motion-actuation',
    '3.1.1':'WCAG21:language-of-page',
    '3.1.2':'WCAG21:language-of-parts',
    '3.2.1':'WCAG21:on-focus',
    '3.2.2':'WCAG21:on-input',
    '3.2.3':'WCAG21:consistent-navigation',
    '3.2.4':'WCAG21:consistent-identification',
    '3.3.1':'WCAG21:error-identification',
    '3.3.2':'WCAG21:labels-or-instructions',
    '3.3.3':'WCAG21:error-suggestion',
    '3.4.3':'WCAG21:error-prevention-legal-financial-data',
    '4.1.1':'WCAG21:parsing',
    '4.1.2':'WCAG21:name-role-value',
    '4.1.3':'WCAG21:status-messages'
    }
    return cod


def get_estandares_array(divc):
    estandars = divc.find_all('li')
    estandares = []
    for es in estandars:
        estandares.append(es.text[17:24])

    return estandares


def achecker(url):
    ac = "https://achecker.achecks.ca/checker/index.php"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    #Importante ponerle el lenguaje predefinido el inglés, sino sale en portugués
    options.add_argument("--lang=en");
    # executable_path param is not needed if you updated PATH
    browser = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')


    try:
        browser.get(ac)
        #timeout_in_seconds = 50
        #WebDriverWait(browser, timeout_in_seconds).until(ec.presence_of_element_located((By.CLASS_NAME, 'evaluation-table')))
        #Lo de abajo hace que se imprima la pagina
        html = browser.page_source
        #s = soup(html, features="html.parser")

        campo_de_texto = browser.find_element(By.ID, "checkuri")
        campo_de_texto.send_keys(url)
        boton_submit = browser.find_element(By.ID, "validate_uri")
        boton_submit.click()
        html = browser.page_source

        informe = get_contenido_achecker(browser)


    except TimeoutException:
        print("I give up...")
    finally:
        browser.quit()
        print("AC hecho")
        return informe

def get_contenido_achecker(browser):
    informe = {
        'Tester_Name' : 'Achecker'
    }

    html_s = browser.page_source
    s = soup(html_s, features="html.parser")

    #Errores conocidos
    div_AC_ERRORS = s.find('div',{'id':'AC_errors'}) 
    h4_AC_ERRORS = div_AC_ERRORS.find_all('h4')
    one_check_AC_ERRORS = div_AC_ERRORS.find_all('div',{'class':'gd_one_check'})

    codes = nombres_por_codigos()
    inf_casos = {}
    for i in range(0,len(h4_AC_ERRORS)):
        text_criteria=h4_AC_ERRORS[i].text[17:]
        pos = text_criteria.find(' ')
        text_criteria = text_criteria[:pos]
        one_check = one_check_AC_ERRORS[i]
        problema = one_check.span.a.text
        solucion = one_check.div.text
        tabla_lineas = one_check.table.tbody
        trs = tabla_lineas.find_all('tr')
        errores_y_lineas = []
        for tr in trs:
            td = tr.td 
            linea_error= td.em
            codigo = td.pre.code
            errores_y_lineas.append({
                'linea':str(linea_error),
                'codigo':str(codigo)
                })
        texto_Actual = 'The next ERROR was found: "'+problema+'". You can solve it with: "'+solucion+'". The error was in the following line(s): \n\n "'
        for er in errores_y_lineas:
            texto_Actual+= 'LINE '+er['linea']+': "'+er['codigo']+'"\n\n'
        if text_criteria in codes:
            nombre_wag = codes[text_criteria]
            if nombre_wag in inf_casos:

                texto_Previo = inf_casos[nombre_wag]['Texto']
                inf_casos[nombre_wag]['Resultado'] = 'Failed'


                texto_r = texto_Previo +"---------------------------------------- \n\n "+texto_Actual
                inf_casos[nombre_wag]['Texto'] = texto_r

            else:
                inf_casos[nombre_wag] = {
                    'Resultado':'Failed',
                    'Texto' : texto_Actual
                }



    #Avisos (likely errors)
    div_AC_likely_problems = s.find('div',{'id':'AC_likely_problems'}) 
    h4_AC_likely_problems = div_AC_likely_problems.find_all('h4')
    one_check_AC_likely_problems = div_AC_likely_problems.find_all('div',{'class':'gd_one_check'})

    for i in range(0,len(h4_AC_likely_problems)):
        text_criteria=h4_AC_likely_problems[i].text[17:]
        pos = text_criteria.find(' ')
        text_criteria = text_criteria[:pos]
        one_check = one_check_AC_likely_problems[i]
        problema = one_check.span.a.text
        tabla_lineas = one_check.table.tbody
        trs = tabla_lineas.find_all('tr')
        errores_y_lineas = []
        for tr in trs:
            td = tr.td 
            linea_error= td.em
            codigo = td.pre.code
            errores_y_lineas.append({
                'linea':str(linea_error),
                'codigo':str(codigo)
                })

        texto_Actual = 'The next WARNING was found: "'+problema+'". The warning was in the following line(s): \n\n "'
        for er in errores_y_lineas:
            texto_Actual+= 'LINE '+er['linea']+': "'+er['codigo']+'".\n\n'
        if text_criteria in codes:
            nombre_wag = codes[text_criteria]
            if nombre_wag in inf_casos:
                resultado_Previo = inf_casos[nombre_wag]['Resultado']
                texto_Previo = inf_casos[nombre_wag]['Texto']
                resultado_Actual = 'Failed'

                if resultado_Previo =='Failed':
                    inf_casos[nombre_wag]['Resultado'] = 'Failed'
                else:
                    inf_casos[nombre_wag]['Resultado'] = 'Cannot Tell'


                texto_r = texto_Previo +"---------------------------------------- \n\n "+texto_Actual
                inf_casos[nombre_wag]['Texto'] = texto_r

            else:
                inf_casos[nombre_wag] = {
                    'Resultado':'Cannot Tell',
                    'Texto' : texto_Actual
                }

    #Checkear (potential problems)
    div_AC_potential_problems = s.find('div',{'id':'AC_potential_problems'}) 
    h4_AC_potential_problems = div_AC_potential_problems.find_all('h4')
    one_check_AC_potential_problems = div_AC_potential_problems.find_all('div',{'class':'gd_one_check'})

    for i in range(0,len(h4_AC_potential_problems)):
        text_criteria=h4_AC_potential_problems[i].text[17:]
        pos = text_criteria.find(' ')
        text_criteria = text_criteria[:pos]
        one_check = one_check_AC_potential_problems[i]
        problema = one_check.span.a.text
        tabla_lineas = one_check.table.tbody
        trs = tabla_lineas.find_all('tr')
        errores_y_lineas = []
        for tr in trs:
            td = tr.td 
            linea_error= td.em
            codigo = td.pre.code
            errores_y_lineas.append({
                'linea':str(linea_error),
                'codigo':str(codigo)
                })

        texto_Actual = 'A POTENTIAL PROBLEM was found: "'+problema+'". The potential problem was in the following line(s): \n\n "'
        for er in errores_y_lineas:
            texto_Actual+= 'LINE '+er['linea']+': "'+er['codigo']+'".\n\n'
        if text_criteria in codes:
            nombre_wag = codes[text_criteria]
            if nombre_wag in inf_casos:

                resultado_Previo = inf_casos[nombre_wag]['Resultado']
                texto_Previo = inf_casos[nombre_wag]['Texto']

                if resultado_Previo =='Failed':
                    inf_casos[nombre_wag]['Resultado'] = 'Failed'
                #elif resultado_Previo =='Cannot Tell':
                else:
                    inf_casos[nombre_wag]['Resultado'] = 'Cannot Tell'
                #else:
                #    inf_casos[nombre_wag]['Resultado'] = 'Not checked'


                texto_r = texto_Previo +"---------------------------------------- \n\n "+texto_Actual
                inf_casos[nombre_wag]['Texto'] = texto_r

            else:
                inf_casos[nombre_wag] = {
                    'Resultado':'Cannot Tell',
                    'Texto' : texto_Actual
                }

            informe['Cases'] = inf_casos


    return informe



def merge_reports(informe1, informe2):
    autor1 = '@'+informe1['Tester_Name']
    autor2 = '@'+informe2['Tester_Name']
    tester_name = str(informe1['Tester_Name'])+' & '+str(informe2['Tester_Name'])

    informe_final = {
           'Tester_Name': tester_name,
           'Summary': '@Access_monitor mark:'+informe1['RESULTADO']
    }

    #Primero añadimos los datos del informe 1
    for key,value in informe1['Cases'].items():
        informe_final[key] = {
            'Resultado' : value['Resultado'],
            'Texto' : '*************'+autor1+'************* \n\n'+value['Texto']+'\n\n ************************** \n\n'
        }

    #Ahora los del informe 2
    for key,value in informe2['Cases'].items():
        #Comprobamos si ya está en el informe
        if key in informe_final:
            resultado_Previo = informe_final[key]['Resultado']
            texto_Previo = informe_final[key]['Texto']
            resultado_Actual = value['Resultado']
            texto_Actual = value['Texto']

            if resultado_Previo =='Failed'or resultado_Actual == 'Failed':
                informe_final[key]['Resultado'] = 'Failed'
            elif resultado_Previo =='Cannot Tell'or resultado_Actual == 'Cannot Tell':
                informe_final[key]['Resultado'] = 'Cannot Tell'
            else:
                informe_final[key]['Resultado'] = 'Passed'


            texto_r = texto_Previo +'*************'+autor2+'************* \n\n'+value['Texto']+'\n\n ************************** \n\n'
            informe_final[key]['Texto'] = texto_r

        else:
            informe_final[key] = {
                'Resultado' : value['Resultado'],
                'Texto' : '*************'+autor2+'************* \n\n'+value['Texto']+'\n\n ************************** \n\n'
            } 
    return informe_final

def fomat_informe(url,informe):
    description = url
    pos = url.find('.')
    url = url[pos+1:]
    pos = url.find('.')
    url = url[:pos]
    informe_limpio = crear_JSON_limpio()
    autores = informe['Tester_Name']
    resultado = informe['Summary']

    informe_limpio['reportFindings']['commissioner'] = 'AUTHOMATIC'
    informe_limpio['reportFindings']['evaluator'] = autores
    informe_limpio['defineScope']['scope'] = {
            "description": str(description),
            "title": str(url)
        }

    longitud = len(informe_limpio['auditSample'])

    #Queda por meter description y fecha
    for i in range(0,longitud):
        tipo = informe_limpio['auditSample'][i]['test']['id']
        if tipo in informe:
            obj = informe[tipo]
            if obj['Resultado'] =='Failed':
                informe_limpio['auditSample'][i]['result']['outcome'] ={
                    "id": "earl:failed",
                    "type": ["OutcomeValue", "Fail"],
                    "title":"Failed"
                }
            elif obj['Resultado'] == 'Cannot Tell':
                informe_limpio['auditSample'][i]['result']['outcome'] = {
                    "id": "earl:cantTell",
                    "type": ["OutcomeValue", "CannotTell"],
                    "title": "Cannot tell"
                }

            elif obj['Resultado'] == 'Not checked':
                informe_limpio['auditSample'][i]['result']['outcome'] = {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"],
                    "title": "Not checked"
                }
            else:
                informe_limpio['auditSample'][i]['result']['outcome'] = {
                    "id": "earl:passed",
                    "type": ["OutcomeValue", "Pass"],
                    "title": "Passed"
                }
            informe_limpio['auditSample'][i]['result']['description'] = obj['Texto']
    return informe_limpio


def crear_JSON_limpio():
    now = datetime.now()
    time = str(now.strftime("%a %b %d %Y"))
    json = {
        "@context": {
            "reporter": "http://github.com/w3c/wai-wcag-em-report-tool/",
            "wcagem": "http://www.w3.org/TR/WCAG-EM/#",
            "Evaluation": "wcagem:procedure",
            "defineScope": "wcagem:step1",
            "scope": "wcagem:step1a",
            "step1b": {
                "@id": "wcagem:step1b",
                "@type": "@id"
            },
            "conformanceTarget": "step1b",
            "accessibilitySupportBaseline": "wcagem:step1c",
            "additionalEvaluationRequirements": "wcagem:step1d",
            "exploreTarget": "wcagem:step2",
            "essentialFunctionality": "wcagem:step2b",
            "pageTypeVariety": "wcagem:step2c",
            "technologiesReliedUpon": "wcagem:step2d",
            "selectSample": "wcagem:step3",
            "structuredSample": "wcagem:step3a",
            "randomSample": "wcagem:step3b",
            "Website": "wcagem:website",
            "Webpage": "wcagem:webpage",
            "auditSample": "wcagem:step4",
            "reportFindings": "wcagem:step5",
            "documentSteps": "wcagem:step5a",
            "commissioner": "wcagem:commissioner",
            "evaluator": "wcagem:evaluator",
            "evaluationSpecifics": "wcagem:step5b",
            "WCAG": "http://www.w3.org/TR/WCAG/#",
            "WCAG20": "http://www.w3.org/TR/WCAG20/#",
            "WCAG21": "http://www.w3.org/TR/WCAG21/#",
            "WAI": "http://www.w3.org/WAI/",
            "A": "WAI:WCAG2A-Conformance",
            "AA": "WAI:WCAG2AA-Conformance",
            "AAA": "WAI:WCAG2AAA-Conformance",
            "wcagVersion": "WAI:standards-guidelines/wcag/#versions",
            "reportToolVersion": "wcagem:reportToolVersion",
            "earl": "http://www.w3.org/ns/earl#",
            "Assertion": "earl:Assertion",
            "TestMode": "earl:TestMode",
            "TestCriterion": "earl:TestCriterion",
            "TestCase": "earl:TestCase",
            "TestRequirement": "earl:TestRequirement",
            "TestSubject": "earl:TestSubject",
            "TestResult": "earl:TestResult",
            "OutcomeValue": "earl:OutcomeValue",
            "Pass": "earl:Pass",
            "Fail": "earl:Fail",
            "CannotTell": "earl:CannotTell",
            "NotApplicable": "earl:NotApplicable",
            "NotTested": "earl:NotTested",
            "assertedBy": "earl:assertedBy",
            "mode": "earl:mode",
            "result": "earl:result",
            "subject": "earl:subject",
            "test": "earl:test",
            "outcome": "earl:outcome",
            "dcterms": "http://purl.org/dc/terms/",
            "title": "dcterms:title",
            "description": "dcterms:description",
            "summary": "dcterms:summary",
            "date": "dcterms:date",
            "hasPart": "dcterms:hasPart",
            "isPartOf": "dcterms:isPartOf",
            "id": "@id",
            "type": "@type",
            "language": "@language"
        },
        "language": "en",
        "type": "Evaluation",
        "reportToolVersion": "3.0.3",
        "defineScope": {
            "id": "_:defineScope",
            "scope": {
                "description": "",
                "title": ""
            },
            "conformanceTarget": "AA",
            "accessibilitySupportBaseline": "",
            "additionalEvaluationRequirements": "",
            "wcagVersion": "2.1"
        },
        "exploreTarget": {
            "id": "_:exploreTarget",
            "essentialFunctionality": "",
            "pageTypeVariety": "",
            "technologiesReliedUpon": []
        },
        "selectSample": {
            "id": "_:selectSample",
            "structuredSample": [],
            "randomSample": []
        },
        "auditSample": [{
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.699Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.699Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:non-text-content",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.700Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.700Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:audio-only-and-video-only-prerecorded",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.700Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.700Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:captions-prerecorded",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.700Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.700Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:audio-description-or-media-alternative-prerecorded",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.701Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:captions-live",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.701Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:audio-description-prerecorded",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.701Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:info-and-relationships",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.701Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:meaningful-sequence",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.701Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:sensory-characteristics",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.701Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:orientation",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.701Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:identify-input-purpose",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:use-of-color",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:audio-control",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:contrast-minimum",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:resize-text",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:images-of-text",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.540Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:reflow",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:non-text-contrast",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:text-spacing",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:content-on-hover-or-focus",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:keyboard",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:no-keyboard-trap",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:character-key-shortcuts",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.702Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:timing-adjustable",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.702Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:pause-stop-hide",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:three-flashes-or-below-threshold",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:bypass-blocks",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:page-titled",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:focus-order",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:link-purpose-in-context",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:multiple-ways",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:headings-and-labels",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:focus-visible",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:pointer-gestures",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:pointer-cancellation",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:label-in-name",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.703Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.703Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:motion-actuation",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:language-of-page",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:language-of-parts",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:on-focus",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:on-input",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:consistent-navigation",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:consistent-identification",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.541Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:error-identification",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:labels-or-instructions",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:error-suggestion",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:error-prevention-legal-financial-data",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.704Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.704Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:parsing",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.705Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.705Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:name-role-value",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }, {
            "type": "Assertion",
            "date": "2022-03-01T18:51:57.705Z",
            "mode": {
                "type": "TestMode",
                "@value": "earl:manual"
            },
            "result": {
                "type": "TestResult",
                "date": "2022-03-01T18:51:57.705Z",
                "description": "",
                "outcome": {
                    "id": "earl:untested",
                    "type": ["OutcomeValue", "NotTested"]
                }
            },
            "subject": {
                "id": "_:subject_1",
                "type": ["TestSubject", "Website"],
                "date": "2022-03-01T18:51:52.539Z",
                "description": "",
                "title": ""
            },
            "test": {
                "id": "WCAG21:status-messages",
                "type": ["TestCriterion", "TestRequirement"],
                "date": "2022-03-01T18:51:52.542Z"
            }
        }],
        "reportFindings": {
            "date": {
                "type": "http://www.w3.org/TR/NOTE-datetime",
                "@value": time
            },
            "summary": "",
            "title": "",
            "commissioner": "",
            "evaluator": "",
            "documentSteps": [{
                "id": "_:about"
            }, {
                "id": "_:defineScope"
            }, {
                "id": "_:exploreTarget"
            }, {
                "id": "_:selectSample"
            }],
            "evaluationSpecifics": ""
        }
    }
    return json