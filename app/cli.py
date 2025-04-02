import typer
import os
import json
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from typing import Optional
from dotenv import load_dotenv

# Initialize Typer app
app = typer.Typer(help="MaterialMind - AI-powered material selection advisor for mechanical engineers")
console = Console()

# Load environment variables
load_dotenv()

# Define the API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

@app.command("recommend")
def recommend_materials(
    description: str = typer.Argument(..., help="Description of the product you want to build"),
    requirements: Optional[str] = typer.Option(None, "--req", "-r", help="Additional requirements or constraints")
):
    with console.status("[bold green]Consulting AI for material recommendations..."):
        try:
            # Prepare request data
            data = {
                "description": description,
                "additional_requirements": requirements
            }
            
            # Make API request
            response = requests.post(f"{API_URL}/api/recommend-materials", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display the results
                console.print(Panel.fit(
                    f"[bold]Product:[/bold] {result['product_description']}",
                    title="MaterialMind Results",
                    border_style="green"
                ))
                
                # Create a table for the materials
                table = Table(title="Recommended Materials")
                table.add_column("Material", style="cyan")
                table.add_column("Properties", style="green")
                table.add_column("Application", style="yellow")
                table.add_column("Rationale", style="blue")
                
                for material in result["materials"]:
                    # Format properties as a string
                    properties_str = "\n".join([f"{k}: {v}" for k, v in material["properties"].items()])
                    
                    table.add_row(
                        material["name"],
                        properties_str,
                        material["application"],
                        material["rationale"]
                    )
                
                console.print(table)
                
                # Display general recommendations
                console.print(Panel(
                    result["recommendations"],
                    title="General Recommendations",
                    border_style="blue"
                ))
                
                # Display PDF path
                if result.get("pdf_path"):
                    console.print(f"\n[bold green]PDF Report generated:[/bold green] {os.path.join('outputs', result['pdf_path'])}")
            else:
                console.print(f"[bold red]Error:[/bold red] {response.status_code} - {response.text}")
        
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command("serve")
def serve_api():
    """Start the MaterialMind API server"""
    console.print("[bold green]Starting MaterialMind API server...[/bold green]")
    os.system("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    app()
