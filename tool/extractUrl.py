import re


def getProcessedUrl(logfile):
    try:
        with open(logfile, "r") as f:
            strings = f.read()
        links = re.findall(
            r"success: (http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
            strings,
        )
        return links
    except FileNotFoundError:
        print("log文件不存在！")
        return []


if __name__ == "__main__":
    res = getProcessedUrl("/d/Work/thesis/OpenWPM/datadir/url.log")
    # print("http://www.google.com/" in res)
    print(res)
