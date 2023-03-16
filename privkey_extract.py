import binascii
from web3.auto import w3
filename="./output/node1/keystore/keypy"
with open(filename) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, 'Password@123')
    private_key = binascii.b2a_hex(private_key)
    print(private_key)
