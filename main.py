"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Andrew Pignataro, Kalai Shanmugam"
__contributors__ = "Mark McBride"
__email__ = "apignata@cisco.com, kmurugap@cisco.com, markmcbr@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import sys
import requests
import csv
from dotenv import load_dotenv
import os

# Load environment variable from .env file
load_dotenv()

# Access environment variable
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# (Optional) set account group name
Account_Group_Name = ""

def get_account_id(account_name):
    """
        API that returns account info
        :return: resp
    """
    try:
        url = "https://api.thousandeyes.com/v7/account-groups"
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/hal+json"}
        response = requests.request('GET', url, headers=headers)
        response.raise_for_status()
        resp = response.json()
        for acc in resp['accountGroups']:
            if acc['accountGroupName'] == account_name:
                return acc["aid"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return ""

def get_te_tests(aid):
    """
    API that returns configured tests and saved events.
    :return: resp
    """

    try:
        url = "https://api.thousandeyes.com/v7/tests"
        payload = None
        params = {"aid": f"{aid}"}
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/hal+json"}
        response = requests.request('GET', url, headers=headers, data=payload, params=params)
        response.raise_for_status()
        resp = response.json()
        temp_te_test_list = []
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        sys.exit()
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        sys.exit()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        sys.exit()
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit()

    # Loop through each test and create a list of dicts
    for test in resp['tests']:
        test_dict = {}
        test_dict["TestId"] = test['testId']
        test_dict["TestName"] = test['testName']
        test_dict["TeShared"] = test['liveShare']

        # Test Type
        if test['type'] == 'voice':
            test_dict["TestType"] = 'rtp-server'
        else:
            test_dict["TestType"] = test['type']
        if 'targetAgentId' in test.keys():
            test_dict["targetAgentId"] = test['targetAgentId']
        else:
            test_dict["targetAgentId"] = "NotApplicable"
        # Interval
        if 'interval' in test:
            test_dict["Interval"] = test['interval']
        else:
            test_dict["Interval"] = ""

        test_dict["AlertsEnabled"] = test['alertsEnabled']
        test_dict["Enabled"] = test['enabled']

        # Protocol
        if 'protocol' in test:
            test_dict["Protocol"] = test['protocol']
        else:
            test_dict["Protocol"] = ""

        # Created By
        if "createdBy" in test:
            test_dict["CreatedBy"] = test['createdBy']
        else:
            test_dict["CreatedBy"] = "unknown"

        # Created Date
        if "createdDate" in test:
            test_dict["CreatedDate"] = test['createdDate']
        else:
            test_dict["CreatedDate"] = "unknown"

        # Target
        if test['type'] == 'dns-server' or test['type'] == 'dns-trace' or test['type'] == 'dnssec':
            test_dict["Target"] = test['domain']
        elif test['type'] == 'agent-to-server':
            test_dict["Target"] = test['server']
        elif (test['type'] == 'page-load' or test['type'] == 'http-server' or test['type'] == 'api'
              or test['type'] == 'web-transactions' or test['type'] == 'ftp-server'):
            test_dict["Target"] = test['url']
        elif test['type'] == 'agent-to-agent' or test['type'] == 'voice':
            agent_name = agent_id_to_agent_name(test['targetAgentId'])
            test_dict["Target"] = agent_name
        elif test['type'] == 'bgp':
            test_dict["Target"] = test['prefix']
        elif test['type'] == 'sip-server':
            test_dict["Target"] = test['sipRegistrar'] + ':' + str(test['port'])
        else:
            test_dict["Target"] = 'unknown'

        # Amount of DNS servers check
        if test['type'] == 'dns-server':
            test_dict['servers'] = len(test['dnsServers'])
        else:
            test_dict['servers'] = "NotApplicable"

        # Time Load Limit
        if test['type'] == 'page-load':
            test_dict['timeout'] = test['pageLoadTimeLimit']
        elif test['type'] == "http-server":
            test_dict['timeout'] = test["httpTimeLimit"]
        elif test['type'] == "api":
            test_dict['timeout'] = test["timeLimit"]
        elif test['type'] == "web-transactions":
            test_dict['timeout'] = test["timeLimit"]
        elif test['type'] == "sip-server":
            test_dict['timeout'] = test["sipTimeLimit"]
        elif test['type'] == "ftp-server":
            test_dict['timeout'] = test["ftpTimeLimit"]
        else:
            test_dict['timeout'] = "NotApplicable"

        # Duration
        if test['type'] == "voice":
            test_dict["duration"] = test["duration"]
        else:
            test_dict["duration"] = "NotApplicable"

        # Throughput
        if test['type'] == "agent-to-agent":
            test_dict["Throughput"] = test["throughputMeasurements"]
            test_dict["direction"] = test["direction"]
            if "throughputDuration" in test.keys():
                test_dict["ThroughputDuration"] = test["throughputDuration"]
            else:
                test_dict["ThroughputDuration"] = "NotApplicable"
        else:
            test_dict["Throughput"] = "NotApplicable"
            test_dict["direction"] = "NotApplicable"
            test_dict["ThroughputDuration"] = "NotApplicable"

        temp_te_test_list.append(test_dict)  # append the test dict to a list

    resp.update({'tests': temp_te_test_list})  # update the dict with the list of test dicts
    return resp


def get_te_test_result(test_id, test_type):
    """
    Returns network test results for every agent and round.
    If you do not specify a window or a start and end date, data is displayed for the most recent testing round.
    :param test_id:
    :param test_type:
    :return: resp
    """

    try:
        url = f"https://api.thousandeyes.com/v7/test-results/{test_id}/{test_type}?window=2m"
        payload = None
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/hal+json"}
        response = requests.request('GET', url, headers=headers, data=payload)
        response.raise_for_status()
        resp = response.json()
        return resp
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        sys.exit()
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        sys.exit()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        sys.exit()
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit()


def get_enterprise_agent_list():
    """
    Returns a list of all Enterprise agents available to your ThousandEyes account,
    including both Enterprise and Cluster.
    :return: enterprise agents id list Ex:[12345, 67890]
    """

    try:
        url = "https://api.thousandeyes.com/v7/agents"
        payload = {}
        params = {"agentTypes": ["enterprise-cluster", "enterprise"]}
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/hal+json"}
        response = requests.request('GET', url, headers=headers, data=payload, params=params)
        response.raise_for_status()
        resp = response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        sys.exit()
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        sys.exit()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        sys.exit()
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit()

    ent_agent_ids = []
    for agents in resp['agents']:
        ent_agent_ids.append(agents['agentId'])

    return ent_agent_ids

def get_agent_type(agent_Id):
    """
    Find the type of agent 
    :return: agent type , cloud or enterprise
    """
    try:
        url = "https://api.thousandeyes.com/v7/agents"
        payload = {}
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/hal+json"}
        response = requests.request('GET', url, headers=headers, data=payload)
        resp = response.json()
        for agent in resp["agents"]:
            if agent["agentId"] == agent_Id:
                return agent["agentType"]
        else:
            return "NotApplicable"
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        sys.exit()
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        sys.exit()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        sys.exit()
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit()

def get_agent_count(test_result, enterprise_agent_list):
    """
    Finds the number of agents and locations for a test
    :param test_result:
    :param enterprise_agent_list:
    :return: TE dict with ex: CloudAgents: 2, CloudAgentList: ['San Francisco, CA', 'New York, NY']
    """

    # Create temp lists
    cloud_agent_id_list = []
    cloud_agent_name_list = []

    ent_agent_id_list = []
    ent_agent_name_list = []

    for result in test_result:
        # Check to see if the agent is an enterprise agent
        if result['agent']['agentId'] in enterprise_agent_list:
            # If enterprise agent is not already added: append to the list
            if result['agent']['agentId'] not in ent_agent_id_list:
                ent_agent_id_list.append(result['agent']['agentId'])
                ent_agent_name_list.append(result['agent']['agentName'])
        # If cloud agent is not already added: append to the list
        elif result['agent']['agentId']not in cloud_agent_id_list:
            cloud_agent_id_list.append(result['agent']['agentId'])
            cloud_agent_name_list.append(result['agent']['agentName'])

    # Counts the number of agents
    cloud_agent_count = int(len(cloud_agent_id_list))
    ent_agent_count = int(len(ent_agent_id_list))

    # Format the cloud and enterprise agents data
    agent = {'agent_count': cloud_agent_count, 'agent_ids': cloud_agent_id_list, 'agent_names': cloud_agent_name_list,
             'e_agent_count': ent_agent_count, 'e_agent_ids': ent_agent_id_list, 'e_agent_names': ent_agent_name_list}

    return agent


def agent_id_to_agent_name(agent_id):
    """
    Returns the name of an agent based on the agent id.
    :param agent_id:
    :return: agentName ex:12345 -> San Jose, CA
    """

    try:
        url = f"https://api.thousandeyes.com/v7/agents/{agent_id}"
        payload = {}
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/hal+json"}
        response = requests.request('GET', url, headers=headers, data=payload)
        response.raise_for_status()
        resp = response.json()
        return resp['agentName']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        sys.exit()
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        sys.exit()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        sys.exit()
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit()


def update_agent_count(te_test_dict, enterprise_agent_dict):
    """
    Updates a dictionary with a new entry for CloudAgents and CloudAgentsList
    :param enterprise_agent_dict:
    :param te_test_dict:
    :return: dict with Agent updates
    """
    i = 0
    for test in te_test_dict['tests']:
        # Check the test type
        if test['TestType'] == 'agent-to-server' or test['TestType'] == 'agent-to-agent':
            testtype = "network"
        else:
            testtype = test['TestType']

        # If test is not enabled set the values to 0 and empty string
        if not test["Enabled"]:
            te_test_dict['tests'][i]["CloudAgents"] = 0
            te_test_dict['tests'][i]["CloudAgentsList"] = ""
            te_test_dict['tests'][i]["EnterpriseAgent"] = 0
            te_test_dict['tests'][i]["EnterpriseAgentsList"] = ""
        elif test['TestType'] == 'bgp':
            te_test_dict['tests'][i]["CloudAgents"] = 0
            te_test_dict['tests'][i]["CloudAgentsList"] = ""
            te_test_dict['tests'][i]["EnterpriseAgent"] = 0
            te_test_dict['tests'][i]["EnterpriseAgentsList"] = ""
        else:
            # Get test results using the test id and test type for each test
            resp = get_te_test_result(test['TestId'], testtype)
            # Use the test results to get the agent count for each test
            agent = get_agent_count(resp['results'], enterprise_agent_dict)

            # Update cloud agents
            te_test_dict['tests'][i]["CloudAgents"] = agent["agent_count"]
            if agent["agent_count"] == 0:
                te_test_dict['tests'][i]["CloudAgentsList"] = ""
            else:
                te_test_dict['tests'][i]["CloudAgentsList"] = agent["agent_names"]

            # Update enterprise agents
            te_test_dict['tests'][i]["EnterpriseAgent"] = agent["e_agent_count"]
            if agent["e_agent_count"] == 0:
                te_test_dict['tests'][i]["EnterpriseAgentsList"] = ""
            else:
                te_test_dict['tests'][i]["EnterpriseAgentsList"] = agent["e_agent_names"]
        i += 1
    return te_test_dict


def convert_to_csv(te_dict):
    """
    Creates a filename.csv from a dict
    :param te_dict:
    :return: filename.csv
    """

    fieldnames = list(te_dict[0].keys())
    with open('te_report.csv', 'w', newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in te_dict:
            writer.writerow(row)
    print("OUTPUT saved in te_report.csv file successfully")


def round_num(num):
    """
    Round the given float number to whole integer
    :param float num:
    :return: whole integer
    """
    s_num = str(num)
    if '.' in s_num:
        id = s_num.split('.')
        if int(id[1][0]) >= 5:
            return int(id[0]) + 1
        else:
            return int(id[0])
    else:
        return s_num


def calculate_usage_manual(tests):
    """
    function calculates cost for all the tests
    :param tests:
    :return: tests with cost calculated
    """
    Units = {

        "Agent_to_Server": {"CloudAgent": 5, "EntAgent": 2.5},
        "Agent_to_Agent": {"CloudAgent": 5, "EntAgent": 2.5},
        "Agent_to_Agent_TE": {"EntAgent": 0.5},
        "DNS_Server": {"CloudAgent": 5, "EntAgent": 2.5},
        "Page_Load": {"CloudAgent": 1, "EntAgent": 0.5},
        "DNS_Trace": {"CloudAgent": 5, "EntAgent": 2.5},
        "HTTP_Server": {"CloudAgent": 1, "EntAgent": 0.5},
        "FTP_Server": {"CloudAgent": 1, "EntAgent": 0.5},
        "Voice_RTP": {"CloudAgent": 1, "EntAgent": 0.5},
        "Voice_SIP": {"CloudAgent": 1, "EntAgent": 0.5},
        "Web_Trans": {"CloudAgent": 1, "EntAgent": 0.5}
    }
    Agent_Server_Usage = 0
    DNS_Server_Usage = 0
    DNS_Trace_Usage = 0
    HTTP_Server_Usage = 0
    Page_Load_Usage = 0
    for test in tests["tests"]:
        TestType = test["TestType"]
        TestName = test["TestName"]
        TestId = test["TestId"]
        CloudAgents = test["CloudAgents"]
        EnterpriseAgents = test["EnterpriseAgent"]
        if test["TeShared"] == False:
            if test["TestType"] == "agent-to-server":
                Interval_in_Min = test["Interval"]/60
                Cloud_usage = (Units["Agent_to_Server"]["CloudAgent"] * (60/Interval_in_Min)*24*31 * test["CloudAgents"])/1000
                Enterprise_usage = (Units["Agent_to_Server"]["EntAgent"] * (60/Interval_in_Min)*24*31 * test["EnterpriseAgent"])/1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                Agent_Server_Usage = Agent_Server_Usage + Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}", end='\n')
            elif test["TestType"] == "dns-server":
                Interval_in_Min = test["Interval"]/60
                Cloud_usage = ((Units["DNS_Server"]["CloudAgent"]*test["servers"]) * (60/Interval_in_Min)*24*31 * test["CloudAgents"])/1000
                Enterprise_usage = ((Units["DNS_Server"]["EntAgent"]*test["servers"]) * (60/Interval_in_Min)*24*31 * test["EnterpriseAgent"])/1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                DNS_Server_Usage = DNS_Server_Usage + Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}", end='\n')
            elif test["TestType"] == "page-load":
                Interval_in_Min = test["Interval"]/60
                Cloud_usage = ((Units["Page_Load"]["CloudAgent"]*test["timeout"]) * (60/Interval_in_Min)*24*31 * test["CloudAgents"])/1000
                Enterprise_usage = ((Units["Page_Load"]["EntAgent"]*test["timeout"]) * (60/Interval_in_Min)*24*31 * test["EnterpriseAgent"])/1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                Page_Load_Usage = Page_Load_Usage + Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}", end='\n')
            elif test["TestType"] == "dns-trace":
                Interval_in_Min = test["Interval"] / 60
                Cloud_usage = (Units["DNS_Trace"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * test["CloudAgents"]) / 1000
                Enterprise_usage = (Units["DNS_Trace"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                DNS_Trace_Usage = DNS_Trace_Usage + Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}", end='\n')
            elif test["TestType"] == "http-server" or test["TestType"] == "api":
                Interval_in_Min = test["Interval"] / 60
                Cloud_usage = ((Units["HTTP_Server"]["CloudAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["CloudAgents"]) / 1000
                Enterprise_usage = ((Units["HTTP_Server"]["EntAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                HTTP_Server_Usage =  HTTP_Server_Usage + Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}", end='\n')
            elif test["TestType"] == "bgp":
                test["Monthly_usage"] = round_num(8 * (60/15 * 24 * 31)/1000)
                Monthly_usage = test["Monthly_usage"]
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "rtp-server":
                Interval_in_Min = test["Interval"] / 60
                Cloud_usage = ((Units["Voice_RTP"]["CloudAgent"] * test["duration"]) * (60 / Interval_in_Min) * 24 * 31 * test["CloudAgents"]) / 1000
                Enterprise_usage = ((Units["Voice_RTP"]["EntAgent"] * test["duration"]) * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "sip-server":
                Interval_in_Min = test["Interval"] / 60
                Cloud_usage = ((Units["Voice_SIP"]["CloudAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["CloudAgents"]) / 1000
                Enterprise_usage = ((Units["Voice_SIP"]["EntAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "web-transactions":
                Interval_in_Min = test["Interval"] / 60
                Cloud_usage = ((Units["Web_Trans"]["CloudAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["CloudAgents"]) / 1000
                Enterprise_usage = ((Units["Web_Trans"]["EntAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "ftp-server":
                Interval_in_Min = test["Interval"] / 60
                Cloud_usage = ((Units["FTP_Server"]["CloudAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["CloudAgents"]) / 1000
                Enterprise_usage = ((Units["FTP_Server"]["EntAgent"] * test["timeout"]) * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000
                Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                HTTP_Server_Usage = HTTP_Server_Usage + Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "agent-to-agent" and test["Throughput"] == False and test["direction"] == "bidirectional":
                Interval_in_Min = test["Interval"] / 60
                cloud_agents = test["CloudAgents"]
                ent_agents = test["EnterpriseAgent"]
                target_agent_type = get_agent_type(test['targetAgentId'])

                if cloud_agents == 0:
                    if target_agent_type == "cloud":
                        cloud_agents = 1
                        Cloud_usage = ((Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * cloud_agents) / 1000) * ent_agents
                        Enterprise_usage = (Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * ent_agents) / 1000
                        Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                    else:
                        Enterprise_usage = (Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * ent_agents) / 1000
                        Monthly_usage = round_num((Enterprise_usage) * 2)

                elif ent_agents == 0:
                    if target_agent_type == "enterprise":
                        ent_agents = 1
                        Cloud_usage = (Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * cloud_agents) / 1000
                        Enterprise_usage = (Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * ent_agents) / 1000 * cloud_agents
                        Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                    else:
                        cloud_usage = (Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * cloud_agents) / 1000
                        Monthly_usage = round_num((cloud_usage) * 2)
                else:
                    Cloud_usage = (Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * cloud_agents) / 1000
                    Enterprise_usage = (Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * ent_agents) / 1000
                    if target_agent_type == "enterprise":
                        target_usage = ((Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * (cloud_agents+ent_agents)) / 1000)
                    else:
                        target_usage = ((Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * (cloud_agents + ent_agents)) / 1000)
                    
                    Monthly_usage = round_num((Cloud_usage + Enterprise_usage + target_usage))
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "agent-to-agent" and test["Throughput"] == False and test["direction"] != "bidirectional":

                Interval_in_Min = test["Interval"] / 60
                cloud_agents = test["CloudAgents"]
                ent_agents = test["EnterpriseAgent"]
                target_agent_type = get_agent_type(test['targetAgentId'])
              
                if test["direction"] == "from-target":
                    if target_agent_type == "enterprise":
                        target_usage = ((Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * (cloud_agents + ent_agents)) / 1000)
                    else:
                        target_usage = ((Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * (cloud_agents + ent_agents)) / 1000)
                    Monthly_usage = round_num(target_usage)
                else:
                    Cloud_usage = (Units["Agent_to_Agent"]["CloudAgent"] * (60 / Interval_in_Min) * 24 * 31 * cloud_agents) / 1000
                    Enterprise_usage = (Units["Agent_to_Agent"]["EntAgent"] * (60 / Interval_in_Min) * 24 * 31 * ent_agents) / 1000
                    Monthly_usage = round_num(Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "agent-to-agent" and test["Throughput"] == True and test["direction"] == "bidirectional":
                Interval_in_Min = test["Interval"] / 60
                Duration = int(test["ThroughputDuration"]) / 1000
                Cloud_usage = 0
                Enterprise_usage = round_num((Units["Agent_to_Agent_TE"]["EntAgent"] * Duration * (60 / Interval_in_Min) * 24 * 31 *test["EnterpriseAgent"]) * 2/ 1000)
                Monthly_usage = (Cloud_usage + Enterprise_usage)
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            elif test["TestType"] == "agent-to-agent" and test["Throughput"] == True and test["direction"] != "bidirectional":
                Interval_in_Min = test["Interval"] / 60
                Duration = int(test["ThroughputDuration"]) / 1000
                Cloud_usage = 0
                Enterprise_usage = round_num((Units["Agent_to_Agent_TE"]["EntAgent"] * Duration * (60 / Interval_in_Min) * 24 * 31 * test["EnterpriseAgent"]) / 1000)
                Monthly_usage = Cloud_usage + Enterprise_usage
                test["Monthly_usage"] = Monthly_usage
                #print(f"{TestType=} {TestName=} {TestId=} {CloudAgents=} {EnterpriseAgents=} {Monthly_usage=}",end='\n')
            else:
                test["Monthly_usage"] = 0
            del test["servers"]
            del test["timeout"]
            del test["duration"]
            del test["Throughput"]
            del test["direction"]
            del test["ThroughputDuration"]
            del test["targetAgentId"]
        else:
            test["Monthly_usage"] = 0
            del test["servers"]
            del test["timeout"]
            del test["duration"]
            del test["Throughput"]
            del test["direction"]
            del test["ThroughputDuration"]
            del test["targetAgentId"]
    #print(f"{Agent_Server_Usage=} {DNS_Server_Usage=} {DNS_Trace_Usage=} {Page_Load_Usage=} {HTTP_Server_Usage=}")
    return tests

# ===========================================================================================================


if __name__ == "__main__":
    if Account_Group_Name != "":
        AID = get_account_id(Account_Group_Name)
    else:
        AID = ""
    te_tests = get_te_tests(AID)
    enterprise_agent_list = get_enterprise_agent_list()
    te_updated_tests = update_agent_count(te_tests, enterprise_agent_list)
    te_updated_tests = calculate_usage_manual(te_updated_tests)
    convert_to_csv(te_updated_tests["tests"])
