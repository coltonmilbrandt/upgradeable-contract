from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import network, Box, BoxV2, ProxyAdmin, TransparentUpgradeableProxy, Contract

def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account})

    # Now we need to hook it up to a proxy
    # Proxy Admins are options, but a multisig is a great way to do that
    # We will make this contract be the proxy amdin
    proxy_admin = ProxyAdmin.deploy({"from": account})

    # the constructor in transparent upgradeable proxy takes the initializer function as data 
    # the data bit is taken and calls _upgradeToAndCall() until it get to the new implementation
    # we have to encode this into bytes
    # box.store is the function to call and "1" is the first parameter, it is what we encode
    # The next line is blank for now, but we can try an initializer later and 
    # pass it in like so... encode_function_data(initializer)
    # initializer = box.store, 1

    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address, 
        proxy_admin.address, 
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    # We are using the proxy address but the box.abi
    # However, we're delegating the function CALL to the box contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(f"The first contract version has stored: {proxy_box.retrieve()}")

    # upgrade
    box_v2 = BoxV2.deploy({"from": account})
    upgrade_transaction = upgrade(
        account, 
        proxy, # This is the proxy contract, it directs the actions to the right contract
        box_v2.address, # This is the new implementation
        proxy_admin_contract=proxy_admin, # If there is an admin contract
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(f"The 2nd version has stored: {proxy_box.retrieve()}")