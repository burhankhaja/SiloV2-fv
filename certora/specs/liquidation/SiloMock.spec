// DISCLAIMER : This contract simulates the underlying silo logic and its share token dependencies, the original silo dispatching were causing `out of resources` disaster for the prover, since summarizing underlying silo logic will give the exact verification result that we could have gotten over the original one

// As the Socrates never said , "Remember the Main goal of this spec is to verify the logic of liquidation module not the underlying silo contracts!"

using PartialLiquidation as partialLiquidation;

ghost mapping(address=>mathint) debt;
ghost mapping(address=>mathint) assetTokenBalances;  
ghost mapping(address=>mathint) collateralTokenBalances;
ghost mapping(address=>mathint) protectedTokenBalances;

// replicate above states in transiant state
ghost mapping(address=>mathint) TRANSIENT_assetTokenBalances;
ghost mapping(address=>mathint) TRANSIENT_collateralTokenBalances;
ghost mapping(address=>mathint) TRANSIENT_protectedTokenBalances;

ghost bool TRANSIENT_interestAccrued;

   
function getExactLiquidationAmounts_CVL() returns (uint256, uint256, uint256, bytes4){
        uint withdrawAssetsFromCollateral;
        uint withdrawAssetsFromProtected;
        uint repayDebtAssets;
        bytes4 customError;

        require repayDebtAssets > 0 && withdrawAssetsFromCollateral > 0 && withdrawAssetsFromProtected > 0;

        return (withdrawAssetsFromCollateral, withdrawAssetsFromProtected, repayDebtAssets, customError);
}

function repayCVL( uint256 _repayDebtAssets, address _borrower) returns bool {
    debt[_borrower] = debt[_borrower] - _repayDebtAssets;

    return true;
}

function forwardTransferFromNoChecksCVL(address _borrower, address _receiver, uint256 _shares) returns bool {
    env e;
    require _receiver != e.msg.sender;
    require _receiver != _borrower;

    // take from borrower
    collateralTokenBalances[_borrower] = collateralTokenBalances[_borrower] - _shares;
    protectedTokenBalances[_borrower] = protectedTokenBalances[_borrower] - _shares;

    // give to receiver 
    collateralTokenBalances[_receiver] = collateralTokenBalances[_receiver] + _shares;
    protectedTokenBalances[_receiver] = protectedTokenBalances[_receiver] + _shares;

    return true;
}

function accrueInterestCVL()  returns bool {
    TRANSIENT_interestAccrued = true;
    return true;
}

function callSolvencyOracleBeforeQuoteCVL()  returns bool {
    return true;
}



function redeemCVL(uint256 _shares , address _receiver, address _owner, ISilo.CollateralType  _collateralType)  returns bool {
// take shares from owner and give to receiver
require _receiver != _owner;

    uint assets; 
    require assets > 0;

   if (_collateralType == ISilo.CollateralType.Collateral) {

    collateralTokenBalances[_owner] = collateralTokenBalances[_owner] - _shares;
    assetTokenBalances[_receiver] = assetTokenBalances[_receiver] + assets;

    // Logic for transient balance
    TRANSIENT_collateralTokenBalances[_owner] = 0;
    TRANSIENT_assetTokenBalances[_receiver] = TRANSIENT_assetTokenBalances[_receiver] + assets;
 

   } else {
      protectedTokenBalances[_owner] = protectedTokenBalances[_owner] - _shares;
      assetTokenBalances[_receiver] = assetTokenBalances[_receiver] + assets;

      // Logic for transient balance
      TRANSIENT_protectedTokenBalances[_owner] = 0;
      TRANSIENT_assetTokenBalances[_receiver] = TRANSIENT_assetTokenBalances[_receiver] + assets;
   }

   return true;
}

function safeTransferFromCVL(address _from, address _to, uint256 _amount)  returns bool {
    env e;
    require _to != e.msg.sender && _from != _to;

    assetTokenBalances[_from] = assetTokenBalances[_from] - _amount;
    assetTokenBalances[_to] = assetTokenBalances[_to] + _amount;

    return true;
}

function safeIncreaseAllowanceCVL(address _spender, uint256 _amount) returns bool  {
    return true;
}

function revertIfErrorCVL(bytes4 _selector)  returns bool {
   return true;
}


function convertToSharesCVL() returns uint256 {
    uint shares;
    require shares > 0;

    return shares;
}

function safeTransferCVL(address _to, uint _amount) returns bool {
    return true;
}