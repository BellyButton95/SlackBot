import config
import datetime
from slackclient import SlackClient
import pandas

# Slack API JSON Fields
COLOR = "color"
FALLBACK = "fallback"
FIELDS = "fields"
FOOTER = "footer"
PRETEXT = "pretext"
TITLE = "title"
SHORT = "short"
TITLE_LINK = "title_link"
TRUE = "true"
VALUE = "value"

# Slack Summary Headers
EXPECTED_PAYOFF = "Expected Payoff"
GROSS_LOSS = "Gross Loss"
GROSS_PROFIT = "Gross Profit"
INITIAL_DEPOSIT = "Initial Deposit"
LOSS_TRADES = "Loss Trades (% of Total)"
PROFIT_FACTOR = "Profit Fator"
PROFIT_TRADES = "Profit Trades (% of Total)"
TOTAL_TRADES = "Total Trades"
TOTAL_PROFIT = "Total Net Profit"


message_text = ""
slack_client = SlackClient(config.BOT_TOKEN)


def send_message(message):
    slack_client.api_call(config.API_POST, channel=config.SLACK_CHANNEL, text=message)


def send_attachment(pretext, color, title, title_link, attachment_fields, footer):
    attachment = parse_attachment(pretext, color, title, title_link, attachment_fields, footer)
    slack_client.api_call(config.API_POST, channel=config.SLACK_CHANNEL, attachments=attachment)


def parse_attachment(pretext, color, title, title_link, fields, footer):
    attachment_json = []
    attachment_dict = {FALLBACK: "",
                       COLOR: color,
                       PRETEXT: pretext,
                       TITLE: title,
                       TITLE_LINK: title_link,
                       FIELDS: fields,
                       FOOTER: footer}
    attachment_json.append(attachment_dict)
    return attachment_json


def generate_fields_from_csv(csv_file_name):
    data_frame = pandas.read_csv(csv_file_name, header=1)
    data_frame_title = pandas.read_csv(csv_file_name)

    total_trades = calculate_total_trades(data_frame)
    total_trades_json = {TITLE: TOTAL_TRADES, VALUE: str(total_trades), SHORT: TRUE}

    profit_trades = calculate_profit_trades(data_frame)
    profit_trades_json = {TITLE: PROFIT_TRADES, VALUE: str(profit_trades) + " (" + str(round(profit_trades/total_trades*100, 2)) + "%)", SHORT: TRUE}
    loss_trades = calculate_loss_trades(data_frame)
    loss_trades_json = {TITLE: LOSS_TRADES, VALUE: str(loss_trades) + " (" + str(round(loss_trades/total_trades*100, 2)) + "%)", SHORT: TRUE}

    gross_profit = calculate_gross_profit(data_frame)
    gross_profit_json = {TITLE: GROSS_PROFIT, VALUE: str(round(gross_profit, 2)), SHORT: TRUE}
    gross_loss = calculate_gross_loss(data_frame)
    gross_loss_json = {TITLE: GROSS_LOSS, VALUE: str(round(gross_loss, 2)), SHORT: TRUE}

    total_net_profit = gross_profit - abs(gross_loss)
    total_net_profit_json = {TITLE: TOTAL_PROFIT, VALUE: str(round(total_net_profit, 2)), SHORT: TRUE}

    profit_factor = gross_profit / abs(gross_loss)
    profit_factor_json = {TITLE: PROFIT_FACTOR, VALUE: str(round(profit_factor, 2)), SHORT: TRUE}

    expected_payoff = total_net_profit / total_trades
    expected_payoff_json = {TITLE: EXPECTED_PAYOFF, VALUE: str(round(expected_payoff, 2)), SHORT: TRUE}

    initial_deposit = calculate_initial_deposit(data_frame)
    initial_deposit_json = {TITLE: INITIAL_DEPOSIT, VALUE: str(round(initial_deposit, 2)), SHORT: TRUE}

    json_fields = [total_net_profit_json, total_trades_json, gross_profit_json, gross_loss_json,
                   profit_trades_json, loss_trades_json, profit_factor_json, expected_payoff_json, initial_deposit_json]

    return json_fields, data_frame_title.columns[0]


def calculate_total_trades(data_frame):
    return data_frame[config.PROFIT].count()


def calculate_loss_trades(data_frame):
    return data_frame.loc[data_frame[config.PROFIT] < 0, config.PROFIT].count()


def calculate_profit_trades(data_frame):
    return data_frame.loc[data_frame[config.PROFIT] >= 0, config.PROFIT].count()


def calculate_gross_profit(data_frame):
    return data_frame.loc[data_frame[config.PROFIT] > 0, config.PROFIT].sum()


def calculate_gross_loss(data_frame):
    return data_frame.loc[data_frame[config.PROFIT] < 0, config.PROFIT].sum()


def calculate_initial_deposit(data_frame):
    first_profit = data_frame[config.PROFIT][0]
    if first_profit >= 0:
        return data_frame[config.ACCOUNT_BALANCE][0]-first_profit
    else:
        return data_frame[config.ACCOUNT_BALANCE][0]+abs(first_profit)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Slack Bot connected and ready to send messages!")
        fields = []
        for file_name in config.CSV_FILES:
            fields, title = generate_fields_from_csv(file_name)
            send_attachment(config.MSG_SUMMARY,
                            config.MSG_COLOR,
                            title + " " + str(datetime.date.today()),
                            "http://www.google.com",
                            fields,
                            config.MSG_FOOTER)
    else:
        print("Error connecting to Slack please refer to the stacktrace")
