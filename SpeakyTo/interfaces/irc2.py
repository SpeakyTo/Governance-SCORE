

from iconservice import *


class IRC2Interface(InterfaceScore):
    """ An interface of ICON Token Standard, IRC-2"""
    @interface
    def name(self) -> str:
        pass

    @interface
    def symbol(self) -> str:
        pass

    @interface
    def decimals(self) -> int:
        pass

    @interface
    def totalSupply(self) -> int:
        pass

    @interface
    def balanceOf(self, _owner: Address) -> int:
        pass

    @interface
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        pass

    @interface
    def treasury_withdraw(self, _dest: Address, _value: int):
        pass

    @interface
    def treasury_deposit(self, _src: Address, _value: int):
        pass
