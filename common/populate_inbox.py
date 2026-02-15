#!/usr/bin/env python3
"""
High-performance Dovecot Maildir population script.
Optimized for container startup speed.
"""

import os
import random
import time
import socket
from multiprocessing import Pool, cpu_count
from time import perf_counter
from email.utils import formatdate

# ── Configuration ────────────────────────────────────────────────────

PASSWD_FILE = "/etc/dovecot/users"
MIN_MESSAGES = int(os.environ.get("MIN_MESSAGES", "5"))
MAX_MESSAGES = int(os.environ.get("MAX_MESSAGES", "20"))
WORKERS = int(os.environ.get("POPULATE_WORKERS", "0"))
WORKERS = cpu_count() if WORKERS == 0 else WORKERS

HOSTNAME = socket.gethostname()
PID = os.getpid()

# ── Random Content Data ──────────────────────────────────────────────

FIRST_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Edward",
    "Fiona",
    "George",
    "Hannah",
    "Ivan",
    "Julia",
    "Kevin",
    "Laura",
    "Michael",
    "Nina",
    "Oscar",
    "Patricia",
    "Quentin",
    "Rachel",
    "Steven",
    "Tina",
    "Ulrich",
    "Victoria",
    "William",
    "Xena",
    "Yuri",
    "Zara",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Anderson",
    "Taylor",
    "Thomas",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Thompson",
    "White",
    "Harris",
    "Clark",
    "Lewis",
    "Robinson",
    "Walker",
]

DOMAINS = [
    "example.com",
    "test.org",
    "mail.test",
    "company.example",
    "dev.local",
    "staging.test",
    "demo.org",
    "sample.net",
]

SUBJECTS = [
    "Meeting tomorrow at {time}",
    "Re: Project update",
    "Quick question about {topic}",
    "Invitation: {event}",
    "FYI: {topic} changes",
    "Action required: {topic}",
    "Weekly report - {date}",
    "Hello from {name}",
    "Important: {topic} deadline",
    "Follow up on our conversation",
    "Lunch on {day}?",
    "New {topic} proposal",
    "Reminder: {event}",
    "Thanks for your help with {topic}",
    "Schedule change notification",
    "Documents attached for review",
    "Team outing next {day}",
    "Quarterly review summary",
    "Re: Re: {topic} discussion",
    "Happy {day}!",
]

TOPICS = [
    "database migration",
    "API redesign",
    "server upgrade",
    "deployment pipeline",
    "security audit",
    "performance review",
    "budget allocation",
    "client onboarding",
    "feature release",
    "documentation update",
    "infrastructure",
    "testing strategy",
]

EVENTS = [
    "Team Standup",
    "Sprint Planning",
    "Company All-Hands",
    "Product Demo",
    "Architecture Review",
    "Retrospective",
    "Holiday Party",
    "Training Session",
    "Workshop",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIMES = ["9:00 AM", "10:30 AM", "2:00 PM", "3:30 PM", "4:00 PM"]

BODY_PARAGRAPHS = [
    "I wanted to follow up on our earlier discussion. I think we should move forward with the proposed changes as soon as possible.",
    "Please find the details below. Let me know if you have any questions or concerns about the approach we discussed.",
    "I've reviewed the latest updates and everything looks good. We should be on track for the deadline.",
    "Could you take a look at this when you get a chance? I'd appreciate your feedback before we proceed.",
    "Just a quick note to let you know that the changes have been deployed to the staging environment for testing.",
    "I'll be out of office next week but will be available by email if anything urgent comes up.",
    "Great work on the latest release! The team has done an excellent job meeting all the requirements.",
    "We need to schedule a meeting to discuss the upcoming milestones. Please share your availability.",
    "The latest metrics are looking very positive. I've attached a summary report for your review.",
    "I wanted to share some thoughts on how we can improve our current workflow and reduce bottlenecks.",
    "Thanks for getting back to me so quickly. I agree with your suggestions and will implement them right away.",
    "We should consider the long-term implications of this decision before committing to a specific approach.",
]

SIGN_OFFS = [
    "Best regards",
    "Kind regards",
    "Thanks",
    "Cheers",
    "Best",
    "Regards",
    "Thank you",
    "All the best",
]

# ── Fast Helpers ─────────────────────────────────────────────────────


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_email():
    return f"{random.choice(FIRST_NAMES).lower()}.{random.choice(LAST_NAMES).lower()}@{random.choice(DOMAINS)}"


def random_subject():
    template = random.choice(SUBJECTS)
    return template.format(
        time=random.choice(TIMES),
        topic=random.choice(TOPICS),
        event=random.choice(EVENTS),
        name=random.choice(FIRST_NAMES),
        date=formatdate(localtime=True),
        day=random.choice(DAYS),
    )


def random_body_text():
    paragraphs = random.sample(BODY_PARAGRAPHS, random.randint(1, 4))
    return "\n\n".join(paragraphs) + f"\n\n{random.choice(SIGN_OFFS)},\n{random_name()}"


def text_to_html(text):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    escaped = escaped.replace("\n\n", "</p><p>").replace("\n", "<br>")
    return f"<html><body><p>{escaped}</p></body></html>"


def maildir_filename():
    return f"{time.time():.6f}.{PID}_{random.randint(100000,999999)}.{HOSTNAME}"


def generate_message(recipient_email):
    boundary = f"===============_{random.randint(1000000,9999999)}=="
    sender_name = random_name()
    sender_email = random_email()
    subject = random_subject()

    now = time.time()
    random_offset = random.randint(0, 90 * 24 * 3600)
    date_header = formatdate(timeval=now - random_offset, localtime=False)

    body_text = random_body_text()
    body_html = text_to_html(body_text)

    return f"""From: {sender_name} <{sender_email}>
To: {recipient_email}
Subject: {subject}
Date: {date_header}
Message-ID: <{random.randint(1000000,9999999)}@{sender_email.split("@")[1]}>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="{boundary}"

--{boundary}
Content-Type: text/plain; charset=utf-8

{body_text}

--{boundary}
Content-Type: text/html; charset=utf-8

{body_html}

--{boundary}--
"""


def parse_users(passwd_path):
    users = []
    with open(passwd_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(":")
            if len(parts) >= 6:
                users.append((parts[0], parts[5]))
    return users


# ── Worker ───────────────────────────────────────────────────────────


def populate_user(args):
    email, home = args
    maildir_new = os.path.join(home, "Maildir", "new")
    os.makedirs(maildir_new, exist_ok=True)

    num_messages = random.randint(MIN_MESSAGES, MAX_MESSAGES)
    count = 0

    for _ in range(num_messages):
        msg = generate_message(email)
        filepath = os.path.join(maildir_new, maildir_filename())
        with open(filepath, "wb", buffering=1024 * 1024) as f:
            f.write(msg.encode("utf-8"))
        count += 1

    return count


# ── Main ─────────────────────────────────────────────────────────────


def main():
    if not os.path.exists(PASSWD_FILE):
        print(f"ERROR: {PASSWD_FILE} not found")
        return

    users = parse_users(PASSWD_FILE)
    if not users:
        print("No users found.")
        return

    print(f"Users: {len(users)}")
    print(f"Messages per user: {MIN_MESSAGES}-{MAX_MESSAGES}")
    print(f"Workers: {WORKERS}")

    start = perf_counter()

    with Pool(WORKERS) as pool:
        results = pool.map(populate_user, users)

    total_messages = sum(results)

    end = perf_counter()
    duration = end - start

    print(f"\nTotal messages created: {total_messages}")
    print(f"Total time: {duration:.2f} seconds")
    if duration > 0:
        print(f"Throughput: {total_messages/duration:.0f} messages/sec")


if __name__ == "__main__":
    main()
