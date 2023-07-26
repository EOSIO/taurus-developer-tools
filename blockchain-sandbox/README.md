# Blockchain Sandbox Tool

One of the fundamental issues in application development is the discovery of bugs that only occur in production deployments and are not reproducible in developer’s testing environment. The usage of hardware keys in the production blockchain deployment also makes it impossible to continue a blockchain from the production environment in a testing or local machine as is. The EOSIO-Taurus blockchain provides some special debug function support that enables developers to download a state snapshot from the production machines and make changes to it (including replacing block signing keys and account keys) and continue production on the local machine. This enables microservices developers to test their local instantiation of the service to explore in-depth to pinpoint the source of the issue.

This tool, based on the EOSIO-Taurus feature, starts a sandbox EOSIO-Taurus blockchain from a blockchain snapshot with keys replaced for developers to replicate a production blockchain without having to have the hardware keys.

## Start A blockchain Sandbox

### How to use it

Usages

Start the sandbox from the nodeos available in the shell env's `$PATH`:

```
Usage: ./scripts/blockchain-sandbox.sh --snapshot=[snapshot path]

# requirements:
# nodeos/cleos availble in the $PATH
# the nodeos should be buildt with the flag EOSIO_NOT_REQUIRE_FULL_VALIDATION=on when doing cmake
# RabbitMQ installed
```

Ports and services exposed
- 8888: RPC port of the producer
- 8880: rodeos_plugin port for query/wasm-ql
- 5672: RabbitMQ port with `amqp://` protocol (non-SSL one), the RabbitMQ user is `test:test`
- 15672: RabbitMQ Web management console

Keys are replaced in the blockchain sandbox. `root` key:

```
PUBLIC_KEY = "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
PRIVATE_KEY = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
```

The blockchain started has long time transaction support, allowing transactions to run as long as 180 seconds.

### A usage example

An example of starting a blockchain sandbox from a snapshot:

```
$ ./scripts/blockchain-sandbox.sh --snapshot=/path/to/snapshots/snapshot-05c2bd54d05984f244e358b29e8f067cef9142d5878653a31a5b45331bfb3214.bin

...
#### Start RabbitMQ
...
#### Start producer nodeos ...
...
#### Stop the producer nodeos to generate a snapshot for the rodeos nodeos ...
...
...

Blockchain sandbox started.

...

Press Enter to shutdown the blockchain, after you finish using this blockchain sandbox ...
```

The ports are available in the container and the host to call the RPC/wasm-ql:

```
$ cleos -u http://127.0.0.1:8888 get info
{
  "server_version": "7656ef01",
  "chain_id": "207d566c00707f54da8482d4428ca5eafa107c62602b7b68bf0b4aca82392352",
  "head_block_num": 96648771,
  "last_irreversible_block_num": 96648770,
  "last_irreversible_block_id": "05c2be42432731c993433e6a7f2a02ab81ec6273c4c3ee33e9bc667eaa18fec1",
  "head_block_id": "05c2be43a329751a145f1b8a26c2e6ae5ea896f2189b5d993fa8937374bac29d",
  "head_block_time": "2023-05-18T17:41:55.500",
  "head_block_producer": "eosio",
  "virtual_block_cpu_limit": 450000000,
  "virtual_block_net_limit": "10485760000",
  "block_cpu_limit": 450000,
  "block_net_limit": 10485760,
  "server_version_string": "v3.0.x",
  "fork_db_head_block_num": 96648771,
  "fork_db_head_block_id": "05c2be43a329751a145f1b8a26c2e6ae5ea896f2189b5d993fa8937374bac29d",
  "server_full_version_string": "v3.0.x-a35e268b4e592eafcbed39212632af7ef43af5e2-dirty",
  "last_irreversible_block_time": "2023-05-18T17:41:55.000",
  "total_cpu_weight": 0,
  "total_net_weight": 0,
  "first_block_num": 96648533
}

$ cleos -u http://127.0.0.1:8880 get info
{
  "server_version": "7656ef01",
  "chain_id": "207d566c00707f54da8482d4428ca5eafa107c62602b7b68bf0b4aca82392352",
  "head_block_num": 96648773,
  "last_irreversible_block_num": 96648771,
  "last_irreversible_block_id": "05c2be43a329751a145f1b8a26c2e6ae5ea896f2189b5d993fa8937374bac29d",
  "head_block_id": "05c2be45e0cad4832c2b67bd77e75e3070b8472378b7875c7c41662bd9fd35f2",
  "head_block_time": "1970-01-01T00:00:00.000",
  "head_block_producer": "",
  "virtual_block_cpu_limit": 0,
  "virtual_block_net_limit": 0,
  "block_cpu_limit": 0,
  "block_net_limit": 0,
  "server_version_string": "v3.0.x",
  "server_full_version_string": "v3.0.x-a35e268b4e592eafcbed39212632af7ef43af5e2-dirty"
}

$ cleos get account root
created: 2021-11-04T06:54:04.500
permissions:
     owner     1:    1 EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV
        active     1:    1 EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV

```

## Tools

### Replace key for account permissions

A tool to replace the key manually for a permission to be the default key (as `root@active`):

```
$ scripts/replace-key.sh -h
usage: Blockchain Sandbox Account Key Replacing Tool [-h] [--acct ACCT] [--perm PERM]

Replace Account Keys For a Blockchain Sandbox

options:
  -h, --help   show this help message and exit
  --acct ACCT
  --perm PERM
```

For example, to replace `login@login`'s key:

```
$ scripts/replace-key.sh --acct login --perm login
Replacing key for login@login ...

...


Key has been replaced. New permission for login:
...
$ cleos get account login

created: 2021-11-04T06:54:24.000
permissions:
     owner     1:    1 root@owner
        active     1:    1 root@active
           login     1:    1 EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV
...
```

