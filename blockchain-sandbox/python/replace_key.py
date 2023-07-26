import sys
import argparse

from blockchain_sandbox_utils import BlockchainSandboxUtils


def main():
    parser = argparse.ArgumentParser(
        prog='Blockchain Sandbox Account Key Replacing Tool',
        description='Replace Account Keys For a Blockchain Sandbox')
    parser.add_argument('--acct')
    parser.add_argument('--perm')
    args = parser.parse_args()

    sandbox = BlockchainSandboxUtils()
    sandbox.replace_key(args.acct, args.perm)

    print("")
    print(f"Key has been replaced. New permission for {args.acct}:")
    sandbox.process_cmd(f"cleos get account {args.acct}")


if __name__ == "__main__":
    sys.exit(main())
