import os
import random
import requests
import json
import time
import urllib3
import sys

from dotenv import load_dotenv

# suppress unverified HTTPS request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(".env")

ALL_COLOURS = {
    "red": (0.77, 0.35),
    "green": (0.52, 0.82),
    "blue": (0.18, 0.18),
    "yellow": (0.53, 0.45),
    "white": (0.3, 0.3),
}

URL = "https://{}/clip/v2/resource/light/{}".format(
    os.environ.get("IP_ADDRESS"), os.environ.get("LIGHT_ID")
)
HEADERS = {"hue-application-key": "{}".format(os.environ.get("HUE_APPLICATION_KEY"))}

INTERVAL_TIME = 0.3

colour_order = []


def set_power_state(state: bool) -> dict:
    data = {"on": {"on": state}}
    return data


def set_brightness(level: float) -> dict:
    data = {"dimming": {"brightness": level}}
    return data


def serialise(*data_items: dict) -> json:
    data = {}
    for data_item in data_items:  # combine all dictionaries received
        data.update(data_item)
    return json.dumps(data)


def send_request(json_data: json) -> requests.Response:
    return requests.put(URL, headers=HEADERS, verify=False, data=json_data)


def generate_simon_colour() -> str:
    simon_colours = ALL_COLOURS.copy()
    simon_colours.pop("white")  # remove white to get the four Simon game colours
    simon_colours = list(simon_colours.keys())
    return random.choice(simon_colours)


def set_colour(colour: str, record: bool = True) -> dict:
    colour_obj = ALL_COLOURS[colour]
    colour_x = colour_obj[0]
    colour_y = colour_obj[1]
    data = {"color": {"xy": {"x": colour_x, "y": colour_y}}}
    # return colour name as well to record
    if record:
        record_colour(colour)
    return data


def set_default_state():
    request_data = serialise(
        set_power_state(True), set_colour("white", False), set_brightness(100)
    )  # ensure power is on!
    send_request(request_data)


def get_answer() -> list:
    os.system("clear")
    print(
        "Enter colours in correct order then hit Enter: (r)ed, (g)reen, (b)lue), (y)ellow"
    )
    answer_string = input()
    answer_list = []
    for char in answer_string:
        match char:
            case "r":
                answer_list.append("red")
            case "g":
                answer_list.append("green")
            case "b":
                answer_list.append("blue")
            case "y":
                answer_list.append("yellow")
            case _:
                print("Invalid character entered!")
                sys.exit(1)

    return answer_list


def record_colour(colour: str):
    colour_order.append(colour)


def start_game():
    game = True
    round = 1
    os.system("clear")
    set_default_state()
    print("Game will begin in three seconds")
    time.sleep(1)

    while game:
        os.system("clear")
        send_request(serialise(set_brightness(0)))
        time.sleep(INTERVAL_TIME)
        if round == 1:
            send_request(
                serialise(set_colour(generate_simon_colour()), set_brightness(100))
            )
            time.sleep(INTERVAL_TIME)
            send_request(serialise(set_brightness(0)))
        else:
            for colour in colour_order:
                send_request(serialise(set_colour(colour, False), set_brightness(100)))
                time.sleep(INTERVAL_TIME)
                send_request(serialise(set_brightness(0)))
                time.sleep(INTERVAL_TIME)
            send_request(
                serialise(set_colour(generate_simon_colour()), set_brightness(100))
            )
            time.sleep(INTERVAL_TIME)
        send_request(serialise(set_brightness(0)))
        time.sleep(INTERVAL_TIME)
        set_default_state()
        player_answer = get_answer()
        if player_answer == colour_order:
            round += 1
            os.system("clear")
            print("Correct!")
            print("Get ready for the next round...")
            time.sleep(1.5)
        else:
            game = False
            print("Incorrect!")
            print("Your answer: " + str(player_answer))
            print("Correct answer: " + str(colour_order))
            print("Final score: " + str(round - 1))
    colour_order.clear()
