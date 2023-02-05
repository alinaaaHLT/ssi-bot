import logging
import re

from configparser import ConfigParser

from utils import ROOT_DIR


class KeywordHelper():
    # These hard-coded negative keywords are used to prevent the bot posting distasteful stuff.
    # It's only inteded as a basic defence.
    # Operator should train their model to avoid falling back on this.
    _default_negative_keywords = [
        ('abor', 'tion'), ('antisemiti'), ('ar', 'yan'), ('ausch', 'witz'),
        ('beh', 'ead'), ('black', ' people'),
        ('child p', 'orn'), ('chi', 'nk'), ('clinton'), ('columbine'), ('concentrati', 'on camp'),
        ('da', 'go'), ('decapi', 'tat'),
        ('execution'),
        ('geno', 'cide'),
        ('hate', ' you'), ('hit', 'ler'), ('holo', 'caust'), ('homophob'),
        ('inc', 'est'), ('is', 'is'), ('israel'),
        ('jew', 'ish'), ('je', 'ws'), ('ji', 'had'),
        ('ki', 'ke'), ('kk', 'k'), ('kys'),
        ('lol', 'i'),
        ('maste', 'r race'), ('murder'), ('muslim'),
        ('nation', 'alist'), ('na', 'zi'), ('nig', 'ga'), ('nig', 'ger'),
        ('pae', 'do'), ('pak', 'i'), ('pale', 'stin'), ('ped', 'o'), ('putin'),
        ('rac' 'ist'), ('r', 'ape'), ('ra', 'pi'), ('ret', 'ard'),
        ('school ', 'shoot'), ('self harm'), ('semi', 'ti'), ('supremacy'),
        ('sp', 'ic'), ('swas', 'tika'),
        ('terr', 'oris'), ('tor', 'ture'), ('tra', 'nny'), ('trump'),
        ('white p', 'ower'),
        ('death'),
        ('fa', 'g'),
        ('fuck', 'off'),
    ]

    def __init__(self, config_key='DEFAULT'):

        self._config = ConfigParser()
        self._config.read(ROOT_DIR / 'ssi-bot.ini')

        self._positive_keywords = []
        self._negative_keywords = ["".join(s) for s in self._default_negative_keywords if s]

        # Append bot's custom positive keywords
        custom_positive_keywords_list = self._config[config_key].get('positive_keywords', '')
        if len(custom_positive_keywords_list) > 2:
            self._positive_keywords += [kw.strip() for kw in custom_positive_keywords_list.lower().split(',')]

        # Append bot's custom negative keywords
        custom_negative_keywords_list = self._config[config_key].get('negative_keywords', '')
        if len(custom_negative_keywords_list) > 2:
            self._negative_keywords += [kw.strip() for kw in custom_negative_keywords_list.lower().split(',')]

        # Loop through each keyword list and test the keyword can be compiled to a regex
        for l in [self._positive_keywords, self._negative_keywords]:
            for kw in l:
                if not self._test_keyword_is_compilable(kw):
                    logging.error(
                        f"Error in keyword {kw}. It will be removed. You may need to add regex escaping to the keyword.")
                    l.remove(kw)

    def _test_keyword_is_compilable(self, kw):
        try:
            re.compile("\b{}".format(kw), re.IGNORECASE)
            return True
        except re.error:
            return False

    def positive_keyword_matches(self, text):
        if self._positive_keywords:
            return [keyword for keyword in self._positive_keywords if
                    re.search(r"\b{}".format(keyword), text, re.IGNORECASE)]
        return []

    def negative_keyword_matches(self, text):
        # Negative keyword is matched with a starting boundary so basic word forms
        # like plurals are matched, for example humans and humanoid would both match for just the keyword human.
        if self._negative_keywords:
            return [keyword for keyword in self._negative_keywords if
                    re.search(r"\b{}".format(keyword), text, re.IGNORECASE)]
        return []
