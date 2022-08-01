# cmi-api-extractor

Extract data from TA's
[Control and Monitoring Interface (C.M.I)](https://www.ta.co.at/x2-bedienung-schnittstellen/cmi/).
The C.M.I. connects to a TA solar and heating control unit like the [UVR16x2](https://www.ta.co.at/x2-frei-programmierbare-regler/uvr16x2/)
and logs certain data values from the control unit's various inputs, outputs and buses.
The python script queries the [C.M.I.'s JSON API](https://wiki.ta.co.at/C.M.I._JSON-API) to retrieve data.

The data from the JSON API are mapped into metrics of a time series database. Currently only exporting
metrics to [Prometheus](https://prometheus.io/) via its [Pushgateway](https://github.com/prometheus/pushgateway/blob/master/README.md)
is supported. JSON API to metrics mapping is done via a config file.

A cron job can be used to periodically retrieve and update values.

## Prerequisits

* python3
* install required python libraries
  `pip install -r requirements.txt`
* running and reachable C.M.I.
* running and reachable Prometheus Pushgateway instance

## Usage

```shell
$ ./cmi-api-extractor.py <cmi_host> <cmi_username> <cmi_password> <cmi_id> <pushgateway_host> <job_name>
```

## Helpful Commands

* delete metric from prometheus pushgateway
  `curl -i -X DELETE http://<host>:9091/metrics/job/<job_name>`
* delete metric from prometheus
  `curl -X POST "http://<host>:9090/api/v1/admin/tsdb/delete_series?match[]=<metric_name>"`
* clean prometheus tombstones
  `curl -XPOST http://homecenter:9090/api/v1/admin/tsdb/clean_tombstones`

## Other Links

* [Technische Alternative (TA) website](https://www.ta.co.at/)
* [C.M.I. wiki entry](https://wiki.ta.co.at/C.M.I.)
* https://github.com/prometheus/pushgateway/blob/master/README.md#exposed-metrics
* https://prometheus.io/docs/practices/pushing/
* https://github.com/prometheus/client_python