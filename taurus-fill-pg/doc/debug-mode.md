## Sample SQL queries
Show the complete list of contracts and tables and the number of entries each table has. In other words the complete blockchain schema known to fill-pg:

```sql
select  key_value_decoded.contract, key_value_decoded.table, count(key_value_decoded.table) from chain.key_value_decoded group by key_value_decoded.table, key_value_decoded.contract  order by key_value_decoded.contract, key_value_decoded.table ASC;
```

Show the first 100 rows from key_decoded_value table.

```sql
SELECT * FROM chain.key_value_decoded
LIMIT 100
```

Show the latest 100 rows from key_decoded_value table

```sql
SELECT * FROM chain.key_value_decoded
ORDER BY block_num DESC LIMIT 100
```

Show the first 100 entries associated to the wallet contract

```sql
SELECT * FROM chain.key_value_decoded
WHERE contract = 'wallet'
LIMIT 100
```

Show the first 100 entries associated to the names table from the address contract.

```sql
SELECT * FROM chain.key_value_decoded
WHERE contract = 'address' AND key_value_decoded.table = 'names'
LIMIT 100
```

Show the latest 100 transaction traces.

```sql
SELECT * FROM chain.transaction_trace
ORDER BY block_num DESC, transaction_ordinal DESC LIMIT 100
```

(You should be able to see the action parameters and return data in the action_traces column, just not very pretty formatted on this tool)

Show the latest 500 entries on the key_value_decoded table from the contract called relations.

```sql
SELECT * FROM chain.key_value_decoded
WHERE contract = 'relations' 
ORDER BY block_num 
DESC LIMIT 500;
```

Show the latest 500 entries on the key_value_decoded_table whose json contains the substring "rempolfrusr"

```sql
SELECT * FROM chain.key_value_decoded
WHERE key_value_decoded.json like '%rempolfrusr%' 
ORDER BY block_num 
DESC LIMIT 500;
```

Show the latest 100 transaction traces that have an action from the wallet contract. 

```sql
create or replace function chain.concat_action_traces_account(arr chain.action_trace[])
	returns text
    immutable
    strict
    language plpgsql
      as $$
      	declare
          result  text := '';
      	begin
        	result := (SELECT string_agg((el::chain.action_trace).act.account, ', ')  FROM UNNEST(arr) as el );
        RETURN result;
      end;
      $$;

SELECT  * FROM chain.transaction_trace
WHERE chain.concat_action_traces_account(chain.transaction_trace.action_traces) = 'wallet'
ORDER BY block_num DESC, transaction_ordinal DESC LIMIT 100
```

Show all contracts and tables that have data on chain.

```sql
select  key_value_decoded.contract, key_value_decoded.table, count(key_value_decoded.table) from chain.key_value_decoded group by key_value_decoded.table, key_value_decoded.contract  order by key_value_decoded.contract, key_value_decoded.table ASC
```

## Known issues

- varchar in key_value_decoded table is not searchable easily

- json fields in key_value_decoded table are not true json (dont try to parse)

- key_value and key_value_decoded tables are not exactly identical (key is missing from decoded table)

- fill-trim option (to have only the elements of the current state on chain and trim the others) on fill-pg most likely still not working as expected for the key_value_decoded table. The other tables work as expected.