from config import dvf_clean ,MODEL_DIR
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from pickle import dump, load
from datetime import datetime


def load_df(data_path):
    return pd.read_csv(data_path, low_memory=False)

def generate_Xy(df:pd.DataFrame):
    y = df['Valeur fonciere']
    X = df.drop(columns=['Valeur fonciere', 'Code departement'])
    return X,y

def generate_train_test(X, y, test_size, random_state):
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def export_pipeline(pipe, pipe_path):
    with open(pipe_path, "wb") as f:
        dump(pipe, f)

def load_pipeline(pipe_path):
    with open(pipe_path, "rb") as f:
        return load(f)

def model_path(name):
    now=datetime.now().strftime("%Y%m%d-%Hh%Mm%S")
    return MODEL_DIR/ f'{now}_{name}.pkl'

def main():
    df = load_df(dvf_clean)
 
    X, y = generate_Xy(df)

    X_train, X_test, y_train, y_test = generate_train_test(X, y, test_size=0.3, random_state=8)
    pipe = Pipeline([('scaler', StandardScaler()), ('rf', RandomForestRegressor(max_depth=6, random_state=0))])
    pipe_path=model_path('rf')
    try:
        print("Entrainement du model...")
        pipe.fit(X_train,y_train)
        print("Entrainement terminé.")
        
    except Exception as e:
        print(e)
    finally:
        export_pipeline(pipe, pipe_path)

    y_train_pred=pipe.predict(X_train)
    y_test_pred=pipe.predict(X_test)
    r2_train=r2_score(y_train, y_train_pred)
    r2_test=r2_score(y_test, y_test_pred)
    print(f'r2 train = {r2_train}')
    print(f'r2_test = {r2_test}')

if __name__ == "__main__":
    main()