from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import onnxruntime as rt
from config import DEPLOYED_MODEL_PATH
from src.utils.geo import validate_and_geocode_address
import numpy as np
router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")

session = rt.InferenceSession(str(DEPLOYED_MODEL_PATH))
input_names = session.get_inputs()

@router.get("/", tags=["Home"], response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/predict", tags=["Prediction"])
async def predict(
    request : Request,
    type_local: str = Form(...),
    address: str = Form(...),
    surface_habitable: float = Form(...),
    nombre_pieces: int = Form(...),
    
    surface_terrain: Optional[float] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    address_type: Optional[str] = Form(None),
    ):
    print(type_local, address, surface_habitable, nombre_pieces, surface_terrain, latitude, longitude, address_type)
    # Prepare template context
    # Server-side address validation
    is_valid, geocode_data = validate_and_geocode_address(address)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Adresse introuvable. Veuillez vérifier l'adresse saisie."
        )
    
    # Use validated data
    validated_address = geocode_data['address']
    validated_lat = geocode_data['latitude']
    validated_lon = geocode_data['longitude']
    
    # Prepare for ML model
    model_input = {
        'type_local': type_local,
        'address': validated_address,
        'latitude': validated_lat,
        'longitude': validated_lon,
        'surface_habitable': surface_habitable,
        'nombre_pieces': nombre_pieces,
        'surface_terrain': surface_terrain,
        'code_commune': geocode_data.get('citycode'),
        'address_type': geocode_data.get('type')
    }
    xx = {
    'Code_postal' :  np.array([[10200.0]]),
    'Code_commune' :  np.array([[33.0]]).astype(np.int64),
    'Surface_habitable' : np.array([[0.0]]),
    'Nombre_pieces_principales' : np.array([[0.0]]),
    'Surface_reelle_bati' : np.array([[0.0]]),
    'Surface_terrain' : np.array([[217.0]])
    }

    prediction = session.run(None, xx)[0][0,0]
    print(prediction)
    
    # TODO: Call your ML model
    # from your_model import predict_price
    # prediction = predict_price(model_input)
    
    # Mock prediction
    base_price = 6000 * surface_habitable
    estimated_price = int(base_price)
    confidence_margin = int(base_price * 0.05)
    
    # Prepare template context
    context = {
        "request": request,
        "input": {
            "type": type_local,
            "address": validated_address,
            "surface_habitable": surface_habitable,
            "nombre_pieces": nombre_pieces,
            "surface_terrain": surface_terrain
        },
        "coordinates": {
            "latitude": validated_lat,
            "longitude": validated_lon,
            "commune": geocode_data.get('citycode')
        },
        "estimation": {
            "price": prediction,
            "price_per_m2": int(estimated_price / surface_habitable),
            "confidence_interval": {
                "min": estimated_price - confidence_margin,
                "max": estimated_price + confidence_margin
            },
            "confidence_level": "high" if geocode_data.get('type') == "housenumber" else "medium"
        },
        "metadata": {
            "address_score": geocode_data['score'],
            "address_type": geocode_data.get('type')
        }
    }
    return templates.TemplateResponse("prediction.html", context)