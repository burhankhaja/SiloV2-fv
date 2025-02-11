// Importing silo0 setup from ./access-single-silo.spec
// @note this setup is for silo0 only make sure confs are compatible too
// @note also try whether cvl functions of a file are imported with it.
import "./access-single-silo.spec";

using Token0 as assetToken0; 
using Silo0 as silo_0;
using ShareProtectedCollateralToken0 as protectedShares_0;
using ShareDebtToken0 as debt_0;


methods {

    function _.isSolventAfterCollateralTransfer(address _sender) external => NONDET;

    function _.reentrancyGuardEntered() external => NONDET;

    function _.flashFee(address _config, address _token, uint256 _amount) internal => flashFeeCVL(_amount) expect (uint256);

    function decimals() external returns(uint8) => NONDET; 
    
    function _.isSolvent() external => NONDET;

    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes  _data) external => NONDET;

    function _.quote(uint256 _baseAmount, address _baseToken) external => CONSTANT ;

}

// //@audit-ok Verified and catches mutation
//@doc: Assuming flashFee to be 0, taking a flashloan should niether increase nor decrease receivers asset balance, (ensuring that token are pulled and pushed correctly between receiver and silo)
rule flashLoanIntegrity {
    env e;
    address _receiver;
    //assetToken0
    uint256 _amount;
    bytes _data;
    require _amount > 0;
    require _receiver != silo_0;
    

    
    mathint receiverBalanceBefore = assetToken0.balanceOf(e, _receiver);
        

    flashLoan(e, _receiver, assetToken0, _amount, _data);

    mathint receiverBalanceAfter = assetToken0.balanceOf(e, _receiver);

    //note the fees are summarized to be zero always
    assert receiverBalanceAfter == receiverBalanceBefore, "Receiver flashloaned asset balance should neither magically increase or decrease, assuming flashFee to be 0";

}




rule SiloSharesCantBeBurntUnexpectedly(method f) filtered {
    f -> !f.isView
}{
    env e;
    calldataarg args;

    uint collateralSharesSupplyBefore = silo_0.totalSupply(e);
    
    f(e, args);

    uint collateralSharesSupplyAfter = silo_0.totalSupply(e);

    assert collateralSharesSupplyAfter < collateralSharesSupplyBefore => canBurn(f), "silo shares shouldn't not be burnt unexpectedly!";
}

//@audit-ok 
rule OnlyHookReceiverCanTransferCollateralSharesWithNoChecks {
    env e;
    address _from; address _to; uint256 _amount;

    address hookReceiver = getHookReceiver(e);

    forwardTransferFromNoChecks@withrevert(e, _from, _to, _amount);
    bool reverted = lastReverted;
    
    assert e.msg.sender != hookReceiver => reverted, "only hook receiver should be able to  transfer collateral shares from any account without checks";

}


//@audit-ok
rule OnlyUserSpecifiedAssetsAreTakenOnDeposit {
    env e;
    uint _assets;
    address _receiver;
    uint _shares1;
    uint _shares2;
    ISilo.CollateralType _collateralType;
    require e.msg.sender != silo_0;

    uint assetBalanceBefore = assetToken0.balanceOf(e, e.msg.sender);

    storage initState = lastStorage;

    _shares1 = deposit(e, _assets, _receiver);

    uint assetBalanceAfterFirstDeposit = assetToken0.balanceOf(e, e.msg.sender);

    _shares2 = deposit(e, _assets, _receiver, _collateralType) at initState;

    uint assetBalanceAfterSecondDeposit = assetToken0.balanceOf(e, e.msg.sender);


    assert assetBalanceBefore == assetBalanceAfterSecondDeposit + _assets && assetBalanceBefore == assetBalanceAfterSecondDeposit + _assets, "Only the specified assets tokens must be taken from msg.sender on depositing";

}


// //@audit-ok
rule GivenReceiversTakeExpectedShareTypesOnDeposit {
    
    env e;
    uint _assets;
    address _receiver;
    ISilo.CollateralType _collateralType;
    // require e.msg.sender != silo_0;

    uint collateralShareBalanceOfReceiverBefore = silo_0.balanceOf(e, _receiver);
    uint protectedShareBalanceOfReceiverBefore = protectedShares_0.balanceOf(e, _receiver);

    //note otherwise overflow will occur since this is the only overflow check in ERC20UPGRADABLE._update
    require collateralShareBalanceOfReceiverBefore <= silo_0.totalSupply(e);
    require protectedShareBalanceOfReceiverBefore <= protectedShares_0.totalSupply(e);

    //  R O O T       S T A T E
    storage initState = lastStorage;


    deposit(e, _assets, _receiver);
    uint collateralSharesBalanceOfReceiverAfterNormalDeposit = silo_0.balanceOf(e, _receiver);


    deposit(e, _assets, _receiver, _collateralType) at initState;
    uint collateralShareBalanceOfReceiverAfterCollateralTypeDeposit = silo_0.balanceOf(e, _receiver);
    uint protectedShareBalanceOfReceiverAfterCollateralTypeDeposit = protectedShares_0.balanceOf(e, _receiver);

    // A S S E R T I O N

    assert _collateralType == ISilo.CollateralType.Collateral => collateralShareBalanceOfReceiverAfterCollateralTypeDeposit > collateralShareBalanceOfReceiverBefore && collateralSharesBalanceOfReceiverAfterNormalDeposit > collateralShareBalanceOfReceiverBefore, "collateral shares must increase in normal deposit and when CollateralType.Collateral is chosen";

    assert _collateralType == ISilo.CollateralType.Protected => protectedShareBalanceOfReceiverAfterCollateralTypeDeposit > protectedShareBalanceOfReceiverBefore, "receiver's protected shares balance must increase after protected type deposit";

}

// //@audit-ok
rule ExactGivenCollateralSharesAreMintedToGivenRecieverOnNormalMint {
    env e;
    uint _mintShares;
    address _receiver;

    uint collateralShareBalanceOfReceiverBefore = silo_0.balanceOf(e, _receiver);
    require collateralShareBalanceOfReceiverBefore <= silo_0.totalSupply(e);

    mint(e,_mintShares, _receiver) ; 

    uint collateralSharesBalanceOfReceiverAfter = silo_0.balanceOf(e, _receiver);
    

    assert collateralSharesBalanceOfReceiverAfter == collateralShareBalanceOfReceiverBefore + _mintShares ,"given receiver must receive exact specified Collateral shares , when funds are deposited via normal mint";
}

// //@audit-ok
rule ReceiversProtectedOrCollateralSharesIncreaseWithExactGivenSharesWithCollateralTypeMint {
    env e;
    uint _mintShares;
    address _receiver;
    ISilo.CollateralType _collateralType;
    

    uint collateralShareBalanceOfReceiverBefore = silo_0.balanceOf(e, _receiver);
    uint protectedShareBalanceOfReceiverBefore = protectedShares_0.balanceOf(e, _receiver);

    // prevents overflow
    require collateralShareBalanceOfReceiverBefore <= silo_0.totalSupply(e);
    require protectedShareBalanceOfReceiverBefore <= protectedShares_0.totalSupply(e);

    // METHOD
    mint(e,_mintShares, _receiver, _collateralType);

    uint collateralShareBalanceOfReceiverAfter = silo_0.balanceOf(e, _receiver);
    uint protectedShareBalanceOfReceiverAfter = protectedShares_0.balanceOf(e, _receiver);

    assert _collateralType == ISilo.CollateralType.Collateral => collateralShareBalanceOfReceiverAfter == collateralShareBalanceOfReceiverBefore + _mintShares, "receiver must receive exact given collateralshares";

    assert _collateralType == ISilo.CollateralType.Protected => protectedShareBalanceOfReceiverAfter == protectedShareBalanceOfReceiverBefore + _mintShares , "receiver must receive exact given protectedshares";


}

// @audit-ok 
rule withdrawalsDecreaseCallersAllowancesOfGivenShareType {
    env e; 
    uint256 _assets; address _receiver; address _owner; ISilo.CollateralType _collateralType; 
    

    uint collateralShareAllowanceBefore = silo_0.allowance(e, _owner, e.msg.sender);
    uint protectedShareAllowanceBefore = protectedShares_0.allowance(e, _owner, e.msg.sender);
    
    require e.msg.sender != _owner && collateralShareAllowanceBefore < max_uint256 && protectedShareAllowanceBefore < max_uint256;

     //  R O O T       S T A T E
    storage initState = lastStorage;

    withdraw(e, _assets, _receiver, _owner);
    bool allowanceDecreasedAfterNormalWithdraw = silo_0.allowance(e, _owner, e.msg.sender) < collateralShareAllowanceBefore;



    withdraw(e, _assets, _receiver, _owner, _collateralType) at initState;
    //if collateral type is protected then protected share allowance must decrease and vice-versa
    bool allowanceDecreasedAfterSecondWithdraw =  _collateralType == ISilo.CollateralType.Collateral ? silo_0.allowance(e, _owner, e.msg.sender) < collateralShareAllowanceBefore : protectedShares_0.allowance(e, _owner, e.msg.sender) < protectedShareAllowanceBefore;



    assert allowanceDecreasedAfterNormalWithdraw &&  allowanceDecreasedAfterSecondWithdraw, "if funds are withdrawn, then the allowances of msg.sender to the owner must always decrease !";

    
}
//@audit-ok
rule RedeemsDecreaseCallersAllowancesOfGivenShareType {
    env e; 
    uint _shares; address _receiver; address _owner; ISilo.CollateralType _collateralType; 
    

    uint collateralShareAllowanceBefore = silo_0.allowance(e, _owner, e.msg.sender);
    uint protectedShareAllowanceBefore = protectedShares_0.allowance(e, _owner, e.msg.sender);
    
    require e.msg.sender != _owner && collateralShareAllowanceBefore < max_uint256 && protectedShareAllowanceBefore < max_uint256;

     //  R O O T       S T A T E
    storage initState = lastStorage;

    redeem(e,_shares, _receiver, _owner) at initState;
    bool allowanceDecreasedAfterNormalRedeem = silo_0.allowance(e, _owner, e.msg.sender) < collateralShareAllowanceBefore;

    redeem( e, _shares,  _receiver,  _owner,  _collateralType) at initState;
    //if collateral type is protected then protected share allowance must decrease and vice-versa
    bool allowanceDecreasedAfterSecondRedeem = _collateralType == ISilo.CollateralType.Collateral ? silo_0.allowance(e, _owner, e.msg.sender) < collateralShareAllowanceBefore : protectedShares_0.allowance(e, _owner, e.msg.sender) < protectedShareAllowanceBefore;

    assert allowanceDecreasedAfterNormalRedeem && allowanceDecreasedAfterSecondRedeem, "if funds are redeemed, then the allowances of msg.sender to the owner must always decrease !";
}

//@audit-ok 
rule ReceiverGetsExactAssetsOnWithdrawalAndOwnersSharesDecrease {
    env e; 
    uint256 _assets; address _receiver; address _owner; ISilo.CollateralType _collateralType; 
    

    uint ownerCollateralBalanceBefore = silo_0.balanceOf(e, _owner);
    uint assetBalanceOfReceiverBefore = assetToken0.balanceOf(e, _receiver);

    require assetBalanceOfReceiverBefore + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require ownerCollateralBalanceBefore <= silo_0.totalSupply(e);
    require _receiver != silo_0;
    require _collateralType == ISilo.CollateralType.Collateral;


     //  R O O T       S T A T E
    storage initState = lastStorage;

    withdraw(e, _assets, _receiver, _owner);
    uint assetBalanceOfReceiverAfterWithdraw_1 = assetToken0.balanceOf(e, _receiver);
    uint ownerCollateralBalanceAfterWithdraw_1 = silo_0.balanceOf(e, _owner);


    withdraw(e, _assets, _receiver, _owner, _collateralType) at initState;

    uint assetBalanceOfReceiverAfterWithdraw_2 = assetToken0.balanceOf(e, _receiver);
    uint ownerCollateralBalanceAfterWithdraw_2 = silo_0.balanceOf(e, _owner);

    assert assetBalanceOfReceiverAfterWithdraw_1 == assetBalanceOfReceiverAfterWithdraw_2 && assetBalanceOfReceiverAfterWithdraw_1 == assetBalanceOfReceiverBefore + _assets, "receivers asset balance must increase with the exact specified assets";

    assert ownerCollateralBalanceAfterWithdraw_2 == ownerCollateralBalanceAfterWithdraw_1 && ownerCollateralBalanceAfterWithdraw_2 < ownerCollateralBalanceBefore, "owner collateral shares must decrease after withdrawal";
    
}


//@audit-ok
rule ExactOwnerSharesAreBurntWhileReceiversAssetBalanceIncreaseOnFirstRedeem {
    env e; 
    uint256 _shares; address _receiver; address _owner;
    

    uint ownerCollateralBalanceBefore = silo_0.balanceOf(e, _owner);
    uint assetBalanceOfReceiverBefore = assetToken0.balanceOf(e, _receiver);

    

    require assetBalanceOfReceiverBefore + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require ownerCollateralBalanceBefore <= silo_0.totalSupply(e);

    require _receiver != silo_0;

    redeem(e,_shares, _receiver, _owner);
    uint assetBalanceOfReceiverAfterRedeem_1 = assetToken0.balanceOf(e, _receiver);
    uint ownerCollateralBalanceAfterRedeem_1 = silo_0.balanceOf(e, _owner);

    assert assetBalanceOfReceiverAfterRedeem_1 > assetBalanceOfReceiverBefore && ownerCollateralBalanceAfterRedeem_1 == ownerCollateralBalanceBefore - _shares, "redeeming must increase receivers asset balance with variable amounts and decrease owner's shares with exact given share amounts";
}

//@audit-ok
rule ExactOwnerSharesAreBurntWhileReceiversAssetBalanceIncreaseOnSecondRedeem {
    env e; 
    uint256 _shares; address _receiver; address _owner; ISilo.CollateralType _collateralType; 
    

    uint ownerCollateralBalanceBefore = silo_0.balanceOf(e, _owner);
    uint assetBalanceOfReceiverBefore = assetToken0.balanceOf(e, _receiver);

    require assetBalanceOfReceiverBefore + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require ownerCollateralBalanceBefore <= silo_0.totalSupply(e);

    require _collateralType == ISilo.CollateralType.Collateral;
    require _receiver != silo_0;


    redeem( e, _shares,  _receiver,  _owner,  _collateralType);
    uint assetBalanceOfReceiverAfterRedeem_2 = assetToken0.balanceOf(e, _receiver);
    uint ownerCollateralBalanceAfterRedeem_2 = silo_0.balanceOf(e, _owner);

    assert assetBalanceOfReceiverAfterRedeem_2 > assetBalanceOfReceiverBefore && ownerCollateralBalanceAfterRedeem_2 == ownerCollateralBalanceBefore - _shares, "redeeming must increase receivers asset balance with variable amounts and decrease owner's shares with exact given share amounts";
}

//@audit-ok
rule OnlyHookReceiverCanCallOnBehalfOfSilo {
    env e; calldataarg args;
    address hookReceiver = getHookReceiver(e);

    callOnBehalfOfSilo@withrevert(e, args);

    bool reverted = lastReverted;
    
    assert e.msg.sender != hookReceiver => reverted, "only hook receiver should be able to  call on behalf of silo";

}


//@audit-ok
rule SiloCantBeReInitialized {
    env e;
    address _config;
    require getSiloConfigAddressFromStorage(e) != 0;

    initialize@withrevert(e, _config);
    bool reverted = lastReverted;

    assert reverted, "silo can't be re-initialized";

}

//@audit-ok
rule SimpleBorrowIncreasesGivenAssetAmountsToReceiverAndRegistersDebtForBorrower {
    env e;
    uint256 _assets; address _receiver; address _borrower;

    uint256 assetBalanceOfReceiverBeforeBorrow = assetToken0.balanceOf(e, _receiver);
    uint debtBalanceOfBorrowerBeforeBorrow = debt_0.balanceOf(e, _borrower);

    require debtBalanceOfBorrowerBeforeBorrow < debt_0.totalSupply(e);
    require assetBalanceOfReceiverBeforeBorrow + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);

    require _receiver != silo_0;
    
    
    borrow(e, _assets, _receiver, _borrower);

    uint256 assetBalanceOfReceiverAfterBorrow = assetToken0.balanceOf(e, _receiver);
    uint debtBalanceOfBorrowerAfterBorrow = debt_0.balanceOf(e, _borrower);

    assert assetBalanceOfReceiverAfterBorrow == assetBalanceOfReceiverBeforeBorrow + _assets, "exact given assets must be borrowed to the receiver";

    assert debtBalanceOfBorrowerAfterBorrow > debtBalanceOfBorrowerBeforeBorrow, "debt must be registered for borrower after borrowing";


}

//@audit-ok
rule BorrowSharesRegisterExactGivenDebtForBorrowerAndIncreaseReceiversAssets {
    env e;
    uint256 _shares; address _receiver; address _borrower;

    uint256 assetBalanceOfReceiverBeforeBorrow = assetToken0.balanceOf(e, _receiver);
    uint debtBalanceOfBorrowerBeforeBorrow = debt_0.balanceOf(e, _borrower);

    require debtBalanceOfBorrowerBeforeBorrow < debt_0.totalSupply(e);
    require assetBalanceOfReceiverBeforeBorrow + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);

    require _receiver != silo_0;

    borrowShares(e, _shares, _receiver, _borrower);

    uint256 assetBalanceOfReceiverAfterBorrow = assetToken0.balanceOf(e, _receiver);
    uint debtBalanceOfBorrowerAfterBorrow = debt_0.balanceOf(e, _borrower);

    assert assetBalanceOfReceiverAfterBorrow > assetBalanceOfReceiverBeforeBorrow , "receivers asset balance must increase";

    assert debtBalanceOfBorrowerAfterBorrow ==  debtBalanceOfBorrowerBeforeBorrow + _shares, "debt must be increased for borrower by the exact given shares amounts";
}

//@audit-ok
rule BorrowingMustDecreaseDebtAllowancesOfBorrowerWithTheCallingSpender {
    env e; uint _assets; uint256 _shares; address _receiver; address _borrower;
    uint debtAllowancesBefore = debt_0.allowance(e, _borrower, e.msg.sender);

    require e.msg.sender != _borrower && debtAllowancesBefore < max_uint256;

    //  R O O T       S T A T E
    storage initState = lastStorage;

    borrow(e, _assets, _receiver, _borrower);
    bool debtAllowancesDecreasedAfterBorrow = debt_0.allowance(e, _borrower, e.msg.sender) < debtAllowancesBefore;


    borrowShares(e, _shares, _receiver, _borrower) at initState;
    bool debtAllowancesDecreasedAfterBorrowShares = debt_0.allowance(e, _borrower, e.msg.sender) < debtAllowancesBefore;

    assert debtAllowancesDecreasedAfterBorrow && debtAllowancesDecreasedAfterBorrowShares, "debt allowances of borrower to the msg.sender must decrease after borrowing";
}


//@audit-ok
rule BorrowSameAssets_TransferAndAllowanceIntegrity {

    env e; uint256 _assets; address _receiver; address _borrower;

    uint256 assetBalanceOfReceiverBeforeBorrow = assetToken0.balanceOf(e, _receiver);
    uint debtBalanceOfBorrowerBeforeBorrow = debt_0.balanceOf(e, _borrower);
    uint debtAllowancesBefore = debt_0.allowance(e, _borrower, e.msg.sender);

    

    require assetBalanceOfReceiverBeforeBorrow + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require debtBalanceOfBorrowerBeforeBorrow < debt_0.totalSupply(e);
    require e.msg.sender != _borrower && debtAllowancesBefore < max_uint256;
    require _receiver != silo_0;

    borrowSameAsset(e, _assets, _receiver, _borrower);

    uint256 assetBalanceOfReceiverAfterBorrow = assetToken0.balanceOf(e, _receiver);
    uint debtBalanceOfBorrowerAfterBorrow = debt_0.balanceOf(e, _borrower);

    bool assetBalanceOfReceiverIncreasedWithGivenAssets = assetBalanceOfReceiverAfterBorrow == assetBalanceOfReceiverBeforeBorrow + _assets;
    bool debtBalanceOfBorrowerIncreased = debtBalanceOfBorrowerAfterBorrow > debtBalanceOfBorrowerBeforeBorrow;

    assert assetBalanceOfReceiverIncreasedWithGivenAssets && debtBalanceOfBorrowerIncreased, "exact given assets must be borrowed to the receiver and debt must be registered for borrower after borrowing";

    assert debt_0.allowance(e, _borrower, e.msg.sender) < debtAllowancesBefore, "debt allowances of borrower to the msg.sender must decrease after borrowing";

}

//@audit-ok
rule repayMustDecreaseBorrowersDebtWithExactGivenRepayersAssets {

    env e; uint256 _assets; address _borrower;
    
    require e.msg.sender != silo_0;

    uint256 assetBalanceOfRepayerBeforeRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerBeforeRepay = debt_0.balanceOf(e, _borrower);

    require assetBalanceOfRepayerBeforeRepay + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require debtBalanceOfBorrowerBeforeRepay < debt_0.totalSupply(e);

    repay(e, _assets, _borrower);

    uint256 assetBalanceOfRepayerAfterRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerAfterRepay = debt_0.balanceOf(e, _borrower);

    assert assetBalanceOfRepayerAfterRepay < assetBalanceOfRepayerBeforeRepay&& debtBalanceOfBorrowerAfterRepay < debtBalanceOfBorrowerBeforeRepay, "repayer's assets must decrease with given amounts and borrowers debt must decrease after repaying"; 

}

//@audit-ok
rule repaySharesMustDecreaseExactAmountsOfBorrowersDebtWithAnyAmountOfRepayerAssets {
    env e; uint256 _shares; address _borrower;
    
    require e.msg.sender != silo_0;

    uint256 assetBalanceOfRepayerBeforeRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerBeforeRepay = debt_0.balanceOf(e, _borrower);

    require assetBalanceOfRepayerBeforeRepay + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require debtBalanceOfBorrowerBeforeRepay < debt_0.totalSupply(e);

    require debtBalanceOfBorrowerBeforeRepay > _shares; 

    repayShares(e, _shares, _borrower);

    uint256 assetBalanceOfRepayerAfterRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerAfterRepay = debt_0.balanceOf(e, _borrower);


    assert assetBalanceOfRepayerAfterRepay < assetBalanceOfRepayerBeforeRepay  && debtBalanceOfBorrowerAfterRepay == debtBalanceOfBorrowerBeforeRepay - _shares, "repayer's assets must decrease with any amounts such thatborrowers debt decrease with the exact given share amounts after repayingShares";
}


//@audit-ok
rule AssetBalancesOfSiloMustRemainSameAfterCollateralTransition {
    env e; 
    uint256 _shares;
    address _owner;
    ISilo.CollateralType _transitionFrom;

    uint256 assetBalanceOfSiloBeforeTransition = assetToken0.balanceOf(e, silo_0);

    transitionCollateral(e, _shares, _owner, _transitionFrom);

    uint256 assetBalanceOfSiloAfterTransition = assetToken0.balanceOf(e, silo_0);

    assert assetBalanceOfSiloBeforeTransition == assetBalanceOfSiloAfterTransition, "asset balances of silo must remain same after transition collateral";
}

//@audit-ok 
rule  TransitionCollateralMustTransitionExactGivenSharesForAnyAmountOfOtherCollateralType  {

    env e;
    uint256 _shares;
    address _owner;
    ISilo.CollateralType _transitionFrom;
    
    uint fromTypeBalanceBefore =  _transitionFrom == ISilo.CollateralType.Collateral ? silo_0.balanceOf(e, _owner) : protectedShares_0.balanceOf(e, _owner);

    uint toTypeBalanceBefore = _transitionFrom == ISilo.CollateralType.Collateral ? protectedShares_0.balanceOf(e, _owner) : silo_0.balanceOf(e, _owner);

    if (_transitionFrom == ISilo.CollateralType.Collateral) {
        require fromTypeBalanceBefore <= silo_0.totalSupply(e) && fromTypeBalanceBefore > 0;
        require toTypeBalanceBefore <= protectedShares_0.totalSupply(e);
    } else {
       require fromTypeBalanceBefore <= protectedShares_0.totalSupply(e) && fromTypeBalanceBefore > 0;
       require toTypeBalanceBefore <= silo_0.totalSupply(e);
    }



    transitionCollateral(e, _shares, _owner, _transitionFrom);

    //AFTER
    uint fromTypeBalanceAfter =  _transitionFrom == ISilo.CollateralType.Collateral ? silo_0.balanceOf(e, _owner) : protectedShares_0.balanceOf(e, _owner);

    uint toTypeBalanceAfter = _transitionFrom == ISilo.CollateralType.Collateral ? protectedShares_0.balanceOf(e, _owner) : silo_0.balanceOf(e, _owner);

    assert fromTypeBalanceAfter == fromTypeBalanceBefore - _shares && toTypeBalanceAfter > toTypeBalanceBefore , "exact given share amounts of transitionfrom collateral must be burnt from owner and any amounts of transitionto collateral must be minted to the owner";

}

//@audit-ok 
rule OnlyAllowedOnesCanTransitionCollateralOnBehalfOfOthers {
    env e;
    uint256 _shares;
    address _owner;
    ISilo.CollateralType _transitionFrom;
    

    uint allowanceBefore = _transitionFrom == ISilo.CollateralType.Collateral ? silo_0.allowance(e, _owner, e.msg.sender) : protectedShares_0.allowance(e, _owner, e.msg.sender);

    require e.msg.sender != _owner;
    require allowanceBefore < max_uint256;

    transitionCollateral(e, _shares, _owner, _transitionFrom);

    uint allowanceAfter = _transitionFrom == ISilo.CollateralType.Collateral ? silo_0.allowance(e, _owner, e.msg.sender) : protectedShares_0.allowance(e, _owner, e.msg.sender);

    assert allowanceAfter < allowanceBefore, "allowances of owner to msg.sender must decrease after transitioning collateral";
}


//@audit-ok
rule InterestIsAccruedOnDepositAndMint {
    env e;
    uint _assets;
    address _receiver;
    uint _mintShares;
    ISilo.CollateralType _collateralType;

    require getSiloDataInterestRateTimestamp(e) < e.block.timestamp;
    require e.block.timestamp < max_uint64;

    //ROOT STATE
    storage initState = lastStorage;

    deposit(e, _assets, _receiver);
    bool interestAccrued_1 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

    deposit(e, _assets, _receiver, _collateralType) at initState;
    bool interestAccrued_2 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

    mint(e,_mintShares, _receiver) at initState; 
    bool interestAccrued_3 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

    mint(e,_mintShares, _receiver, _collateralType) at initState; 
    bool interestAccrued_4 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

    assert interestAccrued_1 && interestAccrued_2 && interestAccrued_3 && interestAccrued_4, "All deposit and mint functions must accrue pending interests!!";
    
}


//=================================================================
//              H   E   L   P   E   R   S
//=================================================================



function flashFeeCVL(uint256 _amount) returns uint256  {
    return 0;
}


function CVL_convertToAssetsOrToShares(uint256 _assets, uint256 _shares) returns (uint256, uint256){
    uint256 assets; uint256 shares;

    require _assets > 0 || _shares > 0;
    if (_assets > 0 ) {
        require _shares == 0;
        require assets == _assets && shares == assets;

        return (assets , shares);
    } else {
        require _assets == 0;
        require shares == _shares && assets == shares;

        return (assets, shares);
    }
}

function canBurn(method f) returns bool {
    return f.selector == sig:burn(address,address,uint256).selector || f.selector == sig:callOnBehalfOfSilo(address,uint256,ISilo.CallType,bytes).selector || f.selector == sig:withdraw(uint256,address,address).selector || f.selector == sig:redeem(uint256,address,address).selector || f.selector == sig:redeem(uint256,address,address, ISilo.CollateralType).selector || f.selector == sig:withdraw(uint256,address,address, ISilo.CollateralType).selector || f.selector == sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector;
}
