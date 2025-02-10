import "./access-single-silo.spec";

using ShareDebtToken0 as debt_0;

// @doc: it is expected that user must be able to take anyones debt without permission, even if user sets receiver approvals, still taking someones debt will revert as the underlying ERC20 token's approvals are not set by the debtor wallet
rule UserCanTakeAnyOnesDebtWithoutPermission {
    env e; address _from; address _to; uint256 _amount;

    uint receiveAllowancesOfFromAndTo = debt_0.receiveAllowance(e, _from , _to);
    uint ERC20AllowancesOfFromAndTo = debt_0.allowance(e, _from, _to);

    require _amount > 0;
    require e.msg.sender == _to;
    require receiveAllowancesOfFromAndTo == _amount;
    require ERC20AllowancesOfFromAndTo == 0;
    
    debt_0.transferFrom@withrevert(e, _from, _to, _amount);

    bool reverted = lastReverted;
    satisfy !reverted, "bug confirmed! user cant take debt without permissions";
}

rule IGNORE__DebugRule__IfThisRulePassesThenThereIsBug__And__ifFailsThenThereIsNoBug {
    env e; address _from; address _to; uint256 _amount;

    uint receiveAllowancesOfFromAndTo = debt_0.receiveAllowance(e, _from , _to);
    uint ERC20AllowancesOfFromAndTo = debt_0.allowance(e, _from, _to);

    require _amount > 0;
    require e.msg.sender == _to;

    require receiveAllowancesOfFromAndTo == _amount;
    require ERC20AllowancesOfFromAndTo == 0;
    
    debt_0.transferFrom@withrevert(e, _from, _to, _amount);

    bool reverted = lastReverted;
    assert reverted, "debugging failed"; 
}    