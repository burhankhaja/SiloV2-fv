import "./SiloMock.spec";

methods { 
   
   function _.convertToShares(
        uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType
    ) internal => convertToSharesCVL() expect uint256;

 
    function _.getConfigsForSolvency(address) external => NONDET ; 

    function _.maxLiquidation(address _siloConfig, address _borrower) external  => NONDET;

    function  _.previewRedeem(uint256 _shares, ISilo.CollateralType _collateralType)  external => NONDET;

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

    function _.safeTransfer(address token, address _to,  uint _amount) internal => safeTransferCVL(_to, _amount) expect bool;

}

//@audit-ok
//@doc: liquidating a borrower must decrease his debt
rule BorrowersDebtIsRepaidOnLiquidation {
    env e;   
    address _collateralAsset; address _debtAsset; address _borrower; uint256 _maxDebtToCover; bool _receiveSToken;

    mathint borrowerDebtBefore = debt[_borrower];

    //call
    liquidationCall(e,_collateralAsset, _debtAsset, _borrower, _maxDebtToCover, _receiveSToken);

    mathint borrowerDebtAfter = debt[_borrower];

    assert borrowerDebtAfter < borrowerDebtBefore, "Liquidation must decrease borrowers debt";
}

//@audit-ok ::
//@doc: asset tokens must be taken from liquidator but not more the the given `_maxDebtToCover` limit
rule AssetsUptoMaxCoverageAreTakenFromLiquidator {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;

    require _receiveSToken; 

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

//@audit-ok 
//@doc: if liquidator want to receive underlying share tokens, he should only get share tokens and not the actual underlying assets
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

    require _receiveSToken;

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

    assert _receiveSToken => liquidatorProtectedShareBalanceAfter > liquidatorProtectedShareBalanceBefore && liquidatorCollateralSharesBalanceAfter > liquidatorCollateralSharesBalanceBefore && LiquidatorAssetBalanceAfter <= liquidatorAssetBalanceBefore, "Liquidator shares balance must increase not the underlying assets"; 

} 

//@audit-ok
//@doc: if liquidator wants to receive underlying assets, he should only get the underlying assets and not any kind of share tokens
rule LiquidatorMustOnlyReceiveUnderlyingAssetsWhileNotChoosingReceiveSToken {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;


    //@note :: since two calls to transfernochecks are aggresively summarized to transfer both protected and collateral shares to receiver, trainsient storage is needed in this context such that the given redeeming share type is set to nill in redeemCVL function and the uncontrolled havocs of collateralTokenBalances and protectedTokenBalances are prevented.
    mathint liquidatorTransientAssetBalanceBefore = TRANSIENT_assetTokenBalances[e.msg.sender];
    mathint liquidatorTransientCollateralSharesBalanceBefore = TRANSIENT_collateralTokenBalances[e.msg.sender];
    mathint liquidatorTransientProtectedShareBalanceBefore = TRANSIENT_protectedTokenBalances[e.msg.sender];

    

    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    );

    mathint liquidatorTransientAssetBalanceAfter  = TRANSIENT_assetTokenBalances[e.msg.sender];
    mathint liquidatorTransientCollateralSharesBalanceAfter = TRANSIENT_collateralTokenBalances[e.msg.sender];
    mathint liquidatorTransientProtectedShareBalanceAfter = TRANSIENT_protectedTokenBalances[e.msg.sender];


    assert !_receiveSToken => liquidatorTransientAssetBalanceAfter > liquidatorTransientAssetBalanceBefore && liquidatorTransientCollateralSharesBalanceAfter <= liquidatorTransientCollateralSharesBalanceBefore && liquidatorTransientProtectedShareBalanceAfter <= liquidatorTransientProtectedShareBalanceBefore, "only underlying assets of liquidator must increase not the shares";

}

//@audit-ok 
//@doc: Liquidation should not hold share tokens, instead it must burn them for exchange of underlying assets
rule PartialLiquidationAlwaysBurnsSharesForExchangeOfUnderlyingAssets {
    env e;
    address _collateralAsset;
    address _debtAsset;
    address _borrower;
    uint256 _maxDebtToCover;
    bool _receiveSToken;


    mathint TransientCollateralSharesBalanceBefore = TRANSIENT_collateralTokenBalances[partialLiquidation];
    mathint TransientProtectedShareBalanceBefore = TRANSIENT_protectedTokenBalances[partialLiquidation];

    require TransientCollateralSharesBalanceBefore > 0 && TransientProtectedShareBalanceBefore > 0;

    //Liquidation call
    liquidationCall( e, 
        _collateralAsset,
        _debtAsset,
        _borrower,
        _maxDebtToCover,
        _receiveSToken
    );

    mathint TransientCollateralSharesBalanceAfter = TRANSIENT_collateralTokenBalances[partialLiquidation];
    mathint TransientProtectedShareBalanceAfter = TRANSIENT_protectedTokenBalances[partialLiquidation];


    assert !_receiveSToken => TransientCollateralSharesBalanceAfter < TransientCollateralSharesBalanceBefore && TransientProtectedShareBalanceAfter < TransientProtectedShareBalanceBefore, "shares must be burnt from liquidation module for exchange of underlying assets";
}

//@audit-ok
//@doc: liquidation must accrue interest on silo
rule InterestIsAccruedInSiloOnLiquidation {
   env e; 
   calldataarg args;
   require !TRANSIENT_interestAccrued;

   liquidationCall( e, args);

   assert TRANSIENT_interestAccrued, "Liquidation must accrue silo interests";

}

//@doc: PartialLiquidation Module can't be intialized twice
rule ReInitializationOfPartialLiquidationModuleIsNotAllowed {
    env e;
    calldataarg args;
    require siloConfig(e) != 0;

    initialize@withrevert(e, args);

    assert lastReverted, "PartialLiquidation Module can't be intialized twice";

}