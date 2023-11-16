import argparse
import logging
import os
import time
from pathlib import Path

import pandas as pd
import tranco

from custom_command import LinkCountingCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager
from tool.extractUrl import getProcessedUrl
from tool.getSites import getSitesFromJson

parser = argparse.ArgumentParser()
parser.add_argument("--tranco", action="store_true", default=False),
args = parser.parse_args()
data_dir = Path("./datadir/")
url_log_path = data_dir / "url.log"
try:
    os.mkdir(data_dir)
    print("文件夹创建成功！")
except FileExistsError:
    print("文件夹已经存在！")

url_logging = logging.getLogger("url_logging")
url_logging.setLevel(logging.DEBUG)
url_logging.addHandler(logging.FileHandler(url_log_path))

# if args.tranco:
#     # Load the latest tranco list. See https://tranco-list.eu/
#     print("Loading tranco top sites list...")
#     t = tranco.Tranco(cache=True, cache_dir=".tranco")
#     latest_list = t.list()
#     sites = ["http://" + x for x in latest_list.top(20)]
#     # sites = ["http://" + x for x in latest_list][10:20000]
# else:
#     sites = []
#     reader = pd.read_csv("./.tranco/8284V-DEFAULT.csv")
#     # print(reader)
#     index = 9000
#     sum = 10000
#     for idx, data in reader.iterrows():
#         if index > 0:
#             index -= 1
#         else:
#             if sum > 0:
#                 sum -= 1
#                 sites.append("http://" + data[1])
#             else:
#                 break
sites = getSitesFromJson("/home/icespite/Work/Thesis/fingerprinting_domains.json")


# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams
NUM_BROWSERS = 6
manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses
    browser_param.http_instrument = True
    # Record cookie changes
    browser_param.cookie_instrument = True
    # Record Navigations
    browser_param.navigation_instrument = True
    # Record JS Web API calls
    browser_param.js_instrument = True
    # Record the callstack of all WebRequests made
    # browser_param.callstack_instrument = True
    # Record DNS resolution
    browser_param.dns_instrument = True
    browser_param.save_content = "beacon,csp_report,image,imageset,main_frame,media,object,object_subrequest,ping,script,stylesheet,sub_frame,web_manifest,websocket,xml_dtd,xmlhttprequest,xslt,other"
    browser_param.profile_archive_dir = Path("./datadir/profiles/")
    browser_param.proxy_ip = "127.0.0.1"
    browser_param.proxy_port = 7890

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
manager_params.memory_watchdog = True
manager_params.process_watchdog = True

success_sites = getProcessedUrl(url_log_path)
for site in success_sites:
    try:
        sites.remove(site)
    except ValueError:
        pass
print(sites[:20])

now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n"
# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite")),
    None,
) as manager:
    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran --->{'successfully' if success else 'unsuccessfully'}"
            )
            if success:
                url_logging.info(f"success: {val}")
            else:
                url_logging.info(f"fail: {val}")

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=index,
            callback=callback,
        )

        # Start by visiting the page
        command_sequence.append_command(GetCommand(url=site, sleep=30), timeout=120)
        # Have a look at custom_command.py to see how to implement your own command
        # command_sequence.append_command(LinkCountingCommand())

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
