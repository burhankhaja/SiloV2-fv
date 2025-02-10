import "./SiloMock.spec";

methods { 
   
   function _.convertToShares(
        uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType
    ) internal => convertToSharesCVL() expect uint256;

 
    function _.getConfigsForSolvency(address) external => NONDET ; //@audit make sure to later reason about this 

    function _.maxLiquidation(address _siloConfig, address _borrower) external  => NONDET;

    function  _.previewRedeem(uint256 _shares, ISilo.CollateralType _collateralType)  external => NONDET;//@audit later make sure to add boorrow and other funcs with just empty imp just in case method change mutation is used

    function _.repay(uint256 _assets, address _borrower)  external => repayCVL(_assets, _borrower) expect bool;

    function _.turnOffReentrancyProtection() external => NONDET ;  //@audit wt the heck is nondet


    function _.getExactLiquidationAmounts(ISiloConfig.ConfigData  _collateralConfig, ISiloConfig.ConfigData _debtConfig, address _user, uint256 _maxDebtToCover, uint256 _liquidationFee) external => getExactLiquidationAmounts_CVL() expect (uint256, uint256, uint256, bytes4); 

    function _.turnOnReentrancyProtection() external => NONDET;

    function _.getTotalAssetsStorage(ISilo.AssetType) external => NONDET;

    function _.totalSupply() external => NONDET;

    function  _.forwardTransferFromNoChecks(address _borrower, address _receiver, uint256 _shares) external => forwardTransferFromNoChecksCVL(_borrower, _receiver, _shares) expect (bool);

    function _.accrueInterest() external => accrueInterestCVL() expect (bool);

    function _.callSolvencyOracleBeforeQuote(ISiloConfig.ConfigData memory) internal => callSolvencyOracleBeforeQuoteCVL() expect (bool);
    
    function  _.redeem(uint256 _shares , address _receiver, address _owner, ISilo.CollateralType  _collateralType)  external=> redeemCVL(_shares , _receiver, _owner, _collateralType) expect (bool);
  
    function _.safeTransferFrom(address _token, address _from, address _to, uint _amount) internal => safeTransferFromCVL(_from,  _to, _amount) expect (bool);

    function _.safeIncreaseAllowance(address _token, address _spender, uint256 _amount) internal => safeIncreaseAllowanceCVL( _spender,  _amount) expect (bool);

    function _.revertIfError(bytes4 _selector)  external=> revertIfErrorCVL(_selector) expect (bool);

    /*
    MAY BE CHANGE DISPATCHES OF THESE FUNCTIONS

     function getConfigsForSolvency(address) returns (ISiloConfig.ConfigData, ISiloConfig.ConfigData) =>silo1 and silo0 as coll and debtconfigs// DISPATCHER(true); //// or maybe require siloConfig.getDebtSilo(e, _borrower) == silo0
    //   function getShareTokenStorage() internal pure returns (IShareToken.ShareTokenStorage


//DONE::::::
     function forwardTransferFromNoChecks(address _from, address _to, uint256 _amount)
        external => DISPATCHER(true);
    



DONE:::    convertToShares => returns > 1 :::::maybe this could return lower values and that might mess up verification, instead of nondet make sure > 0 is always returned

    
    */
    // function _.forwardTransferFromNoChecks(address _from, address _to, uint256 _amount) external => DISPATCHER(true);
    //  function _.getConfigsForSolvency(address) external  => DISPATCHER(true);

     //=======================================
    //  function _.afterAction(address _silo, uint256 _action, bytes  _inputAndOutput) external => NONDET;
     //===================
     function _.safeTransfer(address token, address _to,  uint _amount) internal => safeTransferCVL(_to, _amount) expect bool;

}


//@audit For More specific verified run of  rule  'BorrowersDebtIsRepaidOnLiquidation' over actual ShareDebtToken and other non-mock contracts dispatched contracts check out this:: 
// https://prover.certora.com/output/951980/4e3c67a4d2d7416f834a093a0ad950f9?anonymousKey=714af5389a523e42d185f6fdfe3991404004cd94


//@audit-ok :: 

rule BorrowersDebtIsRepaidOnLiquidation {
    env e;   
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken;

    mathint borrowerDebtBefore = debt[_borrower];

    //call
    liquidationCall(e,_collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    mathint borrowerDebtAfter = debt[_borrower];

    assert borrowerDebtAfter < borrowerDebtBefore, "Liquidation must decrease borrowers debt";
}

//@doc: asset tokens must be taken from liquidator but not more the the given `_maxDebtToCover` limit
rule AssetsUptoMaxCoverageAreTakenFromLiquidator {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;

    mathint LiquidatorAssetBalanceBefore = assetTokenBalances[e.msg.sender];

    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    );

    mathint LiquidatorAssetBalanceAfter = assetTokenBalances[e.msg.sender];


    assert LiquidatorAssetBalanceAfter < LiquidatorAssetBalanceBefore && LiquidatorAssetBalanceAfter >= LiquidatorAssetBalanceBefore - _maxDebtToCover, "assets tokens must be taken from liquidator but not more than his expected max coverage limit";
}


//spec

/*
if receiveStoken then liquidator must receive share tokens, and no underlying assets
otherwise liquidator must receive underlying assets, and no share tokens  &&&& the share balances of liquidation module must remain same as before

*/

//@audit ::: examine :: https://prover.certora.com/output/951980/f8e86e12901647229e9dae2c704c18bf?anonymousKey=b327c2f11a47552ed016df27fbf89426ac12967f

rule LiquidatorMustOnlyReceiveShareTokensWhileChoosingReceiveSToken {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;

    mathint liquidatorAssetBalanceBefore = assetTokenBalances[e.msg.sender];
    mathint liquidatorProtectedShareBalanceBefore = protectedTokenBalances[e.msg.sender];
    mathint liquidatorCollateralSharesBalanceBefore = collateralTokenBalances[e.msg.sender];

    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    );

    mathint LiquidatorAssetBalanceAfter = assetTokenBalances[e.msg.sender];
    mathint liquidatorProtectedShareBalanceAfter = protectedTokenBalances[e.msg.sender];
    mathint liquidatorCollateralSharesBalanceAfter = collateralTokenBalances[e.msg.sender];

    assert _receiveSToken => liquidatorProtectedShareBalanceAfter > liquidatorProtectedShareBalanceBefore && liquidatorCollateralSharesBalanceAfter > liquidatorCollateralSharesBalanceBefore && LiquidatorAssetBalanceAfter == liquidatorAssetBalanceBefore, "Liquidator must receive share tokens, and no underlying assets";

} 

rule LiquidatorMustOnlyReceiveUnderlyingAssetsWhileChoosingNotReceiveSToken {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;

    mathint liquidatorAssetBalanceBefore = assetTokenBalances[e.msg.sender];
    mathint liquidatorProtectedShareBalanceBefore = protectedTokenBalances[e.msg.sender];
    mathint liquidatorCollateralSharesBalanceBefore = collateralTokenBalances[e.msg.sender];

    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    );

    mathint liquidatorAssetBalanceAfter = assetTokenBalances[e.msg.sender];
    mathint liquidatorProtectedShareBalanceAfter = protectedTokenBalances[e.msg.sender];
    mathint liquidatorCollateralSharesBalanceAfter = collateralTokenBalances[e.msg.sender];


  assert !_receiveSToken => liquidatorAssetBalanceAfter > liquidatorAssetBalanceBefore && liquidatorProtectedShareBalanceAfter == liquidatorProtectedShareBalanceBefore && liquidatorCollateralSharesBalanceBefore == liquidatorCollateralSharesBalanceAfter, "Liquidator must receive underlying assets, and no share tokens";


}

//@audit :: examine :: https://prover.certora.com/output/951980/b812f1fd75b140eebf52c096fd5a717b?anonymousKey=25f12c015ce2bc22272ce0854bcdb97897f36bb2
rule PartialLiquidationAlwaysBurnsSharesForExchangeOfUnderlyingAssets {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;


    mathint protectedSharesBefore = protectedTokenBalances[partialLiquidation];
    mathint collateralSharesBefore = collateralTokenBalances[partialLiquidation];

    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    );

    mathint protectedSharesAfter = protectedTokenBalances[partialLiquidation];
    mathint collateralSharesAfter = collateralTokenBalances[partialLiquidation];


  assert !_receiveSToken => protectedSharesBefore == protectedSharesAfter && collateralSharesBefore == collateralSharesAfter, "shares must be burnt from liquidation module for exchange of underlying assets";
}