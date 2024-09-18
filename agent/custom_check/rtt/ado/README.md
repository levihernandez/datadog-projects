# ADO, ODBC, SQL Server Custom Check in Datadog

* Install both the `conf.yaml` and `sqlserver_rtt.py`
* Divide metrics by `failure` or `success`
  ![](img/metrics.png)
* Use metrics generated by the `conf.yaml` to create monitors
  ![](img/tagging.png)
* create a monitor for the failures with rtt
  ![](img/fail-monitor.png)
* create a monitor for success with rtt
  ![](img/success-monitor.png)