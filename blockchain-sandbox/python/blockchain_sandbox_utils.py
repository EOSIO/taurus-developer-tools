
import os
import sys
import time

from TestUtils import Utils


class BlockchainSandboxUtils:
    Utils.Debug = True

    pNodeos = None
    pNodeosRodeos = None
    pRabbitMQ = None

    amqp_address = Utils.DEFAULT_AMQP_ADDR
    amqp_queue = Utils.DEFAULT_AMQP_QUEUE

    producer_data_dir = "./producer_test_data"
    nodeos_rodeos_data_dir = "./nodeos_rodeos_test_data"
    nodeos_endpoint = "http://127.0.0.1:8888"
    rodeos_endpoint = "http://127.0.0.1:8880"

    @staticmethod
    def process_cmd(args):
        Utils.process_cmd(args)

    @staticmethod
    def replace_key(acct, perm):
        print(f"Replacing key for {acct}@{perm} ...")
        outs, errs = Utils.process_cmd(
            f"cleos --no-auto-keosd set account permission {acct} {perm} {Utils.PublicKey} -x 3600 -dsj -p eosio@active")
        with open('/tmp/t.trx', 'wt') as tmp:
            trx = outs.replace("updateauth", "updateauth2", 1)
            tmp.write(trx)
        Utils.process_cmd(
            f"cleos --no-auto-keosd sign --signature-provider '{Utils.PublicKey}=KEY:{Utils.PrivateKey}' -p /tmp/t.trx")

    def start_blockchain(self, snapshot_path=None):
        print(f"#### Start RabbitMQ")
        Utils.start_rabbitmq()
        # mark it is started
        self.pRabbitMQ = True
        time.sleep(10)

        print(f"#### Start producer nodeos ...")
        self.pNodeos = Utils.start_producer_nodeos(
            self.producer_data_dir, with_amqp=True, snapshot_path=snapshot_path, long_time_transaction_mode=True)
        time.sleep(20)

        print(f"#### Stop the producer nodeos to generate a snapshot for the rodeos nodeos ...")
        Utils.stop_nodeos(self.pNodeos, self.producer_data_dir, clean_data=False, sigkill=False)

        producer_snapshot = os.path.join(self.producer_data_dir, "state", "state_snapshot.bin")

        cnt = 0
        print(f"Waiting for file {producer_snapshot} to be generated ... {cnt}")
        while cnt < 240:
            if os.path.isfile(producer_snapshot):
                break
            cnt += 1
            print(f"Waiting for file {producer_snapshot} to be generated ... {cnt}")
            time.sleep(1)
        if cnt == 240:
            print("")
            print(f"ERROR: Failed to get a snapshot {producer_snapshot}. You may retry if it is because the container was too slow...")
            print("")
            return False

        print("New snapshot is generated.")

        print(f"#### Start back producer nodeos ...")
        self.pNodeos = Utils.start_producer_nodeos(self.producer_data_dir, with_amqp=True, clean_data=False)

        print(f"#### Start nodeos with rodeos_plugin for query support ...")
        self.pNodeosRodeos = Utils.start_rodeos_nodeos(
            self.nodeos_rodeos_data_dir,
            snapshot_path=producer_snapshot)

        cnt = 0
        print(f"Waiting for rodeos_plugin to be ready ... {cnt}")
        old_debug = Utils.Debug
        Utils.Debug = False
        while cnt < 360:
            outs, errs = Utils.cleos("-u http://127.0.0.1:8880 get info")
            if "server_full_version_string" in outs:
                break
            cnt += 1
            print(f"Waiting for rodeos_plugin to be ready ... {cnt}")
            time.sleep(1)
        Utils.Debug = old_debug
        if cnt == 360:
            print("")
            print(f"ERROR: Failed to get info from rodeos_plugin. You may retry if it was because the container was too slow...")
            print("")
            return False

        return True

    def stop_blockchain(self):
        if self.pNodeos:
            print(f"#### Stop producer nodeos ...")
            Utils.stop_nodeos(self.pNodeos, self.producer_data_dir)

        if self.pRabbitMQ:
            print(f"#### Stop RabbitMQ ...")
            Utils.stop_rabbitmq()

        if self.pNodeosRodeos:
            print(f"#### Stop nodeos-rodeos ...")
            Utils.stop_nodeos(self.pNodeosRodeos, self.nodeos_rodeos_data_dir)
