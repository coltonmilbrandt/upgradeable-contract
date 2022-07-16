from scripts.helpful_scripts import encode_function_data, get_account, upgrade
from brownie import Box, BoxV2, ProxyAdmin, TransparentUpgradeableProxy, Contract, exceptions
import pytest

def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address, 
        proxy_admin.address, 
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    # We are using the proxy address but the box.abi
    # However, we're delegating the function CALL to the box contract
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    # The TEST will fail if this throws an error
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})
    upgrade(
        account, 
        proxy, # This is the proxy contract, it directs the actions to the right contract
        box_v2, # This is the new implementation
        proxy_admin_contract=proxy_admin # If there is an admin contract
    )
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
    
    
    
    # print(f"The first contract version has stored: {proxy_box.retrieve()}")