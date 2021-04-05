from datetime import datetime
from pytz import timezone
from collections import defaultdict

from app import app
from util.checks import get_overdue_checks

def check_reminders():
    overdue_checks = get_overdue_checks()
    map_ta_to_checks = defaultdict(list)

    for check in overdue_checks:
        map_ta_to_checks[check.ta].append(check)

    for ta, checks in map_ta_to_checks.items():
        count = len(checks)
        if count == 0: continue

        user_id = app.client.users_lookupByEmail(
            email=checks[0].email
        ).get('user').get('id')

        text = f"You have {count} overdue check{'' if count == 1 else 's'}."
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
        ]
        for check in checks:
            due_date = datetime.fromtimestamp(check.due_date).strftime('%A, %B %d %Y')
            details = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Task:*\n{check.name}\n*Due Date:*\n{due_date}"
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://i.imgur.com/clUACZN.png",
                    "alt_text": "check"
                }
            }
            actions = {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "✅ Done"
                        },
                        "style": "primary",
                        "value": f"{check.ta}@{check.name}@{due_date}",
                        "action_id": "check-done",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "⌛ Snooze"
                        },
                        "style": "danger",
                        "value": f"{check.ta}@{check.name}@{due_date}",
                        "action_id": "check-snooze",
                    },
                ],
            }
            blocks.extend([details, actions])

        app.client.chat_postMessage(
            channel=user_id,
            text=text,
            blocks=blocks,
        )

def meeting_reminders():
    if datetime.today().weekday() == 2: # Wednesday
        print("Scheduling grading reminder...")
        meeting = "Grading"
        channel = 'G01K5K9TR71' # ta-grading
        # channel = 'G01JXEXPVPB' # beta-testing
        url = "https://cmu.zoom.us/j/91981168014?pwd=aGc0K0hneHdRZ05qY3VoMzcyTXZWUT09"
        time = datetime.now(timezone('US/Eastern')).replace(hour=20, minute=45, second=0)

    elif datetime.today().weekday() == 3: # Thursday
        print("Scheduling staff meeting reminder...")
        meeting = "Staff meeting"
        channel = 'C01JBBT26VC' # announcements
        url = "https://cmu.zoom.us/j/95048815548?pwd=aFVHZytQaTRycTFCdE9WSUZCQ0xVdz09"
        time = datetime.now(timezone('US/Eastern')).replace(hour=20, minute=35, second=0)

    else:
        return

    response = app.client.chat_scheduleMessage(
        channel=channel,
        post_at=int(time.timestamp()),
        text=f"{meeting} is starting in 15 minutes on Zoom ({url}).",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@channel {meeting} is starting in 15 minutes on Zoom."
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Join Meeting",
                    },
                    "value": "zoom",
                    "url": url,
                    "action_id": "zoom"
                }
            }
        ]
    )
    print(response)

if __name__ == '__main__':
    check_reminders()
    meeting_reminders()