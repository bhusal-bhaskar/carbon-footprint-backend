# 🌿 Carbon Footprint Backend API

> A RESTful API for tracking and analysing personal carbon emissions — built with Flask, MongoDB and JWT authentication.

![Python](https://img.shields.io/badge/Python-3.9-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-REST_API-black?style=flat-square&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?style=flat-square&logo=mongodb)
![JWT](https://img.shields.io/badge/JWT-Authentication-orange?style=flat-square)

---

## 📖 Overview

Carbon Footprint Backend API is a Flask REST API that powers the Carbon Footprint Tracker application. It provides endpoints for user authentication, activity management, sources sub-document management and analytics using MongoDB aggregation pipelines.

---

## ✨ Features

- 🔐 JWT authentication with Basic Auth login
- 👑 Role-based access control — admin and user roles
- 📋 Full CRUD for carbon footprint activities
- 🔗 Sources sub-document management
- 🔍 Query string filtering by type, emission and date range
- 📊 4 MongoDB aggregation pipeline analytics endpoints
- ✅ Input validation and error handling
- 🔄 JWT refresh token support
- 🌉 Auth0 bridge endpoint for frontend integration

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask, Python 3.9 |
| Database | MongoDB |
| Authentication | Flask-JWT-Extended + Flask-HTTPAuth |
| Password Hashing | bcrypt |
| CORS | Flask-CORS |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- MongoDB installed locally
- pip

### 1. Clone the repository

```bash
git clone https://github.com/bhusal-bhaskar/carbon-footprint-backend.git
cd carbon-footprint-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start MongoDB

```bash
mongod --dbpath ~/data/db
```

### 5. Import sample data

```bash
mongoimport --db carbonDB --collection activities --file data/data/sample_data.json --jsonArray
mongoimport --db carbonDB --collection users --file users.json
```

### 6. Start the API

```bash
python app.py
```

API runs on: `http://127.0.0.1:5001`

---

## 🔑 Test Credentials

| Email | Password | Role |
|---|---|---|
| test@email.com | password123 | Admin |
| normal@email.com | password123 | User |

---

## 📁 Project Structure

```
carbon-footprint-backend/
├── app.py
├── routes/
│   ├── auth_routes.py
│   ├── activity_routes.py
│   └── analytics_routes.py
├── utils/
│   ├── validators.py
│   └── emission_calculator.py
├── data/
│   └── sample_data.json
├── users.json
└── requirements.txt
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /users/login | Basic Auth login — returns JWT | Basic Auth |
| POST | /users/register | Register new user account | Public |
| POST | /users/auth0-login | Auth0 bridge — login by email | Public |
| POST | /users/refresh | Refresh JWT access token | JWT Refresh |

### User Management
| Method | Endpoint | Description | Role |
|---|---|---|---|
| GET | /users | Get all users | Admin |
| GET | /users/:id | Get single user | Admin / Own |
| PUT | /users/:id | Update user details | Admin / Own |
| DELETE | /users/:id | Delete user account | Admin / Own |

### Activities
| Method | Endpoint | Description | Role |
|---|---|---|---|
| GET | /activities | Get all activities | User / Admin |
| GET | /activities/:id | Get single activity | User / Admin |
| POST | /activities | Create new activity | User / Admin |
| PUT | /activities/:id | Update activity | User / Admin |
| DELETE | /activities/:id | Delete activity | User / Admin |
| GET | /activities/filter/type | Filter by type | User / Admin |
| GET | /activities/filter/emission | Filter by emission | User / Admin |
| GET | /activities/filter/date | Filter by date range | User / Admin |

### Sources Sub-Documents
| Method | Endpoint | Description | Role |
|---|---|---|---|
| POST | /activities/:id/sources | Add source to activity | User / Admin |
| PUT | /activities/:id/sources/:sid | Update source | User / Admin |
| DELETE | /activities/:id/sources/:sid | Delete source | User / Admin |

### Analytics
| Method | Endpoint | Description | Role |
|---|---|---|---|
| GET | /analytics/total-emissions | Total emissions and count | User / Admin |
| GET | /analytics/emissions-by-type | Breakdown by activity type | User / Admin |
| GET | /analytics/monthly-trends | Monthly emission trends | User / Admin |
| GET | /analytics/highest-activities | Ranked by average emission | User / Admin |

---

## 🔐 Authentication

**HTTP Basic Authentication** — used for the initial login endpoint. The email and password are Base64 encoded and sent in the Authorization header.

**JWT Bearer Token** — returned after successful login and used for all subsequent requests. Sent in the Authorization header as `Bearer <token>`.

**Role-Based Access Control** — admin users can access all data across all users. Regular users can only access their own data.

---

## 📊 Dataset

- 20 activities — ACT-001 to ACT-020
- 5 users including admin and regular accounts
- Each activity has 2 sources sub-documents
- Activities cover Transport, Energy and Consumption categories

---

## 🔗 Related Repository

Frontend application built with Angular 21 and Auth0:

[com661-carbon-footprint-tracker-Frontend](https://github.com/bhusal-bhaskar/com661-carbon-footprint-tracker-Frontend)

---

## 📄 License

This project was built for educational purposes.
