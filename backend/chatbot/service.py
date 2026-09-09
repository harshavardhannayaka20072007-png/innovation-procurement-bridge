"""Safe, no-key-required chatbot responses based on current portal data."""


def generate_chatbot_response(message, context):
    """Answer common questions from the authorized, live database summary only."""
    question = message.strip().lower()
    role = context['role']

    if any(term in question for term in ('challenge', 'apply', 'available')):
        return f"There are **{context['open_challenges']} published challenge(s)** currently open to startups. Open Browse Challenges to review eligibility and deadlines."
    if any(term in question for term in ('milestone', 'evidence', 'proof')):
        if role == 'startup':
            return f"You have **{context['milestones_pending']} milestone(s)** that need action or resubmission. Upload evidence from the Milestones page."
        return f"There are **{context.get('milestones_submitted', 0)} submitted milestone proof(s)** awaiting review."
    if any(term in question for term in ('pilot', 'progress', 'performance')):
        if role == 'startup':
            pilots = context['pilots']
            if not pilots:
                return 'You do not have an assigned pilot yet.'
            latest = pilots[0]
            return f"Your latest pilot, **{latest['challenge_title']}**, is **{latest['status']}** at **{latest['milestone_progress']}%** milestone progress."
        return f"The programme currently has **{context.get('active_pilots', 0)} active or near-completion pilot(s)**."
    if any(term in question for term in ('application', 'proposal', 'score', 'evaluation', 'rank')):
        if role == 'startup':
            return f"You have **{context['applications']} submitted application(s)**. Open My Applications to view status and readiness scores."
        if role == 'evaluator':
            return f"There are **{context['applications_pending']} application(s)** awaiting evaluation or review."
        return f"The programme has **{context.get('applications', 0)} recorded application(s)**. Use Applications or Readiness Ranking for details."
    if any(term in question for term in ('audit', 'ledger', 'blockchain', 'ethereum')):
        if role in ('government', 'admin'):
            return f"The audit ledger currently has **{context.get('audit_records', 0)} sealed record(s)**. Hashes are sealed locally; Ethereum anchoring activates only after its RPC, contract, and wallet are configured."
        return 'The portal records sensitive procurement actions in a tamper-evident audit ledger. Government administrators can inspect the ledger.'
    if any(term in question for term in ('overview', 'how many', 'platform')) and role in ('government', 'admin'):
        return (f"**Live programme overview:** {context['challenges']} challenges, "
                f"{context['applications']} applications, {context['active_pilots']} active pilots, "
                f"and {context['milestones_submitted']} milestone proof(s) awaiting review.")
    return ('I can help with challenges, applications, evaluations, pilots, milestones, and the audit ledger. '
            'I only use records available to your current role.')
