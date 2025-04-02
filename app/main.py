from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os
from app.ai_service import get_material_recommendations
from app.pdf_service import generate_pdf
import uuid

app = FastAPI(
    title="MaterialMind",
    description="AI-powered material recommendation system for mechanical engineers",
    version="1.0.0"
)

class ProductRequest(BaseModel):
    description: str
    additional_requirements: Optional[str] = None

class MaterialSpecification(BaseModel):
    name: str
    properties: dict
    application: str
    rationale: str

class RecommendationResponse(BaseModel):
    product_description: str
    materials: List[MaterialSpecification]
    recommendations: str
    pdf_path: Optional[str] = None

@app.post("/api/recommend-materials", response_model=RecommendationResponse)
async def recommend_materials(request: ProductRequest, background_tasks: BackgroundTasks):
    try:
        # Get material recommendations from AI
        recommendations = get_material_recommendations(
            request.description,
            request.additional_requirements
        )
        
        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())
        pdf_filename = f"MaterialMind_Recommendation_{request_id}.pdf"
        
        # Generate PDF in the background
        background_tasks.add_task(
            generate_pdf,
            recommendations,
            pdf_filename
        )
        
        return {
            "product_description": request.description,
            "materials": recommendations["materials"],
            "recommendations": recommendations["general_recommendations"],
            "pdf_path": pdf_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to MaterialMind API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
