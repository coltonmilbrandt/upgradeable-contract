from brownie import accounts, network, config
# eth_utils needs to be installed "pip3 install eth_utils"
import eth_utils

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local", "local-ganache"]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])

# *args allows for any number of arguments afterward
def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer

    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: 'box.store'.
        Defaults to None.

        args (Any, options):
        The arguments to pass to the inititalizer function

        Returns:
        [bytes]: Return the encoded bytes.
    
    """
    #  we are encoding "initializer=box.store, 1" into bytes so that our smart contracts know
    #  which function to call. If there is no initializer or it's blank, we return an empty hex
    #  string and our smart contract will know it is blank.
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)