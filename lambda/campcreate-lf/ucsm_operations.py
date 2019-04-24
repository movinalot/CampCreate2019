from ucsmsdk.ucshandle import UcsHandle
import os

UCS_HOST = os.environ['UCS_HOST']
UCS_USER = os.environ['UCS_USER']
UCS_PASS = os.environ['UCS_PASS']

def get_ucs_inventory():
    HANDLE = UcsHandle(UCS_HOST, UCS_USER, UCS_PASS)
    HANDLE.login()

    # Queries are executed with a HANDLE member method
    RACKS = HANDLE.query_classid("ComputeRackUnit")

    response = "**"
    # Iterate over list displaying attributes from each object
    for rack in RACKS:
        print(rack.dn, rack.model, rack.serial, rack.total_memory, rack.num_of_cpus)
        response += rack.dn + " " + rack.model + " " + rack.serial + " " + rack.total_memory + " " + rack.num_of_cpus
    response += "**"

    # Logout
    HANDLE.logout()

    return response

def get_ucs_faults():

    sev_critical = 0
    sev_major    = 0
    sev_minor    = 0
    sev_warning  = 0

    HANDLE = UcsHandle(UCS_HOST, UCS_USER, UCS_PASS)
    HANDLE.login()

    faults = HANDLE.query_classid("FaultInst")
    for fault in faults:
        if fault.severity == 'critical':
            sev_critical += 1
        elif fault.severity == 'major':
            sev_major += 1
        elif fault.severity == 'minor':
            sev_minor += 1
        elif fault.severity == 'warning':
            sev_warning += 1

    HANDLE.logout()

    response = ("UCSM Fault Counts - Critical: " + str(sev_critical) +
          " Major: " + str(sev_major) +
          " Minor: " + str(sev_minor) +
          " Warning: " + str(sev_warning))

    print(response)
    return response

def add_ucs_user(inputString):
    from ucsmsdk.mometa.aaa.AaaUser import AaaUser
    from ucsmsdk.mometa.aaa.AaaSshAuth import AaaSshAuth
    from ucsmsdk.mometa.aaa.AaaUserRole import AaaUserRole

    handle = UcsHandle(UCS_HOST, UCS_USER, UCS_PASS)
    handle.login()
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
    response = "Current Users:\n"
    users = handle.query_classid("AaaUser")
    for user in users:
        response = response + user.name + " "
    handle.logout()
    response = "\n" + response + "\n" + "Your password for user " + __user + " is create123. Change upon first login."
    print(response)
    return response

def delete_ucs_user(userName):
    from ucsmsdk.mometa.aaa.AaaUserEp import AaaUserEp

    handle = UcsHandle(UCS_HOST, UCS_USER, UCS_PASS)
    handle.login()
    mo = handle.query_dn("sys/user-ext/user-"+userName)
    handle.remove_mo(mo)

    handle.commit()
    response = "Deleted User: " + userName + "\nCurrent Users:\n"
    users = handle.query_classid("AaaUser")
    for user in users:
        response = response + user.name + " "
    handle.logout()
    print(response)
    return response

if __name__ == "__main__":
    get_ucs_faults()
    get_ucs_inventory()