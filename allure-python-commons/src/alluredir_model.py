import json
from os.path import join, isfile
from os import listdir
from collections import defaultdict


def load_from_json(files):
    datalist = []

    for file in files:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        datalist.append(data)

    return datalist


def remove_old(data_results):
    """ Keep only most recent test result for same test """

    # Group by historyId
    group = defaultdict(list)
    for item in data_results:
        group[item["historyId"]].append(item)

    for historyId, results in group.items():
        assert isinstance(results, list)
        if len(results) > 1:
            results.sort(key=lambda x: x["start"], reverse=True)
            # Now remove all items except first (most recent)
            results.pop(index=0)
            for item in results:
                data_results.remove(item)


def alluredir_model(alluredir, history=False):

    json_containers = [f for f in listdir(alluredir) if isfile(join(alluredir, f)) and "container" in f]
    json_results = [f for f in listdir(alluredir) if isfile(join(alluredir, f)) and "result" in f]

    data_containers = load_from_json(json_containers)
    data_results = load_from_json(json_results)

    # Reference parent containers from the test results
    for result in data_results:
        result["_parents"] = []
        for container in data_containers:
            if result["uuid"] in container.get("children", []):
                result["_parents"].append(container)

    if history is False:
        remove_old(data_results)

    return data_results
