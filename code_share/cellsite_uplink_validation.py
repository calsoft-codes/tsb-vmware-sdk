"""Validate if the vsphere cellsite uplink is assigned to correct vmnic"""

import pytest
import logging
from dell.tsb.sdk.adapter.pytest.qtest import qtest
from dell.tsb.sdk.core.utils.loader import validate_testcase_data

log = logging.getLogger(__name__)

schema = {
    "type": "object",
    "properties": {
        "expected_dvs": {
            "type": "string",
        },
        "expected_vmnic": {
            "type": "string",
        },
        "devices": {
            "type": "array",
        },
    },
    "required": [
        "expected_dvs",
        "expected_vmnic",
        "devices",
    ],
    "additionalProperties": False,
}


@validate_testcase_data(schema)
@qtest({'project_id': '9321231',
        'testcase_id': 'TC-2256',
        'testcase_version': '1.0'})
@pytest.mark.all
@pytest.mark.esxi
@pytest.mark.api
@pytest.mark.IaaS
def test_vsphere_cellsite_uplink_validation(testbed, device, testcase_data):
    """
    Validate if the vsphere cellsite uplink is assigned to correct vmnic

    Steps:
        Step 1: Collect the uplink information
        Step 2: Verify if the expected uplink is assigned to correct vmnic
    Args:
        testbed ('object'): testbed object
        device ('str'): device name to use for this testcase
        testcase_data ('object'): testcase_data object
    Returns:
        None
    Owner:
        otel.sdk@dell.com
    Execution time:
        5 seconds
    """

    if device not in testbed.devices:
        raise Exception(f"Device '{device}' does not exists in the testbed")
    device = testbed.devices[device]
    log.info(f"Verifying if the vCenter '{device.name}' contains the dvs named "
             f"'{testcase_data['expected_dvs']}' and vmnic '{testcase_data['expected_vmnic']}'")
    all_dvs = device.find_api("dell.tsb.sdk.common.libs",
                              "get", api="get_cellsite_uplink_validation")
    for dvs in all_dvs:
        if str(dvs.name) == testcase_data['expected_dvs']:
            vmnic = device.find_api("dell.tsb.sdk.common.libs",
                                    "get", api="get_cellsite_vmnic", dvs=dvs)
            if testcase_data['expected_vmnic'] != vmnic:
                raise Exception(f"vCenter's '{dvs.name}' contains vmnic "
                                f"{vmnic} ; expected: '{testcase_data['expected_vmnic']}'")
            else:
                log.info(f"vCenter {device.name} contains dvs name '{dvs.name}' with correct vmnic "
                         f"named '{testcase_data['expected_vmnic']}'")
                         
 # ---------------------------------------------------------------------------
 
 # https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/blob/dev/harish/cellsite/testcases/cell_site/test_vsphere_cellsite_uplink_validation.py
 # PR : https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/pull/21