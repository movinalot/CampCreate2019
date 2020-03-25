from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.ippool.IppoolPool import IppoolPool
from ucsmsdk.mometa.ippool.IppoolBlock import IppoolBlock

handle = UcsHandle("128.107.70.5", "admin", "C1sco12345")
handle.login()

#query existing IP Pools
def checkIpPools(name=None):
    ip_Pools = handle.query_classid("ippoolPool")
    if name is None:
        # ip_Pools = handle.query_classid("ippoolPool")
        for ip_pool in ip_Pools:
            print("Existing IP Pool Name: ", ip_pool.name, 
                    "IP address Block:", ip_pool.v4_assigned)

    else:
        if name in [item.name for item in ip_Pools]:
            print("The name exists, please enter a different name:")
        else:
            print("I will add a new pool.")
#            addIppoolPool(pool_name, desc)

#def addIpPool(name):
def getUserInputs():
    def checkInput(userInput):
        if userInput == "":
            return (True, "Please provide input - cannot be an empty string.")
        elif " " in userInput:
            return (True, "Spaces are not allowed.")
        return (False, None)
    tempBool = True
    while tempBool:
        poolName = raw_input("What is the name of the IP Pool? ")
#        print(poolName)
        tempBool, err_msg = checkInput(poolName)
    desc = raw_input("Please provide description:  ")
    return poolName, desc

#pool_name, desc = getUserInputs()

#checkIpPools(pool_name)

def addIppoolPool(pool_name, desc):
    # name = pool_name
    # descr = desc
    mo = IppoolPool(parent_mo_or_dn="fabric/lan/network-sets", descr = dec, ext_managed="external", name = pool_name)
    handle.add_mo(mo)
    handle.commit()

def addIppoolBlock(startIP, endIP, gateway, primDNS, secDNS):
    
    mo = IppoolBlock(parent_mo_or_dn="fabric/lan/network-sets/ip-pool-Test_IP_Pool", def_gw="10.1.1.254", r_from="10.1.1.1", prim_dns="208.67.220.220", sec_dns="208.67.222.222", to="10.1.1.10")
    handle.add_mo(mo)
    handle.commit()

checkIpPools()
pool_name, desc = getUserInputs()
#print(poolName)
checkIpPools(pool_name)
addIppoolPool(pool_name, desc)

#handle.add_mo(mo)
#handle.commit()
