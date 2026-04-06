# 🧠 DossierOS — End-to-End SaaS for Dossier Management

<img width="1880" height="839" alt="image" src="https://github.com/user-attachments/assets/c24e9405-6cb9-4723-b31a-7fdaa30eaae1" />


> Fullstack SaaS system with FastAPI backend, Supabase JWT authentication, custom auth middleware, AI-powered workflows, and decoupled frontend. Includes interactive demo UI.

🌐 Demo UI: https://dossieros.lovable.app/

---

## 🎯 What is this?

DossierOS is a **fullstack SaaS system** designed to manage structured technical/regulatory documentation (dossiers), inspired by real-world workflows in regulated industries (e.g., pharma, compliance).


---

## 🏗️ System Architecture

flowchart LR
A[Frontend UI] -->|HTTP + JWT| B[FastAPI Backend]
B --> C[Auth Middleware]
C --> D[Supabase JWT Verification]
B --> E[Business Logic Layer]
E --> F[Dossier Management API]

## 🏗️ Key Characteristics

- API-first design  
- Stateless backend (JWT-based authentication)  
- Middleware-driven security layer  
- Decoupled frontend (replaceable and scalable)  
- AI-ready architecture  

---

## ⚙️ Tech Stack

### Backend
- FastAPI  
- Python  
- Custom Middleware (JWT validation)  
- Modular routing (API structure)  

### Auth & Security
- Supabase Auth  
- Server-side JWT verification  
- Bearer token flow  

### Frontend
- Decoupled UI (served independently)  
- API-driven interaction  
- Interactive demo via Lovable  

### AI Layer
- Designed for integration with LLMs / AI services  
- Supports workflow automation and intelligent features  

---

## 🔐 Authentication Flow

1. User logs in via Supabase  
2. Supabase returns a JWT  
3. Frontend sends the JWT in the `Authorization` header  
4. FastAPI middleware:
   - Extracts the token  
   - Verifies the JWT  
   - Injects user context into the request  
5. Protected endpoints consume the user context  

---

## 📁 Core Features

### Dossier Management
- Create dossiers  
- Structured data handling  
- Editable content  
- API-driven workflow

<img width="1870" height="784" alt="image" src="https://github.com/user-attachments/assets/e076925d-c4aa-4285-90e5-3753cf7d9720" />

<img width="1906" height="867" alt="image" src="https://github.com/user-attachments/assets/ee540d60-b7d7-497f-87f3-6ae223c81395" />



### API Design
- Modular endpoints  
- Scalable routing  
- Clear separation of concerns  

### Security
- JWT-based authentication  
- Middleware validation layer  
- Stateless request handling  

### Frontend 
- Full UX flows (login, dashboard, editor)  
- Mocked state for product simulation  
- Built for presentation and usability testing  

<img width="1910" height="862" alt="image" src="https://github.com/user-attachments/assets/3c841452-3bc1-4fc7-81c7-56adddd0bdba" />



---

## 🤖 AI Integration (Design)

The system is designed to support:

- AI-assisted content generation  
- Document structuring  
- Smart suggestions and automation  

> Currently abstracted and ready for integration with LLM-based services.

<img width="1893" height="822" alt="image" src="https://github.com/user-attachments/assets/55e81cb9-9996-46cb-bf4a-0142e02f7094" />

---

## 🎯 Engineering Highlights

- Clean separation between authentication, middleware, and business logic  
- Real-world JWT validation flow (not mocked)  
- Scalable architecture ready for:
  - Database integration  
  - Role-based access control (RBAC)  
  - AI services  
- Fully decoupled frontend from backend  

---

## 📸 Demo UI

The interactive UI is built using Lovable and simulates the full product experience:

👉 https://dossieros.lovable.app/

This layer focuses on:

- UX/UI quality  
- Product flows  
- Usability  

---

## 🚧 Trade-offs & Decisions

- Frontend uses mock state → faster prototyping and UX validation  
- Backend is fully implemented → demonstrates production-ready architecture  
- AI layer is abstracted → designed for future extensibility  


---

## 👨‍💻 Author

**Federico**  
Data Science | AI Engineer | ML Engineer | Fullstack  
