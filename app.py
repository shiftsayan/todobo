from slack_bolt import App
import requests

from secrets import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, SNOOZE_CHANNEL_ID, GOOGLE_SHEETS_ENDPOINT
from util.allocations import get_allocations

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)

@app.message("")
def Message(message, say):
  if message['text'].startswith("Carmel:"):
      app.client.reactions_add(
          channel=message['channel'],
          timestamp=message['ts'],
          name='party-carmel',
      )

  if message['text'].startswith("Soumil:"):
    app.client.reactions_add(
        channel=message['channel'],
        timestamp=message['ts'],
        name='partysoumil',
    )

  if message['text'].startswith("Chris:"):
    app.client.reactions_add(
        channel=message['channel'],
        timestamp=message['ts'],
        name='party-chris',
    )  

  if message['text'].startswith("*Allocations") or message['text'].startswith("Allocations"):
    allocations = get_allocations(message['text'])
    if allocations is not None:
      say(
        text=allocations,
        username="Allocation Bot",
        icon_emoji=':cake:'
      )

@app.action("check-done")
def ActionDone(ack, body, respond):
    ack()
    response = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "✅ Awesome work!"
        }
    }
    blocks = body['message']['blocks']
    action = body['actions'][0]
    for (i, block) in enumerate(blocks):
      if block['block_id'] == action['block_id']:
        blocks[i] = response
    respond(
      replace_original=True,
      text="✅ Awesome work!",
      blocks=blocks,
    )
    ta, name, due_date = body['actions'][0]['value'].split('@')
    data = {
      'ta': ta,
      'name': name,
      'due_date': due_date,
    }
    requests.post(GOOGLE_SHEETS_ENDPOINT, data=data)

@app.action("check-snooze")
def ActionSnooze(ack, body, respond):
    ack()
    response = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "⌛ No worries, I will follow up with you tomorrow."
        }
    }
    blocks = body['message']['blocks']
    action = body['actions'][0]
    for (i, block) in enumerate(blocks):
      if block['block_id'] == action['block_id']:
        blocks[i] = response
    respond(
      replace_original=True,
      text="⌛ No worries, I will follow up with you tomorrow.",
      blocks=blocks,
    )
    ta, name, due_date = body['actions'][0]['value'].split('@')
    text = f"{body['user']['username']} ({ta}) snoozed a check."
    blocks = [
      {
          "type": "section",
          "text": {
              "type": "mrkdwn",
              "text": text
          }
      },
      {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Task:*\n{name}\n*Due Date:*\n{due_date}"
        },
      },
    ]
    app.client.chat_postMessage(
      channel=SNOOZE_CHANNEL_ID,
      text=text,
      blocks=blocks,
    )

@app.action("zoom")
def ActionZoom(ack):
  ack()

if __name__ == "__main__":
    app.start()