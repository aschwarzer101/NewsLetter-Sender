"""
ActiveMinds Newsletter Automation Script - Mac Mail App Version
Opens draft emails in Mac Mail using mailto links.

SETUP: Make sure Mac Mail is set as your default mail app:
  1. Open Mac Mail
  2. Go to Mail menu → Settings → General
  3. Set "Default email reader" to "Mail"
"""

import subprocess
import urllib.parse
import time

# School templates
SCHOOLS = {
    "Bowen": {
        "email": "communitynotes@bowenpto.org",
        "subject": "RE: Bowen PTO Community Notes Submission Request | ActiveMinds Tutoring",
        "body": """Good afternoon,
ActiveMinds Tutoring would appreciate the opportunity to display our tutoring services in the Bowen PTO Community Notes page.
Please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },

    "Countryside": {
        "email": "update@countrysidepto.org",
        "subject": "Countryside PTO Newsletter Submission Request",
        "body": """Good afternoon,
ActiveMinds Tutoring would appreciate the opportunity to display our tutoring services in the Countryside PTO Newsletter for this Sunday's issue.
Please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },

    "Mason-Rice": {
        "email": "mrnotessubmissions@gmail.com",
        "subject": "Community Classifieds Request",
        "body": """Good Afternoon!
ActiveMinds tutoring would appreciate the opportunity to display our tutoring services in the upcoming Mason-Rice Community Classifieds — please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },

    "Ward": {
        "email": "copresidents@wardpto.org",
        "subject": "ForWard Weekly PTO Newsletter Submission Request | ActiveMinds Tutoring",
        "body": """Good afternoon,
ActiveMinds Tutoring would appreciate the opportunity to display our tutoring services in the next ForWard Newsletter.
Please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },

    "Florida Ruffin Ridley": {
        "email": "pto@ruffinridleypto.org",
        "subject": "PTO Newsletter Submission Request",
        "body": """Good afternoon,
ActiveMinds Tutoring would appreciate the opportunity to display our tutoring services in the upcoming Florida Ruffin Ridley PTO Newsletter.

Please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },

    "Driscoll": {
        "email": "driscollbulletin@gmail.com",
        "subject": "Weekly PTO Bulletin Submission Request | ActiveMinds Tutoring",
        "body": """Good afternoon,
ActiveMinds Tutoring would appreciate the opportunity to display our tutoring services in the Driscoll Classifieds section of the Weekly PTO Bulletin in Sunday's issue.
Please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },

    "Angier": {
        "email": "angiergreensheet@gmail.com",
        "subject": "RE: Greensheet Classifieds Submission Request | ActiveMinds Tutoring",
        "body": """Good afternoon,
ActiveMinds Tutoring would appreciate the opportunity to display our tutoring services in the Greensheet's Classifieds section.
Please see our blurb below:

ActiveMinds Tutoring
[MEMO]
Over 15 years providing tutoring for all academic subjects, studying skills, and standardized test prep (SAT/ACT, ISEE, SSAT). Contact ActiveMinds to learn more about our personalized plans with experienced tutors. 617.227.2225 | learnmore@activemindstutoring.com | http://www.activemindstutoring.com/

Thank you for your consideration!"""
    },
}


def open_draft_in_mail(school_name, school_info, memo_text):
    """Opens a draft compose window in the default mail app via mailto link."""
    body_with_memo = school_info["body"].replace("[MEMO]", memo_text)

    params = urllib.parse.urlencode({
        "subject": school_info["subject"],
        "body": body_with_memo
    }, quote_via=urllib.parse.quote)

    mailto_url = f"mailto:{urllib.parse.quote(school_info['email'])}?{params}"

    try:
        subprocess.run(["open", mailto_url], check=True)
        print(f"  ✅ Opened draft for {school_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to open draft for {school_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("ActiveMinds Newsletter Automation — Mac Mail Version")
    print("=" * 60)
    print(f"\nThis will open {len(SCHOOLS)} draft emails in Mac Mail:")
    for school_name in SCHOOLS.keys():
        print(f"  • {school_name}")

    print("\n" + "-" * 60)
    print("NOTE: Make sure Mac Mail is your default mail app.")
    print("      Each draft will open in a new compose window.")
    print("-" * 60)

    memo_text = input("\nEnter your memo/tagline (replaces [MEMO]):\n> ").strip()

    if not memo_text:
        print("\n❌ Error: Memo text cannot be empty!")
        return

    print(f"\nMemo: {memo_text}")
    confirm = input(f"\nOpen {len(SCHOOLS)} drafts in Mac Mail? (yes/no): ").strip().lower()

    if confirm not in ["yes", "y"]:
        print("\nCancelled. No drafts were created.")
        return

    print("\nOpening drafts...\n")
    success_count = 0
    for school_name, school_info in SCHOOLS.items():
        if open_draft_in_mail(school_name, school_info, memo_text):
            success_count += 1
        time.sleep(1.5)

    print(f"\n{'=' * 60}")
    print(f"Done! {success_count}/{len(SCHOOLS)} drafts opened in Mac Mail.")
    print("Review each compose window and click Send when ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()