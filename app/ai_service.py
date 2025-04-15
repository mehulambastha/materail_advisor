import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt for the AI
SYSTEM_PROMPT = """You are MaterialMind, an expert AI advisor for mechanical engineers specializing in material selection.
When given a product description, provide comprehensive material recommendations with the following details:

1. List appropriate materials for different components of the product
2. For each material, include:
   - Full scientific name and common name
   - Key properties (density, tensile strength, thermal conductivity, endurance limit, fatigue strenth, etc., wherever relevant and necessary)
   - Specific applications within the product
   - Rationale for why this material is suitable
   - Rough Cost of the materials required to make the specific part (in INR. Do not use the symbol for INR, just say INR)
3. Potential material alternatives with pros and cons
4. Manufacturing considerations related to material choices
5. Cost considerations and trade-offs

Format your response as structured JSON with the following format: 


{
  "materials": [
    {
      "name": "Material name",
      "properties": {
        "property1": "value1",
        "property2": "value2"
      },
      "application": "Where to use this material",
      "rationale": "Why this material is suitable"
    }
  ],
  "general_recommendations": "Overall advice about material selection",
  "alt_materials": "Your potential material alternatives with Pros and Cons",
  "manufacturing_considerations": "Manufacturing considerations related to material choices",
  "cost_considerations": "Cost considerations and trade-offs"
}

make sure the JSON data has proper and conventional annotation, like 

Include numerical values with proper units for all material properties.

YOUR FINAL response SHOULD BE STRICTLY VALID JSON ONLY - all properties and values should be properly double quoted. everything should be valid JSON format.  
(so that I can simply load your response in python with josn.loads(), with the folllowing strcuture - 
{
  "materials": [
    {
      "name": "Material name",
      "properties": {
        "property1": "value1",
        "property2": "value2"
      },
      "application": "Where to use this material",
      "rationale": "Why this material is suitable"
    }
  ],
  "general_recommendations": "Overall advice about material selection",
  "alt_materials": "Your potential material alternatives with Pros and Cons",
  "manufacturing_considerations": "Manufacturing considerations related to material choices",
  "cost_considerations": "Cost considerations and trade-offs"
}


    
IMPORTANT: DO NOT HALLUCINATE. DO NOT GIVE FALSE INFORMATION. DO NOT MENTION YOUR NAME, OR THAT YOU ARE AN AI. ANSWER ONLY THOSE QUESTIONS RELATED TO PRODUC DEVELOPMENT AND MATERIAL SELECTION. DO NOT ENGAGE IN CONVERSATIONS OF ANY OTHER MATTER. FOR IRRELEVANT QUESTIONS ASKED, RETURN BACK AN ERROR MESSAGE SAYING INVALID PRODUCT DESCRIPTION.
"""

def get_material_recommendations(product_description: str, additional_requirements: Any = None) -> Dict[str, Any]:
    """
    Get material recommendations from Groq AI for a given product description
    """
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        raise Exception("GROQ_API_KEY environment variable is required")
    
    # Combine the product description with additional requirements
    prompt = f"Product description: {product_description}"
    if additional_requirements:
        prompt += f"\nAdditional requirements: {additional_requirements}"
    
    prompt += "\n\nPlease provide detailed material recommendations for this product, including specific materials for each component, their properties, applications, and rationale."
    
    try:
        # Call Groq API
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Using Llama 3 model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # Lower temperature for more consistent responses
        )
        
        response_content = response.choices[0].message.content
        print("RESPONSE FORM AI IS : \n", response_content)
        
        # Try to parse as JSON
        try:
            material_data = json.loads(response_content)
            print("return data loaded as JSON is : \n ", material_data)
        except json.JSONDecodeError:
            print("JSON PARSING FAILED.")
            # If parsing fails, we'll need to extract JSON from the text
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_content, re.DOTALL)
            if json_match:
                material_data = json.loads(json_match.group(1))
            else:
                # As a fallback, create a simple structure with the raw text
                print("Warning: Could not parse JSON from AI response, using text format instead")
                material_data = {
                    "materials": [
                        {
                            "name": "See recommendations",
                            "properties": {"info": "See full text"},
                            "application": "See full text",
                            "rationale": "See full text"
                        }
                    ],
                    "general_recommendations": response_content
                }
        
        # Process and structure the response
        materials = []
        general_recommendations = material_data.get("general_recommendations", "")
        
        for material in material_data.get("materials", []):
            materials.append({
                "name": material.get("name", ""),
                "properties": material.get("properties", {}),
                "application": material.get("application", ""),
                "rationale": material.get("rationale", "")
            })
        
        return {
            "materials": materials,
            "general_recommendations": general_recommendations
        }
    
    except Exception as e:
        print(f"Error communicating with Groq API: {str(e)}")
        raise Exception(f"AI recommendation failed: {str(e)}")
