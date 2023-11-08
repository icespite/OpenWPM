import re


def getProcessedUrl(logfile):
    with open(logfile, "r") as f:
        strings = f.read()
    links = re.findall(
        "(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
        strings,
    )
    return links


if __name__ == "__main__":
    res = getProcessedUrl("/d/Work/thesis/OpenWPM/datadir/successs.log")
    # print("http://www.google.com/" in res)
    print(res)
