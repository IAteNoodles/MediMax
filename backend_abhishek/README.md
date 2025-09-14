# MediMax Backend - Comprehensive Documentation

## 🏥 Overview

**MediMax Backend** is a comprehensive healthcare management API built with FastAPI, designed to handle complete patient lifecycle management, medical records, appointments, medications, lab reports, and AI-powered medical analysis. This system serves as the core backend for modern healthcare applications.

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Features](#-features)
3. [Architecture](#-architecture)
4. [API Documentation](#-api-documentation)
5. [Database Schema](#-database-schema)
6. [Testing](#-testing)
7. [Deployment](#-deployment)
8. [Configuration](#-configuration)
9. [Contributing](#-contributing)
10. [License](#-license)

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **MariaDB/MySQL 8.0+**
- **pip package manager**

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd MediMax/backend_abhishek
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment configuration**
```bash
# Create .env file in the parent directory
cp ../.env.example ../.env

# Edit .env with your database credentials
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medimax
DB_USER=your_username
DB_PASSWORD=your_password
```

4. **Database setup**
```bash
# Create database and tables (see DATABASE_DOCUMENTATION.md for schema)
mysql -u root -p < database_schema.sql
```

5. **Start the server**
```bash
python app.py
```

🎉 **Server running at**: `http://127.0.0.1:8420`

### Quick Test
```bash
# Test server health
curl http://127.0.0.1:8420/health

# Expected response
{"status": "ok", "database": "ok"}
```

## ✨ Features

### 🏥 Core Healthcare Management
- **Patient Management**: Complete CRUD operations for patient records
- **Medical History**: Comprehensive medical history with categorization
- **Appointment Scheduling**: Full appointment lifecycle management
- **Medication Tracking**: Current and historical medication records
- **Symptom Management**: Detailed symptom tracking per appointment
- **Lab Reports**: Laboratory test results and findings management

### 🔍 Advanced Search & Analytics
- **Multi-criteria Search**: Search patients by name, ID, gender, etc.
- **Complete Patient Profiles**: Unified view of all patient data
- **Medical Reports**: Comprehensive reporting capabilities
- **Data Analytics**: Health trends and pattern analysis

### 🤖 AI Integration
- **Medical Analysis**: AI-powered patient assessment using MedGemma
- **Risk Prediction**: Cardiovascular and diabetes risk assessment
- **Auto-generated Queries**: Intelligent query generation from patient data
- **Medical Summarization**: AI-generated medical history summaries

### 🔒 Enterprise Features
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Error Handling**: Comprehensive error management and logging
- **Data Validation**: Strict input validation and sanitization
- **Database Integrity**: Foreign key constraints and referential integrity
- **Performance Optimization**: Indexed queries and connection pooling

## 🏗️ Architecture

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │◄──►│  FastAPI Backend │◄──►│ MariaDB Database │
│   (Streamlit)   │    │   (Port 8420)    │    │   (Port 3306)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  AI Services    │
                       │  (Ollama/MCP)   │
                       └─────────────────┘
```

### Technology Stack
- **Backend Framework**: FastAPI (Python)
- **Database**: MariaDB/MySQL
- **Database Driver**: PyMySQL
- **AI/ML**: Ollama (MedGemma model)
- **Documentation**: OpenAPI/Swagger
- **Testing**: Python requests library
- **CORS**: FastAPI CORS middleware

### Data Flow
1. **Frontend** sends HTTP requests to FastAPI backend
2. **Backend** validates input and applies business logic
3. **Database** operations with proper transaction management
4. **AI Services** provide medical analysis when requested
5. **Response** formatting and error handling
6. **Frontend** receives structured JSON responses

## 📚 API Documentation

### Complete API Reference
**📖 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Comprehensive API documentation with:
- All 29 endpoints with detailed specifications
- Request/response formats and examples
- Data model definitions
- Error handling guidelines
- Usage examples and best practices

### Interactive Documentation
When the server is running, access:
- **Swagger UI**: http://127.0.0.1:8420/docs
- **ReDoc**: http://127.0.0.1:8420/redoc

### Key Endpoint Categories

#### 🏥 Patient Management
```
POST   /db/new_patient                 # Create new patient
GET    /db/get_all_patients           # List all patients
GET    /db/get_patient_details        # Get patient by ID
PUT    /db/update_patient/{id}        # Update patient
DELETE /db/delete_patient/{id}        # Delete patient
GET    /db/search_patients            # Search patients
GET    /db/get_complete_patient_profile/{id}  # Complete profile
```

#### 📋 Medical Records
```
POST   /db/add_medical_history/{id}   # Add medical history
GET    /db/get_medical_history        # Get medical history
POST   /db/add_appointment/{id}       # Schedule appointment
POST   /db/add_medication/{id}        # Add medication
POST   /db/add_symptom               # Add symptom
```

#### 🧪 Lab Management
```
POST   /db/add_lab_report/{id}       # Create lab report
POST   /db/add_lab_finding           # Add lab finding
GET    /get_n_lab_reports/{id}       # Get lab reports
GET    /db/get_medical_reports       # Get all reports
```

#### 🤖 AI Services
```
GET    /models                       # Available AI models
POST   /assess                       # Patient assessment
GET    /frontend/get_query           # Auto-generate queries
```

## 🗄️ Database Schema

### Database Documentation
**📊 [DATABASE_DOCUMENTATION.md](./DATABASE_DOCUMENTATION.md)** - Complete database reference with:
- Table schemas and relationships
- Enum values and constraints
- Performance optimization
- Backup and recovery procedures

### Core Tables
- **Patient**: Demographics and identification
- **Medical_History**: Medical conditions and history
- **Appointment**: Scheduled appointments
- **Appointment_Symptom**: Symptoms per appointment
- **Medication**: Current and past medications
- **Lab_Report**: Laboratory test orders
- **Lab_Finding**: Individual test results

### Key Relationships
```sql
Patient (1:N) ──► Medical_History
Patient (1:N) ──► Appointment
Patient (1:N) ──► Medication
Patient (1:N) ──► Lab_Report
Appointment (1:N) ──► Appointment_Symptom
Lab_Report (1:N) ──► Lab_Finding
```

### Enum Validation
The system includes automatic mapping between API inputs and database enum values:
```python
# Example: Appointment types
API Input: "Regular" → Database: "routine_checkup"
API Input: "Emergency" → Database: "emergency"
```

## 🧪 Testing

### Test Documentation
**🔬 [API_TESTING_DOCUMENTATION.md](./API_TESTING_DOCUMENTATION.md)** - Complete testing guide with:
- Test file specifications
- Configuration options
- Running instructions
- Result interpretation

### Test Files

#### 1. Comprehensive Testing
```bash
python test_api_traditional.py
```
- ✅ Colored output with detailed logging
- ✅ Tests all 29 endpoints
- ✅ Response validation and timing
- ✅ Error analysis and debugging

#### 2. Quick Testing
```bash
python test_api_simple.py
```
- ⚡ Fast execution for CI/CD
- 🎯 Essential endpoint coverage
- 📊 Summary statistics

### Test Configuration
```python
# Patient ID assignments for testing
PATIENT_ID_FOR_GET = 7      # GET operations
PATIENT_ID_FOR_PUT = 6      # PUT operations  
PATIENT_ID_FOR_DELETE = 1   # DELETE operations (⚠️ destructive)
```

### Sample Test Output
```
==================== API TESTING STARTED ====================
[1/29] Testing GET /health...
✅ SUCCESS: GET /health (Status: 200)
Response: {'status': 'ok', 'database': 'ok'}
Response Time: 0.045s

[2/29] Testing POST /db/new_patient...
✅ SUCCESS: POST /db/new_patient (Status: 200)
Patient Created: ID 156, Name: Sarah Wilson
Response Time: 0.089s
...
==================== TEST SUMMARY ====================
Total Tests: 29
✅ Passed: 27
❌ Failed: 2  
⚠️  Warnings: 0
Success Rate: 93.1%
Total Duration: 15.67s
==================== TESTING COMPLETED ====================
```

## 🚀 Deployment

### Local Development
```bash
# Start development server
python app.py

# Server details
Host: 0.0.0.0 (all interfaces)
Port: 8420
Auto-reload: Enabled
```

### Production Deployment

#### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8420

CMD ["python", "app.py"]
```

#### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Start with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8420 app:app
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8420;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Environment Variables
```env
# Database Configuration
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=medimax
DB_USER=your_username
DB_PASSWORD=your_secure_password

# Server Configuration  
HOST=0.0.0.0
PORT=8420

# AI Services
AGENTIC_ADDRESS=http://your-ai-server:8000
FRONTEND_ADDRESS=http://your-frontend:8501
```

## ⚙️ Configuration

### Database Configuration
```python
# Connection settings in app.py
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306") 
DB_NAME = os.getenv("DB_NAME", "medimax")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Connection pool settings (production)
MAX_CONNECTIONS = 50
MIN_CONNECTIONS = 10
CONNECTION_TIMEOUT = 10
```

### CORS Configuration
```python
# Allowed origins for cross-origin requests
origins = [
    "http://10.26.5.99:8501",    # Production frontend
    "http://localhost:8501",      # Local development
    "http://127.0.0.1:8501"      # Alternative local
]

# CORS middleware settings
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### AI Integration Configuration
```python
# Agentic system addresses
AGENTIC_ADDRESS = "http://10.26.5.99:8000"
FRONTEND_ADDRESS = "http://10.26.5.99:8501"

# AI request timeout
AI_TIMEOUT = 60.0  # seconds
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python test_api_traditional.py`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards
- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type annotations where possible
- **Documentation**: Document all functions and classes
- **Testing**: Include tests for new features
- **Error Handling**: Implement proper error handling

### Commit Message Format
```
type(scope): description

# Types: feat, fix, docs, style, refactor, test, chore
# Examples:
feat(api): add patient search endpoint
fix(db): resolve connection pool issue
docs(readme): update installation instructions
```

## 📄 File Structure

```
backend_abhishek/
├── app.py                           # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── test_api_traditional.py         # Comprehensive API tests
├── test_api_simple.py              # Quick API tests  
├── test_requirements.txt           # Testing dependencies
├── API_DOCUMENTATION.md            # Complete API reference
├── API_TESTING_DOCUMENTATION.md   # Testing guide
├── DATABASE_DOCUMENTATION.md      # Database reference
├── README.md                       # This file
└── mock_data.json                  # Sample data for testing
```

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database server status
systemctl status mysql

# Test connection manually
mysql -h localhost -u your_user -p your_database

# Verify environment variables
echo $DB_HOST $DB_USER $DB_NAME
```

#### Port Already in Use
```bash
# Check what's using port 8420
lsof -i :8420

# Kill process if needed
kill -9 <PID>

# Use alternative port
python app.py --port 8421
```

#### Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+

# Virtual environment recommended
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Debug Mode
Enable detailed logging for troubleshooting:
```python
# In app.py, add logging configuration
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
uvicorn app:app --reload --log-level debug
```

## 📞 Support

### Documentation Links
- **📖 [API Documentation](./API_DOCUMENTATION.md)** - Complete endpoint reference
- **🔬 [Testing Guide](./API_TESTING_DOCUMENTATION.md)** - Testing procedures
- **📊 [Database Reference](./DATABASE_DOCUMENTATION.md)** - Schema and design

### Getting Help
1. Check the documentation files above
2. Review the interactive API docs: http://127.0.0.1:8420/docs
3. Run the test suite to verify functionality
4. Check the troubleshooting section

### Development Team
- **Backend Development**: FastAPI, Database, and API design
- **Testing**: Comprehensive test suite development
- **Documentation**: Complete system documentation
- **AI Integration**: Medical AI model integration

---

## 🏥 MediMax: Transforming Healthcare Through Technology

**MediMax Backend** provides the robust foundation for modern healthcare applications, combining comprehensive medical data management with AI-powered insights to improve patient care and clinical decision-making.

### 🌟 Key Benefits
- **Complete Patient Management**: Comprehensive healthcare data lifecycle
- **AI-Powered Insights**: Medical analysis and risk prediction  
- **Scalable Architecture**: Built for enterprise healthcare environments
- **Developer Friendly**: Extensive documentation and testing tools
- **Production Ready**: Robust error handling and performance optimization

---

*This documentation is maintained by the MediMax development team. For updates and contributions, please follow the contributing guidelines above.*