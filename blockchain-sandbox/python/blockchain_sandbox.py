import sys
import argparse

from blockchain_sandbox_utils import BlockchainSandboxUtils


def main():
    parser = argparse.ArgumentParser(
        prog='Blockchain Sandbox',
        description='Start a Blockchain Sandbox')
    parser.add_argument('--snapshot')
    args = parser.parse_args()

    try:
        sandbox = BlockchainSandboxUtils()
        success = sandbox.start_blockchain(snapshot_path=args.snapshot)

        if not success:
            return 1

        print(f"Replacing permission keys ...")
        # extend the list of (acct, perm) here to add more key replacement by default
        for acct, perm in [("acctmgmt", "acctmgmt")]:
            sandbox.replace_key(acct, perm)

        print("")
        print("Blockchain sandbox started.")
        print("")
        print("You may run these commands to check the producer nodeos and rodeos_plugin status:")
        print("")
        print("docker exec -ti blockchain-sandbox cleos -u http://127.0.0.1:8888 get info")
        print("docker exec -ti blockchain-sandbox cleos -u http://127.0.0.1:8880 get info")
        print("")
        input("Press Enter to shutdown the blockchain, after you finish using this blockchain sandbox ...")

    finally:
        sandbox.stop_blockchain()
    return 0


if __name__ == "__main__":
    sys.exit(main())
