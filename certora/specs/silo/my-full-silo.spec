// Importing silo0 setup from ./access-single-silo.spec
// @note this setup is for silo0 only make sure confs are compatible too
// @note also try whether cvl functions of a file are imported with it.
import "./access-single-silo.spec";

using Token0 as assetToken0; 
using Silo0 as silo_0;
using ShareProtectedCollateralToken0 as protectedShares_0;

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

//@doc: burn mutation:
/// sharecollateral tokens were burnt (supply decreased) only and only due to either withdraw*2 / redeem*2 or transition collateral functions
// cant verify with e.msg.sender since silo is intermediary msg.sender to the the burn function not the tx.origin one
//@note easy one:
// $.totalAssets[ISilo.AssetType(uint256(_args.collateralType))] = totalAssets - assets; 
//@note if shareCollateral tokens were burnt then $.totalAssets[collateraltype] also decreased
//can do it in inverse too for mint mutation!!!
//@audit-issue problems could arize with lib functions like convertToAssetsOrToShares():: that will give 0 value for shares while nonzero for assets , make sure to restrict them equal 

//@audit-issue fails :: https://prover.certora.com/output/951980/6c323e9085894bd7a875ab9f37d8055b/?anonymousKey=ee53ec7c78cde3f9afdaaf7a9a345dcefb99433f
// remember to explicity tell msg.sender not silo via harness, check mint() violation
// other things violate it too //// transfer(to=ecrecover) could be because his balance == maxuint then transfer of one violate /// no no transfer violates because supply cant be 0 and other people have some assets ||||| u neec to requireinvariant from setup about 

// &&& decimals() cause some sort of vacuity /// make ure to do _.decimals() => ALWAYS(18) in certora/specs/setup/summaries/tokens_dispatchers.spec
//@audit do it at last

// rule TotalCollateralAssetsMustIncreaseDecreaseWithActualShareCollateralSupply {


//     // assert that if sharecollateraltoken supply decreased then the $.totalAssets(collatertype) of either of the two must decrese;

//     // // problem one : how do you get $.totalAssets(collateralType) ?
//     // //@note dont forget to require silo to be silo0 .// maybe take help from liquidation.spec
//     // //require config.getDebtSilo(e, _borrower) == debtSilo0; |||| i might have to create partial parametric rule in order to do that
//     // // or should i check on both silo's 
//     //@audit-issue i think i might have to filter main burn function that is actually called or since e.msg.sender could be the accepted one ;;; no no ut require e.msg.sender != silo

//     env e;  method f; calldataarg args;
//     uint256 IGNORE; uint256 collateralAssetsBefore; uint256 collateralAssetsAfter;

    
//     // pre

//     uint collaterSharesSupplyBefore = silo_0.totalSupply(e);
//     (IGNORE, collateralAssetsBefore) = getSiloProtectedAndCollateralAssets(e);

//     require e.msg.sender != silo_0;

//     // ENTRY
//     f(e,args);


//     //POST STATE
//     uint collaterSharesSupplyAfter = silo_0.totalSupply(e);
//     (IGNORE, collateralAssetsAfter) = getSiloProtectedAndCollateralAssets(e);

//     assert collateralAssetsAfter > collateralAssetsBefore <=> collaterSharesSupplyAfter > collaterSharesSupplyBefore, "collateral totalAssets state must be correlated with the actual collateral supply"; //@audit check if it catches burn mutation, remember visibly burn seems diff case but since it is correlation, we gonna catch that

// } // zxc

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

//@audit-issue :: examine :: https://prover.certora.com/output/951980/c0e8410f923a4169b3cc189155f0d0e5?anonymousKey=796600f934197ed1aa27845562762230ea947f92
// transfer --> cause require assetbalace of silo to be <= totalsupply
//@audit-issue `OutOfResources`   ---> SPLIT THIS RULE UP
//@note later make sure some of these crazy rules have different conf files
// rule ExactOwnerSharesAreBurntWhileReceiversAssetBalanceIncrease {
//     env e; 
//     uint256 _shares; address _receiver; address _owner; ISilo.CollateralType _collateralType; 
    

//     uint ownerCollateralBalanceBefore = silo_0.balanceOf(e, _owner);
//     uint assetBalanceOfReceiverBefore = assetToken0.balanceOf(e, _receiver);

//     // require ownerCollateralBalanceBefore <= silo_0.totalSupply(e) && assetBalanceOfReceiverBefore <= assetToken0.totalSupply(e);
//     require _collateralType == ISilo.CollateralType.Collateral;

//     require _receiver != silo_0;

//     //==============================================
//     require assetBalanceOfReceiverBefore + assetToken0.balanceOf(e, silo_0) <= silo_0.totalSupply(e);
//     require ownerCollateralBalanceBefore <= silo_0.totalSupply(e);

//     //@audit examine :: https://prover.certora.com/output/951980/d68cf9acb6dd4899ae98d7c2d6326ed6?anonymousKey=377baf0b03f84f0e461342dd03e06410f93b020f

//     //==========================================
 

     //  R O O T       S T A T E
    // storage initState = lastStorage;

    // redeem(e,_shares, _receiver, _owner) at initState;
    // uint assetBalanceOfReceiverAfterRedeem_1 = assetToken0.balanceOf(e, _receiver);
    // uint ownerCollateralBalanceAfterRedeem_1 = silo_0.balanceOf(e, _owner);


    // redeem( e, _shares,  _receiver,  _owner,  _collateralType) at initState;
    // uint assetBalanceOfReceiverAfterRedeem_2 = assetToken0.balanceOf(e, _receiver);
    // uint ownerCollateralBalanceAfterRedeem_2 = silo_0.balanceOf(e, _owner);

    // assert assetBalanceOfReceiverAfterRedeem_1 == assetBalanceOfReceiverAfterRedeem_2 && assetBalanceOfReceiverAfterRedeem_1 > assetBalanceOfReceiverBefore , "redeeming must increase receivers asset balance with variable amounts";

//     assert ownerCollateralBalanceAfterRedeem_2 == ownerCollateralBalanceAfterRedeem_1 && ownerCollateralBalanceAfterRedeem_2 == ownerCollateralBalanceBefore - _shares, "redeeming must always burn owners shares with the exact given _shares amount";


// } //@audit this rule has been split into two below, after they are verified remove this

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


//@audit later 9 FEB
// rule noReinitiaization {
//     env e;
//     ISiloConfig _config;;
//     require getSiloConfigAddressFromStorage(e) != address(0);


// }
// rule borrow, repay{} &&&&&&& transitioncollateral {}
// rule highlevel mint burn , deposit-withdraw high, interest rate, debt related high level !!!





//@audit-issue will do it later, after m able to  control isSolvent summarization 
// rule SolvencyIsCheckedOnWithdrawalAndRedeems {}

//@audit later
// // // //@audit-ok previous for mint and deposits
// //@audit-issue maybe be add withdraw/redeem functions too and make parametric rule with filtered block of only deposit/mint && withdraw/redeem functions and assume before state then verify interest is accrued ????
// rule InterestIsAccruedOnDepositAndMint {
//     env e;
//     uint _assets;
//     address _receiver;
//     uint _mintShares;
//     ISilo.CollateralType _collateralType;

//     require getSiloDataInterestRateTimestamp(e) < e.block.timestamp;
//     require e.block.timestamp < max_uint64; // if still fails check try catch block

//     //ROOT STATE
//     storage initState = lastStorage;

//     deposit(e, _assets, _receiver);
//     bool interestAccrued_1 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

//     deposit(e, _assets, _receiver, _collateralType) at initState;
//     bool interestAccrued_2 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

//     mint(e,_mintShares, _receiver) at initState; 
//     bool interestAccrued_3 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

//     mint(e,_mintShares, _receiver, _collateralType) at initState; 
//     bool interestAccrued_4 = getSiloDataInterestRateTimestamp(e) == e.block.timestamp;

//     assert interestAccrued_1 && interestAccrued_2 && interestAccrued_3 && interestAccrued_4, "All deposit and mint functions must accrue pending interests!!";
    
// }








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
