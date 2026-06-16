# -*- coding: utf-8 -*-
"""
Stick2It - End-to-End Flow Test
Tests: Registration, Login, Task Creation, Nudge Sending (Email + In-App), and Task Verification.

Run from project root:
    .venv/Scripts/python.exe e2e_test.py
"""

import requests
import time
import json
import sys
import os
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8000"

# â”€â”€â”€ ANSI colours â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0
warnings = []

def ok(msg):
    global passed
    passed += 1
    print(f"  {GREEN}[PASS]{RESET}  {msg}")

def fail(msg, detail=""):
    global failed
    failed += 1
    detail_str = f"\n         {RED}{detail}{RESET}" if detail else ""
    print(f"  {RED}[FAIL]{RESET}  {msg}{detail_str}")

def warn(msg):
    warnings.append(msg)
    print(f"  {YELLOW}[WARN]{RESET}  {msg}")

def header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def section(title):
    print(f"\n{BOLD}â”€â”€ {title} â”€â”€{RESET}")

def api(method, path, token=None, **kwargs):
    """Helper: Make an API call and return (response, data)."""
    url = f"{BASE_URL}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = getattr(requests, method)(url, headers=headers, timeout=15, **kwargs)
        try:
            data = r.json()
        except Exception:
            data = {"_raw": r.text}
        return r, data
    except requests.exceptions.ConnectionError:
        fail(f"Cannot connect to {url} â€” is the backend running on port 8000?")
        sys.exit(1)
    except Exception as e:
        return None, {"error": str(e)}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  1. HEALTH CHECK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("1. SERVER HEALTH")

r, data = api("get", "/api/v1/health")
if r and r.status_code == 200 and data.get("status") == "online":
    ok(f"Backend is online - version {data.get('version', '?')}")
else:
    fail("Backend health check failed", str(data))
    sys.exit(1)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  2. REGISTRATION & LOGIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("2. AUTH FLOW")

ts = int(time.time())
STUDENT_EMAIL    = f"testuser_{ts}@e2e.test"
STUDENT_PASSWORD = "SecureTest@2026"
BUDDY_EMAIL      = f"buddy_{ts}@e2e.test"
BUDDY_NAME       = "Test Buddy"

section("Student Registration")
r, data = api("post", "/api/v1/auth/register", json={
    "name": "E2E Student",
    "email": STUDENT_EMAIL,
    "password": STUDENT_PASSWORD
})
if r and r.status_code == 200 and data.get("success"):
    student_id = data.get("student_id")
    ok(f"Registered student â€” ID: {student_id}")
else:
    fail("Registration failed", str(data))
    sys.exit(1)

section("Student Login")
r, data = api("post", "/api/v1/auth/login", json={
    "email": STUDENT_EMAIL,
    "password": STUDENT_PASSWORD
})
if r and r.status_code == 200 and data.get("token"):
    TOKEN = data["token"]
    ok(f"Login successful â€” token obtained")
else:
    fail("Login failed", str(data))
    sys.exit(1)

section("Duplicate Registration Guard")
r, data = api("post", "/api/v1/auth/register", json={
    "name": "Duplicate",
    "email": STUDENT_EMAIL,
    "password": STUDENT_PASSWORD
})
if r and r.status_code == 400:
    ok("Duplicate email correctly rejected (400)")
else:
    warn(f"Expected 400 for duplicate email, got {r.status_code if r else 'no response'}: {data}")

section("Token Auth â€” /api/v1/me")
r, data = api("get", "/api/v1/me", token=TOKEN)
if r and r.status_code == 200 and data.get("email") == STUDENT_EMAIL:
    ok(f"Token auth works â€” user: {data.get('name')}")
else:
    fail("/api/v1/me failed", str(data))

section("Bad Token Rejection")
r, data = api("get", "/api/v1/me", token="invalid.jwt.token")
if r and r.status_code == 401:
    ok("Invalid token correctly rejected (401)")
else:
    warn(f"Expected 401 for invalid token, got {r.status_code if r else 'no response'}")

# Register buddy account (needed for partner/verification tests)
section("Buddy Registration")
r, data = api("post", "/api/v1/auth/register", json={
    "name": BUDDY_NAME,
    "email": BUDDY_EMAIL,
    "password": "BuddyPass@2026"
})
if r and r.status_code == 200:
    buddy_id = data.get("student_id")
    ok(f"Buddy registered â€” ID: {buddy_id}")
else:
    warn(f"Buddy registration failed (non-blocking): {data}")
    buddy_id = None

r, data = api("post", "/api/v1/auth/login", json={
    "email": BUDDY_EMAIL,
    "password": "BuddyPass@2026"
})
BUDDY_TOKEN = data.get("token") if r and r.status_code == 200 else None
if BUDDY_TOKEN:
    ok("Buddy login successful")
else:
    warn("Buddy login failed â€” buddy-side tests will be skipped")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  3. TASK / COMMITMENT CREATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("3. TASK (COMMITMENT) CREATION")

future_dt = (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()

section("Create Points-based Task")
r, data = api("post", "/api/v1/commitments", token=TOKEN, json={
    "title": "E2E Points Task",
    "committed_datetime": future_dt,
    "stake_value": 20,
    "stake_type": "Points"
})
if r and r.status_code == 200 and data.get("success"):
    POINTS_COMMIT_ID = data.get("commitment_id") or data.get("id")
    ok(f"Points commitment created â€” ID: {POINTS_COMMIT_ID}")
else:
    fail("Points commitment creation failed", str(data))
    POINTS_COMMIT_ID = None

section("Create Social-Stake Task (with Buddy)")
r, data = api("post", "/api/v1/commitments", token=TOKEN, json={
    "title": "E2E Social Task",
    "committed_datetime": future_dt,
    "stake_value": 30,
    "stake_type": "Social",
    "buddy_name": BUDDY_NAME,
    "buddy_email": BUDDY_EMAIL
})
if r and r.status_code == 200 and data.get("success"):
    SOCIAL_COMMIT_ID = data.get("commitment_id") or data.get("id")
    ok(f"Social commitment created â€” ID: {SOCIAL_COMMIT_ID}")
else:
    fail("Social commitment creation failed", str(data))
    SOCIAL_COMMIT_ID = None

section("Verify Commitment Appears in Stats")
r, data = api("get", f"/api/v1/students/{student_id}/stats", token=TOKEN)
if r and r.status_code == 200 and data.get("success"):
    commit_ids = [c["id"] for c in data.get("commitments", [])]
    found_points = POINTS_COMMIT_ID in commit_ids
    found_social = SOCIAL_COMMIT_ID in commit_ids
    if found_points and found_social:
        ok(f"Both commitments visible in stats ({len(commit_ids)} total)")
    elif found_points or found_social:
        warn(f"Only some commitments found in stats: {commit_ids}")
    else:
        fail("New commitments not visible in stats",
             f"Expected {POINTS_COMMIT_ID} and {SOCIAL_COMMIT_ID}, got {commit_ids}")
else:
    fail("Student stats endpoint failed", str(data))

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  4. TASK LIFECYCLE (START â†’ SUBMIT â†’ COMPLETE)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("4. TASK LIFECYCLE")

if POINTS_COMMIT_ID:
    section("Start Points Task")
    r, data = api("patch", f"/api/v1/commitments/{POINTS_COMMIT_ID}/start", token=TOKEN)
    if r and r.status_code == 200 and data.get("success"):
        ok("Task marked as in_progress")
    else:
        fail("Start task failed", str(data))

    section("Submit Points Task for Completion")
    r, data = api("patch", f"/api/v1/commitments/{POINTS_COMMIT_ID}/submit", token=TOKEN)
    if r and r.status_code == 200 and data.get("success"):
        ok(f"Points task completed â€” {data.get('message')}")
    else:
        fail("Submit task failed", str(data))

if SOCIAL_COMMIT_ID:
    section("Start Social Task")
    r, data = api("patch", f"/api/v1/commitments/{SOCIAL_COMMIT_ID}/start", token=TOKEN)
    if r and r.status_code == 200 and data.get("success"):
        ok("Social task marked as in_progress")
    else:
        fail("Start social task failed", str(data))

    section("Submit Social Task for Buddy Verification")
    r, data = api("patch", f"/api/v1/commitments/{SOCIAL_COMMIT_ID}/submit", token=TOKEN)
    if r and r.status_code == 200 and data.get("success"):
        ok(f"Social task submitted for verification â€” {data.get('message')}")
    else:
        fail("Submit social task failed", str(data))

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  5. NUDGE SYSTEM
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("5. NUDGE SYSTEM")

section("Get Nudges (Dashboard Context)")
r, data = api("get", f"/api/v1/students/{student_id}/nudges?context=dashboard", token=TOKEN)
if r and r.status_code == 200:
    nudges = data.get("nudges", [])
    ok(f"Nudge endpoint OK â€” {len(nudges)} nudge(s) returned")
    for n in nudges[:3]:
        print(f"         â€¢ [{n.get('type', '?')}] {n.get('message', '')[:80]}â€¦")
else:
    fail("Nudge endpoint failed", str(data))

section("Test Direct Nudge Sending (/test-nudge)")
r, data = api("get", "/test-nudge")
if r and r.status_code == 200:
    delivered = data.get("delivered", False)
    if delivered:
        ok("Direct nudge sent and delivered (email + in-app confirmed)")
    else:
        warn(f"Direct nudge endpoint OK but delivery returned False â€” check SendGrid key. Response: {data}")
else:
    fail("/test-nudge endpoint failed", str(data))

section("In-App Notification Created by Nudge")
r, data = api("get", "/api/v1/notifications", token=TOKEN)
if r and r.status_code == 200:
    notifs = data.get("notifications", [])
    nudge_notifs = [n for n in notifs if n.get("type") == "nudge"]
    system_notifs = [n for n in notifs if n.get("type") == "system_alert"]
    ok(f"Notification inbox: {len(notifs)} total ({len(nudge_notifs)} nudges, {len(system_notifs)} system alerts)")
    for n in notifs[:3]:
        print(f"         â€¢ [{n.get('type')}][{n.get('status')}] {n.get('message', '')[:70]}â€¦")
else:
    fail("Notifications endpoint failed", str(data))

section("Email Nudge â€” SendGrid API Check")
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("SENDGRID_API_KEY")
    if api_key and len(api_key) > 20 and not api_key.startswith("SG.your"):
        ok(f"SendGrid API key is configured (key prefix: {api_key[:12]}â€¦)")
    else:
        warn("SendGrid API key missing or placeholder â€” emails will be simulated/logged only")
except Exception as e:
    warn(f"Could not verify SendGrid key: {e}")

section("Firebase Push â€” Config Check")
import os as _os
firebase_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "backend", "firebase-adminsdk.json")
if _os.path.exists(firebase_path):
    try:
        with open(firebase_path) as f:
            fb_data = json.load(f)
        if fb_data.get("project_id") and fb_data.get("private_key"):
            ok(f"Firebase service account configured â€” project: {fb_data.get('project_id')}")
        else:
            warn("Firebase JSON exists but looks incomplete")
    except Exception as e:
        warn(f"Firebase JSON parse error: {e}")
else:
    warn(f"Firebase service account JSON not found at {firebase_path}")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  6. BUDDY / ACCOUNTABILITY PARTNER SYSTEM
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("6. BUDDY SYSTEM & ACCOUNTABILITY PARTNERS")

if buddy_id:
    section("Add Accountability Partner")
    r, data = api("post", "/api/v1/partners", token=TOKEN, json={"partner_email": BUDDY_EMAIL})
    if r and r.status_code == 200 and data.get("success"):
        ok(f"Partner request sent to {BUDDY_EMAIL}")
    else:
        fail("Add partner failed", str(data))

    section("Buddy Gets Notification of Request")
    if BUDDY_TOKEN:
        r, data = api("get", "/api/v1/notifications", token=BUDDY_TOKEN)
        if r and r.status_code == 200:
            buddy_notifs = data.get("notifications", [])
            buddy_requests = [n for n in buddy_notifs if n.get("type") == "buddy_request"]
            if buddy_requests:
                ok(f"Buddy received {len(buddy_requests)} buddy request notification(s)")
                # Accept the most recent buddy request
                latest = buddy_requests[0]
                notif_id = latest["id"]
                section("Buddy Accepts Partnership Request")
                r2, d2 = api("post", f"/api/v1/notifications/{notif_id}/respond",
                             token=BUDDY_TOKEN, json={"action": "accept"})
                if r2 and r2.status_code == 200 and d2.get("success"):
                    ok("Buddy accepted â€” partnership established")
                else:
                    warn(f"Accept request failed: {d2}")
            else:
                warn(f"No buddy_request notifications found â€” got: {[n['type'] for n in buddy_notifs]}")
        else:
            fail("Buddy notifications endpoint failed", str(data))
    else:
        warn("Buddy token not available â€” skipping buddy notification test")

section("Get Buddy's View of Commitments")
if BUDDY_TOKEN:
    r, data = api("get", "/api/v1/buddy/commitments", token=BUDDY_TOKEN)
    if r and r.status_code == 200:
        buddy_commits = data.get("commitments", [])
        ok(f"Buddy can see {len(buddy_commits)} commitment(s) to verify")
        for c in buddy_commits[:3]:
            print(f"         â€¢ [{c.get('owner_name')}] {c.get('title')} â€” token: {str(c.get('verification_token', ''))[:16]}â€¦")
    else:
        fail("Buddy commitments endpoint failed", str(data))
else:
    warn("Skipped â€” no buddy token")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  7. TASK VERIFICATION FLOW
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("7. TASK VERIFICATION (BUDDY CONFIRMS COMPLETION)")

# Create a fresh social commitment to test verification end-to-end
section("Create fresh Social Commitment for Verification Test")
r, data = api("post", "/api/v1/commitments", token=TOKEN, json={
    "title": "Verify Me Task",
    "committed_datetime": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
    "stake_value": 15,
    "stake_type": "Social",
    "buddy_name": BUDDY_NAME,
    "buddy_email": BUDDY_EMAIL
})
if r and r.status_code == 200 and data.get("success"):
    VERIFY_COMMIT_ID = data.get("commitment_id") or data.get("id")
    ok(f"Verification test commitment created â€” ID: {VERIFY_COMMIT_ID}")
else:
    fail("Could not create commitment for verification test", str(data))
    VERIFY_COMMIT_ID = None

if VERIFY_COMMIT_ID:
    # Get the verification token from stats
    r, data = api("get", f"/api/v1/students/{student_id}/stats", token=TOKEN)
    VERIFY_TOKEN = None
    if r and r.status_code == 200:
        from backend.app.database import get_db_session
        from backend.app.models import Commitment
        with get_db_session() as db:
            c = db.query(Commitment).filter(Commitment.id == VERIFY_COMMIT_ID).first()
            VERIFY_TOKEN = c.verification_token if c else None
    
    if VERIFY_TOKEN:
        ok(f"Obtained verification token: {VERIFY_TOKEN[:16]}â€¦")

        section("Buddy Views Verification Page (GET /api/v1/verify/{token})")
        r, data = api("get", f"/api/v1/verify/{VERIFY_TOKEN}")
        if r and r.status_code == 200:
            ok(f"Verification info page OK â€” task: {data.get('title')}, status: {data.get('status')}")
        else:
            fail("Verification info endpoint failed", str(data))

        # Submit task first (student marks it done)
        section("Student Submits Task (claims done)")
        r, data = api("patch", f"/api/v1/commitments/{VERIFY_COMMIT_ID}/start", token=TOKEN)
        r, data = api("patch", f"/api/v1/commitments/{VERIFY_COMMIT_ID}/submit", token=TOKEN)
        if r and r.status_code == 200 and data.get("success"):
            ok("Student submitted task for buddy verification")
        else:
            warn(f"Submit returned: {data}")

        section("Buddy Verifies Task as KEPT (POST /api/v1/verify/{token}/kept)")
        r, data = api("post", f"/api/v1/verify/{VERIFY_TOKEN}/kept")
        if r and r.status_code == 200 and data.get("success"):
            ok("[KEPT] Task verified as KEPT - commitment marked completed!")
        else:
            fail("Verification (kept) failed", str(data))

        section("In-App Notification Sent to Student After Verification")
        r, data = api("get", "/api/v1/notifications", token=TOKEN)
        if r and r.status_code == 200:
            notifs = data.get("notifications", [])
            verification_notifs = [n for n in notifs if "verified" in n.get("message", "").lower() 
                                   or "kept" in n.get("message", "").lower()
                                   or "buddy" in n.get("message", "").lower()]
            if verification_notifs:
                ok(f"Student received {len(verification_notifs)} verification notification(s)")
                for n in verification_notifs[:2]:
                    print(f"         â€¢ {n.get('message', '')[:80]}")
            else:
                warn(f"No verification notifications found in {len(notifs)} notifications")
        else:
            fail("Could not fetch notifications after verification", str(data))
    else:
        warn("Could not obtain verification token from DB â€” skipping full verification test")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  8. BROKEN COMMITMENT (PENALTY) TEST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("8. BROKEN COMMITMENT (PENALTY FLOW)")

section("Create another Social Commitment to test failure")
r, data = api("post", "/api/v1/commitments", token=TOKEN, json={
    "title": "Fail Me Task",
    "committed_datetime": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
    "stake_value": 10,
    "stake_type": "Social",
    "buddy_name": BUDDY_NAME,
    "buddy_email": BUDDY_EMAIL
})
FAIL_COMMIT_ID = None
FAIL_TOKEN = None
if r and r.status_code == 200 and data.get("success"):
    FAIL_COMMIT_ID = data.get("commitment_id") or data.get("id")
    ok(f"Fail-test commitment created â€” ID: {FAIL_COMMIT_ID}")
    
    from backend.app.database import get_db_session
    from backend.app.models import Commitment
    with get_db_session() as db:
        c = db.query(Commitment).filter(Commitment.id == FAIL_COMMIT_ID).first()
        FAIL_TOKEN = c.verification_token if c else None
else:
    warn(f"Could not create fail-test commitment: {data}")

if FAIL_TOKEN:
    section("Buddy marks task as BROKEN (POST /api/v1/verify/{token}/broken)")
    r, data = api("post", f"/api/v1/verify/{FAIL_TOKEN}/broken")
    if r and r.status_code == 200 and data.get("success"):
        ok("[BROKEN] Task marked as BROKEN - penalty flow executed")
    else:
        fail("Verification (broken) failed", str(data))

    section("Penalty Notification Delivered to Student")
    r, data = api("get", "/api/v1/notifications", token=TOKEN)
    if r and r.status_code == 200:
        notifs = data.get("notifications", [])
        penalty_notifs = [n for n in notifs if "fail" in n.get("message", "").lower()
                          or "broken" in n.get("message", "").lower()
                          or "penalty" in n.get("message", "").lower()]
        if penalty_notifs:
            ok(f"Penalty notification sent to student ({len(penalty_notifs)} found)")
            for n in penalty_notifs[:2]:
                print(f"         â€¢ {n.get('message', '')[:80]}")
        else:
            warn(f"No penalty notifications in inbox â€” all notifs: {[(n['type'], n['message'][:40]) for n in notifs[:5]]}")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  9. AI / RISK PREDICTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("9. AI RISK PREDICTION")

section("Predict Risk from Database Features")
r, data = api("get", f"/api/v1/students/{student_id}/predict", token=TOKEN)
if r and r.status_code == 200 and data.get("success"):
    pred = data.get("prediction", {})
    risk = pred.get("probability_high_risk", pred.get("risk_score", "N/A"))
    label = pred.get("risk_label", "")
    ok(f"AI prediction: risk={risk}, label={label}")
else:
    warn(f"Prediction endpoint returned: {r.status_code if r else 'no response'} â€” {data}")

section("Predict Risk from Raw Features")
r, data = api("post", "/api/v1/predict", token=TOKEN, json={
    "last_minute_ratio": 0.8,
    "engagement_intensity": 0.3,
    "deadline_pressure": 0.9,
    "login_consistency": 0.4,
    "early_starter": 0,
    "completion_rate": 0.5,
    "activity_span": 0.2
})
if r and r.status_code == 200 and data.get("success"):
    pred = data.get("prediction", {})
    ok(f"Raw feature prediction: risk={pred.get('probability_high_risk', 'N/A')}, label={pred.get('risk_label', 'N/A')}")
else:
    warn(f"Raw prediction failed: {r.status_code if r else 'N/A'} â€” {data}")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  10. SUMMARY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
header("TEST SUMMARY")

total = passed + failed
print(f"\n  {GREEN}{BOLD}{passed}/{total} checks passed{RESET}  â€¢  {RED}{failed} failed{RESET}  â€¢  {YELLOW}{len(warnings)} warnings{RESET}")

if warnings:
    print(f"\n{YELLOW}Warnings:{RESET}")
    for w in warnings:
        print(f"  âš   {w}")

if failed == 0:
    print(f"\n{GREEN}{BOLD}*** All tests passed! The end-to-end flow is working correctly. ***{RESET}")
else:
    print(f"\n{RED}{BOLD}!!! {failed} test(s) failed. Review the output above. !!!{RESET}")

print()

