import "./SiloMock.spec";

methods { 
   
   function _.convertToShares(
        uint256 _assets,
        uint256 _totalAssets,
        uint256 _totalShares,
        Math.Rounding _rounding,
        ISilo.AssetType _assetType
    ) internal => NONDET;

 
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
  
    function _.safeTransferFrom(address _token, address _from, address _to, uint _amount) internal => safeTransferFromCVL( _from,  _to, _amount) expect (bool);

    function _.safeIncreaseAllowance(address _token, address _spender, uint256 _amount) internal => safeIncreaseAllowanceCVL( _spender,  _amount) expect (bool);

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
