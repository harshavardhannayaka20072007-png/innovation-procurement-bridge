import datetime
from backend.db import query_db

def build_user_context(role, user_id, user_info=None):
    """
    Builds structured, role-authorized context from the NEXORA database.
    Ensures users only receive data relevant to their role and permissions.
    """
    if not role:
        return "User is not logged in. Information is unavailable."

    context_parts = []
    today_str = datetime.date.today().isoformat()

    context_parts.append(f"CURRENT SYSTEM DATE: {today_str}")
    context_parts.append(f"USER ROLE: {role.upper()}")
    if user_info:
        if user_info.get('username'):
            context_parts.append(f"USERNAME: {user_info.get('username')}")
        if user_info.get('department'):
            context_parts.append(f"DEPARTMENT: {user_info.get('department')}")
        if user_info.get('company_name'):
            context_parts.append(f"STARTUP COMPANY NAME: {user_info.get('company_name')}")

    if role == 'government':
        context_parts.append(get_government_context())
    elif role == 'startup':
        context_parts.append(get_startup_context(user_id, user_info))
    elif role == 'evaluator':
        context_parts.append(get_evaluator_context(user_id))
    elif role == 'admin':
        context_parts.append(get_admin_context())
    else:
        context_parts.append("Unknown user role.")

    return "\n\n".join(context_parts)

def get_government_context():
    lines = ["=== GOVERNMENT OFFICIAL CONTEXT ==="]

    # 1. Challenges
    challenges = query_db("SELECT * FROM challenges ORDER BY created_at DESC")
    lines.append(f"\n--- CHALLENGES ({len(challenges)} total) ---")
    if challenges:
        for c in challenges:
            lines.append(
                f"- [ID: {c['challenge_id']}] Title: '{c['title']}' | Department: {c['department']} | "
                f"Status: {c['status']} | Deadline: {c['deadline']} | Description: {c['description']} | Requirements: {c['requirements']}"
            )
    else:
        lines.append("No challenges available in the database.")

    # 2. Applications & Readiness Scores
    apps = query_db("""
        SELECT a.*, c.title as challenge_name 
        FROM applications a 
        LEFT JOIN challenges c ON a.challenge_id = c.challenge_id
        ORDER BY a.total_score DESC, a.submitted_at DESC
    """)
    lines.append(f"\n--- APPLICATIONS & STARTUP READINESS SCORES ({len(apps)} total) ---")
    if apps:
        for app in apps:
            score_str = (
                f"Total Score: {app['total_score']} (Eligibility: {app['eligibility_score']}/20, "
                f"Technology: {app['technology_score']}/20, Feasibility: {app['feasibility_score']}/20, "
                f"Timeline: {app['timeline_score']}/20, Experience: {app['experience_score']}/20)"
                if app['total_score'] is not None else "Evaluation Pending / Unscored"
            )
            lines.append(
                f"- [App ID: {app['application_id']}] Startup: '{app['startup_name']}' | Challenge: '{app['challenge_title']}' | "
                f"Status: {app['status']} | {score_str} | Proposal Summary: {app['proposal']}"
            )
    else:
        lines.append("No applications submitted yet.")

    # 3. Evaluations
    evals = query_db("""
        SELECT e.*, u.username as evaluator_name, a.startup_name, a.challenge_title
        FROM evaluations e
        JOIN users u ON e.evaluator_id = u.user_id
        JOIN applications a ON e.application_id = a.application_id
    """)
    lines.append(f"\n--- DETAILED EVALUATIONS ({len(evals)} total) ---")
    if evals:
        for ev in evals:
            lines.append(
                f"- Application #{ev['application_id']} ({ev['startup_name']} for '{ev['challenge_title']}'): "
                f"Evaluator: {ev['evaluator_name']} | Total Score: {ev['total_score']} | Comments: {ev['comments']}"
            )
    else:
        lines.append("No evaluations recorded yet.")

    # 4. Pilots
    pilots = query_db("SELECT * FROM pilots ORDER BY start_date DESC")
    lines.append(f"\n--- PILOTS & DEPLOYMENTS ({len(pilots)} total) ---")
    if pilots:
        for p in pilots:
            lines.append(
                f"- [Pilot ID: {p['pilot_id']}] Startup: '{p['startup_name']}' | Challenge: '{p['challenge_title']}' | "
                f"Status: {p['status']} | Progress: {p['milestone_progress']}% | Timeline: {p['start_date']} to {p['end_date']}"
            )
    else:
        lines.append("No active or past pilots found.")

    # 5. Milestones
    milestones = query_db("""
        SELECT m.*, p.startup_name, p.challenge_title
        FROM milestones m
        JOIN pilots p ON m.pilot_id = p.pilot_id
        ORDER BY m.due_date ASC
    """)
    lines.append(f"\n--- PILOT MILESTONES ({len(milestones)} total) ---")
    if milestones:
        today_str = datetime.date.today().isoformat()
        for m in milestones:
            is_overdue = "YES (OVERDUE)" if (m['due_date'] and m['due_date'] < today_str and m['status'] != 'Approved') else "No"
            lines.append(
                f"- [Milestone ID: {m['milestone_id']}] Pilot ID {m['pilot_id']} ({m['startup_name']}): "
                f"Title: '{m['title']}' | Status: {m['status']} | Due Date: {m['due_date']} | "
                f"Overdue: {is_overdue} | Evidence File: {m['evidence_file'] or 'None Uploaded'}"
            )
    else:
        lines.append("No milestones recorded.")

    # 6. Performance KPIs
    kpis = query_db("""
        SELECT k.*, p.startup_name, p.challenge_title
        FROM performance k
        JOIN pilots p ON k.pilot_id = p.pilot_id
    """)
    lines.append(f"\n--- PILOT PERFORMANCE & KPIS ({len(kpis)} total) ---")
    if kpis:
        for k in kpis:
            lines.append(
                f"- Pilot ID {k['pilot_id']} ({k['startup_name']}): KPI: '{k['kpi_name']}' | "
                f"Target: {k['target_value']} {k['unit']} | Actual: {k['actual_value']} {k['unit']} | Remarks: {k['remarks']}"
            )
    else:
        lines.append("No KPI performance metrics recorded.")

    return "\n".join(lines)


def get_startup_context(user_id, user_info=None):
    lines = ["=== STARTUP USER CONTEXT ==="]
    company_name = user_info.get('company_name') if user_info else None

    # 1. Available Open Challenges
    challenges = query_db("SELECT * FROM challenges WHERE status = 'Published' ORDER BY deadline ASC")
    lines.append(f"\n--- OPEN CHALLENGES AVAILABLE TO APPLY ({len(challenges)} total) ---")
    if challenges:
        for c in challenges:
            lines.append(
                f"- [Challenge ID: {c['challenge_id']}] '{c['title']}' | Dept: {c['department']} | "
                f"Deadline: {c['deadline']} | Requirements: {c['requirements']}"
            )
    else:
        lines.append("No open challenges available at the moment.")

    # 2. Startup's Own Applications
    my_apps = query_db("""
        SELECT * FROM applications 
        WHERE startup_id = ? OR (startup_name = ? AND ? IS NOT NULL)
        ORDER BY submitted_at DESC
    """, (user_id, company_name, company_name))
    
    lines.append(f"\n--- MY SUBMITTED APPLICATIONS ({len(my_apps)} total) ---")
    if my_apps:
        for app in my_apps:
            score_breakdown = (
                f"Total Score: {app['total_score']}/100 [Eligibility: {app['eligibility_score']}/20, "
                f"Tech: {app['technology_score']}/20, Feasibility: {app['feasibility_score']}/20, "
                f"Timeline: {app['timeline_score']}/20, Experience: {app['experience_score']}/20]"
                if app['total_score'] is not None else "Scoring Pending"
            )
            lines.append(
                f"- [App ID: {app['application_id']}] Challenge: '{app['challenge_title']}' | "
                f"Status: {app['status']} | Submitted: {app['submitted_at']} | Readiness Score: {score_breakdown}"
            )
    else:
        lines.append("You have not submitted any applications yet.")

    # 3. Startup's Own Pilots
    my_pilots = query_db("""
        SELECT * FROM pilots 
        WHERE startup_id = ? OR (startup_name = ? AND ? IS NOT NULL)
    """, (user_id, company_name, company_name))

    lines.append(f"\n--- MY ACTIVE / COMPLETED PILOTS ({len(my_pilots)} total) ---")
    if my_pilots:
        for p in my_pilots:
            lines.append(
                f"- [Pilot ID: {p['pilot_id']}] Challenge: '{p['challenge_title']}' | Status: {p['status']} | "
                f"Progress: {p['milestone_progress']}% | Period: {p['start_date']} to {p['end_date']}"
            )
            # Milestones for this pilot
            m_list = query_db("SELECT * FROM milestones WHERE pilot_id = ? ORDER BY due_date ASC", (p['pilot_id'],))
            lines.append("  Milestones:")
            for m in m_list:
                lines.append(
                    f"   * Milestone: '{m['title']}' | Status: {m['status']} | Due Date: {m['due_date']} | "
                    f"Evidence Uploaded: {m['evidence_file'] or 'None (Required)'}"
                )
            
            # KPIs for this pilot
            k_list = query_db("SELECT * FROM performance WHERE pilot_id = ?", (p['pilot_id'],))
            if k_list:
                lines.append("  KPI Metrics:")
                for k in k_list:
                    lines.append(
                        f"   * KPI: {k['kpi_name']} | Target: {k['target_value']} {k['unit']} | Actual: {k['actual_value']} {k['unit']}"
                    )
    else:
        lines.append("No active pilots assigned to your startup.")

    return "\n".join(lines)


def get_evaluator_context(user_id):
    lines = ["=== EVALUATOR USER CONTEXT ==="]

    # 1. Applications Pending Evaluation or Evaluated
    apps = query_db("""
        SELECT a.*, COUNT(e.evaluation_id) as eval_count
        FROM applications a
        LEFT JOIN evaluations e ON a.application_id = e.application_id
        GROUP BY a.application_id
        ORDER BY a.submitted_at DESC
    """)
    lines.append(f"\n--- APPLICATIONS OVERVIEW & SCORING STATUS ({len(apps)} total) ---")
    if apps:
        for app in apps:
            eval_status = f"Evaluated ({app['eval_count']} review(s), Score: {app['total_score']})" if app['total_score'] is not None else "NEEDS EVALUATION"
            lines.append(
                f"- [App ID: {app['application_id']}] Startup: '{app['startup_name']}' | Challenge: '{app['challenge_title']}' | "
                f"App Status: {app['status']} | Scoring Status: {eval_status}"
            )
    else:
        lines.append("No applications submitted.")

    # 2. Detailed Evaluation Records
    evals = query_db("""
        SELECT e.*, a.startup_name, a.challenge_title
        FROM evaluations e
        JOIN applications a ON e.application_id = a.application_id
        ORDER BY e.total_score DESC
    """)
    lines.append(f"\n--- EVALUATIONS RECORDED ({len(evals)} total) ---")
    if evals:
        for ev in evals:
            lines.append(
                f"- [Eval ID: {ev['evaluation_id']}] App #{ev['application_id']} ({ev['startup_name']} for '{ev['challenge_title']}'): "
                f"Scores -> Eligibility: {ev['eligibility_score']}, Tech: {ev['technology_score']}, "
                f"Feasibility: {ev['feasibility_score']}, Timeline: {ev['timeline_score']}, Experience: {ev['experience_score']} | "
                f"Total Score: {ev['total_score']}/100 | Comments: {ev['comments']}"
            )

    # 3. Pilot Milestones Needing Approval / Attention
    milestones = query_db("""
        SELECT m.*, p.startup_name, p.challenge_title
        FROM milestones m
        JOIN pilots p ON m.pilot_id = p.pilot_id
        ORDER BY m.due_date ASC
    """)
    lines.append(f"\n--- PILOT MILESTONES REVIEW ({len(milestones)} total) ---")
    if milestones:
        for m in milestones:
            lines.append(
                f"- Milestone #{m['milestone_id']} [Pilot #{m['pilot_id']} - {m['startup_name']}]: '{m['title']}' | "
                f"Status: {m['status']} | Due: {m['due_date']} | Evidence File: {m['evidence_file'] or 'None'}"
            )

    # 4. KPI Performance Results
    kpis = query_db("""
        SELECT k.*, p.startup_name, p.challenge_title
        FROM performance k
        JOIN pilots p ON k.pilot_id = p.pilot_id
    """)
    lines.append(f"\n--- PILOT KPI PERFORMANCE DATA ({len(kpis)} total) ---")
    if kpis:
        for k in kpis:
            lines.append(
                f"- Pilot #{k['pilot_id']} ({k['startup_name']}): KPI: '{k['kpi_name']}' | "
                f"Target: {k['target_value']} {k['unit']} | Actual: {k['actual_value']} {k['unit']} | Remarks: {k['remarks']}"
            )

    return "\n".join(lines)


def get_admin_context():
    lines = ["=== ADMIN USER CONTEXT ==="]

    # Platform Overview Counts
    users_count = query_db("SELECT COUNT(*) as count FROM users", one=True)['count']
    challenges_count = query_db("SELECT COUNT(*) as count FROM challenges", one=True)['count']
    apps_count = query_db("SELECT COUNT(*) as count FROM applications", one=True)['count']
    pilots_count = query_db("SELECT COUNT(*) as count FROM pilots WHERE status = 'Active'", one=True)['count']
    evals_count = query_db("SELECT COUNT(*) as count FROM evaluations", one=True)['count']
    pending_evals = query_db("SELECT COUNT(*) as count FROM applications WHERE total_score IS NULL", one=True)['count']
    pending_milestones = query_db("SELECT COUNT(*) as count FROM milestones WHERE status = 'Submitted'", one=True)['count']

    lines.append(f"""
--- PLATFORM METRICS OVERVIEW ---
- Total Registered Users: {users_count}
- Total Challenges: {challenges_count}
- Total Submitted Applications: {apps_count}
- Applications Pending Evaluation: {pending_evals}
- Total Completed Evaluations: {evals_count}
- Active Pilots: {pilots_count}
- Milestones Pending Approval: {pending_milestones}
""")

    # Stage Bottlenecks
    draft_challenges = query_db("SELECT COUNT(*) as count FROM challenges WHERE status = 'Draft'", one=True)['count']
    published_challenges = query_db("SELECT COUNT(*) as count FROM challenges WHERE status = 'Published'", one=True)['count']
    shortlisted_apps = query_db("SELECT COUNT(*) as count FROM applications WHERE status = 'Shortlisted'", one=True)['count']
    approved_pilot_apps = query_db("SELECT COUNT(*) as count FROM applications WHERE status = 'Approved for Pilot'", one=True)['count']

    lines.append("--- STAGE WORKFLOW SUMMARY ---")
    lines.append(f"- Draft Challenges: {draft_challenges}")
    lines.append(f"- Published Challenges: {published_challenges}")
    lines.append(f"- Shortlisted Applications: {shortlisted_apps}")
    lines.append(f"- Applications Approved for Pilot: {approved_pilot_apps}")

    return "\n".join(lines)
