from ucsmsdk.ucshandle import UcsHandle
import os

UCS_HOST = os.environ['UCS_HOST']
UCS_USER = os.environ['UCS_USER']
UCS_PASS = os.environ['UCS_PASS']

def ucs_login():
    handle = UcsHandle(ip=UCS_HOST, username=UCS_USER, password=UCS_PASS)
    handle.login()

    return handle

def ucs_logout(handle):
    handle.logout()
    
def add_ucs_ippool(ippool_name, ippool_descr, ippool_def_gw, ippool_from, ippool_to, ippool_prim_dns, ippool_sec_dns):
    from ucsmsdk.mometa.ippool.IppoolPool import IppoolPool
    from ucsmsdk.mometa.ippool.IppoolBlock import IppoolBlock

    handle = ucs_login()

    mo = IppoolPool(parent_mo_or_dn="fabric/lan/network-sets", descr=ippool_descr, ext_managed="external", name=ippool_name)
    handle.add_mo(mo,True)

    mo = IppoolBlock(parent_mo_or_dn="fabric/lan/network-sets/ip-pool-"+ippool_name, def_gw=ippool_def_gw, r_from=ippool_from, to=ippool_to, prim_dns=ippool_prim_dns, sec_dns=ippool_sec_dns)
    handle.add_mo(mo,True)

    handle.commit()

    response = "IpPool: " + ippool_name + " with IP Block: " + ippool_from + "-" + ippool_to + " has been created/updated"

    ucs_logout(handle)

    print(response)
    return response

def delete_ucs_vlan(vlan_name):

    handle = ucs_login()

    vlans = handle.query_classid("fabricVlan")
    vlan_found = False
    for vlan in vlans:
        if vlan.name == vlan_name:
            vlan_found = True
            break

    if vlan_found:
        handle.remove_mo(vlan)
        response = "Vlan: " + vlan.name + " with Vlan ID: " + vlan.id + " has been deleted"
    else:
        response = "Vlan: " + vlan_name + " does not exist"

    handle.commit()

    print(response)
    return response

def add_ucs_vlan(vlan_name, vlan_id):
    from ucsmsdk.ucshandle import UcsHandle
    from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

    handle = ucs_login()

    fabric_lan_cloud = handle.query_classid("FabricLanCloud")
    mo = FabricVlan(parent_mo_or_dn=fabric_lan_cloud[0], name=vlan_name, id=vlan_id)
    handle.add_mo(mo, True)
    handle.commit()

    vlans = handle.query_classid("fabricVlan")
    for vlan in vlans:
        if vlan.name == vlan_name and vlan.id == vlan_id:
            vlan_found = True
            break

    if vlan_found:
        response = "Vlan: " + vlan.name + " with Vlan ID: " + vlan.id + " has been created/updated"
    else:
        response = "Vlan: " + vlan.name + " with Vlan ID: " + vlan.id + " creation/update failed"

    ucs_logout(handle)

    print(response)
    return response

def get_ucs_inventory():

    handle = ucs_login()

    SERVER_CLASSES = ["ComputeRackUnit", "ComputeBlade"]
    # Queries are executed with a HANDLE member method
    SERVERS = handle.query_classids(SERVER_CLASSES)

    response = "**"
    # Iterate over list displaying attributes from each object
    for server_class in SERVER_CLASSES:
        for server in SERVERS[server_class]:
            response += "DN: " + server.dn + ", Model: " + server.model + ", Serial: " + server.serial + ", Total Memory: " + server.total_memory + ", Num. CPUs: " + server.num_of_cpus + "<br/>"
    response += "**"

    ucs_logout(handle)

    print(response)
    return response

def get_ucs_faults():

    sev_critical = 0
    sev_major    = 0
    sev_minor    = 0
    sev_warning  = 0

    handle = ucs_login()

    faults = handle.query_classid("FaultInst")
    for fault in faults:
        if fault.severity == 'critical':
            sev_critical += 1
        elif fault.severity == 'major':
            sev_major += 1
        elif fault.severity == 'minor':
            sev_minor += 1
        elif fault.severity == 'warning':
            sev_warning += 1

    response = ("UCSM Fault Counts - Critical: " + str(sev_critical) +
          " Major: " + str(sev_major) +
          " Minor: " + str(sev_minor) +
          " Warning: " + str(sev_warning))

    ucs_logout(handle)

    print(response)
    return response

def get_ucs_user():
    from ucsmsdk.mometa.aaa.AaaUserEp import AaaUserEp
    from ucsmsdk.ucshandle import UcsHandle

    handle = ucs_login()

    response = ""
    users = handle.query_classid("AaaUser")
    for user in users:
        response = response + "Username: " + user.name + ", First: " + user.first_name + ", Last: " + user.last_name + ", Email: " + user.email + "<br/>"

    ucs_logout(handle)

    print(response)
    return response

def add_ucs_user(inputString):
    from ucsmsdk.mometa.aaa.AaaUser import AaaUser
    from ucsmsdk.mometa.aaa.AaaSshAuth import AaaSshAuth
    from ucsmsdk.mometa.aaa.AaaUserRole import AaaUserRole

    handle = ucs_login()
    #First, Last, Email, Username, Role
    print(inputString)
    inputs = inputString.split(',')
    __first = inputs[0]
    __last = inputs[1]
    __email = inputs[2]
    __user = inputs[3]
    __role = inputs[4]
    print(inputs)
    mo = AaaUser(parent_mo_or_dn="sys/user-ext", email=__email, first_name=__first, last_name=__last, name=__user, pwd="create123")
    mo_1 = AaaSshAuth(parent_mo_or_dn=mo, data="", str_type="none")
    mo_2 = AaaUserRole(parent_mo_or_dn=mo, descr="", name=__role)
    handle.add_mo(mo)
    handle.commit()
    response = "Current Users:<br/>"
    users = handle.query_classid("AaaUser")
    for user in users:
        response = response + user.name + " "

    response = "<br/>" + response + "<br/>" + "Your password for user " + __user + " is create123. Change upon first login."

    ucs_logout(handle)

    print(response)
    return response

def delete_ucs_user(userName):
    from ucsmsdk.mometa.aaa.AaaUserEp import AaaUserEp

    handle = ucs_login()
    mo = handle.query_dn("sys/user-ext/user-"+userName)
    handle.remove_mo(mo)

    handle.commit()
    response = "Deleted User: " + userName + "<br/>Current Users:<br/>"
    users = handle.query_classid("AaaUser")
    for user in users:
        response = response + user.name + " "

    ucs_logout(handle)

    print(response)
    return response

def manage_org(org_op, org_name, org_descr=None):
    from ucsmsdk.mometa.org.OrgOrg import OrgOrg
    
    handle = ucs_login()

    if org_op.lower() == "add":
        mo = OrgOrg(parent_mo_or_dn='org-root', name=org_name, descr=org_descr)
        handle.add_mo(mo, modify_present=True)
        handle.commit()
        response = "Org: " + org_name + " Added/Updated."
    elif org_op.lower() == "remove":
        mo = handle.query_dn("org-root/org-"+org_name)
        if mo:
            handle.remove_mo(mo)
            handle.commit()
            response = "Org: " + org_name + " Removed."
        else:
            response = "Org: " + org_name + " Not Found."
    elif org_op.lower() == "update":
        mo = handle.query_dn("org-root/org-"+org_name)
        if mo:
            mo.descr = org_descr
            handle.add_mo(mo, modify_present=True)
            handle.commit()
            response = "Org: " + org_name + " Updated."
        else:
            response = "Org: " + org_name + " Not Found: could not update."

    ucs_logout(handle)

    print(response)
    return response
if __name__ == "__main__":
    manage_org("Add","junk","junk org")
    manage_org("Update","junk","updated junk org")
    manage_org("Remove","junk")

    #get_ucs_faults()
    #get_ucs_inventory()
    #add_ucs_vlan("john", "3000")
    #delete_ucs_vlan("john")
    #add_ucs_ippool("test-john", "test desc", "10.1.1.254", "10.1.1.1", "10.1.1.10", "208.67.220.220", "208.67.222.222")
