import json


def getSitesFromJson(json_file_path):
    sites = []
    with open(json_file_path, "r") as f:
        data = json.load(f)
        # yield data
        for key, value in data.items():
            # yield value
            for site in value:
                sites.append(site["top_url"])
    return sites


if __name__ == "__main__":
    json_file_path = "/home/icespite/Work/Thesis/fingerprinting_domains.json"
    sites = getSitesFromJson(json_file_path)
    print(sites[:10])
