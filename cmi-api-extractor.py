#!/usr/bin/env python3

import sys
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

if len(sys.argv) != 6:
    print('Arguments not matching! Usage:')
    print(sys.argv[0] + ' <cmi_host> <cmi_username> <cmi_password> <cmi_id> <pushgateway_host>')
    sys.exit(1)

cmi_host = sys.argv[1]
cmi_username = sys.argv[2]
cmi_password = sys.argv[3]
cmi_id = sys.argv[4]
pushgateway_host = sys.argv[5]

metric_prefix = 'test_1_cmi'
metric_mapping_config = {
    "Logging Analog": {
        "1": {
            "metric": "collector_celsius"
        },
        "2": {
            "metric": "reservoir_celsius",
            "labels": {
                "layer": "top 1"
            }
        },
        "3": {
            "metric": "reservoir_celsius",
            "labels": {
                "layer": "bottom 2"
            }
        },
        "4": {
            "metric": "hot_water_circulation_celsius",
            "labels": {
                "direction": "flow"
            }
        },
        "5": {
            "metric": "solar_circulation_celsius",
            "labels": {
                "direction": "return"
            }
        },
        "7": {
            "metric": "solar_circulation_celsius",
            "labels": {
                "direction": "flow"
            }
        },
        "8": {
            "metric": "reservoir_celsius",
            "labels": {
                "layer": "top 2"
            }
        },
        "9": {
            "metric": "reservoir_celsius",
            "labels": {
                "layer": "middle 1"
            }
        },
        "10": {
            "metric": "reservoir_celsius",
            "labels": {
                "layer": "bottom 1"
            }
        },
        "11": {
            "metric": "boiler_circulation_celsius",
            "labels": {
                "direction": "flow"
            }
        },
        "12": {
            "metric": "outside_celsius"
        },
        "13": {
            "metric": "heating_circulation_celsius",
            "labels": {
                "direction": "flow"
            }
        },
        "14": {
            "metric": "reservoir_celsius",
            "labels": {
                "layer": "middle 2"
            }
        },
        "16": {
            "metric": "solar_circulation_flow_rate_lperh"
        },
        "17": {
            "metric": "boiler_circulation_flow_rate_lperh"
        },
        "18": {
            "metric": "boiler_circulation_celsius",
            "labels": {
                "direction": "return"
            }
        },
        "19": {
            "metric": "solar_power_kW"
        },
        "20": {
            "metric": "solar_energy_kWh_total"
        },
        "21": {
            "metric": "boiler_power_kW"
        },
        "22": {
            "metric": "boiler_energy_kWh_total"
        }
    },
    "Logging Digital": {
        "1": {
            "metric": "hot_water_circulation_pump_state"
        },
        "2": {
            "metric": "reservoir_charging_state",
            "labels": {
                "layer": "top"
            }
        },
        "3": {
            "metric": "reservoir_charging_state",
            "labels": {
                "layer": "middle"
            }
        },
        "4": {
            "metric": "solar_circulation_pump_state"
        },
        "6": {
            "metric": "boiler_circulation_pump_state"
        },
        "7": {
            "metric": "heating_circulation_pump_state"
        },
        "8": {
            "metric": "heating_circulation_mixer_state"
        },
        "9": {
            "metric": "heating_circulation_mixer_2_state"
        },
        "11": {
            "metric": "boiler_valve_state"
        },
        "16": {
            "metric": "solar_circulation_pump_2_state"
        }
    }
}

common_labels = {
    'instance': 'cmi',
    'cmi_id': cmi_id
}


def create_metrics(section: str, cmi_response_data, collector_registry: CollectorRegistry):

    logging_section = cmi_response_data[section]
    # print(logging_section)

    existing_metrics = {}

    for value in logging_section:
        # print('value:')
        # print(value)
        config_key = value['Number']

        if str(config_key) not in metric_mapping_config[section]:
            continue

        mapping_config = metric_mapping_config[section][str(config_key)]
        # print(mapping_config)

        labelnames = list(common_labels.keys())
        labels = common_labels

        if 'labels' in mapping_config:
            labelnames = labelnames + list(mapping_config['labels'].keys())
            labels = labels | mapping_config['labels']

        # print(labelnames)
        # print(labels)

        metric_name = mapping_config['metric']
        print(metric_name)

        if metric_name in existing_metrics:
            g = existing_metrics[metric_name]
        else:
            g = Gauge(mapping_config['metric'], 'test', namespace=metric_prefix, registry=collector_registry, labelnames=labelnames)
            existing_metrics[metric_name] = g

        g.labels(**labels).set(value['Value']['Value'])


# http://<host>:8080/INCLUDE/api.cgi?jsonnode=1&jsonparam=Ld
url = 'http://' + cmi_host + '/INCLUDE/api.cgi?jsonnode=1&jsonparam=La,Ld'
response = requests.get(url, auth=(cmi_username, cmi_password))
# print(response.text)

cmi_response = response.json()
# print(cmi_response)

registry = CollectorRegistry()

create_metrics('Logging Analog', cmi_response['Data'], registry)
create_metrics('Logging Digital', cmi_response['Data'], registry)

job_name = 'test_1_cmi_extractor'

push_to_gateway(pushgateway_host, job=job_name, registry=registry)
