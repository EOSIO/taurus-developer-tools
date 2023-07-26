#!/usr/bin/env python3

import os
import shlex
import shutil
import signal
import subprocess
import sys
import typing
import time
import json

script_dir = os.path.dirname(os.path.abspath(__file__))


class Utils:
    Debug = False
    PUBLIC_KEY = "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
    PRIVATE_KEY = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
    PublicKey = PUBLIC_KEY
    PrivateKey = PRIVATE_KEY
    SIGNATURE_PROVIDER = f"{PUBLIC_KEY}=KEY:{PRIVATE_KEY}"

    DEFAULT_AMQP_ADDR = "amqp://test:test@127.0.0.1:5672"
    DEFAULT_AMQP_QUEUE = "bptrx"

    # these options reflect the config in production env
    PRODUCER_NODEOS_OPTIONS = " ".join([
        "--plugin eosio::chain_api_plugin",
        "--plugin eosio::db_size_api_plugin",
        "--plugin eosio::http_plugin",
        "--plugin eosio::net_api_plugin",
        "--plugin eosio::net_plugin",
        "--plugin eosio::producer_api_plugin",
        "--plugin eosio::producer_plugin",
        "--abi-serializer-max-time-ms 1000000000",
        "--access-control-allow-origin '*'",
        "--chain-state-db-size-mb 10240",
        "--contracts-console",
        "--cpu-effort-percent 95",
        "--database-map-mode heap",
        "--disable-replay-opts",
        "--disable-subjective-billing 1",
        "--enable-stale-production",
        "--http-max-response-time-ms 1000000000",
        "--http-validate-host false",
        "--last-block-cpu-effort-percent 100",
        "--last-block-time-offset-us 0",
        "--max-body-size 100000000",
        "--max-clients 10",
        "--max-irreversible-block-age -1",
        "--producer-name eosio",
        "--resource-monitor-not-shutdown-on-threshold-exceeded",
        "--signature-cpu-billable-pct 0",
        "--verbose-http-errors",
        "--wasm-runtime eos-vm-jit",
        "--http-server-address 0.0.0.0:8888",
        "--p2p-listen-endpoint 0.0.0.0:9876",
        "--p2p-peer-address 127.0.0.1:9877",
        "--override-chain-cpu-limits true"
    ])

    SHIP_NODEOS_OPTIONS = " ".join([
        "--plugin eosio::chain_api_plugin",
        "--plugin eosio::db_size_api_plugin",
        "--plugin eosio::http_plugin",
        "--plugin eosio::net_api_plugin",
        "--plugin eosio::net_plugin",
        "--plugin eosio::producer_api_plugin",
        "--plugin eosio::producer_plugin",
        "--plugin eosio::state_history_plugin",
        "--abi-serializer-max-time-ms 1000000000",
        "--access-control-allow-origin '*'",
        "--chain-state-db-size-mb 10240",
        "--chain-state-history",
        "--contracts-console",
        "--cpu-effort-percent 95",
        "--database-map-mode heap",
        "--disable-replay-opts",
        "--disable-subjective-billing 1",
        "--enable-stale-production",
        "--http-max-response-time-ms 1000000000",
        "--http-validate-host false",
        "--last-block-cpu-effort-percent 100",
        "--last-block-time-offset-us 0",
        "--max-body-size 100000000",
        "--max-clients 10",
        "--max-irreversible-block-age -1",
        "--max-transaction-time 445",
        "--resource-monitor-not-shutdown-on-threshold-exceeded",
        "--signature-cpu-billable-pct 0",
        "--trace-history",
        "--verbose-http-errors",
        "--wasm-runtime eos-vm-jit",
        "--http-server-address 0.0.0.0:8889",
        "--p2p-listen-endpoint 0.0.0.0:9877",
        "--p2p-peer-address 127.0.0.1:9876",
        "--override-chain-cpu-limits true"
    ])

    RODEOS_NODEOS_OPTIONS = " ".join([
        "--plugin eosio::chain_api_plugin",
        "--plugin eosio::db_size_api_plugin",
        "--plugin eosio::http_plugin",
        "--plugin eosio::net_api_plugin",
        "--plugin eosio::net_plugin",
        "--plugin eosio::producer_api_plugin",
        "--plugin eosio::producer_plugin",
        "--plugin b1::rodeos_plugin",
        "--abi-serializer-max-time-ms 1000000000",
        "--access-control-allow-origin '*'",
        "--chain-state-db-size-mb 10240",
        "--contracts-console",
        "--cpu-effort-percent 95",
        "--database-map-mode heap",
        "--disable-replay-opts",
        "--disable-subjective-billing 1",
        "--enable-stale-production",
        "--http-max-response-time-ms 1000000000",
        "--http-validate-host false",
        "--last-block-cpu-effort-percent 100",
        "--last-block-time-offset-us 0",
        "--max-body-size 100000000",
        "--max-clients 10",
        "--max-irreversible-block-age -1",
        "--max-transaction-time 445",
        "--resource-monitor-not-shutdown-on-threshold-exceeded",
        "--signature-cpu-billable-pct 0",
        "--verbose-http-errors",
        "--wasm-runtime eos-vm-jit",
        "--http-server-address 0.0.0.0:8889",
        "--p2p-listen-endpoint 0.0.0.0:9877",
        "--p2p-peer-address 127.0.0.1:9876",
        "--sync-fetch-span 1000",
        "--wql-exec-time 30000",
        "--wql-query-mem 3000",
        "--wql-listen 0.0.0.0:8880",
        "--override-chain-cpu-limits true"
    ])

    # from env, or by default, from /usr/local
    TaurusNodeRoot = os.environ.get("TAURUS_NODE_ROOT", "/usr/local")

    NodeosPath = f"{TaurusNodeRoot}/bin/nodeos"
    if not os.path.exists(NodeosPath):
        sys.exit("Unable to find nodeos")

    CleosPath = f"{TaurusNodeRoot}/bin/cleos"
    if not os.path.exists(CleosPath):
        sys.exit("Unable to find cleos")

    RodeosPath = f"{TaurusNodeRoot}/bin/rodeos"
    if not os.path.exists(RodeosPath):
        sys.exit("Unable to find rodeos")

    @staticmethod
    def start_rabbitmq():
        print("Starting rabbitmq")
        Utils.process_cmd("rabbitmq-server -detached")
        time.sleep(10)

        # create queue
        queue_name = Utils.DEFAULT_AMQP_QUEUE
        Utils.process_cmd("rabbitmq-plugins enable rabbitmq_management")
        Utils.process_cmd("rabbitmqctl add_user test test")
        Utils.process_cmd("rabbitmqctl set_user_tags test administrator")
        Utils.process_cmd("rabbitmqctl set_permissions -p / test '.*' '.*' '.*'")
        Utils.process_cmd(f"rabbitmqadmin declare queue name={queue_name} durable=true")

    @staticmethod
    def stop_rabbitmq():
        Utils.process_cmd("rabbitmqctl shutdown")

    # start a nodes with producer plugin enabled
    @staticmethod
    def start_producer_nodeos(
            data_dir, clean_data=True, with_amqp=False, snapshot_path=None, long_time_transaction_mode=False):
        if clean_data:
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
            os.mkdir(data_dir)
        cmd = Utils.NodeosPath
        cmd += f" {Utils.PRODUCER_NODEOS_OPTIONS}"
        cmd += f" --data-dir {data_dir}"
        cmd += f" --config-dir {data_dir}/config"
        if snapshot_path is None:
            if clean_data:
                # a genesis.json is expected at the same dir as this python file
                cmd += f" --genesis-json {script_dir}/genesis.json"
        else:
            cmd += f" --snapshot {snapshot_path}"
            cmd += f" --replace-account-key {{\"account\":\"root\",\"permission\":\"owner\",\"pub_key\":\"{Utils.PublicKey}\"}}"
            cmd += f" --replace-account-key {{\"account\":\"root\",\"permission\":\"active\",\"pub_key\":\"{Utils.PublicKey}\"}}"
            cmd += f" --replace-producer-keys {Utils.PublicKey}"

        if with_amqp:
            cmd += " --amqp-trx-queue-name bptrx"
            cmd += " --amqp-trx-queue-size 50"
            cmd += " --plugin eosio::amqp_trx_plugin"
            cmd += " --amqp-trx-ack-mode in_block"

        if long_time_transaction_mode:
            cmd += " --max-transaction-time 180000"
        else:
            cmd += " --max-transaction-time 445"
        if Utils.Debug:
            print("```")
            print(cmd)
            print("```")
        with open(f"{data_dir}/nodeos.log", "w") as f:
            my_env = os.environ.copy()
            if with_amqp:
                my_env["EOSIO_AMQP_ADDRESS"] = Utils.DEFAULT_AMQP_ADDR
            return subprocess.Popen(cmd.split(), env=my_env, stdout=subprocess.PIPE, stderr=f)

    # start a nodes with ship plugin enabled
    @staticmethod
    def start_ship_nodeos(data_dir):
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        os.mkdir(data_dir)
        cmd = Utils.NodeosPath

        cmd += f" {Utils.SHIP_NODEOS_OPTIONS}"
        # a genesis.json is expected at the same dir as this python file
        cmd += f" --genesis-json {script_dir}/genesis.json"
        cmd += f" --data-dir {data_dir}"
        cmd += f" --config-dir {data_dir}/config"

        if Utils.Debug:
            print("```")
            print(cmd)
            print("```")
        with open(f"{data_dir}/nodeos.log", "w") as f:
            return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=f)

    @staticmethod
    def start_rodeos(ro_data_dir, options=None):
        if os.path.exists(ro_data_dir):
            shutil.rmtree(ro_data_dir)
        cmd = Utils.RodeosPath
        if options:
            cmd += " " + options
        else:
            cmd += " --wql-allow-origin='*'"
            cmd += " --data-dir " + ro_data_dir
            cmd += " --config-dir " + ro_data_dir + "/config"
        if Utils.Debug:
            print("```")
            print(cmd)
            print("```")
        with open("rodeos.log", "w") as f:
            return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=f)

    # start a nodeos with rodeos plugin enabled
    @staticmethod
    def start_rodeos_nodeos(data_dir, clean_data=True, snapshot_path=None):
        if clean_data:
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
            os.mkdir(data_dir)
        cmd = Utils.NodeosPath

        cmd += f" {Utils.RODEOS_NODEOS_OPTIONS}"

        cmd += f" --data-dir {data_dir}"
        cmd += f" --config-dir {data_dir}/config"

        if snapshot_path is None:
            if clean_data:
                # a genesis.json is expected at the same dir as this python file
                cmd += f" --genesis-json {script_dir}/genesis.json"
        else:
            cmd += f" --snapshot {snapshot_path}"
            cmd += f" --replace-account-key {{\"account\":\"root\",\"permission\":\"owner\",\"pub_key\":\"{Utils.PublicKey}\"}}"
            cmd += f" --replace-account-key {{\"account\":\"root\",\"permission\":\"active\",\"pub_key\":\"{Utils.PublicKey}\"}}"
            cmd += f" --replace-producer-keys {Utils.PublicKey}"

        if Utils.Debug:
            print("```")
            print(cmd)
            print("```")
        with open(f"{data_dir}/nodeos.log", "w") as f:
            return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=f)

    @staticmethod
    def stop_nodeos(nodeos_proc, data_dir, clean_data=True, sigkill=True):
        if nodeos_proc.pid:
            if sigkill:
                os.kill(nodeos_proc.pid, signal.SIGKILL)
            else:
                os.kill(nodeos_proc.pid, signal.SIGTERM)
        if clean_data:
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)

    @staticmethod
    def stop_rodeos(rodeos_proc, ro_data_dir, clean_data=True):
        if rodeos_proc.pid:
            os.kill(rodeos_proc.pid, signal.SIGKILL)
        if clean_data:
            if os.path.exists(ro_data_dir):
                shutil.rmtree(ro_data_dir)

    @staticmethod
    def process_cmd(cmd: typing.Union[str, typing.List[str]], input_message=None):
        if isinstance(cmd, str):
            cmd_str = cmd
            # don't use cmd.split(), be aware of data like '["action is good"]'
            cmd_lst = shlex.split(cmd)
        else:
            cmd_str = " ".join(cmd)
            cmd_lst = cmd
        try:
            popen = subprocess.Popen(cmd_lst, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     encoding="utf8",
                                     errors="backslashreplace")
            outs, errs = popen.communicate(input_message)
            popen.wait()
        except subprocess.CalledProcessError as e:
            print("```")
            print(cmd)
            print(f"{e.output}")
            print("```")
            exit(1)
        if Utils.Debug:
            print("```")
            # print out cmd as str so that it's easy to copy and paste manually
            print(f"$ {cmd_str}\n")
            if outs:
                print(f"{outs}")
            if errs:
                print(f"\n[STDERR]\n{errs}")
            print("```")
        return outs, errs

    @staticmethod
    def cleos(cmd: str):
        return Utils.process_cmd(Utils.CleosPath + " " + cmd)

    @staticmethod
    def create_wallet(wallet_name):
        Utils.cleos(f"wallet create --name {wallet_name} --to-console")
        return Utils.cleos(f"wallet import --name {wallet_name} --private-key {Utils.PrivateKey}")

    @staticmethod
    def remove_wallet(wallet_name):
        subprocess.call("pkill -9 keosd".split())
        wallet_file = os.path.expanduser('~') + "/eosio-wallet/" + wallet_name + ".wallet"
        if os.path.exists(wallet_file):
            os.remove(wallet_file)

    @staticmethod
    def import_key(wallet_name, private_key):
        return Utils.cleos(f"wallet import --name {wallet_name} --private-key {private_key}")

    @staticmethod
    def create_account(account_name, active_key=""):
        return Utils.cleos(f"create account eosio {account_name} {Utils.PublicKey} {active_key}")

    @staticmethod
    # publish contract and return transaction as json object
    def set_contract(nodeos_api, account, contract_dir, wasm_file, abi_file, permission, version2=False):
        wasm_file_path = f"{contract_dir}/{wasm_file}"
        abi_file_path = f"{contract_dir}/{abi_file}"
        setcode2_opt = "--run-setcode2" if version2 else ""
        setabi2_opt = "--run-setabi2" if version2 else ""
        # note: set abi before set code to avoid some chicken-and-egg dependency traps
        cmd = f"-u {nodeos_api} set abi {setabi2_opt} {account} {abi_file_path} -p {permission}"
        Utils.cleos(cmd)
        cmd = f"-u {nodeos_api} set code {setcode2_opt} {account} {wasm_file_path} -p {permission}"
        return Utils.cleos(cmd)

    @staticmethod
    def generate_trx(nodeos_api, account, action, data, permission):
        cmd = f"-u {nodeos_api} push action {account} {action} '{data}' -dsj -x 3600 -p {permission}"
        outs, errs = Utils.cleos(cmd)
        return outs

    @staticmethod
    def activate_protocol_feature(nodeos_api):
        endpoint = f"{nodeos_api}/v1/producer/schedule_protocol_feature_activations"
        digest = "0ec7e080177b2c02b278d5088611686b49d739925a92d9bfcacd7fc6b74053bd"
        data = f"{{\"protocol_features_to_activate\":[\"{digest}\"]}}"
        cmd = f"curl -s -X POST {endpoint} --data '{data}'"
        return Utils.process_cmd(cmd)

    @staticmethod
    def check_amqp_trace(outs):
        try:
            trace = json.loads(outs)
        except Exception:
            print("ERROR: failed to parse the trace string to JSON")
            return False

        if "status" not in trace:
            print("ERROR: No status found from the amqp trace")
            return False
        if trace["status"] != "executed":
            print("ERROR: Status is not 'executed' from the amqp trace")
            return False
        if "trace" not in trace:
            print("ERROR: No 'trace' field found from the amqp trace")
            return False
        if type(trace["trace"]) is not type([]):
            print("ERROR: 'trace' field is not an list from the amqp trace")
            return False
        if len(trace["trace"]) != 2:
            print("ERROR: 'trace' list len is not 2 from the amqp trace")
            return False
        action_trace = trace["trace"][1]
        if "error_code" in action_trace and action_trace["error_code"] is not None:
            print("ERROR: 'error_code' is not null from the action trace from the amqp trace")
            return False

        return True

    @staticmethod
    def assert_no_error(errs):
        assert "error" not in errs and "Error" not in errs and "ERROR" not in errs, "Error/error/ERROR found"

    @staticmethod
    def assert_has_error(errs):
        assert "error" in errs or "Error" in errs or "ERROR" in errs, "Error/error/ERROR not found"
