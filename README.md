# InnoVote - Innovation Fest Voting Platform

InnoVote is a comprehensive web-based voting platform designed for Innovation Fest events. It allows exhibitors to register their projects and visitors to vote and provide feedback in a fair and transparent manner.

## 🚀 Features

### Core Features

- **Project Registration**: Exhibitors can register their projects with detailed information
- **One-Person-One-Vote**: Enforced through session-based tracking and device fingerprinting
- **Feedback System**: Visitors can leave comments and ratings on any project
- **Admin Panel**: Real-time statistics and project approval management
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### Project Management

- Project approval workflow for quality control
- Categorization and tagging system
- Rich project information including GitHub links, demos, and media
- Team member management

### Voting System

- Session-based visitor tracking
- Device fingerprinting for enhanced security
- Vote confirmation with project preview
- Real-time vote counting

### Admin Features

- Live statistics dashboard
- Project approval/disapproval
- Feedback management
- Comprehensive project analytics

## 🛠️ Technology Stack

### Backend

- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (development) / PostgreSQL (production)
- **Flask-CORS** - Cross-origin resource sharing
- **python-dotenv** - Environment variable management

### Frontend

- **React** - JavaScript library for building user interfaces
- **CSS3** - Modern styling with gradients and animations
- **Responsive Design** - Mobile-first approach

## 📦 Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:

```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 🎯 Usage

### For Exhibitors

1. Click "Register Project" to submit your project
2. Fill in project details including title, description, team info
3. Wait for admin approval
4. Your project will appear in the voting list once approved

### For Visitors

1. Browse the list of approved projects
2. Use search and filter options to find projects of interest
3. Vote for your favorite project (one vote per person)
4. Leave feedback on any project you find interesting

### For Admins

1. Click "Admin Panel" to access administrative features
2. Review and approve/disapprove submitted projects
3. Monitor real-time voting statistics
4. Review feedback from visitors

## 🌐 API Endpoints

### Project Management

- `GET /api/projects` - Get all projects with filtering
- `POST /api/projects` - Register new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project

### Voting

- `POST /api/vote` - Cast a vote
- `GET /api/visitor-status` - Check voting status

### Feedback

- `POST /api/feedback` - Submit feedback

### Admin

- `GET /api/admin/stats` - Get comprehensive statistics
- `POST /api/admin/projects/{id}/approve` - Approve project
- `POST /api/admin/projects/{id}/disapprove` - Disapprove project

## 🚀 Quick Start

Both servers are now running:

- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:3000

Visit http://localhost:3000 to start using the application!

---

**Built with ❤️ for Innovation Fest**
