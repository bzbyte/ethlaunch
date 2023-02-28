# Prerequisites

This tool assumes geth and bootnode executables are present in $PATH . If not, then follow the below commands to install:

```
git clone https://github.com/ethereum/go-ethereum.git
cd go-ethereum && make all
mv ./build/bin/* /usr/local/bin
```

# Getting Started

Before you can start running the script you need to install the dependencies. To install the dependencies, go to the project directory and run:

```
npm install
```

## Create new Network

To create a new Clique network run the below command:

```
npm run create
```

This will display a prompt asking for total number of authority and non-authority nodes you wish to setup. Along with that it will ask for block time and password for locking authority accounts. You can just skip to apply the default values which would create a network of 2 authority and 1 non-authority nodes. It prefunds authority accounts with 1000 ETH.

After the network is created and started it will display commands to attach to the nodes. Here is an example output:

```
? Enter total authority nodes ... 2
? Enter total peer nodes ... 1
? Enter password for ethereum accounts ... Password@123
? Enter block time ... 5
Successfully started the network with 2 authority and 1 peer nodes. Here are
commands to connect to running nodes:
Node 1 (Authority):
 IPC Attach: geth attach ./output/node1/geth.ipc
 RPC Endpoint: localhost:8546
Node 2 (Authority):
 IPC Attach: geth attach ./output/node2/geth.ipc
 RPC Endpoint: localhost:8547
Node 3 (Peer):
 IPC Attach: geth attach ./output/node3/geth.ipc
 RPC Endpoint: localhost:8548
```

## Stop Network

To stop the network, run the below command:

```
npm run stop
```

## Restart Network

To start a stopped network or restart running network, run the below command:

```
npm run restart
```

## Delete Network

If you want to stop and delete the network, run the below command:

```
npm run delete
```

## Useful command for interacting with the geth execution engine.

```
personal.unlockAccount(eth.coinbase, "Password@123", 3000000)

eth.sendTransaction({from:`${eth.coinbase}`, to:`${eth.accounts[0]}`, value: web3.toWei(10, "ether"), gas:21000});

web3.fromWei(eth.getBalance(eth.accounts[0]), "ether")
```

## Executing the consensus engine by hand

The scripts setup a single node eth setup with 3 get clients and one bootp discover process.
The consensus engine is however stopped. i.e. the clique network is not proposing any blocks.
This repo was created to play with engine API and "hand run the consensus" in order to better under standing the Engine API.

### Step0: Prereq:
Disable JWT processing on the authrpc service by commenting out JWT processing the geth binary.
JWT is disable to assist calling the Engine API with curl commands.

### Make sure the geth is at right revision

commit ee530c0d5aa70d2c00ab5691a89ab431b73f8165 (HEAD -> master, origin/master, origin/HEAD)
Merge: b3ae07348 a0d63bc69
Author: Péter Szilágyi <peterke@gmail.com>
Date:   Thu Feb 23 13:24:31 2023 +0200

### Step1: Get the hash of the head block
```
HEAD_HASH=`../go-ethereum/build/bin/geth --exec 'eth.getBlockByNumber(eth.blockNumber)' attach ./output/node1/geth.ipc 2>/dev/null | grep "hash:" | cut -f 4 -d " " | cut -f 1 -d,`
```

### Step2: Setup the fork choice rule based on the headblock hash retrieved in step 1
```
 curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"engine_forkchoiceUpdatedV1","params":[{"headBlockHash":"$HEAD_BLOCK", "safeBlockHash":"$HEAD_BLOCK", "finalizedBlockHash":"0x0000000000000000000000000000000000000000000000000000000000000000"}, {"timestamp":"0x5",  "prevRandao":"0x0000000000000000000000000000000000000000000000000000000000000000", "suggestedFeeRecipient":"0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b"}],"id":67}' http://localhost:8551

RETURNS: the payload id
{"jsonrpc":"2.0","id":67,"result":{"payloadStatus":{"status":"VALID","latestValidHash":"0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a","validationError":null},"payloadId":"0xce4ee46c8a5c1be5"}}
```

### Step3: Retrive the payload/block proposal using the payloadid
```
curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"engine_getPayloadV1","params":["0xce4ee46c8a5c1be5"],"id":67}' http://localhost:8551

RETURNS: the payload in the result field
{"jsonrpc":"2.0","id":67,"result":{"parentHash":"0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a","feeRecipient":"0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b","stateRoot":"0xca3149fa9e37db08d1cd49c9061db1002ef1cd58db2210f2115c8c989b2bdf45","receiptsRoot":"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421","logsBloom":"0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","prevRandao":"0x0000000000000000000000000000000000000000000000000000000000000000","blockNumber":"0x1","gasLimit":"0x1c9c380","gasUsed":"0x0","timestamp":"0x5","extraData":"0xd883010b03846765746888676f312e31382e31856c696e7578","baseFeePerGas":"0x7","blockHash":"0x4254db005a10650fe825e28e99339992caa467281056e60e5ee4e9bebc6d139d","transactions":[],"withdrawals":null}}

```

### Step4: Execute the payload

The result field from the above command are the params feild for the next.

```
curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"engine_newPayloadV1","params":[{"parentHash":"0x3b8 ..... }],"id":67}' http://localhost:8551

```

### Step5: Finalize/Set the block safe.

Run forkchoice update rule and set the new head to the block we executed in this iteration. 
Goto step1.
