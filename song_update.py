import pandas as pd
import json

#### API INFO FOR MANUAL CONSOLE CALLS ##############################################
# link: https://open.spotify.com/playlist/37i9dQZF1EJHLNFgEksUus?si=ff8a0c2ae48c4205
#playlsit id: 37i9dQZF1EJHLNFgEksUus
# fields: items(added_by.id,track(name,href,album(name,href)))
#make sure you get like 100
####################################################################################

####### parse_item #######
# inputs: json dictionary item and a manual date
# outputs: a pandas series with all the song components organized
def parse_item(item, date):
    #important: these are the same as the pansas columns
    keyList  = ["song_name","song_id","album_name","album_id","added_by","first_appear"]

    # make a quick dictionary
    ret_dict = {key: None for key in keyList}
    ret_dict["song_name"] = item["track"]["name"]
    ret_dict["song_id"] = item["track"]["href"].rsplit('/', 1)[-1]
    ret_dict["album_name"] = item["track"]["album"]["name"]
    ret_dict["album_id"] = item["track"]["album"]["href"].rsplit('/', 1)[-1]
    ret_dict["added_by"] = item['added_by']['id']
    ret_dict["first_appear"] = date

    # but return it as a pandas series
    return pd.Series(ret_dict)

####### update_frame #######
# inputs: the temporary dataframe, the json file to pull from, and the manual date
# outputs: a whole dataframe for the current day's playlist
def update_frame(dataframe, json_input, date):
    # iterate through all of the songs in the json output
    for i in range(0,(len(json_input["items"]))):
        item = json_input["items"][i]
        # add thing from json to dataframe here
        current_length = len(dataframe)
        dataframe.loc[current_length + 1] = parse_item(item, date)
    dataframe.reset_index(drop=True)
    # and print the current playlist frame, for fun
    print(dataframe.to_markdown())
    return dataframe

####### get_user_input #######
# inputs: some user specified data
# outputs: a dictionary with that data
def get_user_input():
    print("Preapring to run dataset update:\n")

    # get date information
    print("What is the pull date for these songs?")
    pull_date = input()
    print("The date is", pull_date, "\n")

    # prep json data from the Spotify api
    print("What json file do they live in?")
    json_current = input()
    print("the json import is", json_current)
    j_open = open(json_current + ".json")
    json_c = json.load(j_open)
    print("successfully read new json file\n")

    # connect with a current dataset of songs
    print("What dataset should we append to? (include .csv)")
    current_set = input()
    print("the current dataset is", current_set)
    input_dict = {"date": pull_date, "jsonfile": json_c, "dataset" : current_set}
    return input_dict

####### extract_data #######
# inputs: the day's frame, and the input parameter dictionary
# outputs: none
# it only adds new rows to the specified dataset if they represent new songs
def extract_data(new_frame, input_dict):
    new_frame = update_frame(new_frame, input_dict["jsonfile"], input_dict["date"])
    current_frame = pd.read_csv(input_dict["dataset"])
    for i in range(len(new_frame)):
        songid = new_frame.iloc[i]["song_id"]
        if songid in current_frame['song_id'].values:
            print("song",i,"is already in there")
        else:
            print("i am adding a new song for", i)
            current_length = len(current_frame)
            current_frame.loc[current_length + 1] = new_frame.iloc[i]
            current_frame.reset_index(drop=True)
    current_frame.reset_index(drop=True)
    current_frame.to_csv(input_dict["dataset"], index=False)

if __name__ == "__main__":
    gameMainframe = pd.DataFrame(columns=["song_name", "song_id", "album_name", "album_id", "added_by", "first_appear"])
    extract_data(gameMainframe, get_user_input())

