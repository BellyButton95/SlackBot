import config
from slackclient import SlackClient

# Slack API JSON Fields
COLOR = "color"
FALLBACK = "fallback"
FIELDS = "fields"
PRETEXT = "pretext"
TITLE = "title"
TITLE_LINK = "title_link"

message_text = ""
slack_client = SlackClient(config.BOT_TOKEN)


def send_message(message):
    slack_client.api_call(config.API_POST, channel=config.SLACK_CHANNEL, text=message)


def send_attachment(pretext, color, title, title_link, attachment_fields):
    attachment = parse_attachment(pretext, color, title, title_link, attachment_fields)
    slack_client.api_call(config.API_POST, channel=config.SLACK_CHANNEL, attachments=attachment)


def parse_attachment(pretext, color, title, title_link, fields):
    attachment_json = []
    attachment_dict = {FALLBACK: "",
                       COLOR: color,
                       PRETEXT: pretext,
                       TITLE: title,
                       TITLE_LINK: title_link,
                       FIELDS: fields}
    attachment_json.append(attachment_dict)
    return attachment_json


# TODO
def parse_csv_file():
    return


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Slack Bot connected and ready to send messages!")
        fields = []
        for i in range(12):
            field = {"title": "Title", "value": "Value", "short": "true"}
            fields.append(field)

        print(send_attachment(config.MSG_SUMMARY,
                              config.MSG_COLOR,
                              "iCCI 50 Summary 06/07/2018",
                              "http://www.google.com",
                              fields))
    else:
        print("Error connecting to Salck please refer to the stacktrace")