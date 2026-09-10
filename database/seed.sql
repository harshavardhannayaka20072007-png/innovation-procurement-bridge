-- Seed Data for Innovation Procurement Bridge (SIH 2026)
-- ===========================================================
-- The seed accounts are deliberately disabled. Provision strong, unique
-- credentials with scripts/reset_passwords.py before allowing any sign-in.
-- ===========================================================

-- Insert Users
INSERT INTO users (username, email, password_hash, role, department, company_name) VALUES
('gov_admin',       'gov@maharashtra.gov.in',       '!', 'government', 'Urban Development Dept', NULL),
('techsolve',       'techsolve@startup.in',         '!', 'startup', NULL, 'TechSolve Mobility Labs'),
('greenwater',      'greenwater@startup.in',        '!', 'startup', NULL, 'GreenWater AI Solutions'),
('evaluator_tech',  'evaluator@maharashtra.gov.in', '!', 'evaluator', 'State Technical Evaluation Committee', NULL),
('sys_admin',       'admin@bridge.gov.in',          '!', 'admin', 'Maharashtra State Innovation Cell', NULL);

-- Insert Challenges
INSERT INTO challenges (title, department, description, requirements, deadline, status, created_by) VALUES
('AI Smart Traffic Signal Control System for Municipal Junctions', 'Urban Development Dept', 'Deploy computer vision AI at key city intersections to reduce bottleneck congestion during peak hours.', 'Edge-compatible camera processing, low-latency API dashboard, integration with existing traffic light controllers.', '2026-10-30', 'Published', 1),
('IoT Sensor Network for Rural Water Quality Monitoring', 'Water Supply & Sanitation Dept', 'Real-time telemetry sensors to monitor TDS, pH, and turbidity in rural water reservoirs across Konkan region.', 'Solar-powered sensors, GSM connectivity, automated alert system for contamination detection.', '2026-11-15', 'Published', 1),
('Automated Public Grievance Classification & Resolution Dashboard', 'General Administration Dept', 'NLP-driven classification of citizen complaints with automated routing to regional officers.', 'Multi-lingual support (Marathi & English), automated SLA escalation alerts, analytics portal.', '2026-12-01', 'Draft', 1);

-- Insert Applications
INSERT INTO applications (challenge_id, startup_id, startup_name, challenge_title, description, proposal, status, eligibility_score, technology_score, feasibility_score, timeline_score, experience_score, total_score) VALUES
(1, 2, 'TechSolve Mobility Labs', 'AI Smart Traffic Signal Control System for Municipal Junctions', 'Edge AI traffic light optimization platform proven to reduce congestion by 35%.', 'Our solution utilizes YOLOv8-based computer vision deployed on edge hardware to dynamically switch signals.', 'Shortlisted', 18, 19, 17, 16, 18, 88),
(2, 3, 'GreenWater AI Solutions', 'IoT Sensor Network for Rural Water Quality Monitoring', 'Ultra-low-power IoT water quality probes with satellite/cellular failover.', 'We offer patent-pending optical sensors with self-cleaning wiper mechanisms and 5-year battery life.', 'Approved for Pilot', 19, 19, 18, 18, 18, 92);

-- Insert Evaluations
INSERT INTO evaluations (application_id, evaluator_id, eligibility_score, technology_score, feasibility_score, timeline_score, experience_score, total_score, comments) VALUES
(1, 4, 18, 19, 17, 16, 18, 88, 'Strong computer vision capability. Recommended for field benchmarking.'),
(2, 4, 19, 19, 18, 18, 18, 92, 'Excellent hardware readiness and low maintenance design. Ideal candidate for pilot deployment.');

-- Insert Pilot
INSERT INTO pilots (application_id, challenge_id, startup_id, startup_name, challenge_title, status, milestone_progress, start_date, end_date) VALUES
(2, 2, 3, 'GreenWater AI Solutions', 'IoT Sensor Network for Rural Water Quality Monitoring', 'Active', 65, '2026-08-01', '2026-11-30');

-- Insert Milestones
INSERT INTO milestones (pilot_id, title, description, due_date, status, evidence_file) VALUES
(1, 'Phase 1: Sensor Hardware Deployment', 'Deploy 25 IoT nodes in designated test villages in Konkan region.', '2026-08-25', 'Approved', 'milestone_1_report.pdf'),
(1, 'Phase 2: Real-time Telemetry Dashboard Integration', 'Connect field sensors to Government Cloud dashboard with SLA alerts.', '2026-09-30', 'Submitted', 'dashboard_integration_proof.pdf'),
(1, 'Phase 3: 60-Day Field Accuracy Verification', 'Demonstrate 98%+ measurement accuracy against lab water samples.', '2026-11-15', 'Pending', NULL);

-- Insert Performance Records
INSERT INTO performance (pilot_id, kpi_name, target_value, actual_value, unit, remarks) VALUES
(1, 'Sensor Telemetry Uptime', '99.0', '99.4', '%', 'Operating reliably across all 25 field stations.'),
(1, 'Contamination Alert Latency', '< 5', '2.3', 'Minutes', 'Alert notifications triggered instantly upon threshold breach.'),
(1, 'Measurement Accuracy vs Lab Samples', '95.0', '97.8', '%', 'Verified by MPCB certified laboratory testing.');
