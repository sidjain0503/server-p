# InscribeVerse - Fast API Server 🚀

**🎉 Build APIs at the speed of thought with InscribeVerse Meta-Engine!**

_Transform schemas into production-ready APIs in minutes, not weeks._


**Schema-driven API generation system** that transforms data definitions into complete REST APIs automatically.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![JWT](https://img.shields.io/badge/JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

## 🎯 What is InscribeVerse?

InscribeVerse is a **meta-engine** that eliminates repetitive API development. Define your data schema once, and get a complete REST API with:

✅ **Auto-generated CRUD operations** (Create, Read, Update, Delete, List, Count)  
✅ **JWT Authentication System** with flexible route protection  
✅ **Type-safe validation** with Pydantic v2  
✅ **Interactive API documentation** (Swagger/OpenAPI)  
✅ **PostgreSQL integration** with async SQLAlchemy  
✅ **Extensible custom endpoints** for business logic  
✅ **Flexible authentication control** (public/protected routes)  
✅ **Production-ready** architecture

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                Schema Definition                            │
│  ProductSchema, CustomerSchema, TaskSchema, AuthSchemas    │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼─────────────┐
    │      Meta-Engine          │
    │  • Dynamic Model Factory  │
    │  • Generic CRUD Service   │
    │  • Route Factory          │
    │  • Schema Registry        │
    │  • Auth Configuration     │
    └─────────┬─────────────────┘
              │
    ┌─────────▼─────────────┐
    │    Runtime APIs       │
    │  /api/v1/auth/        │ 🔐 Authentication
    │  /api/v1/products/    │ 🌐 Public Read
    │  /api/v1/customers/   │ 🔒 Protected
    │  /api/v1/tasks/       │ 🔒 Protected
    └───────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/sidjain0503/server-p.git
cd server-p

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database settings

# Initialize database
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"

# Start development server
python -m app.main
```

### Access Your APIs

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root Info**: http://localhost:8000/

## 📁 Project Structure

```
server-p/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/                      # Core system components
│   │   ├── config.py              # Configuration management
│   │   └── database.py            # Database connection & setup
│   ├── meta_engine/               # Meta-Engine Core 🧠
│   │   ├── orchestrator.py        # Main meta-engine coordinator
│   │   ├── model_factory.py       # Dynamic SQLAlchemy model creation
│   │   ├── crud_service.py        # Generic CRUD operations
│   │   ├── route_factory.py       # Dynamic FastAPI route generation
│   │   └── demo.py                # Demo schema creation
│   ├── models/                    # Data models
│   │   ├── base.py                # Base model classes
│   │   └── schemas/               # Schema Definitions 📋
│   │       ├── registry.py        # Central schema registry
│   │       ├── product_schema.py  # E-commerce product schema
│   │       ├── customer_schema.py # CRM customer schema
│   │       └── task_schema.py     # Project management task schema
│   └── api/                       # API Routes
│       └── v1/                    # API Version 1
│           ├── __init__.py        # API router aggregation
│           ├── dependencies.py    # Common API dependencies
│           └── routes/            # Custom Business Logic Routes
│               ├── products.py    # Product custom endpoints
│               ├── customers.py   # Customer custom endpoints
│               └── tasks.py       # Task custom endpoints
├── requirements.txt               # Python dependencies
└── .env.example                  # Environment variables template
```

## 🎯 Core Features

### 1. **Schema-Driven Development**

Define your data structure once:

```python
# app/models/schemas/product_schema.py
product_schema = SchemaDefinition(
    name="Product",
    title="Product",
    description="E-commerce product with inventory management",
    fields=[
        FieldDefinition(
            name="name",
            type=FieldType.STRING,
            required=True,
            max_length=200,
            description="Product name"
        ),
        FieldDefinition(
            name="price",
            type=FieldType.DECIMAL,
            required=True,
            description="Product price in USD"
        ),
        FieldDefinition(
            name="stock_quantity",
            type=FieldType.INTEGER,
            required=True,
            min_value=0,
            description="Available stock quantity"
        ),
        # ... more fields
    ]
)
```

### 2. **Auto-Generated APIs**

Get complete REST APIs instantly:

```bash
# Authentication API
POST   /api/v1/auth/register       # User registration
POST   /api/v1/auth/login          # User login (get JWT token)
GET    /api/v1/auth/me             # Get current user info
POST   /api/v1/auth/logout         # User logout

# Products API (Public Read + Protected Write)
GET    /api/v1/products/           # 🌐 PUBLIC: List products with pagination
POST   /api/v1/products/           # 🔒 PROTECTED: Create new product
GET    /api/v1/products/{id}       # 🌐 PUBLIC: Get product by ID
PUT    /api/v1/products/{id}       # 🔒 PROTECTED: Update product
DELETE /api/v1/products/{id}       # 🔒 PROTECTED: Delete product
GET    /api/v1/products/count      # 🌐 PUBLIC: Count total products

# Customers API (Fully Protected)
GET    /api/v1/customers/          # 🔒 PROTECTED: List customers
POST   /api/v1/customers/          # 🔒 PROTECTED: Create new customer
GET    /api/v1/customers/{id}      # 🔒 PROTECTED: Get customer by ID
PUT    /api/v1/customers/{id}      # 🔒 PROTECTED: Update customer
DELETE /api/v1/customers/{id}      # 🔒 PROTECTED: Delete customer

# Same flexible pattern for any new schema!
```

### 3. **Custom Business Logic**

Extend with domain-specific endpoints (with flexible authentication):

```python
# app/api/v1/routes/products.py

# Protected custom endpoint - requires JWT token
@router.get("/{product_id}/analytics")
async def get_product_analytics(
    product_id: int,
    current_user: User = Depends(get_current_user)  # 🔒 PROTECTED
):
    """Custom endpoint for product analytics - requires authentication"""
    return {"revenue": 50000, "top_products": [...]}

# Public custom endpoint - no authentication required
@router.get("/category/{category}")
async def get_products_by_category(category: str):
    """Browse products by category - public access"""
    return {"products": [...]}

# Protected business operation
@router.post("/{product_id}/duplicate")
async def duplicate_product(
    product_id: int,
    current_user: User = Depends(get_current_user)  # 🔒 PROTECTED
):
    """Custom business logic for product duplication"""
    # Your custom logic here
```

### 4. **Type-Safe Validation**

All APIs include automatic validation:

```json
// POST /api/v1/products/
{
  "name": "Laptop Pro",
  "price": 1299.99,
  "stock_quantity": 50,
  "category": "Electronics",
  "description": "High-performance laptop"
}
```

## 🗄️ Database Integration

- **Async PostgreSQL** with SQLAlchemy 2.0
- **Automatic table creation** from schemas
- **Migration support** with Alembic
- **Connection pooling** for performance
- **Health monitoring** for reliability

## 🔧 Development Workflow

### Adding a New Domain

1. **Define Schema**:

```python
# app/models/schemas/order_schema.py
order_schema = SchemaDefinition(
    name="Order",
    fields=[
        FieldDefinition(name="customer_id", type=FieldType.INTEGER, required=True),
        FieldDefinition(name="total_amount", type=FieldType.DECIMAL, required=True),
        FieldDefinition(name="status", type=FieldType.STRING, required=True),
    ]
)
```

2. **Register Schema**:

```python
# app/models/schemas/registry.py
def register_all_schemas():
    meta_engine = get_meta_engine()
    meta_engine.register_schema(order_schema)  # Add this line
```

3. **Add Custom Routes** (Optional):

```python
# app/api/v1/routes/orders.py
@router.post("/{order_id}/ship")
async def ship_order(order_id: int):
    """Custom shipping logic"""
    pass
```

4. **Include Routes**:

```python
# app/api/v1/__init__.py
from app.api.v1.routes import orders

api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
```

**Result**: Complete Order API with CRUD + custom shipping endpoint! 🎉

## 📊 Current Domain APIs

### Products (E-commerce)

- Product catalog management
- Inventory tracking
- Category organization
- Analytics & reporting

### Customers (CRM)

- Customer relationship management
- Loyalty points system
- Status tracking
- Customer insights

### Tasks (Project Management)

- Task creation & management
- Priority & status workflows
- Deadline tracking
- Team collaboration

## 🛠️ Technology Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM with PostgreSQL
- **PostgreSQL**: Primary database
- **Pydantic v2**: Data validation & serialization
- **Asyncpg**: High-performance PostgreSQL driver
- **Uvicorn**: ASGI server for production

## 📚 API Documentation

Interactive documentation is automatically generated:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🚀 Production Deployment

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/inscribeverse
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inscribeverse
DB_USER=inscribeverse
DB_PASSWORD=your_secure_password

# Application
APP_NAME=InscribeVerse
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "app.main"]
```

```bash
# Build and run
docker build -t inscribeverse .
docker run -p 8000:8000 inscribeverse
```

## 🧪 Testing Your APIs

### Authentication Flow

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "display_name": "Test User"
  }'

# 2. Login to get JWT token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }' | jq -r '.access_token')

# 3. Use token for protected endpoints
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/auth/me"
```

### Public vs Protected Routes

```bash
# ✅ Public routes (no token required)
curl "http://localhost:8000/api/v1/products/"
curl "http://localhost:8000/api/v1/products/category/electronics"

# ❌ Protected routes (token required)
curl "http://localhost:8000/api/v1/customers/"  # Returns 403 Forbidden

# ✅ Protected routes (with token)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/customers/"
```

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Enter test data and execute
4. See real-time results


## 🔐 Authentication System

InscribeVerse includes a complete **JWT-based authentication system** with flexible route protection:

### 🎛️ **Flexible Authentication Control**

**Schema-Level Configuration:**

```python
# Public product catalog
auth_config={
    "read_public": True,        # Anyone can browse products
    "write_protected": True,    # Only authenticated users can modify
}

# Private customer data
auth_config={
    "require_auth": True,       # All operations require authentication
    "read_public": False,       # Customer data is private
}
```

**Route-Level Configuration:**

```python
# Protected custom route
@router.get("/analytics")
async def analytics(current_user: User = Depends(get_current_user)):
    # Requires JWT token

# Public custom route
@router.get("/public-data")
async def public_data():
    # No authentication required
```

### 🔑 **Authentication Features**

- **User Registration & Login** with bcrypt password hashing
- **JWT Token Generation** with configurable expiration
- **Token Validation** with automatic user extraction
- **Role-Based Access Control (RBAC)** with permissions
- **OAuth-Ready Architecture** (Google, LinkedIn, etc.)
- **Audit Trail Integration** (created_by, updated_by tracking)
