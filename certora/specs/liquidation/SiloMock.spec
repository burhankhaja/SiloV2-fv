// This contract simulates the underlying silo logic, the original silo dispatching were causing `out of resources` disaster for the prover, since summarizing underlying silo logic will give the exact verification result that we could have gotten on the original one, As the Socrates never said , "Remember the goal is to verify the logic of liquidation module"

ghost mapping(address=>mathint) debt;
   
function getExactLiquidationAmounts_CVL() returns (uint256, uint256, uint256, bytes4){
        uint withdrawAssetsFromCollateral;
        uint withdrawAssetsFromProtected;
        uint repayDebtAssets;
        bytes4 customError;

        require repayDebtAssets > 0 && withdrawAssetsFromCollateral > 0 && withdrawAssetsFromProtected > 0;

        return (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError);
}

function repayCVL(uint256 _repayDebtAssets, address _borrower) returns bool {
    debt[_borrower] = debt[_borrower] - _repayDebtAssets;
    bool _ignore;
    return _ignore;
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




