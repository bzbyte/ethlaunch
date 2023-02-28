import binascii
from web3.auto import w3
filename="/home/faraz/wrk/apk/ETH-Private-Network/output/node1/keystore/UTC--2023-02-27T01-29-09.214732881Z--6cdd05167d20b906b902b0a97718809a7bfdb17a"
with open(filename) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, 'Password@123')
    private_key = binascii.b2a_hex(private_key)
    print(private_key)
