import unittest
import urllib3
import simon
from unittest.mock import patch


class TestSimon(unittest.TestCase):

    def test_set_power_state(self):
        data = simon.set_power_state(False)
        self.assertDictEqual(data, {"on": {"on": False}})
        data = simon.set_power_state(True)
        self.assertDictEqual(data, {"on": {"on": True}})

    def test_set_brightness(self):
        data = simon.set_brightness(100)
        self.assertDictEqual(data, {"dimming": {"brightness": 100}})
        data = simon.set_brightness(0)
        self.assertDictEqual(data, {"dimming": {"brightness": 0}})

    def test_serialise(self):
        output = simon.serialise({"dimming": {"brightness": 100}}, {"on": {"on": True}})
        self.assertEqual(output, '{"dimming": {"brightness": 100}, "on": {"on": true}}')

    def test_send_request(self):
        # suppress unverified HTTPS request warning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        res = simon.send_request('{"dimming": {"brightness": 100}, "on": {"on": true}}')
        self.assertEqual(200, res.status_code)

    def test_generate_simon_colour(self):
        output = simon.generate_simon_colour()
        self.assertIn(output, ["red", "green", "blue", "yellow"])

    def test_set_colour(self):
        output0 = simon.set_colour("blue", False)
        self.assertDictEqual(
            output0,
            {
                "color": {
                    "xy": {
                        "x": simon.ALL_COLOURS["blue"][0],
                        "y": simon.ALL_COLOURS["blue"][1],
                    }
                }
            },
        )

    # patching due to input() call in function
    @patch("builtins.input", return_value="r")
    def test_get_answer0(self, patched_input):
        output = simon.get_answer()
        self.assertListEqual(output, ["red"])

    # patching due to input() call in function
    @patch("builtins.input", return_value="rgy")
    def test_get_answer1(self, patched_input):
        output = simon.get_answer()
        self.assertListEqual(output, ["red", "green", "yellow"])


if __name__ == "__main__":
    unittest.main()
