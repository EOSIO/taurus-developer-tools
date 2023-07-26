# Description

This release contains the first release of Taurus `fill-pg` v1.0.0

## New Enterprise Features
- In this release a new debug mode was added to work with EOSIO-Taurus for enterprise applications. To activate this mode, simply add the flag --fpg-debug-mode to the command line
- This will enable devs to see the `action parameters` and `return values` and all `key-value data stored in blockchain state` in a human readable format and searchable using SQL

## taurus-fill-pg

`fill-pg` fills postgresql with data from nodeos's State History Plugin. It provides nearly all
data that applications which monitor the chain need. It provides the following:

* Header information from each block
* Transaction and action traces, including inline actions and deferred transactions
* Contract table history, at the block level
* Tables which track the history of chain state, including
  * Accounts, including permissions and linkauths
  * Account resource limits and usage
  * Contract code
  * Contract ABIs
  * Consensus parameters
  * Activated consensus upgrades

### PostgreSQL table schema changes

This release completely rewrites the SHiP protocol to SQL conversion code so that the database tables would directly align with the data structures defined in the SHiP protocol. This also changes the table schema used by previous releases.

Here are the basic rules for the conversion:

  - Nested SHiP `struct` types with more than one field are mapped to SQL custom types.
  - Nested SHiP `vector` types are mapped to SQL arrays.
  - SHiP `variant` types are mapped to a SQL type or table containing the union fields of their constituent types.  

Consequently, instead of having their own tables in previous releases, `action_trace`, `action_trace_ram_delta`, `action_trace_auth_sequence` and `action_trace_authorization` are arrays nested inside `transaction_trace` table or `action_trace` type. The SQL `UNNEST` operator can be used to flatten arrays into tables for query. 

The current list of tables created by  `fill-pg` are:
  - account
  - account_metadata
  - block_info  
  - code                      
  - contract_index_double
  - contract_index_long_double
  - contract_index128
  - contract_index256
  - contract_index64 
  - contract_row
  - contract_table
  - fill_status
  - generated_transaction
  - global_property
  - key_value
  - key_value_decoded (* created only when running with the --fpg-debug-mode enabled)
  - permission
  - permission_link
  - protocol_state
  - received_block  
  - resource_limits
  - resource_limits_config
  - resource_limits_state
  - resource_usage
  - transaction_trace (* when running with the --fpg-debug-mode enabled, the columns corresponding to action data/return value will be decoded)

## Additional details

`fill-pg` keeps action data and contract table data in its original binary form. Future versions
may optionally support converting this to JSON.

To conserve space, `fill-pg` doesn't store blocks in postgresql. The majority of apps
don't need the blocks since:

* Blocks don't include inline actions and only include some deferred transactions. Most
  applications need to handle these, so they should examine the traces instead. e.g. many transfers
  live in the inline actions and deferred transactions that blocks exclude.
* Most apps don't verify block signatures. If they do, then they should connect directly to
  nodeos's State History Plugin to get the necessary data. Note that contrary to
  popular belief, the data returned by the `/v1/get_block` RPC API is insufficient for
  signature verification since it uses a lossy JSON conversion.
* Most apps which currently use the `/v1/get_block` RPC API (e.g. `eosjs`) only need a tiny
  subset of the data within each block; `fill-pg` stores this data. There are apps which use
  `/v1/get_block` incorrectly since their authors didn't realize the blocks miss
  critical data that their applications need.

`fill-pg` supports both full history and partial history (`trim` option). This allows users
to make their own tradeoffs. They can choose between supporting queries covering the entire
history of the chain, or save space by only covering recent history.

## Debug Mode (NEW feature added to work with EOSIO-Taurus for enterprise applications)

To activate this mode, simply add the flag `--fpg-debug-mode`.

Fill-pg running in debug mode ( --fpg-debug-mode ) will enable devs to:

* Send an ABI or protobuf encoded action into nodeos and immediately see the action params and the return value in plain text in Postgres (on the `transaction_trace` table). 

* See human readable versions of key values for each smart contract table in nodeos inside Postgres. A new table called will be created called `key_value_decoded` where all the decoded data will be available.

## Getting Started

### Building

Currently only docker-based build on macOS is supported, to build a Docker image that will build the `fill-pg` binary, run:

```
docker build .
```

### Interacting with EOSIO-Taurus node

You can use docker-compose to see how fill-pg interacts with nodeos and postgresql. 

First, make sure a nodeos (https://github.com/EOSIO/taurus-node) instance is currently running and properly configured to be running its SHIP plugin on port 8080.

Then, execute the command:

```
docker-compose up -f docker-compose-local.yaml
```

After the containers are built, fill-pg will start getting the first bulk of information from nodeos (similar to getting a full snapshot of the current state).

A docker container running Postgres will be accessible through local port 6543. Use postgres as user, and password as password to connect to it. You can use a postgres client to connect to it, for example using psql:

```
psql -U postgres -p 6543 -h 127.0.0.1
```

You can also use the pre-packaged pgAdmin web interface to interact with your Human Readable State database as shown below. 

Point your browser to http://localhost:5050 , it should login you automatically, but in case it asks for user/password, use postgres@postgres.com and password, respectively.

## More Documentation

1. [Additional information on `fill-pg` options and filters.](doc/database-fillers.md) 
2. [Configuring EOSIO-Taurus to connect to `fill-pg`.](doc/nodeos-state-history.md)
3. [More on the debug-mode option, including examples of SQL queries.](doc/debug-mode.md)  (* feature added to work with EOSIO-Taurus for enterprise applications)

