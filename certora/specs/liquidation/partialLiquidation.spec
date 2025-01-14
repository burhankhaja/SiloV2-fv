import "../setup/CompleteSiloSetup.spec";
import "../silo/unresolved.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";

methods {
    // Dispatchers to Silos
    // function _.isSolvent(address) external => DISPATCHER(true) ;
    // function _.repay(uint256, address) external => DISPATCHER(true) ;
    // function _.callOnBehalfOfSilo(address, uint256, ISilo.CallType, bytes) external => DISPATCHER(true);
    // function _.redeem(uint256, address, address, ISilo.CollateralType) external => DISPATCHER(true);
    // function _.previewRedeem(uint256) external => DISPATCHER(true);
    // function _.getLiquidity() external => DISPATCHER(true);
    
    unresolved external in PartialLiquidation.liquidationCall(address, address, address, uint256, bool) 
        => DISPATCH(use_fallback=true) [ silo0._, silo1._ ] default NONDET;
    unresolved external in PartialLiquidation.maxLiquidation(address) 
        => DISPATCH(use_fallback=true) [ silo0._, silo1._ ] default NONDET;
}

