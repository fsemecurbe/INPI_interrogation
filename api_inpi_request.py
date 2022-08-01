import streamlit as st
import pandas as pd
import requests
import json
import numpy as np




def requete_siren(siren):
    url = 'https://data.inpi.fr/entreprises/'+siren+'?q='+siren
    #print(url)
    response = requests.post(url, timeout=22.50)
    df = pd.read_json(response.text)
    df['nom_variable'] = df.index
    df['valeur_variable'] = df['_source']
    df['siren'] = siren
    df = df.set_index('siren')
    df = df.pivot(columns='nom_variable', values='valeur_variable')
    
    #df = df.set_index('siren')
    return(df)

def requete_sirens(sirens):
    '''Fonction pour requeter une liste de sirens '''
    list_df = []
    my_bar = st.progress(0)
    pct_rate = 1 / len(sirens)
    


    for count,siren in enumerate(np.unique(sirens)):
        try: # j'ai rajouté un try pour gérer les erreurs de siren
            list_df.append(requete_siren(siren))
        except:
            pass
            #print("Erreur pour le siren " + siren)
            list_df.append(pd.DataFrame({'siren':siren, 'erreur': 'absence INPI'}, index=[siren]))
        my_bar.progress((count+1) * pct_rate)
        
    return(pd.concat(list_df, ignore_index=False))

def deplier_obsevations(df):    
    df_obs = df.loc[~df.observations.isna(),['siren', 'observations']].copy()
    df_obs = df_obs.loc[df_obs.observations.apply(len)>0].copy()
       
    obs = pd.concat(df_obs.observations.apply(lambda x : pd.DataFrame(x[0], index=[0])).values)
    obs['siren'] = df_obs.index
    obs = obs.set_index('siren')
    df = pd.merge(df, obs, left_index=True, right_index=True, how='outer')
    return(df)



st.title("Accès aux données d'identité légale des sociétés")
st.markdown("Les données proviennent du site https://data.inpi.fr/. Veuillez rentrer une liste de numéros siren séparés par des espaces ou des retours chariots.")


with st.form("my_form"):
    sirens = st.text_area('Liste de Sirens à requêter', '316203199\n394140933\n402091672\n830327250\n320554215')
    submit = st.form_submit_button("Executer l'interrogation")

if submit:    
    
    df = requete_sirens(sirens.split())
    
    try: 
        df = deplier_obsevations(df)
    except:
        pass
    
    dfn = df
   
    variables_pb = ['actes','etablissements','representants','observations', 'beneficiaires']
    variables_pb =  [var for var in variables_pb if var in dfn.columns]
    
    st.dataframe(dfn.drop(columns=variables_pb))
 
    
    st.download_button(
             label="télécharger les données",
             data=df.to_csv().encode('utf-8'),
             file_name='large_df.csv',
             mime='text/csv',
         )

