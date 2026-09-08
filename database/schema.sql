CREATE TABLE challenges (
    challenge_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    department VARCHAR(255),
    requirements TEXT,
    deadline DATE,
    status VARCHAR(50) DEFAULT 'Draft'
);
CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    startup_id INT NOT NULL,
    solution TEXT,
    technology TEXT,
    timeline VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Submitted',
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id)
);
CREATE TABLE scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    eligibility_score INT DEFAULT 0,
    technology_score INT DEFAULT 0,
    feasibility_score INT DEFAULT 0,
    timeline_score INT DEFAULT 0,
    experience_score INT DEFAULT 0,
    total_score INT DEFAULT 0,
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);
CREATE TABLE pilots (
    pilot_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    objective TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Planned',
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);
CREATE TABLE milestones (
    milestone_id INT AUTO_INCREMENT PRIMARY KEY,
    pilot_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id)
);
CREATE TABLE evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    milestone_id INT NOT NULL,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    description TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Submitted',
    FOREIGN KEY (milestone_id) REFERENCES milestones(milestone_id)
);
CREATE TABLE performance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    pilot_id INT NOT NULL,
    kpi_name VARCHAR(255) NOT NULL,
    target_value DECIMAL(10,2),
    actual_value DECIMAL(10,2),
    unit VARCHAR(100),
    remarks TEXT,
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id)
);
CREATE TABLE decisions (
    decision_id INT AUTO_INCREMENT PRIMARY KEY,
    pilot_id INT NOT NULL,
    decision VARCHAR(20) NOT NULL,
    remarks TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id)
);
