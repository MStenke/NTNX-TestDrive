import streamlit as st
import custom_functions
import pandas as pd
import clipboard
from datetime import timedelta, date
from PIL import Image
from fpdf import FPDF

######################
# Page Config
######################
st.set_page_config(page_title="Nutanix Test Drive Gutschein-Generator", page_icon='./style/favicon.png', layout="wide")
# Use CSS Modifications stored in CSS file            
st.markdown(f"<style>{custom_functions.local_css('style/style.css')}</style>", unsafe_allow_html=True)

######################
# Page sections
######################
header_section = st.container()
step_1_section = st.container()
step_2_section = st.container()
step_3_section = st.container()

######################
# Page content
######################
with header_section:
    st.markdown("<h1 style='text-align: left; color:#034ea2;'>Nutanix Test Drive Gutschein-Generator</h1>", unsafe_allow_html=True)
    st.markdown('Ein Hobby-Projekt von [**Martin Stenke**](https://www.linkedin.com/in/mstenke/) zum Erstellen von  [**Nutanix Test Drive**](https://collector.nutanix.com/) Gutscheinen für Nutanix Interessenten. **Nur für Nutanix Mitarbeitern vorgesehen.** (Zuletzt aktualisiert: 16.02.2022)')
    st.info('***Disclaimer: Hierbei handelt es sich lediglich um ein Hobby Projekt - keine Garantie auf Vollständigkeit oder Korrektheit der Auswertung / Daten.***')
    st.markdown("---")

with step_1_section:
    st.markdown('### **Schritt 1: CSV Datei mit den Nutanix Test Drive Interessenten erstellen**')
    st.write('Bitte Interessenten aufführen die Zugang zu einem Nutanix Test Drive erhalten sollen. Die E-Mail Adresse ist dabei zwingend erforderlich, Vor- und Nachname hingegen optional aber natürlich dennoch empfohlen, damit systembedingt passende Daten z.B. für eine korrekte Ansprache vorliegen.')

    data = pd.DataFrame(columns=["E-Mail Adresse","Vorname","Nachname"])

    if 'Data' not in st.session_state:
            st.session_state['Data'] = data

    col_email,col_vorname,col_nachname = st.columns([2,1,1])
    with col_email:
        st.text_input('E-Mail Adresse:', key='email', value='', max_chars=50)
    with col_vorname:
        st.text_input('Vorname (optional):', key='vorname', max_chars=30)
    with col_nachname:
        st.text_input('Nachname (optional):', key='nachname', max_chars=30)
    
    warning_placeholder = st.container()
    warning_placeholder.empty()
    col_add_entry,col_drop_entry,col_drop_all = st.columns([2,1,1])
    with col_add_entry:
        if st.button("Neuen Eintrag hinzufügen"):
            email = st.session_state['email'].strip()
            if custom_functions.verify_email(email):
                if not email in st.session_state['Data'].values:
                    vorname = st.session_state['vorname'].strip()
                    nachname = st.session_state['nachname'].strip()
                    st.session_state['Data'] = st.session_state['Data'].append({"E-Mail Adresse": email,"Vorname": vorname,"Nachname": nachname}, ignore_index=True)
                else:
                   warning_placeholder.warning('E-Mail bereits vorhanden.') 
            else:
                warning_placeholder.warning('E-Mail Adresse ungültig')

    with col_drop_entry:
        if st.button('Letzten Eintrag löschen'):
            st.session_state['Data'].drop(st.session_state['Data'].tail(1).index,inplace=True)
        
    with col_drop_all:
        if st.button('Alle Einträge löschen'):
            data = pd.DataFrame(columns=["E-Mail Adresse","Vorname","Nachname"])
            st.session_state['Data'] = data
    
    # Show table 
    st.table(st.session_state['Data'])
    # Generate CSV 
    csv = custom_functions.convert_df(st.session_state['Data'])

    st.download_button(
        "Download CSV Datei",
        csv,
        "Nutanix-Test-Drive-Interessenten.csv",
        "text/csv",
        key='download-csv'
        )
           
with step_2_section:
    st.write('---')
    st.markdown("### **Schritt 2: Zugangs-Code's & Links als CSV Datei generieren**")

    st.write('Leider liegt dieser Schritt in einem Nutanix Mitarbeiter geschützem Bereich der eine Nutzer-Authentifizierung erfordert. Ohne passenden API User (den ein Hobby Coder wie ich - wohl aus gutem Grund - nicht erhält 😅) lässt sich dieser Schritt leider nicht "von außen" automatisieren, sodass Schritt 2 manuell zu erledigen ist. Ist im Grunde genommen aber auch schnell gemacht. Genaue Anleitung in dem aufklappbaren Feld. 😄')
    
    with st.expander("Anleitung"):
        st.write("Bitte die folgende Nutanix interne URL: https://api.nutanixtestdrive.com/private/upload/ aufrufen und die zuvor generierte CSV Datei mit den Nutanix Test Drive Interessenten dort hochladen (Nutanix Mitabeiter Authentifizierung erforderlich).")
        st.write("Bitte die Duration auf 4h belassen (diese kann nach Bedarf um 4h von dem Test Drive Interessenten verlängert werden), beim Template ist es egal was Sie auswählen (wird nachher überschrieben), den Haken bei WalkMe Autoplay gesetzt lassen (macht die Verwendung einfacher), den Haken bei Send Emails entfernen (sonst werden die Interessenten automatisch von einer generischen E-Mail-Adresse kontaktiert) und zuletzt bei Region us selektiert lassen. Die so erzeugte CSV Datei wird in Schritt 3 benötigt.")
        st.write('**Die Einstellungen sollten idealerweise wie folgt aussehen:**')
        st.image("images/upload_csv.png")
        st.info('**Wichtiger Hinweis:** Sobald die aus Schritt 1 generierte CSV Datei in dem internen Portal hochgeladen wurde beginnt der Testzeitraum der nach **10 Tagen** abläuft. Danach können die Codes nicht mehr verwendet werden. Daher sollte Schritt 2 und 3 sowie die Weitergabe an den Kunden am besten direkt nacheinander durchgeführt werden.')
    

with step_3_section:
    st.write('---')
    st.markdown('### **Schritt 3: PDF Gutschein oder Text-Vorlage generieren**')
    
    try:
        
        column_1,column_2 = st.columns(2)
        with column_1:
            uploaded_file = st.file_uploader("CSV Datei mit Zugangs-Codes's hochladen:", type='CSV')
        with column_2:
            td_selection = { 1:'Freie Auswahl', 
                            2:'Nutanix Basis Test Drive (NCI, Prism, Calm)',
                            3:'Unified Storage Test Drive', 
                            4:'Xi Leap Test Drive',
                            5:'Era Test Drive',
                            6:'Flow Test Drive', 
                            7:'Clusters on AWS Test Drive',
                            8:'Clusters on Azure Test Drive',
                            9:'Nutanix Mine with HYCU Test Drive',
                            10:'AOS Deep Dive',
                            11:'Files Deep Dive',
                            12:'Calm Deep Dive',
                            13:'One-Click Kubernetes Deep Dive',
                            14:'Xi Leap Deep Dive'}
            testdrive_option = st.selectbox('Test Drive Typ auswählen:', td_selection.keys(), format_func=lambda x:td_selection[ x ])
    
        if uploaded_file is not None:
        
            dataframe = pd.read_csv(uploaded_file)
            csv_file_df = custom_functions.url_to_df(dataframe['link'])

            column_1_2,column_2_2 = st.columns(2)

            with column_1_2:
                user = st.selectbox('Für welchen Interessenten?',csv_file_df['query_email'])

            with column_2_2:
                sender = st.text_input('Wer ist der Nutanix Ansprechpartner (Name, Titel, E-Mail)? (optional)',max_chars=70)

            user_row = csv_file_df.loc[csv_file_df['query_email'] == user]
            test_drive_type = td_selection[testdrive_option]
            access_code = user_row['query_token'].to_string(index=False)
            end_date_valid = (date.today() + timedelta(days=10)).strftime("%d.%m.%Y")

            test_drive_link = user_row['scheme'].to_string(index=False)+'://'+user_row['netloc'].to_string(index=False)+user_row['path'].to_string(index=False)+'?email='+user_row['query_email'].to_string(index=False)+'&token='+user_row['query_token'].to_string(index=False)+custom_functions.get_td_type_by_selection(testdrive_option)+'&region=us'

            html_str = f"""- Test Drive Typ: {test_drive_type}
- E-Mail-Adresse: {user}
- Access Code: {access_code}
- Nutanix Test Drive Zugangs-Link: {test_drive_link}
- Gültigkeit: 10 Tage, bis spätestens {end_date_valid}
"""
            if sender.strip() != '':
                html_str_2 = f"- Ihr Nutanix Ansprechpartner: {sender}"
                html_str = html_str+html_str_2

            col_actions,col_preview = st.columns([1,4])
            with col_actions:
                st.markdown("<h4 style='text-align: left; color:#034ea2;'>Aktionen:</h4>", unsafe_allow_html=True)
                
                if st.button('Text-Vorlage kopieren'):
                    clipboard.copy(html_str)
                    clipboard.paste()
                    st.success("Erfolgreich kopiert")
                st.write('---')

                pdf = FPDF(orientation="L", unit="mm", format=(250.12,420.16))#"A4")
                pdf.set_margins(0,0,0)                
                pdf.add_page()
                pdf.image("images/template.png", 0, 0, 420.16, 250.12)
                pdf.set_font("Arial", "",18)
                pdf.text(16,115, 'Test Drive Typ:')
                pdf.text(25,125, f'{str(test_drive_type)}')
                pdf.text(16,137, 'E-Mail-Adresse:')
                pdf.text(25,147, f'{str(user)}')
                pdf.text(16,159, 'Access Code:')
                pdf.text(25,169, f'{str(access_code)}')                
                
                if sender.strip() != '':
                    pdf.image("images/button.png",16,182,165,15,"PNG",f'{test_drive_link}')
                    pdf.set_font("Arial", "",16)
                    pdf.text(16,208, f'* Gültigkeit: 10 Tage, bis spätestens {str(end_date_valid)}')
                    pdf.set_font("Arial", "",18)
                    pdf.text(16,230, 'Bei Fragen wenden Sie sich an Ihren Nutanix Ansprechpartner:')
                    pdf.text(16,240, f'{str(sender)}')
                else:
                    pdf.image("images/button.png",16,190,165,15,"PNG",f'{test_drive_link}')
                    pdf.set_font("Arial", "",16)
                    pdf.text(16,216, f'* Gültigkeit: 10 Tage, bis spätestens {str(end_date_valid)}')
                file_download_name = user.split("@")[0]
                st.download_button(
                    "PDF Gutschein erstellen",
                    data=pdf.output(dest='S').encode('latin-1'),
                    file_name=f"Nutanix Test Drive Gutschein - {file_download_name}.pdf",
                )

            with col_preview:
                st.markdown("<h4 style='text-align: left; color:#034ea2;'>Text-Vorlage:</h4>", unsafe_allow_html=True)
                st.markdown(html_str, unsafe_allow_html=True)
                st.info('**Wichtig:** Test Drive Zugangs-Link *nicht klicken*, Test Drive Zeitraum startet sofort ab Klick.')

    except Exception as e: 
        step_3_section.error("##### FEHLER: Die hochgeladene CSV Datei mit den Zugangs-Codes konnte leider nicht ausgelesen werden.")
        step_3_section.markdown("**Bitte stellen Sie sicher, dass es sich um eine CSV Datei handelt welche in Schritt 2 erzeugt und nicht modifiziert wurde.**")
        step_3_section.markdown("---")
        step_3_section.markdown("Im folgenden die genaue Fehlermeldung für das Troubleshooting:")
        step_3_section.exception(e)
