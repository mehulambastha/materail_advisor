# MaterialMind - AI-Powered Material Advisor for Mechanical Engineers

MaterialMind is an AI-driven application that helps mechanical engineers select the optimal materials for their products. By analyzing product descriptions and requirements, MaterialMind provides detailed material recommendations with scientific specifications, applications, and rationales.

## Features

- **AI-Powered Material Recommendations**: Get expert advice on material selection tailored to your specific product needs
- **Detailed Material Specifications**: Access comprehensive material properties, including tensile strength, density, thermal properties, and more
- **Component-Specific Suggestions**: Recommendations for which materials to use for different parts of your product
- **PDF Report Generation**: Export material specifications and recommendations to a professionally formatted PDF
- **Command-Line Interface**: Quick and easy access through a user-friendly CLI
- **API Access**: Integrate with your existing tools via the FastAPI backend

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
API_URL=http://localhost:8000
```

## Usage

### Start the API Server

```bash
python -m app.cli serve
```

### Get Material Recommendations via CLI

```bash
python -m app.cli recommend "I need to design a lightweight drone frame that can withstand moderate impacts and operate in temperatures between -10°C and 40°C"
```

Add additional requirements (optional):

```bash
python -m app.cli recommend "I need to design a lightweight drone frame" --req "Must be corrosion resistant and cost-effective for mass production"
```

### API Endpoints

- **POST /api/recommend-materials**: Get material recommendations for a product
- **GET /**: Simple health check endpoint

## Adding a NextJS Frontend (Future Enhancement)

This project is designed to be extended with a NextJS frontend. The API is built to support this integration seamlessly.

## License

MIT
