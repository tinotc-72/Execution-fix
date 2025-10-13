# minimal_test.py

from solders.instruction import Instruction
from solders.pubkey import Pubkey

data_list = [2, 240, 73, 2, 0]
data = bytes(data_list)

accounts = []  # or list of AccountMeta objects

ix = Instruction(Pubkey.default(), data, accounts)
print(ix)