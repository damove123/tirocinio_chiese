from firebase import firebase
import pandas as pd
from tqdm import tqdm
import csv


def getGroup(groupName):
    """
    Returns all the "ck_id"s of the members of a group as a list
    :param groupName: name of the group
    :return: a list of "ck_id"s
    """
    firebase_url = 'https://cityknowledge.firebaseio.com'
    fbase = firebase.FirebaseApplication(firebase_url, None)
    result = fbase.get('/groups', groupName)
    return list(result['members'].keys())


def getData(ck_id_list):
    """
    Returns a list of data points given a ck_id along with images
    :param ck_id_list: list of "ck_id"s
    :return: a list of data (dictionaries) for each ck_id
    """
    firebase_url = 'https://cityknowledge.firebaseio.com'
    fbase = firebase.FirebaseApplication(firebase_url, None)
    allData = []
    for ck_id in tqdm(ck_id_list):
        result = fbase.get('/data', ck_id)
        try:
            for index, key in enumerate(result['media']['images'].keys()):
                result['media' + str(index)] = result['media']['images'][key]
            del result['media']
        except:
            pass
        allData.append(flatten_dict(result))
    return allData


def flatten_dict(input_dict, parent_key='', sep='_'):
    flattened_dict = {}
    for key, value in input_dict.items():
        new_key = f'{parent_key}{sep}{key}' if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, sep='_'))
        else:
            flattened_dict[new_key] = value
    return flattened_dict


def JtoCSV(dataList, filepath):
    l = 0
    for dic in data:
        if len(dic.keys()) > l:
            l = len(dic.keys())
            biggestDic = dic

    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = biggestDic.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Write header
        writer.writeheader()
        # Write data
        for row in dataList:
            writer.writerow(row)

    print("finished writing to file: " + filepath)


"""
group_name = "MARB%20Artifacts"
ck_id_list = getGroup(group_name)
data = getData(ck_id_list)
for artifact in data:
    try:
        print(artifact["media0_medium"])
    except:
        continue
print(data[0].keys())

csvfile = pd.read_csv("Churches_B12_Complete_Gathered_Church_Information - CSV sheet.csv")
print(csvfile.head(5))

"""


def replace(string: str):
    return string.replace(' ', '%20')


def get_artifact_group(church_name):
    immagini_reperti = []

    church_data = pd.read_csv('Churches.csv')
    # Ricerca della riga corrispondente al nome della chiesa inserito

    artifact_info = church_data[church_data['Local Name'].str.contains(church_name, case=False, na=False)]
    if artifact_info.empty:
        return None
    else:
        # Estrai solo il contenuto dell'ultima colonna
        ultima_colonna = church_data.columns[-1]
        artifact_info = artifact_info[ultima_colonna]

    print(artifact_info)


get_artifact_group('Le Cappuccine')


