-- Database Schema for Innovation Procurement Bridge (SIH 2026)

DROP TABLE IF EXISTS performance;
DROP TABLE IF EXISTS milestones;
DROP TABLE IF EXISTS pilots;
DROP TABLE IF EXISTS evaluations;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK(role IN ('admin', 'government', 'startup', 'evaluator')),
    department VARCHAR(150),
    company_name VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE challenges (
    challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft' CHECK(status IN ('Draft', 'Published', 'Closed')),
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    startup_id INTEGER NOT NULL,
    startup_name VARCHAR(150) NOT NULL,
    challenge_title VARCHAR(255) NOT NULL,
    description TEXT,
    proposal TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'Under Review', 'Shortlisted', 'Approved for Pilot', 'Rejected')),
    eligibility_score INTEGER,
    technology_score INTEGER,
    feasibility_score INTEGER,
    timeline_score INTEGER,
    experience_score INTEGER,
    total_score INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id),
    FOREIGN KEY (startup_id) REFERENCES users(user_id)
);

CREATE TABLE evaluations (
    evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    evaluator_id INTEGER NOT NULL,
    eligibility_score INTEGER NOT NULL,
    technology_score INTEGER NOT NULL,
    feasibility_score INTEGER NOT NULL,
    timeline_score INTEGER NOT NULL,
    experience_score INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(application_id),
    FOREIGN KEY (evaluator_id) REFERENCES users(user_id)
);

CREATE TABLE pilots (
    pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    startup_id INTEGER NOT NULL,
    startup_name VARCHAR(150) NOT NULL,
    challenge_title VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Near Completion', 'Completed', 'Stopped')),
    milestone_progress INTEGER DEFAULT 0,
    start_date DATE DEFAULT (DATE('now')),
    end_date DATE,
    FOREIGN KEY (application_id) REFERENCES applications(application_id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id),
    FOREIGN KEY (startup_id) REFERENCES users(user_id)
);

CREATE TABLE milestones (
    milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pilot_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Submitted', 'Approved', 'Rejected')),
    evidence_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id)
);

CREATE TABLE performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pilot_id INTEGER NOT NULL,
    kpi_name VARCHAR(255) NOT NULL,
    target_value VARCHAR(100) NOT NULL,
    actual_value VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id)
);
