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

function repayCVL(uint256 _repayDebtAssets, address _borrower) {
    debt[_borrower] = debt[_borrower] - _repayDebtAssets;
}




