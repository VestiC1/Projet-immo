from config import DVF, dvf_clean
import pandas as pd
from .insee_api import DensitePopulation, validate_and_geocode_address


def load_df(data_path):
    return pd.read_csv(data_path, sep='|', decimal=",", compression="zip", low_memory=False)

def save_df(df, df_path):
    df.to_csv(df_path, index=False)

def clean_df(df):
    # Sélection des colonnes pour calculer [Surface habitable]
    df_new = df[['Date mutation', 'Nature mutation', 'Valeur fonciere', 'Code postal', 'Code departement', 'Code commune', 'Surface Carrez du 1er lot', 'Surface Carrez du 2eme lot', 'Surface Carrez du 3eme lot', 'Surface Carrez du 4eme lot', 'Surface Carrez du 5eme lot', 'Nombre pieces principales', 'Surface reelle bati', 'Surface terrain', 'Type de voie', 'Type local', 'Commune']]
    # Suppression des doublons
    df_new = df_new.drop_duplicates()
    # Remplacement des NaN par 0.00 dans les colonnes avec des valeurs numerique pour le calcul de [Surface habitable]
    df_new = df_new.fillna(.0)
    # Calcul de [Surface habitable]
    df_new["Surface habitable"] = df_new["Surface Carrez du 1er lot"] + df_new["Surface Carrez du 2eme lot"] + df_new["Surface Carrez du 3eme lot"] + df_new["Surface Carrez du 4eme lot"] + df_new["Surface Carrez du 5eme lot"]
    # Selection : Si les lignes avec [Surface habitable] = 0, remplacer la valeur de [Surface reelle bati]
    df_new["Surface habitable"] = df_new.apply(lambda row: row["Surface reelle bati"] if row["Surface habitable"] == 0 else row["Surface habitable"], axis=1)
    # Calcul du prix m2
    df_new["Prix m2"] = df_new["Valeur fonciere"] / df_new["Surface habitable"]
    # Sélection des colonnes
    df_new = df_new[['Valeur fonciere', 'Code postal', 'Code departement', 'Code commune', 'Surface habitable', 'Nombre pieces principales', 'Surface reelle bati', 'Surface terrain','Type de voie', 'Type local', 'Prix m2', 'Commune']]
    return df_new

def add_features(df):
    # Calcul de la densité de population
    geo_dict = {}
    densite_api = DensitePopulation()
    
    # Concaténation des colonnes commune et code postal
    df['commune_postal'] = df['Commune'].astype(str) + ', ' + df['Code postal'].astype(str)
    code_postal = df['commune_postal'].to_frame().drop_duplicates()

    df["longitude"] = 0.0
    df["latitude"] = 0.0
    df["densite"] = 0.0
    # Boucle sur toutes les lignes pour récupérer densité, latitude, longitude
    for index, row in code_postal.iterrows():
        commune_postal = row['commune_postal']
        print(f"\r{index}", end="", flush=True)
        # Si on a déjà traité cette commune+code_postal, on réutilise
        if commune_postal in geo_dict:
            # Utiliser les valeurs du cache
            latitude, longitude, densite = geo_dict[commune_postal]
            df.loc[df['commune_postal'] == commune_postal, 'latitude'] = latitude
            df.loc[df['commune_postal'] == commune_postal, 'longitude'] = longitude
            df.loc[df['commune_postal'] == commune_postal, 'densite'] = densite
            continue
            
        # Géocodage de l'adresse
        is_valid, geocode_data = validate_and_geocode_address(commune_postal)
        
        if is_valid and geocode_data:
            # Récupération de la densité, latitude, longitude
            result = densite_api.get_densite(geocode_data)
            if result:
                densite, latitude, longitude = result
                # Stocker dans le cache
                geo_dict[commune_postal] = (latitude, longitude, densite)
                # Mettre à jour le DataFrame
                df.loc[df['commune_postal'] == commune_postal, 'latitude'] = latitude
                df.loc[df['commune_postal'] == commune_postal, 'longitude'] = longitude
                df.loc[df['commune_postal'] == commune_postal, 'densite'] = densite
            else:
                # Valeurs par défaut si pas de données
                geo_dict[commune_postal] = (0.0, 0.0, 0.0)
        else:
            # Valeurs par défaut si géocodage échoué
            geo_dict[commune_postal] = (0.0, 0.0, 0.0)
    
    return df

def main():
    df=load_df(DVF)
    df=clean_df(df)
    df=add_features(df)

    save_df(df, dvf_clean)

if __name__ == "__main__":
    main()