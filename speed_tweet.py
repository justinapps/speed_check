"""
Send a complaint tweet to your ISP if your speed is below a certain threshold.
"""

#!/usr/bin/env python

import subprocess
import datetime
import json
import twitter

class SpeedTweet(object):
    """
    Check internet speed at given time intervals and sends a complaint
    tweet to the provider if speed is below a set threshold.
    """

    def __init__(self):

        self.download_threshold = 40

    def run_command(self, cmd, default_asserts=True):
        """
        Run commands.
        Returns std out, std error and return code.
        """
        child = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)

        result = child.communicate()
        exit_code = child.returncode
        std_out = result[0].decode('UTF-8').splitlines()
        std_err = result[1].decode('UTF-8').splitlines()

        if default_asserts:
            assert exit_code == 0
            assert std_err == []

        return std_out, std_err, exit_code

    def get_speed(self):
        """
        Uses speedtest-cli to perform a speedtest.
        Returns a dictionary with the current time and results.
        """
        std_out, _, _ = self.run_command("speedtest-cli --simple", default_asserts=True)
        print(std_out)

        current_ping = float(std_out[0].replace('Ping: ', '').replace(' ms', ''))
        current_download = float(std_out[1].replace('Download: ', '').replace(' Mbit/s', ''))
        current_upload = float(std_out[2].replace('Upload: ', '').replace(' Mbit/s', ''))

        return {'date': datetime.datetime.now(),
                'ping': current_ping,
                'download': current_download,
                'upload': current_upload}

    def send_tweet(self, tweet):
        """
        Takes a string as a parameter and uses the Twitter API to send a complaint.
        """
        with open('twitter_config.json') as json_data_file:
            data = json.load(json_data_file)

        api = twitter.Api(consumer_key=data["consumer_key"],
                          consumer_secret=data["consumer_secret"],
                          access_token_key=data["access_token_key"],
                          access_token_secret=data["access_token_secret"])
        api.PostUpdate(tweet)

    def check_threshold(self):
        """
        Takes dict with results and compares speed to the defined threshold.
        Sends tweet if threshold not met.
        """
        custom_tweet = "Your custom tweet here"
        results = self.get_speed()

        if results['download'] < self.download_threshold:
            print("Sending tweet...")
            self.send_tweet(custom_tweet)

if __name__ == "__main__":
    SPEED = SpeedTweet()
    SPEED.check_threshold()
