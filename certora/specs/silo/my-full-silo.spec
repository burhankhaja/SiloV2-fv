// Importing silo0 setup from ./access-single-silo.spec
// @note this setup is for silo0 only make sure confs are compatible too
// @note also try whether cvl functions of a file are imported with it.
import "./access-single-silo.spec";

using Token0 as assetToken0; 
using Silo0 as silo_0;
using ShareProtectedCollateralToken0 as protectedShares_0;
using ShareDebtToken0 as debt_0;


methods {


//--------------------------problem--------------------------------------------------
     function _.isSolventAfterCollateralTransfer(address _sender) external => CVL_isSolventAfterCollateralTransfer(_sender) expect bool; //@audit-issue not summaried because it is library function, use lib name . function but that causes diff error
    //  find a way for Lib.isSol......

    // function SiloMathLib.convertToAssetsOrToShares( uint256 _assets, uint256 _shares, uint256 _totalAssets, uint256 _totalShares, Math.Rounding _roundingToAssets, Math.Rounding _roundingToShares, ISilo.AssetType _assetType) internal returns (uint256, uint256) => CVL_convertToAssetsOrToShares(_assets, _shares) expect (uint256, uint256); //@note won't be summarized until you alias it with library name, for now that return crazy errors
    //@audit-note i think there is no need for this one, it might cause unsoundness while deposit integrity where assets or shares could be switched on mutation, we need arbitary share value and plus i think this doensn't cause timeouts
//--------------------------------------^^^-----------------------------------------------/

    function _.reentrancyGuardEntered() external => NONDET;
    function _.flashFee(address _config, address _token, uint256 _amount) internal => flashFeeCVL(_amount) expect (uint256);

    //CAUSES MEMORY COMPLEXITY :: CHECK THIS :: https://prover.certora.com/output/951980/a35630a365a24637be44a2cd48ff330c/?anonymousKey=79f75f65cac991ee7978b58505f895c5918d58cd
    function decimals() external returns(uint8) => NONDET; //@note or maybe try cvl summarization to it
    // function _.isSolventAfterCollateralTransfer(address) external => NONDET;
    // function _.transfer(address,uint256) external  => DISPATCHER(true);
    // function _.transferFrom(address,address,uint256) external => DISPATCHER(true);
    function _.isSolvent() external => NONDET;
    function _.onFlashLoan(address _initiator, address _token, uint256 _amount, uint256 _fee, bytes  _data) external => NONDET;
    function _.quote(uint256 _baseAmount, address _baseToken) external => CONSTANT ;

    



}


//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================

//@doc: Assuming flashFee to be 0, taking a flashloan should niether increase nor decrease receivers asset balance, (ensuring that token are pulled and pushed correctly between receiver and silo)
// //@audit-ok Verified and catches mutation
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

//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================

//@doc: burn mutation: @later after validity is confirmed @audit do a full mutation test on burn mutation below one

/*
voilated in multiple 
 - burn: ShareToken._getSilo() ↪ 0x1f8f ::: instead of e.ms.sender != silo_0 , do this from harenss to get it directly::: can easily get with sharetoken.silo() ; /?????? => e.msg.sender != silo_0.silo(e)
 - callOnBehalfOfSilo: , require msg.sender != hook receiver copy from its rule and boom it wont get triggered
 - transitionCollateral: explicitly filter this method, since transitioning doesn't decrease balance
 - OPTIMIZATION :::: filter isView functions for quick run
 - redeem and withdraw fail because :::: the receiver is set to silo_0 itself , partially parameterize it >>>>> before that verify whether other violations are fixed as this will take lil bit of more time  ||| @note reason about if this is required in mint rule too
*/

//@audit :: examine :: https://prover.certora.com/output/951980/468bf6481509494db310ede4fbc3d908?anonymousKey=13b700fe1aba512f6696cb2f197d24c1210bf03a
//@audit verifying this is important than mint rule ........ do it later 
//@audit :::: cmd ::::: certoraRun certora/config/silo/Silo_verified/silo0.conf --rule "SiloAssetBalanceMustDecreaseOnEveryBurningOfSupply" 

//@audit  :: this run will violate on withdraw/redeem -> expected ===> make sure others methods dont revert it , it is just debugging purpose,,,,, if everything correct modifty this rule into partially parametric such that receiver is not silo_0 itself into withdraw/redeem functions!!! ::: https://prover.certora.com/output/951980/1c6fff14089c4893918516d9e078a04c?anonymousKey=d28d99a074ead2479c1b1e08120aae129bdb23d9

// fails::: vacous:: callonbehalfof _____ filter that later:::
// sharetoken.getSilo returns different silo .... do requier msg.sender != silo and sharetoken.getsilo both
// or maybe require ShareTokenLib.getShareTokenStorage().silo; to be ===== silo_0.silo(e) ..... 
// ^^^ add above harness function to silo0.... then check if burn() method violates again....

// quick check :: add only fix to burn() check if it is prevented


rule SiloAssetBalanceMustDecreaseOnEveryBurningOfSupply(method f) filtered {
     f -> (f.selector != sig:transitionCollateral(uint256,address,ISilo.CollateralType).selector &&  !f.isView )
}{
    env e;   calldataarg args;
    uint collateralSharesSupplyBefore = silo_0.totalSupply(e);
    uint siloAssetBalanceBefore = assetToken0.balanceOf(e, silo_0);
    
    //fix
    require e.msg.sender != silo_0.silo(e);
    require e.msg.sender != getHookReceiver(e); //@audit if vacuity is a thing maybe try , assert msg.sender != this => this way paths are always reachable for the prover.....


    f(e, args);

    uint collateralSharesSupplyAfter = silo_0.totalSupply(e);
    uint siloAssetBalanceAfter = assetToken0.balanceOf(e, silo_0);

    assert collateralSharesSupplyAfter < collateralSharesSupplyBefore => siloAssetBalanceAfter < siloAssetBalanceBefore, "Silo's asset balance must decrease on every burning of supply";
}


//@audit-issue cant understand rn why it fails on redeem funcs::: https://prover.certora.com/output/951980/468bf6481509494db310ede4fbc3d908?anonymousKey=13b700fe1aba512f6696cb2f197d24c1210bf03a
//@audit do all other required checks
// @audit then make sure this::::: totalsupply of silo_0 < max_uint and greater than 0 , may be underflow / overflow is causing this
//@audit take another look and withdraw/ redeem funcs before coming back here
rule SiloAssetBalanceMustIncreaseOnEveryMintingOfSupply {
    env e; method f; calldataarg args;
    uint collateralSharesSupplyBefore = silo_0.totalSupply(e);
    uint siloAssetBalanceBefore = assetToken0.balanceOf(e, silo_0);
    require e.msg.sender != silo_0;

    f(e, args);

    uint collateralSharesSupplyAfter = silo_0.totalSupply(e);
    uint siloAssetBalanceAfter = assetToken0.balanceOf(e, silo_0);

    assert collateralSharesSupplyAfter > collateralSharesSupplyBefore => siloAssetBalanceAfter > siloAssetBalanceBefore, "Silo's asset balance must increase on every minting of supply";
}



//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================

//@audit-issue violates :: isSolventAfterCollateralTransfer() is not getting summarized , that is why i get violation since porver assumes user to be solvent, might need to find some other way

// rule OnlySolventUsersCanTransferCollaterals {
//     env e;
//     address _to;
//     uint256 _amount;
//     // assume sender to be in-solvent
//     // require  !ShareCollateralTokenLib.isSolventAfterCollateralTransfer(e.msg.sender); 
//     //@note check if violation is due to multiple returns values from lib solvent function, might need to summarize it to constant //might have to use ghost state for that
//     //method
//     require getTransferWithChecks(e);
//     require !solvent[e.msg.sender];

//     transfer@withrevert(e, _to, _amount);

//     bool reverted = lastReverted;
//     assert reverted, "only solvent users must be able to transfer collateral shares";

//     //@audit-issue :: violated :: isSolventAfterCollateralTransfer is not gettting summarized dont know why :: https://prover.certora.com/output/951980/8e6e053dbe0946039632a0d3d564b5b1/?anonymousKey=5176edf6c96dc86892b45d890e8d5d1b189c3867
//     //@audit lil bit idea
//     /*
//     since isSolventAFterColateralTransfre:
//     if (collateral.silo != deposit.silo) return true;

//     require counter to above call

//     and then it calls SiloSolvencyLib.isSolvent

//     now summarize is solvent with the current cvl logic for the isSolventAfter

//     maybbe this will help
//     */
// }

// //@audit-ok Verified :: https://prover.certora.com/output/951980/7ec3d05bbea94783a2bfc8a046c21368/?anonymousKey=ccd903cbd8d66e6ba29d0b9908b4d6c74f42b73f
rule OnlyHookReceiverCanTransferCollateralSharesWithNoChecks {
    env e;
    address _from; address _to; uint256 _amount;

    //problem: how do you get hook receiver's address :: might need harness
    address hookReceiver = getHookReceiver(e);

    forwardTransferFromNoChecks@withrevert(e, _from, _to, _amount);
    bool reverted = lastReverted;
    
    assert e.msg.sender != hookReceiver => reverted, "only hook receiver should be able to  transfer collateral shares from any account without checks";

}



// //===================================================================
//                                 // D E P O S I T     /    M I N T 

//@audit-ok
rule OnlyUserSpecifiedAssetsAreTakenOnDeposit {
    env e;
    //@note maybe verify with initStorage 
    // shares = deposit(uint256 _assets, address _receiver);
    // shares2 = deposit(uint256 _assets, address _receiver, CollateralType _collateralType);

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

//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================//==========================================================================================


// i think if i just specify collateral type here, i might catch those mutations too where collateral type shares are mutated...
// @audit-ok :: examine :: split into two :: => https://prover.certora.com/output/951980/7ef2d0a819014461b379424bba6f6007?anonymousKey=93231250de3ad98e196a34787f3ad14d7b06adc6
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

//@note first of all we verify side by side integrity of both types of withdraw, then we verify their actual spec alongside
//@audit-ok   ::: Still test again , since you cleaned it , might have removed important conditions maybe (At last day)
// https://prover.certora.com/output/951980/49cbd1fbc90941eb9b2e6363d07e6da1?anonymousKey=1c7a3426386570f7b221625019b4cc747009d689
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

//@audit-issue for borrowing related rules create different spec that is exact like max-correctness.conf since i need token1 logic for collateralsilo logics do that....or just change this conf

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
    //  borrowSameAsset(uint256 _assets, address _receiver, address _borrower)
    /*
    spec: 
     - receivers assets must increase, assuming he aint silo_0 itself with given amount
     - borrowers debt must increase
     - allowances of _borrower to msg.sender must decrease, assuming msg.sender != _borrower itself and allowances < max_uint256
     - 


     @note later
     - this silo is set to collateral silo
     - interest is accrued for this silo

*/
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
    /*
    - msg.sender's assets must decrease with given amounts , assuming he aint sill_0 itself
    - borrowers debt tokens must decrease
    - interest must be accrued for this silo
    */
    env e; uint256 _assets; address _borrower;
    
    require e.msg.sender != silo_0;

    uint256 assetBalanceOfRepayerBeforeRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerBeforeRepay = debt_0.balanceOf(e, _borrower);

    require assetBalanceOfRepayerBeforeRepay + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require debtBalanceOfBorrowerBeforeRepay < debt_0.totalSupply(e);

    repay(e, _assets, _borrower);

    uint256 assetBalanceOfRepayerAfterRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerAfterRepay = debt_0.balanceOf(e, _borrower);

    assert assetBalanceOfRepayerAfterRepay < assetBalanceOfRepayerBeforeRepay&& debtBalanceOfBorrowerAfterRepay < debtBalanceOfBorrowerBeforeRepay, "repayer's assets must decrease with given amounts and borrowers debt must decrease after repaying"; //@note :: examine :: https://prover.certora.com/output/951980/ff5afc109981452f9374d7fd0a899252?anonymousKey=ca1e253d7bf71324d3f6717c7ea225251b87e3db

    //@audit later: for specific case, // assert assetBalanceOfRepayerAfterRepay == assetBalanceOfRepayerBeforeRepay - _assets && debtBalanceOfBorrowerAfterRepay < debtBalanceOfBorrowerBeforeRepay, "repayer's assets must decrease with given amounts and borrowers debt must decrease after repaying";

}
//@audit-ok
rule repaySharesMustDecreaseExactAmountsOfBorrowersDebtWithAnyAmountOfRepayerAssets {
    env e; uint256 _shares; address _borrower;
    
    require e.msg.sender != silo_0;

    uint256 assetBalanceOfRepayerBeforeRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerBeforeRepay = debt_0.balanceOf(e, _borrower);

    require assetBalanceOfRepayerBeforeRepay + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
    require debtBalanceOfBorrowerBeforeRepay < debt_0.totalSupply(e);

    require debtBalanceOfBorrowerBeforeRepay > _shares; // beta :: examine :: https://prover.certora.com/output/951980/ace5dbf448694961a0c24465a697d333?anonymousKey=d7ddb22a2b32f408c3083d575389e69bc98478d8

    repayShares(e, _shares, _borrower);

    uint256 assetBalanceOfRepayerAfterRepay = assetToken0.balanceOf(e, e.msg.sender);
    uint debtBalanceOfBorrowerAfterRepay = debt_0.balanceOf(e, _borrower);


    assert assetBalanceOfRepayerAfterRepay < assetBalanceOfRepayerBeforeRepay  && debtBalanceOfBorrowerAfterRepay == debtBalanceOfBorrowerBeforeRepay - _shares, "repayer's assets must decrease with any amounts such thatborrowers debt decrease with the exact given share amounts after repayingShares";
}


//@audit-ok :: examine :: https://prover.certora.com/output/951980/486cbd62622b4c9dac97057beb801cb6?anonymousKey=8c1197c3009cb7466f9c55790e3d5c6829253583
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

//@audit-ok :: examine :: https://prover.certora.com/output/951980/793485737d9446c09db514e4f84ef257?anonymousKey=64dc126a28e023651d1862b9bca20e3a502f801a
rule  TransitionCollateralMustTransitionExactGivenSharesForAnyAmountOfOtherCollateralType  {
    /*
   - exact given share amounts of transitionfrom collateral is burnt from owner
   - any amounts of transitionto collateral is minted to the owner
   - if msg.sender != owner && !max_allowance => allowances of owner to msg.sender must decrease for `transition` collateral
    */

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

//@audit-ok :: examine :: https://prover.certora.com/output/951980/0666ffede970424a82643a6d5692b903?anonymousKey=29516d665693c52d3c54f869f2ac5261ff75764f
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






// rule mint/burn pubilc mutation

// rule Bug {}
// rule PartialLiquidation >.....????




// rule hasdebtinothersilo {}
// rule setcollateraltothisthatsilo {}
// rule transferwithsolvency rule
// rule interestaccrual etc




/*@audit later

rule borrowAndBorrowSharesSetCollatoralOfUserToSilo1 {}
rule borrowSameAssetsSetsBorrowsCollateralToThisSilo {}

or maybe write parametric rule where you verify , certain method was called and user's collateral was set to :
- this silo (silo0)
- other silo (silo1)

*/


//@note high level rule zxc
//@audit :: examine :: https://prover.certora.com/output/951980/73609f75533e4d82abf63be961315796?anonymousKey=236137d206a85f894185cf6ce804c59f6d290c78
//@audit-issue violated ::::::: fix
rule BorrowersCantHaveDebtInBothSilosAtOnce {
    env e; method f; calldataarg args; address _borrower;
    uint borrowerDebtBefore = debt_0.balanceOf(e, _borrower);
    require siloConfig.hasDebtInOtherSilo(e, silo_0, _borrower);


    f(e,args);
    
    uint borrowerDebtAfter = debt_0.balanceOf(e, _borrower);
    
    assert borrowerDebtAfter == borrowerDebtBefore, "user cant have debt in silo0 and silo1 at once,";

} 

// rule borrowAndBorrowSharesSetUserCollaterToSilo1 {} // can it be turned into highlevel rule, understand why borrowshares vs borrowassets do that check ..... 

//@audit later::: rule allowanceDecreaseBorrowSameAssets {}


// rule ltvIsCheckedForSolvencyInAllTypesOfBorrow {} @audit later ::: we need _issolvent controlled summarization for this
// rule interestIsAccruedForBothSilosInBorrowAndBorrowShares {} @audit later:::: throw in parametric one

// rule borrow, && borrowsameAssets && repay{} &&&&&&& transitioncollateral {} 
// rule highlevel mint burn , deposit-withdraw high, interest rate, debt related high level !!!





//@audit-issue will do it later, after m able to  control isSolvent summarization 
// rule SolvencyIsCheckedOnWithdrawalAndRedeems {}

//@audit later
// // // //@audit-ok previous for mint and deposits
// //@audit-issue maybe be add withdraw/redeem functions too and make parametric rule with filtered block of only deposit/mint && withdraw/redeem functions and assume before state then verify interest is accrued ????
rule InterestIsAccruedOnDepositAndMint {
    env e;
    uint _assets;
    address _receiver;
    uint _mintShares;
    ISilo.CollateralType _collateralType;

    require getSiloDataInterestRateTimestamp(e) < e.block.timestamp;
    require e.block.timestamp < max_uint64; // if still fails check try catch block

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
//helpers

function flashFeeCVL(uint256 _amount) returns uint256  {
    return 0;
    // if (_amount == 0) return 0;
    // uint256 flashloanFee;
    // require flashloanFee > 0 && flashloanFee < 500000000000000000;
    // uint256 precision;
    // require precision == 1000000000000000000;

    // uint fee = _amount *  flashloanFee / precision;
    // return fee;
}

/*
    function convertToAssetsOrToShares(
        uint256 _assets,
        uint256 _shares,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _roundingToAssets,
        Math.Rounding _roundingToShares,
        ISilo.AssetType _assetType
    ) internal pure returns (uint256 assets, uint256 shares) {
        if (_assets == 0) {
            require(_shares != 0, ISilo.InputZeroShares());
            shares = _shares;
            assets = convertToAssets(_shares, _totalAssets, _totalShares, _roundingToAssets, _assetType);
            require(assets != 0, ISilo.ReturnZeroAssets());
        } else if (_shares == 0) {
            shares = convertToShares(_assets, _totalAssets, _totalShares, _roundingToShares, _assetType);
            assets = _assets;
            require(shares != 0, ISilo.ReturnZeroShares());
        } else {
            revert ISilo.InputCanBeAssetsOrShares();
        }
    }
*/
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


//-----------custom---burhankhaja--------------//
// !ShareCollateralTokenLib.isSolventAfterCollateralTransfer(e.msg.sender); 
ghost mapping(address => bool) solvent;

// @title An arbitrary (pure) function for the interest rate
function CVL_isSolventAfterCollateralTransfer(
    address _sender
) returns bool {
    return solvent[_sender];
}


// //@note Best helper function!!!
// //@audit note silo-core/contracts/lib/Views.sol 
// /**
//     function getSiloStorage()
//         internal
//         view
//         returns (
//             uint192 daoAndDeployerRevenue,
//             uint64 interestRateTimestamp,
//             uint256 protectedAssets,
//             uint256 collateralAssets,
//             uint256 debtAssets
//         )

// */
// //@note can easily now verify that mint/burn pub mutation with above helper
