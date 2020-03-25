""" UCS Operations """
import os
from ucsmsdk.ucshandle import UcsHandle

UCS_HOST = os.environ['UCS_HOST']
UCS_USER = os.environ['UCS_USER']
UCS_PASS = os.environ['UCS_PASS']

def ucs_login():
    """ Login to UCS """
    handle = UcsHandle(ip=UCS_HOST, username=UCS_USER, password=UCS_PASS)
    handle.login()

    return handle

def ucs_logout(handle):
    """ Logout of UCS """
    handle.logout()

def get_ucs_inventory():
    """ Get UCS Blade and Rack Server Inventory """
    handle = ucs_login()

    server_classes = ["ComputeRackUnit", "ComputeBlade"]
    # Queries are executed with a HANDLE member method
    servers = handle.query_classids(server_classes)

    response = "**"
    # Iterate over list displaying attributes from each object
    for server_class in server_classes:
        for server in servers[server_class]:
            response += (
                "Dn: " + server.dn +
                ", Model: " + server.model +
                ", Serial: " + server.serial +
                ", Memory: " + server.total_memory +
                ", # CPU: " + server.num_of_cpus +
                "<br/>"
            )
    response += "**"

    ucs_logout(handle)

    print(response)
    return response

def get_ucs_faults():
    """ Get UCS Faults """

    sev_critical = 0
    sev_major = 0
    sev_minor = 0
    sev_warning = 0

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

    response = (
        "UCSM Fault Counts - Critical: " + str(sev_critical) +
        " Major: " + str(sev_major) +
        " Minor: " + str(sev_minor) +
        " Warning: " + str(sev_warning)
    )

    ucs_logout(handle)

    print(response)
    return response

def manage_org(inputs):
    """ Manage UCS Organizations """

    from ucsmsdk.mometa.org.OrgOrg import OrgOrg

    handle = ucs_login()

    object_op = inputs[0]
    org_parent = inputs[1]
    org_name = inputs[2]
    if len(inputs) == 4:
        org_descr = inputs[3]

    if object_op == "add":
        parent_org_dn = 'org-' + org_parent.replace('/', '/org-')
        parent_org = handle.query_dn(parent_org_dn)
        if parent_org:
            ucs_mo = OrgOrg(parent_mo_or_dn=parent_org_dn, name=org_name, descr=org_descr)
            handle.add_mo(ucs_mo, modify_present=True)
            handle.commit()
            response = "Org: " + (parent_org_dn+"/org-"+org_name).replace('/org-','/').replace('org-','') + " - Added."
        else:
            response = "Org: " + (parent_org_dn).replace('/org-','/').replace('org-','') + " - Parent Org Not Found: could not Add."
    elif object_op == "remove":
        parent_org_dn = 'org-' + org_parent.replace('/', '/org-')
        ucs_mo = handle.query_dn(parent_org_dn+"/org-"+org_name)
        if ucs_mo:
            handle.remove_mo(ucs_mo)
            handle.commit()
            response = "Org: " + (parent_org_dn+"/org-"+org_name).replace('/org-','/').replace('org-','') + " - Removed."
        else:
            response = "Org: " + (parent_org_dn+"/org-"+org_name).replace('/org-','/').replace('org-','') + " - Not Found: could not remove."
    elif object_op == "update":
        parent_org_dn = 'org-' + org_parent.replace('/', '/org-')
        ucs_mo = handle.query_dn(parent_org_dn+"/org-"+org_name)
        if ucs_mo:
            ucs_mo.descr = org_descr
            handle.add_mo(ucs_mo, modify_present=True)
            handle.commit()
            response = "Org: " + (parent_org_dn+"/org-"+org_name).replace('/org-','/').replace('org-','') + " - Updated."
        else:
            response = "Org: " + (parent_org_dn+"/org-"+org_name).replace('/org-','/').replace('org-','') + " - Not Found: could not update."

    ucs_logout(handle)

    print(response)
    return response

def manage_vmedia(inputs):
    """ Manage UCS Vmedia Policy Mounts"""

    from ucsmsdk.mometa.cimcvmedia.CimcvmediaConfigMountEntry import CimcvmediaConfigMountEntry

    handle = ucs_login()

    object_op = inputs[0]
    org_parent = inputs[1]
    vmedia_name = inputs[2]
    vmedia_mount_name = inputs[3]

    parent_org_dn = 'org-' + org_parent.replace('/', '/org-')
    vmedia_dn = parent_org_dn+"/mnt-cfg-policy-"+vmedia_name
    vmedia_mount_dn = parent_org_dn+"/mnt-cfg-policy-"+vmedia_name+"/cfg-mnt-entry-"+vmedia_mount_name

    print(vmedia_dn)
    print(vmedia_mount_dn)

    if object_op == "add" or object_op == "update":
        vmedia_mount_image_path = inputs[4]
        vmedia_mount_image_file_name = inputs[5]
        vmedia_mount_device_type = inputs[6]
        vmedia_mount_protocol = inputs[7]
        vmedia_mount_remote_ip_address = inputs[8]

        ucs_mo = handle.query_dn(vmedia_dn)

        action = ""

        if ucs_mo:
            vmedia_mount_mo = handle.query_dn(vmedia_mount_dn)
            if vmedia_mount_mo == None:
                vmedia_mount_mo = CimcvmediaConfigMountEntry(
                    parent_mo_or_dn=parent_org_dn+"/mnt-cfg-policy-"+vmedia_name,
                    mapping_name=vmedia_mount_name,
                    device_type=vmedia_mount_device_type,
                    mount_protocol=vmedia_mount_protocol,
                    remote_ip_address=vmedia_mount_remote_ip_address,
                    image_path=vmedia_mount_image_path,
                    image_file_name=vmedia_mount_image_file_name
                )
                action = "Added"
            else:
                print(vmedia_mount_device_type)
                vmedia_mount_mo.device_type=vmedia_mount_device_type
                vmedia_mount_mo.mount_protocol=vmedia_mount_protocol
                vmedia_mount_mo.remote_ip_address=vmedia_mount_remote_ip_address
                vmedia_mount_mo.image_path=vmedia_mount_image_path
                vmedia_mount_mo.image_file_name=vmedia_mount_image_file_name
                action = "Updated"
            
            handle.add_mo(vmedia_mount_mo, modify_present=True)
            handle.commit()
            response = "Vmedia Mount: " + org_parent + '/'+ vmedia_name + '/' + vmedia_mount_name + " - " + action + "."
        else:
            response = "Vmedia Policy: " + org_parent + '/'+ vmedia_name + " - Not Found."

    elif object_op == "remove":
        vmedia_mount_mo = handle.query_dn(vmedia_mount_dn)
        if vmedia_mount_mo:
            handle.remove_mo(vmedia_mount_mo)
            handle.commit()
            response = "Vmedia Mount: " + org_parent + '/'+ vmedia_name + '/' + vmedia_mount_name + " - Removed."
        else:
            response = "Vmedia Mount: "  + org_parent + '/'+ vmedia_name + '/' + vmedia_mount_name + " - Not Found."

    ucs_logout(handle)

    print(response)
    return response

if __name__ == "__main__":

    inputs = ["add", "root/bot-org", "bot-vmedia", "CentOS-AA", "/iso/", "centos-8.iso", "cdd", "http", "10.10.10.10"]
    manage_vmedia(inputs)

    inputs = ["remove", "root/bot-org", "bot-vmedia", "CentOS-BB"]
    manage_vmedia(inputs)
    #manage_org(inputs)
    #get_ucs_faults()
    #get_ucs_inventory()
