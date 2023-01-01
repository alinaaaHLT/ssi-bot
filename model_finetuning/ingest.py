from os import walk
import os
from db import (Comment as db_Comment, Submission as db_Submission)
from db import create_tables
import html
import json

mypath = "json_data\\"
fullpath_json = {}
counter = 0
verbose = True


def main():
    for path in os.listdir(mypath):
        # check if current path is a file
        if not os.path.isfile(os.path.join(mypath, path)):
            subdict = {}
            fullpath_json[path] = subdict
            sr_path = mypath + path + "\\"
            counter = 0

            for json_path in os.listdir(sr_path):
                test = (os.path.join(sr_path, json_path))
                if os.path.isfile(os.path.join(sr_path, json_path)):
                    fullpath_json[path][counter] = sr_path + json_path
                    counter = counter+1
                    print(sr_path + json_path)

    create_tables()

    for sub in fullpath_json:
        for thing in fullpath_json[sub]:
            try:
                json_path = fullpath_json[sub][thing]

                data = None

                try:
                    # Fixes a bug that stops the code when there is an empty/invalid JSON leftover
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        try:
                            for json_item in data['data']:

                                if 'body' in json_item:
                                    # if 'body' is present then assume it's a comment
                                    test = None
                                    test = json_item['body']
                                    if isinstance(test, type(None)):
                                        print(test)
                                        continue
                                    db_record = db_Comment.get_or_none(db_Comment.id == json_item['id'])

                                    if not db_record:

                                        json_item['body'] = clean_text(json_item['body'])
                                        try:
                                            test = json_item['body'].startswith('[')
                                        except:
                                            print("*")
                                        # Try to detect whether the comment is a URL only with no text so we can ignore it later
                                        json_item['is_url_only'] = (json_item['body'].startswith('[') and json_item['body'].endswith(')')) \
                                                                   or ('http' in json_item['body'].lower() and ' ' not in json_item['body'])

                                        db_record = db_Comment.create(**json_item)
                                        if verbose:
                                            print(f"comment {json_item['id']} written to database")

                                elif 'selftext' in json_item:
                                    # if 'selftext' is present then assume it's a submission
                                    db_record = db_Submission.get_or_none(db_Submission.id == json_item['id'])

                                    if not db_record:

                                        json_item['selftext'] = clean_text(json_item['selftext'])

                                        db_record = db_Submission.create(**json_item)
                                        if verbose:
                                            print(f"submission {json_item['id']} written to database")
                        except:
                            print('Decoding JSON has failed')
                except:
                    print('Decoding JSON has failed')
            except ValueError:
                print('Decoding JSON has failed')
    print("Done")

def clean_text(text):
	# have to unescape it twice, for reason I don't fully understand
	text = html.unescape(text)
	text = html.unescape(text)
	# Strip and whitespace off of the end
	text = text.strip()

	return text

if __name__ == '__main__':
	main()