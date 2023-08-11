"""Verify if a vSAN datastore exists on the domain and cluster on a specific vSphere"""

import pytest
import logging
from dell.tsb.sdk.adapter.pytest.qtest import qtest
from dell.tsb.sdk.core.utils.loader import validate_testcase_data

log = logging.getLogger(__name__)

schema = {
    "type": "object",
    "properties": {
        "domain": {
            "type": "string",
        },
        "cluster": {
            "type": "string",
        },
        "datastore": {
            "type": "string",
        },
        "devices": {
            "type": "array",
        },
    },
    "required": [
        "domain",
        "cluster",
        "datastore",
        "devices",
    ],
    "additionalProperties": False,
}


@validate_testcase_data(schema)
@qtest({'project_id': '154',
        'testcase_id': 'TC-577',
        'testcase_version': '1.0'})
@pytest.mark.all_ndc
@pytest.mark.vsan_ndc
@pytest.mark.IaaS
def test_vsan_datastore(testbed, device, testcase_data):
    """
    Verify if a vSAN datastore exists on the domain and cluster on a specific vSphere

    Steps:
        Step 1: Collect the vSAN host
        Step 2: Collect the datastore for each of these hosts
        Step 3: Verify if a specific datastore exists
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

    content = device.rest.RetrieveContent()
    hosts = content.rootFolder.childEntity[0].hostFolder
    childentity = hosts.childEntity

    log.info(f"Verifying if vSAN datastore '{testcase_data['datastore']}' exists on the domain "
             f"'{testcase_data['domain']}; cluster 'testcase_data['cluster']' on the device"
             f"  '{device.name}'")

    error_msgs = []
    pass_msgs = []
    for ce in childentity:
        if testcase_data['domain'] + '-' + testcase_data['cluster'] in ce.name:
            for host in ce.host:
                for ds in host.datastore:
                    if f"{testcase_data['domain']}-{testcase_data['datastore']}" in ds.name:
                        # Found it
                        pass_msgs.append(f"Datastore '{testcase_data['datastore']}'"
                                         f" exists on the host '{host.name}'; domain "
                                         f"'{testcase_data['domain']}'; cluster "
                                         f"'{testcase_data['cluster']}'")
                    else:
                        error_msgs.append(f"Datastore '{testcase_data['datastore']}' does not "
                                          f"exists on the host '{host.name}'; domain "
                                          f"'{testcase_data['domain']}'; cluster"
                                          f" '{testcase_data['cluster']}'")
            break
    else:
        raise Exception(f"Datastore '{testcase_data['datastore']}' does not exists on the domain "
                        f"'{testcase_data['domain']}'; cluster '{testcase_data['cluster']}'")

    if pass_msgs and len(error_msgs) == 0:
        log.info('\n'.join(pass_msgs))
    else:
        log.info('\n'.join(pass_msgs))
        raise Exception('\n'.join(error_msgs))
        
#----------------------------------------------------------------------------------------------

# https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/blob/dev/bhushan/testcases/testcases/vSAN/test_vsan_datastore.py

# PR : https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/pull/7
        
        
