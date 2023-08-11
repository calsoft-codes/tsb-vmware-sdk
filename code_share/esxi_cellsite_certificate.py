"""Validate esxi can generate certificate correctly"""
import pytest
import logging
import polling2
import paramiko
from dell.tsb.sdk.adapter.pytest.qtest import qtest
from dell.tsb.sdk.core.utils.loader import validate_testcase_data

log = logging.getLogger(__name__)

schema = {
    "type": "object",
    "properties": {
        "max_stabilize_time": {
            "type": "number",
        },
        "sleep_stabilize_time": {
            "type": "number",
        },
        "devices": {
            "type": "array",
        },
    },
    "required": [
        "max_stabilize_time",
        "sleep_stabilize_time",
        "devices",
    ],
    "additionalProperties": False,
}


@validate_testcase_data(schema)
@qtest({'project_id': '9321231',
        'testcase_id': 'TC-2338',
        'testcase_version': '1.0'})
@pytest.mark.all
@pytest.mark.esxi
@pytest.mark.cli
@pytest.mark.IaaS
def test_esxi_cellsite_certificate(testbed, device, testcase_data):
    """
    Validate esxi can generate certificate correctly

    Steps:
        Step 1: Generate a Certificate
        Step 2: Restart process hostd and vpxa
        Step 3: Validate esxcli is stabilized after restarting both processes
    Args:
        testbed ('object'): testbed object
        device ('str'): device name to use for this testcase
        testcase_data ('object'): testcase_data object
    Returns:
        None
    Owner:
        otel.sdk@dell.com
    Execution time:
        25 seconds
    """

    if device not in testbed.devices:
        raise Exception(f"Device '{device}' does not exists in the testbed")
    device = testbed.devices[device]

    log.info(f"Verify successful generation of a certificate on the esxi device '{device.name}'")
    try:
        device.find_api("dell.tsb.sdk.common.libs", "get", api="generate_certificates")
    except Exception:
        raise Exception(f"The generation of a certificate on the esxi device"
                        f" '{device.name}' is failed")

    log.info("Certificate has been generated correctly")

    log.info("Verify esxcli system stability after restarting the processes")
    total_time = testcase_data['max_stabilize_time']
    sleep_time = testcase_data['sleep_stabilize_time']

    try:
        polling2.poll(lambda: device.find_api("dell.tsb.sdk.common.libs", "get",
                                              api="get_ntp_status"),
                      step=sleep_time, timeout=total_time,
                      ignore_exceptions=paramiko.ssh_exception.SSHException)
    except polling2.TimeoutException:
        raise Exception('esxcli system has not re-stabilized, future testcase could be affected')

    log.info("esxcli system has been re-stabilized")
    
# ----------------------------------------------------------------------------------------------
# https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/blob/dev/sudhita/cellsite/testcases/cell_site/test_esxi_cellsite_certificate.py
# PR : https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/pull/22