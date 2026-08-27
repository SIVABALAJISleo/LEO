import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from leo_engine import LEOv7_MemoryEfficient

def populate_enterprise_faq():
    """Add real enterprise FAQ to cache."""
    leo = LEOv7_MemoryEfficient()
    leo.initialize_cache()
    
    # REAL enterprise IT questions and answers
    faq_data = {
        "How do I reset my password?": 
            "Go to myaccount.company.com, click 'Forgot Password', check your email for reset link, create new password with 12+ characters including uppercase, lowercase, number, and special character.",
        
        "What's the VPN setup process?": 
            "Download Cisco AnyConnect from IT portal. Install it. Open AnyConnect. Server: vpn.company.com. Username: your AD login. Password: your AD password. Click Connect.",
        
        "How do I request a new laptop?": 
            "Submit IT ticket via ServiceNow portal. Include: department, laptop specs needed, business justification. Wait for manager approval. IT will ship within 5-7 business days.",
        
        "How do I connect to the printer?": 
            "Go to Settings > Devices > Printers. Click 'Add a printer or scanner'. Search for 'Floor3-HP-LaserJet'. Select it. Click 'Add device'. Done.",
        
        "What's the onboarding process for new hires?": 
            "1. IT provisions account (1 day). 2. HR sends onboarding checklist. 3. Attend orientation (2 hours). 4. Department training (variable). 5. System access granted (3-5 days).",
        
        "How do I report a security incident?": 
            "Call IT Security immediately: ext 5555. Do NOT touch the affected device. Document what happened. Security team will investigate within 1 hour.",
        
        "Where's the company handbook?": 
            "Download from HR portal: hr.company.com > Documents > Handbook. Or email hr@company.com to request printed copy.",
        
        "How do I book a conference room?": 
            "Use Outlook calendar. Click 'New Event'. Select 'Room' dropdown. Search 'Conference Room North'. Select time slot. Send invite to roomreservation@company.com.",
        
        "What's the leave approval process?": 
            "Submit in HR portal minimum 2 weeks in advance. Manager auto-approves (or requests changes). HR confirms. Your calendar updates automatically.",
        
        "How do I access the file server?": 
            "On Windows: File Explorer > Map Network Drive > \\\\fileserver.company.local\\yourteam > use AD credentials. On Mac: Finder > Connect to Server > smb://fileserver.company.local",
    }
    
    print("📝 Populating LEO cache with enterprise FAQ...\n")
    
    for question, answer in faq_data.items():
        leo.add_to_cache(question, answer, sync_index=False)
    
    leo._sync_vector_index()
    
    print(f"\n✅ Cache populated with {len(faq_data)} enterprise FAQs")
    print("   These answers have been pre-computed and stored locally.")
    print("   Next queries will use semantic matching (FAST, NO LLM NEEDED)\n")

if __name__ == "__main__":
    populate_enterprise_faq()
