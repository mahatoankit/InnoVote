

## 🗳️ Project Title: **Fair & Secure Voting Management System for College Exhibition**

**Built with Django + NeonDB**

---

### 🧠 **Project Concept (Core Idea)**

Develop a secure, fair, and intuitive **voting system** for a college exhibition, where multiple teams present their projects and visitors are allowed to vote **only once** for their favorite. Additionally, visitors can leave **optional feedback or recommendations** for any project — including those they don’t vote for.

The goal is to maximize **audience engagement**, ensure **vote integrity**, and provide **real-time control and transparency** for organizers.

---

### 🏗️ **How the System Works**

#### 1. **Admin Panel (Authenticated)**

* Built with Django admin or a custom frontend
* Admin can:

  * Add/edit/delete **projects**
  * Add/manage **project members**
  * Generate and persist a list of unique **voting IDs** (short, random, and stored securely)
  * Control voting lifecycle:

    * **Start/Stop voting**
    * **Show/Hide results**
  * View vote analytics and feedback submissions
  * Download or audit vote logs for transparency

#### 2. **Voting Dashboard (Public User Interface)**

* Visitors access a **web-based interface** (responsive design)
* They can:

  * **Browse all projects** with descriptions/media
  * **Vote** once using a valid, unused **voting ID** (printed on entry card)
  * Submit **optional feedback/recommendations** for any project

#### 3. **Voting ID System**

* At entry, each visitor is handed a **card with a 5-character voting ID** (random mix of A–Z, a–z, 0–9)
* Voting ID:

  * Is auto-generated and stored in **NeonDB**
  * Has a `used: Boolean` flag to prevent reuse
  * Is persisted to avoid regeneration or duplication
* Example of vote IDs: `A7bT2`, `z9Xc1`

#### 4. **Vote Flow Enforcement**

* Visitors can vote **only once** using their `voting_id`
* System checks:

  * If ID exists
  * If it’s unused
* If valid, vote is saved and the `voting_id` marked as **used**
* Feedbacks are unrestricted and can be left anonymously or linked to projects (optional)

#### 5. **Result Visibility Control**

* Voting results are **hidden from the public during voting phase**
* Only visible when the **admin explicitly enables** them via the admin panel

---

### 💾 **Database (NeonDB - PostgreSQL)**

#### Tables:

* `projects` — title, description, media, team members
* `members` — linked to projects
* `votes` — project\_id, vote\_id (foreign key), timestamp
* `vote_ids` — code (5-char string), used (boolean), created\_at
* `feedbacks` — project\_id, feedback\_text, (optional voter info or timestamp)
* `admin_logs` — timestamped admin activities for audit

---

### 🎨 **UI/UX Design**

* Use `#C12A37` as the **primary color** (college branding)
* Clean, intuitive UI optimized for:

  * Touch-screen kiosks
  * Tablets and mobile
* Touch-friendly components for voting and browsing

---

### ✨ Optional Features

* Print **QR codes** on entry cards to auto-fill vote ID field
* Categorize projects (e.g., tech, environment, health)
* Role-based admin access (e.g., judges, moderators)
* Analytics dashboard (most voted, votes per hour, feedback trends)
* Multi-language support

---

### ✅ Summary of Key Advantages

| Feature                        | Description                                            |
| ------------------------------ | ------------------------------------------------------ |
| **Fair Voting**                | One person, one vote using unique short code           |
| **Secure & Private**           | No personal info required; no repeat voting            |
| **Admin Controlled**           | Full power to start/stop voting and control visibility |
| **Feedback Friendly**          | Visitors can leave insights without voting             |
| **Real-time Analytics**        | Admins can monitor activity instantly                  |
| **Persistence & Auditability** | Every action is stored securely in NeonDB              |

---

### ⚙️ **Tech Stack**

* **Backend:** Django (with Django Admin for internal control)
* **Frontend:** Django Templates or React (optional)
* **Database:** NeonDB (PostgreSQL serverless)
* **Hosting:** Railway, Vercel, or traditional VPS (your choice)
* **QR & Code Generator:** Python logic using `random.choices()` or `secrets`

---

### ✅ Deliverables

* Complete Django backend with admin panel
* NeonDB-integrated models for votes, feedbacks, and projects
* Public-facing vote/feedback interface
* Code generation utility (one-time pre-vote IDs)
* Result display page (only visible when toggled by admin)
* Deployment-ready setup

---
