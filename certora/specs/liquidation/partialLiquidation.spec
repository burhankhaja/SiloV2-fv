// using SiloConfig as siloConfig;
import "./SiloMock.spec";

methods { // 16 UNIQUE NONDET
//    function  _.forwardTransferFromNoChecks(address, address, uint256) external => NONDET;
   
   function _.convertToShares(
        uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType
    ) internal => NONDET;

    // function _.accrueInterest() external => NONDET;

    // function _.callSolvencyOracleBeforeQuote()  external => NONDET;
 
    function _.getConfigsForSolvency(address) external => NONDET ; //@audit make sure to later reason about this 

    function _.maxLiquidation(address _siloConfig, address _borrower) external  => NONDET;

    // function  _.redeem(uint256 _shares , address _receiver, address _owner, ISilo.CollateralType  _collateralType)  external => NONDET;

    function  _.previewRedeem(uint256 _shares, ISilo.CollateralType _collateralType)  external => NONDET;//@audit later make sure to add boorrow and other funcs with just empty imp just in case method change mutation is used


    function _.repay(uint256 _assets, address _borrower)  external => repayCVL(_assets, _borrower) expect bool;

    function _.turnOffReentrancyProtection() external => NONDET ;  //@audit wt the heck is nondet

    // function _.safeTransferFrom(address _from, address _to, uint256 _amount)  external => NONDET;

    // function _.safeIncreaseAllowance(address _spender, uint256 _amount)  external => NONDET;
    //@audit later add safetransfer() too ,,, must have and maybe other erc20 too
    //@audit later make sure tokens are properly dispatched to valid erc20 asset token 0

    // function _.revertIfError(bytes4 _selector)  external => NONDET;

    function _.getExactLiquidationAmounts(ISiloConfig.ConfigData  _collateralConfig, ISiloConfig.ConfigData _debtConfig, address _user, uint256 _maxDebtToCover, uint256 _liquidationFee) external => getExactLiquidationAmounts_CVL() expect (uint256, uint256, uint256, bytes4); 

    function _.turnOnReentrancyProtection() external => NONDET;


    function _.getTotalAssetsStorage(ISilo.AssetType) external => NONDET;
    function _.totalSupply() external => NONDET;

    //==========================================================================
    function  _.forwardTransferFromNoChecks(address _borrower, address _receiver, uint256 _shares) external => forwardTransferFromNoChecksCVL(_borrower, _receiver, _shares) expect (bool);

    function _.accrueInterest() external => accrueInterestCVL() expect (bool);

    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => callSolvencyOracleBeforeQuoteCVL() expect (bool);
    




    function  _.redeem(uint256 _shares , address _receiver, address _owner, ISilo.CollateralType  _collateralType)  external=> redeemCVL(_shares , _receiver, _owner, _collateralType) expect (bool);







    
    

  
    function _.safeTransferFrom(address _token, address _from, address _to, uint _amount) internal => safeTransferFromCVL( _from,  _to, _amount) expect (bool);

    function _.safeIncreaseAllowance(address _token, address _spender, uint256 _amount) internal => safeIncreaseAllowanceCVL( _spender,  _amount) expect (bool);
    //@audit later add safetransfer() too ,,, must have and maybe other erc20 too
    //@audit later make sure tokens are properly dispatched to valid erc20 asset token 0

    function _.revertIfError(bytes4 _selector)  external=> revertIfErrorCVL(_selector) expect (bool);

}


//@audit-ok
rule BorrowersDebtIsRepaidOnLiquidation {
    env e;   
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken;

    mathint borrowerDebtBefore = debt[_borrower];
    //call
    liquidationCall(e,_collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    mathint borrowerDebtAfter = debt[_borrower];


    assert borrowerDebtAfter < borrowerDebtBefore, "Liquidation must decrease borrowers debt";
}





    



function forwardTransferFromNoChecksCVL(address _borrower, address _receiver, uint256 _shares) returns bool {
    bool _ignore; 
    return _ignore;
}

function accrueInterestCVL()  returns bool {
    bool _ignore;
    return _ignore;
}

function callSolvencyOracleBeforeQuoteCVL()  returns bool {
    bool _ignore;
   return _ignore;
}

function redeemCVL(uint256 _shares , address _receiver, address _owner, ISilo.CollateralType  _collateralType)  returns bool {
    bool _ignore;
    return _ignore;
}

function safeTransferFromCVL(address _from, address _to, uint256 _amount)  returns bool {
    bool _ignore;
    return _ignore;
}

function safeIncreaseAllowanceCVL(address _spender, uint256 _amount) returns bool  {
    bool _ignore;
    return _ignore;
}

function revertIfErrorCVL(bytes4 _selector)  returns bool {
    bool _ignore;
    return _ignore;
}
//==============================================================================================================
//==============================================================================================================
//==============================================================================================================
//==============================================================================================================

// import "../setup/CompleteSiloSetup.spec";
// import "../silo/unresolved.spec";
// import "../simplifications/Oracle_quote_one_UNSAFE.spec";
// import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";
// import "../simplifications/SiloMathLib_SAFE.spec";


// using SiloConfig as config;
// using Silo0 as debtSilo0;
// using Token0 as assetToken0; //underlying debt asset of silo0
// using ShareDebtToken0 as debtToken0; // token that represents debt
// // rmember silo0 is itself shareCollateralToken



// methods {
//     // Dispatchers to Silos
//     function _.isSolvent(address) external => DISPATCHER(true) ;
//     function _.repay(uint256, address) external => DISPATCHER(true) ;
//     function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => DISPATCHER(true);
//     function _.redeem(uint256, address, address, ISilo.CollateralType) external => DISPATCHER(true);
//     function _.previewRedeem(uint256) external => DISPATCHER(true);
//     function _.getLiquidity() external => DISPATCHER(true);
//     function _.forwardTransferFromNoChecks(address,address,uint256) external => DISPATCHER(true);
//     function _.getExactLiquidationAmounts(ISiloConfig.ConfigData,  ISiloConfig.ConfigData, address _borrower, uint256, uint256) external => CVL_getExactLiquidationAmounts(_borrower) expect (uint256, uint256, uint256, bytes4);

//     function _.convertToShares(uint256 _assets,uint256 _totalAssets,uint256 _totalShares,Math.Rounding _rounding,ISilo.AssetType _assetType) external => CVL_convertToShares(_assets) expect (uint256);
  
    
//     // unresolved external in PartialLiquidation.liquidationCall(address, address, address, uint256, bool) 
//     //     => DISPATCH(use_fallback=true) [ silo0._, silo1._ ] default NONDET;
//     // unresolved external in PartialLiquidation.maxLiquidation(address) 
//     //     => DISPATCH(use_fallback=true) [ silo0._, silo1._ ] default NONDET;

//     //@doc: timeout :: https://docs.certora.com/en/latest/docs/user-guide/out-of-resources/timeout.html#example-usage
//     //@run: raisedWhile :: https://prover.certora.com/output/951980/d9978de52f78462aaf9648cd4957731c

    
//     // function SiloERC4626Lib.maxWithdrawWhenDebt(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,uint256,uint256,ISilo.CollateralType,uint256) internal returns (uint256,uint256) => NONDET;
//     // function PartialLiquidationLib.liquidationPreview(uint256,uint256,uint256,uint256,uint256,PartialLiquidationLib.LiquidationPreviewParams) internal returns (uint256,uint256,uint256) => NONDET ;
//     // function PartialLiquidationExecLib.liquidationPreview(SiloSolvencyLib.LtvData,PartialLiquidationLib.LiquidationPreviewParams) internal returns (uint256,uint256,bytes4) => NONDET ;
//     // function PartialLiquidationLib.maxLiquidation(uint256,uint256,uint256,uint256,uint256,uint256) internal returns (uint256,uint256) => NONDET;
//     // function SiloLendingLib.calculateMaxBorrow(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,uint256,uint256,ISiloConfig) internal returns (uint256,uint256) => NONDET ;

//     // function SiloSolvencyLib.getLtv(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.OracleType,ISilo.AccrueInterestInMemory,uint256) internal returns (uint256) => NONDET;
//     // function SiloSolvencyLib.isSolvent(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.AccrueInterestInMemory) internal returns (bool) => NONDET;
//     // function SiloLendingLib.maxBorrow(address,bool) internal returns (uint256,uint256) => NONDET ;
//     // function SiloERC4626Lib.maxWithdraw(address,ISilo.CollateralType,uint256) internal returns (uint256,uint256) => NONDET ;
//     // function SiloSolvencyLib.isBelowMaxLtv(ISiloConfig.ConfigData,ISiloConfig.ConfigData,address,ISilo.AccrueInterestInMemory) internal returns (bool) => NONDET;   

//     //@doc: https://docs.certora.com/en/latest/docs/user-guide/out-of-resources/timeout.html#library-based-systems
//     /*
//         function MyBigLibrary._ external => NONDET;
//         function MyBigLibrary._ internal => NONDET;

//     */
//         // function SiloERC4626Lib._ external => NONDET;
//         // // function SiloERC4626Lib._ internal => NONDET;

//         // function SiloLendingLib._ external => NONDET;
//         // // function SiloLendingLib._ internal => NONDET;

//         // function SiloSolvencyLib._ external => NONDET;
//         // // function SiloSolvencyLib._ internal => NONDET;

//         // function PartialLiquidationLib._ external => NONDET;
//         // // function PartialLiquidationLib._ internal => NONDET;

//         // function PartialLiquidationExecLib._ external => NONDET;
//         // // function PartialLiquidationExecLib._ internal => NONDET;
        
//     /**
//     suicide option @audit-issue when nothing works:

// //@doc:https://docs.certora.com/en/latest/docs/user-guide/out-of-resources/timeout.html#command-line-options

// --prover_args '-destructiveOptimizations enable'
// This option enables some aggressive simplifications that speed up the prover in many cases but breaks call trace generation in case a rule is violated.
    
//     */
    

// }

// rule PartialLiquidationCantBeInitializedTwice {
//     env e;
//     calldataarg args;

//     require siloConfig(e) != 0;

//     initialize@withrevert(e,args);

//     bool reverted = lastReverted;
//     assert reverted, "cant initialize liquidiation module twice";
// }

// // i think i should force siloConfig.get functions to validate cases where debt is in pariticular silo
// // and then verify balances of tokens directly on collateral and debt share token contract names 
// // like if debtin --> silo0 ==== collateralShareToken0.balanceOf && DebtShareToken0.balanceOf

// // rule checkDebug {
// //     env e;
// //     calldataarg args;
// //     method f;

// //     address borrower;

// //     require config.getDebtSilo(e, borrower) == debtSilo0;

//     //@audit note
//     // now require debtSilo0's configdata.token to be some underlying asset for which you will check
//     // repayers balance against

//     //@audit @note
//     // wait wait mock/Token0 is underlying asset for silo0 and vice verssssssssssssssssssssssssssssssssssssssa
//     // collateralshareToken (non-protected) are correcponding to the silo they are in
//     // e.g collateralShareToken0 = silo0 and same for silo1
//     // though there is a file in harness/silo*/ShareCollateralToken*.sol
//     // still config sets otherwise: "SiloConfig:_COLLATERAL_SHARE_TOKEN***=Silo***",

// //     f(e,args);

// //     assert true;

// // }

// //@doc: underlying debt_asset must be taken from the liquidator and not more than _maxDebtToCover
// rule LiquidatorDebtCoverageLimit {
//     env e;   
//     address _collateralAsset;
//     address _debtAsset;
//     address _borrower;
//     uint256 _maxDebtToCover;
//     bool _receiveSToken;

//     require _debtAsset == assetToken0;
//     require config.getDebtSilo(e, _borrower) == debtSilo0;

//     uint liquidatorToken0BalanceBefore = assetToken0.balanceOf(e, e.msg.sender);

//     //call
//     liquidationCall(e,_collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);


//     uint liquidatorToken0BalanceAfter = assetToken0.balanceOf(e, e.msg.sender);
//     mathint difference = liquidatorToken0BalanceBefore - liquidatorToken0BalanceAfter;
    
//     // assert
//     assert _maxDebtToCover > 0 => liquidatorToken0BalanceAfter < liquidatorToken0BalanceBefore && difference <= _maxDebtToCover, "debt assets must be paid from liquidator and only upto given max covered debt";


// }

// //@audit CheckPoint()
// //@doc: public mutation: can be caught by (_debtShareToken) of borrower must decrease as the liquidtor repaid his loan with collateral assets!!!
// // rule BorrowersDebtMustDecreaseOnLiquidation {
// //     env e;

// //     assert debtToken0.balanceOf(borrower) decreased after liquidation was called assuming maxDebtToCover > 0;

// // }


// //@audit-issue  what if we just summarize whole Silo logic to mock.spec where repay and redeem update some ghost state ???? @note but first i think it will be wise to Verify Silo and action before doing this type of thing???




// //rule: receiveSToken, i think for verifying protected and collateral shares that can be summed up
// // like this: when $(true) : either or both of receiver's protected and collateral token increase and not the underlying asset balance
// // similarly when $(false): only underlying asset balance of receiver must increase not the underlying one.
// // I think when CertoraTeam mutates either protected or colateral share token, that violation will be caught by our rule cause prover will assume all cases where protected shares are in and not collateraal ones so if protected one's function is mutated that could be caught
// // evaluate with mutation testing
// // if not you can always copy LIb call and require either of two assets to be of some value and then validate accordingly
// // @audit BEST::: OR OF COURSE YOU CAN VALIDATE THE UNDERLYING ASSUMPTION, OF HOW LIBS WORK ON USER'S PROTECTED OR COLLATERAL SHARES AND DIRECTLY ASSUME THOSE...
// //@audit for this rule , i would need to use collateraltoken0 same way i did debtSilo0 and its token

// //=========================================================
// // helpers
//  function CVL_getExactLiquidationAmounts( address _borrower) returns (uint256, uint256, uint256, bytes4) {
//     //note later if needed add logic for `_borrower` param, for now , ignore it
//     uint256 withdrawAssetsFromCollateral;
//     uint256 withdrawAssetsFromProtected;
//     uint256 repayDebtAssets;
//     bytes4 customError;

//     require withdrawAssetsFromCollateral > 0 && withdrawAssetsFromProtected > 0 && repayDebtAssets > 0;

//     return (withdrawAssetsFromCollateral,withdrawAssetsFromProtected,repayDebtAssets,customError);
//  }

//    /*
//       returns (
//             uint256 withdrawAssetsFromCollateral,
//             uint256 withdrawAssetsFromProtected,
//             uint256 repayDebtAssets,
//             bytes4 customError
//         )
//     */

// function CVL_convertToShares(uint256 _assets) returns uint256 {
//     require _assets > 0;
//     return _assets;
// }    


//==========================================================================================
//==========================================================================================
//==========================================================================================
//==========================================================================================
//==========================================================================================
//  DEBUG PROBE



/**
RUNS:::::
ORIGINAL : https://prover.certora.com/output/951980/3db9c7f7227f4613aa3c1b85f4128414?anonymousKey=b184c670d0cfef49f48c5b108e38f8647f33ffaf

MUTATION :: https://prover.certora.com/output/951980/ec470d951318427a813abeae3a6a9d36?anonymousKey=a8e73aaebad26d98f983e3e36545970558d7bbeb

*/