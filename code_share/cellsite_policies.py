"""Validate the management portgroup created on vcenter"""

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
        "expected_portgroup": {
            "type": "string",
        },
        "expected_vlan": {
            "type": "string",
        },
        "expected_loadbalance": {
            "type": "string",
        },
        "expected_uplinks": {
            "type": "string",
        },
        "devices": {
            "type": "array",
        },
    },
    "required": [
        "expected_dvs",
        "expected_portgroup",
        "expected_vlan",
        "expected_loadbalance",
        "expected_uplinks",
        "devices",
    ],
    "additionalProperties": False,
}


@validate_testcase_data(schema)
@qtest({'project_id': '9321231',
        'testcase_id': 'TC-2254',
        'testcase_version': '1.0'})
@pytest.mark.all
@pytest.mark.esxi
@pytest.mark.api
@pytest.mark.IaaS
def test_vsphere_cellsite_policies(testbed, device, testcase_data):
    """
    Validate if the Vcenter cellsite host status is as expected

    Steps:
        Step 1: Collect the vsphere cellsite host status
        Step 2: Verify if the expected cellsite host status as expected
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
    log.info("Verifying management port group is created under cell-site with required policies")
    distributedVSwitch = device.find_api("dell.tsb.sdk.common.libs",
                                         "get", api="get_cellsite_policies")
    errorFlag = 0
    for dvs in distributedVSwitch:
        if str(dvs.name) == testcase_data['expected_dvs']:
            dvsconfig = dvs.config
            dvscapability = dvs.capability
            dvsuplinks = dvsconfig.uplinkPortPolicy.uplinkPortName
            loadbalance = dvscapability.featuresSupported
            notify_switch = dvs.config.defaultPortConfig.uplinkTeamingPolicy.notifySwitches
            fail_back = dvs.config.defaultPortConfig.uplinkTeamingPolicy.reversePolicy
            expected_portgroup = testcase_data['expected_portgroup']
            for portgroup in dvs.portgroup:
                if str(portgroup.name) == expected_portgroup:
                    log.info(f"Expected portgroup is {expected_portgroup}")
                    dvsconfigvlan = portgroup.config.defaultPortConfig.vlan
                    if dvsconfigvlan.vlanId == testcase_data['expected_vlan']:
                        log.info("Expected VLAN ID {} is assigned"
                                 .format(testcase_data['expected_vlan']))
                    else:
                        errorFlag += 1
                        log.info(f"Expected VLAN ID is not assigned, Expected is "
                                 f"{testcase_data['expected_vlan']} ,"
                                 f"actual is : {dvsconfigvlan.vlanId}")
                else:
                    log.info("Expected portgroup not in list.")
            if testcase_data['expected_loadbalance'] in str(loadbalance.nicTeamingPolicy):
                log.info("{} load balancing detail".format(loadbalance.nicTeamingPolicy))
            else:
                errorFlag += 1
                log.info("{} load balancing is not Route Bases"
                         .format(loadbalance.nicTeamingPolicys))
            if len(dvsuplinks) == testcase_data['expected_uplinks']:
                log.info("{} Expected uplinks are connected"
                         .format(testcase_data['expected_uplinks']))
            else:
                errorFlag += 1
                log.info("Expected uplinks are not connected,"
                         " Expected is {} : {}".format(testcase_data['expected_uplinks'],
                                                       len(dvsuplinks)))
            if notify_switch.value:
                log.info("notify switch : yes")
            else:
                errorFlag += 1
                log.info("notify switch : No")
            if fail_back.value:
                log.info("failback : yes")
            else:
                errorFlag += 1
                log.info("failback : No")
                break
        if errorFlag != 0:
            raise Exception("Expected policies are not correct")
            break
        else:
            log.info("Expected policies are correct")
            break
    else:
        raise Exception("management port group is not created"
                        " under cell-site with required policies")
						
# ----------------------------------------------------------------------------------------------
# https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/blob/dev/vaibhav/cellsite/testcases/cell_site/test_vsphere_cellsite_policies.py
# PR : https://eos2git.cec.lab.emc.com/OTEL-automation/tsb-vmware-sdk/pull/23

