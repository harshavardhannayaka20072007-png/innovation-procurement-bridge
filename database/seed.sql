USE innovation_procurement;

INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Admin Officer', 'gov@nexora.gov.in', '$2b$12$eImiTXuWVxfM37uY4JANjO5E/f/xWJ.63X58iI6.eG3K1.Xk5fV2G', 'government'),
(2, 'Tech Startup Inc', 'contact@techstartup.com', '$2b$12$eImiTXuWVxfM37uY4JANjO5E/f/xWJ.63X58iI6.eG3K1.Xk5fV2G', 'startup'),
(3, 'Dr. Evaluator', 'evaluator@nexora.gov.in', '$2b$12$eImiTXuWVxfM37uY4JANjO5E/f/xWJ.63X58iI6.eG3K1.Xk5fV2G', 'evaluator');

INSERT INTO departments (id, name, code) VALUES
(1, 'Ministry of Urban Development', 'MUD'),
(2, 'Department of Water Resources', 'DWR');

INSERT INTO startups (id, user_id, company_name, registration_no, domain, readiness_level) VALUES
(1, 2, 'EcoTech Solutions', 'REG-2026-001', 'Smart Infrastructure', 7);

INSERT INTO challenges (id, department_id, title, description, problem_statement, budget, deadline, status) VALUES
(1, 1, 'AI Traffic Optimization', 'Smart traffic routing system', 'Optimize urban signal timings in real-time.', 5000000.00, '2026-10-30', 'published');