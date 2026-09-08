CREATE DATABASE IF NOT EXISTS innovation_procurement;
USE innovation_procurement;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('government', 'startup', 'evaluator', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS startups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    registration_no VARCHAR(50) UNIQUE,
    domain VARCHAR(100),
    readiness_level INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    problem_statement TEXT NOT NULL,
    budget DECIMAL(12,2),
    deadline DATE NOT NULL,
    status ENUM('draft', 'published', 'closed') DEFAULT 'published',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    startup_id INT NOT NULL,
    solution_summary TEXT NOT NULL,
    technical_stack TEXT,
    proposed_timeline_months INT,
    status ENUM('submitted', 'under_review', 'shortlisted', 'rejected', 'selected') DEFAULT 'submitted',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id),
    FOREIGN KEY (startup_id) REFERENCES startups(id)
);

CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL UNIQUE,
    eligibility_score DECIMAL(5,2) DEFAULT 0.00,
    technology_score DECIMAL(5,2) DEFAULT 0.00,
    feasibility_score DECIMAL(5,2) DEFAULT 0.00,
    total_score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    evaluator_id INT NOT NULL,
    feedback TEXT,
    recommendation ENUM('approve', 'reject', 'needs_revision'),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (evaluator_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS pilots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    start_date DATE,
    end_date DATE,
    status ENUM('active', 'completed', 'halted') DEFAULT 'active',
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

CREATE TABLE IF NOT EXISTS milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pilot_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    due_date DATE,
    status ENUM('pending', 'submitted', 'verified') DEFAULT 'pending',
    FOREIGN KEY (pilot_id) REFERENCES pilots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    milestone_id INT NOT NULL,
    file_url VARCHAR(255) NOT NULL,
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kpis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pilot_id INT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    target_value VARCHAR(50),
    actual_value VARCHAR(50),
    status ENUM('met', 'unmet', 'in_progress') DEFAULT 'in_progress',
    FOREIGN KEY (pilot_id) REFERENCES pilots(id)
);

CREATE TABLE IF NOT EXISTS decisions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pilot_id INT NOT NULL UNIQUE,
    final_decision ENUM('SCALE', 'IMPROVE', 'STOP') NOT NULL,
    remarks TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pilot_id) REFERENCES pilots(id)
);