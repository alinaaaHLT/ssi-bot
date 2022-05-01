import logging
import time
import json
# import torch
import requests
from configparser import ConfigParser
# from detoxify import Detoxify

from utils import ROOT_DIR

def query(payload, API_URL, headers):
    while True:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == requests.codes.ok:
            break
        else:
            # Not connected to internet maybe?
            logging.info('Unsuccessful request, status code '+ str(response.status_code))
            if response.status_code==400:
                print(headers)
                print(payload)
                break
            time.sleep(3)
    return response.json()

class ToxicityHelper():

    _detoxify = None
    # simplified using hitomi-team toxicity classifier
    _threshold_map = {'nsfw': 0.9, 'hate': 0.9, 'threat': 0.9}

    def __init__(self, config_section='DEFAULT'):
        logging.info('Initializing detoxify')
        self._config = ConfigParser()
        self._config.read(ROOT_DIR / 'ssi-bot.ini')
        self._headers = {"Authorization": "Bearer "+self._config['DEFAULT'].get('huggingface_token', None)}

        self.load_config_section(config_section)

        # cuda_available = torch.cuda.is_available()
        # self._detoxify = Detoxify('unbiased-small', device='cuda' if cuda_available else 'cpu')

    def _detoxify_predict(self, text):
        # max. BERT input is 512 tokens
        # the tokenization is a bit obscure to us so we'll use word-like thingies as a proxy
        # wordlike_list = text.split()
        # if len(wordlike_list)>500:
        #     logging.info(f"Big input, trimming...")
        #     text = " ".join(wordlike_list[:500])
        # logging.info('Running inference')
        payload = {"inputs": text}
        API_URL = "https://api-inference.huggingface.co/models/hitomi-team/discord-toxicity-classifier"
        output_list = query(payload, API_URL, self._headers)
        # logging.info('Query successful')
        return_dict = {}
        if len(output_list)!=1:
            print(output_list)
            return return_dict
        # logging.info('Parsing result')
        temp_results = output_list[0]
        return_dict = {'nsfw': 0, 'hate': 0, 'threat': 0}
        for result in temp_results:
            labelseq = json.loads(result['label'])
            score = result['score']
            return_dict['nsfw'] = return_dict['nsfw'] + result['score'] * labelseq[0]
            return_dict['hate'] = return_dict['hate'] + result['score'] * labelseq[1]
            return_dict['threat'] = return_dict['threat'] + result['score'] * labelseq[2]
        return return_dict

    def load_config_section(self, config_section):
        # This can be used to re-configure on the fly.
        logging.info(f"Configuring toxicity helper with section {config_section}...")

        for key in self._threshold_map:
            # Loop through all of the detoxify keys,
            # and see if one exists in the config section for this bot.
            # If so, then update the map.
            config_key = f"{key}_threshold"
            if config_key in self._config[config_section]:
                self._threshold_map[key] = self._config[config_section].getfloat(config_key)

    def text_above_toxicity_threshold(self, input_text):
        # logging.info(f"ToxicityHelper, testing {input_text}")

        try:
            results = self._detoxify_predict(input_text)
        except:
            logging.exception(f"Exception when trying to run detoxify prediction on {input_text}")

        # logging.info(f"ToxicityHelper, results are {results}")

        if self._threshold_map.keys() != results.keys():
            logging.warning(f"Detoxify results keys and threshold map keys do not match. The toxicity level of the input text cannot be calculated.")
            return True

        for key in self._threshold_map:
            if results[key] > self._threshold_map[key]:
                return True
